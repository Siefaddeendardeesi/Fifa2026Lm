"""Feature store with registry, versioning, and reusable transformers."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.config.constants import FINAL_COLUMNS
from src.config.settings import get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class FeatureTransformer(ABC):
    """Base class for feature transformers."""

    name: str = "base"
    version: str = "1.0.0"

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply transformation to match DataFrame."""

    @abstractmethod
    def get_output_columns(self) -> list[str]:
        """Return columns produced by this transformer."""

    def get_lineage(self) -> dict[str, str]:
        return {"name": self.name, "version": self.version}


class FormFeatureTransformer(FeatureTransformer):
    """Rolling form features."""

    name = "form_features"
    version = "1.0.0"

    def __init__(self, window: int = 10) -> None:
        self.window = window

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        from src.etl.form_features import add_form_features

        return add_form_features(df, window=self.window)

    def get_output_columns(self) -> list[str]:
        cols = []
        for prefix in ("home", "away"):
            for stat in (
                "wins",
                "draws",
                "losses",
                "goals_for",
                "goals_against",
                "clean_sheets",
                "points",
                "goal_diff",
                "win_rate",
            ):
                cols.append(f"{prefix}_form_{stat}_{self.window}")
        return cols


class WCFeatureTransformer(FeatureTransformer):
    """World Cup title features."""

    name = "wc_features"
    version = "1.0.0"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        from src.etl.wc_features import add_wc_features

        return add_wc_features(df)

    def get_output_columns(self) -> list[str]:
        return ["home_wc_titles", "away_wc_titles"]


class EloFeatureTransformer(FeatureTransformer):
    """ELO rating features."""

    name = "elo_features"
    version = "1.0.0"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        from src.etl.merge_elo import merge_elo

        return merge_elo(df)

    def get_output_columns(self) -> list[str]:
        return ["home_elo", "away_elo", "elo_diff"]


class RankingFeatureTransformer(FeatureTransformer):
    """FIFA ranking features."""

    name = "ranking_features"
    version = "1.0.0"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        from src.etl.loaders import load_fifa_rankings
        from src.etl.merge_rankings import merge_rankings

        rankings = load_fifa_rankings()
        return merge_rankings(df, rankings)

    def get_output_columns(self) -> list[str]:
        return [
            "home_fifa_rank",
            "away_fifa_rank",
            "fifa_rank_diff",
            "home_confederation",
            "away_confederation",
        ]


class FeatureRegistry:
    """Registry of available feature transformers."""

    def __init__(self) -> None:
        self._transformers: dict[str, FeatureTransformer] = {}

    def register(self, transformer: FeatureTransformer) -> None:
        self._transformers[transformer.name] = transformer
        logger.info("feature_registered", name=transformer.name, version=transformer.version)

    def get(self, name: str) -> FeatureTransformer:
        if name not in self._transformers:
            raise KeyError(f"Unknown feature transformer: {name}")
        return self._transformers[name]

    def list_features(self) -> list[dict[str, str]]:
        return [t.get_lineage() for t in self._transformers.values()]


def get_default_registry() -> FeatureRegistry:
    """Create registry with standard transformers."""
    registry = FeatureRegistry()
    settings = get_settings()
    registry.register(FormFeatureTransformer(window=settings.form_window))
    registry.register(WCFeatureTransformer())
    registry.register(EloFeatureTransformer())
    registry.register(RankingFeatureTransformer())
    return registry


class FeatureStore:
    """Feature generation with versioning and lineage tracking."""

    FEATURE_VERSION = "1.0.0"

    def __init__(self, registry: FeatureRegistry | None = None) -> None:
        self.settings = get_settings()
        self.registry = registry or get_default_registry()
        self.lineage_path = self.settings.metadata_dir / "feature_lineage.json"

    def build_features(
        self,
        matches: pd.DataFrame,
        *,
        transformer_names: list[str] | None = None,
    ) -> pd.DataFrame:
        """Apply registered transformers in sequence."""
        df = matches.copy()
        names = transformer_names or list(self.registry._transformers.keys())
        lineage: list[dict[str, str]] = []

        for name in names:
            transformer = self.registry.get(name)
            df = transformer.transform(df)
            lineage.append(transformer.get_lineage())

        for col in FINAL_COLUMNS:
            if col not in df.columns:
                df[col] = pd.NA

        self._save_lineage(lineage, len(df))
        return df[FINAL_COLUMNS].copy()

    def _save_lineage(self, lineage: list[dict[str, str]], row_count: int) -> None:
        self.lineage_path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "feature_version": self.FEATURE_VERSION,
            "timestamp": datetime.now(UTC).isoformat(),
            "row_count": row_count,
            "transformers": lineage,
            "output_columns": FINAL_COLUMNS,
        }
        self.lineage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def save(self, df: pd.DataFrame, path: Path | None = None) -> Path:
        """Persist feature matrix."""
        out = path or self.settings.features_parquet
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out, index=False)
        logger.info("features_saved", path=str(out), rows=len(df))
        return out

    def load(self, path: Path | None = None) -> pd.DataFrame:
        """Load feature matrix."""
        p = path or self.settings.features_parquet
        df = pd.read_parquet(p)
        df["date"] = pd.to_datetime(df["date"])
        return df
