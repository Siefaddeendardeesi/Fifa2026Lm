"""Merge ELO ratings onto matches (computed from history or snapshot fallback)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.etl.normalize import normalize_teams


def compute_elo_from_matches(
    matches: pd.DataFrame,
    k_factor: float = 20.0,
    home_advantage: float = 100.0,
    initial_rating: float = 1500.0,
) -> pd.DataFrame:
    """
    Compute point-in-time ELO ratings by replaying match history chronologically.
    Ratings are recorded before each match update.
    """
    ratings: dict[str, float] = {}
    records: list[dict[str, Any]] = []

    chron = matches.sort_values("date")

    for idx, row in chron.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        rh = ratings.get(home, initial_rating)
        ra = ratings.get(away, initial_rating)

        records.append(
            {
                "_idx": idx,
                "home_elo": rh,
                "away_elo": ra,
            }
        )

        rh_adj = rh + home_advantage
        expected_home = 1.0 / (1.0 + 10 ** ((ra - rh_adj) / 400.0))

        if row["home_score"] > row["away_score"]:
            actual_home = 1.0
        elif row["home_score"] == row["away_score"]:
            actual_home = 0.5
        else:
            actual_home = 0.0

        delta = k_factor * (actual_home - expected_home)
        ratings[home] = rh + delta
        ratings[away] = ra - delta

    elo_df = pd.DataFrame(records).set_index("_idx")
    result = matches.copy()
    result["home_elo"] = elo_df["home_elo"]
    result["away_elo"] = elo_df["away_elo"]
    result["elo_diff"] = result["home_elo"] - result["away_elo"]
    return result


def merge_elo(matches: pd.DataFrame, elo: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Add home_elo, away_elo, elo_diff.
    Uses chronological ELO computation by default.
    """
    if elo is not None and not elo.empty and elo["date"].nunique() > 1:
        out = matches.copy()
        elo = normalize_teams(elo.copy())
        elo = elo.rename(columns={"date": "elo_date"}).sort_values(["team", "elo_date"])

        for team_col, prefix in (("home_team", "home"), ("away_team", "away")):
            side = out[[team_col, "date"]].copy().sort_values([team_col, "date"])
            rank_side = elo.rename(columns={"team": team_col}).sort_values([team_col, "elo_date"])
            merged = pd.merge_asof(
                side,
                rank_side,
                left_on="date",
                right_on="elo_date",
                by=team_col,
                direction="backward",
            )
            out[f"{prefix}_elo"] = merged["elo"].values

        out["elo_diff"] = out["home_elo"] - out["away_elo"]
        return out

    return compute_elo_from_matches(matches)
