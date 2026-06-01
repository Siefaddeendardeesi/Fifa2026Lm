"""Tests for src.models.trainer."""

from __future__ import annotations

import pytest

from src.models.trainer import ModelTrainer
from src.utils.exceptions import ModelTrainingError


def test_trainer_random_forest(train_test_frames, test_settings) -> None:
    train, test = train_test_frames
    trainer = ModelTrainer(model_type="random_forest")
    result = trainer.train(train, test, run_name="pytest_run")
    assert result["model_type"] == "random_forest"
    assert "accuracy" in result["metrics"]
    assert result["run_id"] is not None


def test_trainer_empty_data_raises(test_settings) -> None:
    import pandas as pd

    trainer = ModelTrainer(model_type="random_forest")
    empty = pd.DataFrame(columns=["date", "home_team", "away_team", "result"])
    with pytest.raises(ModelTrainingError):
        trainer.train(empty, empty)
