"""Endpoint per siti archeologici / culturali — v6.37.

I siti sono luoghi materiali discreti (rovine, monumenti, siti UNESCO)
distinti dalle `GeoEntity` (stati) e dalle `HistoricalCity` (centri urbani).

GET /v1/sites                           list paginated con filtri
GET /v1/sites/types                     enum SiteType
GET /v1/sites/unesco                    solo siti UNESCO
GET /v1/sites/nearby?lat=&lon=&radius=  nearby geographic
GET /v1/sites/{id}                      detail

ETHICS-009-analogy: nome originale primario (es. "Uluru", non "Ayers
Rock"); nomi coloniali in name_variants. ethical_notes esplicita
danneggiamenti storici (Bamiyan Buddhas, Palmyra ISIS) e ritorni
indigeni (Uluru Climbing Ban 2019).
"""

import json
import logging
import math
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from src.cache import cache_response
from src.db.database import get_db
from src.db.models import ArchaeologicalSite, GeoEntity

logger = logging.getLogger(__name__)

router = APIRouter(tags=["siti archeologici"])


# ─── Response helpers ──────────────────────────────────────────────

def _site_to_dict(site: ArchaeologicalSite) -> dict:
    """Serializza un sito in dict JSON-ready."""
    try:
        sources = json.loads(site.sources) if site.sources else []
    except (json.JSONDecodeError, TypeError):
        sources = []
    try:
        name_variants = json.loads(site.name_variants) if site.name_variants else []
    except (json.JSONDecodeError, TypeError):
        name_variants = []

    return {
        "id": site.id,
        "name_original": site.name_original,
        "name_original_lang": site.name_original_lang,
        "latitude": site.latitude,
        "longitude": site.longitude,
        "date_start": site.date_start,
        "date_end": site.date_end,
        "site_type": site.site_type,
        "description": site.description,
        "unesco_id": site.unesco_id,
        "unesco_year": site.unesco_year,
        "entity_id": site.entity_id,
        "confidence_score": site.confidence_score,
        "status": site.status,
        "ethical_notes": site.ethical_notes,
        "sources": sources,
        "name_variants": name_variants,
    }


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distanza haversine (km) tra due coppie (lat, lon) WGS84."""
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    )
    return r * 2 * math.asin(math.sqrt(a))


# ─── Endpoints ──────────────────────────────────────────────────────

@router.get(
    "/v1/sites",
    summary="List archaeological / cultural sites (paginated)",
    description=(
        "Returns a paginated list of archaeological sites and historical "
        "monuments (UNESCO World Heritage, ruins, sacred sites, ancient "
        "cities, pyramids, etc.). Distinct from `/v1/entities` (political "
        "states) and `/v1/cities` (urban centers with political life).\n\n"
        "**Filters** (all optional):\n"
        "- `year` — sites with documented use in this year (date_start <= Y <= date_end)\n"
        "- `site_type` — ruins, monument, temple, pyramid, sacred_site, etc.\n"
        "- `entity_id` — sites belonging to a specific historical entity\n"
        "- `unesco_only=true` — only UNESCO World Heritage Sites\n"
        "- `status` — confirmed, uncertain, disputed\n\n"
        "**For AI agents**: use alongside `/v1/entities/{id}/sites` (not yet "
        "available) to discover material heritage within a historical entity."
    ),
)
@cache_response(ttl_seconds=3600)
def list_sites(
    request: Request,
    response: Response,
    year: int | None = Query(None, ge=-10000, le=2100, description="Site active in this year"),
    site_type: str | None = Query(None, max_length=50),
    entity_id: int | None = Query(None, ge=1),
    unesco_only: bool = Query(False, description="Filter to only UNESCO sites"),
    status: Literal["confirmed", "uncertain", "disputed"] | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(ArchaeologicalSite)

    if year is not None:
        q = q.filter(
            or_(ArchaeologicalSite.date_start.is_(None), ArchaeologicalSite.date_start <= year)
        )
        q = q.filter(
            or_(ArchaeologicalSite.date_end.is_(None), ArchaeologicalSite.date_end >= year)
        )
    if site_type:
        q = q.filter(ArchaeologicalSite.site_type == site_type)
    if entity_id is not None:
        q = q.filter(ArchaeologicalSite.entity_id == entity_id)
    if unesco_only:
        q = q.filter(ArchaeologicalSite.unesco_id.isnot(None))
    if status:
        q = q.filter(ArchaeologicalSite.status == status)

    total = q.count()
    sites = q.order_by(ArchaeologicalSite.name_original).offset(offset).limit(limit).all()

    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "sites": [_site_to_dict(s) for s in sites],
    }


@router.get(
    "/v1/sites/types",
    summary="List site types with counts",
    description="Enum of SiteType values with count of sites per type.",
)
def site_types(db: Session = Depends(get_db)):
    rows = (
        db.query(ArchaeologicalSite.site_type, func.count(ArchaeologicalSite.id))
        .group_by(ArchaeologicalSite.site_type)
        .order_by(desc(func.count(ArchaeologicalSite.id)))
        .all()
    )
    return [{"site_type": t, "count": c} for t, c in rows]


@router.get(
    "/v1/sites/unesco",
    summary="UNESCO World Heritage Sites only",
    description=(
        "Shortcut for `/v1/sites?unesco_only=true`. Returns all sites with a "
        "non-null `unesco_id`, ordered by inscription year descending."
    ),
)
@cache_response(ttl_seconds=3600)
def unesco_sites(
    request: Request,
    response: Response,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(ArchaeologicalSite).filter(ArchaeologicalSite.unesco_id.isnot(None))
    total = q.count()
    sites = (
        q.order_by(desc(ArchaeologicalSite.unesco_year), ArchaeologicalSite.name_original)
        .offset(offset).limit(limit).all()
    )
    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "sites": [_site_to_dict(s) for s in sites],
    }


@router.get(
    "/v1/sites/nearby",
    summary="Archaeological sites near coordinates",
    description=(
        "Find archaeological / cultural sites within `radius` km of a lat/lon "
        "point. Ordered by distance. Python haversine (dev/SQLite) — PostGIS "
        "native `ST_DWithin` in prod adds minimal speedup since sites are "
        "point-located (no polygon complexity)."
    ),
)
def sites_nearby(
    response: Response,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(50, ge=1, le=5000, description="Radius in km"),
    site_type: str | None = Query(None, max_length=50),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(ArchaeologicalSite)
    if site_type:
        q = q.filter(ArchaeologicalSite.site_type == site_type)
    sites = q.all()

    scored = []
    for s in sites:
        dist = _haversine_km(lat, lon, s.latitude, s.longitude)
        if dist <= radius:
            scored.append((s, round(dist, 1)))
    scored.sort(key=lambda x: x[1])
    top = scored[:limit]

    response.headers["Cache-Control"] = "public, max-age=3600"
    return {
        "query": {"lat": lat, "lon": lon, "radius_km": radius, "site_type": site_type},
        "count": len(top),
        "sites": [
            {**_site_to_dict(s), "distance_km": d} for s, d in top
        ],
    }


@router.get(
    "/v1/sites/{site_id}",
    summary="Site detail",
    description="Full detail for a single archaeological site by numeric ID.",
)
@cache_response(ttl_seconds=3600)
def get_site(
    site_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    site = db.query(ArchaeologicalSite).filter(ArchaeologicalSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail=f"Site {site_id} not found")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return _site_to_dict(site)
