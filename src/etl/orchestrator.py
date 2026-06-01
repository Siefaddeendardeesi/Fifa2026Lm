"""ETL orchestration layer with retry, caching, and validation."""

from __future__ import annotations

import time
from typing import Any

from src.config.settings import get_settings
from src.etl.build_dataset import build_feature_matrix, save_splits
from src.etl.download import download_all
from src.etl.loaders import load_matches
from src.etl.metadata import MetadataStore
from src.etl.validation import save_validation_report, validate_features, validate_matches
from src.utils.exceptions import ETLProcessingError
from src.utils.logging import configure_logging, get_logger

logger = get_logger(__name__)


class ETLOrchestrator:
    """Production ETL pipeline orchestrator."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.metadata = MetadataStore()

    def run_download(
        self,
        *,
        include_optional_kaggle: bool = False,
        skip_kaggle: bool = False,
        force: bool = False,
    ) -> dict[str, Any]:
        """Download all raw data sources."""
        configure_logging()
        start = time.perf_counter()
        status = "success"
        details: dict[str, Any] = {}

        try:
            logger.info("etl_download_start", skip_kaggle=skip_kaggle)
            download_all(
                include_optional_kaggle=include_optional_kaggle,
                skip_kaggle=skip_kaggle,
            )
            for name, path in [
                ("results", self.settings.results_csv),
                ("elo", self.settings.elo_csv),
            ]:
                if path.exists():
                    self.metadata.record_source(name, path)
            details["sources"] = list(self.metadata._data.get("sources", {}).keys())
        except Exception as exc:
            status = "failed"
            details["error"] = str(exc)
            raise
        finally:
            duration = time.perf_counter() - start
            self.metadata.record_run(
                "download", status=status, duration_seconds=duration, details=details
            )

        return {"status": status, "duration_seconds": duration, "details": details}

    def run_build_features(
        self,
        *,
        min_date: str | None = None,
        split: str = "default",
        include_managers: bool = False,
        validate: bool = True,
    ) -> dict[str, Any]:
        """Build and validate feature matrix."""
        configure_logging()
        start = time.perf_counter()
        status = "success"
        details: dict[str, Any] = {}

        try:
            min_date = min_date or self.settings.min_match_date
            logger.info("etl_build_features_start", min_date=min_date)

            matches = load_matches()
            if validate:
                matches = validate_matches(matches)
                save_validation_report("matches", True, {"rows": len(matches)})

            df = build_feature_matrix(min_date=min_date, include_managers=include_managers)
            if validate:
                df = validate_features(df)
                save_validation_report(
                    "features", True, {"rows": len(df), "columns": list(df.columns)}
                )

            train, test = save_splits(df, split=split)
            self.metadata.record_source("features", self.settings.features_parquet)
            details.update(
                {
                    "total_rows": len(df),
                    "train_rows": len(train),
                    "test_rows": len(test),
                }
            )
        except Exception as exc:
            status = "failed"
            details["error"] = str(exc)
            if validate:
                save_validation_report("features", False, {"error": str(exc)})
            raise ETLProcessingError(str(exc)) from exc
        finally:
            duration = time.perf_counter() - start
            self.metadata.record_run(
                "build_features", status=status, duration_seconds=duration, details=details
            )

        return {"status": status, "duration_seconds": duration, "details": details}

    def run_full_pipeline(
        self,
        *,
        skip_download: bool = False,
        skip_kaggle: bool = False,
        split: str = "default",
    ) -> dict[str, Any]:
        """Run complete ETL pipeline."""
        results: dict[str, Any] = {}
        if not skip_download:
            results["download"] = self.run_download(skip_kaggle=skip_kaggle)
        results["features"] = self.run_build_features(split=split)
        return results
