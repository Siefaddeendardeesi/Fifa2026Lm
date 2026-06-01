"""Load World Cup 2026 squad reference data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from src.config import REFERENCE_DIR

SQUADS_JSON = REFERENCE_DIR / "wc2026_squads.json"


def load_wc2026_squads(path: Path | None = None) -> dict[str, Any]:
    """Return squad payload keyed by team name."""
    squads_path = path or SQUADS_JSON
    if not squads_path.exists():
        return {"squads": {}}
    with open(squads_path, encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def teams_with_squads(path: Path | None = None) -> list[str]:
    """Sorted list of teams that have announced squad data."""
    data = load_wc2026_squads(path)
    return sorted(data.get("squads", {}).keys())


def get_team_squad(team: str, path: Path | None = None) -> dict[str, Any] | None:
    """Return squad entry for a team, or None if not announced."""
    data = load_wc2026_squads(path)
    squads = data.get("squads", {})
    entry = squads.get(team)
    return cast(dict[str, Any] | None, entry)
