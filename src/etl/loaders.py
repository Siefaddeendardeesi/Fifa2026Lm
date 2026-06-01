"""Load raw CSV sources into typed DataFrames."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import RAW_DIR, RESULTS_CSV
from src.etl.normalize import normalize_teams


def derive_result(home_score: int, away_score: int) -> str:
    """
    Target from home team perspective only.
    Win  = home team won
    Draw = tie
    Loss = home team lost (away team won)
    """
    if home_score > away_score:
        return "Win"
    if home_score == away_score:
        return "Draw"
    return "Loss"


def load_matches(path: Path | None = None) -> pd.DataFrame:
    """Load international results and derive target column."""
    csv_path = path or RESULTS_CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}. Run: python scripts/download_data.py")

    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "home_team", "away_team", "home_score", "away_score"])

    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["result"] = df.apply(lambda r: derive_result(r["home_score"], r["away_score"]), axis=1)

    if "neutral" not in df.columns:
        df["neutral"] = False
    df["neutral"] = df["neutral"].fillna(False).astype(bool)

    keep = [
        "date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "neutral",
        "tournament",
        "city",
        "country",
        "result",
    ]
    keep = [c for c in keep if c in df.columns]
    df = df[keep].sort_values("date").reset_index(drop=True)
    return normalize_teams(df)


def find_fifa_ranking_file() -> Path | None:
    """Locate FIFA ranking CSV in raw directory."""
    preferred = RAW_DIR / "fifa_ranking_historical.csv"
    if preferred.exists():
        return preferred

    patterns = ["fifa_ranking*.csv", "*ranking*.csv"]
    for pattern in patterns:
        files = list(RAW_DIR.rglob(pattern))
        files = [
            f
            for f in files
            if "wc" not in f.name.lower()
            and "world-cup" not in str(f).lower()
            and "unmapped" not in f.name.lower()
        ]
        if files:
            return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return None


def load_fifa_rankings(path: Path | None = None) -> pd.DataFrame:
    """Load and normalize FIFA ranking data to long format."""
    csv_path = path or find_fifa_ranking_file()
    if csv_path is None or not csv_path.exists():
        raise FileNotFoundError("FIFA ranking CSV not found in data/raw/")

    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Dato-Futbol historical: team, total_points, date
    if "date" in df.columns and "team" in df.columns and "total_points" in df.columns:
        out = pd.DataFrame()
        out["rank_date"] = pd.to_datetime(df["date"], errors="coerce")
        out["team"] = df["team"].astype(str)
        out["total_points"] = pd.to_numeric(df["total_points"], errors="coerce")
        out["rank"] = out.groupby("rank_date")["total_points"].rank(ascending=False, method="min")
        out["confederation"] = pd.NA
        return out.dropna(subset=["rank_date", "team"]).sort_values(["team", "rank_date"])

    # cashncarry format: wide with rank_date column
    if "rank_date" in df.columns:
        id_cols = ["rank_date"]
        long_df = df.melt(id_vars=id_cols, var_name="team", value_name="rank")
        long_df["rank_date"] = pd.to_datetime(long_df["rank_date"], errors="coerce")
        long_df = long_df.dropna(subset=["rank_date", "rank"])
        long_df["rank"] = pd.to_numeric(long_df["rank"], errors="coerce")
        long_df = long_df.dropna(subset=["rank"])
        long_df["total_points"] = pd.NA
        long_df["confederation"] = pd.NA
        return long_df.sort_values(["team", "rank_date"])

    # Long format with country_full
    date_col = next((c for c in ("date", "rank_date", "ranking_date") if c in df.columns), None)
    team_col = next(
        (c for c in ("country_full", "team", "country", "nation") if c in df.columns), None
    )
    if date_col and team_col:
        out = pd.DataFrame()
        out["rank_date"] = pd.to_datetime(df[date_col], errors="coerce")
        out["team"] = df[team_col].astype(str)
        out["rank"] = pd.to_numeric(
            df.get("rank", df.get("total_ranking", pd.Series(dtype=float))),
            errors="coerce",
        )
        out["total_points"] = pd.to_numeric(df.get("total_points", pd.NA), errors="coerce")
        conf_col = next((c for c in df.columns if "confed" in c), None)
        out["confederation"] = df[conf_col] if conf_col else pd.NA
        if out["rank"].isna().all() and out["total_points"].notna().any():
            out["rank"] = out.groupby("rank_date")["total_points"].rank(
                ascending=False, method="min"
            )
        return out.dropna(subset=["rank_date", "team"]).sort_values(["team", "rank_date"])

    raise ValueError(f"Unrecognized FIFA ranking format in {csv_path}")


def load_elo(path: Path | None = None) -> pd.DataFrame:
    """Load ELO ratings (date, team, rating)."""
    from src.config import ELO_CSV

    csv_path = path or ELO_CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}")

    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    # elofootball.com format
    if "rank" in df.columns and "country" in df.columns:
        date_col = "date" if "date" in df.columns else df.columns[0]
        df["date"] = pd.to_datetime(df[date_col], format="%Y%m%d", errors="coerce")
        if df["date"].isna().all():
            df["date"] = pd.to_datetime(df[date_col], errors="coerce")
        out = pd.DataFrame(
            {
                "date": df["date"],
                "team": df["country"].astype(str),
                "elo": pd.to_numeric(df.get("elo", df.get("rating")), errors="coerce"),
            }
        )
        return out.dropna(subset=["date", "team", "elo"]).sort_values(["team", "date"])

    # Generic: date, team, elo/rating columns
    date_col = next((c for c in ("date", "rank_date") if c in df.columns), df.columns[0])
    team_col = next((c for c in ("team", "country", "nation") if c in df.columns), None)
    elo_col = next((c for c in ("elo", "rating", "elo_rating") if c in df.columns), None)
    if team_col and elo_col:
        out = pd.DataFrame(
            {
                "date": pd.to_datetime(df[date_col], errors="coerce"),
                "team": df[team_col].astype(str),
                "elo": pd.to_numeric(df[elo_col], errors="coerce"),
            }
        )
        return out.dropna(subset=["date", "team", "elo"]).sort_values(["team", "date"])

    raise ValueError(f"Unrecognized ELO format in {csv_path}")
