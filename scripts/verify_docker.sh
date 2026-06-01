#!/usr/bin/env bash
# Validate Docker image build and container health.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_DIR="${ROOT}/docker"
ENV_FILE="${COMPOSE_DIR}/.env"

cd "${ROOT}"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker CLI not found"
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Creating ${ENV_FILE} from docker/.env.example"
  cp "${COMPOSE_DIR}/.env.example" "${ENV_FILE}"
fi

echo "==> Validating compose configuration"
docker compose -f "${COMPOSE_DIR}/docker-compose.yml" --env-file "${ENV_FILE}" config >/dev/null
docker compose \
  -f "${COMPOSE_DIR}/docker-compose.yml" \
  -f "${COMPOSE_DIR}/docker-compose.prod.yml" \
  --env-file "${ENV_FILE}" config >/dev/null

echo "==> Building API image"
docker compose -f "${COMPOSE_DIR}/docker-compose.yml" --env-file "${ENV_FILE}" build api

echo "==> Starting API service"
docker compose -f "${COMPOSE_DIR}/docker-compose.yml" --env-file "${ENV_FILE}" up -d api

echo "==> Waiting for /health"
for _ in $(seq 1 30); do
  if curl -sf "http://localhost:${API_PORT:-8000}/health" >/dev/null; then
    echo "API health check passed"
    docker compose -f "${COMPOSE_DIR}/docker-compose.yml" --env-file "${ENV_FILE}" down
    exit 0
  fi
  sleep 2
done

echo "ERROR: API health check failed"
docker compose -f "${COMPOSE_DIR}/docker-compose.yml" --env-file "${ENV_FILE}" logs api || true
docker compose -f "${COMPOSE_DIR}/docker-compose.yml" --env-file "${ENV_FILE}" down || true
exit 1
