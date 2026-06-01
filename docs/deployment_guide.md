# Deployment Guide

## Prerequisites

- Python 3.12+
- Docker & Docker Compose (for containerized deployment)
- Trained model at `data/processed/baseline_model.joblib`
- Feature matrix at `data/processed/features.parquet`

## Local Development

```bash
pip install -e ".[dev]"
cp .env.example .env
python scripts/download_data.py --skip-kaggle
python scripts/build_features.py
python scripts/train_baseline.py

# API
uvicorn app.api.main:app --reload --port 8000

# Dashboard
streamlit run app/dashboard/main.py
```

## Docker Compose

```bash
cd docker
docker compose up --build
```

| Service | Port | URL |
|---------|------|-----|
| API | 8000 | http://localhost:8000/docs |
| Dashboard | 8501 | http://localhost:8501 |
| MLflow | 5000 | http://localhost:5000 |
| Grafana | 3000 | http://localhost:3000 |
| Prometheus | 9090 | http://localhost:9090 |
| Nginx | 80 | http://localhost/ |

## Cloud Deployment

Scripts in `deployment/`:

| Platform | Script | Required Env Vars |
|----------|--------|-------------------|
| Azure | `deploy-azure.sh` | `AZURE_RESOURCE_GROUP`, `AZURE_ACR_NAME` |
| AWS | `deploy-aws.sh` | `AWS_REGION`, `ECR_REPO`, `ECS_CLUSTER` |
| GCP | `deploy-gcp.sh` | `GCP_PROJECT_ID` |
| Render | `deploy-render.sh` | `RENDER_API_KEY`, `RENDER_SERVICE_ID` |
| Railway | `deploy-railway.sh` | `RAILWAY_TOKEN` |

## Environment Variables

See `.env.example`. Critical production settings:

```
ENVIRONMENT=production
LOG_JSON=true
MLFLOW_TRACKING_URI=http://mlflow:5000
API_RATE_LIMIT=100/minute
```

## Health Checks

- API: `GET /health` — returns model_loaded status
- Docker: built-in HEALTHCHECK on port 8000

## Monitoring

Prometheus scrapes `/metrics` from the API. Grafana dashboard at `monitoring/grafana/dashboard.json` tracks prediction latency, errors, confidence, and simulation duration.

## DVC Data Pipeline

```bash
dvc repro          # Run full pipeline
dvc push           # Push artifacts to remote
dvc pull           # Pull from remote
```

Configure remote in `.dvc/config` (local, S3, Azure, GCS).
