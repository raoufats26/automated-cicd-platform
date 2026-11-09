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

Use **Ubuntu Server 24.04 LTS** in VMware (2 GB RAM, 20 GB disk). Set the network adapter to
**Bridged** (or NAT with internet access, which is enough since the runner connects out).
Kali also works for experiments, but Docker's official install instructions target Ubuntu.

## 2. Install Docker (Linux, on the server)

Follow the official steps for Ubuntu: https://docs.docker.com/engine/install/ubuntu/
("Install using the apt repository"). Then verify:

```bash
docker --version
docker compose version
sudo docker run --rm hello-world     # expected: "Hello from Docker!"
sudo apt install -y curl             # used by the health check
```

## 3. Install GitLab Runner (Linux, on the server)

Follow https://docs.gitlab.com/runner/install/linux-repository/ , then:

```bash
sudo systemctl status gitlab-runner   # expected: active (running)
```

## 4. Create the runner in GitLab (browser)

1. Project **automated-cicd-platform** -> **Settings -> CI/CD -> Runners -> New project runner**.
2. Tags: `deploy`. Untick **Run untagged jobs**.
3. Create it and copy the token (starts with `glrt-`). Treat it like a password.

## 5. Register it (Linux, on the server)

```bash
sudo gitlab-runner register
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
