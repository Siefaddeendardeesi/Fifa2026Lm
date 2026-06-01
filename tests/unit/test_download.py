"""Tests for src.etl.download."""

from __future__ import annotations

import zipfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.etl import download


def test_ensure_dir(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "dir"
    download._ensure_dir(target)
    assert target.is_dir()


def test_download_url_writes_file(mocker, tmp_path: Path) -> None:
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.content = b"csv,data"
    mocker.patch("src.etl.download.requests.get", return_value=mock_resp)
    dest = tmp_path / "out.csv"
    download._download_url("http://example.com/data.csv", dest)
    assert dest.read_bytes() == b"csv,data"


def test_download_kaggle_dataset_success(mocker, tmp_path: Path) -> None:
    mock_api = MagicMock()
    mocker.patch("kaggle.api.kaggle_api_extended.KaggleApi", return_value=mock_api)
    download.download_kaggle_dataset("user/dataset", tmp_path)
    mock_api.authenticate.assert_called_once()
    mock_api.dataset_download_files.assert_called_once()


def test_download_kaggle_dataset_failure(mocker, tmp_path: Path) -> None:
    mocker.patch(
        "kaggle.api.kaggle_api_extended.KaggleApi",
        side_effect=ImportError("no kaggle"),
    )
    with pytest.raises(RuntimeError, match="Kaggle download failed"):
        download.download_kaggle_dataset("user/dataset", tmp_path)


def test_download_github_fallbacks(mocker, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(download, "RAW_DIR", tmp_path)
    monkeypatch.setattr(download, "GITHUB_FALLBACKS", {tmp_path / "results.csv": "http://x"})
    mocker.patch("src.etl.download._download_url")
    download.download_github_fallbacks()
    download._download_url.assert_called_once()


def test_download_all_skip_kaggle(mocker, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(download, "RAW_DIR", tmp_path)
    mocker.patch("src.etl.download.download_github_fallbacks")
    mocker.patch("src.etl.download.download_fjelstul_csvs")
    mocker.patch("src.etl.download.download_elo")
    download.download_all(skip_kaggle=True)
    download.download_github_fallbacks.assert_called_once()


def test_extract_zip_if_needed(tmp_path: Path) -> None:
    zpath = tmp_path / "data.zip"
    dest = tmp_path / "out"
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("file.txt", "content")
    download.extract_zip_if_needed(zpath, dest)
    assert (dest / "file.txt").read_text(encoding="utf-8") == "content"


def test_download_elo_skips_existing(mocker, tmp_path: Path, monkeypatch) -> None:
    elo = tmp_path / "elo.csv"
    elo.write_text("exists", encoding="utf-8")
    monkeypatch.setattr(download, "ELO_CSV", elo)
    url_mock = mocker.patch("src.etl.download._download_url")
    download.download_elo()
    url_mock.assert_not_called()
