# Architecture

## Overview

FIFA2026LM is a production ML platform for predicting international football match outcomes, simulating the 2026 World Cup, and ranking national teams.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Streamlit  │     │   FastAPI    │     │  GitHub Actions │
│  Dashboard  │     │     API      │     │     CI/CD       │
└──────┬──────┘     └──────┬───────┘     └─────────────────┘
       │                   │
       └─────────┬─────────┘
                 ▼
       ┌─────────────────────┐
       │   Service Layer     │
       │ (Prediction, Sim,   │
       │  Rankings, Teams)   │
       └─────────┬───────────┘
                 ▼
┌────────────────────────────────────────────────────────┐
│                      src/                              │
│  etl → features → models → simulation → rankings       │
└────────────────────────────────────────────────────────┘
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
  data/ (DVC)         mlruns/ (MLflow)
```

## Layers

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Presentation | `app/dashboard/`, `app/api/` | UI and REST endpoints |
| Services | `app/services/` | Business logic orchestration |
| Domain | `src/` | ETL, features, ML, simulation, rankings |
| Infrastructure | `docker/`, `deployment/`, `monitoring/` | Deployment and observability |
| Config | `src/config/` | Environment-driven settings |

## Data Flow

1. **Download** — Raw CSVs from Kaggle, GitHub, eloratings.net
2. **Validate** — Pandera schemas on matches and features
3. **Transform** — ELO, FIFA rankings, form, WC titles, squad values
4. **Train** — Multi-model framework with MLflow tracking
5. **Serve** — Champion model via API and dashboard
6. **Simulate** — Monte Carlo tournament with cached match probabilities

## Key Design Decisions

- **Settings singleton** via pydantic-settings; no hardcoded paths
- **Feature store** decouples feature engineering from model code
- **Model registry** supports champion/challenger promotion and rollback
- **Backward-compatible shims** in `src/models/ranking.py` and `tournament.py`

## Technology Stack

Python 3.12, pandas, scikit-learn, XGBoost/LightGBM/CatBoost, Optuna, MLflow, FastAPI, Streamlit, Pandera, structlog, Prometheus, Docker, DVC, pytest.
