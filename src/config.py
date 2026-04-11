"""Configurazione centralizzata di AtlasPI con supporto .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ─── Applicazione ────────────────────────────────────────────────
APP_VERSION = "4.6.0"
APP_TITLE = "AtlasPI"
APP_DESCRIPTION = "Database geografico storico strutturato per agenti AI"

# ─── Database ────────────────────────────────────────────────────
# Supporto duale: SQLite (dev) / PostgreSQL+PostGIS (prod)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATA_DIR / 'atlaspi.db'}",
)

# ─── Server ──────────────────────────────────────────────────────
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "10100"))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"

# ─── CORS ────────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ─── Logging ─────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # "json" o "text"

# ─── Rate limiting ───────────────────────────────────────────────
RATE_LIMIT = os.getenv("RATE_LIMIT", "60/minute")

# ─── Seed ────────────────────────────────────────────────────────
AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() == "true"
