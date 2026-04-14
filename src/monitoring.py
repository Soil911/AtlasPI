"""Observability per AtlasPI: integrazione Sentry + helper runtime.

Sentry e' opt-in: si attiva solo se `SENTRY_DSN` e' presente nell'ambiente.
In sviluppo locale (DSN vuoto) tutte le funzioni sono no-op, quindi il
modulo puo' essere importato senza side effect.

Separato da `logging_config` perche' Sentry cattura eccezioni gia' gestite
dal logging strutturato — ha ruoli e lifecycle diversi.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from src.config import (
    APP_VERSION,
    ENVIRONMENT,
    PROCESS_START_TIME,
    SENTRY_DSN,
    SENTRY_ENVIRONMENT,
    SENTRY_PROFILES_SAMPLE_RATE,
    SENTRY_RELEASE,
    SENTRY_TRACES_SAMPLE_RATE,
)

logger = logging.getLogger(__name__)

_sentry_initialized = False


def init_sentry() -> bool:
    """Inizializza Sentry SDK se configurato.

    Ritorna True se Sentry e' attivo, False altrimenti.
    Idempotente: chiamate successive sono no-op.
    """
    global _sentry_initialized

    if _sentry_initialized:
        return True

    if not SENTRY_DSN:
        logger.info("Sentry disabilitato (SENTRY_DSN non impostato)")
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
    except ImportError:
        logger.warning("sentry-sdk non installato: monitoring disattivato")
        return False

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        release=SENTRY_RELEASE,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
            SqlalchemyIntegration(),
            # Cattura ERROR e piu' gravi, ma non li duplica negli event
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        # Evita di mandare PII per default (gli IP restano per rate limit tracing)
        send_default_pii=False,
    )

    _sentry_initialized = True
    logger.info(
        "Sentry inizializzato [env=%s release=%s traces=%.2f]",
        SENTRY_ENVIRONMENT,
        SENTRY_RELEASE,
        SENTRY_TRACES_SAMPLE_RATE,
    )
    return True


def sentry_is_active() -> bool:
    """True se Sentry e' stato inizializzato correttamente."""
    return _sentry_initialized


def capture_exception(exc: Exception, **context: Any) -> None:
    """Wrapper sicuro per inviare eccezioni a Sentry.

    Se Sentry non e' attivo, logga solo localmente.
    """
    if _sentry_initialized:
        try:
            import sentry_sdk
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_extra(key, value)
                sentry_sdk.capture_exception(exc)
            return
        except Exception:
            logger.exception("Fallita cattura eccezione verso Sentry")
    logger.error("Eccezione non catturata da Sentry: %s", exc, exc_info=exc)


def uptime_seconds() -> float:
    """Secondi dall'avvio del processo. Utile per /health."""
    return round(time.time() - PROCESS_START_TIME, 1)


def runtime_info() -> dict[str, Any]:
    """Snapshot di diagnostica per /health."""
    return {
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "uptime_seconds": uptime_seconds(),
        "sentry_active": _sentry_initialized,
    }
