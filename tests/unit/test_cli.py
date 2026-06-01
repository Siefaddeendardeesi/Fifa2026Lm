"""Tests for scripts CLI entry points."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pandas as pd


def test_cli_train_main(mocker) -> None:
    mocker.patch.object(sys, "argv", ["cli", "--model-type", "logistic_regression"])
    mocker.patch("scripts.cli.configure_logging")
    settings = mocker.Mock()
    settings.train_parquet.exists.return_value = True
    settings.features_parquet = MagicMock()
    mocker.patch("scripts.cli.get_settings", return_value=settings)

    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2023-01-01"]),
            "result": ["Win", "Loss"],
        }
    )
    mocker.patch("scripts.cli.pd.read_parquet", return_value=df)
    mocker.patch(
        "scripts.cli.get_split_dates",
        return_value=(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-01-01")),
    )
    mock_trainer = mocker.patch("scripts.cli.ModelTrainer")
    mock_trainer.return_value.train.return_value = {"metrics": {"accuracy": 0.5}}

    from scripts.cli import train_main

    train_main()
    mock_trainer.return_value.train.assert_called_once()


def test_cli_etl_main(mocker) -> None:
    mocker.patch.object(sys, "argv", ["cli", "--skip-download"])
    mocker.patch("scripts.cli.configure_logging")
    mock_orch = mocker.patch("scripts.cli.ETLOrchestrator")
    mock_orch.return_value.run_full_pipeline.return_value = {"features": {}}

    from scripts.cli import etl_main

    etl_main()
    mock_orch.return_value.run_full_pipeline.assert_called_once()
