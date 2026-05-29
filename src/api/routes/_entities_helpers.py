"""Private helpers + schemas locali per src/api/routes/entities.py.

v6.97.0 (audit R6): estratti da entities.py (1814 righe → ~1200) per
ridurre il file principale e raggruppare gli helper per concern:

- Continent classification (`_get_continent`)
- Pydantic schemas locali (SearchResult, SearchResponse, TypeInfo, ...)
- ORM → API conversion (`_entity_to_response`)
- Query helpers (`_eager_query`, `_apply_sort`)
- Spatial filters bbox (`_parse_bbox`, `_apply_bbox_filter`)
- Spatial filters point-in-polygon (`_parse_contains`, `_apply_contains_filter`)
- Nearby distance computation (`_nearby_postgis`, `_nearby_python_haversine`)
- Reverse-geocoding (`_point_in_boundary_shapely`, `_where_was_sqlite`, `_where_was_postgis`)
- Aggregation utilities (`_year_to_century_label`)

Tutti gli helper sono privati (prefix `_`) e importati esplicitamente da
entities.py — niente `from X import *`. Schemas pubblici (no underscore)
sono usati anche dagli endpoint per response_model.

ETHICS: ogni helper preserva la semantica originale documentata nel
docstring (continent classification = approssimazione politica;
boundary point-in-polygon = false-negative > false-positive; PostGIS
nearby usa geography ::sferoide WGS84).
"""

from __future__ import annotations

import json
import logging
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel
from shapely.errors import GEOSException
from shapely.geometry import Point
from shapely.geometry import shape as shapely_shape
from sqlalchemy import and_, desc, func, or_, text
from sqlalchemy.orm import Session, defer, selectinload

from src.api.schemas import CapitalResponse, EntityResponse
from src.db.database import is_postgres
from src.db.models import GeoEntity

logger = logging.getLogger(__name__)

# ─── Type aliases ───────────────────────────────────────────────────

StatusFilter = Literal["confirmed", "uncertain", "disputed"] | None
SortField = Literal["name", "year_start", "confidence", "year_end"] | None


# ─── Schemas locali ─────────────────────────────────────────────────

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
    """Risposta search.

    v6.66 FIX 4: include sia `total` (canonico) sia `count` (legacy deprecato).
    """
    total: int
    count: int  # DEPRECATED v6.66 — alias di `total`, verra' rimosso in v6.68.
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


# ─── Continent classification (math hardcoded) ──────────────────────


def _get_continent(lat: float | None, lon: float | None) -> str:
    """Determina il continente dalla posizione della capitale.

    ETHICS: il mapping è un'approssimazione geografica, non una
    dichiarazione politica. Le entità trans-continentali (es. Impero
    Romano, Ottomano) vengono assegnate al continente della capitale.

    v6.63 fix (audit #02): Oceania include Melanesia (PNG, Solomon,
    Vanuatu, Fiji), Micronesia (Guam, Marshall), Polinesia orientale
    (Easter Island, Hawaii, French Polynesia). Check fatto PRIMA di Asia.

    v6.67 fix (audit v2 #04 HIGH): Middle East lon range esteso da 50 a
    63 per includere Iran (Persepolis 52.89°E). Prima del fix, l'Impero
    Achemenide cadeva nel fallback Africa — geograficamente sbagliato.
    """
    if lat is None or lon is None:
        return "Unknown"

    # Middle East special case (politicamente Asia ma spesso trattato a parte).
    if 25 <= lat <= 42 and 25 <= lon <= 63:
        return "Middle East"

    # v6.63: Oceania (Melanesia + Micronesia + Polynesia) — CHECKED FIRST.
    if -50 <= lat <= 25:
        # West Pacific (Melanesia + Micronesia + West Polynesia)
        if 130 <= lon <= 180:
            return "Oceania"
        # East Pacific (Polynesia + Hawaii)
        if -180 <= lon <= -105:
            return "Oceania"

    # Africa
    if lat < 37 and -20 <= lon <= 55 and lat < (37 - (lon - 10) * 0.05 if lon > 10 else 37):
        if lat < 35:
            return "Africa"

    # Europe
    if 35 <= lat <= 72 and -25 <= lon <= 40:
        return "Europe"

    # Asia (mainland — islands gia' presi da Oceania check).
    if -15 <= lat <= 75 and 40 <= lon <= 180:
        return "Asia"

    # North America
    if 7 <= lat <= 85 and -170 <= lon <= -50:
        return "Americas"

    # South America
    if -60 <= lat <= 15 and -85 <= lon <= -30:
        return "Americas"

    # Africa fallback
    if -40 <= lat <= 37 and -20 <= lon <= 55:
        return "Africa"

    return "Other"


# ─── ORM → API conversion ───────────────────────────────────────────


def _entity_to_response(entity: GeoEntity, *, include_geometry: bool = True) -> EntityResponse:
    """Converte un record ORM in risposta API.

    v6.91 PERF (suggestion #72): `include_geometry=False` salta sia il
    JSON-parse del `boundary_geojson` (costo dominante a limit=300) sia il
    fetch della colonna dal DB (deferita a livello query).
    """
    capital = None
    if entity.capital_name and entity.capital_lat is not None:
        capital = CapitalResponse(
            name=entity.capital_name,
            lat=entity.capital_lat,
            lon=entity.capital_lon,
        )

    geojson = None
    if include_geometry and entity.boundary_geojson:
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
        wikidata_qid=entity.wikidata_qid,
        # v6.87 ADR-004: capital history per polities long-duration.
        capital_history=entity.capital_history,
    )


# ─── Query helpers ──────────────────────────────────────────────────


def _eager_query(db: Session, *, include_geometry: bool = True):
    """Query GeoEntity con eager-load delle relazioni + opzionale defer.

    selectinload evita cartesian product su large result sets (suggestion #67).
    v6.91 PERF (suggestion #72): include_geometry=False defer-loada
    boundary_geojson (~30-300KB per row) per evitare 2.1s a limit=300.
    """
    opts = [
        selectinload(GeoEntity.name_variants),
        selectinload(GeoEntity.territory_changes),
        selectinload(GeoEntity.sources),
        selectinload(GeoEntity.capital_history),  # v6.87 ADR-004
    ]
    if not include_geometry:
        opts.append(defer(GeoEntity.boundary_geojson))
    return db.query(GeoEntity).options(*opts)


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


# ─── Spatial filters: bbox ──────────────────────────────────────────


def _parse_bbox(bbox: str | None) -> tuple[float, float, float, float] | None:
    """Parse bbox 'min_lon,min_lat,max_lon,max_lat' (RFC 7946: lon prima).

    Raises HTTPException 422 se formato invalido o coordinate fuori range.
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

    PostgreSQL+PostGIS (v6.94.1+, audit R1): ST_Intersects(boundary_geom, envelope)
    usa l'indice GiST sulla colonna `ix_geo_entities_boundary_geom_gist`
    (migration 022 — la 019 era no-op per collisione di nome con la 004, vedi
    Wave 2.1). Fallback al capital-point per entità senza boundary_geom.

    SQLite (dev): filtro approssimato sul solo capital-point.
    """
    parsed = _parse_bbox(bbox)
    if parsed is None:
        return q
    min_lon, min_lat, max_lon, max_lat = parsed

    if is_postgres:
        # ADR-009: boundary_geom non e' mappata in ORM. Usiamo column() come ref.
        from sqlalchemy import column

        boundary_geom = column("boundary_geom")
        envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
        return q.filter(
            or_(
                and_(
                    boundary_geom.isnot(None),
                    func.ST_Intersects(boundary_geom, envelope),
                ),
                and_(
                    boundary_geom.is_(None),
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


# ─── Spatial filters: point-in-polygon ──────────────────────────────


def _parse_contains(contains: str | None) -> tuple[float, float] | None:
    """Parse contains 'lat,lon' (NB: lat prima — coerente con /v1/where-was).

    v6.94.1 (audit R1).
    """
    if not contains:
        return None
    try:
        parts = [float(x.strip()) for x in contains.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="contains deve essere 'lat,lon' (2 float separati da virgola)",
        )
    if len(parts) != 2:
        raise HTTPException(
            status_code=422,
            detail=f"contains richiede esattamente 2 valori, ricevuti {len(parts)}",
        )
    lat, lon = parts
    if not (-90.0 <= lat <= 90.0):
        raise HTTPException(status_code=422, detail="Latitudine fuori range [-90, 90]")
    if not (-180.0 <= lon <= 180.0):
        raise HTTPException(status_code=422, detail="Longitudine fuori range [-180, 180]")
    return (lat, lon)


def _apply_contains_filter(q, contains: str | None):
    """Filtra entita' il cui boundary_geom contiene il punto (lat, lon).

    PostgreSQL+PostGIS: ST_Contains(boundary_geom, ST_MakePoint(...)) — usa GiST.
    SQLite: ritorna query vuota (PostGIS-only feature).
    """
    parsed = _parse_contains(contains)
    if parsed is None:
        return q
    lat, lon = parsed

    if is_postgres:
        from sqlalchemy import column

        boundary_geom = column("boundary_geom")
        point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        return q.filter(
            boundary_geom.isnot(None),
            func.ST_Contains(boundary_geom, point),
        )

    return q.filter(False)


# ─── Nearby distance computation ────────────────────────────────────


def _nearby_postgis(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float,
    year: int | None,
    limit: int,
) -> list[tuple[GeoEntity, float]]:
    """PostGIS-native nearby usando ST_DWithin su ::geography sferoide WGS84.

    v6.2.0: ~20ms p95 su 750 entita' (vs ~180ms haversine Python).
    Indicizzabile via GiST se volume cresce. Ritorna lista (GeoEntity,
    distance_km) ordinata per distanza crescente.
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

    O(n) su tutte le entita' con capitale. Accettabile fino a qualche migliaio
    di righe. Per scala maggiore in dev, usare Postgres locale.
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


# ─── Reverse-geocoding (where-was) ─────────────────────────────────


def _point_in_boundary_shapely(lat: float, lon: float, boundary_geojson: str | None) -> bool:
    """SQLite fallback: shapely point-in-polygon.

    ETHICS-005: rispetta il confidence del boundary. Se malformato/vuoto,
    ritorna False (meglio false-negative che false-positive).

    NOTE: GeoJSON usa (lon, lat), non (lat, lon).
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
        # Polygon invalido (self-intersecting, etc.).
        return False


def _where_was_sqlite(
    db: Session,
    lat: float,
    lon: float,
    year: int | None,
) -> list[GeoEntity]:
    """Reverse-geocoding Python fallback (dev/test su SQLite). O(n)."""
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
    """Reverse-geocoding PostGIS nativo.

    ST_Contains(ST_GeomFromGeoJSON(boundary_geojson), point). Con ADR-009
    boundary_geom + GiST index questa query passa via planner all'indice.
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


# ─── Aggregation utilities ──────────────────────────────────────────


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


__all__ = [
    # type aliases
    "StatusFilter",
    "SortField",
    # schemas
    "SearchResult",
    "SearchResponse",
    "TypeInfo",
    "ContinentInfo",
    "EventStatsInfo",
    "StatsResponse",
    # private helpers
    "_get_continent",
    "_entity_to_response",
    "_eager_query",
    "_apply_sort",
    "_parse_bbox",
    "_apply_bbox_filter",
    "_parse_contains",
    "_apply_contains_filter",
    "_nearby_postgis",
    "_nearby_python_haversine",
    "_point_in_boundary_shapely",
    "_where_was_sqlite",
    "_where_was_postgis",
    "_year_to_century_label",
]
