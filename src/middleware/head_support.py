"""Middleware che aggiunge supporto HEAD a tutti i GET endpoint — v6.66 FIX 8.

FastAPI by default registra solo il metodo dichiarato nel decorator (`@router.get`).
Le richieste HEAD su questi path rispondono 405 Method Not Allowed, ma per
la RFC 9110 §9.3.2 ogni endpoint GET dovrebbe accettare HEAD restituendo
gli stessi header senza body.

Approccio adottato: intercettiamo HEAD in middleware, lo eseguiamo come GET
interno, poi rimuoviamo il body dalla risposta. Questo e' piu' semplice che
decorare centinaia di endpoint uno a uno con `@router.head` e garantisce
comportamento uniforme.

ETHICS: questo middleware non tocca dati storici ne' applica semantica
aggiuntiva — e' purament0e compliance HTTP. Non serve ETHICS comment.
"""

from __future__ import annotations

from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class HeadSupportMiddleware(BaseHTTPMiddleware):
    """Intercetta HEAD, delega a GET internamente, strip del body.

    Il middleware fa il rewrite del method prima di chiamare call_next
    (cosi il router trova il handler GET), e rimuove il body dalla
    risposta prima di restituirla al client. I response headers (incluso
    Content-Length, Content-Type, Cache-Control) restano invariati.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method != "HEAD":
            return await call_next(request)

        # Rewrite: HEAD -> GET per il routing interno.
        # Non possiamo modificare request.method direttamente (immutable scope),
        # ma possiamo mutare request.scope["method"].
        original_scope_method = request.scope.get("method")
        request.scope["method"] = "GET"
        try:
            response = await call_next(request)
        finally:
            # Ripristina per sicurezza (request.scope e' condiviso in alcune condizioni).
            request.scope["method"] = original_scope_method

        # Strip del body — HEAD deve avere body vuoto per RFC 9110.
        # StreamingResponse / FileResponse richiedono gestione speciale:
        # costruiamo una Response nuova con status e headers ma senza body.
        headers = MutableHeaders(raw=list(response.raw_headers))
        # Content-Length rimane come era nella GET (== length del body che
        # SAREBBE stato inviato), per semantica RFC 9110 §9.3.2. Alcuni
        # proxy tuttavia segnalano mismatch — togliamo il body ma il
        # Content-Length originale e' mantenuto nell'header come hint.
        return Response(
            content=b"",
            status_code=response.status_code,
            headers=dict(headers),
            media_type=response.media_type,
        )
