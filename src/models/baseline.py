"""Backward-compatible baseline training."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.config.constants import CATEGORICAL_COLS, FEATURE_COLS, NUMERIC_COLS
from src.config.settings import get_settings
from src.models.base import XGBoostModel, get_model
from src.models.evaluation import generate_evaluation_report

FEATURE_COLS_EXPORT = FEATURE_COLS
NUMERIC_COLS_EXPORT = NUMERIC_COLS
CATEGORICAL_COLS_EXPORT = CATEGORICAL_COLS


def prepare_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    """Extract features X and encoded target y."""
    return XGBoostModel().prepare_xy(df)


def train_and_evaluate(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    model_path: Path | None = None,
    model_type: str = "xgboost",
) -> dict[str, Any]:
    """Train model and return metrics."""
    settings = get_settings()
    model_impl = get_model(model_type)
    x_train, y_train = model_impl.prepare_xy(train_df)
    x_test, y_test = model_impl.prepare_xy(test_df)

    pipeline = model_impl.build_pipeline(list(x_train.columns))
    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_test)
    y_proba = pipeline.predict_proba(x_test)

    report = generate_evaluation_report(y_test, y_pred, y_proba, pipeline, x_test)
    out_path = model_path or settings.model_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, out_path)

    metrics: dict[str, Any] = {
        **report.metrics,
        "accuracy": report.metrics.get("accuracy", 0.0),
        "macro_f1": report.metrics.get("f1_macro", 0.0),
        "confusion_matrix": report.confusion_matrix,
        "classification_report": report.classification_report,
        "train_size": len(y_train),
        "test_size": len(y_test),
        "model_path": str(out_path),
    }

    report_path = settings.reports_dir / "baseline_metrics.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(metrics, indent=2, default=str), encoding="utf-8")

    html_path = settings.reports_dir / "evaluation_report.html"
    report.save_html(html_path)

    return metrics


def print_metrics(metrics: dict[str, Any]) -> None:
    print(f"\nTrain size: {metrics['train_size']}")
    print(f"Test size:  {metrics['test_size']}")
    print(f"Accuracy:   {metrics.get('accuracy', 0):.4f}")
    print(f"Macro F1:   {metrics.get('macro_f1', metrics.get('f1_macro', 0)):.4f}")
    print(f"\nModel saved to {metrics['model_path']}")
