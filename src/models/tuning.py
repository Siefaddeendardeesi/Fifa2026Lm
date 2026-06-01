"""Optuna hyperparameter tuning."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import optuna
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score

from src.config.settings import get_settings
from src.models.base import get_model
from src.utils.logging import get_logger
from src.utils.seeds import set_global_seed

logger = get_logger(__name__)

SEARCH_SPACES: dict[str, dict[str, tuple[Any, Any]]] = {
    "xgboost": {
        "n_estimators": (100, 500),
        "max_depth": (3, 10),
        "learning_rate": (0.01, 0.3),
    },
    "lightgbm": {
        "n_estimators": (100, 500),
        "max_depth": (3, 10),
        "learning_rate": (0.01, 0.3),
    },
    "catboost": {
        "iterations": (100, 500),
        "depth": (3, 10),
        "learning_rate": (0.01, 0.3),
    },
    "random_forest": {
        "n_estimators": (100, 400),
        "max_depth": (4, 20),
    },
    "logistic_regression": {
        "C": (0.01, 10.0),
    },
}


class HyperparameterTuner:
    """Optuna-based hyperparameter optimization."""

    def __init__(self, model_type: str = "xgboost", n_trials: int = 30) -> None:
        self.model_type = model_type
        self.n_trials = n_trials
        self.settings = get_settings()
        self.model_impl = get_model(model_type)

    def tune(
        self,
        train_df: pd.DataFrame,
        *,
        n_folds: int = 3,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Run Optuna study with cross-validation."""
        set_global_seed()
        x, y = self.model_impl.prepare_xy(train_df)
        space = SEARCH_SPACES.get(self.model_type, {})

        def objective(trial: optuna.Trial) -> float:
            params: dict[str, Any] = {}
            for name, bounds in space.items():
                low, high = bounds
                if isinstance(low, int) and isinstance(high, int):
                    params[name] = trial.suggest_int(name, low, high)
                else:
                    params[name] = trial.suggest_float(name, float(low), float(high), log=True)

            pipeline = self.model_impl.build_pipeline(list(x.columns))
            pipeline.set_params(**{f"classifier__{k}": v for k, v in params.items()})

            cv = StratifiedKFold(
                n_splits=n_folds, shuffle=True, random_state=self.settings.random_seed
            )
            scores = cross_val_score(pipeline, x, y, cv=cv, scoring="f1_macro", n_jobs=-1)
            return float(np.mean(scores))

        study = optuna.create_study(direction="maximize", pruner=optuna.pruners.MedianPruner())
        study.optimize(objective, n_trials=self.n_trials, timeout=timeout, show_progress_bar=False)

        result = {
            "model_type": self.model_type,
            "best_params": study.best_params,
            "best_score": study.best_value,
            "n_trials": len(study.trials),
        }

        report_path = self.settings.reports_dir / f"{self.model_type}_optuna_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        logger.info("tuning_complete", **result)
        return result
