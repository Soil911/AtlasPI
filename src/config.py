"""Configurazione centralizzata di AtlasPI con supporto .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ─── Ambiente ────────────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")

# ─── Applicazione ────────────────────────────────────────────────
APP_VERSION = "6.11.0"
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

# ─── Sicurezza rete ─────────────────────────────────────────────
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]
TRUSTED_PROXIES = [
    p.strip()
    for p in os.getenv("TRUSTED_PROXIES", "127.0.0.1").split(",")
    if p.strip()
]

# ─── CORS ────────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ─── Logging ─────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # "json" o "text"

# ─── Rate limiting ───────────────────────────────────────────────
RATE_LIMIT = os.getenv("RATE_LIMIT", "60/minute")

# ─── Seed ────────────────────────────────────────────────────────
AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() == "true"

# ─── Observability: Sentry ───────────────────────────────────────
# Vuoto in sviluppo (nessun invio). In produzione impostare DSN reale
# via env var SENTRY_DSN. Sample rate di default basso per risparmiare quota.
SENTRY_DSN = os.getenv("SENTRY_DSN", "").strip()
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", ENVIRONMENT)
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
SENTRY_PROFILES_SAMPLE_RATE = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0"))
SENTRY_RELEASE = os.getenv("SENTRY_RELEASE", f"atlaspi@{APP_VERSION}")

# ─── Observability: Uptime / misc ───────────────────────────────
# Timestamp di avvio del processo per calcolare uptime in /health.
import time as _time  # noqa: E402 (import localizzato per evitare dipendenze al top)
PROCESS_START_TIME = _time.time()

# URL pubblico canonico del servizio (usato in sitemap.xml, OG tags, docs).
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://atlaspi.cra-srl.com")
