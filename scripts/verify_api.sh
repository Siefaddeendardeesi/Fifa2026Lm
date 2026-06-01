#!/usr/bin/env bash
# Smoke-test FastAPI endpoints.
set -euo pipefail

BASE_URL="${API_BASE_URL:-http://localhost:8000}"

echo "==> GET /health"
curl -sf "${BASE_URL}/health" | grep -q '"status"'

echo "==> GET /teams"
curl -sf "${BASE_URL}/teams" | grep -q '"count"'

echo "==> GET /groups"
curl -sf "${BASE_URL}/groups" | grep -q '"group_count"'

echo "==> GET /rankings"
curl -sf "${BASE_URL}/rankings?method=elo&pool_size=8&since=2020-01-01" | grep -q '"rankings"'

echo "==> POST /predict"
curl -sf -X POST "${BASE_URL}/predict" \
  -H "Content-Type: application/json" \
  -d '{"home_team":"Brazil","away_team":"Argentina","neutral":true}' | grep -q '"home_win"'

echo "==> POST /simulate"
curl -sf -X POST "${BASE_URL}/simulate" \
  -H "Content-Type: application/json" \
  -d '{"n_simulations":10,"seed":42}' | grep -q '"n_simulations"'

echo "==> GET /metrics"
curl -sf "${BASE_URL}/metrics" | grep -q "fifa_prediction_latency_seconds"

echo "All API smoke tests passed"
