"""Rate limiting centralizzato via slowapi.

v6.66.0 (audit #security): configurazione single-source-of-truth del
limiter, applicabile sia come middleware globale (default_limits) sia
come decorator per endpoint pesanti.

v6.92.1 (audit R2 — multi-worker safety): storage backend switchato da
in-memory a Redis quando REDIS_URL e' settato. In-memory funziona solo
con singolo worker; il Dockerfile lancia gunicorn con `--workers 2`, e
con storage in-memory ogni worker mantiene un suo contatore separato —
risultato: un client puo' fare effettivamente 2x il limite dichiarato.
Con Redis come storage condiviso, i contatori sono coerenti tra worker.

Chiave: IP del client (estratto da X-Forwarded-For in presenza di proxy,
altrimenti request.client.host). Nginx davanti al container imposta
X-Forwarded-For con l'IP reale — quindi get_remote_address di slowapi
va benissimo.

Limiti per endpoint:
- Default globale: 120/minute (sopra RATE_LIMIT del config — safety margin)
- /v1/entities/*, /v1/events/*, /v1/periods/*, /v1/search/*: 300/minute
  (endpoint di detail/search, uso interattivo mappa)
- /v1/export/*: 20/minute (endpoint pesante, generazione GeoJSON/CSV)
- /v1/snapshot/*: 60/minute (computa molte risorse in un hop)

Override tramite env var RATE_LIMIT se serve tuning in produzione senza
redeploy — e.g. "30/minute" per throttling d'emergenza.

ETHICS: il rate limiting NON deve impedire ricerche legittime di
ricercatori/studenti. Limiti tarati per uso umano interattivo + qualche
scraper educato. Un agent AI aggressivo triggerera' 429, e va bene.
"""

import logging
import os

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import RATE_LIMIT

logger = logging.getLogger(__name__)


def _resolve_storage_uri() -> str:
    """Scegli storage backend per il limiter.

    Strategia:
    1. Se REDIS_URL e' settato e raggiungibile (ping ok) → usa Redis.
       Storage condiviso tra worker → contatori coerenti, multi-worker safe.
    2. Altrimenti → memory:// (in-process, dev locale o Redis down).

    Il ping e' importante: senza di esso, slowapi tenta connessioni
    Redis ad ogni richiesta e fallisce con 500. Con fallback graceful
    a memory://, il servizio continua a girare anche se Redis e' giu',
    a costo di rate limit per-worker (accettabile, vedi cache.py).
    """
    redis_url = os.getenv("REDIS_URL", "").strip()
    if not redis_url:
        logger.info("Rate limiter: REDIS_URL non settato → storage in-memory (dev mode)")
        return "memory://"

    try:
        import redis as _redis
        client = _redis.Redis.from_url(
            redis_url,
            socket_connect_timeout=3,
            socket_timeout=2,
        )
        client.ping()
        # Log senza esporre eventuali credenziali nell'URL.
        redacted = redis_url.split("@")[-1] if "@" in redis_url else redis_url
        logger.info("Rate limiter: storage Redis attivo (%s)", redacted)
        return redis_url
    except Exception:
        logger.warning(
            "Rate limiter: REDIS_URL settato ma ping fallito → fallback memory:// "
            "(rate limit sara' per-worker, non condiviso)",
            exc_info=True,
        )
        return "memory://"


# Singleton — importato da src/main.py e dai router che vogliono
# applicare un decorator @limiter.limit() specifico.
#
# v6.92.1: storage Redis quando disponibile. Con `gunicorn --workers 2`
# (Dockerfile) i contatori sono condivisi → un client non puo' piu'
# bypassare il limite essendo bilanciato su 2 worker.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT],
    storage_uri=_resolve_storage_uri(),
    headers_enabled=True,  # aggiunge X-RateLimit-* alle risposte
    strategy="fixed-window",
)


# ─── Preset di limiti per categoria di endpoint ─────────────────────
# Usati come decorator: @limiter.limit(RATE_LIMIT_DETAIL)
RATE_LIMIT_DEFAULT = RATE_LIMIT
RATE_LIMIT_DETAIL = "300/minute"   # entities/events/periods detail + list
RATE_LIMIT_SEARCH = "300/minute"   # /v1/search, /v1/entities?q=
RATE_LIMIT_SNAPSHOT = "60/minute"  # /v1/snapshot/year/* (pesante)
RATE_LIMIT_EXPORT = "20/minute"    # /v1/export/* (molto pesante) — raised from 10 (#69)
RATE_LIMIT_CSP_REPORT = "30/minute"  # /v1/csp-report (anti log-flood)
