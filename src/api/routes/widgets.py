"""Embeddable widgets — v6.22.0.

GET /widget/entity/{id}       Entity card widget (iframe-friendly HTML)
GET /widget/timeline           Mini timeline widget
GET /widget/on-this-day        On-this-day widget
GET /widgets                   Showcase page with embed code examples

All widget responses set X-Frame-Options: ALLOWALL to permit embedding
in third-party sites via <iframe>.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, HTMLResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["widgets"])

WIDGETS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static" / "widgets"


def _widget_response(file_path: Path) -> Response:
    """Return an HTML file with X-Frame-Options allowing embedding."""
    if not file_path.exists():
        return HTMLResponse(
            content="<html><body>Widget not found</body></html>",
            status_code=404,
        )
    content = file_path.read_text(encoding="utf-8")
    return HTMLResponse(
        content=content,
        status_code=200,
        headers={
            "X-Frame-Options": "ALLOWALL",
            "Content-Security-Policy": "frame-ancestors *",
        },
    )


@router.get("/widgets", include_in_schema=False)
async def widget_showcase():
    """Showcase page listing all available widgets with embed code."""
    return _widget_response(WIDGETS_DIR / "showcase.html")


@router.get("/widget/entity/{entity_id}", include_in_schema=False)
async def widget_entity(entity_id: int, request: Request):
    """Entity card widget — embeddable via iframe."""
    return _widget_response(WIDGETS_DIR / "entity.html")


@router.get("/widget/timeline", include_in_schema=False)
async def widget_timeline(request: Request):
    """Mini timeline widget — embeddable via iframe."""
    return _widget_response(WIDGETS_DIR / "timeline.html")


@router.get("/widget/on-this-day", include_in_schema=False)
async def widget_on_this_day(request: Request):
    """On This Day widget — embeddable via iframe."""
    return _widget_response(WIDGETS_DIR / "on-this-day.html")
