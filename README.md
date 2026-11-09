# GitLab CI/CD Platform

A small FastAPI application that will be tested, built, published and deployed
automatically by a GitLab CI/CD pipeline onto a Linux server running Docker Compose.

> **Status:** Phase 1 — application foundation (no Docker or CI yet).

## Target architecture

```
Developer -> GitLab Repository -> GitLab CI/CD -> GitLab Runner
   Pipeline: validate -> test -> build -> publish -> deploy -> verify
```

## API endpoints

| Method | Path              | Description                        |
|--------|-------------------|------------------------------------|
| GET    | `/`               | Application information            |
| GET    | `/health`         | Health check                       |
| GET    | `/api/status`     | Application status and uptime      |
| GET    | `/api/users`      | List example users                 |
| GET    | `/api/users/{id}` | One user (404 if it does not exist)|

Interactive documentation is generated automatically at `/docs`.

## Project structure

```
app/            Application code (FastAPI)
tests/          Automated tests (Pytest)
requirements.txt  Python dependencies
```

## Run locally (Windows / PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the tests
pytest -v

# Start the API at http://127.0.0.1:8000
uvicorn app.main:app --reload
```

## Configuration

| Variable      | Default       | Purpose                   |
|---------------|---------------|---------------------------|
| `APP_ENV`     | `development` | Environment name          |
| `APP_VERSION` | `1.0.0`       | Version shown by the API  |

## Roadmap

1. Application foundation (current)
2. Local Docker environment
3. Git and GitLab
4. GitLab CI/CD and Runner
5. Container registry
6. Linux deployment
7. Security and improvements
8. Documentation
