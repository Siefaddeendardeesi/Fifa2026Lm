"""Tests for src.etl.squads."""

from __future__ import annotations

import json
from pathlib import Path

from src.etl.squads import get_team_squad, load_wc2026_squads, teams_with_squads


def test_load_wc2026_squads_from_project(project_root) -> None:
    data = load_wc2026_squads(project_root / "data" / "reference" / "wc2026_squads.json")
    assert "squads" in data


def test_load_wc2026_squads_missing_returns_empty(tmp_path: Path) -> None:
    assert load_wc2026_squads(tmp_path / "missing.json") == {"squads": {}}


def test_teams_with_squads(project_root) -> None:
    path = project_root / "data" / "reference" / "wc2026_squads.json"
    if not path.exists():
        return
    teams = teams_with_squads(path)
    assert isinstance(teams, list)


def test_get_team_squad(tmp_path: Path) -> None:
    path = tmp_path / "squads.json"
    path.write_text(
        json.dumps({"squads": {"Brazil": {"players": []}}}),
        encoding="utf-8",
    )
    assert get_team_squad("Brazil", path) == {"players": []}
    assert get_team_squad("Unknown", path) is None
