# Reproducibility Guide

## Random Seeds

| Component | Control |
|-----------|---------|
| Global | `RANDOM_SEED=42` in `.env` or `Settings.random_seed` |
| Training | `set_global_seed()` before fit |
| Optuna | `random_state` in CV splits |
| Simulation | `seed` parameter in `SimulationEngine.run()` |

## Environment Pinning

```bash
pip install -e ".[dev]"
python --version   # 3.12+
pip freeze > requirements-lock.txt
```

Docker images use `python:3.12-slim` for deterministic runtime.

## Data Versioning

```bash
dvc repro                    # Rebuild pipeline from dvc.yaml
dvc push / dvc pull          # Sync with remote storage
```

Tracked artifacts: raw data, features, train/test splits, model.

## MLflow Experiments

Every training run logs:
- Hyperparameters
- Metrics (accuracy, F1, log loss, ROC AUC)
- Model artifact and evaluation HTML report

Retrieve: `mlflow ui --backend-store-uri file:./mlruns`

## Feature Lineage

`data/metadata/feature_lineage.json` records transformer versions and row counts.

## ETL Metadata

`data/metadata/etl_metadata.json` stores source checksums (SHA-256) and pipeline run history.

## Verification Checklist

1. Set `RANDOM_SEED=42`
2. Run `dvc repro` or full ETL + train pipeline
3. Compare model metrics against prior `baseline_metrics.json`
4. Run simulation with fixed seed — champion probabilities should match within Monte Carlo variance
5. Record `pip freeze`, git commit hash, and DVC lock file in experiment notes

## Split Strategies

| Strategy | Train cutoff | Test start |
|----------|-------------|------------|
| default | 2022-01-01 | 2022-01-01 |
| wc2022 | 2022-11-01 | 2022-11-20 |

Pass `--split wc2022` to build/train scripts.
