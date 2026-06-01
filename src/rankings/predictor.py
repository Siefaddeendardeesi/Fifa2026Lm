"""Match prediction utilities."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.models.baseline import prepare_xy

_SNAPSHOT_STATS = (
    "elo",
    "fifa_rank",
    "confederation",
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
)

_HOME_COL_MAP = {
    "elo": "home_elo",
    "fifa_rank": "home_fifa_rank",
    "confederation": "home_confederation",
    "form_wins_10": "home_form_wins_10",
    "form_draws_10": "home_form_draws_10",
    "form_losses_10": "home_form_losses_10",
    "form_goals_for_10": "home_form_goals_for_10",
    "form_goals_against_10": "home_form_goals_against_10",
    "form_clean_sheets_10": "home_form_clean_sheets_10",
    "form_points_10": "home_form_points_10",
    "form_goal_diff_10": "home_form_goal_diff_10",
    "form_win_rate_10": "home_form_win_rate_10",
    "wc_titles": "home_wc_titles",
    "squad_value": "home_squad_value",
}

_AWAY_COL_MAP = {k: v.replace("home_", "away_") for k, v in _HOME_COL_MAP.items()}


def extract_team_snapshot(df: pd.DataFrame, team: str) -> dict[str, Any] | None:
    mask = (df["home_team"] == team) | (df["away_team"] == team)
    sub = df.loc[mask].sort_values("date")
    if sub.empty:
        return None
    row = sub.iloc[-1]
    col_map = _HOME_COL_MAP if row["home_team"] == team else _AWAY_COL_MAP
    snap: dict[str, Any] = {}
    for stat in _SNAPSHOT_STATS:
        snap[stat] = row.get(col_map[stat])
    snap["last_match_date"] = row["date"]
    return snap


def build_match_row(
    home_snap: dict[str, Any],
    away_snap: dict[str, Any],
    *,
    neutral: bool = True,
) -> pd.DataFrame:
    row: dict[str, Any] = {"neutral": neutral}
    for stat in _SNAPSHOT_STATS:
        row[_HOME_COL_MAP[stat]] = home_snap[stat]
        row[_AWAY_COL_MAP[stat]] = away_snap[stat]

    home_elo = home_snap.get("elo")
    away_elo = away_snap.get("elo")
    home_rank = home_snap.get("fifa_rank")
    away_rank = away_snap.get("fifa_rank")
    row["elo_diff"] = (
        float(home_elo) - float(away_elo)
        if home_elo is not None
        and away_elo is not None
        and pd.notna(home_elo)
        and pd.notna(away_elo)
        else np.nan
    )
    row["fifa_rank_diff"] = (
        float(home_rank) - float(away_rank)
        if home_rank is not None
        and away_rank is not None
        and pd.notna(home_rank)
        and pd.notna(away_rank)
        else np.nan
    )
    return pd.DataFrame([row])


def predict_match_proba(
    pipeline: Any,
    home_snap: dict[str, Any],
    away_snap: dict[str, Any],
    *,
    neutral: bool = True,
) -> tuple[float, float, float]:
    row = build_match_row(home_snap, away_snap, neutral=neutral)
    x, _ = prepare_xy(row.assign(result="Win"))
    proba = pipeline.predict_proba(x)[0]
    return float(proba[0]), float(proba[1]), float(proba[2])


def build_match_probability_cache(
    pipeline: Any,
    snapshots: dict[str, dict[str, Any]],
    teams: list[str],
) -> dict[tuple[str, str], tuple[float, float, float]]:
    from src.config.constants import HOSTS

    cache: dict[tuple[str, str], tuple[float, float, float]] = {}
    for home in teams:
        for away in teams:
            if home == away:
                continue
            neutral = True
            if home in HOSTS and away not in HOSTS or away in HOSTS and home not in HOSTS:
                neutral = False
            cache[(home, away)] = predict_match_proba(
                pipeline, snapshots[home], snapshots[away], neutral=neutral
            )
    return cache
