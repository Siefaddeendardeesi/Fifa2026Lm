# MLflow Model Registry

## Overview

FIFA2026Lm uses MLflow Model Registry for production model versioning alongside the local file-based registry in `data/processed/models/registry/`.

| Setting | Env Variable | Default |
|---------|--------------|---------|
| Tracking URI | `MLFLOW_TRACKING_URI` | `file:./mlruns` |
| Registry URI | `MLFLOW_REGISTRY_URI` | same as tracking |
| Model name | `CHAMPION_MODEL_NAME` | `champion` |
| Experiment | `MLFLOW_EXPERIMENT_NAME` | `fifa2026-match-outcome` |

## Register Champion Model

After training, register the champion:

```bash
python scripts/register_mlflow_champion.py
```

This script:

1. Finds the latest finished MLflow run with a `model` artifact (or uses `--run-id`)
2. Registers it as `champion` in Model Registry
3. Transitions the version to **Production**
4. Archives any previous Production versions

## Promotion Workflow

```
Train (ModelTrainer)
  └─> mlflow.sklearn.log_model(..., artifact_path="model")
        └─> register_mlflow_champion.py
              └─> mlflow.register_model("runs:/<run_id>/model", "champion")
                    └─> transition_model_version_stage(..., "Production")
```

### Stages

| Stage | Purpose |
|-------|---------|
| Production | Live champion served by API and dashboard |
| Staging | Pre-production validation |
| Archived | Superseded versions |

Programmatic promotion:

```python
from src.models.mlflow_registry import promote_model_version

promote_model_version("champion", version="2", stage="Production")
```

## Verification

```bash
bash scripts/verify_mlflow.sh
```

Expected output includes a Production-stage model, e.g. `champion v1 in Production stage`.

## Docker Compose

In Docker, MLflow uses PostgreSQL as the backend store. Set in `docker/.env`:

```env
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_REGISTRY_URI=http://mlflow:5000
```

## CI Integration

The `mlflow-registry` CI job runs `register_mlflow_champion.py` and `verify_mlflow.sh` on every test pipeline completion.
