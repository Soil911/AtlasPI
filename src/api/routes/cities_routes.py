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

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from src.api.errors import AtlasError
from src.db.database import get_db, is_postgres
from src.db.enums import CityType, RouteType
from src.db.models import HistoricalCity, RouteCityLink, TradeRoute

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cities-routes"])


class CityNotFoundError(AtlasError):
    def __init__(self, city_id: int):
        super().__init__(404, f"Città con id={city_id} non trovata", "NOT_FOUND")


class RouteNotFoundError(AtlasError):
    def __init__(self, route_id: int):
        super().__init__(404, f"Rotta con id={route_id} non trovata", "NOT_FOUND")


# ─── helpers ───────────────────────────────────────────────────────────────


def _parse_bbox(bbox: str | None) -> tuple[float, float, float, float] | None:
    """Parse bbox string "min_lon,min_lat,max_lon,max_lat" → tuple o 422."""
    if bbox is None:
        return None
    parts = bbox.split(",")
    if len(parts) != 4:
        raise HTTPException(
            status_code=422,
            detail=f"bbox deve avere 4 valori (min_lon,min_lat,max_lon,max_lat), ricevuti {len(parts)}",
        )
    try:
        min_lon, min_lat, max_lon, max_lat = (float(p.strip()) for p in parts)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"bbox contiene valori non numerici: {bbox!r}",
        )
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        raise HTTPException(
            status_code=422, detail="longitudine fuori range [-180,180]"
        )
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        raise HTTPException(
            status_code=422, detail="latitudine fuori range [-90,90]"
        )
    if min_lon > max_lon or min_lat > max_lat:
        raise HTTPException(
            status_code=422, detail="bbox invertito: min > max"
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


def _route_summary(r: TradeRoute) -> dict:
    commodities = json.loads(r.commodities) if r.commodities else []
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
    summary="Lista città storiche",
    description=(
        "Lista paginata di città storiche con filtri su anno, tipo, entità, "
        "bbox e prossimità geografica. Una città è separata dalla capital_* "
        "di GeoEntity perché può sopravvivere più entità politiche."
    ),
)
def list_cities(
    response: Response,
    year: int | None = Query(
        None,
        description="Anno di attività (città esistente in quell'anno): "
        "founded_year <= year AND (abandoned_year IS NULL OR abandoned_year >= year).",
    ),
    city_type: str | None = Query(
        None, description="Filtra per CityType (es. TRADE_HUB, CAPITAL)"
    ),
    entity_id: int | None = Query(
        None, description="Filtra per entità politica di appartenenza"
    ),
    bbox: str | None = Query(
        None,
        description="Filtro spaziale. Formato: min_lon,min_lat,max_lon,max_lat.",
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
    summary="Enumera i tipi di città",
    description="Restituisce l'enum CityType con breve descrizione.",
)
def list_city_types(response: Response):
    response.headers["Cache-Control"] = "public, max-age=86400"
    descriptions = {
        "CAPITAL": "Capitale politica di un'entità (attuale o storica).",
        "TRADE_HUB": "Nodo commerciale (Samarcanda, Venezia, Malacca).",
        "RELIGIOUS_CENTER": "Centro religioso di rilevanza trans-regionale.",
        "FORTRESS": "Fortezza o città murata con funzione difensiva primaria.",
        "PORT": "Porto marittimo o fluviale di rilevanza commerciale/militare.",
        "ACADEMIC_CENTER": "Centro di studi (Timbuctù, Bologna, Nalanda).",
        "INDUSTRIAL_CENTER": "Centro produttivo industriale (post-1750).",
        "MULTI_PURPOSE": "Più funzioni co-dominanti (default).",
        "OTHER": "Città fuori dalle categorie standard.",
    }
    return {
        "city_types": [
            {"type": t.value, "description": descriptions.get(t.value, "")}
            for t in CityType
        ],
    }


@router.get(
    "/v1/cities/{city_id}",
    summary="Dettaglio città storica",
    description=(
        "Dettaglio di una città storica con name_variants (ETHICS-009: "
        "rename coloniali/imperiali), sources e entità di appartenenza."
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
    summary="Lista rotte commerciali",
    description=(
        "Lista paginata di rotte commerciali storiche (Silk Road, Trans-"
        "Saharan, Trans-Atlantic slave trade, Amber Route, etc). "
        "ETHICS-010: `involves_slavery=true` filtra le rotte che "
        "trafficavano esseri umani — il flag è esplicito perché la "
        "distinzione è eticamente rilevante."
    ),
)
def list_routes(
    response: Response,
    year: int | None = Query(
        None, description="Anno di attività (start_year <= year <= end_year)."
    ),
    route_type: str | None = Query(
        None, description="LAND / SEA / RIVER / CARAVAN / MIXED"
    ),
    involves_slavery: bool | None = Query(
        None, description="ETHICS-010: filtra rotte che trafficavano esseri umani"
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
    summary="Enumera i tipi di rotta",
    description="Restituisce l'enum RouteType con breve descrizione.",
)
def list_route_types(response: Response):
    response.headers["Cache-Control"] = "public, max-age=86400"
    descriptions = {
        "LAND": "Rotta terrestre (strade, sentieri).",
        "SEA": "Rotta marittima oceanica.",
        "RIVER": "Rotta fluviale interna.",
        "CARAVAN": "Rotta carovaniera (cammelli, yak) con caravanserragli.",
        "MIXED": "Combinazione di più modalità.",
    }
    return {
        "route_types": [
            {"type": t.value, "description": descriptions.get(t.value, "")}
            for t in RouteType
        ],
    }


@router.get(
    "/v1/routes/{route_id}",
    summary="Dettaglio rotta commerciale",
    description=(
        "Dettaglio completo con geometria GeoJSON, commodities, waypoints "
        "ordinati e sources. ETHICS-010: `ethical_notes` esplicita scala e "
        "main_actors per le rotte schiaviste."
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
