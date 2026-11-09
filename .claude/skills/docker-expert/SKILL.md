---
name: docker-expert
description: Docker expertise for writing and reviewing Dockerfiles, multi-stage builds, Docker Compose files, container networking and volumes, image size optimization, container security hardening, and troubleshooting. Use when containerizing an app, editing Dockerfile or compose.yaml, shrinking images, or debugging containers that fail to build, start, or connect.
---

# Docker Expert

## Rules
- Inspect existing Dockerfile/compose files first; preserve conventions unless there is a reason.
- Never put secrets in images, build args, or compose files committed to git.
- Ask before destructive commands (`docker system prune -a`, `docker volume rm`, `down -v`): volumes can hold database data.

## Dockerfile best practices
- Pin base image versions (`python:3.12-slim`, `node:22-alpine`), never `latest`. Pin by digest for high-security builds.
- Order layers from least to most frequently changing: copy dependency manifests, install, then copy source.
- Combine `apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*` in one layer.
- Use `.dockerignore` (`.git`, `node_modules`, `.env`, `__pycache__`, `*.log`).
- Run as non-root; add `HEALTHCHECK`; use exec-form `CMD ["..."]` so signals reach the process.
- Use `COPY` not `ADD`; use BuildKit cache mounts for package managers.

## Multi-stage examples
FastAPI:
```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 app
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && rm -rf /wheels
COPY --chown=app:app . .
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Next.js (standalone output; requires `output: "standalone"` in next.config):
```dockerfile
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci
FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

## Docker Compose (v2, file `compose.yaml`, no `version:` key)
```yaml
services:
  api:
    build: ./backend
    env_file: .env
    depends_on:
      db: { condition: service_healthy }
    networks: [internal, web]
    restart: unless-stopped
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets: [db_password]
    volumes: [pgdata:/var/lib/postgresql/data]
    networks: [internal]          # not published to the host
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10
networks:
  internal: { internal: true }
  web: {}
volumes:
  pgdata:
secrets:
  db_password:
    file: ./secrets/db_password.txt
```
Commands: `docker compose up -d --build`, `docker compose ps`, `docker compose logs -f api`, `docker compose config` (validate and view the resolved file), `docker compose down` (add `-v` only with approval).

## Networking and volumes
- Containers on the same user-defined network reach each other by service name (`db:5432`), not `localhost`.
- `ports: "8080:80"` publishes to the host; bind locally with `"127.0.0.1:5432:5432"` if needed. Do not publish databases publicly.
- Named volumes for persistent data; bind mounts for dev source code only. Backup: `docker run --rm -v pgdata:/d -v "$PWD":/b alpine tar czf /b/pgdata.tgz -C /d .`
- Inspect: `docker network ls`, `docker network inspect <n>`, `docker volume ls`, `docker inspect <c>`.

## Image optimization
- Prefer `-slim` or `alpine` (alpine uses musl; some Python wheels build slowly or break, so use slim for Python).
- Multi-stage so build tools stay out of the final image; install only production dependencies.
- Measure: `docker images`, `docker history <image>`, `docker system df`. Tools like `dive` help inspect layers.
- Use BuildKit (default) and registry cache: `docker buildx build --cache-from type=registry,ref=... --cache-to type=inline`.

## Container security
- Non-root `USER`; `read_only: true` with `tmpfs` for writable paths; `cap_drop: [ALL]`; `security_opt: [no-new-privileges:true]`.
- Never mount `/var/run/docker.sock` or use `privileged: true` unless unavoidable (it is root-equivalent on the host).
- Scan images: `trivy image <image>` (fail CI on HIGH/CRITICAL); scan Dockerfiles with `hadolint`.
- Use trusted official images, rebuild regularly for patches, set resource limits (`mem_limit`, `cpus`).
- Secrets via runtime env/secret files or Compose secrets, never `ENV`/`ARG` in the Dockerfile.

## Troubleshooting
| Symptom | Check |
|---|---|
| Container exits immediately | `docker logs <c>`; `docker inspect -f '{{.State.ExitCode}}' <c>`; wrong CMD/missing env |
| Cannot connect between services | same network? using service name? app bound to `0.0.0.0` not `127.0.0.1`? |
| Build slow / cache miss | layer order; `.dockerignore`; copy manifests before source |
| `permission denied` on volume | UID mismatch; `chown` in image or volume |
| Port already allocated | `docker ps`; `ss -tulpn` (Linux) / `netstat -ano` (Windows) |
| No space left | `docker system df`; ask before `docker system prune` |
Debug shell: `docker exec -it <c> sh`, or `docker run --rm -it --entrypoint sh <image>`.
