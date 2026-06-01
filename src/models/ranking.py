"""Backward-compatible re-exports."""

from src.rankings.engine import rank_teams
from src.rankings.predictor import (
    build_match_row,
    extract_team_snapshot,
    predict_match_proba,
)

__all__ = ["build_match_row", "extract_team_snapshot", "predict_match_proba", "rank_teams"]
