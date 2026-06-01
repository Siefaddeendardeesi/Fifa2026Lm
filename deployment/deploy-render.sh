#!/usr/bin/env bash
# Deploy to Render
set -euo pipefail

RENDER_API_KEY="${RENDER_API_KEY:?Set RENDER_API_KEY}"
SERVICE_ID="${RENDER_SERVICE_ID:?Set RENDER_SERVICE_ID}"

curl -X POST "https://api.render.com/v1/services/${SERVICE_ID}/deploys" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"clearCache": false}'

echo "Render deploy triggered for service ${SERVICE_ID}"
