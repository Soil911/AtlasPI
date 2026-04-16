"""AtlasPI — Database geografico storico strutturato per agenti AI."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.api.errors import register_error_handlers
from src.api.middleware import (
    RateLimitMiddleware,  # noqa: F401 — disponibile per uso futuro
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from src.api.routes import admin_cofounder, admin_insights, analytics, chains, cities_routes, compare, docs_ui, entities, events, export, health, relations, search, timeline
from src.config import (
    APP_TITLE,
    APP_VERSION,
    CORS_ORIGINS,
    ENVIRONMENT,
    HOST,
    PORT,
    RATE_LIMIT,
)
from src.db.database import Base, engine
from src.db.seed import seed_database, seed_events_database
from src.logging_config import setup_logging
from src.monitoring import init_sentry

# Logging prima di tutto (Sentry si aggancia poi al logger root)
setup_logging()
# Sentry init prima dell'app: cosi' cattura anche errori di startup
init_sentry()
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])


def _run_alembic_migrations():
    """Esegui migrazioni Alembic (solo per PostgreSQL in produzione).

    Per SQLite in sviluppo, usa create_all() che e' piu' semplice e veloce.
    Per PostgreSQL, le migrazioni Alembic garantiscono upgrade incrementali sicuri.
    """
    try:
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrazioni Alembic applicate con successo")
    except Exception:
        logger.error("Errore durante le migrazioni Alembic", exc_info=True)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea tabelle e popola dati demo all'avvio."""
    from src.config import AUTO_SEED
    from src.db.database import is_postgres, is_sqlite

    logger.info("Inizializzazione AtlasPI v%s [%s]...", APP_VERSION, ENVIRONMENT)

    if is_sqlite:
        # Dev: crea tabelle direttamente dal metadata dei modelli
        Base.metadata.create_all(bind=engine)
        logger.info("SQLite: tabelle create/verificate con create_all()")
    elif is_postgres:
        # Prod: usa migrazioni Alembic per upgrade incrementali sicuri
        _run_alembic_migrations()
    else:
        # Fallback per database non riconosciuti
        Base.metadata.create_all(bind=engine)
        logger.warning("Database non riconosciuto: tabelle create con create_all()")

    if AUTO_SEED:
        seed_database()
        try:
            from src.ingestion.update_boundaries import update_all_boundaries
            update_all_boundaries()
        except Exception:
            logger.warning("Aggiornamento confini fallito — i dati demo avranno confini approssimativi", exc_info=True)
        # v6.3: seed eventi storici (separato dal seed entità — l'uno può
        # esistere senza l'altro, per dev locale senza dataset eventi)
        try:
            seed_events_database()
        except Exception:
            logger.warning("Seed eventi fallito — v6.3 events layer non disponibile", exc_info=True)

    logger.info("AtlasPI pronto")
    yield


OPENAPI_DESCRIPTION = """
# AtlasPI — Database Geografico Storico per Agenti AI

**500+ entita' storiche** su 9 regioni, da 4500 a.C. al 2024.
Confini reali da fonti accademiche, governance etica documentata.

## Quick Start

```python
import requests

# Cerca entita' per anno
r = requests.get("http://localhost:10100/v1/entity?year=1500")
entities = r.json()["entities"]

# Snapshot del mondo in un anno
r = requests.get("http://localhost:10100/v1/snapshot/1500")
world = r.json()  # count, summary per tipo/continente, entities

# Entita' vicine a coordinate
r = requests.get("http://localhost:10100/v1/nearby?lat=41.9&lon=12.5&year=100")
nearby = r.json()

# Confronta due entita'
r = requests.get("http://localhost:10100/v1/compare/1/2")
comparison = r.json()
```

```javascript
// JavaScript/Node.js
const res = await fetch('http://localhost:10100/v1/snapshot/1500');
const { entities, summary } = await res.json();
```

```bash
# curl
curl -s http://localhost:10100/v1/nearby?lat=30\\&lon=31\\&year=-300 | jq .
curl -s http://localhost:10100/v1/snapshot/1500?type=empire | jq .summary
curl -s http://localhost:10100/v1/random | jq .name_original
```

## Principi Etici
- **ETHICS-001**: Nomi originali/locali come dato primario
- **ETHICS-002**: Conquiste e violenze documentate esplicitamente
- **ETHICS-003**: Territori contestati con tutte le versioni

## Fonti
- Natural Earth (ne_110m_admin_0_countries)
- aourednik/historical-basemaps (7 periodi: 100-1900)
"""

app = FastAPI(
    title=APP_TITLE,
    description=OPENAPI_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "entit\u00e0", "description": "CRUD e ricerca entit\u00e0 geopolitiche storiche"},
        {"name": "relazioni", "description": "Contemporanei, correlazioni e confronto tra entit\u00e0"},
        {"name": "esportazione", "description": "Export GeoJSON, CSV e Timeline"},
        {"name": "sistema", "description": "Health check e diagnostica"},
    ],
)

# ─── Middleware (ordine: ultimo aggiunto = primo eseguito) ────────

# GZip compression (min 500 bytes)
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS — legge origini da configurazione, supporta domini di produzione
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Security headers (include X-Process-Time)
app.add_middleware(SecurityHeadersMiddleware)

# Request logging (include X-Request-ID) + analytics DB write (v6.12)
app.add_middleware(RequestLoggingMiddleware)

# Rate limiting (slowapi) — middleware applica i default_limits globali
# senza bisogno di decorator @limiter.limit() su ogni endpoint.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Error handling
register_error_handlers(app)

# ─── Routes ──────────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(entities.router)
app.include_router(export.router)
app.include_router(relations.router)
app.include_router(events.router)
app.include_router(cities_routes.router)
app.include_router(chains.router)
app.include_router(analytics.router)
app.include_router(admin_insights.router)
app.include_router(admin_cofounder.router)
app.include_router(timeline.router)
app.include_router(compare.router)
app.include_router(search.router)
app.include_router(docs_ui.router)


@app.get("/", include_in_schema=False)
async def serve_landing():
    """Landing page inglese (target: developer / agent AI). Migliora SEO e conversione."""
    landing = STATIC_DIR / "landing" / "index.html"
    if landing.exists():
        return FileResponse(landing)
    # Fallback: se la landing non e' deployata, serve la mappa
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/app", include_in_schema=False)
async def serve_app():
    """Mappa interattiva italiana (l'app vera e propria)."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/embed", include_in_schema=False)
async def serve_embed():
    """Serve la versione embed (UI minimale per iframe)."""
    return FileResponse(STATIC_DIR / "embed.html")


@app.get("/robots.txt", include_in_schema=False)
async def serve_robots():
    """Directive per crawler SEO."""
    return FileResponse(
        STATIC_DIR / "robots.txt",
        media_type="text/plain",
    )


@app.get("/sitemap.xml", include_in_schema=False)
async def serve_sitemap():
    """Sitemap XML con le route indicizzabili."""
    return FileResponse(
        STATIC_DIR / "sitemap.xml",
        media_type="application/xml",
    )


@app.get("/v1/openapi.json", include_in_schema=False)
async def openapi_override():
    """Override OpenAPI spec con server URL per produzione."""
    schema = app.openapi()
    # In produzione, aggiungi il server URL reale
    if ENVIRONMENT != "development":
        schema["servers"] = [
            {"url": f"https://{HOST}:{PORT}" if PORT != 443 else f"https://{HOST}",
             "description": f"AtlasPI {ENVIRONMENT}"},
        ]
    else:
        schema["servers"] = [
            {"url": f"http://{HOST}:{PORT}", "description": "AtlasPI development"},
        ]
    return JSONResponse(content=schema)


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
