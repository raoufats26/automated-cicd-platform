---
name: devops-engineer
description: General DevOps engineering guidance covering CI/CD architecture, Linux server administration, infrastructure automation, deployment strategies (rolling, blue-green, canary), infrastructure security hardening, and troubleshooting. Use when designing pipelines or deployment flows, setting up or hardening Linux servers, writing automation scripts, or diagnosing failing deployments and services.
---

# DevOps Engineer

## Principles
- Automate anything done twice; keep everything in version control (pipelines, scripts, configs).
- Prefer simple, reproducible, idempotent steps. Fail fast (`set -euo pipefail` in shell).
- Security first: least privilege, no secrets in code or images, pin versions, verify before trusting.
- Inspect the existing project before proposing changes. Ask before destructive actions (deleting volumes, `rm -rf`, force pushes, dropping data, rebooting servers).
- Explain decisions simply; the user is a beginner.

## CI/CD architecture
Standard flow: `lint -> test -> build -> scan -> publish -> deploy(staging) -> deploy(production)`.
- Build once, deploy the same immutable artifact (image tagged with commit SHA) to every environment.
- Keep config outside the artifact (environment variables / secret store).
- Gate production behind a manual approval or protected branch/tag.
- Cache dependencies; run independent jobs in parallel; keep pipelines under ~10 minutes.
- Always include a rollback path (previous image tag stays available).

## Deployment strategies
| Strategy | Use when | Rollback |
|---|---|---|
| Recreate | Downtime acceptable, simplest | Redeploy old version |
| Rolling | Multiple replicas, no downtime | Roll back to previous tag |
| Blue-green | Need instant switch and rollback | Switch traffic back |
| Canary | Want to test on a small share of users | Stop canary, route to stable |

Always add a health check (`/health` endpoint) and verify it after deploy before declaring success.

## Linux administration (Ubuntu/Debian examples)
```bash
# Inspect system
uname -a; lsb_release -a; uptime; df -h; free -m
ss -tulpn                      # listening ports
systemctl status <svc>; journalctl -u <svc> -n 100 --no-pager
top -o %CPU   # or: ps aux --sort=-%mem | head

# Users and SSH
sudo adduser deploy && sudo usermod -aG docker deploy   # note: docker group ~ root-equivalent
mkdir -p ~/.ssh && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```
Server hardening checklist:
1. Key-only SSH: in `/etc/ssh/sshd_config` set `PasswordAuthentication no`, `PermitRootLogin no`; validate with `sudo sshd -t` before `sudo systemctl reload ssh` and keep a second session open.
2. Firewall: `sudo ufw default deny incoming && sudo ufw allow OpenSSH && sudo ufw allow 80,443/tcp && sudo ufw enable` (allow SSH first or you lock yourself out).
3. Automatic security updates: `sudo apt install unattended-upgrades`.
4. `fail2ban` for SSH brute force; dedicated non-root `deploy` user.
5. Never expose database ports (5432) publicly.

## Infrastructure automation
- Shell for small tasks; Ansible for multi-host config (idempotent, agentless over SSH); Terraform/OpenTofu for cloud resources. Do not add these tools unless the project needs them.
- Script template:
```bash
#!/usr/bin/env bash
set -euo pipefail
trap 'echo "failed at line $LINENO" >&2' ERR
```
- Test with a dry run where possible (`ansible-playbook --check`, `terraform plan`).

## Infrastructure security
- Secrets: CI/CD masked + protected variables or a secret manager; never commit `.env`. Rotate if leaked (deleting the commit is not enough).
- Use dedicated deploy keys with minimal scope; one key per purpose.
- Scan: dependencies, container images (Trivy), secrets (gitleaks), IaC.
- TLS everywhere (Let's Encrypt / certbot or a reverse proxy like Caddy/Traefik/nginx).
- Log and monitor: health checks, `journalctl`, container logs, disk usage alerts.

## Troubleshooting method
1. Reproduce and read the exact error; check the most recent change first.
2. Narrow the layer: code -> build -> image -> network -> host -> DNS/TLS.
3. Check the basics: disk full (`df -h`), memory (`free -m`), ports (`ss -tulpn`), permissions, wrong env vars, time/DNS.
4. Logs: `journalctl -xe`, `docker logs --tail 100 <c>`, pipeline job log.
5. Change one thing at a time; record the fix.

Common causes: `Permission denied (publickey)` (wrong key/permissions/user), `no space left on device` (`docker system df`), port already in use (`ss -tulpn | grep :PORT`), service restarts in a loop (`journalctl -u`), works locally but not in CI (env/version differences).
