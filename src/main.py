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


@app.get("/embed", include_in_schema=False)
async def serve_embed():
    """Serve la versione embed (UI minimale per iframe)."""
    return FileResponse(STATIC_DIR / "embed.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
