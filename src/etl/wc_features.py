"""World Cup title and appearance features from Fjelstul database."""

from __future__ import annotations

import pandas as pd

from src.config import FJELSTUL_DIR
from src.etl.normalize import normalize_teams


def _load_tournaments() -> pd.DataFrame:
    path = FJELSTUL_DIR / "tournaments.csv"
    if not path.exists():
        return pd.DataFrame(columns=["year", "winner", "start_date"])

    t = pd.read_csv(path)
    t["start_date"] = pd.to_datetime(t.get("start_date", t.get("year")), errors="coerce")
    if t["start_date"].isna().all() and "year" in t.columns:
        t["start_date"] = pd.to_datetime(t["year"].astype(str) + "-06-01")
    winner_col = "winner" if "winner" in t.columns else "winner_name"
    t["winner"] = t[winner_col] if winner_col in t.columns else None
    return t[["start_date", "winner"]].dropna(subset=["start_date"])


def _titles_by_date(tournaments: pd.DataFrame) -> pd.DataFrame:
    """For each title win, record team and date."""
    rows = []
    for _, row in tournaments.iterrows():
        if pd.notna(row["winner"]):
            rows.append({"team": str(row["winner"]), "title_date": row["start_date"]})
    return pd.DataFrame(rows)


def _appearances_by_date() -> pd.DataFrame:
    path = FJELSTUL_DIR / "qualified_teams.csv"
    if not path.exists():
        return pd.DataFrame(columns=["team", "appearance_date"])

    qt = pd.read_csv(path)
    year_col = "year" if "year" in qt.columns else "tournament_id"
    team_col = "team_name" if "team_name" in qt.columns else "team"
    qt["appearance_date"] = pd.to_datetime(
        qt[year_col].astype(str).str.extract(r"(\d{4})")[0] + "-06-01",
        errors="coerce",
    )
    qt["team"] = qt[team_col].astype(str)
    return qt[["team", "appearance_date"]].dropna()


def _count_before(dates: pd.Series, events: pd.DataFrame, team: str, date_col: str) -> int:
    if events.empty:
        return 0
    mask = (events["team"] == team) & (events[date_col] < dates)
    return int(mask.sum())


def add_wc_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Add home_wc_titles and away_wc_titles as of each match date."""
    out = matches.copy()
    tournaments = normalize_teams(_load_tournaments())
    titles = normalize_teams(_titles_by_date(tournaments))
    appearances = normalize_teams(_appearances_by_date())

    if titles.empty and appearances.empty:
        out["home_wc_titles"] = 0
        out["away_wc_titles"] = 0
        return out

    def titles_for(team: str, dt: pd.Timestamp) -> int:
        if titles.empty:
            return 0
        return int(((titles["team"] == team) & (titles["title_date"] < dt)).sum())

    out["home_wc_titles"] = out.apply(lambda r: titles_for(r["home_team"], r["date"]), axis=1)
    out["away_wc_titles"] = out.apply(lambda r: titles_for(r["away_team"], r["date"]), axis=1)
    return out
