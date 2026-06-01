"""Tests for src.etl.form_features."""

from __future__ import annotations

import pandas as pd

from src.etl.form_features import add_form_features


def test_add_form_features_columns(sample_matches_df: pd.DataFrame) -> None:
    out = add_form_features(sample_matches_df, window=10)
    assert "home_form_wins_10" in out.columns
    assert "away_form_wins_10" in out.columns
    assert len(out) == len(sample_matches_df)


def test_form_features_first_match_has_nan_or_zero(sample_matches_df: pd.DataFrame) -> None:
    out = add_form_features(sample_matches_df.sort_values("date"), window=10)
    first = out.iloc[0]
    assert pd.isna(first["home_form_wins_10"]) or first["home_form_wins_10"] == 0
