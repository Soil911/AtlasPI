"""Error handling centralizzato per AtlasPI.

Nessun stacktrace esposto al client. Errori loggati internamente.
Schema strutturato: {"error": {"code": "...", "message": "...", "request_id": "..."}}
"""

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.logging_config import request_id_var

logger = logging.getLogger(__name__)

# ── Codici errore standard ──────────────────────────────────────
ERROR_CODES = {
    400: "BAD_REQUEST",
    404: "NOT_FOUND",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
}


class AtlasError(Exception):
    """Errore base di AtlasPI."""

    def __init__(self, status_code: int, detail: str, code: str | None = None):
        self.status_code = status_code
        self.detail = detail
        self.code = code or ERROR_CODES.get(status_code, "UNKNOWN_ERROR")


class EntityNotFoundError(AtlasError):
    def __init__(self, entity_id: int):
        super().__init__(404, f"Entit\u00e0 con id={entity_id} non trovata", "NOT_FOUND")


class ValidationError(AtlasError):
    def __init__(self, detail: str):
        super().__init__(422, detail, "VALIDATION_ERROR")


def _error_response(
    status_code: int,
    detail: str,
    code: str | None = None,
    details: dict | None = None,
) -> JSONResponse:
    """Costruisce una risposta di errore strutturata.

    v6.66 FIX 7: formato unificato per tutti gli errori.

    Formato completo::

        {
          "error": {
            "code": "NOT_FOUND",
            "message": "...",
            "details": {...},         # optional context
            "request_id": "..."
          },
          "detail": "...",            # LEGACY flat
          "request_id": "...",        # LEGACY flat
          "error_detail": {...}       # LEGACY structured alias
        }

    La nuova forma canonica e' `error.*` come oggetto annidato.
    I campi legacy `detail`, `request_id` e `error_detail` restano per
    retrocompatibilita' con client gia' deployati.
    """
    error_code = code or ERROR_CODES.get(status_code, "UNKNOWN_ERROR")
    rid = request_id_var.get("-")
    # v6.66 FIX 7: error envelope canonico unificato.
    err_obj = {
        "code": error_code,
        "message": detail,
        "request_id": rid,
    }
    if details is not None:
        err_obj["details"] = details

    return JSONResponse(
        status_code=status_code,
        content={
            # v6.66 canonico
            "error": err_obj,
            # Legacy flat (retrocompatibilita' — test e client deployati)
            "detail": detail,
            "request_id": rid,
            # Legacy strutturato
            "error_detail": {
                "code": error_code,
                "message": detail,
                "request_id": rid,
            },
        },
    )


def register_error_handlers(app: FastAPI):
    """Registra gli handler di errore globali."""

    @app.exception_handler(AtlasError)
    async def atlas_error_handler(request: Request, exc: AtlasError):
        logger.warning("AtlasError %d [%s]: %s", exc.status_code, exc.code, exc.detail)
        return _error_response(exc.status_code, exc.detail, exc.code)

    @app.exception_handler(422)
    async def validation_error_handler(request: Request, exc):
        logger.warning("Validation error: %s", exc)
        return _error_response(422, "Parametri di richiesta non validi", "VALIDATION_ERROR")

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        logger.exception("Internal server error")
        return _error_response(500, "Errore interno del server", "INTERNAL_ERROR")

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Cattura tutte le eccezioni non gestite.

        Logga il traceback completo lato server ma restituisce
        al client solo un messaggio generico sicuro.
        """
        logger.error(
            "Eccezione non gestita su %s %s: %s\n%s",
            request.method,
            request.url.path,
            exc,
            traceback.format_exc(),
        )
        return _error_response(500, "Errore interno del server", "INTERNAL_ERROR")
