"""Endpoint di esportazione dati.

GET /v1/export/geojson               FeatureCollection GeoJSON entities
GET /v1/export/csv                   CSV tabellare entities
GET /v1/export/timeline              Timeline JSON per visualizzazione

v6.48 — export GeoJSON per tutti i resource types puntuali:
GET /v1/export/sites.geojson         archaeological sites (Point geometry)
GET /v1/export/rulers.geojson        rulers con posizione via entity.capital
GET /v1/export/languages.geojson     languages con center_lat/lon
"""

import csv
import io
import json
import logging

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session, joinedload

from src.db.database import get_db
from src.db.models import ArchaeologicalSite, GeoEntity, HistoricalLanguage, HistoricalRuler
# v6.66.0 (audit #security): export endpoint pesanti, limite stretto 10/min
from src.middleware.rate_limit import RATE_LIMIT_EXPORT, limiter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["esportazione"])


@router.get(
    "/v1/export/geojson",
    summary="Esporta tutte le entità come GeoJSON FeatureCollection",
    description=(
        "Standard GeoJSON — importabile in QGIS, Leaflet, Mapbox, etc. "
        "Usa `geometry=none` per esportare solo le proprieta' (molto piu' veloce) "
        "o `geometry=centroid` per esportare solo le capitali come Point."
    ),
)
@limiter.limit(RATE_LIMIT_EXPORT)
def export_geojson(
    request: Request,
    response: Response,  # v6.66: richiesto da slowapi con headers_enabled=True
    year: int | None = Query(None, ge=-4000, le=2100),
    geometry: str = Query(
        "full",
        pattern="^(full|centroid|none)$",
        description="full = poligoni completi (default); centroid = Point capitali; none = solo properties",
    ),
    db: Session = Depends(get_db),
):
    q = db.query(GeoEntity)

    if year is not None:
        from sqlalchemy import or_
        q = q.filter(GeoEntity.year_start <= year)
        q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))

    # PERF: costruiamo il JSON a mano per evitare json.loads + json.dumps
    # sulle MultiPolygon (che sono gia' stringhe JSON valide nel DB).
    # Con 700+ boundary MultiPolygon il risparmio e' dell'ordine di secondi.
    buf = io.StringIO()
    buf.write('{"type":"FeatureCollection","features":[')
    first = True
    for e in q.all():
        if not first:
            buf.write(",")
        first = False

        # Properties — piccole, jsonifichiamo normalmente
        props = {
            "name_original": e.name_original,
            "name_original_lang": e.name_original_lang,
            "entity_type": e.entity_type,
            "year_start": e.year_start,
            "year_end": e.year_end,
            "status": e.status,
            "confidence_score": e.confidence_score,
        }
        props_json = json.dumps(props, ensure_ascii=False)

        # Geometry — in base alla modalita' richiesta
        if geometry == "none":
            geom_json = "null"
        elif geometry == "centroid":
            if e.capital_lat is not None and e.capital_lon is not None:
                geom_json = (
                    '{"type":"Point","coordinates":['
                    f'{e.capital_lon},{e.capital_lat}]}}'
                )
            else:
                geom_json = "null"
        else:  # full
            if e.boundary_geojson:
                # E' gia' una stringa JSON valida nel DB: embed direttamente.
                geom_json = e.boundary_geojson
            else:
                geom_json = "null"

        buf.write(
            f'{{"type":"Feature","id":{e.id},'
            f'"geometry":{geom_json},"properties":{props_json}}}'
        )
    buf.write("]}")

    return Response(
        content=buf.getvalue(),
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
@limiter.limit(RATE_LIMIT_EXPORT)
def export_csv(
    request: Request,
    response: Response,  # v6.66: richiesto da slowapi con headers_enabled=True
    db: Session = Depends(get_db),
):
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
@limiter.limit(RATE_LIMIT_EXPORT)
def export_timeline(
    request: Request,
    response: Response,  # v6.66: richiesto da slowapi con headers_enabled=True
    db: Session = Depends(get_db),
):
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


# ─── v6.48: GeoJSON export per resource types puntuali ──────────────

def _safe_json(raw: str | None) -> list | dict | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


@router.get(
    "/v1/export/sites.geojson",
    summary="Export archaeological sites as GeoJSON FeatureCollection",
    description=(
        "Standard GeoJSON Points per tutti i siti archeologici / UNESCO. "
        "Compatibile con QGIS, Leaflet, Mapbox, D3. Filtro opzionale "
        "`year` (siti con documentata attivita' in quell'anno)."
    ),
)
@limiter.limit(RATE_LIMIT_EXPORT)
def export_sites_geojson(
    request: Request,
    response: Response,  # v6.66: richiesto da slowapi con headers_enabled=True
    year: int | None = Query(None, ge=-10000, le=2100),
    unesco_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    q = db.query(ArchaeologicalSite)
    if year is not None:
        from sqlalchemy import or_
        q = q.filter(or_(ArchaeologicalSite.date_start.is_(None), ArchaeologicalSite.date_start <= year))
        q = q.filter(or_(ArchaeologicalSite.date_end.is_(None), ArchaeologicalSite.date_end >= year))
    if unesco_only:
        q = q.filter(ArchaeologicalSite.unesco_id.isnot(None))

    sites = q.all()
    features = []
    for s in sites:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [s.longitude, s.latitude]},
            "properties": {
                "id": s.id,
                "name_original": s.name_original,
                "name_original_lang": s.name_original_lang,
                "site_type": s.site_type,
                "date_start": s.date_start,
                "date_end": s.date_end,
                "unesco_id": s.unesco_id,
                "unesco_year": s.unesco_year,
                "entity_id": s.entity_id,
                "confidence_score": s.confidence_score,
                "status": s.status,
                "description": s.description,
                "ethical_notes": s.ethical_notes,
                "sources": _safe_json(s.sources),
                "name_variants": _safe_json(s.name_variants),
            },
        })

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {"count": len(features), "source": "AtlasPI /v1/export/sites.geojson"},
    }


@router.get(
    "/v1/export/rulers.geojson",
    summary="Export historical rulers as GeoJSON",
    description=(
        "GeoJSON Points per rulers — geometry derivata da capitale dell'entita' "
        "governata (se `entity_id` risolvibile). Per rulers senza entita' mappata, "
        "geometry = null (feature incluso per completezza). Filtro `year` per "
        "rulers in carica in quell'anno."
    ),
)
@limiter.limit(RATE_LIMIT_EXPORT)
def export_rulers_geojson(
    request: Request,
    year: int | None = Query(None, ge=-5000, le=2100),
    region: str | None = Query(None, max_length=50),
    db: Session = Depends(get_db),
):
    q = db.query(HistoricalRuler).outerjoin(GeoEntity, HistoricalRuler.entity_id == GeoEntity.id)
    if year is not None:
        from sqlalchemy import or_
        q = q.filter(or_(HistoricalRuler.reign_start.is_(None), HistoricalRuler.reign_start <= year))
        q = q.filter(or_(HistoricalRuler.reign_end.is_(None), HistoricalRuler.reign_end >= year))
    if region:
        q = q.filter(HistoricalRuler.region == region)

    rulers = q.all()
    features = []
    for r in rulers:
        # Derive geometry from entity capital if available.
        geometry = None
        if r.entity and r.entity.capital_lat is not None and r.entity.capital_lon is not None:
            geometry = {
                "type": "Point",
                "coordinates": [r.entity.capital_lon, r.entity.capital_lat],
            }
        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": r.id,
                "name_original": r.name_original,
                "name_original_lang": r.name_original_lang,
                "name_regnal": r.name_regnal,
                "title": r.title,
                "region": r.region,
                "dynasty": r.dynasty,
                "birth_year": r.birth_year,
                "death_year": r.death_year,
                "reign_start": r.reign_start,
                "reign_end": r.reign_end,
                "entity_id": r.entity_id,
                "entity_name_fallback": r.entity_name_fallback,
                "confidence_score": r.confidence_score,
                "status": r.status,
                "description": r.description,
                "ethical_notes": r.ethical_notes,
                "sources": _safe_json(r.sources),
                "name_variants": _safe_json(r.name_variants),
                "notable_events": _safe_json(r.notable_events),
            },
        })

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "count": len(features),
            "with_geometry": sum(1 for f in features if f["geometry"] is not None),
            "source": "AtlasPI /v1/export/rulers.geojson",
        },
    }


@router.get(
    "/v1/export/languages.geojson",
    summary="Export historical languages as GeoJSON",
    description=(
        "GeoJSON Points usando `center_lat/center_lon`. Filtro opzionale "
        "per year (lingue parlate in quell'anno), family, vitality_status."
    ),
)
@limiter.limit(RATE_LIMIT_EXPORT)
def export_languages_geojson(
    request: Request,
    year: int | None = Query(None, ge=-10000, le=2100),
    family: str | None = Query(None, max_length=100),
    vitality_status: str | None = Query(None, max_length=30),
    db: Session = Depends(get_db),
):
    q = db.query(HistoricalLanguage)
    if year is not None:
        from sqlalchemy import or_
        q = q.filter(or_(HistoricalLanguage.period_start.is_(None), HistoricalLanguage.period_start <= year))
        q = q.filter(or_(HistoricalLanguage.period_end.is_(None), HistoricalLanguage.period_end >= year))
    if family:
        q = q.filter(HistoricalLanguage.family.ilike(f"%{family}%"))
    if vitality_status:
        q = q.filter(HistoricalLanguage.vitality_status == vitality_status)

    langs = q.all()
    features = []
    for l in langs:
        geometry = None
        if l.center_lat is not None and l.center_lon is not None:
            geometry = {
                "type": "Point",
                "coordinates": [l.center_lon, l.center_lat],
            }
        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": l.id,
                "name_original": l.name_original,
                "name_original_lang": l.name_original_lang,
                "iso_code": l.iso_code,
                "family": l.family,
                "script": l.script,
                "region_name": l.region_name,
                "period_start": l.period_start,
                "period_end": l.period_end,
                "vitality_status": l.vitality_status,
                "confidence_score": l.confidence_score,
                "status": l.status,
                "description": l.description,
                "ethical_notes": l.ethical_notes,
                "sources": _safe_json(l.sources),
                "name_variants": _safe_json(l.name_variants),
            },
        })

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "count": len(features),
            "with_geometry": sum(1 for f in features if f["geometry"] is not None),
            "source": "AtlasPI /v1/export/languages.geojson",
        },
    }
