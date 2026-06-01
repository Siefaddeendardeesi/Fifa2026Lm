#!/usr/bin/env python3
"""CLI: download all raw data sources."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.etl.download import download_all  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Download FIFA pipeline raw data")
    parser.add_argument(
        "--optional-kaggle",
        action="store_true",
        help="Also download optional Kaggle datasets (evangower WC, alt rankings)",
    )
    parser.add_argument(
        "--skip-kaggle",
        action="store_true",
        help="Skip Kaggle downloads (use existing files in data/raw/)",
    )
    args = parser.parse_args()
    download_all(
        include_optional_kaggle=args.optional_kaggle,
        skip_kaggle=args.skip_kaggle,
    )


if __name__ == "__main__":
    main()
