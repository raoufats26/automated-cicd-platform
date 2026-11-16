> **Project type:** DevOps / Cloud / Infrastructure Engineering
>
> **Priority:** Portfolio Project 01 --- Build first
>
> **Status:** 🟡 Phases 1-4 complete · Phase 5 (Container Registry) next
>
> **Primary objective:** Build, test, publish and deploy a containerized
> application automatically through a GitLab CI/CD pipeline.

---

## 🧭 1. Project at a glance

### The idea in one sentence

Build a delivery platform where a code change pushed to GitLab
automatically triggers validation, automated tests, Docker image
creation, image publication and deployment to a Linux server.

### Why this project exists

A developer changes an application and pushes the code. Without
automation, someone may need to manually:

1. Download or pull the new source code.
2. Install dependencies.
3. Run tests.
4. Build a Docker image.
5. Publish the image to a registry.
6. Connect to a server.
7. Stop the previous application.
8. Start the new version.
9. Check that the application is healthy.

Our platform automates this workflow and makes deployments repeatable,
traceable and safer.

### Target outcome

By the end, we should be able to push a commit to GitLab and
demonstrate:

- A GitLab pipeline starts automatically.
- Code validation and automated tests run.
- A Docker image is built.
- The image is pushed to GitLab Container Registry.
- A Linux server deploys the new image.
- A health check confirms that the application is responding.
- Deployment failures can be diagnosed and, in the extended version, rolled back.

### What this project is --- and is not

**It is:** a practical CI/CD and container deployment platform, with a
small API used as the workload.

**It is not:** primarily a FastAPI programming project, a frontend
project, or a Kubernetes project. The application is deliberately simple
so the engineering effort stays focused on automation and
infrastructure.

---

## 🎯 2. Learning and career objectives

This project connects several technical areas into one demonstrable
workflow.

| Area | What the project demonstrates |
|---|---|
| Git & GitLab | Version control, branches, commits, merge requests and repository workflows |
| CI/CD | Automated pipeline stages, jobs, artifacts, rules and troubleshooting |
| GitLab Runner | How CI jobs are actually executed |
| Docker | Images, containers, ports, networks, layers and image lifecycle |
| Container Registry | Versioning and storing deployable images |
| Linux | Server administration, users, permissions, services and logs |
| SSH | Secure remote access and deployment automation |
| Python & FastAPI | A small application that can be tested and deployed |
| Pytest | Automated tests and repeatable quality checks |
| Bash | Deployment and operational scripting |
| Security | Secret handling, least privilege and safer deployment practices |
| Observability (extension) | Health checks, metrics, dashboards and troubleshooting |

### Professional positioning

This project supports a profile oriented toward:

**DevOps Engineer · Cloud & Infrastructure · Automation**

It is especially useful as evidence that networking, Linux, Python,
Docker and security fundamentals can be combined into a working
infrastructure workflow.

---

## 🏗️ 3. Target architecture

### High-level flow

```
Developer
   |
   | git push
   v
GitLab Repository
   |
   | detects a commit
   v
GitLab CI/CD Pipeline
   |
   v
GitLab Runner
   |
   +--> 1. Validate
   |
   +--> 2. Test (Pytest)
   |
   +--> 3. Build Docker image
   |
   +--> 4. Publish image
   |         |
   |         v
   |    GitLab Container Registry
   |
   +--> 5. Deploy over SSH
             |
             v
       Ubuntu Deployment Server
             |
             v
       Docker Compose
             |
             v
       FastAPI Container
             |
             v
       HTTP Health Check
```

### End-to-end sequence

1. A developer changes the FastAPI application.
2. The developer commits and pushes the change to GitLab.
3. GitLab detects the new commit and creates a pipeline.
4. A GitLab Runner picks up and executes the pipeline jobs.
5. The validation job checks basic code quality or configuration.
6. The test job installs the required Python packages and runs Pytest.
7. The build job creates a Docker image.
8. The publish job authenticates to GitLab Container Registry and pushes a uniquely tagged image.
9. The deploy job connects to the Ubuntu server through SSH.
10. The server pulls the selected image and starts the new application with Docker Compose.
11. A health-check step requests the application's `/health` endpoint.
12. The pipeline reports success or failure.

> **Important concept:** GitLab coordinates the pipeline; GitLab Runner
> executes the jobs. They are related, but they are not the same
> component.

---

## 🧩 4. Understand every platform component

### 4.1 Git

**Purpose:** Version control.

Git tracks source-code changes over time. It lets us create commits,
work with branches, compare changes and return to earlier versions.

Key concepts:

- Repository: project history and files tracked by Git.
- Commit: a recorded change.
- Branch: an independent line of development.
- Merge: combining changes from different branches.
- Remote: a hosted repository such as GitLab.

Useful commands:

```
git init
git status
git add .
git commit -m "Add FastAPI application"
git branch
git remote -v
git push
```

### 4.2 GitLab

**Purpose:** Host the Git repository and coordinate CI/CD.

GitLab provides:

- Source-code hosting.
- Branches and merge requests.
- Pipeline definitions and execution history.
- Job logs and artifacts.
- CI/CD variables.
- Container Registry.
- Environments and deployment history.

GitLab does not execute every job by itself. It assigns jobs to
available runners.

### 4.3 GitLab CI/CD

**Purpose:** Define the automated workflow.

The pipeline is configured in a file named `.gitlab-ci.yml` at the
repository root.

Typical concepts:

- `stages`: ordered pipeline stages.
- `jobs`: individual tasks.
- `script`: commands executed by a job.
- `image`: container image used by a job, where applicable.
- `variables`: job or pipeline configuration values.
- `rules`: conditions that determine when a job runs.
- `needs`: dependencies that can allow jobs to run efficiently.
- `artifacts`: files retained from a job.
- `cache`: reusable dependencies or data to speed up jobs.

A pipeline is made of jobs. Jobs are assigned to runners.

### 4.4 GitLab Runner

**Purpose:** Execute CI/CD jobs.

A runner is an agent that receives jobs from GitLab and runs their
commands.

Common executor types:

| Executor | General idea |
|---|---|
| Shell | Runs commands directly on the runner host |
| Docker | Runs jobs in Docker containers |
| Docker Autoscaler / other supported executors | Provides more dynamic execution capacity |

The executor affects isolation, available tools and how Docker builds
are performed.

**Decision to make during the CI/CD phase:** use an appropriate
GitLab-hosted/shared runner if available to the account and project, or
configure a self-managed runner. Check current GitLab plan, usage limits
and runner availability before choosing. Do not assume unlimited free CI
minutes.

### 4.5 Docker

**Purpose:** Package the application and its runtime dependencies into
an image.

Important distinctions:

- Image: a packaged, immutable template used to create containers.
- Container: a running or stopped instance of an image.
- Dockerfile: instructions for building an image.
- Volume: persistent storage managed by Docker.
- Network: communication path between containers.
- Port mapping: exposes a container port through the host.
- Tag: a label used to identify an image version.

Example:

```
docker build -t fastapi-demo:local .
docker run --rm -p 8000:8000 fastapi-demo:local
```

### 4.6 Docker Compose

**Purpose:** Describe and operate one or more containers through a YAML
configuration.

For this project, Compose will describe how the FastAPI service runs on
the deployment server.

Typical responsibilities:

- Select the image.
- Configure port mappings.
- Set runtime environment variables.
- Configure restart behaviour.
- Define health checks.
- Attach networks and volumes if required.

Compose is not the same as Docker itself: it is a tool for defining and
managing an application made of containers.

### 4.7 GitLab Container Registry

**Purpose:** Store the Docker images produced by the pipeline.

The pipeline builds an image, tags it and pushes it to the registry. The
deployment server later pulls that image.

The registry separates **building** an artifact from **running** it.

Recommended principle:

> Build an image once, give it an identifiable version, and deploy that
> same image. Avoid rebuilding a different image independently on the
> production server.

Use an immutable identifier such as a commit SHA for traceability. A
convenience tag such as `latest` may be used carefully, but should not
be the only reliable deployment identifier.

### 4.8 Linux / Ubuntu deployment server

**Purpose:** Host the deployed application.

The server will:

- Accept restricted SSH deployment access.
- Have Docker Engine and the Compose plugin installed.
- Authenticate to the GitLab Container Registry.
- Pull the requested image.
- Run the application through Docker Compose.
- Expose the application over HTTP.
- Provide logs and service status for troubleshooting.

The first implementation can use a local Ubuntu virtual machine if
practical. A separate cloud VM is not required to learn the workflow.

### 4.9 SSH

**Purpose:** Secure remote administration and deployment.

The pipeline will authenticate to the deployment server using an SSH key
rather than a hardcoded password.

Concepts:

- Private key: secret credential; never commit it.
- Public key: installed in the deployment user's `authorized_keys`.
- Host key: identifies the remote server; verify it rather than disabling host-key checking.
- Deploy user: dedicated account with only the permissions required for deployment.

The private key should be stored in an appropriately protected GitLab
CI/CD variable, often as a file-type variable where supported by the
chosen setup.

### 4.10 FastAPI and Pytest

**Purpose:** Provide a small application and tests so the platform has
something real to deliver.

FastAPI is the workload, not the main subject of the project.

Pytest verifies expected application behaviour before a new image is
published and deployed.

---

## 🧪 5. Application specification

### Application

A small Python API using FastAPI.

### Required endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Return basic application information |
| GET | `/health` | Return a health response for deployment verification |
| GET | `/api/status` | Return application status/version information |
| GET | `/api/users` | Return example user data |

### Example expected behaviour

`GET /health`

```
{
  "status": "healthy"
}
```

`GET /api/status`

```
{
  "status": "running",
  "service": "fastapi-cicd-platform"
}
```

These are illustrative response shapes. The implementation may add a
version or other fields.

### Test requirements

Tests should cover:

- Root endpoint responds successfully.
- Health endpoint returns the expected status.
- Status endpoint returns the expected structure.
- Users endpoint returns the expected data type and structure.
- Invalid or unexpected behaviour is handled appropriately where relevant.

Tests should run locally before the Docker and GitLab stages are
introduced.

---

## 🗂️ 6. Planned repository structure

The structure will grow as each phase is implemented.

```
gitlab-cicd-platform/
│
├── app/
│   ├── __init__.py
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   └── test_main.py
│
├── .claude/
│   └── skills/
│       ├── devops-engineer/
│       │   └── SKILL.md
│       ├── docker-expert/
│       │   └── SKILL.md
│       └── gitlab-cicd/
│           └── SKILL.md
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── requirements.txt
├── .gitlab-ci.yml
└── README.md
```

### File responsibilities

| File / folder | Responsibility |
|---|---|
| `app/` | Application source code |
| `app/main.py` | FastAPI routes and application setup |
| `tests/` | Automated tests |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Instructions to build the application image |
| `docker-compose.yml` | Runtime service configuration |
| `.dockerignore` | Excludes unnecessary files from Docker build context |
| `.gitignore` | Excludes local/generated files from Git |
| `.gitlab-ci.yml` | GitLab pipeline definition |
| `README.md` | Project documentation and instructions |
| `.claude/skills/` | Project-specific Claude Code instructions |

Not every file needs to exist immediately. Create files in the phase
where they become useful.

---

## 🔐 7. Security principles

Security is part of the implementation, not an afterthought.

### Secrets

- Never hardcode passwords, tokens or private SSH keys.
- Never commit `.env` files containing secrets.
- Use GitLab CI/CD variables for pipeline secrets.
- Use protected variables for protected branches/environments where appropriate.
- Mask variables where supported, but do not assume masking makes a secret safe if a job can print or exfiltrate it.
- Restrict who can edit pipeline configuration and protected variables.

### SSH

- Use a dedicated deployment account.
- Use SSH key authentication.
- Verify the server's host key.
- Do not use `StrictHostKeyChecking=no` as a shortcut.
- Restrict the deployment account's permissions.
- Keep private keys out of the repository and logs.

### Docker

- Prefer a minimal, trusted base image.
- Pin versions deliberately.
- Run the application as a non-root user where practical.
- Avoid embedding secrets in image layers.
- Keep the image small and remove unnecessary build dependencies.
- Review image vulnerabilities with a scanner in the security extension.

### Deployment

- Deploy a known image tag or digest.
- Verify application health after deployment.
- Keep a known-good previous version available for rollback.
- Separate staging and production configuration.
- Do not expose unnecessary ports or services.

---

## 🛣️ 8. Implementation roadmap

The project will be built incrementally. Do not jump ahead because later
phases depend on the earlier ones.

### Phase 0 --- Preparation

**Status: 🟢 Completed / in progress**

- [x] Create the project folder.
- [x] Configure Context7 MCP in the project.
- [x] Create three project-specific Claude Code skills.
- [x] Decide to build incrementally with Claude Code.
- [ ] Finish checking the skills against current official documentation.
- [ ] Verify Superpowers plugin is installed and available.

**Current environment plan**

- Host: Windows 11.
- Terminal: PowerShell.
- IDE: VS Code.
- Claude Code: project assistant.
- Node.js and npm: available for Claude Code tooling.
- Docker and Git: intended local development tools.
- VMware with Kali Linux: available, but Kali is not the preferred Ubuntu deployment target.
- WSL: not currently installed; do not add it unless a later technical need justifies it.

### Phase 1 --- FastAPI application foundation

**Status: 🟢 Completed**

Deliverables:

- [x] Create the application structure.
- [x] Implement the four API endpoints.
- [x] Add Pytest tests.
- [x] Add Python dependencies.
- [x] Add `.gitignore`.
- [x] Write the initial README.
- [x] Install dependencies in a local Python environment.
- [x] Run the application locally.
- [x] Run all tests and confirm they pass.

**Exit criteria:** The API works locally and the tests pass.

### Phase 2 --- Docker containerization

**Status: 🟢 Completed**

Deliverables:

- [x] Write a secure, understandable Dockerfile.
- [x] Add `.dockerignore`.
- [x] Add `docker-compose.yml`.
- [x] Build the Docker image.
- [x] Run the container locally.
- [x] Test all required endpoints through the mapped port.
- [x] Inspect logs, container status and image details.
- [x] Add a container health check where appropriate.

**Exit criteria:** The same API runs successfully inside a Docker
container.

### Phase 3 --- Git and GitLab repository

**Status: 🟢 Completed**

Deliverables:

- [x] Initialize Git.
- [x] Review `.gitignore`.
- [x] Create a GitLab project.
- [x] Add the GitLab remote.
- [x] Push the initial code.
- [ ] Create a feature branch and merge request to practise the workflow.
- [x] Confirm the repository contains no secrets.

**Exit criteria:** The project is hosted on GitLab and changes can be
pushed reliably.

### Phase 4 --- GitLab CI/CD pipeline

**Status: 🟢 Completed**

Create `.gitlab-ci.yml` with an initial pipeline:

1. **Validate** --- basic checks and configuration validation.
2. **Test** --- install dependencies and run Pytest.
3. **Build** --- build the Docker image.

Then:

- [x] Understand pipeline stages versus jobs.
- [x] Choose an available runner strategy.
- [x] Configure the runner or select an available hosted runner.
- [x] Run the pipeline on a push.
- [x] Inspect job logs and fix failures.
- [ ] Add suitable rules and dependency caching where useful. (caching added; rules not yet)

**Exit criteria:** A push triggers a pipeline and validation, tests and
image build succeed.

### Phase 5 --- Container Registry

**Status: ⚪ Not started**

Deliverables:

- [ ] Enable or locate the GitLab Container Registry for the project.
- [ ] Authenticate securely from the pipeline.
- [ ] Tag images with a commit-based identifier.
- [ ] Push images to the registry.
- [ ] Confirm the image appears in the registry.
- [ ] Confirm that the image can be pulled again.

**Exit criteria:** The pipeline publishes a versioned image that can be
pulled independently.

### Phase 6 --- Linux deployment

**Status: ⚪ Not started**

Deliverables:

- [ ] Prepare an Ubuntu deployment environment.
- [ ] Install Docker Engine and the Compose plugin.
- [ ] Create a restricted deployment user.
- [ ] Configure SSH key authentication.
- [ ] Verify the server host key.
- [ ] Configure secure registry authentication.
- [ ] Add protected CI/CD variables.
- [ ] Write the deployment script or job.
- [ ] Pull the selected image on the server.
- [ ] Start or update the application using Compose.
- [ ] Verify the `/health` endpoint.
- [ ] Inspect deployment logs.

**Exit criteria:** A successful pipeline deploys the new image to Ubuntu
and verifies the application.

### Phase 7 --- Reliability and security improvements

**Status: ⚪ Planned extension**

- [ ] Separate staging and production environments.
- [ ] Add a deliberate approval or promotion step for production.
- [ ] Implement a rollback procedure to a previous known-good image.
- [ ] Review runner and deployment permissions.
- [ ] Add image scanning.
- [ ] Add dependency scanning where practical.
- [ ] Review logs for accidental secret exposure.
- [ ] Document backup and recovery assumptions.

**Exit criteria:** The deployment process has a documented recovery path
and appropriate access controls.

### Phase 8 --- Monitoring and observability

**Status: ⚪ Optional extension**

Possible tools:

- Prometheus for metrics collection.
- Grafana for dashboards.
- Application and container health metrics.
- Centralized or structured logs, if justified.

Do this only after the basic deployment is stable. Monitoring should
answer concrete questions such as whether the application is up, how
much CPU/memory it uses and whether requests are failing.

### Phase 9 --- Portfolio and documentation

**Status: ⚪ Planned**

- [ ] Final architecture diagram.
- [ ] Updated README with setup and deployment instructions.
- [ ] Screenshots of successful pipelines.
- [ ] Registry image and tag evidence.
- [ ] Deployment and health-check evidence.
- [ ] Security decisions and limitations.
- [ ] Troubleshooting guide.
- [ ] Short demonstration video or live demo.
- [ ] CV project description based only on completed features.

---

## 🧠 9. Important concepts to understand

### CI versus CD

**Continuous Integration (CI):** automatically integrates changes and
runs checks such as validation and tests.

**Continuous Delivery:** keeps the software in a deployable state, with
production release potentially requiring approval.

**Continuous Deployment:** automatically releases every change that
passes the required pipeline to production.

Our first version automates the pipeline and deployment to our chosen
target. We should describe the exact behaviour accurately rather than
use these terms interchangeably.

### Build versus deploy

- Build: produce a deployable artifact, in our case a Docker image.
- Publish: store the image in a registry.
- Deploy: run a selected image in the target environment.

The deployment server should pull the already-built image rather than
rebuild the application source.

### Runner versus pipeline

- Pipeline: the workflow defined and tracked by GitLab.
- Job: one unit of work in that workflow.
- Runner: the execution agent that runs the job.

### Image versus container

- Image: packaged template.
- Container: an instance created from the image.

A new image can be built without starting a container. A container can
be stopped while its image remains stored locally.

### Registry versus server

- Registry: stores versioned images.
- Deployment server: pulls an image and runs a container from it.

### Health check versus successful deployment command

A successful SSH command or successful `docker compose up` does not
prove the application is usable. The deployment should make an HTTP
request to the application health endpoint and check the result.

---

## 🧰 10. Tools and services

| Tool | Role | Planned use |
|---|---|---|
| Git | Version control | Local source history |
| GitLab | Repository and CI/CD | Hosted project and pipelines |
| GitLab Runner | Job execution | Execute pipeline jobs |
| GitLab Container Registry | Image storage | Store deployable images |
| Python | Application language | FastAPI service |
| FastAPI | API framework | Simple application workload |
| Pytest | Testing | Automated application tests |
| Docker | Container runtime/build | Build and run images |
| Docker Compose | Container configuration | Run the service on the server |
| Ubuntu | Deployment OS | Linux deployment target |
| SSH | Secure remote access | Pipeline-to-server deployment |
| Bash | Shell automation | Deployment operations |
| Context7 | Documentation retrieval | Help Claude consult current documentation |
| Claude Code skills | Project instructions | DevOps, Docker and GitLab workflows |

### Cost and service considerations

The project should use free/local options wherever possible.

- Local development can run on the Windows machine with Docker.
- An Ubuntu VM can be used as a deployment target.
- GitLab runner availability, free-tier limits and registry limits must be checked in the account before relying on them.
- Do not create paid cloud resources without explicitly deciding to do so.
- A local VM is sufficient to learn SSH deployment and Linux operations.

---

## 🧯 11. Troubleshooting playbook

When something fails, diagnose it layer by layer. Do not randomly change
several files at once.

| Symptom | First checks |
|---|---|
| Tests fail locally | Read the failing assertion and traceback; verify dependencies and application behaviour |
| Docker build fails | Inspect the first failing build step, Dockerfile paths and dependency installation |
| Container exits | Run `docker ps -a` and inspect `docker logs <container>` |
| API is not reachable | Check container status, application bind address, port mapping and firewall |
| Pipeline is stuck | Check whether a compatible runner is available and whether job tags match |
| Pipeline job fails | Read the job log from the first meaningful error |
| Registry push fails | Check image name, tag, registry URL and authentication permissions |
| SSH connection fails | Check host, port, network path, username, key format and server host key |
| Docker command denied on server | Check deployment-user permissions and Docker access policy |
| Deployment succeeds but health check fails | Inspect container logs, port mapping, startup time and endpoint response |

Useful diagnostic commands:

```
git status
docker version
docker ps -a
docker images
docker logs <container-name>
docker compose ps
docker compose logs
```

On Ubuntu, useful commands include:

```
whoami
id
uname -a
df -h
free -h
systemctl status docker
docker ps -a
docker compose ps
docker compose logs
ss -tulpn
```

Replace placeholders such as `<container-name>` with actual values. Do
not paste secrets into logs or screenshots.

---

## 📸 12. Evidence to collect for the portfolio

Capture evidence as each milestone is completed.

| Milestone | Evidence |
|---|---|
| Application | API response from `/` and `/health` |
| Tests | Terminal output showing tests passing |
| Docker | Successful image build and running container |
| GitLab | Repository and commit history |
| CI/CD | Successful pipeline with visible stages |
| Registry | Published image and version tag |
| Linux | Server running the deployed container |
| SSH | Successful secure deployment workflow without exposing credentials |
| Health verification | HTTP response after deployment |
| Rollback | Demonstration that a previous image can be restored |
| Monitoring | Dashboard showing application or host metrics, if implemented |

Never include private keys, access tokens, passwords, unmasked
environment variables or sensitive server details in portfolio
screenshots.

---

## 📝 13. CV description --- use after implementation

### Project title

**Automated CI/CD Platform for Containerized Applications**

### Draft description

Designed and implemented an automated CI/CD workflow using GitLab CI/CD,
Docker and Linux. Built a FastAPI application and automated validation,
testing, container image creation, registry publication and remote
deployment. Configured GitLab Runner, SSH-based deployment, secure CI/CD
variables and post-deployment health checks.

**Technologies:** Git, GitLab CI/CD, GitLab Runner, Docker, Docker
Compose, Python, FastAPI, Pytest, Linux, Bash, SSH.

> Update this description after implementation. Remove any capability
> that was not completed and tested. Add measurable results only when
> you have evidence.

---

## 📚 14. Official documentation

Use official documentation as the primary reference when implementing
version-specific commands and configuration.

- GitLab CI/CD documentation
- GitLab Runner documentation
- GitLab Container Registry
- Docker documentation
- Docker Compose documentation
- FastAPI documentation
- Pytest documentation
- Ubuntu Server documentation
- OpenSSH documentation
- Context7

Always verify current syntax, supported versions, account limits and
security recommendations before applying commands to the project.

---

## 📅 15. Project work log

Use this section to record progress after each work session.

### Session template

**Date:**

**Phase:**

**Goal for this session:**

**What I implemented**

**Commands I ran**

```
# Add commands here
```

**What worked**

**Errors and troubleshooting**

**Concepts I learned**

**Files created or modified**

**Next action**

---

### Session 2026-11-16: Phase 6, Linux deployment (verified)

**Date:** 2026-11-16

**Phase:** 6 (Linux deployment), finished and verified. Phase 5 (registry) re-verified.

**Goal for this session:** Bring the self-hosted Kali deploy runner online, deploy automatically from `main`, prove a second automated deploy, and collect evidence for the portfolio.

**What I implemented**
- Installed Kali to disk (it had been running in Live mode) and set up Docker 28.5.2, Compose v2.40.3 and GitLab Runner 19.5.3 (shell executor, tag `deploy`, "run untagged jobs" off).
- Deploy job in `.gitlab-ci.yml`, run on `main` only, with `environment.url` set to the Kali VM and `APP_VERSION` set to the commit SHA.
- `deploy/deploy.sh`: registry login, pull, `up -d`, health-check retry loop, and `trap ... docker logout` on exit.
- `deploy/docker-compose.deploy.yml`: pulls the image from the registry and never builds on the server.
- Visible change: `GET /` now returns `"message": "Deployed by GitLab CI/CD"`, with the test updated.
- README "Results / Evidence" section with 9 screenshots, and an updated Roadmap.

**Commands I ran**

```
# Kali (Linux): diagnose Live mode, then check the network
findmnt -n -o SOURCE,FSTYPE /          # overlay root = Live mode
grep -o 'boot=live' /proc/cmdline
lsblk
curl -sS -o /dev/null -w "%{http_code}\n" https://gitlab.com   # HTTPS works although ICMP is blocked

# Kali (Linux): runner setup (full sequence in docs/DEPLOYMENT.md)
sudo /usr/local/bin/gitlab-runner register
sudo /usr/local/bin/gitlab-runner verify
sudo /usr/local/bin/gitlab-runner status
sudo usermod -aG docker gitlab-runner
sudo -u gitlab-runner docker ps
sudo rm /home/gitlab-runner/.bash_logout
sudo journalctl -u gitlab-runner -f    # follow the runner's logs

# Kali (Linux): check the deployed container
sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
curl http://localhost:8000/api/status

# Windows (PowerShell)
.\.venv\Scripts\python.exe -m pytest -v
Invoke-RestMethod http://192.168.175.128:8000/api/status | Format-List
# Polling loop: waits until the version changes after a push.
# Replace <previous-version> with the version running before the push (e.g. b59db033).
do {
    $s = Invoke-RestMethod http://192.168.175.128:8000/api/status
    Write-Host "$(Get-Date -Format HH:mm:ss)  version=$($s.version)  uptime=$($s.uptime_seconds)"
    Start-Sleep -Seconds 10
} while ($s.version -eq "<previous-version>")

git add / git commit / git push origin main
```

**What worked**
- Four automated deploys were verified, each confirmed with `/api/status` from Windows showing the matching version:
  1. `e9f486a2`: first deploy (APP_VERSION and registry logout).
  2. `b59db033`: code change (the `message` field).
  3. `da7a3839`: screenshots commit. I pushed `ac5b71a` and `da7a383` back to back; the newer commit won, which is the expected behaviour.
  4. `8769f47c`: roadmap update and blurred screenshot.
- Pipeline `#3072974617` passed all four stages in 1 min 41 s.
- Registry: `latest` and `b59db033` share one digest; older tags (`e9f486a2`, `f104d547`) remain available for rollback.
- 8 of 8 tests pass locally.

**Errors and troubleshooting**
- **Kali was in Live mode (overlay root):** changes are lost on reboot. Fix: install Kali to the virtual disk, then redo the runner setup.
- **ICMP blocked, HTTPS worked:** `ping` to the internet failed, but HTTPS requests succeeded. Lesson: do not use `ping` to judge connectivity; test with `curl` on the port you actually need.
- **`sudo gitlab-runner` not found:** sudo's `secure_path` does not include `/usr/local/bin`. Fix: use the full path `/usr/local/bin/gitlab-runner`.
- **Shell executor jobs failing at the end:** the `.bash_logout` file in the runner user's home is a known problem on Debian-based systems. Fix: delete it.
- **Runner token exposed in chat:** the `glrt-...` registration token was pasted into a chat. **Rotation: DONE.** The old runner was deleted in GitLab. Note that `gitlab-runner unregister` only removes the runner manager (the local registration), not the runner itself, so the runner had to be deleted in GitLab as well, otherwise the exposed token would stay valid. A new runner was created and registered, and the deploy job was retried successfully on it.
- **Windows vs Linux case sensitivity:** the screenshots folder was `docs/Screenshots` on disk but the README linked `docs/screenshots`. Windows ignores case, GitLab does not, so the images would have been broken. Fix: renamed the folder to lowercase. Also, the first push forgot the images because Git saw the folder under another name.
- **First health check fails during startup:** `curl` returned "Connection reset by peer" on attempt 1, because the container was still starting. Expected behaviour, not a bug: the retry loop succeeded on attempt 2.
- **Public IP in a screenshot:** it was blurred in `06-runner-online.png`, but the old image remains in git history (`da7a383`). Low risk, no rewrite done.

**Concepts I learned**
- `CI_JOB_TOKEN`: a per-job registry credential, revoked when the job ends. It is separate from the runner's own token.
- Why the deploy uses the commit-SHA tag, not `latest`: every running version is traceable, and old tags allow rollback.
- A health-check retry loop handles the gap between "container started" and "app ready".
- `--password-stdin` and `docker logout` keep credentials out of process lists and off the disk.
- Shell executor vs Docker executor, and why docker-group access is root-equivalent on the server.
- `sudo` has its own `secure_path`, independent of your normal `PATH`.

**Files created or modified**
`.gitlab-ci.yml`, `deploy/deploy.sh`, `deploy/docker-compose.deploy.yml`, `app/main.py`, `tests/test_main.py`, `docs/DEPLOYMENT.md`, `docs/screenshots/*.png` (9 files), `README.md`, `docs/PROJECT_MASTER_GUIDE.md`.

**Next action**
Phase 7 (Reliability & security), steps 1-3 **DONE and verified** (see the Phase 7 entry below).

---

### Session 2026-11-16 (later): Phase 7, reliability and security (steps 1-3 verified)

**Date:** 2026-11-16

**Phase:** 7 (Reliability & security), in progress.

**Goal for this session:** Rotate the exposed runner token, serialise production deploys, and prove a rollback.

**What I implemented**
1. Runner token rotation: old runner deleted in GitLab (`unregister` only removes the runner manager, so the runner itself had to be deleted), new runner created and registered.
2. `resource_group: production` on the deploy job: only one deploy to production at a time, across pipelines.
3. Rollback through GitLab Environments, with a "Rollback procedure" section in `docs/DEPLOYMENT.md`.

**What worked**
- The deploy of `ec0a187d` succeeded with `resource_group` set, on the new runner.
- Rollback: production went from `ec0a187d` to `b59db033` at 11:26:48 (uptime 1.71 s). It reused the existing registry image, with no rebuild. The Deployment history shows it as ID 11, run from old pipeline #3072974617.
- Roll-forward: a new pipeline on `main`.
- Prerequisites that must be ON: "Prevent outdated deployment jobs" and "Allow job retries for rollback deployments".

**Concepts I learned**
- Rollback here means re-running an old deploy job, which is only possible because images are tagged by commit and old tags are kept.
- A rollback changes the running container, not `main`; the next push to `main` deploys forward again.
- `resource_group` queues deploys instead of running them in parallel.

**Files created or modified**
`.gitlab-ci.yml`, `docs/DEPLOYMENT.md`, `docs/screenshots/10-rollback-environment.png`, `README.md`, `docs/PROJECT_MASTER_GUIDE.md`.

**Rollback path used:** Operate -> Environments -> production -> rollback arrow on the target row -> confirm. Roll-forward with the arrow on the newest row did NOT create a job; the reliable roll-forward was Build -> Pipelines -> Run pipeline on `main`.

**Next action**
Phase 7 remaining steps:
4. Docs-only rules: `rules: changes:` on validate, test, build and deploy **DONE and verified.**
   - Code-path push `ebdc17d4`: full pipeline, deployed at 11:40:00 (uptime 2.32).
   - Docs-only push `382de9a`: no pipeline, no deploy. `/api/status` still showed `ebdc17d4` with uptime 359.3 at 11:46.
   - Evidence: `docs/screenshots/11-docs-only-skip.png`.
5. Trivy image scanning.
6. Registry cleanup policy.
7. "Security decisions & limitations" section in the README.

---

## ✅ 16. Definition of done

The core project is complete when all of the following are true:

- [ ] FastAPI application works and has automated tests.
- [ ] Application runs in Docker locally.
- [ ] Source code is hosted in GitLab.
- [ ] GitLab pipeline starts on the intended code changes.
- [ ] Pipeline validates and tests the application.
- [ ] Pipeline builds a Docker image.
- [ ] Pipeline publishes the image to GitLab Container Registry.
- [ ] Pipeline deploys the image to an Ubuntu server through SSH.
- [ ] The server runs the application through Docker Compose.
- [ ] The pipeline verifies the health endpoint after deployment.
- [ ] Secrets are not committed to the repository.
- [ ] Deployment and troubleshooting instructions are documented.
- [ ] The project can be demonstrated and explained without relying on Claude to answer every question.

### The guiding principle

**Build it → understand it → test it → document it → demonstrate it.**

Do not optimize for the number of tools in the technology stack.

Optimize for a reliable system that you can explain, troubleshoot and
defend in a technical interview.
