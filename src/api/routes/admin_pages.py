"""Shell HTML PUBBLICHE delle dashboard admin (traffic-fix #2).

Le shell delle dashboard (`/admin/analytics`, `/admin/brief`) sono servite
pubblicamente — come `/docs` — perché NON contengono dati: solo layout + JS.
Tutti i DATI restano protetti da `verify_admin` (`/admin/analytics/data`,
`/admin/ai/*`, `/admin/insights`, `/admin/coverage-report`, `/admin/dev-ips`, …).

Le shell caricano `static/admin/admin-auth.js`, che chiede il token una volta,
lo salva in localStorage e lo invia come header `X-Admin-Token` su ogni chiamata
`/admin/*`. Questo elimina la fragilità del caching Basic-Auth del browser
(401 intermittenti osservati in produzione, 2026-05-31).

NB: questo router è incluso in main.py SENZA `verify_admin`. Le due path sono
allowlistate in `PUBLIC_ADMIN_SHELLS`, riconosciuta dallo startup-guard di
Wave 1.1 e dal test `tests/test_admin_auth.py`.
"""
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

from src.api.routes.analytics import DASHBOARD_HTML

router = APIRouter(tags=["admin"])

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static"

# Shell intenzionalmente pubbliche (solo layout, nessun dato). Allowlist
# condivisa con lo startup-guard e i test di admin-auth.
PUBLIC_ADMIN_SHELLS = frozenset({"/admin/analytics", "/admin/brief"})


@router.get("/admin/analytics", include_in_schema=False)
async def analytics_shell():
    """Shell pubblica della dashboard analytics (dati via /admin/analytics/data, protetti)."""
    return HTMLResponse(content=DASHBOARD_HTML)


@router.get("/admin/brief", include_in_schema=False)
async def brief_shell():
    """Shell pubblica del Co-Founder Brief (dati via /admin/ai/*, /admin/insights, protetti)."""
    brief_path = STATIC_DIR / "admin" / "brief.html"
    return FileResponse(brief_path, media_type="text/html")
