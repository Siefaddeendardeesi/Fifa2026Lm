"""Tests for src.features.store."""

from __future__ import annotations

import pandas as pd
import pytest

from src.features.store import (
    EloFeatureTransformer,
    FeatureRegistry,
    FeatureStore,
    FormFeatureTransformer,
    get_default_registry,
)


def test_feature_registry_register_and_list() -> None:
    reg = FeatureRegistry()
    t = FormFeatureTransformer(window=5)
    reg.register(t)
    assert reg.get("form_features").window == 5
    assert len(reg.list_features()) == 1


def test_feature_registry_unknown_raises() -> None:
    with pytest.raises(KeyError):
        FeatureRegistry().get("missing")


def test_form_transformer_output_columns() -> None:
    cols = FormFeatureTransformer(window=10).get_output_columns()
    assert "home_form_wins_10" in cols


def test_elo_transformer_on_matches(sample_matches_df: pd.DataFrame) -> None:
    out = EloFeatureTransformer().transform(sample_matches_df)
    assert "home_elo" in out.columns


def test_feature_store_build_and_save(sample_matches_df, test_settings, tmp_path) -> None:
    store = FeatureStore(registry=FeatureRegistry())
    store.registry.register(FormFeatureTransformer(window=10))
    store.registry.register(EloFeatureTransformer())
    out = store.build_features(
        sample_matches_df, transformer_names=["form_features", "elo_features"]
    )
    path = store.save(out, tmp_path / "feat.parquet")
    loaded = store.load(path)
    assert len(loaded) == len(out)


def test_get_default_registry() -> None:
    reg = get_default_registry()
    assert "form_features" in reg._transformers
