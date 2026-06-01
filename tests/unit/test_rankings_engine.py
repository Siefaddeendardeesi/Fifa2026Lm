"""Tests for src.rankings.engine."""

from __future__ import annotations

import pandas as pd
import pytest

from src.rankings.engine import (
    RankingEngine,
    RankingMethod,
    active_teams,
    rank_by_elo,
    rank_by_model,
    rank_hybrid,
    rank_teams,
    select_pool,
)
from src.rankings.predictor import extract_team_snapshot
from src.utils.exceptions import RankingError


def test_active_teams(features_df) -> None:
    since = pd.Timestamp("2020-01-01")
    teams = active_teams(features_df, since)
    assert len(teams) > 10


def test_select_pool(features_df) -> None:
    since = pd.Timestamp("2020-01-01")
    teams = active_teams(features_df, since)
    snaps = {t: extract_team_snapshot(features_df, t) for t in teams[:60]}
    snaps = {k: v for k, v in snaps.items() if v}
    pool = select_pool(snaps, list(snaps.keys()), pool_size=10)
    assert len(pool) <= 10


def test_rank_by_elo(features_df) -> None:
    teams = ["Brazil", "Argentina", "France"]
    snaps = {t: extract_team_snapshot(features_df, t) for t in teams}
    snaps = {k: v for k, v in snaps.items() if v and pd.notna(v.get("elo"))}
    if len(snaps) < 2:
        pytest.skip("elo snapshots missing")
    df = rank_by_elo(snaps, list(snaps.keys()))
    assert "rank" in df.columns


def test_rank_by_model(trained_pipeline, features_df) -> None:
    teams = ["Brazil", "Argentina", "France", "Germany"]
    snaps = {t: extract_team_snapshot(features_df, t) for t in teams}
    snaps = {k: v for k, v in snaps.items() if v}
    if len(snaps) < 4:
        pytest.skip("snapshots missing")
    df = rank_by_model(snaps, list(snaps.keys()), trained_pipeline)
    assert "avg_win_prob" in df.columns


def test_rank_hybrid(features_df, trained_pipeline) -> None:
    teams = ["Brazil", "Argentina", "France"]
    snaps = {t: extract_team_snapshot(features_df, t) for t in teams}
    snaps = {k: v for k, v in snaps.items() if v}
    if len(snaps) < 3:
        pytest.skip("snapshots missing")
    elo_df = rank_by_elo(snaps, list(snaps.keys()))
    model_df = rank_by_model(snaps, list(snaps.keys()), trained_pipeline)
    hybrid = rank_hybrid(elo_df, model_df)
    assert "hybrid_score" in hybrid.columns


def test_ranking_engine_methods(features_df, trained_pipeline, test_settings) -> None:
    engine = RankingEngine()
    for method in (RankingMethod.ELO, RankingMethod.MODEL, RankingMethod.HYBRID):
        df = engine.compute(method=method, since="2020-01-01", pool_size=8, df=features_df)
        assert len(df) >= 2


def test_ranking_engine_insufficient_pool(features_df) -> None:
    engine = RankingEngine()
    tiny = features_df.head(5)
    with pytest.raises(RankingError):
        engine.compute(method=RankingMethod.MODEL, since="2099-01-01", pool_size=48, df=tiny)


def test_rank_teams_backward_compat(features_df, trained_pipeline) -> None:
    df = rank_teams(features_df, since="2020-01-01", pool_size=6)
    assert "rank" in df.columns
