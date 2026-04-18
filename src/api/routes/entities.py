"""Endpoint per le entità geopolitiche — vedi ADR-002.

GET /v1/entity?name=...&year=...&status=...&type=...&sort=...  query principale
GET /v1/entities?limit=...&offset=...                           elenco paginato
GET /v1/entities/{id}                                           dettaglio entità
GET /v1/search?q=...                                            autocomplete
GET /v1/types                                                   tipi disponibili
GET /v1/stats                                                   statistiche dataset
GET /v1/continents                                              continenti disponibili
GET /v1/where-was?lat=...&lon=...&year=...                      reverse-geocoding temporale (v6.34)
"""

import json
import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel
from shapely.geometry import Point, shape as shapely_shape
from shapely.errors import GEOSException
from sqlalchemy import and_, desc, func, or_, select, text
from sqlalchemy.orm import Session, joinedload

from src.api.errors import EntityNotFoundError
from src.cache import cache_response
from src.api.schemas import (
    CapitalResponse,
    EntityResponse,
    PaginatedEntityResponse,
)
from src.db.database import get_db, is_postgres
from src.db.models import GeoEntity, HistoricalEvent, NameVariant, Source, TerritoryChange

logger = logging.getLogger(__name__)

router = APIRouter(tags=["entità"])

# Tipi per validazione
StatusFilter = Literal["confirmed", "uncertain", "disputed"] | None
SortField = Literal["name", "year_start", "confidence", "year_end"] | None


# ─── Continente da coordinate ────────────────────────────────────

def _get_continent(lat: float | None, lon: float | None) -> str:
    """Determina il continente dalla posizione della capitale.

    ETHICS: il mapping è un'approssimazione geografica, non una
    dichiarazione politica. Le entità trans-continentali (es. Impero
    Romano, Ottomano) vengono assegnate al continente della capitale.
    """
    if lat is None or lon is None:
        return "Unknown"

    # Middle East special case (politicamente Asia ma spesso trattato a parte)
    if 25 <= lat <= 42 and 25 <= lon <= 50:
        return "Middle East"

    # Africa
    if lat < 37 and -20 <= lon <= 55 and lat < (37 - (lon - 10) * 0.05 if lon > 10 else 37):
        if lat < 35:
            return "Africa"

    # Europe
    if 35 <= lat <= 72 and -25 <= lon <= 40:
        return "Europe"

    # Asia (including Far East, Central, South, Southeast)
    if -15 <= lat <= 75 and 40 <= lon <= 180:
        return "Asia"

    # North America
    if 7 <= lat <= 85 and -170 <= lon <= -50:
        return "Americas"

    # South America
    if -60 <= lat <= 15 and -85 <= lon <= -30:
        return "Americas"

    # Oceania
    if -50 <= lat <= 0 and 100 <= lon <= 180:
        return "Oceania"

    # Africa fallback
    if -40 <= lat <= 37 and -20 <= lon <= 55:
        return "Africa"

    return "Other"


# ─── Schema aggiuntivi ──────────────────────────────────────────

class SearchResult(BaseModel):
    id: int
    name_original: str
    name_original_lang: str
    entity_type: str
    year_start: int
    year_end: int | None
    status: str
    confidence_score: float
    continent: str | None = None


class SearchResponse(BaseModel):
    count: int
    results: list[SearchResult]


class TypeInfo(BaseModel):
    type: str
    count: int


class ContinentInfo(BaseModel):
    continent: str
    count: int


class EventStatsInfo(BaseModel):
    """Statistiche aggregate eventi storici."""
    total_events: int
    events_with_day: int
    events_with_month: int
    date_coverage_unique_days: int
    date_coverage_pct: float
    date_precision_breakdown: dict[str, int]


class StatsResponse(BaseModel):
    total_entities: int
    types: list[TypeInfo]
    status_counts: dict[str, int]
    year_range: dict[str, int]
    avg_confidence: float
    total_sources: int
    total_territory_changes: int
    disputed_count: int
    continents: list[ContinentInfo] = []
    events: EventStatsInfo | None = None


# ─── Conversione ─────────────────────────────────────────────────

def _entity_to_response(entity: GeoEntity) -> EntityResponse:
    """Converte un record ORM in risposta API."""
    capital = None
    if entity.capital_name and entity.capital_lat is not None:
        capital = CapitalResponse(
            name=entity.capital_name,
            lat=entity.capital_lat,
            lon=entity.capital_lon,
        )

    geojson = None
    if entity.boundary_geojson:
        try:
            geojson = json.loads(entity.boundary_geojson)
        except (json.JSONDecodeError, TypeError):
            logger.warning("GeoJSON malformato per entità %d", entity.id)

    continent = _get_continent(entity.capital_lat, entity.capital_lon)

    return EntityResponse(
        id=entity.id,
        entity_type=entity.entity_type,
        year_start=entity.year_start,
        year_end=entity.year_end,
        name_original=entity.name_original,
        name_original_lang=entity.name_original_lang,
        name_variants=entity.name_variants,
        capital=capital,
        boundary_geojson=geojson,
        # ETHICS-005: provenance tracking fields.
        boundary_source=entity.boundary_source,
        boundary_aourednik_name=entity.boundary_aourednik_name,
        boundary_aourednik_year=entity.boundary_aourednik_year,
        boundary_aourednik_precision=entity.boundary_aourednik_precision,
        boundary_ne_iso_a3=entity.boundary_ne_iso_a3,
        confidence_score=entity.confidence_score,
        status=entity.status,
        territory_changes=entity.territory_changes,
        sources=entity.sources,
        ethical_notes=entity.ethical_notes,
        continent=continent,
    )


def _eager_query(db: Session):
    return db.query(GeoEntity).options(
        joinedload(GeoEntity.name_variants),
        joinedload(GeoEntity.territory_changes),
        joinedload(GeoEntity.sources),
    )


def _apply_sort(q, sort: SortField, order: str = "asc"):
    """Applica ordinamento alla query."""
    if not sort:
        return q
    col_map = {
        "name": GeoEntity.name_original,
        "year_start": GeoEntity.year_start,
        "year_end": GeoEntity.year_end,
        "confidence": GeoEntity.confidence_score,
    }
    col = col_map.get(sort, GeoEntity.name_original)
    return q.order_by(desc(col) if order == "desc" else col)


def _parse_bbox(bbox: str | None) -> tuple[float, float, float, float] | None:
    """Parse bbox string 'min_lon,min_lat,max_lon,max_lat' into a tuple.

    Convenzione standard (Mapbox/OpenStreetMap/GeoJSON RFC 7946):
    `min_lon, min_lat, max_lon, max_lat` (longitudine prima!).

    Raises HTTPException 422 se il formato è invalido o le coordinate
    sono fuori range geografico.
    """
    if not bbox:
        return None
    try:
        parts = [float(x.strip()) for x in bbox.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="bbox deve essere 'min_lon,min_lat,max_lon,max_lat' (4 float separati da virgola)",
        )
    if len(parts) != 4:
        raise HTTPException(
            status_code=422,
            detail=f"bbox richiede esattamente 4 valori, ricevuti {len(parts)}",
        )
    min_lon, min_lat, max_lon, max_lat = parts
    if not (-180.0 <= min_lon <= 180.0 and -180.0 <= max_lon <= 180.0):
        raise HTTPException(status_code=422, detail="Longitudine fuori range [-180, 180]")
    if not (-90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0):
        raise HTTPException(status_code=422, detail="Latitudine fuori range [-90, 90]")
    if min_lon > max_lon or min_lat > max_lat:
        raise HTTPException(
            status_code=422,
            detail="bbox: min_lon/min_lat devono essere <= max_lon/max_lat",
        )
    return (min_lon, min_lat, max_lon, max_lat)


def _apply_bbox_filter(q, bbox: str | None):
    """Filtra entità per bounding box geografico.

    PostgreSQL+PostGIS (prod):
        ST_Intersects(ST_GeomFromGeoJSON(boundary_geojson), bbox_envelope)
        OR fallback al capital-point se l'entità non ha boundary_geojson.
        Sfrutta l'indice GiST `ix_geo_entities_boundary_geom` se presente.

    SQLite (dev):
        Filtro approssimato sul solo capital-point (lat/lon BETWEEN bbox).
        Più rapido del calcolo Shapely su tutte le righe; perde le entità
        con boundary che intersecano il bbox ma con capitale fuori. Usare
        Postgres locale per accuratezza piena in dev.

    Args:
        q: SQLAlchemy query su GeoEntity.
        bbox: stringa "min_lon,min_lat,max_lon,max_lat" oppure None.

    Returns:
        Query filtrata (no-op se bbox è None).
    """
    parsed = _parse_bbox(bbox)
    if parsed is None:
        return q
    min_lon, min_lat, max_lon, max_lat = parsed

    if is_postgres:
        # PostGIS: spatial intersection sull'envelope. SRID 4326 = WGS84.
        # OR sul capitale per entità prive di boundary_geojson.
        envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
        return q.filter(
            or_(
                and_(
                    GeoEntity.boundary_geojson.isnot(None),
                    func.ST_Intersects(
                        func.ST_GeomFromGeoJSON(GeoEntity.boundary_geojson),
                        envelope,
                    ),
                ),
                and_(
                    GeoEntity.boundary_geojson.is_(None),
                    GeoEntity.capital_lat.between(min_lat, max_lat),
                    GeoEntity.capital_lon.between(min_lon, max_lon),
                ),
            )
        )

    # SQLite fallback: solo capital-point.
    return q.filter(
        GeoEntity.capital_lat.isnot(None),
        GeoEntity.capital_lon.isnot(None),
        GeoEntity.capital_lat.between(min_lat, max_lat),
        GeoEntity.capital_lon.between(min_lon, max_lon),
    )


# ─── Endpoints ───────────────────────────────────────────────────

@router.get(
    "/v1/entity",
    response_model=PaginatedEntityResponse,
    summary="Cerca entità per nome, anno, status e tipo",
    description=(
        "Endpoint principale (ADR-002). Cerca per nome (anche varianti), "
        "filtra per anno, status e tipo. Supporta ordinamento."
    ),
)
def query_entity(
    response: Response,
    name: str | None = Query(None, max_length=200, description="Nome (parziale) dell'entità"),
    year: int | None = Query(None, ge=-4000, le=2100, description="Anno di riferimento (negativo = a.C.)"),
    status: StatusFilter = Query(None, description="Filtra per status"),
    type: str | None = Query(None, max_length=50, description="Filtra per entity_type (empire, kingdom, city, etc.)"),
    continent: str | None = Query(None, max_length=50, description="Filtra per continente (Europe, Asia, Africa, Americas, Middle East, Oceania)"),
    bbox: str | None = Query(
        None,
        max_length=80,
        description=(
            "Bounding box geografico 'min_lon,min_lat,max_lon,max_lat' (RFC 7946). "
            "Restituisce entità il cui boundary_geojson interseca il bbox; per entità "
            "senza boundary, fallback alla capitale dentro il bbox. PostGIS in prod, "
            "approssimato in dev SQLite."
        ),
    ),
    sort: SortField = Query(None, description="Ordina per: name, year_start, confidence, year_end"),
    order: Literal["asc", "desc"] = Query("asc", description="Direzione ordinamento"),
    limit: int = Query(20, ge=1, le=100, description="Risultati per pagina"),
    offset: int = Query(0, ge=0, description="Offset per paginazione"),
    db: Session = Depends(get_db),
):
    q = _eager_query(db)

    if name:
        pattern = f"%{name}%"
        variant_ids = select(NameVariant.entity_id).where(NameVariant.name.ilike(pattern))
        q = q.filter(
            or_(
                GeoEntity.name_original.ilike(pattern),
                GeoEntity.id.in_(variant_ids),
            )
        )

    if year is not None:
        q = q.filter(GeoEntity.year_start <= year)
        q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))

    if status:
        q = q.filter(GeoEntity.status == status)

    if type:
        q = q.filter(GeoEntity.entity_type == type)

    # bbox filter (PostGIS ST_Intersects in prod, capital-point in SQLite)
    q = _apply_bbox_filter(q, bbox)

    total = q.count()
    q = _apply_sort(q, sort, order)
    results = q.offset(offset).limit(limit).all()
    entities = [_entity_to_response(e) for e in results]

    # Filtra per continente post-query (calcolato da coordinate)
    if continent:
        entities = [e for e in entities if e.continent and e.continent.lower() == continent.lower()]
        total = len(entities)

    response.headers["Cache-Control"] = "public, max-age=3600"
    return PaginatedEntityResponse(count=total, limit=limit, offset=offset, entities=entities)


@router.get(
    "/v1/entities",
    response_model=PaginatedEntityResponse,
    summary="List all historical entities (paginated)",
    description=(
        "Primary discovery endpoint for AtlasPI's 862 historical geopolitical "
        "entities. Returns empires, kingdoms, sultanates, republics, chiefdoms, "
        "confederations, dynasties, caliphates, and more — spanning 4500 BCE to "
        "2024 across all inhabited continents.\n\n"
        "**Filters** (all optional, combinable):\n"
        "- `year` — entities existing in this specific year\n"
        "- `status` — confirmed / uncertain / disputed\n"
        "- `entity_type` — empire, kingdom, sultanate, etc.\n"
        "- `continent` — Europe, Asia, Africa, Americas, Middle East, Oceania\n"
        "- `bbox` — spatial bounding box (minLon,minLat,maxLon,maxLat)\n"
        "- `search` — fuzzy match on name_original and name_variants\n\n"
        "**For AI agents**: use this as the entry point to discover entities, "
        "then follow `/v1/entities/{id}/periods`, `/successors`, `/predecessors`, "
        "`/similar`, `/events` for rich contextualization.\n\n"
        "**Free public API — no authentication required.**"
    ),
)
@cache_response(ttl_seconds=300)
def list_entities(
    request: Request,
    response: Response,
    bbox: str | None = Query(
        None,
        max_length=80,
        description="Bounding box 'min_lon,min_lat,max_lon,max_lat' (vedi /v1/entity).",
    ),
    sort: SortField = Query(None, description="Ordina per: name, year_start, confidence, year_end"),
    order: Literal["asc", "desc"] = Query("asc", description="Direzione ordinamento"),
    limit: int = Query(20, ge=1, le=100, description="Risultati per pagina"),
    offset: int = Query(0, ge=0, description="Offset"),
    db: Session = Depends(get_db),
):
    q = _eager_query(db)
    q = _apply_bbox_filter(q, bbox)
    # Direct count avoids subquery wrapping from joinedload, ~10x faster
    count_q = _apply_bbox_filter(db.query(func.count(GeoEntity.id)), bbox)
    total = count_q.scalar() or 0
    q = _apply_sort(q, sort, order)
    results = q.offset(offset).limit(limit).all()
    entities = [_entity_to_response(e) for e in results]

    response.headers["Cache-Control"] = "public, max-age=3600"
    return PaginatedEntityResponse(count=total, limit=limit, offset=offset, entities=entities)


@router.get(
    "/v1/entities/light",
    summary="List ALL entities without boundary_geojson — optimized for map viewport",
    description=(
        "Returns all historical entities with ONLY lightweight fields (id, "
        "name_original, entity_type, year range, capital coords, confidence, "
        "status). Excludes `boundary_geojson` which is the dominant payload "
        "driver. Single call returns ~1000 entities in ~200KB vs ~2MB+ "
        "from paginated `/v1/entities` (9 calls, ~17MB).\n\n"
        "**Primary use case**: frontend map bootstrap. Client loads ALL "
        "entities at once, filters client-side by year/type/continent. On "
        "click, frontend calls `/v1/entities/{id}` for full detail + "
        "boundary polygon.\n\n"
        "**Query params**:\n"
        "- `year` (optional): filter entities active in this year\n"
        "- `bbox` (optional): filter by capital-point-in-bbox (no polygon intersect here)\n\n"
        "**For AI agents**: use this first for 'give me an overview of all X', "
        "then fetch full detail on specific IDs as needed."
    ),
)
@cache_response(ttl_seconds=3600)
def list_entities_light(
    request: Request,
    response: Response,
    year: int | None = Query(None, ge=-5000, le=2100, description="Active in this year"),
    bbox: str | None = Query(None, max_length=80),
    db: Session = Depends(get_db),
):
    """Lightweight endpoint — no boundary_geojson in payload.

    Risolve il problema scalabilita' della home: 1033 entita' in
    ~200KB vs ~17MB della /v1/entities paginata.
    """
    # Select only needed cols.
    q = db.query(
        GeoEntity.id,
        GeoEntity.name_original,
        GeoEntity.name_original_lang,
        GeoEntity.entity_type,
        GeoEntity.year_start,
        GeoEntity.year_end,
        GeoEntity.capital_name,
        GeoEntity.capital_lat,
        GeoEntity.capital_lon,
        GeoEntity.confidence_score,
        GeoEntity.status,
    )

    if year is not None:
        q = q.filter(GeoEntity.year_start <= year)
        q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))

    # bbox: filter only by capital-point (lightweight — no polygon)
    parsed = _parse_bbox(bbox)
    if parsed is not None:
        min_lon, min_lat, max_lon, max_lat = parsed
        q = q.filter(
            GeoEntity.capital_lat.isnot(None),
            GeoEntity.capital_lon.isnot(None),
            GeoEntity.capital_lat.between(min_lat, max_lat),
            GeoEntity.capital_lon.between(min_lon, max_lon),
        )

    rows = q.all()
    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "count": len(rows),
        "entities": [
            {
                "id": r.id,
                "name_original": r.name_original,
                "name_original_lang": r.name_original_lang,
                "entity_type": r.entity_type,
                "year_start": r.year_start,
                "year_end": r.year_end,
                "capital_name": r.capital_name,
                "capital_lat": r.capital_lat,
                "capital_lon": r.capital_lon,
                "confidence_score": r.confidence_score,
                "status": r.status,
                "continent": _get_continent(r.capital_lat, r.capital_lon),
            }
            for r in rows
        ],
    }


@router.get(
    "/v1/entities/batch",
    summary="Fetch multiple entities by ID in a single request",
    description=(
        "Batch endpoint for AI agents: given a comma-separated list of entity IDs, "
        "returns all matching entities in a single round-trip. Reduces latency "
        "significantly when an agent needs to display a timeline, comparison table, "
        "or collection of related entities.\n\n"
        "**Usage**: `GET /v1/entities/batch?ids=1,2,3,4,5` (max 100 per call)\n\n"
        "**Response shape**:\n"
        "```json\n"
        "{\n"
        "  \"requested\": 5,\n"
        "  \"found\": 4,\n"
        "  \"not_found\": [999],\n"
        "  \"entities\": [ ... full detail for each ID ... ]\n"
        "}\n"
        "```\n\n"
        "**Example**: the MCP client calls this when a user asks 'compare these "
        "5 empires side-by-side'. One request instead of five, 5× faster."
    ),
)
@cache_response(ttl_seconds=3600)
def get_entities_batch(
    request: Request,
    response: Response,
    ids: str = Query(..., description="Comma-separated entity IDs (max 100)", examples=["1,2,3", "10,42,201,333"]),
    db: Session = Depends(get_db),
):
    """Return multiple entities by ID in a single round-trip."""
    # Parse IDs
    try:
        id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="ids must be a comma-separated list of integers, e.g. ?ids=1,2,3",
        )

    if not id_list:
        raise HTTPException(status_code=400, detail="ids parameter is empty")

    # Cap at 100 to prevent abuse
    if len(id_list) > 100:
        raise HTTPException(
            status_code=400,
            detail=f"Max 100 IDs per batch request; got {len(id_list)}. "
                   f"Split into multiple requests or use /v1/entities?limit=100",
        )

    # Deduplicate
    id_list = list(dict.fromkeys(id_list))

    # Fetch all in one query
    entities = _eager_query(db).filter(GeoEntity.id.in_(id_list)).all()
    found_ids = {e.id for e in entities}
    not_found = [i for i in id_list if i not in found_ids]

    # Build response maintaining requested order
    entity_map = {e.id: _entity_to_response(e) for e in entities}
    ordered = [entity_map[i] for i in id_list if i in entity_map]

    return {
        "requested": len(id_list),
        "found": len(entities),
        "not_found": not_found,
        "entities": ordered,
    }


@router.get(
    "/v1/entities/{entity_id}",
    response_model=EntityResponse,
    summary="Get detailed information for a single historical entity",
    description=(
        "Full detail view of a historical entity by its numeric ID. Returns:\n\n"
        "- **Core**: name_original (in native script), entity_type, year_start, "
        "year_end, capital name/lat/lon\n"
        "- **Geographic**: boundary_geojson (full polygon/multipolygon geometry), "
        "boundary_source (natural_earth / aourednik / historical_map / "
        "approximate_generated — provenance tier), boundary tracking fields\n"
        "- **Quality**: confidence_score (0.0-1.0), status (confirmed/uncertain/"
        "disputed)\n"
        "- **Names**: name_variants in multiple languages/scripts\n"
        "- **Sources**: full bibliographic citations (academic, primary, "
        "archaeological, etc.)\n"
        "- **Territory changes**: documented acquisitions/losses with dates, "
        "explicit change_type (CONQUEST, SUCCESSION, COLONIZATION, etc.)\n"
        "- **Ethical notes**: contested territories, colonial framings, "
        "alternative names\n\n"
        "For AI agents: after fetching an entity detail, chain requests to "
        "`/v1/entities/{id}/periods` (which historical epochs it existed in), "
        "`/v1/entities/{id}/events` (events involving this entity), "
        "`/v1/entities/{id}/similar` (top-N similar by confidence)."
    ),
)
@cache_response(ttl_seconds=3600)
def get_entity(entity_id: int, request: Request, response: Response, db: Session = Depends(get_db)):
    entity = _eager_query(db).filter(GeoEntity.id == entity_id).first()
    if not entity:
        raise EntityNotFoundError(entity_id)

    response.headers["Cache-Control"] = "public, max-age=3600"
    return _entity_to_response(entity)


@router.get(
    "/v1/search",
    response_model=SearchResponse,
    summary="Ricerca veloce per autocomplete",
    description="Restituisce risultati leggeri (senza GeoJSON) per ricerca rapida.",
)
def search_entities(
    q: str = Query(..., min_length=1, max_length=200, description="Testo da cercare"),
    limit: int = Query(10, ge=1, le=50, description="Max risultati"),
    db: Session = Depends(get_db),
):
    pattern = f"%{q}%"
    variant_ids = select(NameVariant.entity_id).where(NameVariant.name.ilike(pattern))
    results = (
        db.query(GeoEntity)
        .filter(or_(GeoEntity.name_original.ilike(pattern), GeoEntity.id.in_(variant_ids)))
        .limit(limit)
        .all()
    )

    return SearchResponse(
        count=len(results),
        results=[
            SearchResult(
                id=e.id,
                name_original=e.name_original,
                name_original_lang=e.name_original_lang,
                entity_type=e.entity_type,
                year_start=e.year_start,
                year_end=e.year_end,
                status=e.status,
                confidence_score=e.confidence_score,
            )
            for e in results
        ],
    )


@router.get(
    "/v1/search/fuzzy",
    summary="Ricerca fuzzy multi-script su name_original + name_variants",
    description=(
        "Ranking per similarità (SequenceMatcher ratio) sul nome originale e "
        "sulle varianti. Funziona cross-script (Greek, Persian, Chinese, "
        "Cyrillic) perché la metrica è character-level. Utile per agenti AI "
        "che ricevono nomi approssimati o in trascrizione errata."
    ),
)
def search_entities_fuzzy(
    q: str = Query(..., min_length=1, max_length=200, description="Testo da cercare (fuzzy)"),
    limit: int = Query(10, ge=1, le=50, description="Max risultati"),
    min_score: float = Query(
        0.4,
        ge=0.0,
        le=1.0,
        description="Soglia minima di similarità (0.0=tutto, 1.0=solo match esatti)",
    ),
    db: Session = Depends(get_db),
):
    """Ricerca fuzzy su tutti i nomi (originale + varianti).

    ETHICS-001 rispettato: match sul name_original (lingua locale) come
    priorità, con bonus di ranking per match esatto/prefisso sul nome
    originale rispetto ai variants (che possono essere trascrizioni
    coloniali).

    Algoritmo:
    - Per ogni entità carica name_original + tutti i name_variants.
    - Calcola SequenceMatcher ratio sul lowercase-stripped candidate.
    - Bonus di +0.10 se il match è sul name_original (non su una variant).
    - Bonus di +0.15 se il match è un prefisso case-insensitive.
    - Risultati filtrati per min_score, ordinati per score discendente.
    """
    import re
    from difflib import SequenceMatcher

    q_norm = q.strip().lower()
    if not q_norm:
        return {"query": q, "count": 0, "results": []}

    def _tokenize(s: str) -> list[str]:
        """v6.42: tokenize su whitespace + punct, lowercase."""
        return [tok for tok in re.split(r"[\s\-_.,;:'\"()]+", s.lower()) if tok]

    q_tokens = _tokenize(q_norm)

    # Carica tutte le entità + varianti (N=~1000 è fattibile in memoria
    # senza indici trigram PostgreSQL).
    entities = (
        db.query(GeoEntity)
        .options(joinedload(GeoEntity.name_variants))
        .all()
    )

    scored: list[tuple[float, GeoEntity, str, bool]] = []
    for e in entities:
        candidates: list[tuple[str, bool]] = [(e.name_original, True)]
        for v in e.name_variants:
            candidates.append((v.name, False))

        best_score = 0.0
        best_matched_name = e.name_original
        best_is_original = True
        for cand_name, is_original in candidates:
            if not cand_name:
                continue
            cand_norm = cand_name.strip().lower()

            # 1. Char-level ratio (original).
            ratio = SequenceMatcher(None, q_norm, cand_norm).ratio()

            # 2. v6.42: token-level ratio. Per 'venice' vs 'Repubblica di Venezia'
            # il char-level e' basso, ma SequenceMatcher('venice','venezia') ~0.77.
            # Prendi il max per-token e OR-alo con il char-level.
            # v6.61 fix: separa tokens PRIMARY (fuori parens) da tokens SECONDARY
            # (dentro parens). Secondary matches ricevono penalty perche' descrittivi.
            # Es. 'sultanate' NON deve matchare 'Gelgel (pre-sultanate Bali)' con
            # score 1.0 — il sultanate e' descrittivo, non il nome dell'entita'.
            primary_part = cand_norm
            secondary_part = ""
            if "(" in cand_norm and ")" in cand_norm:
                # Split: before paren is primary, inside paren is secondary
                idx_open = cand_norm.index("(")
                idx_close = cand_norm.index(")", idx_open)
                primary_part = (cand_norm[:idx_open] + cand_norm[idx_close + 1:]).strip()
                secondary_part = cand_norm[idx_open + 1:idx_close]

            primary_tokens = _tokenize(primary_part)
            secondary_tokens = _tokenize(secondary_part)

            best_primary = 0.0
            for q_tok in q_tokens:
                for c_tok in primary_tokens:
                    if not c_tok:
                        continue
                    tr = SequenceMatcher(None, q_tok, c_tok).ratio()
                    if tr > best_primary:
                        best_primary = tr

            best_secondary = 0.0
            for q_tok in q_tokens:
                for c_tok in secondary_tokens:
                    if not c_tok:
                        continue
                    tr = SequenceMatcher(None, q_tok, c_tok).ratio()
                    if tr > best_secondary:
                        best_secondary = tr

            # Primary tokens win at full weight; secondary at 0.6 weight.
            token_ratio = max(best_primary, best_secondary * 0.6)

            ratio = max(ratio, token_ratio)
            cand_tokens = primary_tokens + secondary_tokens  # keep for downstream prefix bonus

            # ETHICS-001: bonus per match sul name_original.
            if is_original:
                ratio += 0.10
            # Prefix bonus (parziale ma solido).
            if cand_norm.startswith(q_norm) or q_norm.startswith(cand_norm):
                ratio += 0.15
            # Substring fallback (handles acronyms like "URSS" in longer forms).
            elif q_norm in cand_norm or cand_norm in q_norm:
                ratio += 0.08

            # v6.42: token prefix bonus — 'venice' prefix 4-chars di 'venezia'.
            token_prefix_found = False
            for q_tok in q_tokens:
                for c_tok in cand_tokens:
                    if not c_tok:
                        continue
                    if (c_tok.startswith(q_tok) and len(q_tok) >= 3) or \
                       (q_tok.startswith(c_tok) and len(c_tok) >= 3):
                        ratio += 0.12
                        token_prefix_found = True
                        break
                if token_prefix_found:
                    break

            if ratio > best_score:
                best_score = ratio
                best_matched_name = cand_name
                best_is_original = is_original

        if best_score >= min_score:
            scored.append((best_score, e, best_matched_name, best_is_original))

    scored.sort(key=lambda t: -t[0])
    top = scored[:limit]

    return {
        "query": q,
        "count": len(top),
        "results": [
            {
                "id": e.id,
                "name_original": e.name_original,
                "name_original_lang": e.name_original_lang,
                "matched_name": matched,
                "matched_is_original": is_original,
                "score": round(min(score, 1.0), 4),  # cap display at 1.0
                "entity_type": e.entity_type,
                "year_start": e.year_start,
                "year_end": e.year_end,
                "status": e.status,
                "confidence_score": e.confidence_score,
            }
            for score, e, matched, is_original in top
        ],
    }


@router.get(
    "/v1/types",
    response_model=list[TypeInfo],
    summary="List all entity types with counts",
    description=(
        "Returns the distinct `entity_type` values used across the dataset, "
        "with a count of entities per type. Used for populating filter UI "
        "and for AI agents to understand the categorization vocabulary.\n\n"
        "Typical types include: empire, kingdom, sultanate, republic, "
        "confederation, dynasty, caliphate, khanate, principality, duchy, "
        "city-state, chiefdom, tribal_nation, cultural_region, civilization.\n\n"
        "Use with `/v1/entities?entity_type=<type>` to filter."
    ),
)
def list_types(db: Session = Depends(get_db)):
    results = (
        db.query(GeoEntity.entity_type, func.count(GeoEntity.id))
        .group_by(GeoEntity.entity_type)
        .order_by(desc(func.count(GeoEntity.id)))
        .all()
    )
    return [TypeInfo(type=t, count=c) for t, c in results]


@router.get(
    "/v1/continents",
    response_model=list[ContinentInfo],
    summary="Elenco continenti con conteggio entità",
    description="Restituisce i continenti disponibili calcolati dalle coordinate delle capitali.",
)
def list_continents(db: Session = Depends(get_db)):
    entities = db.query(GeoEntity).all()
    counts: dict[str, int] = {}
    for e in entities:
        c = _get_continent(e.capital_lat, e.capital_lon)
        counts[c] = counts.get(c, 0) + 1
    return sorted(
        [ContinentInfo(continent=c, count=n) for c, n in counts.items()],
        key=lambda x: x.count,
        reverse=True,
    )


@router.get(
    "/v1/random",
    response_model=EntityResponse,
    summary="Entit\u00e0 casuale (con filtri opzionali)",
    description=(
        "Restituisce un'entit\u00e0 casuale dal dataset. "
        "Supporta filtri per tipo, anno, status e continente."
    ),
)
def random_entity(
    response: Response,
    type: str | None = Query(None, max_length=50, description="Filtra per entity_type"),
    year: int | None = Query(None, ge=-4500, le=2100, description="Entit\u00e0 attiva in questo anno"),
    status: StatusFilter = Query(None, description="Filtra per status"),
    continent: str | None = Query(None, max_length=50, description="Filtra per continente"),
    db: Session = Depends(get_db),
):
    import random as rnd

    # PERF: selezioniamo prima solo gli ID + (se serve) capital_lat/lon per il
    # filtro continente, poi carichiamo eagerly SOLO l'entita' scelta. Con 700+
    # entita' ognuna con 60-200KB di boundary, q.all() su _eager_query
    # trasferisce decine di MB e impiega secondi.
    id_q = db.query(
        GeoEntity.id, GeoEntity.capital_lat, GeoEntity.capital_lon
    )

    if type:
        id_q = id_q.filter(GeoEntity.entity_type == type)
    if status:
        id_q = id_q.filter(GeoEntity.status == status)
    if year is not None:
        id_q = id_q.filter(GeoEntity.year_start <= year)
        id_q = id_q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))

    candidates = id_q.all()

    # Filtro continente post-query (calcolato da coordinate)
    if continent:
        candidates = [
            c for c in candidates
            if _get_continent(c.capital_lat, c.capital_lon).lower() == continent.lower()
        ]

    if not candidates:
        from src.api.errors import AtlasError
        raise AtlasError(status_code=404, detail="Nessuna entit\u00e0 corrisponde ai filtri")

    chosen_id = rnd.choice(candidates).id
    entity = _eager_query(db).filter(GeoEntity.id == chosen_id).one()
    response.headers["Cache-Control"] = "no-cache"
    return _entity_to_response(entity)


def _nearby_postgis(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float,
    year: int | None,
    limit: int,
) -> list[tuple[GeoEntity, float]]:
    """PostGIS-native nearby query usando ST_DWithin su geography.

    Indicizzabile via GiST su `ST_MakePoint(capital_lon, capital_lat)::geography`
    se il volume di entita' cresce oltre la soglia O(n) utile. A 747 righe
    l'index non e' necessario ma il percorso nativo e' comunque piu' veloce
    del Python haversine + full scan.

    Ritorna lista di tuple (GeoEntity, distance_km) gia' ordinata per
    distanza crescente e tagliata a `limit`.
    """
    radius_m = radius_km * 1000.0

    sql_parts = [
        "SELECT id,",
        "       ST_Distance(",
        "           ST_MakePoint(capital_lon, capital_lat)::geography,",
        "           ST_MakePoint(:lon, :lat)::geography",
        "       ) / 1000.0 AS dist_km",
        "  FROM geo_entities",
        " WHERE capital_lat IS NOT NULL AND capital_lon IS NOT NULL",
        "   AND ST_DWithin(",
        "           ST_MakePoint(capital_lon, capital_lat)::geography,",
        "           ST_MakePoint(:lon, :lat)::geography,",
        "           :radius_m",
        "       )",
    ]
    params: dict = {"lat": lat, "lon": lon, "radius_m": radius_m, "limit": limit}

    if year is not None:
        sql_parts.append("   AND year_start <= :year AND (year_end IS NULL OR year_end >= :year)")
        params["year"] = year

    sql_parts.append(" ORDER BY dist_km ASC LIMIT :limit")
    sql = "\n".join(sql_parts)

    rows = db.execute(text(sql), params).all()
    if not rows:
        return []

    ids_dists: list[tuple[int, float]] = [(row.id, float(row.dist_km)) for row in rows]
    ids = [i for i, _ in ids_dists]

    entities_map = {
        e.id: e
        for e in db.query(GeoEntity).filter(GeoEntity.id.in_(ids)).all()
    }
    # Preserve PostGIS ordering (by dist_km) while pairing with ORM instances.
    return [(entities_map[i], round(d, 1)) for i, d in ids_dists if i in entities_map]


def _nearby_python_haversine(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float,
    year: int | None,
    limit: int,
) -> list[tuple[GeoEntity, float]]:
    """Fallback Python haversine per SQLite (no PostGIS).

    O(n) su tutte le entita' con capitale — accettabile fino a qualche
    migliaio di righe. Per scala maggiore in dev, usare Postgres locale.
    """
    import math

    def haversine(lat1, lon1, lat2, lon2):
        earth_r = 6371  # km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return earth_r * 2 * math.asin(math.sqrt(a))

    q = db.query(GeoEntity).filter(
        GeoEntity.capital_lat.isnot(None),
        GeoEntity.capital_lon.isnot(None),
    )
    if year is not None:
        q = q.filter(GeoEntity.year_start <= year)
        q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))

    entities = q.all()
    results: list[tuple[GeoEntity, float]] = []
    for e in entities:
        dist = haversine(lat, lon, e.capital_lat, e.capital_lon)
        if dist <= radius_km:
            results.append((e, round(dist, 1)))

    results.sort(key=lambda x: x[1])
    return results[:limit]


@router.get(
    "/v1/nearby",
    summary="Entit\u00e0 vicine a coordinate date",
    description=(
        "Trova entit\u00e0 storiche vicine a una posizione geografica. "
        "Utile per agenti AI che partono da coordinate."
    ),
)
def nearby_entities(
    lat: float = Query(..., ge=-90, le=90, description="Latitudine"),
    lon: float = Query(..., ge=-180, le=180, description="Longitudine"),
    radius: float = Query(500, ge=1, le=5000, description="Raggio in km"),
    year: int | None = Query(None, ge=-4500, le=2100, description="Anno (opzionale)"),
    limit: int = Query(10, ge=1, le=50, description="Max risultati"),
    response: Response = None,
    db: Session = Depends(get_db),
):
    """Trova entit\u00e0 vicine a (lat, lon) entro `radius` km.

    ETHICS: la prossimit\u00e0 geografica \u00e8 calcolata dalla capitale,
    non dai confini reali. Per entit\u00e0 estese (es. Impero Romano)
    il risultato \u00e8 approssimativo.

    v6.2.0: in produzione (PostgreSQL+PostGIS) la query usa ST_DWithin
    nativo su ::geography — accurato su grande scala (distanze su
    sferoide WGS84) e indicizzabile via GiST. In sviluppo (SQLite)
    ripiega su haversine Python, semanticamente equivalente entro
    l'errore tipico ST_Distance vs haversine (~0.3%).
    """
    if is_postgres:
        results = _nearby_postgis(db, lat, lon, radius, year, limit)
        response.headers["X-Distance-Algorithm"] = "postgis"
    else:
        results = _nearby_python_haversine(db, lat, lon, radius, year, limit)
        response.headers["X-Distance-Algorithm"] = "haversine"

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "query": {"lat": lat, "lon": lon, "radius_km": radius, "year": year},
        "count": len(results),
        "entities": [
            {
                "id": e.id,
                "name_original": e.name_original,
                "entity_type": e.entity_type,
                "year_start": e.year_start,
                "year_end": e.year_end,
                "status": e.status,
                "confidence_score": e.confidence_score,
                "capital": {"name": e.capital_name, "lat": e.capital_lat, "lon": e.capital_lon},
                "distance_km": dist,
                "continent": _get_continent(e.capital_lat, e.capital_lon),
            }
            for e, dist in results
        ],
    }


# ─── v6.34: Reverse-geocoding temporale ──────────────────────────────

def _point_in_boundary_shapely(lat: float, lon: float, boundary_geojson: str | None) -> bool:
    """SQLite fallback: shapely point-in-polygon.

    ETHICS-005: rispetta il confidence del boundary. Se il boundary_geojson
    e' mal formato o vuoto, ritorna False (l'entita' non viene considerata
    "controllare" quel punto — meglio false-negative che false-positive).

    NOTE geografica: GeoJSON usa ordinamento (lon, lat), non (lat, lon).
    """
    if not boundary_geojson:
        return False
    try:
        geom = shapely_shape(json.loads(boundary_geojson))
    except (json.JSONDecodeError, ValueError, TypeError, GEOSException):
        return False
    try:
        return geom.contains(Point(lon, lat))
    except GEOSException:
        # Polygon invalido (self-intersecting, etc.) — tratta come non-contenente.
        return False


def _where_was_sqlite(
    db: Session,
    lat: float,
    lon: float,
    year: int | None,
) -> list[GeoEntity]:
    """Reverse-geocoding Python fallback (dev/test su SQLite).

    O(n) su tutte le entita' con boundary_geojson. A ~850 entita' e'
    accettabile (~300-500ms). In produzione PostGIS fa ST_Contains
    nativamente con indice GiST.
    """
    q = db.query(GeoEntity).filter(GeoEntity.boundary_geojson.isnot(None))
    if year is not None:
        q = q.filter(GeoEntity.year_start <= year)
        q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))
    entities = q.all()
    return [e for e in entities if _point_in_boundary_shapely(lat, lon, e.boundary_geojson)]


def _where_was_postgis(
    db: Session,
    lat: float,
    lon: float,
    year: int | None,
) -> list[GeoEntity]:
    """Reverse-geocoding PostGIS nativo (prod).

    Usa ST_Contains su ST_GeomFromGeoJSON(boundary_geojson). Se esiste
    l'indice GiST spaziale sulla colonna (ADR-001 migration futura),
    la query e' O(log n). Senza indice e' comunque ~10x piu' veloce
    del fallback Python grazie a implementazione C nativa.
    """
    sql_parts = [
        "SELECT id FROM geo_entities",
        "WHERE boundary_geojson IS NOT NULL",
        "  AND ST_Contains(",
        "      ST_GeomFromGeoJSON(boundary_geojson),",
        "      ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)",
        "  )",
    ]
    params: dict = {"lat": lat, "lon": lon}
    if year is not None:
        sql_parts.append("  AND year_start <= :year AND (year_end IS NULL OR year_end >= :year)")
        params["year"] = year

    sql = "\n".join(sql_parts)
    try:
        rows = db.execute(text(sql), params).all()
    except Exception:
        logger.warning("PostGIS ST_Contains failed for where-was query", exc_info=True)
        return []

    if not rows:
        return []

    ids = [r.id for r in rows]
    return db.query(GeoEntity).filter(GeoEntity.id.in_(ids)).all()


@router.get(
    "/v1/where-was",
    summary="Reverse-geocoding temporale: quali entit\u00e0 controllavano un punto in un anno",
    description=(
        "Given a geographic point (lat, lon) and a year, returns all historical "
        "entities whose documented `boundary_geojson` contains that point. Primary "
        "use case: **genealogy / diaspora research** (\"my great-grandfather from "
        "Lviv in 1905 — which country was that?\"), historical tourism, and "
        "educational AI tutors.\n\n"
        "**Two modes**:\n"
        "- **Year-specific** (`?lat=X&lon=Y&year=Z`): entities controlling that "
        "point in year Z\n"
        "- **History timeline** (`?lat=X&lon=Y&include_history=true`): ALL "
        "entities that ever controlled that point, sorted chronologically — "
        "shows the full succession at that location from ancient times to today.\n\n"
        "**Backend**: PostgreSQL+PostGIS uses native `ST_Contains` (O(log n) with "
        "GiST index). SQLite dev uses shapely Python fallback. Semantic parity "
        "guaranteed within ~0.1\u00b0 tolerance from polygon simplification.\n\n"
        "**For AI agents**: ideal for grounding \"where was X\" questions. After "
        "getting the entity list, follow up with `/v1/entities/{id}` for full "
        "context (boundaries, rulers, events)."
    ),
)
@cache_response(ttl_seconds=3600)
def where_was(
    request: Request,
    response: Response,
    lat: float = Query(..., ge=-90, le=90, description="Latitudine del punto"),
    lon: float = Query(..., ge=-180, le=180, description="Longitudine del punto"),
    year: int | None = Query(
        None,
        ge=-5000,
        le=2100,
        description="Anno di riferimento. Richiesto se include_history=false.",
    ),
    include_history: bool = Query(
        False,
        description="Se true, ritorna tutte le entit\u00e0 che hanno controllato "
        "il punto storicamente (serie temporale). Se false, solo l'anno richiesto.",
    ),
    db: Session = Depends(get_db),
):
    """Reverse-geocoding temporale.

    # ETHICS-003: se il punto ricade in un territorio contestato (es.
    # Palestina/Israele, Kashmir, Taiwan, Western Sahara, Crimea), questo
    # endpoint RITORNA tutte le entita' con status='disputed' che lo
    # rivendicano — non una sola versione "canonica". L'API non arbitra
    # la sovranita', la documenta (CLAUDE.md: "nessuna versione unica").
    """
    # Validazione: almeno uno tra year e include_history deve essere significativo.
    if year is None and not include_history:
        raise HTTPException(
            status_code=400,
            detail="Specify either `year=<int>` for a specific year, "
                   "or `include_history=true` for the full timeline at this point.",
        )

    # Dispatch per backend.
    def _query(y: int | None) -> list[GeoEntity]:
        if is_postgres:
            return _where_was_postgis(db, lat, lon, y)
        return _where_was_sqlite(db, lat, lon, y)

    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["X-WhereWas-Backend"] = "postgis" if is_postgres else "shapely"

    if include_history:
        # Tutte le entita' che hanno mai controllato il punto.
        entities = _query(None)
        # Ordina cronologicamente (asc per year_start).
        entities.sort(key=lambda e: (e.year_start, e.year_end or 9999))

        # Span temporale coperto.
        if entities:
            min_year = min(e.year_start for e in entities)
            max_year = max((e.year_end if e.year_end is not None else 2024) for e in entities)
            covered_years = max_year - min_year + 1
        else:
            min_year = max_year = None
            covered_years = 0

        # Se e' stato fornito anche year, estrai le entita' che lo coprono.
        current_entities = []
        if year is not None:
            current_entities = [
                e for e in entities
                if e.year_start <= year and (e.year_end is None or e.year_end >= year)
            ]

        return {
            "query": {
                "lat": lat,
                "lon": lon,
                "year": year,
                "include_history": True,
            },
            "point_covered_years": covered_years,
            "timeline_span": {
                "earliest_year": min_year,
                "latest_year": max_year,
            },
            "total_entities": len(entities),
            "current_entities_count": len(current_entities) if year is not None else None,
            "timeline": [
                {
                    "entity_id": e.id,
                    "name_original": e.name_original,
                    "name_original_lang": e.name_original_lang,
                    "entity_type": e.entity_type,
                    "year_start": e.year_start,
                    "year_end": e.year_end,
                    "confidence_score": e.confidence_score,
                    "status": e.status,
                    "is_current": (
                        year is not None
                        and e.year_start <= year
                        and (e.year_end is None or e.year_end >= year)
                    ),
                }
                for e in entities
            ],
        }

    # Year-specific mode.
    entities = _query(year)
    return {
        "query": {
            "lat": lat,
            "lon": lon,
            "year": year,
            "include_history": False,
        },
        "count": len(entities),
        "entities": [
            {
                "id": e.id,
                "name_original": e.name_original,
                "name_original_lang": e.name_original_lang,
                "entity_type": e.entity_type,
                "year_start": e.year_start,
                "year_end": e.year_end,
                "confidence_score": e.confidence_score,
                "status": e.status,
                "capital": (
                    {"name": e.capital_name, "lat": e.capital_lat, "lon": e.capital_lon}
                    if e.capital_name
                    else None
                ),
            }
            for e in entities
        ],
    }


@router.get(
    "/v1/snapshot/{year}",
    summary="Snapshot del mondo in un anno specifico",
    description=(
        "Restituisce tutte le entit\u00e0 attive in un dato anno, "
        "con conteggi per tipo e continente. Ideale per agenti AI "
        "che vogliono ricostruire il mondo in un momento storico."
    ),
)
def year_snapshot(
    year: int,
    response: Response,
    type: str | None = Query(None, max_length=50, description="Filtra per tipo"),
    continent: str | None = Query(None, max_length=50, description="Filtra per continente"),
    db: Session = Depends(get_db),
):
    if year < -4500 or year > 2100:
        from src.api.errors import AtlasError
        raise AtlasError(status_code=400, detail=f"Anno fuori range: {year}")

    q = db.query(GeoEntity).filter(GeoEntity.year_start <= year)
    q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))

    if type:
        q = q.filter(GeoEntity.entity_type == type)

    entities = q.all()

    # Calcola continenti e filtra se richiesto
    results = []
    type_counts: dict[str, int] = {}
    continent_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}

    for e in entities:
        c = _get_continent(e.capital_lat, e.capital_lon)
        if continent and c.lower() != continent.lower():
            continue
        results.append((e, c))
        type_counts[e.entity_type] = type_counts.get(e.entity_type, 0) + 1
        continent_counts[c] = continent_counts.get(c, 0) + 1
        status_counts[e.status] = status_counts.get(e.status, 0) + 1

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "year": year,
        "count": len(results),
        "summary": {
            "types": type_counts,
            "continents": continent_counts,
            "statuses": status_counts,
        },
        "entities": [
            {
                "id": e.id,
                "name_original": e.name_original,
                "entity_type": e.entity_type,
                "year_start": e.year_start,
                "year_end": e.year_end,
                "status": e.status,
                "confidence_score": e.confidence_score,
                "continent": c,
                "capital": {"name": e.capital_name, "lat": e.capital_lat, "lon": e.capital_lon}
                if e.capital_name else None,
            }
            for e, c in results
        ],
    }


@router.get(
    "/v1/stats",
    response_model=StatsResponse,
    summary="Statistiche del dataset",
    description="Panoramica del dataset: conteggi, range, media confidence.",
)
def dataset_stats(response: Response, db: Session = Depends(get_db)):
    total = db.query(GeoEntity).count()

    type_counts = (
        db.query(GeoEntity.entity_type, func.count(GeoEntity.id))
        .group_by(GeoEntity.entity_type)
        .all()
    )

    status_counts = dict(
        db.query(GeoEntity.status, func.count(GeoEntity.id))
        .group_by(GeoEntity.status)
        .all()
    )

    min_year = db.query(func.min(GeoEntity.year_start)).scalar() or 0
    max_year = db.query(func.max(GeoEntity.year_start)).scalar() or 0
    avg_conf = db.query(func.avg(GeoEntity.confidence_score)).scalar() or 0.0
    total_sources = db.query(Source).count()
    total_changes = db.query(TerritoryChange).count()
    disputed = db.query(GeoEntity).filter(GeoEntity.status == "disputed").count()

    # Continenti
    all_entities = db.query(GeoEntity).all()
    continent_counts: dict[str, int] = {}
    for ent in all_entities:
        c = _get_continent(ent.capital_lat, ent.capital_lon)
        continent_counts[c] = continent_counts.get(c, 0) + 1

    # ─── Event stats ────────────────────────────────────────────
    total_events = db.query(HistoricalEvent).count()
    events_with_day = db.query(HistoricalEvent).filter(
        HistoricalEvent.day.isnot(None),
    ).count()
    events_with_month = db.query(HistoricalEvent).filter(
        HistoricalEvent.month.isnot(None),
    ).count()
    # Unique MM-DD combinations
    unique_days = (
        db.query(HistoricalEvent.month, HistoricalEvent.day)
        .filter(HistoricalEvent.month.isnot(None), HistoricalEvent.day.isnot(None))
        .distinct()
        .count()
    )
    # Date precision breakdown
    precision_rows = (
        db.query(HistoricalEvent.date_precision, func.count(HistoricalEvent.id))
        .group_by(HistoricalEvent.date_precision)
        .all()
    )
    precision_breakdown = {
        (p or "UNKNOWN"): c for p, c in precision_rows
    }

    event_stats = EventStatsInfo(
        total_events=total_events,
        events_with_day=events_with_day,
        events_with_month=events_with_month,
        date_coverage_unique_days=unique_days,
        date_coverage_pct=round(unique_days / 366 * 100, 1) if unique_days else 0.0,
        date_precision_breakdown=precision_breakdown,
    )

    response.headers["Cache-Control"] = "public, max-age=3600"

    return StatsResponse(
        total_entities=total,
        types=[TypeInfo(type=t, count=c) for t, c in type_counts],
        status_counts=status_counts,
        year_range={"min": min_year, "max": max_year},
        avg_confidence=round(avg_conf, 3),
        total_sources=total_sources,
        total_territory_changes=total_changes,
        disputed_count=disputed,
        continents=sorted(
            [ContinentInfo(continent=c, count=n) for c, n in continent_counts.items()],
            key=lambda x: x.count, reverse=True,
        ),
        events=event_stats,
    )


# ─── Aggregation ────────────────────────────────────────────────

def _year_to_century_label(year: int) -> str:
    """Converte un anno in etichetta di secolo (es. 1500 → 'XVI', -500 → 'V a.C.')."""
    if year > 0:
        century = (year - 1) // 100 + 1
    elif year < 0:
        century = (-year - 1) // 100 + 1
    else:
        century = 1

    roman_map = {
        1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
        6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X",
        11: "XI", 12: "XII", 13: "XIII", 14: "XIV", 15: "XV",
        16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX", 20: "XX",
        21: "XXI", 22: "XXII", 23: "XXIII", 24: "XXIV", 25: "XXV",
        26: "XXVI", 27: "XXVII", 28: "XXVIII", 29: "XXIX", 30: "XXX",
        31: "XXXI", 32: "XXXII", 33: "XXXIII", 34: "XXXIV", 35: "XXXV",
        36: "XXXVI", 37: "XXXVII", 38: "XXXVIII", 39: "XXXIX", 40: "XL",
        41: "XLI", 42: "XLII", 43: "XLIII", 44: "XLIV", 45: "XLV",
        46: "XLVI",
    }
    label = roman_map.get(century, str(century))
    return f"{label} a.C." if year < 0 else label


@router.get(
    "/v1/aggregation",
    summary="Statistiche aggregate per secolo, tipo, continente e status",
    description=(
        "Restituisce conteggi aggregati delle entit\u00e0 raggruppati per "
        "secolo (basato su year_start), tipo, continente e status. "
        "Ideale per dashboard e analisi AI."
    ),
)
def aggregation(response: Response, db: Session = Depends(get_db)):
    entities = db.query(GeoEntity).all()

    by_century: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_continent: dict[str, int] = {}
    by_status: dict[str, int] = {}
    earliest = 0
    latest = 0

    for e in entities:
        # Century
        century_label = _year_to_century_label(e.year_start)
        by_century[century_label] = by_century.get(century_label, 0) + 1

        # Type
        by_type[e.entity_type] = by_type.get(e.entity_type, 0) + 1

        # Continent
        c = _get_continent(e.capital_lat, e.capital_lon)
        by_continent[c] = by_continent.get(c, 0) + 1

        # Status
        by_status[e.status] = by_status.get(e.status, 0) + 1

        # Time span
        if e.year_start < earliest:
            earliest = e.year_start
        if e.year_start > latest:
            latest = e.year_start

    # Ordina secoli cronologicamente (a.C. prima, poi d.C.)
    def century_sort_key(label: str) -> int:
        roman_to_int = {
            "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
            "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
            "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
            "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20,
            "XXI": 21, "XXII": 22, "XXIII": 23, "XXIV": 24, "XXV": 25,
            "XXVI": 26, "XXVII": 27, "XXVIII": 28, "XXIX": 29, "XXX": 30,
            "XXXI": 31, "XXXII": 32, "XXXIII": 33, "XXXIV": 34, "XXXV": 35,
            "XXXVI": 36, "XXXVII": 37, "XXXVIII": 38, "XXXIX": 39, "XL": 40,
            "XLI": 41, "XLII": 42, "XLIII": 43, "XLIV": 44, "XLV": 45,
            "XLVI": 46,
        }
        if label.endswith(" a.C."):
            roman = label[:-5]
            return -(roman_to_int.get(roman, 0))
        return roman_to_int.get(label, 0)

    sorted_centuries = sorted(by_century.keys(), key=century_sort_key)

    response.headers["Cache-Control"] = "public, max-age=3600"

    return {
        "by_century": [{"century": c, "count": by_century[c]} for c in sorted_centuries],
        "by_type": sorted(
            [{"type": t, "count": n} for t, n in by_type.items()],
            key=lambda x: x["count"], reverse=True,
        ),
        "by_continent": sorted(
            [{"continent": c, "count": n} for c, n in by_continent.items()],
            key=lambda x: x["count"], reverse=True,
        ),
        "by_status": sorted(
            [{"status": s, "count": n} for s, n in by_status.items()],
            key=lambda x: x["count"], reverse=True,
        ),
        "total": len(entities),
        "time_span": {"earliest": earliest, "latest": latest},
    }
