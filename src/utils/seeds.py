"""Reproducibility utilities."""

from __future__ import annotations

import os
import random

import numpy as np

from src.config.settings import get_settings


def set_global_seed(seed: int | None = None) -> int:
    """Set random seeds for Python, NumPy, and environment."""
    settings = get_settings()
    seed = seed if seed is not None else settings.random_seed
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    return seed
