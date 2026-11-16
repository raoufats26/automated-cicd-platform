# Deployment guide (Phase 6)

How the pipeline deploys to a Linux server, and how to prepare that server.

## How it works

```
git push main -> GitLab pipeline -> validate -> test -> build+push image -> deploy
                                                                              |
                          GitLab Runner (installed ON the server, tag "deploy")
                                                                              |
                  deploy/deploy.sh: docker login -> pull image -> compose up -> check /health
```

**Why the runner lives on the server:** GitLab's shared runners are on the internet and
cannot connect to a VM on a home network. A runner on the server connects *out* to GitLab,
so no ports need opening and no SSH private key is stored in GitLab.
Deploy jobs run on that runner, so `docker compose` acts on the same machine.

**Secrets:** none are stored. The job logs in to the registry with `CI_JOB_TOKEN`, a temporary
token GitLab creates for each job. Runner registration uses a token you paste once on the server.

## 1. The server

This project uses the **Kali Linux VM in VMware** as the deployment server (Kali is Debian-based).
Ubuntu Server remains the preferred production-style target; the commands below also work there
with the differences noted.

- VMware network adapter: **NAT** is enough (the runner connects *out* to GitLab). Use **Bridged**
  if you also want to reach the app from Windows at `http://<vm-ip>:8000`.
- Change the default `kali` / `kali` password first (`passwd`). The app port 8000 will be open on this VM.
- Give the VM at least 2 GB RAM and 20 GB free disk.

```bash
sudo apt update && sudo apt full-upgrade -y     # Linux (Kali): bring the VM up to date
```

## 2. Install Docker (Linux / Kali, on the server)

Kali documents installing Docker from its own repositories (the `docker.io` package):

```bash
sudo apt install -y docker.io curl
sudo systemctl enable docker --now
docker --version
sudo docker run --rm hello-world       # expected: "Hello from Docker!"
docker compose version                 # expected: a version number; see below if missing
```

If `docker compose version` says "unknown command", install the Compose package and re-check:
```bash
sudo apt install -y docker-compose
docker compose version
```

On Ubuntu use Docker's official apt repository instead: https://docs.docker.com/engine/install/ubuntu/

## 3. Install GitLab Runner (Linux, on the server)

The standard package script may not recognise Kali, so use GitLab's manual binary install
(https://docs.gitlab.com/runner/install/linux-manually/), which works on any Linux:

```bash
sudo curl -L --output /usr/local/bin/gitlab-runner   "https://s3.dualstack.us-east-1.amazonaws.com/gitlab-runner-downloads/latest/binaries/gitlab-runner-linux-amd64"
sudo chmod +x /usr/local/bin/gitlab-runner
sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash
sudo /usr/local/bin/gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
sudo /usr/local/bin/gitlab-runner start
sudo /usr/local/bin/gitlab-runner status   # expected: "gitlab-runner: Service is running"
```
Check your CPU type first with `uname -m`: `x86_64` uses the `amd64` binary above (use `arm64`
for `aarch64`).

**Why the full path?** On Kali, `sudo` only searches a fixed list of folders (`secure_path`),
and `/usr/local/bin` is not in it, so plain `sudo gitlab-runner ...` says "command not found".
Typing the full path avoids the problem.

**Remove `.bash_logout`.** On Debian-based systems (Kali, Ubuntu) the new user gets a
`.bash_logout` file that makes every shell-executor job fail at the end
(a known GitLab Runner issue). Delete it:
```bash
sudo rm /home/gitlab-runner/.bash_logout
```

**Kali must be installed to disk.** In Live mode everything (runner, Docker, config) is lost
at reboot. Install Kali to the virtual disk first.

## 4. Create the runner in GitLab (browser)

1. Project **automated-cicd-platform** -> **Settings -> CI/CD -> Runners -> New project runner**.
2. Tags: `deploy`. Untick **Run untagged jobs**.
3. Create it and copy the token (starts with `glrt-`). Treat it like a password.

## 5. Register it (Linux, on the server)

```bash
sudo /usr/local/bin/gitlab-runner register
```
- GitLab instance URL: `https://gitlab.com`
- Token: the `glrt-...` value
- Executor: `shell`

Allow it to use Docker (note: docker group access is equivalent to root on that machine,
which is acceptable for a lab VM and a reason to keep the runner on a dedicated server):

```bash
sudo usermod -aG docker gitlab-runner
sudo systemctl restart gitlab-runner
sudo -u gitlab-runner docker ps       # expected: an empty table, no "permission denied"
```

In GitLab, the runner should show a green dot (online).

## 6. Deploy

Push to `main`. The `deploy` job runs on your runner.

Check on the server:
```bash
docker ps                            # container "fastapi-cicd-platform", status (healthy)
curl http://localhost:8000/health    # {"status":"healthy"}
```
From your Windows PC use the VM's IP (`ip a` on the server) instead of `localhost`:
`http://<vm-ip>:8000/health`.

## Troubleshooting

| Symptom | Check |
|---|---|
| `deploy` job stays "pending" | Runner offline, or its tag is not `deploy`, or "run untagged" setting mismatch |
| `permission denied ... docker.sock` | `gitlab-runner` user not in the `docker` group; re-run the `usermod` step and restart the runner |
| `unauthorized` on pull | Registry login failed; check the job log of the `docker login` step |
| Health check fails | Job log prints the last 50 container log lines; also run `docker compose -p fastapi-cicd logs` |
| `curl: command not found` | `sudo apt install -y curl` |
