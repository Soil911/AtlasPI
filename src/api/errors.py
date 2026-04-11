"""Error handling centralizzato per AtlasPI.

Nessun stacktrace esposto al client. Errori loggati internamente.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.logging_config import request_id_var

logger = logging.getLogger(__name__)


class AtlasError(Exception):
    """Errore base di AtlasPI."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class EntityNotFoundError(AtlasError):
    def __init__(self, entity_id: int):
        super().__init__(404, f"Entità con id={entity_id} non trovata")


class ValidationError(AtlasError):
    def __init__(self, detail: str):
        super().__init__(422, detail)


def _error_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "detail": detail,
            "request_id": request_id_var.get("-"),
        },
    )


def register_error_handlers(app: FastAPI):
    """Registra gli handler di errore globali."""

    @app.exception_handler(AtlasError)
    async def atlas_error_handler(request: Request, exc: AtlasError):
        logger.warning("AtlasError %d: %s", exc.status_code, exc.detail)
        return _error_response(exc.status_code, exc.detail)

    @app.exception_handler(422)
    async def validation_error_handler(request: Request, exc):
        logger.warning("Validation error: %s", exc)
        return _error_response(422, "Parametri di richiesta non validi")

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        logger.exception("Internal server error")
        return _error_response(500, "Errore interno del server")
