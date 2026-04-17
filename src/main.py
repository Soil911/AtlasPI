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
from src.api.routes import admin_cache, admin_cofounder, admin_insights, analytics, chains, cities_routes, compare, docs_ui, entities, events, export, health, periods, relations, search, snapshot, timeline, widgets
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
from src.db.seed import seed_database, seed_events_database, seed_periods_database, sync_new_periods
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

    # Redis cache (graceful: no-op if REDIS_URL not set or unreachable).
    from src.cache import init_redis
    init_redis()

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
        # v6.31: ensure aourednik raw data is available (clone if missing)
        try:
            from src.ingestion.ensure_aourednik_data import ensure_aourednik
            ensure_aourednik()
        except Exception:
            logger.warning("aourednik fetch failed — boundary enrichment limited", exc_info=True)

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
        # v6.27: seed historical periods (independent from entities/events)
        # v6.29: always run sync after seed so new batch files land in prod.
        try:
            seed_periods_database()
            sync_result = sync_new_periods()
            if sync_result.get("inserted", 0) > 0:
                logger.info("Periods sync: %d new periods added", sync_result["inserted"])
        except Exception:
            logger.warning("Seed/sync periods fallito — v6.27 periods layer non disponibile", exc_info=True)
        # v6.31: sync dynasty chains from data/chains/ (idempotent, dedup by name)
        try:
            from src.ingestion.ingest_chains import ingest_chains
            chain_result = ingest_chains()
            if chain_result.get("inserted", 0) > 0:
                logger.info(
                    "Chains sync: %d new chains, %d total links",
                    chain_result["inserted"],
                    chain_result.get("total_links_created", 0),
                )
        except Exception:
            logger.warning("Sync chains fallito", exc_info=True)
        # v6.30: guard against displaced aourednik fuzzy matches (ETHICS-006)
        # Runs every startup; idempotent (only fixes entities with >3000km displacement).
        try:
            from src.ingestion.fix_displaced_aourednik import fix_displaced
            disp_stats = fix_displaced(dry_run=False)
            if disp_stats.get("fixed", 0) > 0:
                logger.warning(
                    "Displaced aourednik rollback: fixed %d entities (threshold 3000km)",
                    disp_stats["fixed"],
                )
        except Exception:
            logger.warning("Displacement guard fallito", exc_info=True)
        # v6.31: guard against antimeridian-crossing and wrong-polygon inheritors
        # (Alaska wraps +180 causing USA label in France; tribes inheriting full
        # USA polygon; USSR getting modern Russia polygon; Fiji/NZ antimeridian)
        try:
            from src.ingestion.fix_antimeridian_and_wrong_polygons import fix_all
            am_stats = fix_all(dry_run=False)
            total_fixed = am_stats.get("wrong_polygon_fixed", 0) + am_stats.get("antimeridian_clipped", 0)
            if total_fixed > 0:
                logger.warning(
                    "Antimeridian/wrong-polygon fix: %d wrong-polygon resets + %d antimeridian clips",
                    am_stats["wrong_polygon_fixed"],
                    am_stats["antimeridian_clipped"],
                )
        except Exception:
            logger.warning("Antimeridian guard fallito", exc_info=True)

    logger.info("AtlasPI pronto")
    yield


OPENAPI_DESCRIPTION = """
# AtlasPI — Historical Geography API for AI Agents

**The first REST API and MCP server for structured historical geography.**
Free, public, Apache 2.0 licensed. No login. No API key. No registration.

## What AtlasPI is

A structured historical-geographic database designed specifically for AI agents,
researchers, and digital-humanities developers. Every record carries:

- **Real boundaries** (GeoJSON polygons/multipolygons from Natural Earth,
  aourednik/historical-basemaps, and curated academic maps — not placeholders)
- **Academic sources** (2,400+ bibliographic citations)
- **Confidence scores** (0.0–1.0 per entity/event)
- **Explicit ethical framings** (conquests labeled as CONQUEST not "succession";
  contested names preserved; colonial renamings documented)
- **Native-language primary names** (Mēxihcah not "Aztec"; Tawantinsuyu not
  "Inca"; 漢朝 not "Han Dynasty")

## What's in the dataset (live)

| Resource | Count | Endpoint |
|---|---|---|
| Historical entities | **862** | `/v1/entities` |
| Historical events | **490** | `/v1/events` |
| Historical periods | **48** | `/v1/periods` |
| Historical cities | **110** | `/v1/cities` |
| Trade routes | **41** | `/v1/routes` |
| Dynasty chains | **94** | `/v1/chains` |
| Sources | **2,400+** | (embedded) |

**Temporal range**: 4500 BCE → 2024 CE.
**Geographic range**: all inhabited continents (Europe 17%, Asia 31%, Africa 18%,
Americas 17%, Middle East 11%, Oceania 2%).

## Why this API exists

Existing geo datasets (Natural Earth, OSM, Wikidata) are either modern-only,
unstructured, or poorly cross-linked. AI agents need:
1. Semantic queries — not just SPARQL
2. Contextualized answers — e.g., "what was happening in 1250 globally" in
   one call (`/v1/snapshot/year/1250`)
3. Cross-referenced entities — e.g., "which periods did Imperium Romanum
   overlap with?" (`/v1/entities/{id}/periods`)
4. Ethical framings — e.g., "Aztec Imperial Period" is labeled
   region=americas, with historiographic_note on Spanish conquest

AtlasPI provides all of this in a uniform REST API.

## Quick Start

**Python:**
```python
import requests
BASE = "https://atlaspi.cra-srl.com"

# Discover entities existing in 1500 CE
r = requests.get(f"{BASE}/v1/entities", params={"year": 1500, "limit": 20})

# Single-call world snapshot
r = requests.get(f"{BASE}/v1/snapshot/year/1250")
print(r.json()["periods"]["items"])  # periods active in 1250, by region

# Events on a specific date
r = requests.get(f"{BASE}/v1/events/on-this-day/07-14")  # Bastille Day

# Find similar entities by weighted algorithm
r = requests.get(f"{BASE}/v1/entities/1/similar?limit=10")

# Cross-resource period linkage
r = requests.get(f"{BASE}/v1/entities/1/periods")  # Imperium Romanum periods
```

**curl:**
```bash
curl -s https://atlaspi.cra-srl.com/v1/snapshot/year/1492 | jq .periods
curl -s https://atlaspi.cra-srl.com/v1/entities/1/similar | jq '.similar[0]'
curl -s https://atlaspi.cra-srl.com/v1/periods/by-slug/bronze-age
curl -s "https://atlaspi.cra-srl.com/v1/events?year=1453"
```

## Key endpoint categories

- **Discovery**: `/v1/entities`, `/v1/events`, `/v1/periods`, `/v1/chains`
- **Detail**: `/v1/entities/{id}`, `/v1/events/{id}`, `/v1/periods/by-slug/{slug}`
- **Cross-resource**: `/v1/entities/{id}/periods`, `/v1/events/{id}/periods`,
  `/v1/entities/{id}/predecessors`, `/v1/entities/{id}/successors`
- **Temporal**: `/v1/snapshot/year/{year}`, `/v1/periods/at-year/{year}`,
  `/v1/events/on-this-day/{mm-dd}`, `/v1/events/at-date/{iso-date}`
- **Spatial**: `/v1/nearby`, `/v1/entities?bbox=...`
- **Semantic**: `/v1/entities/{id}/similar`, `/v1/search/advanced`, `/v1/compare/{id1}/{id2}`
- **Export**: `/v1/export/geojson`, `/v1/export/csv`, `/v1/export/timeline`

## Also available

- **MCP Server** (34 tools, v0.7.0): [github.com/Soil911/AtlasPI](https://github.com/Soil911/AtlasPI/tree/main/mcp-server) — plug directly into Claude Desktop, Claude Code, or any MCP client
- **OpenAPI spec**: `/openapi.json` — machine-readable schema
- **Swagger UI**: `/docs` — interactive documentation
- **LLMs.txt**: `/llms.txt` — AI-agent-friendly site map
- **Plugin manifest**: `/.well-known/ai-plugin.json` — OpenAI plugin spec

## Ethics (ETHICS-001 → ETHICS-010)

- Native-language primary names (ETHICS-001)
- Explicit conquest/violence labeling (ETHICS-002)
- Contested territories with all versions (ETHICS-003)
- Boundary provenance transparent (ETHICS-005)
- Geographic guard against fuzzy-match displacement (ETHICS-006)
- Academic event terminology (GENOCIDE, COLONIAL_VIOLENCE) — no euphemisms (ETHICS-007)
- Known-silence fields for events with suppressed documentation (ETHICS-008)
- Colonial renamings documented, not hidden (ETHICS-009)
- Slavery-involved trade routes flagged (ETHICS-010)

## Data sources

- **Natural Earth** (public domain): ne_110m_admin_0_countries
- **aourednik/historical-basemaps** (CC BY 4.0): 54 period snapshots 4500 BCE → 2025
- **Academic citations**: Cambridge Histories, Oxford Handbooks, regional specialists

## License

**Apache License 2.0** — free for commercial and non-commercial use.
Full source: [github.com/Soil911/AtlasPI](https://github.com/Soil911/AtlasPI)
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
app.include_router(periods.router)
app.include_router(snapshot.router)
app.include_router(analytics.router)
app.include_router(admin_insights.router)
app.include_router(admin_cache.router)
app.include_router(admin_cofounder.router)
app.include_router(timeline.router)
app.include_router(compare.router)
app.include_router(search.router)
app.include_router(docs_ui.router)
app.include_router(widgets.router)


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


@app.get("/llms.txt", include_in_schema=False)
async def serve_llms_txt():
    """LLMs.txt — emerging standard for AI agent site discovery.

    Provides an AI-agent-readable description of all endpoints, their purposes,
    and the data model. Consumed by Claude, GPT, Perplexity, and others.
    """
    return FileResponse(
        STATIC_DIR / "llms.txt",
        media_type="text/plain; charset=utf-8",
    )


@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def serve_ai_plugin():
    """OpenAI plugin manifest — plug directly into ChatGPT-compatible platforms."""
    return FileResponse(
        STATIC_DIR / ".well-known" / "ai-plugin.json",
        media_type="application/json",
    )


@app.get("/.well-known/mcp.json", include_in_schema=False)
async def serve_mcp_manifest():
    """MCP server discovery manifest."""
    return FileResponse(
        STATIC_DIR / ".well-known" / "mcp.json",
        media_type="application/json",
    )


@app.get("/about", include_in_schema=False)
async def serve_about():
    """Public about page — what AtlasPI is, for humans and search engines."""
    return FileResponse(STATIC_DIR / "about.html", media_type="text/html")


@app.get("/faq", include_in_schema=False)
async def serve_faq():
    """Public FAQ page with JSON-LD FAQPage schema for rich search results."""
    return FileResponse(STATIC_DIR / "faq.html", media_type="text/html")


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
