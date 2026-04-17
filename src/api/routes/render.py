"""v6.39: server-side PNG map rendering.

Rende gli entity boundaries come PNG statico, utile per:
- AI agents che vogliono inserire un'immagine in chat
- Embedding diretto in email, PDF, Slack
- Thumbnails per social sharing (Open Graph)

Uso matplotlib con backend 'Agg' (no GUI). Cached via Redis per year.

GET /v1/render/snapshot/{year}.png     world map in quell'anno
GET /v1/render/entity/{id}.png         singola entity boundary
"""

import io
import json
import logging

import matplotlib
matplotlib.use("Agg")  # Non-GUI backend for server-side rendering
import matplotlib.pyplot as plt
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response as FastAPIResponse
from shapely.errors import GEOSException
from shapely.geometry import shape as shapely_shape
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.cache import cache_response
from src.db.database import get_db
from src.db.models import GeoEntity

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rendering"])


# ─── Color palette ─────────────────────────────────────────────────

_STATUS_COLORS = {
    "confirmed": "#58a6ff",   # blue (matches frontend)
    "uncertain": "#fbca04",   # yellow
    "disputed": "#f85149",    # red
}


def _draw_geom(ax, geom, color: str, alpha: float = 0.65):
    """Disegna un shapely geometry su matplotlib Axes.

    Gestisce Polygon, MultiPolygon, Point. Se geometry invalido, skip.
    """
    try:
        if geom.geom_type == "Polygon":
            xs, ys = geom.exterior.xy
            ax.fill(xs, ys, facecolor=color, edgecolor="white", linewidth=0.3, alpha=alpha)
            for interior in geom.interiors:
                ix, iy = interior.xy
                ax.fill(ix, iy, facecolor="white", alpha=1.0)
        elif geom.geom_type == "MultiPolygon":
            for poly in geom.geoms:
                _draw_geom(ax, poly, color, alpha)
        elif geom.geom_type == "Point":
            ax.plot(geom.x, geom.y, "o", markersize=4, color=color, alpha=alpha)
    except (GEOSException, ValueError, AttributeError):
        # Skip malformed geometry silently
        pass


# ─── Endpoints ──────────────────────────────────────────────────────

@router.get(
    "/v1/render/snapshot/{year}.png",
    summary="Render PNG del mondo in un dato anno",
    description=(
        "Returns a PNG image showing all historical entities active in "
        "the given year, with boundaries colored by status (confirmed/"
        "uncertain/disputed).\n\n"
        "**Primary use case**: AI agents that want to insert a visual "
        "into chat ('show me Europe in 800 CE'). Also useful for "
        "social sharing thumbnails (Open Graph) and PDF reports.\n\n"
        "**Backend**: matplotlib with 'Agg' backend (no GUI). Cached 1h."
    ),
)
def render_snapshot_png(
    year: int,
    request: Request,
    width: int = Query(1200, ge=200, le=3000, description="Image width in pixels"),
    height: int = Query(600, ge=100, le=2000, description="Image height in pixels"),
    title: str | None = Query(None, max_length=200, description="Optional title override"),
    db: Session = Depends(get_db),
):
    if year < -5000 or year > 2100:
        raise HTTPException(status_code=400, detail=f"year {year} out of range")

    # Query entities con boundary attive nell'anno
    q = db.query(GeoEntity).filter(GeoEntity.boundary_geojson.isnot(None))
    q = q.filter(GeoEntity.year_start <= year)
    q = q.filter(or_(GeoEntity.year_end.is_(None), GeoEntity.year_end >= year))
    entities = q.all()

    if not entities:
        raise HTTPException(status_code=404, detail=f"No entities with boundary in year {year}")

    dpi = 100
    fig, ax = plt.subplots(
        figsize=(width / dpi, height / dpi), dpi=dpi, facecolor="#0d1117"
    )
    ax.set_facecolor("#161b22")

    # Render by status (disputed on top of uncertain on top of confirmed)
    for status in ("confirmed", "uncertain", "disputed"):
        color = _STATUS_COLORS[status]
        subset = [e for e in entities if e.status == status]
        for e in subset:
            try:
                g = shapely_shape(json.loads(e.boundary_geojson))
                _draw_geom(ax, g, color)
            except (json.JSONDecodeError, ValueError, GEOSException):
                continue

    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Title
    year_display = f"{-year} BCE" if year < 0 else f"{year} CE"
    title_text = title or f"AtlasPI — {year_display} ({len(entities)} entities)"
    ax.set_title(title_text, color="#e6edf3", fontsize=14, pad=12)

    # Render to PNG bytes
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="#0d1117", dpi=dpi)
    plt.close(fig)
    buf.seek(0)

    return FastAPIResponse(
        content=buf.getvalue(),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Year": str(year),
            "X-Entity-Count": str(len(entities)),
        },
    )


@router.get(
    "/v1/render/entity/{entity_id}.png",
    summary="Render PNG del boundary di una singola entity",
    description="Focused map showing a single entity's boundary.",
)
def render_entity_png(
    entity_id: int,
    request: Request,
    width: int = Query(800, ge=200, le=2000),
    height: int = Query(600, ge=100, le=1500),
    db: Session = Depends(get_db),
):
    entity = db.query(GeoEntity).filter(GeoEntity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    if not entity.boundary_geojson:
        raise HTTPException(
            status_code=404, detail=f"Entity {entity_id} has no boundary_geojson"
        )

    try:
        g = shapely_shape(json.loads(entity.boundary_geojson))
    except (json.JSONDecodeError, ValueError, GEOSException) as e:
        raise HTTPException(status_code=500, detail=f"Malformed boundary: {e}")

    dpi = 100
    fig, ax = plt.subplots(
        figsize=(width / dpi, height / dpi), dpi=dpi, facecolor="#0d1117"
    )
    ax.set_facecolor("#161b22")

    color = _STATUS_COLORS.get(entity.status, "#58a6ff")
    _draw_geom(ax, g, color, alpha=0.75)

    # Auto-zoom to entity bounds + padding
    try:
        minx, miny, maxx, maxy = g.bounds
        px = (maxx - minx) * 0.15
        py = (maxy - miny) * 0.15
        ax.set_xlim(minx - px, maxx + px)
        ax.set_ylim(miny - py, maxy + py)
    except Exception:
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)

    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    year_display = f"{entity.year_start}" if entity.year_start >= 0 else f"{-entity.year_start} BCE"
    end_display = "ongoing" if entity.year_end is None else str(entity.year_end)
    ax.set_title(
        f"{entity.name_original} ({year_display}–{end_display})",
        color="#e6edf3",
        fontsize=14,
        pad=12,
    )

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="#0d1117", dpi=dpi)
    plt.close(fig)
    buf.seek(0)

    return FastAPIResponse(
        content=buf.getvalue(),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Entity-Id": str(entity.id),
        },
    )
