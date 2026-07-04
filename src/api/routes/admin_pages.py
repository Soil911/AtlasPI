"""Shell HTML PUBBLICHE delle dashboard admin (traffic-fix #2).

La shell del Co-Founder Brief (`/admin/brief`) è servita pubblicamente — come
`/docs` — perché NON contiene dati: solo layout + JS. Tutti i DATI restano
protetti da `verify_admin` (`/admin/ai/*`, `/admin/insights`,
`/admin/coverage-report`, …).

La shell carica `static/admin/admin-auth.js`, che chiede il token una volta,
lo salva in localStorage e lo invia come header `X-Admin-Token` su ogni chiamata
`/admin/*`. Questo elimina la fragilità del caching Basic-Auth del browser
(401 intermittenti osservati in produzione, 2026-05-31).

NB: questo router è incluso in main.py SENZA `verify_admin`. La path è
allowlistata in `PUBLIC_ADMIN_SHELLS`, riconosciuta dallo startup-guard di
Wave 1.1 e dal test `tests/test_admin_auth.py`.

v6.99.115: la dashboard analytics interna (`/admin/analytics` + endpoint dati
+ dev-ips) è stata RIMOSSA — le statistiche web umane passano a Matomo
self-hosted (stats.cra-srl.com, siteId 2, cookieless). La telemetria API
(api_request_logs, middleware, agents_insights, analyzer failed_searches del
Co-Founder) resta: è sistema qualità, non analytics umane.
"""
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["admin"])

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static"

# Shell intenzionalmente pubbliche (solo layout, nessun dato). Allowlist
# condivisa con lo startup-guard e i test di admin-auth.
PUBLIC_ADMIN_SHELLS = frozenset({"/admin/brief"})


@router.get("/admin/brief", include_in_schema=False)
async def brief_shell():
    """Shell pubblica del Co-Founder Brief (dati via /admin/ai/*, /admin/insights, protetti)."""
    brief_path = STATIC_DIR / "admin" / "brief.html"
    return FileResponse(brief_path, media_type="text/html")
