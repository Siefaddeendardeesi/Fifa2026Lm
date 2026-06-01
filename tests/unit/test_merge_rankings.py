"""Tests for src.etl.merge_rankings."""

from __future__ import annotations

import pandas as pd

from src.etl.merge_rankings import load_confederation_fallback, merge_rankings


def test_merge_rankings_adds_columns(sample_matches_df: pd.DataFrame) -> None:
    rankings = pd.DataFrame(
        {
            "rank_date": pd.to_datetime(["2023-01-01", "2024-06-01"] * 2),
            "team": ["Brazil", "Brazil", "Argentina", "Argentina"],
            "rank": [1.0, 2.0, 3.0, 4.0],
            "total_points": [1800, 1750, 1700, 1680],
            "confederation": ["CONMEBOL", "CONMEBOL", "CONMEBOL", "CONMEBOL"],
        }
    )
    out = merge_rankings(sample_matches_df, rankings)
    assert "home_fifa_rank" in out.columns
    assert "fifa_rank_diff" in out.columns


def test_load_confederation_fallback(project_root) -> None:
    df = load_confederation_fallback()
    assert "team" in df.columns
