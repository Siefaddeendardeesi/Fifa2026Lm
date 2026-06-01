"""Team name normalization via mapping.csv."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import MAPPING_CSV, UNMAPPED_LOG


def load_mapping(path: Path | None = None) -> dict[str, str]:
    mapping_path = path or MAPPING_CSV
    if not mapping_path.exists():
        return {}
    df = pd.read_csv(mapping_path)
    return dict(zip(df["raw_name"].astype(str), df["canonical_name"].astype(str), strict=True))


def normalize_team_name(name: str, mapping: dict[str, str]) -> str:
    if pd.isna(name):
        return name
    name = str(name).strip()
    return mapping.get(name, name)


def normalize_teams(
    df: pd.DataFrame,
    mapping: dict[str, str] | None = None,
    log_unmapped: bool = True,
) -> pd.DataFrame:
    """Apply canonical team names to home_team and away_team columns."""
    mapping = mapping or load_mapping()
    out = df.copy()
    for col in ("home_team", "away_team"):
        if col in out.columns:
            out[col] = out[col].apply(lambda x: normalize_team_name(x, mapping))

    if log_unmapped and mapping and {"home_team", "away_team"}.issubset(out.columns):
        _log_unmapped(out, mapping)
    return out


def _log_unmapped(df: pd.DataFrame, mapping: dict[str, str]) -> None:
    """Log team names that were not in mapping (for iterative fixes)."""
    canonical = set(mapping.values()) | set(mapping.keys())
    all_teams = set(df["home_team"].dropna()) | set(df["away_team"].dropna())
    unmapped = sorted(t for t in all_teams if t not in canonical)
    if unmapped:
        UNMAPPED_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(UNMAPPED_LOG, "w", encoding="utf-8") as f:
            f.write("\n".join(unmapped))
        print(f"Logged {len(unmapped)} unmapped team names to {UNMAPPED_LOG}")
