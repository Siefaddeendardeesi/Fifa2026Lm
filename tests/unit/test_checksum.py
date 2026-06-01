"""Tests for src.utils.checksum."""

from __future__ import annotations

from pathlib import Path

from src.utils.checksum import compute_sha256, verify_checksum


def test_compute_and_verify_sha256(tmp_path: Path) -> None:
    f = tmp_path / "data.bin"
    f.write_bytes(b"hello fifa")
    digest = compute_sha256(f)
    assert len(digest) == 64
    assert verify_checksum(f, digest) is True
    assert verify_checksum(f, digest.upper()) is True
    assert verify_checksum(f, "0" * 64) is False
