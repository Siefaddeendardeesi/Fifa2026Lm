# Production Go-Live Checklist

Use this checklist before deploying FIFA2026Lm to production.

## 1. Code Quality

- [ ] `ruff check src app tests scripts monitoring` — zero errors
- [ ] `black --check src app tests scripts monitoring` — pass
- [ ] `isort --check-only src app tests scripts monitoring` — pass
- [ ] `mypy src app monitoring` — zero errors

## 2. Tests & Coverage

- [ ] `pytest tests/ --cov=src --cov=app --cov-fail-under=90` — all pass, ≥ 90% coverage
- [ ] E2E API tests pass (`tests/e2e/test_api.py`)

## 3. Security

- [ ] `pip install -e ".[dev]" && pip-audit` — zero high/medium vulnerabilities on **runtime** dependencies
- [ ] Secrets externalized (no hardcoded passwords in compose or code)
- [ ] `docker/.env` created from `docker/.env.example` with strong passwords
- [ ] Root `.env` not committed to version control
- [ ] API rate limiting enabled (`API_RATE_LIMIT`)
- [ ] Security headers middleware active

## 4. Docker & Compose

- [ ] Copy `docker/.env.example` → `docker/.env` and set all required values
- [ ] `docker compose -f docker/docker-compose.yml --env-file docker/.env config` — valid
- [ ] `docker compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml --env-file docker/.env config` — valid
- [ ] `bash scripts/verify_docker.sh` — image builds, API health passes
- [ ] All services start: api, dashboard, postgres, mlflow, prometheus, grafana, nginx

## 5. API & Dashboard

- [ ] `bash scripts/verify_api.sh` — all endpoints respond correctly
- [ ] `bash scripts/verify_streamlit.sh` — dashboard health passes
- [ ] Champion model loaded (`GET /health` → `model_loaded: true`)

## 6. MLflow & Models

- [ ] `python scripts/register_mlflow_champion.py` — champion registered
- [ ] `bash scripts/verify_mlflow.sh` — Production model exists
- [ ] Local registry champion at `data/processed/baseline_model.joblib` or `models/champion_model.joblib`

## 7. Data Pipeline (Optional Pre-Go-Live)

- [ ] `pip install -e ".[pipeline]"` for DVC (dev/CI only)
- [ ] `dvc repro` — pipeline succeeds
- [ ] Feature parquet and model artifacts present in `data/processed/`

## 8. CI/CD

- [ ] GitHub Actions CI green (lint, test, security, compose-config, mlflow-registry, docker)
- [ ] Release workflow tested with tag push (optional)

## 9. Deployment

- [ ] Target cloud credentials configured
- [ ] Deployment script validated: `bash -n deployment/deploy-<target>.sh`
- [ ] `docs/deployment_guide.md` steps reviewed for target platform
- [ ] Monitoring: Prometheus scraping `/metrics`, Grafana dashboard loaded

## 10. Post-Deploy Smoke Test

- [ ] `GET /health` → 200
- [ ] `POST /predict` with known teams → valid probabilities
- [ ] Streamlit dashboard loads all pages
- [ ] MLflow UI shows Production model

---

**Sign-off**

| Role | Name | Date | Approved |
|------|------|------|----------|
| Engineering | | | |
| DevOps | | | |
| QA | | | |
