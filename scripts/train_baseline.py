#!/usr/bin/env python3
"""CLI: train baseline Win/Draw/Loss classifier."""

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import TRAIN_PARQUET  # noqa: E402
from src.etl.build_dataset import (  # noqa: E402
    build_feature_matrix,
    get_split_dates,
    save_splits,
)
from src.models.baseline import print_metrics, train_and_evaluate  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline match outcome model")
    parser.add_argument(
        "--split",
        choices=["default", "wc2022"],
        default="default",
        help="Train/test split strategy",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild features before training",
    )
    args = parser.parse_args()

    if args.rebuild or not TRAIN_PARQUET.exists():
        df = build_feature_matrix()
        save_splits(df, split=args.split)
    else:
        df = pd.read_parquet(TRAIN_PARQUET.parent / "features.parquet")

    train_cutoff, test_start = get_split_dates(args.split)
    train_df = df[df["date"] < train_cutoff]
    test_df = df[df["date"] >= test_start]

    metrics = train_and_evaluate(train_df, test_df)
    print_metrics(metrics)


if __name__ == "__main__":
    main()
