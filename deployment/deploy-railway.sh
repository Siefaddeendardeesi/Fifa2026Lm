#!/usr/bin/env bash
# Deploy to Railway
set -euo pipefail

RAILWAY_TOKEN="${RAILWAY_TOKEN:?Set RAILWAY_TOKEN}"

npm install -g @railway/cli 2>/dev/null || true
railway login --token "$RAILWAY_TOKEN"
railway up --dockerfile docker/Dockerfile

echo "Railway deployment initiated"
