#!/usr/bin/env python3
"""CLI: build feature matrix from raw data."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.etl.build_dataset import build_feature_matrix, save_splits  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Build FIFA match feature matrix")
    parser.add_argument(
        "--split",
        choices=["default", "wc2022"],
        default="default",
        help="Train/test split strategy (default: 2022-01-01 cutoff)",
    )
    parser.add_argument(
        "--min-date",
        default="1992-01-01",
        help="Minimum match date (FIFA rankings start 1992)",
    )
    parser.add_argument(
        "--include-managers",
        action="store_true",
        help="Scrape Wikipedia manager history (slow)",
    )
    args = parser.parse_args()

    df = build_feature_matrix(
        min_date=args.min_date,
        include_managers=args.include_managers,
    )
    save_splits(df, split=args.split)


if __name__ == "__main__":
    main()
