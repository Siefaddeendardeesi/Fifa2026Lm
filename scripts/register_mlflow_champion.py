#!/usr/bin/env python3
"""Register the champion model in MLflow Model Registry."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.mlflow_registry import (
    ensure_champion_registered,
    register_champion_model,
    registry_summary,
)
from src.utils.logging import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Register champion model in MLflow Model Registry")
    parser.add_argument("--run-id", help="MLflow run ID containing model artifact")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Register even if a Production model already exists",
    )
    args = parser.parse_args()
    configure_logging()

    if args.force:
        version = register_champion_model(run_id=args.run_id)
        print(f"Registered {version.name} v{version.version} -> Production")
    else:
        version = ensure_champion_registered(run_id=args.run_id)
        print(f"Production model: {version.name} v{version.version}")

    summary = registry_summary()
    print(f"Registry models: {summary['registered_model_count']}")


if __name__ == "__main__":
    main()
