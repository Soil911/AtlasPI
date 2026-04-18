"""Endpoint per ricevere i violation report di Content-Security-Policy.

Il browser invia una POST con Content-Type `application/csp-report` o
`application/reports+json` ogni volta che una risorsa viene bloccata
(o *sarebbe* stata bloccata, in report-only mode).

v6.66.0: CSP e' attivo in report-only. Questi endpoint raccolgono le
violazioni per 1-2 settimane per capire cosa blocca davvero. Dopo la
review dei report si passa a enforce mode in release futura.

I report vengono loggati a livello WARNING (non salvati a DB per evitare
spam DoS). Rate limit aggiuntivo applicato a monte via middleware globale.

Formato payload (browser-dependent):
    {
      "csp-report": {
        "document-uri": "https://atlaspi.cra-srl.com/app",
        "violated-directive": "img-src",
        "blocked-uri": "https://some-cdn.com/foo.png",
        "line-number": 42,
        "source-file": "https://atlaspi.cra-srl.com/static/main.js",
        ...
      }
    }
"""

import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import Response

logger = logging.getLogger("atlaspi.csp")

router = APIRouter(tags=["sistema"])


@router.post(
    "/v1/csp-report",
    include_in_schema=False,  # endpoint interno, non documentato pubblicamente
    status_code=204,
)
async def csp_report(request: Request) -> Response:
    """Riceve e logga i violation report da CSP report-only.

    Ritorna sempre 204 (No Content) per non dare informazione
    utile a chi tenta di abusare dell'endpoint.
    """
    try:
        raw = await request.body()
        if not raw:
            return Response(status_code=204)

        # Parse best-effort. Il Content-Type puo' essere
        # application/csp-report o application/reports+json.
        try:
            payload = json.loads(raw.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            logger.warning(
                "CSP report non-JSON body (%d bytes) from %s",
                len(raw),
                request.client.host if request.client else "?",
            )
            return Response(status_code=204)

        # Limita la dimensione del payload loggato (anti-log-flood).
        # In produzione questi report vengono raccolti via grep su journalctl.
        report_section = payload.get("csp-report") if isinstance(payload, dict) else None
        if not report_section:
            # Nuovo formato Reporting API (array di oggetti)
            report_section = payload

        logger.warning(
            "CSP violation from %s: %s",
            request.headers.get("referer", "?"),
            json.dumps(report_section)[:2000],  # cap a 2KB per log entry
        )
    except Exception:
        # Non esporre mai errori interni — un attaccante non deve sapere
        # se l'endpoint ha avuto problemi.
        logger.exception("Errore processing CSP report")

    return Response(status_code=204)
