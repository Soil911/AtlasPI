"""Advanced Search + Data Export — v6.19.

GET /search                              Interactive search page (HTML)
GET /v1/search/advanced?q=...            Unified search across all data types
GET /v1/export/entities?format=csv       Entities export (CSV/GeoJSON)
GET /v1/export/events?format=csv         Events export (CSV/JSON)

The unified search searches across entities (name_original, name_variants),
events (name_original, description), cities (name_original), and trade routes
(name_original). Results are ranked by relevance: exact match > starts with >
contains.

NOTE: The existing /v1/search (autocomplete) and /v1/export/* endpoints are
preserved in their original files. This module adds /v1/search/advanced as the
new unified cross-type search, and extends export with format and filter support.
"""

from __future__ import annotations

import csv
import io
import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.cache import cache_response
from src.db.database import get_db
from src.db.models import (
    GeoEntity,
    HistoricalCity,
    HistoricalEvent,
    NameVariant,
    TradeRoute,
)

logger = logging.getLogger(__name__)

router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static"

# ─── Search page ──────────────────────────────────────────────────


@router.get("/search", include_in_schema=False)
async def serve_search_page():
    """Serve the advanced search interactive page."""
    return FileResponse(STATIC_DIR / "search" / "index.html")


# ─── Unified search API ──────────────────────────────────────────


def _score_match(query_lower: str, text: str | None) -> float:
    """Score a match between query and text for relevance ranking.

    Scoring: exact match = 1.0, starts with = 0.9, contains = 0.7.
    """
    if not text:
        return 0.0
    text_lower = text.lower()
    if text_lower == query_lower:
        return 1.0
    if text_lower.startswith(query_lower):
        return 0.9
    if query_lower in text_lower:
        return 0.7
    return 0.0


def _highlight(text: str, query: str) -> str:
    """Produce a highlight snippet showing query in context."""
    if not text or not query:
        return text or ""
    idx = text.lower().find(query.lower())
    if idx == -1:
        return text[:200]
    start = max(0, idx - 40)
    end = min(len(text), idx + len(query) + 40)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


@router.get(
    "/v1/search/advanced",
    summary="Unified search across all data types",
    tags=["ricerca"],
    description=(
        "Searches entities, events, cities, and trade routes in a single query. "
        "Results are ranked by relevance (exact match > starts with > contains). "
        "Supports optional filters: type (entity_type), year_min, year_max, "
        "status, confidence_min, confidence_max, data_type (entity/event/city/route)."
    ),
)
@cache_response(ttl_seconds=120)
def advanced_search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=300, description="Search query"),
    data_type: str | None = Query(
        None,
        description="Filter by data type: entity, event, city, route (or comma-separated)",
    ),
    entity_type: str | None = Query(
        None,
        description="Filter entities by entity_type (empire, kingdom, etc.)",
    ),
    year_min: int | None = Query(None, description="Minimum year (inclusive)"),
    year_max: int | None = Query(None, description="Maximum year (inclusive)"),
    status: str | None = Query(None, description="Filter by status (confirmed/uncertain/disputed)"),
    confidence_min: float | None = Query(None, ge=0.0, le=1.0, description="Minimum confidence score"),
    confidence_max: float | None = Query(None, ge=0.0, le=1.0, description="Maximum confidence score"),
    sort: str = Query(
        "relevance",
        description="Sort by: relevance, name, year, confidence",
    ),
    limit: int = Query(30, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    response: Response = None,
    db: Session = Depends(get_db),
):
    q_lower = q.strip().lower()
    pattern = f"%{q_lower}%"

    # Parse requested data types
    allowed_types = {"entity", "event", "city", "route"}
    if data_type:
        requested = {t.strip().lower() for t in data_type.split(",")}
        requested = requested & allowed_types
    else:
        requested = allowed_types

    results: list[dict] = []

    # --- Entities ---
    if "entity" in requested:
        eq = db.query(GeoEntity)
        variant_ids = select(NameVariant.entity_id).where(NameVariant.name.ilike(pattern))
        eq = eq.filter(
            or_(GeoEntity.name_original.ilike(pattern), GeoEntity.id.in_(variant_ids))
        )
        if entity_type:
            eq = eq.filter(GeoEntity.entity_type == entity_type)
        if year_min is not None:
            eq = eq.filter(GeoEntity.year_start >= year_min)
        if year_max is not None:
            eq = eq.filter(
                or_(GeoEntity.year_end.is_(None), GeoEntity.year_end <= year_max)
            )
        if status:
            eq = eq.filter(GeoEntity.status == status)
        if confidence_min is not None:
            eq = eq.filter(GeoEntity.confidence_score >= confidence_min)
        if confidence_max is not None:
            eq = eq.filter(GeoEntity.confidence_score <= confidence_max)

        for e in eq.all():
            score = _score_match(q_lower, e.name_original)
            # Also check name variants for better score
            variants = db.query(NameVariant).filter(NameVariant.entity_id == e.id).all()
            for v in variants:
                vs = _score_match(q_lower, v.name)
                if vs > score:
                    score = vs
            if score == 0:
                score = 0.5  # matched via ILIKE but not direct scoring

            results.append({
                "type": "entity",
                "id": e.id,
                "name": e.name_original,
                "name_lang": e.name_original_lang,
                "subtype": e.entity_type,
                "year_start": e.year_start,
                "year_end": e.year_end,
                "status": e.status,
                "confidence_score": e.confidence_score,
                "score": round(score, 4),
                "highlight": _highlight(e.name_original, q),
            })

    # --- Events ---
    if "event" in requested:
        evq = db.query(HistoricalEvent)
        evq = evq.filter(
            or_(
                HistoricalEvent.name_original.ilike(pattern),
                HistoricalEvent.description.ilike(pattern),
            )
        )
        if year_min is not None:
            evq = evq.filter(HistoricalEvent.year >= year_min)
        if year_max is not None:
            evq = evq.filter(HistoricalEvent.year <= year_max)
        if status:
            evq = evq.filter(HistoricalEvent.status == status)
        if confidence_min is not None:
            evq = evq.filter(HistoricalEvent.confidence_score >= confidence_min)
        if confidence_max is not None:
            evq = evq.filter(HistoricalEvent.confidence_score <= confidence_max)

        for ev in evq.all():
            name_score = _score_match(q_lower, ev.name_original)
            desc_score = _score_match(q_lower, ev.description) * 0.8  # description matches rank lower
            score = max(name_score, desc_score)
            if score == 0:
                score = 0.5

            hl = _highlight(ev.name_original, q)
            if name_score < desc_score:
                hl = _highlight(ev.description, q)

            results.append({
                "type": "event",
                "id": ev.id,
                "name": ev.name_original,
                "name_lang": ev.name_original_lang,
                "subtype": ev.event_type,
                "year_start": ev.year,
                "year_end": ev.year_end,
                "status": ev.status,
                "confidence_score": ev.confidence_score,
                "score": round(score, 4),
                "highlight": hl,
            })

    # --- Cities ---
    if "city" in requested:
        cq = db.query(HistoricalCity)
        cq = cq.filter(HistoricalCity.name_original.ilike(pattern))
        if year_min is not None:
            cq = cq.filter(
                or_(HistoricalCity.founded_year.is_(None), HistoricalCity.founded_year >= year_min)
            )
        if year_max is not None:
            cq = cq.filter(
                or_(HistoricalCity.abandoned_year.is_(None), HistoricalCity.abandoned_year <= year_max)
            )
        if status:
            cq = cq.filter(HistoricalCity.status == status)
        if confidence_min is not None:
            cq = cq.filter(HistoricalCity.confidence_score >= confidence_min)
        if confidence_max is not None:
            cq = cq.filter(HistoricalCity.confidence_score <= confidence_max)

        for c in cq.all():
            score = _score_match(q_lower, c.name_original)
            if score == 0:
                score = 0.5

            results.append({
                "type": "city",
                "id": c.id,
                "name": c.name_original,
                "name_lang": c.name_original_lang,
                "subtype": c.city_type,
                "year_start": c.founded_year,
                "year_end": c.abandoned_year,
                "status": c.status,
                "confidence_score": c.confidence_score,
                "score": round(score, 4),
                "highlight": _highlight(c.name_original, q),
            })

    # --- Trade Routes ---
    if "route" in requested:
        rq = db.query(TradeRoute)
        rq = rq.filter(TradeRoute.name_original.ilike(pattern))
        if year_min is not None:
            rq = rq.filter(
                or_(TradeRoute.start_year.is_(None), TradeRoute.start_year >= year_min)
            )
        if year_max is not None:
            rq = rq.filter(
                or_(TradeRoute.end_year.is_(None), TradeRoute.end_year <= year_max)
            )
        if status:
            rq = rq.filter(TradeRoute.status == status)
        if confidence_min is not None:
            rq = rq.filter(TradeRoute.confidence_score >= confidence_min)
        if confidence_max is not None:
            rq = rq.filter(TradeRoute.confidence_score <= confidence_max)

        for r in rq.all():
            score = _score_match(q_lower, r.name_original)
            if score == 0:
                score = 0.5

            results.append({
                "type": "route",
                "id": r.id,
                "name": r.name_original,
                "name_lang": r.name_original_lang,
                "subtype": r.route_type,
                "year_start": r.start_year,
                "year_end": r.end_year,
                "status": r.status,
                "confidence_score": r.confidence_score,
                "score": round(score, 4),
                "highlight": _highlight(r.name_original, q),
            })

    # --- Sort ---
    if sort == "name":
        results.sort(key=lambda x: (x["name"] or "").lower())
    elif sort == "year":
        results.sort(key=lambda x: x.get("year_start") or 0)
    elif sort == "confidence":
        results.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)
    else:  # relevance (default)
        results.sort(key=lambda x: x["score"], reverse=True)

    total = len(results)
    paged = results[offset : offset + limit]

    if response:
        response.headers["Cache-Control"] = "public, max-age=300"

    return {
        "query": q,
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": paged,
    }


# ─── Enhanced Exports ─────────────────────────────────────────────

_UTF8_BOM = "\ufeff"
_MAX_EXPORT_ROWS = 1000


@router.get(
    "/v1/export/entities",
    summary="Export entities as CSV or GeoJSON",
    tags=["esportazione"],
    description=(
        "Export entities with filters. Formats: csv (UTF-8 with BOM for Excel), "
        "geojson (FeatureCollection). Max 1000 rows per export."
    ),
)
def export_entities(
    format: str = Query("csv", description="Export format: csv or geojson"),
    entity_type: str | None = Query(None, description="Filter by entity_type"),
    year_min: int | None = Query(None, description="Minimum year_start"),
    year_max: int | None = Query(None, description="Maximum year_start"),
    status: str | None = Query(None, description="Filter by status"),
    confidence_min: float | None = Query(None, ge=0.0, le=1.0),
    confidence_max: float | None = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    q = db.query(GeoEntity)

    if entity_type:
        q = q.filter(GeoEntity.entity_type == entity_type)
    if year_min is not None:
        q = q.filter(GeoEntity.year_start >= year_min)
    if year_max is not None:
        q = q.filter(GeoEntity.year_start <= year_max)
    if status:
        q = q.filter(GeoEntity.status == status)
    if confidence_min is not None:
        q = q.filter(GeoEntity.confidence_score >= confidence_min)
    if confidence_max is not None:
        q = q.filter(GeoEntity.confidence_score <= confidence_max)

    entities = q.order_by(GeoEntity.year_start).limit(_MAX_EXPORT_ROWS).all()

    if format == "geojson":
        features = []
        for e in entities:
            geom = None
            if e.boundary_geojson:
                try:
                    geom = json.loads(e.boundary_geojson)
                except (json.JSONDecodeError, TypeError):
                    pass
            features.append({
                "type": "Feature",
                "id": e.id,
                "geometry": geom,
                "properties": {
                    "name_original": e.name_original,
                    "name_original_lang": e.name_original_lang,
                    "entity_type": e.entity_type,
                    "year_start": e.year_start,
                    "year_end": e.year_end,
                    "status": e.status,
                    "confidence_score": e.confidence_score,
                    "capital_name": e.capital_name,
                },
            })

        geojson_str = json.dumps(
            {"type": "FeatureCollection", "features": features},
            ensure_ascii=False,
        )
        return Response(
            content=geojson_str,
            media_type="application/geo+json",
            headers={
                "Content-Disposition": "attachment; filename=atlaspi_entities.geojson",
            },
        )

    # Default: CSV
    buf = io.StringIO()
    buf.write(_UTF8_BOM)
    writer = csv.writer(buf)
    writer.writerow([
        "id", "name_original", "name_original_lang", "entity_type",
        "year_start", "year_end", "status", "confidence_score",
        "capital_name", "capital_lat", "capital_lon", "ethical_notes",
    ])
    for e in entities:
        writer.writerow([
            e.id, e.name_original, e.name_original_lang, e.entity_type,
            e.year_start, e.year_end or "", e.status, e.confidence_score,
            e.capital_name or "", e.capital_lat or "", e.capital_lon or "",
            (e.ethical_notes or "")[:200],
        ])

    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=atlaspi_entities.csv",
        },
    )


@router.get(
    "/v1/export/events",
    summary="Export events as CSV or JSON",
    tags=["esportazione"],
    description=(
        "Export historical events with filters. Formats: csv (UTF-8 with BOM), "
        "json (JSON array). Max 1000 rows per export."
    ),
)
def export_events(
    format: str = Query("csv", description="Export format: csv or json"),
    event_type: str | None = Query(None, description="Filter by event_type"),
    year_min: int | None = Query(None, description="Minimum year"),
    year_max: int | None = Query(None, description="Maximum year"),
    status: str | None = Query(None, description="Filter by status"),
    confidence_min: float | None = Query(None, ge=0.0, le=1.0),
    confidence_max: float | None = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    q = db.query(HistoricalEvent)

    if event_type:
        q = q.filter(HistoricalEvent.event_type == event_type)
    if year_min is not None:
        q = q.filter(HistoricalEvent.year >= year_min)
    if year_max is not None:
        q = q.filter(HistoricalEvent.year <= year_max)
    if status:
        q = q.filter(HistoricalEvent.status == status)
    if confidence_min is not None:
        q = q.filter(HistoricalEvent.confidence_score >= confidence_min)
    if confidence_max is not None:
        q = q.filter(HistoricalEvent.confidence_score <= confidence_max)

    events = q.order_by(HistoricalEvent.year).limit(_MAX_EXPORT_ROWS).all()

    if format == "json":
        items = []
        for ev in events:
            items.append({
                "id": ev.id,
                "name_original": ev.name_original,
                "name_original_lang": ev.name_original_lang,
                "event_type": ev.event_type,
                "year": ev.year,
                "year_end": ev.year_end,
                "month": ev.month,
                "day": ev.day,
                "location_name": ev.location_name,
                "main_actor": ev.main_actor,
                "description": ev.description,
                "status": ev.status,
                "confidence_score": ev.confidence_score,
            })
        return Response(
            content=json.dumps(items, ensure_ascii=False, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=atlaspi_events.json",
            },
        )

    # Default: CSV
    buf = io.StringIO()
    buf.write(_UTF8_BOM)
    writer = csv.writer(buf)
    writer.writerow([
        "id", "name_original", "name_original_lang", "event_type",
        "year", "year_end", "month", "day", "location_name",
        "main_actor", "status", "confidence_score", "description",
    ])
    for ev in events:
        writer.writerow([
            ev.id, ev.name_original, ev.name_original_lang, ev.event_type,
            ev.year, ev.year_end or "", ev.month or "", ev.day or "",
            ev.location_name or "", ev.main_actor or "", ev.status,
            ev.confidence_score, (ev.description or "")[:300],
        ])

    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=atlaspi_events.csv",
        },
    )
