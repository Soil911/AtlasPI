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
USER_AGENT = "atlaspi-mcp/0.7.0 (+https://github.com/Soil911/AtlasPI)"


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

    async def similar(
        self, entity_id: int, *, limit: int = 10, min_score: float = 0.3,
    ) -> Any:
        """GET /v1/entities/{entity_id}/similar — entities most similar to this one."""
        return await self._get(
            f"/v1/entities/{int(entity_id)}/similar",
            params={"limit": limit, "min_score": min_score},
        )

    async def stats(self) -> Any:
        """GET /v1/stats — statistiche aggregate del dataset."""
        return await self._get("/v1/stats")

    async def aggregation(self) -> Any:
        """GET /v1/aggregation — breakdown per secolo, tipo, continente, status."""
        return await self._get("/v1/aggregation")

    async def health(self) -> Any:
        """GET /health — stato di salute del servizio (debug)."""
        return await self._get("/health")

    # -- v6.3 events ---------------------------------------------------

    async def list_events(
        self,
        *,
        year_min: int | None = None,
        year_max: int | None = None,
        event_type: str | None = None,
        status: str | None = None,
        known_silence: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """GET /v1/events — lista filtrata di eventi storici."""
        return await self._get(
            "/v1/events",
            {
                "year_min": year_min,
                "year_max": year_max,
                "event_type": event_type,
                "status": status,
                "known_silence": known_silence,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_event(self, event_id: int) -> Any:
        """GET /v1/events/{event_id} — dettaglio evento storico."""
        return await self._get(f"/v1/events/{int(event_id)}")

    async def event_types(self) -> Any:
        """GET /v1/events/types — enum EventType + EventRole."""
        return await self._get("/v1/events/types")

    async def events_for_entity(
        self, entity_id: int, *, role: str | None = None
    ) -> Any:
        """GET /v1/entities/{id}/events — eventi in cui l'entità compare."""
        return await self._get(
            f"/v1/entities/{int(entity_id)}/events",
            {"role": role},
        )

    # -- v6.23 events for map ------------------------------------------

    async def events_for_map(
        self,
        *,
        year: int,
        window: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """GET /v1/events/map — eventi con coordinate per overlay mappa.

        Payload leggero ottimizzato per rendering marker. La finestra
        si auto-espande per epoche antiche (±50 per anni < -1000,
        ±25 per -1000..0, ±10 per moderno).
        """
        return await self._get(
            "/v1/events/map",
            {"year": year, "window": window, "limit": limit},
        )

    async def on_this_day(self, mm_dd: str) -> Any:
        """GET /v1/events/on-this-day/{mm_dd} — eventi avvenuti in questa data.

        Formato mm_dd: MM-DD (es. '07-04' per 4 luglio).
        """
        return await self._get(f"/v1/events/on-this-day/{mm_dd}")

    async def date_coverage(self) -> Any:
        """GET /v1/events/date-coverage — quali date MM-DD hanno eventi."""
        return await self._get("/v1/events/date-coverage")

    # -- v6.27 historical periods ---------------------------------------

    async def list_periods(
        self,
        *,
        region: str | None = None,
        period_type: str | None = None,
        year: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """GET /v1/periods — filtered list of historical epochs/periods."""
        return await self._get(
            "/v1/periods",
            {
                "region": region,
                "period_type": period_type,
                "year": year,
                "status": status,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_period(self, period_id: int) -> Any:
        """GET /v1/periods/{period_id} — period detail by numeric ID."""
        return await self._get(f"/v1/periods/{int(period_id)}")

    async def get_period_by_slug(self, slug: str) -> Any:
        """GET /v1/periods/by-slug/{slug} — period detail by slug."""
        return await self._get(f"/v1/periods/by-slug/{slug}")

    async def periods_at_year(
        self, year: int, *, region: str | None = None,
    ) -> Any:
        """GET /v1/periods/at-year/{year} — periods that include a given year."""
        return await self._get(
            f"/v1/periods/at-year/{int(year)}",
            {"region": region},
        )

    async def entity_periods(
        self, entity_id: int, *, region: str | None = None,
    ) -> Any:
        """GET /v1/entities/{entity_id}/periods — periods overlapping an entity's lifespan."""
        return await self._get(
            f"/v1/entities/{int(entity_id)}/periods",
            {"region": region},
        )

    async def event_periods(
        self, event_id: int, *, region: str | None = None,
    ) -> Any:
        """GET /v1/events/{event_id}/periods — periods containing an event's year."""
        return await self._get(
            f"/v1/events/{int(event_id)}/periods",
            {"region": region},
        )

    async def world_snapshot(
        self, year: int, *, top_n: int | None = None,
    ) -> Any:
        """GET /v1/snapshot/year/{year} — rich aggregated view of the world at a year."""
        return await self._get(
            f"/v1/snapshot/year/{int(year)}",
            {"top_n": top_n},
        )

    # -- v6.4 cities & routes ------------------------------------------

    async def list_cities(
        self,
        *,
        year: int | None = None,
        city_type: str | None = None,
        entity_id: int | None = None,
        bbox: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """GET /v1/cities — lista filtrata di città storiche."""
        return await self._get(
            "/v1/cities",
            {
                "year": year,
                "city_type": city_type,
                "entity_id": entity_id,
                "bbox": bbox,
                "status": status,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_city(self, city_id: int) -> Any:
        """GET /v1/cities/{city_id} — dettaglio città storica."""
        return await self._get(f"/v1/cities/{int(city_id)}")

    async def city_types(self) -> Any:
        """GET /v1/cities/types — enum CityType."""
        return await self._get("/v1/cities/types")

    async def list_routes(
        self,
        *,
        year: int | None = None,
        route_type: str | None = None,
        involves_slavery: bool | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """GET /v1/routes — lista filtrata di rotte commerciali."""
        return await self._get(
            "/v1/routes",
            {
                "year": year,
                "route_type": route_type,
                "involves_slavery": involves_slavery,
                "status": status,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_route(self, route_id: int) -> Any:
        """GET /v1/routes/{route_id} — dettaglio rotta con waypoints."""
        return await self._get(f"/v1/routes/{int(route_id)}")

    async def route_types(self) -> Any:
        """GET /v1/routes/types — enum RouteType."""
        return await self._get("/v1/routes/types")

    # -- v6.5 chains ---------------------------------------------------

    async def list_chains(
        self,
        *,
        chain_type: str | None = None,
        region: str | None = None,
        year: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """GET /v1/chains — lista filtrata di catene successorie."""
        return await self._get(
            "/v1/chains",
            {
                "chain_type": chain_type,
                "region": region,
                "year": year,
                "status": status,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_chain(self, chain_id: int) -> Any:
        """GET /v1/chains/{chain_id} — dettaglio catena con link ordinati."""
        return await self._get(f"/v1/chains/{int(chain_id)}")

    async def chain_types(self) -> Any:
        """GET /v1/chains/types — enum ChainType + TransitionType."""
        return await self._get("/v1/chains/types")

    async def entity_predecessors(self, entity_id: int) -> Any:
        """GET /v1/entities/{id}/predecessors — predecessori nelle catene."""
        return await self._get(f"/v1/entities/{int(entity_id)}/predecessors")

    async def entity_successors(self, entity_id: int) -> Any:
        """GET /v1/entities/{id}/successors — successori nelle catene."""
        return await self._get(f"/v1/entities/{int(entity_id)}/successors")

    # -- v6.7 unified timeline + fuzzy search --------------------------

    async def full_timeline(
        self,
        entity_id: int,
        *,
        include_entity_links: bool | None = None,
    ) -> Any:
        """GET /v1/entities/{id}/timeline — stream unificato.

        Combina territory_changes + HistoricalEvent (via EventEntityLink) +
        transizioni ChainLink in un unico stream ordinato cronologicamente.
        """
        return await self._get(
            f"/v1/entities/{int(entity_id)}/timeline",
            {"include_entity_links": include_entity_links},
        )

    async def fuzzy_search(
        self,
        q: str,
        *,
        limit: int | None = None,
        min_score: float | None = None,
    ) -> Any:
        """GET /v1/search/fuzzy — ricerca approssimata cross-script.

        Usa difflib.SequenceMatcher per match tolleranti a errori di
        spelling, translitterazioni diverse e script differenti (latino,
        cirillico, arabo, cinese, devanagari...).
        """
        return await self._get(
            "/v1/search/fuzzy",
            {"q": q, "limit": limit, "min_score": min_score},
        )

    # -- v6.7 composite: nearest historical city -----------------------

    async def nearest_historical_city(
        self,
        *,
        lat: float,
        lon: float,
        year: int | None = None,
        city_type: str | None = None,
        limit: int | None = None,
        max_candidates: int = 500,
    ) -> Any:
        """Ricerca la citta' storica piu' vicina a (lat, lon) in un dato anno.

        Composizione client-side: non c'e' un endpoint /v1/cities/nearest.
        Scarica fino a ``max_candidates`` citta' attive nell'anno e calcola
        la distanza haversine in Python per ordinarle.
        """
        data = await self.list_cities(
            year=year,
            city_type=city_type,
            limit=max_candidates,
        )
        cities = data.get("cities") or data.get("items") or []
        return {
            "query": {
                "lat": float(lat),
                "lon": float(lon),
                "year": year,
                "city_type": city_type,
                "limit": limit,
            },
            "candidates_considered": len(cities),
            "cities": cities,
        }
