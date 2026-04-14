"""Client HTTP async per l'API REST di AtlasPI.

Wrappa httpx.AsyncClient con:
- base URL configurabile via env var ``ATLASPI_API_URL``
  (default: https://atlaspi.cra-srl.com)
- timeout di rete sano
- normalizzazione delle eccezioni in :class:`AtlasPIClientError`
- helper async per ognuno degli endpoint pubblici v1
"""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://atlaspi.cra-srl.com"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "atlaspi-mcp/0.1.0 (+https://github.com/Soil911/AtlasPI)"


class AtlasPIClientError(RuntimeError):
    """Errore generico del client AtlasPI.

    Wrappa errori di rete (timeout, DNS) e errori HTTP (4xx/5xx) con un
    messaggio leggibile dall'agente AI che ha invocato il tool.
    """

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def get_base_url() -> str:
    """Ritorna la base URL letta dalla env var ``ATLASPI_API_URL``.

    Se la variabile non e' impostata o e' vuota, ritorna il default
    di produzione (https://atlaspi.cra-srl.com). Eventuale slash finale
    viene rimosso per evitare ``//`` nei path.
    """
    raw = os.environ.get("ATLASPI_API_URL", "").strip()
    base = raw or DEFAULT_BASE_URL
    return base.rstrip("/")


def _drop_none(params: dict[str, Any]) -> dict[str, Any]:
    """Rimuove le chiavi con valore None da un dict di query params."""
    return {k: v for k, v in params.items() if v is not None}


class AtlasPIClient:
    """Client async per gli endpoint REST v1 di AtlasPI.

    Usabile come async context manager::

        async with AtlasPIClient() as client:
            data = await client.get_stats()

    Oppure standalone (in tal caso chiamare ``aclose()`` a fine vita).
    """

    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = (base_url or get_base_url()).rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )

    async def __aenter__(self) -> AtlasPIClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Chiude il client httpx sottostante (solo se posseduto)."""
        if self._owns_client:
            await self._client.aclose()

    # -- Helper interno -------------------------------------------------

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Esegue una GET su ``path`` e ritorna il body JSON decodificato.

        Solleva :class:`AtlasPIClientError` per timeout, errori di rete
        o status code non 2xx.
        """
        try:
            response = await self._client.get(path, params=_drop_none(params or {}))
        except httpx.TimeoutException as exc:
            raise AtlasPIClientError(
                f"AtlasPI request timed out after {self._client.timeout.read}s "
                f"({path})"
            ) from exc
        except httpx.RequestError as exc:
            raise AtlasPIClientError(
                f"Network error while calling AtlasPI ({path}): {exc}"
            ) from exc

        if response.status_code >= 400:
            detail = response.text[:500]
            raise AtlasPIClientError(
                f"AtlasPI returned HTTP {response.status_code} for {path}: {detail}",
                status_code=response.status_code,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise AtlasPIClientError(
                f"AtlasPI returned non-JSON response for {path}"
            ) from exc

    # -- Endpoints v1 ---------------------------------------------------

    async def search_entities(
        self,
        *,
        name: str | None = None,
        year: int | None = None,
        type: str | None = None,
        continent: str | None = None,
        status: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """GET /v1/entity — ricerca filtrata di entita'."""
        return await self._get(
            "/v1/entity",
            {
                "name": name,
                "year": year,
                "type": type,
                "continent": continent,
                "status": status,
                "sort": sort,
                "order": order,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_entity(self, entity_id: int) -> Any:
        """GET /v1/entities/{entity_id} — dettaglio entita'."""
        return await self._get(f"/v1/entities/{int(entity_id)}")

    async def snapshot(
        self,
        year: int,
        *,
        type: str | None = None,
        continent: str | None = None,
    ) -> Any:
        """GET /v1/snapshot/{year} — snapshot del mondo in un anno."""
        return await self._get(
            f"/v1/snapshot/{int(year)}",
            {"type": type, "continent": continent},
        )

    async def nearby(
        self,
        *,
        lat: float,
        lon: float,
        radius: float | None = None,
        year: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """GET /v1/nearby — entita' vicine a coordinate (km)."""
        return await self._get(
            "/v1/nearby",
            {
                "lat": lat,
                "lon": lon,
                "radius": radius,
                "year": year,
                "limit": limit,
            },
        )

    async def compare(self, id1: int, id2: int) -> Any:
        """GET /v1/compare/{id1}/{id2} — confronto fra due entita'."""
        return await self._get(f"/v1/compare/{int(id1)}/{int(id2)}")

    async def random(
        self,
        *,
        type: str | None = None,
        year: int | None = None,
        status: str | None = None,
        continent: str | None = None,
    ) -> Any:
        """GET /v1/random — entita' casuale (con filtri opzionali)."""
        return await self._get(
            "/v1/random",
            {
                "type": type,
                "year": year,
                "status": status,
                "continent": continent,
            },
        )

    async def evolution(self, entity_id: int) -> Any:
        """GET /v1/entities/{entity_id}/evolution — timeline cambi territoriali."""
        return await self._get(f"/v1/entities/{int(entity_id)}/evolution")

    async def stats(self) -> Any:
        """GET /v1/stats — statistiche aggregate del dataset."""
        return await self._get("/v1/stats")

    async def aggregation(self) -> Any:
        """GET /v1/aggregation — breakdown per secolo, tipo, continente, status."""
        return await self._get("/v1/aggregation")

    async def health(self) -> Any:
        """GET /health — stato di salute del servizio (debug)."""
        return await self._get("/health")
