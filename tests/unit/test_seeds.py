"""Tests for src.utils.seeds."""

from __future__ import annotations

import numpy as np

from src.utils.seeds import set_global_seed


def test_set_global_seed_returns_value(test_settings) -> None:
    seed = set_global_seed(123)
    assert seed == 123
    a = np.random.rand()
    set_global_seed(123)
    b = np.random.rand()
    assert a == b


def test_set_global_seed_uses_settings_default(test_settings) -> None:
    assert set_global_seed() == test_settings.random_seed
