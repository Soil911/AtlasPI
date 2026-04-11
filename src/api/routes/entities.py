"""Endpoint per le entità geopolitiche — vedi ADR-002.

GET /v1/entity?name=...&year=...&status=...&type=...&sort=...  query principale
GET /v1/entities?limit=...&offset=...                           elenco paginato
GET /v1/entities/{id}                                           dettaglio entità
GET /v1/search?q=...                                            autocomplete
GET /v1/types                                                   tipi disponibili
GET /v1/stats                                                   statistiche dataset
GET /v1/continents                                              continenti disponibili
"""

import json
import logging
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, joinedload

from src.api.errors import EntityNotFoundError
from src.api.schemas import (
    CapitalResponse,
    EntityResponse,
    PaginatedEntityResponse,
)
from src.db.database import get_db
from src.db.models import GeoEntity, NameVariant, Source, TerritoryChange

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
    summary="Elenco paginato di tutte le entità",
)
def list_entities(
    response: Response,
    sort: SortField = Query(None, description="Ordina per: name, year_start, confidence, year_end"),
    order: Literal["asc", "desc"] = Query("asc", description="Direzione ordinamento"),
    limit: int = Query(20, ge=1, le=100, description="Risultati per pagina"),
    offset: int = Query(0, ge=0, description="Offset"),
    db: Session = Depends(get_db),
):
    total = db.query(GeoEntity).count()
    q = _eager_query(db)
    q = _apply_sort(q, sort, order)
    results = q.offset(offset).limit(limit).all()
    entities = [_entity_to_response(e) for e in results]

    response.headers["Cache-Control"] = "public, max-age=3600"
    return PaginatedEntityResponse(count=total, limit=limit, offset=offset, entities=entities)


@router.get(
    "/v1/entities/{entity_id}",
    response_model=EntityResponse,
    summary="Dettaglio di una singola entità",
)
def get_entity(entity_id: int, response: Response, db: Session = Depends(get_db)):
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
    "/v1/types",
    response_model=list[TypeInfo],
    summary="Elenco tipi di entità disponibili",
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
    )
