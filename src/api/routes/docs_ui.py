"""Route per la pagina API Explorer (/docs-ui)."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["sistema"])

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static"


@router.get("/docs-ui", include_in_schema=False)
async def serve_docs_ui():
    """Serve the interactive API documentation page (custom, not Swagger)."""
    return FileResponse(
        STATIC_DIR / "docs-ui" / "index.html",
        media_type="text/html",
    )
