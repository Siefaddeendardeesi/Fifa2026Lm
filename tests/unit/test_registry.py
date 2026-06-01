"""Tests for src.models.registry."""

from __future__ import annotations

from pathlib import Path

import joblib
import pytest

from src.models.base import RandomForestModel
from src.models.registry import ModelMetadata, ModelRegistry
from src.utils.exceptions import ModelNotFoundError


def _train_tiny_model(path: Path, features_df) -> Path:
    impl = RandomForestModel()
    train = features_df.head(100)
    x, y = impl.prepare_xy(train)
    pipe = impl.build_pipeline(list(x.columns))
    pipe.fit(x, y)
    joblib.dump(pipe, path)
    return path


def test_registry_register_and_list(tmp_path: Path, features_df, test_settings) -> None:
    reg = ModelRegistry(registry_path=tmp_path / "registry")
    model_path = tmp_path / "model.joblib"
    _train_tiny_model(model_path, features_df)
    meta = reg.register(model_path, model_type="random_forest", metrics={"accuracy": 0.5})
    assert isinstance(meta, ModelMetadata)
    assert len(reg.list_models()) == 1


def test_registry_promote_and_champion(tmp_path: Path, features_df, test_settings) -> None:
    reg = ModelRegistry(registry_path=tmp_path / "registry")
    model_path = tmp_path / "model.joblib"
    _train_tiny_model(model_path, features_df)
    meta = reg.register(model_path, model_type="random_forest", metrics={"f1_macro": 0.4})
    promoted = reg.promote_to_champion(meta.version)
    assert promoted.status == "champion"
    champion = reg.get_champion()
    assert champion is not None
    assert champion.version == meta.version


def test_registry_rollback(tmp_path: Path, features_df, test_settings) -> None:
    reg = ModelRegistry(registry_path=tmp_path / "registry")
    p1 = tmp_path / "m1.joblib"
    p2 = tmp_path / "m2.joblib"
    _train_tiny_model(p1, features_df)
    _train_tiny_model(p2, features_df)
    m1 = reg.register(p1, model_type="random_forest", metrics={"accuracy": 0.1})
    reg.register(p2, model_type="random_forest", metrics={"accuracy": 0.2})
    reg.promote_to_champion(m1.version)
    rolled = reg.rollback(m1.version)
    assert rolled.version == m1.version


def test_load_champion_from_registry(
    tmp_path: Path, features_df, test_settings, monkeypatch
) -> None:
    reg = ModelRegistry(registry_path=tmp_path / "registry")
    model_path = tmp_path / "model.joblib"
    _train_tiny_model(model_path, features_df)
    meta = reg.register(model_path, model_type="random_forest", metrics={"accuracy": 0.5})
    reg.promote_to_champion(meta.version)
    fake_model_path = tmp_path / "nonexistent_champion.joblib"
    monkeypatch.setattr(
        "src.models.registry.get_settings",
        lambda: type("S", (), {"model_path": fake_model_path})(),
    )
    loaded = reg.load_champion()
    assert hasattr(loaded, "predict")


def test_promote_missing_raises(tmp_path: Path, test_settings) -> None:
    reg = ModelRegistry(registry_path=tmp_path / "registry")
    with pytest.raises(ModelNotFoundError):
        reg.promote_to_champion("missing_version")
