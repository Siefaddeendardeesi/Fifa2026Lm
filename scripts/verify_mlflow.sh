#!/usr/bin/env bash
# Verify MLflow tracking and model registry.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-file:./mlruns}"
export MLFLOW_REGISTRY_URI="${MLFLOW_REGISTRY_URI:-${MLFLOW_TRACKING_URI}}"

echo "==> Ensuring champion model is registered"
python scripts/register_mlflow_champion.py

echo "==> Verifying registry state"
python - <<'PY'
import sys

from src.models.mlflow_registry import get_production_model_version, registry_summary

summary = registry_summary()
production = get_production_model_version()
if summary["registered_model_count"] < 1:
    print("ERROR: no registered models found", file=sys.stderr)
    sys.exit(1)
if production is None:
    print("ERROR: no Production-stage model found", file=sys.stderr)
    sys.exit(1)
print(f"OK: {production.name} v{production.version} in Production stage")
PY

echo "MLflow registry verification passed"
