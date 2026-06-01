"""Tests for src.etl.merge_elo."""

from __future__ import annotations

import pandas as pd

from src.etl.merge_elo import compute_elo_from_matches, merge_elo


def test_compute_elo_from_matches(sample_matches_df: pd.DataFrame) -> None:
    out = compute_elo_from_matches(sample_matches_df)
    assert "home_elo" in out.columns
    assert "away_elo" in out.columns
    assert "elo_diff" in out.columns
    assert out["home_elo"].notna().all()


def test_merge_elo_default_computes(sample_matches_df: pd.DataFrame) -> None:
    out = merge_elo(sample_matches_df)
    assert out["elo_diff"].equals(out["home_elo"] - out["away_elo"])


def test_merge_elo_with_multi_date_snapshot(sample_matches_df: pd.DataFrame) -> None:
    """merge_elo uses computed ELO when snapshot has insufficient date history."""
    matches = sample_matches_df.sort_values("date").reset_index(drop=True)
    elo = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-06-01", "2024-06-01"]),
            "team": ["Brazil", "Argentina"],
            "elo": [1600.0, 1580.0],
        }
    )
    out = merge_elo(matches, elo=elo)
    assert "home_elo" in out.columns
    assert out["home_elo"].notna().all()
