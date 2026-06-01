"""Optional Transfermarkt squad values via Apify."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests

from src.config import TRANSFERMARKT_CSV


def load_squad_values(path: Path | None = None) -> pd.DataFrame:
    """Load cached squad value data if available."""
    csv_path = path or TRANSFERMARKT_CSV
    if not csv_path.exists():
        return pd.DataFrame(columns=["team", "date", "squad_value"])
    df = pd.read_csv(csv_path, parse_dates=["date"])
    return df


def fetch_via_apify(teams: list[str]) -> pd.DataFrame:
    """
    Fetch squad values from Apify Transfermarkt scraper.
    Requires APIFY_TOKEN in environment.
    """
    token = os.getenv("APIFY_TOKEN")
    if not token:
        print("APIFY_TOKEN not set — skipping Transfermarkt download")
        return pd.DataFrame(columns=["team", "date", "squad_value"])

    # Generic Apify run — actor ID may vary; cache results locally
    actor_id = "curious_coder/transfermarkt-scraper"
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"teams": teams}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        items = data.get("data", {}).get("items", [])
        if not items:
            return pd.DataFrame(columns=["team", "date", "squad_value"])
        df = pd.DataFrame(items)
        df.to_csv(TRANSFERMARKT_CSV, index=False)
        return df
    except Exception as exc:
        print(f"Apify Transfermarkt fetch failed: {exc}")
        return pd.DataFrame(columns=["team", "date", "squad_value"])


def merge_squad_values(matches: pd.DataFrame, values: pd.DataFrame) -> pd.DataFrame:
    """Merge latest squad value before match date for each team."""
    out = matches.copy()
    if values.empty:
        out["home_squad_value"] = pd.NA
        out["away_squad_value"] = pd.NA
        return out

    values = values.sort_values(["team", "date"])
    for team_col, prefix in (("home_team", "home"), ("away_team", "away")):
        side = out[[team_col, "date"]].copy().sort_values("date")
        val = values.rename(columns={"team": team_col})
        merged = pd.merge_asof(
            side,
            val,
            left_on="date",
            right_on="date",
            by=team_col,
            direction="backward",
        )
        out[f"{prefix}_squad_value"] = merged["squad_value"].values
    return out
