#!/usr/bin/env bash
# Verify Streamlit dashboard responds.
set -euo pipefail

BASE_URL="${STREAMLIT_BASE_URL:-http://localhost:8501}"

echo "==> Checking Streamlit health endpoint"
for _ in $(seq 1 30); do
  if curl -sf "${BASE_URL}/_stcore/health" >/dev/null 2>&1; then
    echo "Streamlit health check passed"
    exit 0
  fi
  sleep 2
done

echo "ERROR: Streamlit did not become ready at ${BASE_URL}"
exit 1
