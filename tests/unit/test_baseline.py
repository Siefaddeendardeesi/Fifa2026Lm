"""Tests for src.models.baseline."""

from __future__ import annotations

import joblib

from src.models.baseline import prepare_xy, print_metrics, train_and_evaluate


def test_prepare_xy(features_df) -> None:
    x, y = prepare_xy(features_df.head(80))
    assert len(x) == len(y)


def test_train_and_evaluate_random_forest(train_test_frames, test_settings, tmp_path) -> None:
    train, test = train_test_frames
    model_path = tmp_path / "test_model.joblib"
    metrics = train_and_evaluate(
        train,
        test,
        model_path=model_path,
        model_type="random_forest",
    )
    assert model_path.exists()
    assert "accuracy" in metrics
    assert metrics["train_size"] > 0
    assert joblib.load(model_path) is not None


def test_print_metrics(capsys) -> None:
    print_metrics({"train_size": 10, "test_size": 5, "accuracy": 0.5, "model_path": "/tmp/m"})
    captured = capsys.readouterr()
    assert "Train size" in captured.out
