"""Configurazione centralizzata di AtlasPI."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "atlaspi.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

APP_VERSION = "1.0.0"
APP_TITLE = "AtlasPI"
APP_DESCRIPTION = "Database geografico storico strutturato per agenti AI"
