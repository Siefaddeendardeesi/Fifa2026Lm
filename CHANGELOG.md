# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-31

### Added

- Production project structure (`app/`, `src/`, `tests/`, `docker/`, `docs/`)
- Pydantic-settings configuration with dev/test/staging/production profiles
- Pandera data validation with validation reports
- ETL orchestration layer with metadata, checksums, and source versioning
- Feature store with registry, transformers, and lineage tracking
- Modular ML framework: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost
- Optuna hyperparameter tuning with cross-validation
- MLflow experiment tracking and local model registry (champion/challenger)
- Model evaluation HTML reports with confusion matrix, calibration, SHAP, feature importance
- Monte Carlo simulation engine (48 teams, 12 groups, 32-team knockout, multiprocessing)
- Team ranking engine: ELO, model-based, and hybrid methods
- FastAPI REST API with rate limiting, security headers, and Prometheus metrics
- Streamlit dashboard with Overview, Groups, Predictions, Simulation, Rankings, Squads, Analytics
- Docker multi-stage build and Docker Compose stack (API, dashboard, MLflow, Postgres, Nginx, Grafana)
- GitHub Actions CI/CD pipeline (lint, test, security scan, build, Docker)
- Deployment scripts for Azure, AWS, GCP, Render, and Railway
- DVC pipeline configuration for data and model versioning
- Comprehensive test suite (unit, integration, e2e) with 90%+ coverage target
- Structured logging via structlog

### Changed

- Refactored legacy `app.py` to use `app/dashboard/main.py`
- Enhanced ETL downloads with retry logic, exponential backoff, and caching
- Migrated config from hardcoded paths to environment-driven settings

### Security

- Secrets via environment variables (`.env.example` template)
- API rate limiting and security response headers
- Non-root Docker container user

[1.0.0]: https://github.com/example/fifa2026lm/releases/tag/v1.0.0
