"""Small FastAPI application used as the target of the CI/CD pipeline."""

import os
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

APP_NAME = "gitlab-cicd-platform"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("APP_ENV", "development")

_started_at = time.time()

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Demo API deployed through a GitLab CI/CD pipeline.",
)


class User(BaseModel):
    id: int
    name: str
    email: str


# In-memory data: stands in for a database in this project.
USERS: list[User] = [
    User(id=1, name="Alice Martin", email="alice@example.com"),
    User(id=2, name="Bob Karim", email="bob@example.com"),
    User(id=3, name="Chloe Dupont", email="chloe@example.com"),
]


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a consistent JSON body for every 404 error."""
    detail = getattr(exc, "detail", "Not Found")
    if detail == "Not Found":
        detail = f"Route '{request.url.path}' does not exist"
    return JSONResponse(status_code=404, content={"error": detail})


@app.get("/")
def root() -> dict:
    """Application information."""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "docs": "/docs",
        "message": "Deployed by GitLab CI/CD",
    }


@app.get("/health")
def health() -> dict:
    """Health check, used by Docker and the pipeline to verify a deployment."""
    return {"status": "healthy"}


@app.get("/api/status")
def status() -> dict:
    """Application status."""
    return {
        "status": "running",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "uptime_seconds": round(time.time() - _started_at, 2),
    }


@app.get("/api/users", response_model=list[User])
def list_users() -> list[User]:
    """Example users endpoint."""
    return USERS


@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    """Return one user, or 404 if it does not exist."""
    for user in USERS:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail=f"User {user_id} not found")
