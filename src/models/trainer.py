"""Model training with MLflow tracking."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

from src.config.settings import get_settings
from src.models.base import BaseModel, get_model
from src.models.evaluation import generate_evaluation_report
from src.utils.exceptions import ModelTrainingError
from src.utils.logging import get_logger
from src.utils.seeds import set_global_seed

logger = get_logger(__name__)


class ModelTrainer:
    """Train models with MLflow experiment tracking."""

    def __init__(self, model_type: str = "xgboost") -> None:
        self.settings = get_settings()
        self.model_type = model_type
        self.model_impl: BaseModel = get_model(model_type)
        mlflow.set_tracking_uri(self.settings.mlflow_tracking_uri)
        mlflow.set_experiment(self.settings.mlflow_experiment_name)

    def train(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        *,
        params: dict[str, Any] | None = None,
        run_name: str | None = None,
        save_path: Path | None = None,
    ) -> dict[str, Any]:
        """Train model and log to MLflow."""
        set_global_seed()
        start = time.perf_counter()

        x_train, y_train = self.model_impl.prepare_xy(train_df)
        x_test, y_test = self.model_impl.prepare_xy(test_df)

        if len(y_train) == 0 or len(y_test) == 0:
            raise ModelTrainingError("Empty train or test set")

        pipeline = self.model_impl.build_pipeline(list(x_train.columns))
        if params:
            pipeline.set_params(**{f"classifier__{k}": v for k, v in params.items()})

        run_name = run_name or f"{self.model_type}_{int(time.time())}"

        with mlflow.start_run(run_name=run_name):
            mlflow.log_param("model_type", self.model_type)
            mlflow.log_param("train_size", len(y_train))
            mlflow.log_param("test_size", len(y_test))
            for k, v in (params or self.model_impl.get_default_params()).items():
                mlflow.log_param(k, v)

            pipeline.fit(x_train, y_train)
            y_pred = pipeline.predict(x_test)
            y_proba = pipeline.predict_proba(x_test)

            report = generate_evaluation_report(y_test, y_pred, y_proba, pipeline, x_test)
            for metric, value in report.metrics.items():
                mlflow.log_metric(metric, value)

            out_path = save_path or self.settings.models_dir / f"{self.model_type}_model.joblib"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(pipeline, out_path)
            mlflow.log_artifact(str(out_path))

            report_path = self.settings.reports_dir / f"{self.model_type}_evaluation.html"
            report.save_html(report_path)
            mlflow.log_artifact(str(report_path))

            metrics_path = self.settings.reports_dir / f"{self.model_type}_metrics.json"
            metrics_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
            mlflow.log_artifact(str(metrics_path))

            mlflow.sklearn.log_model(pipeline, artifact_path="model")

            duration = time.perf_counter() - start
            mlflow.log_metric("training_duration_seconds", duration)

            active_run = mlflow.active_run()
            result = {
                "model_type": self.model_type,
                "model_path": str(out_path),
                "metrics": report.metrics,
                "duration_seconds": duration,
                "run_id": active_run.info.run_id if active_run is not None else None,
            }
            logger.info("model_trained", **{k: v for k, v in result.items() if k != "metrics"})
            return result
