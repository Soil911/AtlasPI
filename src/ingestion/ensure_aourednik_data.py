"""Ensure aourednik/historical-basemaps raw data is available.

On container startup, if the aourednik dataset is missing, clone it.
This keeps the Docker image small while enabling boundary enrichment
on any fresh deploy.

Can be called from main.py startup hook.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
AOUREDNIK_DIR = RAW_DIR / "aourednik-historical-basemaps"
AOUREDNIK_URL = "https://github.com/aourednik/historical-basemaps.git"


def ensure_aourednik(timeout: int = 120) -> bool:
    """Clone aourednik data if missing. Returns True if available."""
    expected_sample = AOUREDNIK_DIR / "geojson" / "world_1500.geojson"
    if expected_sample.exists():
        logger.info("aourednik data already present at %s", AOUREDNIK_DIR)
        return True

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("Cloning aourednik/historical-basemaps (CC BY 4.0)...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", AOUREDNIK_URL, str(AOUREDNIK_DIR)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            logger.warning(
                "git clone failed (rc=%d): %s",
                result.returncode,
                result.stderr[:500] if result.stderr else "(no stderr)",
            )
            return False

        if expected_sample.exists():
            logger.info("aourednik data cloned successfully")
            return True
        else:
            logger.warning("aourednik clone succeeded but expected file missing")
            return False
    except subprocess.TimeoutExpired:
        logger.warning("aourednik clone timed out after %ds", timeout)
        return False
    except FileNotFoundError:
        logger.warning("git not available — aourednik fetch skipped")
        return False
    except Exception as exc:
        logger.warning("aourednik fetch error: %s", exc)
        return False
