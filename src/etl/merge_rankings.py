"""Merge FIFA rankings and confederations onto matches (backward as-of join)."""

from __future__ import annotations

import pandas as pd

from src.etl.normalize import load_mapping, normalize_team_name


def _asof_merge_team(
    matches: pd.DataFrame,
    rankings: pd.DataFrame,
    team_col: str,
    prefix: str,
) -> pd.DataFrame:
    """Merge most recent ranking before match date for home or away team."""
    out = matches.copy()
    rename_map = {
        "rank": f"{prefix}_fifa_rank",
        "total_points": f"{prefix}_fifa_points",
        "confederation": f"{prefix}_confederation",
    }
    for new_col in rename_map.values():
        out[new_col] = pd.NA

    for team, idx in out.groupby(team_col).groups.items():
        team_rank = rankings[rankings["team"] == team].sort_values("rank_date")
        if team_rank.empty:
            continue
        team_rows = out.loc[idx].sort_values("date")
        merged = pd.merge_asof(
            team_rows[["date"]],
            team_rank,
            left_on="date",
            right_on="rank_date",
            direction="backward",
        )
        for old, new in rename_map.items():
            if old in merged.columns:
                out.loc[team_rows.index, new] = merged[old].values

    return out


def load_confederation_fallback() -> pd.DataFrame:
    """Load team confederation from Fjelstul teams.csv as fallback."""
    from src.config import FJELSTUL_DIR

    teams_path = FJELSTUL_DIR / "teams.csv"
    if not teams_path.exists():
        return pd.DataFrame(columns=["team", "confederation"])

    teams = pd.read_csv(teams_path)
    if "team_name" in teams.columns:
        out = pd.DataFrame(
            {
                "team": teams["team_name"],
                "confederation": teams.get("confederation", teams.get("confederation_code")),
            }
        )
    elif "team" in teams.columns:
        out = teams[["team", "confederation"]].copy()
    else:
        return pd.DataFrame(columns=["team", "confederation"])

    out = out.drop_duplicates("team")
    mapping = load_mapping()
    out["team"] = out["team"].apply(lambda x: normalize_team_name(x, mapping))
    return out


def merge_rankings(
    matches: pd.DataFrame,
    rankings: pd.DataFrame,
) -> pd.DataFrame:
    """Add home/away FIFA rank, points, confederation, and fifa_rank_diff."""
    out = matches.copy()
    mapping = load_mapping()
    rankings = rankings.copy()
    rankings["team"] = rankings["team"].apply(lambda x: normalize_team_name(x, mapping))

    out = _asof_merge_team(out, rankings, "home_team", "home")
    out = _asof_merge_team(out, rankings, "away_team", "away")

    out["fifa_rank_diff"] = out["away_fifa_rank"] - out["home_fifa_rank"]

    fallback = load_confederation_fallback()
    if not fallback.empty:
        fb = fallback.drop_duplicates("team").set_index("team")["confederation"]
        out["home_confederation"] = out["home_confederation"].fillna(out["home_team"].map(fb))
        out["away_confederation"] = out["away_confederation"].fillna(out["away_team"].map(fb))

    return out
