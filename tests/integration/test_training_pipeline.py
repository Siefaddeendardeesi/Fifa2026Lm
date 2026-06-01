"""Integration tests for model training pipeline."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from src.models.baseline import train_and_evaluate
from src.models.registry import ModelRegistry
from src.models.trainer import ModelTrainer


def test_end_to_end_training_random_forest(features_df, test_settings, tmp_path) -> None:
    cutoff = pd.Timestamp("2022-01-01")
    train = features_df[features_df["date"] < cutoff].tail(1500)
    test = features_df[features_df["date"] >= cutoff].head(400)

    model_path = tmp_path / "integration_model.joblib"
    metrics = train_and_evaluate(train, test, model_path=model_path, model_type="random_forest")
    assert model_path.exists()
    pipe = joblib.load(model_path)
    x, _ = (
        __import__("src.models.base", fromlist=["RandomForestModel"])
        .RandomForestModel()
        .prepare_xy(test.head(10))
    )
    preds = pipe.predict(x)
    assert len(preds) == len(x)
    assert metrics["accuracy"] >= 0


def test_trainer_mlflow_integration(features_df, test_settings) -> None:
    train = features_df[features_df["date"] < "2022-01-01"].tail(800)
    test = features_df[features_df["date"] >= "2022-01-01"].head(200)
    trainer = ModelTrainer(model_type="random_forest")
    result = trainer.train(train, test, run_name="integration_test")
    assert Path(result["model_path"]).exists()


def test_registry_after_training(features_df, test_settings, tmp_path) -> None:
    train = features_df.head(200)
    model_path = tmp_path / "m.joblib"
    train_and_evaluate(train, train, model_path=model_path, model_type="random_forest")
    reg = ModelRegistry(registry_path=tmp_path / "reg")
    meta = reg.register(model_path, model_type="random_forest", metrics={"accuracy": 0.3})
    reg.promote_to_champion(meta.version)
    assert reg.get_champion() is not None
