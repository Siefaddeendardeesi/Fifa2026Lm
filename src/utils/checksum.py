"""File checksum utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path


def compute_sha256(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksum(path: Path, expected: str) -> bool:
    """Verify file matches expected SHA-256 digest."""
    return compute_sha256(path) == expected.lower()
