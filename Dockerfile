# Small official Python image (Debian "slim" = fewer packages, smaller attack surface)
FROM python:3.12-slim

# Don't write .pyc files; print logs immediately instead of buffering them
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first: Docker caches this layer and only re-runs it
# when requirements.txt changes, which makes rebuilds much faster.
# Tests/dev tools are not needed at runtime, so we install only what the API needs.
COPY requirements.txt .
RUN grep -Ev '^(pytest|httpx)|^#|^$' requirements.txt > requirements-runtime.txt \
    && pip install --no-cache-dir -r requirements-runtime.txt \
    && rm requirements-runtime.txt

COPY app ./app

# Run as a non-root user: if the app is compromised, the attacker has fewer rights
RUN useradd --system --no-create-home appuser
USER appuser

EXPOSE 8000

# Python is already in the image, so we use it for the check (no curl needed)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# 0.0.0.0 = listen on all interfaces, otherwise the port mapping can't reach the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
