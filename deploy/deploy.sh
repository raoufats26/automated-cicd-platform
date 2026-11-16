#!/usr/bin/env bash
# Deploys the image given in $IMAGE on this server, then checks /health.
# Run by the GitLab Runner installed on the server (see docs/DEPLOYMENT.md).
set -euo pipefail   # stop at the first error, on unset variables, and on pipe failures

# Always remove the registry credential when the script ends (success or failure)
trap 'docker logout "$CI_REGISTRY" >/dev/null 2>&1' EXIT

: "${IMAGE:?IMAGE is not set}"
: "${CI_REGISTRY:?CI_REGISTRY is not set}"
: "${CI_JOB_TOKEN:?CI_JOB_TOKEN is not set}"

COMPOSE="docker compose -p fastapi-cicd -f deploy/docker-compose.deploy.yml"
HEALTH_URL="http://localhost:8000/health"

echo "==> Logging in to $CI_REGISTRY"
echo "$CI_JOB_TOKEN" | docker login -u gitlab-ci-token --password-stdin "$CI_REGISTRY"

echo "==> Pulling $IMAGE"
$COMPOSE pull

echo "==> Starting the new version"
$COMPOSE up -d

echo "==> Waiting for $HEALTH_URL"
for i in $(seq 1 15); do
  if curl -fsS "$HEALTH_URL" > /dev/null; then
    echo "Healthy after $i attempt(s):"
    curl -fsS "$HEALTH_URL"; echo
    $COMPOSE ps
    exit 0
  fi
  sleep 2
done

echo "ERROR: application did not become healthy. Container logs:"
$COMPOSE logs --tail 50
exit 1
