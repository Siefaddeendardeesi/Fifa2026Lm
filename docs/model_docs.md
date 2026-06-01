# Model Documentation

## Problem

Multi-class classification: predict match outcome from the **home team perspective**.

| Label | Code | Meaning |
|-------|------|---------|
| Win | 0 | Home team wins |
| Draw | 1 | Tie |
| Loss | 2 | Home team loses |

## Supported Models

| Type | Key | Default Use |
|------|-----|-------------|
| Logistic Regression | `logistic_regression` | Baseline / interpretability |
| Random Forest | `random_forest` | Non-linear baseline |
| XGBoost | `xgboost` | **Default champion** |
| LightGBM | `lightgbm` | Speed-optimized |
| CatBoost | `catboost` | Categorical-heavy data |

All models implement `BaseModel` with `build_pipeline()`, `prepare_xy()`, and `get_default_params()`.

## Training

```bash
python scripts/train_baseline.py --model-type xgboost
python scripts/cli.py  # with --tune --register flags
```

- Train cutoff: before 2022-01-01 (default split)
- Test set: 2022-01-01 onward
- Preprocessing: median imputation (numeric), one-hot encoding (categorical)
- Tracking: MLflow parameters, metrics, artifacts

## Hyperparameter Tuning

Optuna with stratified k-fold CV, median pruner. Best params saved to `data/processed/reports/{model}_optuna_report.json`.

## Evaluation Metrics

Accuracy, precision/recall/F1 (macro), ROC AUC (OvR), log loss. Reports include confusion matrix, calibration curves, feature importance, and SHAP summary.

## Model Registry

Local registry at `data/processed/models/registry/`:

- **Register** — copy artifact with version timestamp
- **Promote** — set champion, copy to `baseline_model.joblib`
- **Rollback** — re-promote any archived version

### MLflow Model Registry

Production models are registered in MLflow Model Registry under the name configured by `CHAMPION_MODEL_NAME` (default: `champion`).

```bash
# Register champion from latest MLflow run with model artifact
python scripts/register_mlflow_champion.py

# Force re-register from a specific run
python scripts/register_mlflow_champion.py --run-id <RUN_ID> --force

# Register during training CLI
python scripts/cli.py --register-mlflow
```

Promotion workflow:

1. Training logs sklearn model to MLflow (`artifact_path=model`)
2. `register_mlflow_champion.py` registers the model and transitions it to **Production**
3. Previous Production versions are archived automatically
4. Verify with `bash scripts/verify_mlflow.sh`

See [mlflow_registry.md](mlflow_registry.md) for full registry operations.

## Inference

Match probabilities used by:
- `/predict` API endpoint
- Streamlit Predictions page
- Monte Carlo simulation (precomputed cache for all 48×47 ordered pairs)
- Team ranking engine (average win probability vs pool)

## Reproducibility

Fixed `random_seed=42` in settings. Set via `RANDOM_SEED` env var. See [reproducibility_guide.md](reproducibility_guide.md).
