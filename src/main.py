"""AtlasPI — Database geografico storico strutturato per agenti AI."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.errors import register_error_handlers
from src.api.routes import entities, export, health, relations
from src.config import (
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    AUTO_SEED,
    CORS_ORIGINS,
    RATE_LIMIT,
)
from src.db.database import Base, engine
from src.db.seed import seed_database
from src.logging_config import setup_logging
from src.middleware.request_logging import RequestLoggingMiddleware
from src.middleware.security import SecurityHeadersMiddleware

# Logging prima di tutto
setup_logging()
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea tabelle e popola dati demo all'avvio."""
    logger.info("Inizializzazione AtlasPI v%s...", APP_VERSION)

    Base.metadata.create_all(bind=engine)

    if AUTO_SEED:
        seed_database()
        try:
            from src.ingestion.update_boundaries import update_all_boundaries
            update_all_boundaries()
        except Exception:
            logger.warning("Aggiornamento confini fallito — i dati demo avranno confini approssimativi", exc_info=True)

    logger.info("AtlasPI pronto")
    yield


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Middleware (ordine: ultimo aggiunto = primo eseguito) ────────

# GZip compression (min 500 bytes)
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Error handling
register_error_handlers(app)

# ─── Routes ──────────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(entities.router)
app.include_router(export.router)
app.include_router(relations.router)


@app.get("/", include_in_schema=False)
async def serve_ui():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
