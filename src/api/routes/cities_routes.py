"""Endpoint per città storiche e rotte commerciali — v6.4.

GET  /v1/cities                     list + filter (year, type, entity_id, bbox, near)
GET  /v1/cities/{id}                detail
GET  /v1/cities/types               enumera CityType

GET  /v1/routes                     list + filter (year, route_type, involves_slavery)
GET  /v1/routes/{id}                detail (con waypoints ordinati)
GET  /v1/routes/types               enumera RouteType

ETHICS-009: il nome primario è quello originale/locale; i rename coloniali
(Constantinople/Istanbul, Königsberg/Kaliningrad) vanno in name_variants
con spiegazione del contesto in ethical_notes.

ETHICS-010: le rotte che trafficavano esseri umani (Trans-Atlantic /
Trans-Saharan / Indian Ocean slave trade) hanno `involves_slavery=True` +
`"humans_enslaved"` in `commodities`. Il flag `involves_slavery` è
denormalizzato apposta per permettere filtri espliciti:
`/v1/routes?involves_slavery=true` restituisce tutte e solo le rotte
schiaviste documentate.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from src.api.errors import AtlasError
from src.db.database import get_db
from src.db.enums import CityType, RouteType
from src.db.models import HistoricalCity, RouteCityLink, TradeRoute

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cities-routes"])


class CityNotFoundError(AtlasError):
    def __init__(self, city_id: int):
        super().__init__(404, f"City with id={city_id} not found", "NOT_FOUND")


class RouteNotFoundError(AtlasError):
    def __init__(self, route_id: int):
        super().__init__(404, f"Route with id={route_id} not found", "NOT_FOUND")


# ─── helpers ───────────────────────────────────────────────────────────────


def _parse_bbox(bbox: str | None) -> tuple[float, float, float, float] | None:
    """Parse bbox string "min_lon,min_lat,max_lon,max_lat" → tuple o 422."""
    if bbox is None:
        return None
    parts = bbox.split(",")
    if len(parts) != 4:
        raise HTTPException(
            status_code=422,
            detail=f"bbox must have 4 values (min_lon,min_lat,max_lon,max_lat), got {len(parts)}",
        )
    try:
        min_lon, min_lat, max_lon, max_lat = (float(p.strip()) for p in parts)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"bbox contains non-numeric values: {bbox!r}",
        )
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        raise HTTPException(
            status_code=422, detail="longitude out of range [-180,180]"
        )
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        raise HTTPException(
            status_code=422, detail="latitude out of range [-90,90]"
        )
    if min_lon > max_lon or min_lat > max_lat:
        raise HTTPException(
            status_code=422, detail="inverted bbox: min > max"
        )
    return (min_lon, min_lat, max_lon, max_lat)


def _city_summary(c: HistoricalCity) -> dict:
    return {
        "id": c.id,
        "name_original": c.name_original,
        "name_original_lang": c.name_original_lang,
        "city_type": c.city_type,
        "latitude": c.latitude,
        "longitude": c.longitude,
        "founded_year": c.founded_year,
        "abandoned_year": c.abandoned_year,
        "population_peak": c.population_peak,
        "entity_id": c.entity_id,
        "confidence_score": c.confidence_score,
        "status": c.status,
    }


def _city_detail(c: HistoricalCity) -> dict:
    base = _city_summary(c)
    # JSON fields sono salvati come stringhe — decodifichiamo per l'output.
    sources = json.loads(c.sources) if c.sources else []
    name_variants = json.loads(c.name_variants) if c.name_variants else []
    base.update(
        {
            "population_peak_year": c.population_peak_year,
            "ethical_notes": c.ethical_notes,
            "sources": sources,
            "name_variants": name_variants,
            "entity_name": c.entity.name_original if c.entity else None,
        }
    )
    return base


def _simplify_linestring(geometry: dict | None, tolerance: float = 0.5) -> dict | None:
    """Semplifica un LineString/MultiLineString GeoJSON con tolleranza Douglas-Peucker.

    v6.66 FIX 3: il frontend deve poter disegnare le rotte nella vista lista
    senza scaricare la geometria completa. Usiamo shapely se disponibile,
    altrimenti fallback al thinning "ogni N punti" per minimizzare dipendenze.

    Tolerance 0.5° mantiene la forma generale (~55 km in lat) riducendo
    i vertici del 70-90% su rotte lunghe (Silk Road etc.).
    """
    if not geometry or not isinstance(geometry, dict):
        return None
    gtype = geometry.get("type")
    if gtype not in {"LineString", "MultiLineString"}:
        # Altri tipi (es. Polygon per rotte "area") → ritorna tal quale.
        return geometry

    try:
        from shapely.geometry import mapping as _mapping
        from shapely.geometry import shape as _shape
        g = _shape(geometry)
        simplified = g.simplify(tolerance, preserve_topology=False)
        return _mapping(simplified)
    except Exception:
        # Fallback: thinning ogni N punti (preserva gli endpoint).
        try:
            if gtype == "LineString":
                coords = geometry.get("coordinates", [])
                if len(coords) <= 4:
                    return geometry
                step = max(1, len(coords) // 20)
                thinned = coords[::step]
                if thinned[-1] != coords[-1]:
                    thinned.append(coords[-1])
                return {"type": "LineString", "coordinates": thinned}
        except Exception:
            pass
        return geometry


def _route_start_end_coords(r: TradeRoute) -> tuple[float | None, float | None, float | None, float | None]:
    """Estrae (start_lat, start_lon, end_lat, end_lon) da geometry o waypoints."""
    # Preferisci geometry_geojson se disponibile.
    if r.geometry_geojson:
        try:
            g = json.loads(r.geometry_geojson)
            if g.get("type") == "LineString":
                coords = g.get("coordinates", [])
                if coords:
                    sx, sy = coords[0][0], coords[0][1]
                    ex, ey = coords[-1][0], coords[-1][1]
                    # GeoJSON: [lon, lat] per convention RFC 7946.
                    return (sy, sx, ey, ex)
            elif g.get("type") == "MultiLineString":
                lines = g.get("coordinates", [])
                if lines and lines[0] and lines[-1]:
                    sx, sy = lines[0][0][0], lines[0][0][1]
                    ex, ey = lines[-1][-1][0], lines[-1][-1][1]
                    return (sy, sx, ey, ex)
        except (json.JSONDecodeError, TypeError, IndexError, KeyError):
            pass
    # Fallback: waypoints (primo e ultimo terminale).
    try:
        links = sorted(r.city_links, key=lambda lk: lk.sequence_order or 0)
        if links and links[0].city and links[-1].city:
            return (
                links[0].city.latitude,
                links[0].city.longitude,
                links[-1].city.latitude,
                links[-1].city.longitude,
            )
    except Exception:
        pass
    return (None, None, None, None)


def _route_summary(r: TradeRoute) -> dict:
    """Summary di una rotta.

    v6.66 FIX 3: include geometry_simplified (Douglas-Peucker 0.5°) +
    start/end lat/lon come fallback minimale — il frontend deve poter
    disegnare le linee sulla mappa senza fare una seconda chiamata a
    /v1/routes/{id} per ciascuna rotta. La full geometry resta in
    /v1/routes/{id} come `geometry` (full resolution).
    """
    commodities = json.loads(r.commodities) if r.commodities else []
    geometry_full = None
    if r.geometry_geojson:
        try:
            geometry_full = json.loads(r.geometry_geojson)
        except (json.JSONDecodeError, TypeError):
            geometry_full = None
    geometry_simplified = _simplify_linestring(geometry_full, tolerance=0.5)
    start_lat, start_lon, end_lat, end_lon = _route_start_end_coords(r)
    return {
        "id": r.id,
        "name_original": r.name_original,
        "name_original_lang": r.name_original_lang,
        "route_type": r.route_type,
        "start_year": r.start_year,
        "end_year": r.end_year,
        "involves_slavery": r.involves_slavery,
        "commodities": commodities,
        "confidence_score": r.confidence_score,
        "status": r.status,
        # v6.66 FIX 3: geometria leggera per rendering in list view.
        "geometry_simplified": geometry_simplified,
        "start_lat": start_lat,
        "start_lon": start_lon,
        "end_lat": end_lat,
        "end_lon": end_lon,
    }


def _route_detail(r: TradeRoute) -> dict:
    base = _route_summary(r)
    sources = json.loads(r.sources) if r.sources else []
    geometry = json.loads(r.geometry_geojson) if r.geometry_geojson else None
    waypoints = [
        {
            "sequence_order": link.sequence_order,
            "is_terminal": link.is_terminal,
            "city_id": link.city_id,
            "city_name": link.city.name_original if link.city else None,
            "latitude": link.city.latitude if link.city else None,
            "longitude": link.city.longitude if link.city else None,
        }
        for link in r.city_links
    ]
    base.update(
        {
            "description": r.description,
            "ethical_notes": r.ethical_notes,
            "sources": sources,
            "geometry": geometry,
            "waypoints": waypoints,
        }
    )
    return base


# ─── CITIES ────────────────────────────────────────────────────────────────


@router.get(
    "/v1/cities",
    summary="List historical cities",
    description=(
        "Paginated list of historical cities with filters on year, type, entity, "
        "bbox and geographic proximity. A city is kept separate from GeoEntity's "
        "capital_* because it can outlive multiple political entities."
    ),
)
def list_cities(
    response: Response,
    year: int | None = Query(
        None,
        description="Activity year (city existing in that year): "
        "founded_year <= year AND (abandoned_year IS NULL OR abandoned_year >= year).",
    ),
    city_type: str | None = Query(
        None, description="Filter by CityType (e.g. TRADE_HUB, CAPITAL)"
    ),
    entity_id: int | None = Query(
        None, description="Filter by the political entity the city belongs to"
    ),
    bbox: str | None = Query(
        None,
        description="Spatial filter. Format: min_lon,min_lat,max_lon,max_lat.",
    ),
    status: str | None = Query(
        None, description="confirmed / uncertain / disputed"
    ),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(HistoricalCity)

    if year is not None:
        q = q.filter(
            or_(HistoricalCity.founded_year.is_(None), HistoricalCity.founded_year <= year),
            or_(HistoricalCity.abandoned_year.is_(None), HistoricalCity.abandoned_year >= year),
        )
    if city_type is not None:
        q = q.filter(HistoricalCity.city_type == city_type)
    if entity_id is not None:
        q = q.filter(HistoricalCity.entity_id == entity_id)
    if status is not None:
        q = q.filter(HistoricalCity.status == status)

    parsed = _parse_bbox(bbox)
    if parsed is not None:
        min_lon, min_lat, max_lon, max_lat = parsed
        # Cities hanno SEMPRE coordinate (colonne NOT NULL), quindi
        # il filtro è uniforme su SQLite/PostGIS: bastano BETWEEN sui punti.
        # (L'indice GiST su PostGIS accelera comunque se disponibile,
        # ma qui le query sono point-in-rectangle, non geometry intersection.)
        q = q.filter(
            HistoricalCity.latitude.between(min_lat, max_lat),
            HistoricalCity.longitude.between(min_lon, max_lon),
        )

    total = q.count()
    results = (
        q.order_by(HistoricalCity.name_original, HistoricalCity.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    response.headers["Cache-Control"] = "public, max-age=1800"
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "cities": [_city_summary(c) for c in results],
    }


@router.get(
    "/v1/cities/types",
    summary="Enumerate city types",
    description="Returns the CityType enum with a short description.",
)
def list_city_types(response: Response):
    response.headers["Cache-Control"] = "public, max-age=86400"
    descriptions = {
        "CAPITAL": "Political capital of an entity (current or historical).",
        "TRADE_HUB": "Trade hub (Samarkand, Venice, Malacca).",
        "RELIGIOUS_CENTER": "Religious center of trans-regional significance.",
        "FORTRESS": "Fortress or walled city with a primary defensive function.",
        "PORT": "Maritime or river port of commercial/military significance.",
        "ACADEMIC_CENTER": "Center of learning (Timbuktu, Bologna, Nalanda).",
        "INDUSTRIAL_CENTER": "Industrial production center (post-1750).",
        "MULTI_PURPOSE": "Multiple co-dominant functions (default).",
        "OTHER": "City outside the standard categories.",
    }
    return {
        "city_types": [
            {"type": t.value, "description": descriptions.get(t.value, "")}
            for t in CityType
        ],
    }


@router.get(
    "/v1/cities/{city_id}",
    summary="Historical city detail",
    description=(
        "Detail of a historical city with name_variants (ETHICS-009: "
        "colonial/imperial renames), sources and owning entity."
    ),
)
def get_city(city_id: int, response: Response, db: Session = Depends(get_db)):
    c = (
        db.query(HistoricalCity)
        .options(joinedload(HistoricalCity.entity))
        .filter(HistoricalCity.id == city_id)
        .first()
    )
    if not c:
        raise CityNotFoundError(city_id)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return _city_detail(c)


# ─── ROUTES ────────────────────────────────────────────────────────────────


@router.get(
    "/v1/routes",
    summary="List trade routes",
    description=(
        "Paginated list of historical trade routes (Silk Road, Trans-"
        "Saharan, Trans-Atlantic slave trade, Amber Route, etc). "
        "ETHICS-010: `involves_slavery=true` filters routes that "
        "trafficked human beings — the flag is explicit because the "
        "distinction is ethically significant."
    ),
)
def list_routes(
    response: Response,
    year: int | None = Query(
        None, description="Activity year (start_year <= year <= end_year)."
    ),
    route_type: str | None = Query(
        None, description="LAND / SEA / RIVER / CARAVAN / MIXED"
    ),
    involves_slavery: bool | None = Query(
        None, description="ETHICS-010: filter routes that trafficked human beings"
    ),
    status: str | None = Query(
        None, description="confirmed / uncertain / disputed"
    ),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(TradeRoute)
    if year is not None:
        q = q.filter(
            or_(TradeRoute.start_year.is_(None), TradeRoute.start_year <= year),
            or_(TradeRoute.end_year.is_(None), TradeRoute.end_year >= year),
        )
    if route_type is not None:
        q = q.filter(TradeRoute.route_type == route_type)
    if involves_slavery is not None:
        q = q.filter(TradeRoute.involves_slavery == involves_slavery)
    if status is not None:
        q = q.filter(TradeRoute.status == status)

    total = q.count()
    results = (
        q.order_by(TradeRoute.name_original, TradeRoute.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    response.headers["Cache-Control"] = "public, max-age=1800"
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "routes": [_route_summary(r) for r in results],
    }


@router.get(
    "/v1/routes/types",
    summary="Enumerate route types",
    description="Returns the RouteType enum with a short description.",
)
def list_route_types(response: Response):
    response.headers["Cache-Control"] = "public, max-age=86400"
    descriptions = {
        "LAND": "Land route (roads, trails).",
        "SEA": "Ocean-going maritime route.",
        "RIVER": "Inland river route.",
        "CARAVAN": "Caravan route (camels, yaks) with caravanserais.",
        "MIXED": "Combination of multiple modes.",
    }
    return {
        "route_types": [
            {"type": t.value, "description": descriptions.get(t.value, "")}
            for t in RouteType
        ],
    }


@router.get(
    "/v1/routes/{route_id}",
    summary="Trade route detail",
    description=(
        "Full detail with GeoJSON geometry, commodities, ordered waypoints "
        "and sources. ETHICS-010: `ethical_notes` makes scale and "
        "main_actors explicit for slave-trade routes."
    ),
)
def get_route(route_id: int, response: Response, db: Session = Depends(get_db)):
    r = (
        db.query(TradeRoute)
        .options(
            joinedload(TradeRoute.city_links).joinedload(RouteCityLink.city),
        )
        .filter(TradeRoute.id == route_id)
        .first()
    )
    if not r:
        raise RouteNotFoundError(route_id)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return _route_detail(r)


@router.get("/v1/trade-routes", include_in_schema=False)
def redirect_trade_routes(request: Request):
    """Alias: /v1/trade-routes → /v1/routes (backward compat for users hitting wrong path)."""
    qs = request.url.query
    target = f"/v1/routes?{qs}" if qs else "/v1/routes"
    return RedirectResponse(url=target, status_code=301)
