---
name: gitlab-cicd
description: GitLab CI/CD expertise for writing and debugging .gitlab-ci.yml, pipeline stages and jobs, GitLab Runner and executors, GitLab Container Registry, CI/CD variables and secrets, SSH deployment, and pipeline optimization. Use when creating or editing .gitlab-ci.yml, registering runners, pushing images to the registry, deploying over SSH, or fixing slow or failing GitLab pipelines.
---

# GitLab CI/CD Expert

## Rules
- Check the existing `.gitlab-ci.yml`, `include:` files, and project settings before editing.
- Validate changes: CI Lint (project > Build > Pipeline editor > Validate) or `glab ci lint`.
- Never hardcode secrets; never `echo` variables; never commit private keys.
- Ask before changing production deploy jobs or protected variables.

## Pipeline skeleton
```yaml
stages: [lint, test, build, deploy]

default:
  image: python:3.12-slim
  interruptible: true

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  IMAGE: "$CI_REGISTRY_IMAGE/api"

workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG

.python-cache:
  cache:
    key:
      files: [requirements.txt]
    paths: [.cache/pip]

test:
  stage: test
  extends: .python-cache
  script:
    - pip install -r requirements.txt
    - pytest --junitxml=report.xml
  artifacts:
    when: always
    reports:
      junit: report.xml
    expire_in: 1 week
```
Key concepts: `stages` (sequential groups), jobs in a stage run in parallel, `needs:` creates a DAG (skip waiting for the whole stage), `rules:` (use instead of deprecated `only/except`), `extends:` and hidden `.jobs` for reuse, `include:` for shared templates, `artifacts` pass files between jobs, `cache` speeds dependencies (not guaranteed).

## Build and push to GitLab Container Registry
Docker-in-Docker (needs a runner with privileged mode):
```yaml
build:
  stage: build
  image: docker:27
  services: [docker:27-dind]
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  script:
    - docker build --pull -t "$IMAGE:$CI_COMMIT_SHORT_SHA" -t "$IMAGE:latest" .
    - docker push "$IMAGE:$CI_COMMIT_SHORT_SHA"
    - docker push "$IMAGE:latest"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```
Predefined vars: `CI_REGISTRY`, `CI_REGISTRY_IMAGE`, `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD` (`CI_JOB_TOKEN` based, short-lived). Alternative without privileged mode: Kaniko/BuildKit rootless. Tag with the commit SHA; use `latest` only as a convenience pointer.
For deploying from a server, create a **deploy token** (`read_registry`) rather than using a personal token.

## Variables and secrets
- Settings > CI/CD > Variables. Enable **Masked** (hidden in logs), **Protected** (only protected branches/tags), and **Hidden** for sensitive values; use type **File** for keys/certs.
- Masking has limits (min 8 chars, restricted charset); do not rely on it alone, since scripts can still leak values.
- Prefer external secret managers (HashiCorp Vault, cloud secret stores) with OIDC `id_tokens` for sensitive production access.
- Scope per environment: `environment: production` plus environment-scoped variables.

## SSH deployment
Setup: create a dedicated key (`ssh-keygen -t ed25519 -f deploy_key -N ""`), add the public key to `~deploy/.ssh/authorized_keys` on the server (optionally restrict with `command=`/`from=`), store the private key as a **File** variable `SSH_PRIVATE_KEY` (Protected) and the server fingerprint as `SSH_KNOWN_HOSTS` (get it with `ssh-keyscan -t ed25519 host`, verify it manually).
```yaml
deploy:
  stage: deploy
  image: alpine:3.20
  environment:
    name: production
    url: https://example.com
  before_script:
    - apk add --no-cache openssh-client
    - install -m 600 -D "$SSH_PRIVATE_KEY" ~/.ssh/id_ed25519
    - install -m 644 -D "$SSH_KNOWN_HOSTS" ~/.ssh/known_hosts
  script:
    - ssh deploy@"$DEPLOY_HOST" "cd /srv/app && docker compose pull && docker compose up -d && docker image prune -f"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
  resource_group: production
```
Do NOT use `StrictHostKeyChecking=no` (enables man-in-the-middle). Use `resource_group` to prevent concurrent deploys. Verify with a health check after `up -d`.

## GitLab Runner
- Executors: **docker** (recommended, isolated per job), **shell** (runs on host, risky, shared state), **kubernetes**, **docker-autoscaler**/instance for scaling.
- Install and register (Linux): after installing `gitlab-runner`, create the runner in the UI (Settings > CI/CD > Runners > New project runner) to get a `glrt-` token, then:
```bash
sudo gitlab-runner register --non-interactive --url https://gitlab.com \
  --token "$RUNNER_TOKEN" --executor docker --docker-image alpine:3.20
sudo gitlab-runner status; sudo gitlab-runner verify
sudo journalctl -u gitlab-runner -n 100
```
- Config lives in `/etc/gitlab-runner/config.toml`; set `privileged = true` only for dind and only on trusted, dedicated runners; use `concurrent` to tune parallelism.
- Use tags to target runners (`tags: [docker]`); mark runners Protected for production jobs.

## Optimization
- `needs:` for a DAG; `parallel:` / `parallel: matrix:` for splitting tests; `interruptible: true` + auto-cancel redundant pipelines.
- Cache keyed on lockfiles; small base images; reuse Docker layer cache (`--cache-from`).
- `rules:changes` to skip irrelevant jobs; `artifacts:expire_in` and minimal `paths`; `GIT_DEPTH: 20` to shallow clone.
- Reuse logic with `include:` + `extends:` + `!reference`.

## Troubleshooting
| Symptom | Likely cause / fix |
|---|---|
| Job stuck "pending" | no runner with matching tags, or runner offline/paused |
| `Cannot connect to the Docker daemon` | missing `services: docker:dind` or `DOCKER_HOST`/TLS vars; runner not privileged |
| `denied: access forbidden` on push | wrong login; registry disabled; pushing to wrong path |
| `Permission denied (publickey)` | wrong key variable, file perms 600, key not in `authorized_keys` |
| Variable empty | variable Protected but branch not protected; wrong environment scope; `$` needs `$$` escaping |
| YAML invalid | run CI Lint; check indentation, quoted `:` in scripts, `rules` syntax |
| Cache never hits | key changes each run; runner cache not shared between runners |
Debug: add `CI_DEBUG_TRACE: "true"` temporarily (it exposes secrets in logs, so remove it and delete the job log afterward), read the full job log, retry on a fresh runner, reproduce locally with the same image.
