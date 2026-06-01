"""Team ranking engine: ELO, model-based, and hybrid."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.config.settings import get_settings
from src.rankings.predictor import extract_team_snapshot, predict_match_proba
from src.utils.exceptions import RankingError
from src.utils.logging import get_logger

logger = get_logger(__name__)


class RankingMethod(StrEnum):
    ELO = "elo"
    MODEL = "model"
    HYBRID = "hybrid"


def active_teams(df: pd.DataFrame, since: pd.Timestamp) -> list[str]:
    recent = df[df["date"] >= since]
    return sorted(set(recent["home_team"]) | set(recent["away_team"]))


def select_pool(
    snapshots: dict[str, dict[str, Any]],
    teams: list[str],
    pool_size: int,
) -> list[str]:
    eligible = [t for t in teams if t in snapshots and pd.notna(snapshots[t].get("fifa_rank"))]
    if len(eligible) < pool_size:
        eligible = [t for t in teams if t in snapshots]
    eligible.sort(
        key=lambda t: (
            float(snapshots[t].get("fifa_rank") or 9999),
            -float(snapshots[t].get("elo") or 0),
        ),
    )
    return eligible[:pool_size]


def rank_by_elo(
    snapshots: dict[str, dict[str, Any]],
    teams: list[str],
) -> pd.DataFrame:
    rows = []
    for team in teams:
        if team not in snapshots:
            continue
        elo = snapshots[team].get("elo")
        if elo is None or pd.isna(elo):
            continue
        rows.append(
            {
                "team": team,
                "elo_score": float(elo),
                "fifa_rank": snapshots[team].get("fifa_rank"),
            }
        )
    out = pd.DataFrame(rows).sort_values("elo_score", ascending=False).reset_index(drop=True)
    out.insert(0, "rank", out.index + 1)
    return out


def rank_by_model(
    snapshots: dict[str, dict[str, Any]],
    pool: list[str],
    pipeline: Any,
    *,
    neutral: bool = True,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for team in pool:
        home_snap = snapshots[team]
        win_probs: list[float] = []
        for opp in pool:
            if opp == team:
                continue
            p_win, _, p_loss = predict_match_proba(
                pipeline, home_snap, snapshots[opp], neutral=neutral
            )
            win_probs.append(p_win)
            _, _, p_loss_away = predict_match_proba(
                pipeline, snapshots[opp], home_snap, neutral=neutral
            )
            win_probs.append(p_loss_away)
        rows.append(
            {
                "team": team,
                "avg_win_prob": float(np.mean(win_probs)),
                "fifa_rank": home_snap.get("fifa_rank"),
                "elo": home_snap.get("elo"),
            }
        )
    out = pd.DataFrame(rows).sort_values("avg_win_prob", ascending=False).reset_index(drop=True)
    out.insert(0, "rank", out.index + 1)
    return out


def rank_hybrid(
    elo_ranks: pd.DataFrame,
    model_ranks: pd.DataFrame,
    *,
    elo_weight: float = 0.4,
) -> pd.DataFrame:
    merged = elo_ranks[["team", "elo_score"]].merge(
        model_ranks[["team", "avg_win_prob"]], on="team", how="inner"
    )
    elo_norm = merged["elo_score"] / merged["elo_score"].max()
    model_norm = merged["avg_win_prob"] / merged["avg_win_prob"].max()
    merged["hybrid_score"] = elo_weight * elo_norm + (1 - elo_weight) * model_norm
    out = merged.sort_values("hybrid_score", ascending=False).reset_index(drop=True)
    out.insert(0, "rank", out.index + 1)
    return out


class RankingEngine:
    """Unified ranking engine."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def compute(
        self,
        *,
        method: RankingMethod = RankingMethod.MODEL,
        since: str = "2024-01-01",
        pool_size: int = 48,
        neutral: bool = True,
        df: pd.DataFrame | None = None,
        model_path: Path | None = None,
    ) -> pd.DataFrame:
        features = df if df is not None else pd.read_parquet(self.settings.features_parquet)
        features = features.copy()
        features["date"] = pd.to_datetime(features["date"])
        since_ts = pd.Timestamp(since)

        teams = active_teams(features, since_ts)
        raw_snapshots = {t: extract_team_snapshot(features, t) for t in teams}
        snapshots: dict[str, dict[str, Any]] = {
            t: snap for t, snap in raw_snapshots.items() if snap is not None
        }
        pool = select_pool(snapshots, teams, pool_size)

        if len(pool) < 2:
            raise RankingError("Need at least two teams with recent data in the pool.")

        if method == RankingMethod.ELO:
            return rank_by_elo(snapshots, pool)

        pipeline = joblib.load(model_path or self.settings.model_path)
        model_ranks = rank_by_model(snapshots, pool, pipeline, neutral=neutral)

        if method == RankingMethod.MODEL:
            model_ranks["pool_size"] = len(pool)
            return model_ranks

        elo_ranks = rank_by_elo(snapshots, pool)
        hybrid = rank_hybrid(elo_ranks, model_ranks)
        hybrid["pool_size"] = len(pool)
        logger.info("rankings_computed", method=method.value, pool_size=len(pool))
        return hybrid


def rank_teams(
    df: pd.DataFrame | None = None,
    *,
    model_path: Path | None = None,
    since: str = "2024-01-01",
    pool_size: int = 48,
    neutral: bool = True,
) -> pd.DataFrame:
    """Backward-compatible model-based ranking."""
    engine = RankingEngine()
    result = engine.compute(
        method=RankingMethod.MODEL,
        since=since,
        pool_size=pool_size,
        neutral=neutral,
        df=df,
        model_path=model_path,
    )
    if "avg_draw_prob" not in result.columns:
        result["avg_draw_prob"] = 0.0
    if "wc_titles" not in result.columns:
        result["wc_titles"] = None
    if "last_match_date" not in result.columns:
        result["last_match_date"] = None
    return result
