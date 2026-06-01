"""Wikipedia manager history scraper (optional enrichment)."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import requests

from src.config import MANAGERS_DIR

WIKI_BASE = "https://en.wikipedia.org/wiki/"


def _wiki_slug(team: str) -> str:
    slug = team.replace(" ", "_")
    return f"{slug}_national_football_team_manager_history"


def fetch_manager_history(team: str, cache_dir: Path | None = None) -> pd.DataFrame | None:
    """Scrape manager history table from Wikipedia."""
    cache_dir = cache_dir or MANAGERS_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{team.replace(' ', '_')}.csv"

    if cache_file.exists():
        return pd.read_csv(cache_file, parse_dates=["from", "to"])

    url = WIKI_BASE + _wiki_slug(team)
    try:
        headers = {"User-Agent": "Fifa2026Lm/1.0 (research project)"}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        tables = pd.read_html(response.text)
    except Exception as exc:
        print(f"Could not fetch managers for {team}: {exc}")
        return None

    manager_table = None
    for table in tables:
        cols = [str(c).lower() for c in table.columns]
        if any("manager" in c or "coach" in c for c in cols):
            manager_table = table
            break

    if manager_table is None or manager_table.empty:
        return None

    manager_table.columns = [
        re.sub(r"\s+", "_", str(c).lower().strip()) for c in manager_table.columns
    ]
    manager_col = next(
        (c for c in manager_table.columns if "manager" in c or "coach" in c or "name" in c),
        manager_table.columns[0],
    )
    from_col = next((c for c in manager_table.columns if "from" in c or "start" in c), None)
    to_col = next((c for c in manager_table.columns if "to" in c or "end" in c), None)

    out = pd.DataFrame()
    out["manager"] = manager_table[manager_col]
    if from_col:
        out["from"] = pd.to_datetime(manager_table[from_col], errors="coerce")
    if to_col:
        out["to"] = pd.to_datetime(manager_table[to_col], errors="coerce")
    out["team"] = team
    out.to_csv(cache_file, index=False)
    return out


def resolve_manager(
    team: str, match_date: pd.Timestamp, cache: dict[str, pd.DataFrame | None]
) -> str | None:
    if team not in cache:
        cache[team] = fetch_manager_history(team)
    history = cache.get(team)
    if history is None or history.empty:
        return None
    for _, row in history.iterrows():
        start = row.get("from")
        end = row.get("to")
        if pd.isna(start):
            continue
        if pd.isna(end):
            end = pd.Timestamp.max
        if start <= match_date <= end:
            manager = row.get("manager")
            return str(manager) if manager is not None and not pd.isna(manager) else None
    return None


def add_manager_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Optional: add home_manager and away_manager columns."""
    out = matches.copy()
    cache: dict[str, pd.DataFrame | None] = {}
    teams = set(out["home_team"]) | set(out["away_team"])

    for team in teams:
        fetch_manager_history(team)

    out["home_manager"] = out.apply(
        lambda r: resolve_manager(r["home_team"], r["date"], cache), axis=1
    )
    out["away_manager"] = out.apply(
        lambda r: resolve_manager(r["away_team"], r["date"], cache), axis=1
    )
    return out
