"""Tests for src.etl.normalize."""

from __future__ import annotations

import pandas as pd

from src.etl.normalize import load_mapping, normalize_team_name, normalize_teams


def test_normalize_team_name_with_mapping() -> None:
    mapping = {"USA": "United States"}
    assert normalize_team_name("USA", mapping) == "United States"
    assert normalize_team_name("Brazil", mapping) == "Brazil"


def test_normalize_teams_applies_both_columns(sample_matches_df: pd.DataFrame) -> None:
    mapping = {"Brazil": "Brazil FC"}
    out = normalize_teams(sample_matches_df, mapping=mapping, log_unmapped=False)
    assert (out["home_team"] == "Brazil FC").any() or (out["away_team"] == "Brazil FC").any()


def test_load_mapping_empty_when_missing(tmp_path) -> None:
    assert load_mapping(tmp_path / "no_mapping.csv") == {}
