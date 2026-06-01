"""Download raw datasets from Kaggle, GitHub, and eloratings.net."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.config import (
    ELO_CSV,
    FJELSTUL_BASE_URL,
    FJELSTUL_DIR,
    FJELSTUL_FILES,
    KAGGLE_DATASETS,
    RAW_DIR,
    RESULTS_CSV,
)
from src.config.settings import get_settings
from src.utils.exceptions import ETLDownloadError
from src.utils.logging import get_logger

logger = get_logger(__name__)

GITHUB_FALLBACKS = {
    RESULTS_CSV: (
        "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
    ),
    RAW_DIR
    / "fifa_ranking_historical.csv": (
        "https://raw.githubusercontent.com/Dato-Futbol/fifa-ranking/master/ranking_fifa_historical.csv"
    ),
}


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


@retry(
    retry=retry_if_exception_type((requests.RequestException, ETLDownloadError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=1, max=30),
    reraise=True,
)
def _download_url(url: str, dest: Path) -> None:
    settings = get_settings()
    if settings.etl_cache_enabled and dest.exists() and dest.stat().st_size > 0:
        logger.info("download_cache_hit", path=str(dest))
        return
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ETLDownloadError(f"Failed to download {url}", details={"url": url}) from exc
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(response.content)
    logger.info("download_complete", source=url, dest=str(dest), bytes=len(response.content))


def download_kaggle_dataset(slug: str, dest_dir: Path) -> None:
    """Download and unzip a Kaggle dataset via the Kaggle Python API."""
    _ensure_dir(dest_dir)
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(slug, path=str(dest_dir), unzip=True)
        logger.info("kaggle_download_complete", slug=slug)
    except Exception as exc:
        raise RuntimeError(
            f"Kaggle download failed for {slug}. "
            "Ensure kaggle.json or KAGGLE_USERNAME/KAGGLE_KEY are configured.\n"
            f"{exc}"
        ) from exc


def _find_and_copy_results(dest: Path) -> None:
    """Locate results.csv after Kaggle unzip (filename may vary)."""
    candidates = list(RAW_DIR.rglob("results.csv"))
    if not candidates:
        candidates = list(RAW_DIR.rglob("*results*.csv"))
    if not candidates:
        raise FileNotFoundError("Could not find results.csv after Kaggle download")
    shutil.copy2(candidates[0], dest)
    logger.info("results_copied", dest=str(dest))


def download_github_fallbacks() -> None:
    """Download core files from public GitHub mirrors when Kaggle is unavailable."""
    for dest, url in GITHUB_FALLBACKS.items():
        if not dest.exists():
            _download_url(url, dest)


@retry(
    retry=retry_if_exception_type((requests.RequestException, ETLDownloadError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=1, max=30),
    reraise=True,
)
def _download_fjelstul_file(filename: str) -> None:
    url = f"{FJELSTUL_BASE_URL}/{filename}"
    dest = FJELSTUL_DIR / filename
    if dest.exists():
        logger.info("download_skip_existing", file=filename)
        return
    _download_url(url, dest)
    logger.info("fjelstul_download_complete", file=filename)


def download_fjelstul_csvs() -> None:
    """Fetch Fjelstul World Cup Database CSVs from GitHub."""
    _ensure_dir(FJELSTUL_DIR)
    for filename in FJELSTUL_FILES:
        _download_fjelstul_file(filename)


def download_elo() -> None:
    """Download world ELO ratings snapshot (TSV) from eloratings.net."""
    if ELO_CSV.exists():
        logger.info("download_skip_existing", file="elo.csv")
        return
    _download_url("https://www.eloratings.net/World.tsv", ELO_CSV)
    logger.info("elo_download_complete", dest=str(ELO_CSV))


def download_all(
    include_optional_kaggle: bool = False,
    skip_kaggle: bool = False,
) -> None:
    """Orchestrate all downloads."""
    _ensure_dir(RAW_DIR)
    logger.info("download_all_start", skip_kaggle=skip_kaggle)

    kaggle_ok = False
    if not skip_kaggle:
        try:
            download_kaggle_dataset(KAGGLE_DATASETS["results"], RAW_DIR)
            if not RESULTS_CSV.exists():
                _find_and_copy_results(RESULTS_CSV)

            download_kaggle_dataset(KAGGLE_DATASETS["fifa_ranking"], RAW_DIR)
            download_kaggle_dataset(KAGGLE_DATASETS["wc_1930_2022"], RAW_DIR / "wc_kaggle")

            if include_optional_kaggle:
                download_kaggle_dataset(KAGGLE_DATASETS["wc_1930_2018"], RAW_DIR / "wc_evangower")
                download_kaggle_dataset(
                    KAGGLE_DATASETS["fifa_ranking_alt"], RAW_DIR / "fifa_ranking_alt"
                )
            kaggle_ok = True
        except RuntimeError as exc:
            logger.warning("kaggle_unavailable", error=str(exc))

    if not kaggle_ok or skip_kaggle:
        download_github_fallbacks()

    download_fjelstul_csvs()
    download_elo()
    logger.info("download_all_complete")


def extract_zip_if_needed(zip_path: Path, dest_dir: Path) -> None:
    """Helper to manually extract a downloaded zip."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
