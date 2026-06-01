#!/usr/bin/env python3
"""Unified CLI for FIFA2026LM pipelines."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from src.config.settings import get_settings
from src.etl.build_dataset import build_feature_matrix, get_split_dates, save_splits
from src.etl.orchestrator import ETLOrchestrator
from src.models.baseline import print_metrics, train_and_evaluate
from src.models.registry import ModelRegistry
from src.models.trainer import ModelTrainer
from src.models.tuning import HyperparameterTuner
from src.utils.logging import configure_logging


def etl_main() -> None:
    parser = argparse.ArgumentParser(description="ETL pipeline")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-kaggle", action="store_true")
    parser.add_argument("--split", default="default")
    args = parser.parse_args()
    configure_logging()
    ETLOrchestrator().run_full_pipeline(
        skip_download=args.skip_download, skip_kaggle=args.skip_kaggle, split=args.split
    )


def train_main() -> None:
    parser = argparse.ArgumentParser(description="Train match outcome model")
    parser.add_argument("--split", choices=["default", "wc2022"], default="default")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--model-type", default="xgboost")
    parser.add_argument("--tune", action="store_true")
    parser.add_argument("--register", action="store_true")
    parser.add_argument(
        "--register-mlflow",
        action="store_true",
        help="Register model in MLflow Model Registry",
    )
    args = parser.parse_args()
    configure_logging()
    settings = get_settings()

    if args.rebuild or not settings.train_parquet.exists():
        df = build_feature_matrix()
        save_splits(df, split=args.split)
    else:
        df = pd.read_parquet(settings.features_parquet)

    train_cutoff, test_start = get_split_dates(args.split)
    train_df = df[df["date"] < train_cutoff]
    test_df = df[df["date"] >= test_start]

    params = None
    if args.tune:
        tuner = HyperparameterTuner(args.model_type, n_trials=10)
        tune_result = tuner.tune(train_df, n_folds=3)
        params = tune_result["best_params"]

    if args.model_type == "xgboost" and not args.tune:
        metrics = train_and_evaluate(train_df, test_df)
        print_metrics(metrics)
    else:
        trainer = ModelTrainer(args.model_type)
        result = trainer.train(train_df, test_df, params=params)
        print(f"Trained {args.model_type}: {result['metrics']}")

    if args.register:
        registry = ModelRegistry()
        metrics_path = settings.reports_dir / "baseline_metrics.json"
        if metrics_path.exists():
            import json

            metrics = json.loads(metrics_path.read_text())
            registry.register(
                settings.model_path,
                model_type=args.model_type,
                metrics={k: v for k, v in metrics.items() if isinstance(v, (int, float))},
            )
            models = registry.list_models()
            if models:
                registry.promote_to_champion(models[-1].version)

    if args.register_mlflow:
        from src.models.mlflow_registry import ensure_champion_registered

        version = ensure_champion_registered()
        print(f"MLflow Production model: {version.name} v{version.version}")


if __name__ == "__main__":
    train_main()
