"""Tests for src.rankings.predictor."""

from __future__ import annotations

import pandas as pd
import pytest

from src.rankings.predictor import (
    build_match_probability_cache,
    build_match_row,
    extract_team_snapshot,
    predict_match_proba,
)


def test_extract_team_snapshot(features_df) -> None:
    team = features_df["home_team"].iloc[-1]
    snap = extract_team_snapshot(features_df, team)
    assert snap is not None
    assert "elo" in snap
    assert snap["last_match_date"] is not None


def test_extract_team_snapshot_missing() -> None:
    df = pd.DataFrame(
        {"date": [pd.Timestamp("2024-01-01")], "home_team": ["X"], "away_team": ["Y"]}
    )
    assert extract_team_snapshot(df, "Z") is None


def test_build_match_row() -> None:
    home = {"elo": 1600.0, "fifa_rank": 1.0, "confederation": "UEFA"}
    away = {"elo": 1500.0, "fifa_rank": 5.0, "confederation": "UEFA"}
    for stat in (
        "form_wins_10",
        "form_draws_10",
        "form_losses_10",
        "form_goals_for_10",
        "form_goals_against_10",
        "form_clean_sheets_10",
        "form_points_10",
        "form_goal_diff_10",
        "form_win_rate_10",
        "wc_titles",
        "squad_value",
    ):
        home.setdefault(stat, 0)
        away.setdefault(stat, 0)
    row = build_match_row(home, away, neutral=True)
    assert "elo_diff" in row.columns
    assert float(row["elo_diff"].iloc[0]) == 100.0


def test_predict_match_proba(trained_pipeline, features_df) -> None:
    brazil = extract_team_snapshot(features_df, "Brazil")
    argentina = extract_team_snapshot(features_df, "Argentina")
    if brazil is None or argentina is None:
        pytest.skip("teams not in features")
    w, d, l = predict_match_proba(trained_pipeline, brazil, argentina)
    assert abs(w + d + l - 1.0) < 0.01


def test_build_match_probability_cache(trained_pipeline, features_df) -> None:
    teams = ["Brazil", "Argentina", "France"]
    snaps = {t: extract_team_snapshot(features_df, t) for t in teams}
    snaps = {k: v for k, v in snaps.items() if v}
    if len(snaps) < 3:
        pytest.skip("snapshots missing")
    cache = build_match_probability_cache(trained_pipeline, snaps, teams)
    assert ("Brazil", "Argentina") in cache
    assert abs(sum(cache[("Brazil", "Argentina")]) - 1.0) < 0.01
