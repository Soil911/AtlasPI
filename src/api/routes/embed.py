"""Endpoint /embed/* — Phase G4c badge embed.

Genera SVG badges che blog/wiki/storia-sites possono embeddare per
linkare a una entita' AtlasPI. Backlink SEO + scoperta organica.

GET /embed/badge.svg?entity=ID&style=dark|light
GET /embed/preview/{entity_id}      — HTML preview con esempio di embed
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import GeoEntity, Source

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/embed", tags=["embed"])


def _esc_xml(s: str | None) -> str:
    """Escape per XML/SVG."""
    if not s:
        return ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _fmt_year(y: int | None) -> str:
    if y is None:
        return "—"
    if y < 0:
        return f"{abs(y)} BCE"
    return f"{y} CE"


def _truncate(s: str, n: int = 28) -> str:
    if not s:
        return ""
    return s if len(s) <= n else s[: n - 1] + "…"


PALETTE = {
    "dark": {
        "bg": "#0f1116",
        "border": "#2a2c33",
        "title": "#e6e8eb",
        "subtitle": "#9aa1a8",
        "accent": "#ffc896",
        "muted": "#6a7079",
    },
    "light": {
        "bg": "#fafafa",
        "border": "#dcdfe3",
        "title": "#1a1c20",
        "subtitle": "#5c6470",
        "accent": "#b87333",
        "muted": "#8a8f95",
    },
}


@router.get(
    "/badge.svg",
    summary="SVG badge per embed in blog/wiki",
    description=(
        "Genera un badge SVG (400x88) per linkare a una entita' AtlasPI.\n\n"
        "Esempio:\n"
        "```html\n"
        "<a href='https://atlaspi.cra-srl.com/app?entity=178'>\n"
        "  <img src='https://atlaspi.cra-srl.com/embed/badge.svg?entity=178' alt='Ptolemaic Kingdom on AtlasPI'>\n"
        "</a>\n"
        "```\n\n"
        "Cache 1h client + 6h CDN."
    ),
)
def badge_svg(
    entity: int = Query(..., ge=1, description="ID entita'"),
    style: str = Query("dark", regex="^(dark|light)$", description="dark | light"),
    db: Session = Depends(get_db),
):
    ent: GeoEntity | None = db.query(GeoEntity).filter(GeoEntity.id == entity).first()
    if not ent:
        raise HTTPException(status_code=404, detail=f"entity {entity} not found")

    n_sources = db.query(Source).filter(Source.entity_id == ent.id).count()
    p = PALETTE[style]
    name = _esc_xml(_truncate(ent.name_original or f"Entity #{ent.id}", 32))
    period = f"{_fmt_year(ent.year_start)} — {_fmt_year(ent.year_end) if ent.year_end else 'present'}"
    period = _esc_xml(period)
    etype = _esc_xml(_truncate(ent.entity_type or "—", 24))
    conf_pct = int((ent.confidence_score or 0) * 100)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="88" viewBox="0 0 400 88"
     role="img" aria-label="AtlasPI badge for {name}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{p['bg']}"/>
      <stop offset="1" stop-color="{p['bg']}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="88" rx="6" ry="6" fill="url(#g)" stroke="{p['border']}" stroke-width="1"/>

  <!-- AtlasPI mark -->
  <text x="14" y="22" font-family="-apple-system,'Segoe UI',sans-serif"
        font-size="11" font-weight="600" letter-spacing="0.8" fill="{p['accent']}">ATLASPI</text>
  <text x="73" y="22" font-family="-apple-system,'Segoe UI',sans-serif"
        font-size="10" fill="{p['muted']}">historical geography</text>

  <!-- Entity name -->
  <text x="14" y="46" font-family="-apple-system,'Segoe UI',sans-serif"
        font-size="16" font-weight="600" fill="{p['title']}">{name}</text>

  <!-- Period -->
  <text x="14" y="64" font-family="-apple-system,'Segoe UI',sans-serif"
        font-size="11" fill="{p['subtitle']}">{period}</text>

  <!-- Type + sources count -->
  <text x="14" y="80" font-family="-apple-system,'Segoe UI',sans-serif"
        font-size="10" fill="{p['muted']}">{etype} • {n_sources} sources • confidence {conf_pct}%</text>
</svg>
"""
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={
            # 1h browser, 6h CDN
            "Cache-Control": "public, max-age=3600, s-maxage=21600",
            # CORS aperto per essere embeddable ovunque
            "Access-Control-Allow-Origin": "*",
            # X-Robots-Tag: gli embed creano un sacco di "duplicate" URLs
            "X-Robots-Tag": "noindex",
        },
    )


@router.get(
    "/preview/{entity_id}",
    summary="HTML preview con snippet copy-paste per embed",
    response_class=Response,
)
def badge_preview(
    entity_id: int,
    db: Session = Depends(get_db),
):
    ent = db.query(GeoEntity).filter(GeoEntity.id == entity_id).first()
    if not ent:
        raise HTTPException(status_code=404, detail=f"entity {entity_id} not found")

    name = _esc_xml(ent.name_original or f"Entity #{ent.id}")
    base = "https://atlaspi.cra-srl.com"
    badge_dark = f"{base}/embed/badge.svg?entity={entity_id}&style=dark"
    badge_light = f"{base}/embed/badge.svg?entity={entity_id}&style=light"

    snippet_html = f"""<a href="{base}/app?entity={entity_id}" target="_blank" rel="noopener">
  <img src="{badge_dark}" alt="{name} on AtlasPI" loading="lazy">
</a>"""
    snippet_md = f"[![{name} on AtlasPI]({badge_dark})]({base}/app?entity={entity_id})"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AtlasPI badge — {name}</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    body {{ font: 14px/1.5 -apple-system, "Segoe UI", sans-serif; background: #0f1116; color: #e6e8eb; padding: 32px; max-width: 720px; margin: 0 auto; }}
    h1 {{ color: #ffc896; font-size: 20px; }}
    code, pre {{ background: #1a1c20; color: #c8cdd3; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 12px; }}
    pre {{ padding: 12px; overflow-x: auto; border: 1px solid #2a2c33; }}
    .row {{ display: flex; gap: 16px; align-items: center; margin: 16px 0; }}
    .note {{ color: #9aa1a8; font-size: 12px; }}
    a {{ color: #ffc896; }}
  </style>
</head>
<body>
  <h1>AtlasPI embed badge</h1>
  <p>Use these snippets to link to <a href="{base}/app?entity={entity_id}">{name}</a> from your blog/wiki/website. Backlinks help discover AtlasPI organically.</p>

  <h2>Dark badge</h2>
  <div class="row"><img src="{badge_dark}" alt="{name} on AtlasPI"></div>
  <p>HTML:</p>
  <pre>{_esc_xml(snippet_html)}</pre>
  <p>Markdown:</p>
  <pre>{_esc_xml(snippet_md)}</pre>

  <h2>Light badge</h2>
  <div class="row" style="background:#fff;padding:8px;border-radius:6px"><img src="{badge_light}" alt="{name} on AtlasPI"></div>
  <p>Direct URL: <code>{badge_light}</code></p>

  <p class="note">Caching: 1h browser, 6h CDN. Counts of sources/confidence update on next refresh.</p>
</body>
</html>
"""
    return Response(content=html, media_type="text/html; charset=utf-8")
