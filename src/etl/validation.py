"""Pandera schemas for data validation."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pandera as pa
from pandera import Check, Column, DataFrameSchema

from src.config.constants import VALID_CONFEDERATIONS
from src.config.settings import get_settings
from src.utils.exceptions import DataValidationError
from src.utils.logging import get_logger

logger = get_logger(__name__)

MatchesSchema = DataFrameSchema(  # type: ignore[no-untyped-call]
    {
        "date": Column("datetime64[ns]", nullable=False),
        "home_team": Column(str, Check.str_length(min_value=1), nullable=False),
        "away_team": Column(str, Check.str_length(min_value=1), nullable=False),
        "home_score": Column(int, Check.ge(0), nullable=False),
        "away_score": Column(int, Check.ge(0), nullable=False),
        "neutral": Column(bool, nullable=True),
        "result": Column(str, Check.isin(["Win", "Draw", "Loss"]), nullable=False),
    },
    strict=False,
    coerce=True,
)

FeaturesSchema = DataFrameSchema(  # type: ignore[no-untyped-call]
    {
        "date": Column("datetime64[ns]", nullable=False),
        "home_team": Column(str, nullable=False),
        "away_team": Column(str, nullable=False),
        "home_elo": Column(float, Check.in_range(800, 2500), nullable=True),
        "away_elo": Column(float, Check.in_range(800, 2500), nullable=True),
        "home_fifa_rank": Column(float, Check.ge(1), nullable=True),
        "away_fifa_rank": Column(float, Check.ge(1), nullable=True),
        "result": Column(str, Check.isin(["Win", "Draw", "Loss"]), nullable=False),
    },
    strict=False,
    coerce=True,
)

RankingsSchema = DataFrameSchema(  # type: ignore[no-untyped-call]
    {
        "rank_date": Column("datetime64[ns]", nullable=False),
        "team": Column(str, Check.str_length(min_value=1), nullable=False),
        "rank": Column(float, Check.ge(1), nullable=True),
    },
    strict=False,
    coerce=True,
)


def validate_matches(df: pd.DataFrame) -> pd.DataFrame:
    """Validate raw match data; raise on failure."""
    try:
        validated = MatchesSchema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as exc:
        raise DataValidationError(
            "Match data validation failed",
            details={"errors": exc.failure_cases.to_dict(orient="records")},
        ) from exc
    _check_duplicate_matches(validated)
    _check_same_team_matches(validated)
    return validated


def validate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Validate feature matrix; raise on failure."""
    try:
        validated = FeaturesSchema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as exc:
        raise DataValidationError(
            "Feature validation failed",
            details={"errors": exc.failure_cases.to_dict(orient="records")},
        ) from exc
    _check_confederations(df)
    return validated


def validate_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Validate FIFA ranking data."""
    try:
        return RankingsSchema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as exc:
        raise DataValidationError(
            "Ranking validation failed",
            details={"errors": exc.failure_cases.to_dict(orient="records")},
        ) from exc


def _check_duplicate_matches(df: pd.DataFrame) -> None:
    dupes = df.duplicated(subset=["date", "home_team", "away_team"], keep=False)
    if dupes.any():
        count = int(dupes.sum())
        raise DataValidationError(
            f"Found {count} duplicate match rows",
            details={"duplicate_count": count},
        )


def _check_same_team_matches(df: pd.DataFrame) -> None:
    same = df["home_team"] == df["away_team"]
    if same.any():
        raise DataValidationError(
            "Matches where home_team equals away_team are invalid",
            details={"count": int(same.sum())},
        )


def _check_confederations(df: pd.DataFrame) -> None:
    for col in ("home_confederation", "away_confederation"):
        if col not in df.columns:
            continue
        values = df[col].dropna().astype(str).unique()
        invalid = [v for v in values if v not in VALID_CONFEDERATIONS and v != "nan"]
        if invalid:
            logger.warning("unknown_confederations", column=col, values=invalid[:10])


def validate_wc2026_teams(teams: list[str], expected: int = 48) -> None:
    """Ensure World Cup team list is complete."""
    if len(teams) != expected:
        raise DataValidationError(
            f"Expected {expected} teams, got {len(teams)}",
            details={"teams": teams},
        )
    if len(set(teams)) != len(teams):
        raise DataValidationError("Duplicate teams in World Cup roster")


def save_validation_report(
    name: str,
    passed: bool,
    details: dict[str, object],
    path: Path | None = None,
) -> Path:
    """Persist validation report JSON."""
    settings = get_settings()
    report_dir = settings.reports_dir / "validation"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = path or report_dir / f"{name}_{datetime.utcnow():%Y%m%d_%H%M%S}.json"
    payload = {
        "name": name,
        "passed": passed,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details,
    }
    report_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    logger.info("validation_report_saved", path=str(report_path), passed=passed)
    return report_path
