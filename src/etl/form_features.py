"""Rolling form features over last N matches per team."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import FORM_WINDOW


def _team_match_log(matches: pd.DataFrame) -> pd.DataFrame:
    """Expand matches to one row per team appearance."""
    home = matches[["date", "home_team", "away_team", "home_score", "away_score"]].copy()
    home["team"] = home["home_team"]
    home["goals_for"] = home["home_score"]
    home["goals_against"] = home["away_score"]
    home["is_home"] = True

    away = matches[["date", "home_team", "away_team", "home_score", "away_score"]].copy()
    away["team"] = away["away_team"]
    away["goals_for"] = away["away_score"]
    away["goals_against"] = away["home_score"]
    away["is_home"] = False

    log = pd.concat([home, away], ignore_index=True)
    log["win"] = (log["goals_for"] > log["goals_against"]).astype(int)
    log["draw"] = (log["goals_for"] == log["goals_against"]).astype(int)
    log["loss"] = (log["goals_for"] < log["goals_against"]).astype(int)
    log["clean_sheet"] = (log["goals_against"] == 0).astype(int)
    return log.sort_values(["team", "date"]).reset_index(drop=True)


def _rolling_form(log: pd.DataFrame, window: int) -> pd.DataFrame:
    """Rolling stats excluding current match (shift by 1)."""
    stats = ["win", "draw", "loss", "goals_for", "goals_against", "clean_sheet"]
    rolled = log.copy()
    grouped = rolled.groupby("team", group_keys=False)

    for col in stats:
        rolled[f"form_{col}"] = grouped[col].transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).sum()
        )

    rolled["form_matches"] = grouped.cumcount()
    rolled["form_matches"] = rolled.groupby("team")["form_matches"].shift(1).fillna(0)
    rolled["form_points"] = 3 * rolled["form_win"] + rolled["form_draw"]
    rolled["form_goal_diff"] = rolled["form_goals_for"] - rolled["form_goals_against"]
    denom = rolled["form_matches"].clip(upper=window).replace(0, np.nan)
    rolled["form_win_rate"] = rolled["form_win"] / denom
    return rolled


def add_form_features(matches: pd.DataFrame, window: int = FORM_WINDOW) -> pd.DataFrame:
    """Attach home/away rolling form features to match rows."""
    log = _team_match_log(matches)
    rolled = _rolling_form(log, window)

    form_map = {
        "form_win": "wins",
        "form_draw": "draws",
        "form_loss": "losses",
        "form_goals_for": "goals_for",
        "form_goals_against": "goals_against",
        "form_clean_sheet": "clean_sheets",
        "form_points": "points",
        "form_goal_diff": "goal_diff",
        "form_win_rate": "win_rate",
    }

    out = matches.copy()
    for is_home, prefix in ((True, "home"), (False, "away")):
        side = rolled[rolled["is_home"] == is_home][
            ["date", "home_team", "away_team"] + list(form_map.keys())
        ].copy()
        rename = {src: f"{prefix}_form_{dst}_{window}" for src, dst in form_map.items()}
        side = side.rename(columns=rename)
        out = out.merge(side, on=["date", "home_team", "away_team"], how="left")

    # Standardize column names to _10 suffix for FINAL_COLUMNS
    if window == 10:
        rename_final = {}
        for prefix in ("home", "away"):
            for dst in form_map.values():
                rename_final[f"{prefix}_form_{dst}_10"] = f"{prefix}_form_{dst}_10"
        out = out.rename(columns=rename_final)

    return out
