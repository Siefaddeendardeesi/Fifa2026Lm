"""Tests for src.etl.validation."""

from __future__ import annotations

import pandas as pd
import pytest

from src.etl.validation import (
    save_validation_report,
    validate_features,
    validate_matches,
    validate_rankings,
    validate_wc2026_teams,
)
from src.utils.exceptions import DataValidationError


def _valid_match_row() -> dict:
    return {
        "date": pd.Timestamp("2024-01-01"),
        "home_team": "Brazil",
        "away_team": "Argentina",
        "home_score": 2,
        "away_score": 1,
        "neutral": False,
        "result": "Win",
    }


def test_validate_matches_success(sample_matches_df: pd.DataFrame) -> None:
    df = validate_matches(sample_matches_df)
    assert len(df) == len(sample_matches_df)


def test_validate_matches_duplicate_raises() -> None:
    row = _valid_match_row()
    df = pd.DataFrame([row, row])
    with pytest.raises(DataValidationError, match="duplicate"):
        validate_matches(df)


def test_validate_matches_same_team_raises() -> None:
    df = pd.DataFrame([{**_valid_match_row(), "away_team": "Brazil", "result": "Draw"}])
    with pytest.raises(DataValidationError, match="home_team equals away_team"):
        validate_matches(df)


def test_validate_features_success(features_df: pd.DataFrame) -> None:
    subset = features_df.dropna(subset=["home_elo", "away_elo", "home_fifa_rank", "away_fifa_rank"])
    subset = subset[
        (subset["home_elo"].between(800, 2500)) & (subset["away_elo"].between(800, 2500))
    ].head(100)
    validated = validate_features(subset)
    assert len(validated) == len(subset)


def test_validate_rankings() -> None:
    df = pd.DataFrame(
        {
            "rank_date": pd.to_datetime(["2024-01-01", "2024-02-01"]),
            "team": ["Brazil", "France"],
            "rank": [1, 2],
        }
    )
    out = validate_rankings(df)
    assert len(out) == 2


def test_validate_wc2026_teams() -> None:
    teams = [f"Team{i}" for i in range(48)]
    validate_wc2026_teams(teams, expected=48)


def test_validate_wc2026_teams_wrong_count() -> None:
    with pytest.raises(DataValidationError):
        validate_wc2026_teams(["A", "B"], expected=48)


def test_save_validation_report(test_settings, tmp_path) -> None:
    path = save_validation_report("unit_test", True, {"rows": 10}, path=tmp_path / "r.json")
    assert path.exists()
    assert "passed" in path.read_text(encoding="utf-8")
