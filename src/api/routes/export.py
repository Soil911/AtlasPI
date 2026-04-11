"""Endpoint di esportazione dati.

GET /v1/export/geojson    FeatureCollection GeoJSON
GET /v1/export/csv        CSV tabellare
GET /v1/export/timeline   Timeline JSON per visualizzazione
"""

import csv
import io
import json
import logging

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session, joinedload

from src.db.database import get_db
from src.db.models import GeoEntity

logger = logging.getLogger(__name__)

router = APIRouter(tags=["esportazione"])


@router.get(
    "/v1/export/geojson",
    summary="Esporta tutte le entità come GeoJSON FeatureCollection",
    description="Standard GeoJSON — importabile in QGIS, Leaflet, Mapbox, etc.",
)
def export_geojson(
    year: int | None = Query(None, ge=-4000, le=2100),
    db: Session = Depends(get_db),
):
    q = db.query(GeoEntity).options(joinedload(GeoEntity.name_variants))

    if year is not None:
        from sqlalchemy import or_
        q = q.filter(GeoEntity.year_start <= year)
        q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))

    features = []
    for e in q.all():
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
            },
        })

    collection = {"type": "FeatureCollection", "features": features}
    return Response(
        content=json.dumps(collection, ensure_ascii=False),
        media_type="application/geo+json",
        headers={
            "Content-Disposition": "attachment; filename=atlaspi_entities.geojson",
            "Cache-Control": "public, max-age=3600",
        },
    )


@router.get(
    "/v1/export/csv",
    summary="Esporta entità come CSV",
    description="CSV tabellare per analisi in Excel, Pandas, R.",
)
def export_csv(db: Session = Depends(get_db)):
    entities = db.query(GeoEntity).order_by(GeoEntity.year_start).all()

    output = io.StringIO()
    writer = csv.writer(output)
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
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=atlaspi_entities.csv",
        },
    )


@router.get(
    "/v1/export/timeline",
    summary="Dati per visualizzazione timeline",
    description="JSON ottimizzato per rendering timeline interattiva.",
)
def export_timeline(db: Session = Depends(get_db)):
    entities = (
        db.query(GeoEntity)
        .order_by(GeoEntity.year_start)
        .all()
    )

    items = []
    for e in entities:
        items.append({
            "id": e.id,
            "name": e.name_original,
            "type": e.entity_type,
            "start": e.year_start,
            "end": e.year_end,
            "status": e.status,
            "confidence": e.confidence_score,
        })

    return {
        "count": len(items),
        "min_year": min(i["start"] for i in items) if items else 0,
        "max_year": max(i["end"] or 2025 for i in items) if items else 2025,
        "items": items,
    }
