"""Rate limiting centralizzato via slowapi.

v6.66.0 (audit #security): configurazione single-source-of-truth del
limiter, applicabile sia come middleware globale (default_limits) sia
come decorator per endpoint pesanti.

Chiave: IP del client (estratto da X-Forwarded-For in presenza di proxy,
altrimenti request.client.host). Nginx davanti al container imposta
X-Forwarded-For con l'IP reale — quindi get_remote_address di slowapi
va benissimo.

Limiti per endpoint:
- Default globale: 120/minute (sopra RATE_LIMIT del config — safety margin)
- /v1/entities/*, /v1/events/*, /v1/periods/*, /v1/search/*: 300/minute
  (endpoint di detail/search, uso interattivo mappa)
- /v1/export/*: 10/minute (endpoint pesante, generazione GeoJSON/CSV)
- /v1/snapshot/*: 60/minute (computa molte risorse in un hop)

Override tramite env var RATE_LIMIT se serve tuning in produzione senza
redeploy — e.g. "30/minute" per throttling d'emergenza.

ETHICS: il rate limiting NON deve impedire ricerche legittime di
ricercatori/studenti. Limiti tarati per uso umano interattivo + qualche
scraper educato. Un agent AI aggressivo triggerera' 429, e va bene.
"""

import logging

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import RATE_LIMIT

logger = logging.getLogger(__name__)

# Singleton — importato da src/main.py e dai router che vogliono
# applicare un decorator @limiter.limit() specifico.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT],
    # v6.66.0: storage_uri=None usa storage in-memory. Per multi-worker
    # (uvicorn --workers N) si raccomanda Redis via:
    #   storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    # Per ora in prod giriamo con 1 worker → in-memory OK.
    headers_enabled=True,  # aggiunge X-RateLimit-* alle risposte
    strategy="fixed-window",
)


# ─── Preset di limiti per categoria di endpoint ─────────────────────
# Usati come decorator: @limiter.limit(RATE_LIMIT_DETAIL)
RATE_LIMIT_DEFAULT = RATE_LIMIT
RATE_LIMIT_DETAIL = "300/minute"   # entities/events/periods detail + list
RATE_LIMIT_SEARCH = "300/minute"   # /v1/search, /v1/entities?q=
RATE_LIMIT_SNAPSHOT = "60/minute"  # /v1/snapshot/year/* (pesante)
RATE_LIMIT_EXPORT = "10/minute"    # /v1/export/* (molto pesante)
RATE_LIMIT_CSP_REPORT = "30/minute"  # /v1/csp-report (anti log-flood)
