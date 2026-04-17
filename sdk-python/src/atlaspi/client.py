"""Synchronous and asynchronous HTTP client for AtlasPI.

Both clients share the same endpoint taxonomy; the async version uses
httpx.AsyncClient internally.
"""

from __future__ import annotations

from typing import Any

import httpx

DEFAULT_BASE_URL = "https://atlaspi.cra-srl.com"
DEFAULT_TIMEOUT = 30.0


class AtlasPIError(Exception):
    """Raised on network or HTTP errors."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


# ─── Resource namespaces (sync) ─────────────────────────────────────


class _EntitiesNS:
    def __init__(self, parent: AtlasPI) -> None:
        self._p = parent

    def list(self, **params: Any) -> dict:
        """GET /v1/entities — filter by year, status, entity_type, continent, bbox, search, limit, offset."""
        return self._p._get("/v1/entities", params)

    def get(self, entity_id: int) -> dict:
        """GET /v1/entities/{id} — full detail."""
        return self._p._get(f"/v1/entities/{int(entity_id)}")

    def batch(self, ids: list[int]) -> dict:
        """GET /v1/entities/batch?ids=1,2,3 — fetch multiple in one request (max 100)."""
        return self._p._get(
            "/v1/entities/batch",
            {"ids": ",".join(str(int(i)) for i in ids)},
        )

    def similar(self, entity_id: int, *, limit: int = 10, min_score: float = 0.3) -> dict:
        """GET /v1/entities/{id}/similar — top-N similar entities."""
        return self._p._get(
            f"/v1/entities/{int(entity_id)}/similar",
            {"limit": limit, "min_score": min_score},
        )

    def events(self, entity_id: int) -> dict:
        """GET /v1/entities/{id}/events — events linked to this entity."""
        return self._p._get(f"/v1/entities/{int(entity_id)}/events")

    def periods(self, entity_id: int, *, region: str | None = None) -> dict:
        """GET /v1/entities/{id}/periods — historical periods overlapping entity's lifespan."""
        return self._p._get(
            f"/v1/entities/{int(entity_id)}/periods",
            {"region": region} if region else None,
        )

    def successors(self, entity_id: int) -> dict:
        """GET /v1/entities/{id}/successors — chain successors."""
        return self._p._get(f"/v1/entities/{int(entity_id)}/successors")

    def predecessors(self, entity_id: int) -> dict:
        """GET /v1/entities/{id}/predecessors — chain predecessors."""
        return self._p._get(f"/v1/entities/{int(entity_id)}/predecessors")

    def timeline(self, entity_id: int) -> dict:
        """GET /v1/entities/{id}/timeline — unified timeline for entity."""
        return self._p._get(f"/v1/entities/{int(entity_id)}/timeline")

    def nearby(self, *, lat: float, lon: float, year: int, radius_km: int | None = None) -> dict:
        """GET /v1/nearby — entities near given coordinates at year."""
        params = {"lat": lat, "lon": lon, "year": year}
        if radius_km is not None:
            params["radius_km"] = radius_km
        return self._p._get("/v1/nearby", params)


class _EventsNS:
    def __init__(self, parent: AtlasPI) -> None:
        self._p = parent

    def list(self, **params: Any) -> dict:
        """GET /v1/events — filter by year, year_range, event_type, continent."""
        return self._p._get("/v1/events", params)

    def get(self, event_id: int) -> dict:
        """GET /v1/events/{id} — full event detail."""
        return self._p._get(f"/v1/events/{int(event_id)}")

    def on_this_day(self, mm_dd: str) -> dict:
        """GET /v1/events/on-this-day/{mm-dd} — events on a calendar day (e.g. '07-14')."""
        return self._p._get(f"/v1/events/on-this-day/{mm_dd}")

    def at_date(self, iso_date: str) -> dict:
        """GET /v1/events/at-date/{date} — events on a specific date ('YYYY-MM-DD')."""
        return self._p._get(f"/v1/events/at-date/{iso_date}")

    def date_coverage(self) -> dict:
        """GET /v1/events/date-coverage — which MM-DD dates have events."""
        return self._p._get("/v1/events/date-coverage")

    def periods(self, event_id: int, *, region: str | None = None) -> dict:
        """GET /v1/events/{id}/periods — periods containing this event's year."""
        return self._p._get(
            f"/v1/events/{int(event_id)}/periods",
            {"region": region} if region else None,
        )


class _PeriodsNS:
    def __init__(self, parent: AtlasPI) -> None:
        self._p = parent

    def list(self, **params: Any) -> dict:
        """GET /v1/periods — filter by region, period_type, year, status."""
        return self._p._get("/v1/periods", params)

    def get(self, period_id: int) -> dict:
        """GET /v1/periods/{id} — full period detail."""
        return self._p._get(f"/v1/periods/{int(period_id)}")

    def by_slug(self, slug: str) -> dict:
        """GET /v1/periods/by-slug/{slug} — e.g. 'bronze-age', 'edo-period'."""
        return self._p._get(f"/v1/periods/by-slug/{slug}")

    def at_year(self, year: int, *, region: str | None = None) -> dict:
        """GET /v1/periods/at-year/{year} — periods active in a specific year."""
        return self._p._get(
            f"/v1/periods/at-year/{int(year)}",
            {"region": region} if region else None,
        )

    def types(self) -> dict:
        """GET /v1/periods/types — enum of period types."""
        return self._p._get("/v1/periods/types")

    def regions(self) -> dict:
        """GET /v1/periods/regions — enum of region scopes."""
        return self._p._get("/v1/periods/regions")


class _ChainsNS:
    def __init__(self, parent: AtlasPI) -> None:
        self._p = parent

    def list(self, **params: Any) -> dict:
        return self._p._get("/v1/chains", params)

    def get(self, chain_id: int) -> dict:
        return self._p._get(f"/v1/chains/{int(chain_id)}")

    def types(self) -> dict:
        return self._p._get("/v1/chains/types")


class _CitiesNS:
    def __init__(self, parent: AtlasPI) -> None:
        self._p = parent

    def list(self, **params: Any) -> dict:
        return self._p._get("/v1/cities", params)

    def get(self, city_id: int) -> dict:
        return self._p._get(f"/v1/cities/{int(city_id)}")

    def types(self) -> dict:
        return self._p._get("/v1/cities/types")


class _RoutesNS:
    def __init__(self, parent: AtlasPI) -> None:
        self._p = parent

    def list(self, **params: Any) -> dict:
        return self._p._get("/v1/routes", params)

    def get(self, route_id: int) -> dict:
        return self._p._get(f"/v1/routes/{int(route_id)}")

    def types(self) -> dict:
        return self._p._get("/v1/routes/types")


class _SearchNS:
    def __init__(self, parent: AtlasPI) -> None:
        self._p = parent

    def fuzzy(self, q: str, *, limit: int | None = None) -> dict:
        """GET /v1/search/fuzzy — multi-script fuzzy name match."""
        params: dict[str, Any] = {"q": q}
        if limit is not None:
            params["limit"] = limit
        return self._p._get("/v1/search/fuzzy", params)

    def advanced(self, q: str, **params: Any) -> dict:
        """GET /v1/search/advanced — unified search across resource types."""
        return self._p._get("/v1/search/advanced", {"q": q, **params})

    def autocomplete(self, q: str, *, limit: int | None = None) -> dict:
        """GET /v1/search — quick autocomplete."""
        params: dict[str, Any] = {"q": q}
        if limit is not None:
            params["limit"] = limit
        return self._p._get("/v1/search", params)


class _ExportNS:
    def __init__(self, parent: AtlasPI) -> None:
        self._p = parent

    def geojson(self) -> dict:
        """GET /v1/export/geojson — full FeatureCollection."""
        return self._p._get("/v1/export/geojson")

    def csv_raw(self) -> str:
        """GET /v1/export/csv — returns CSV text."""
        return self._p._get_text("/v1/export/csv")

    def timeline(self) -> dict:
        """GET /v1/export/timeline — timeline-formatted JSON."""
        return self._p._get("/v1/export/timeline")


# ─── Sync client ────────────────────────────────────────────────────


class AtlasPI:
    """Synchronous AtlasPI API client."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": user_agent or f"atlaspi-client/0.1.0 (+{DEFAULT_BASE_URL})"},
        )
        self.entities = _EntitiesNS(self)
        self.events = _EventsNS(self)
        self.periods = _PeriodsNS(self)
        self.chains = _ChainsNS(self)
        self.cities = _CitiesNS(self)
        self.routes = _RoutesNS(self)
        self.search = _SearchNS(self)
        self.export = _ExportNS(self)

    def __enter__(self) -> AtlasPI:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    # ─── Shortcuts on the top-level client ──────────────────────────

    def snapshot(self, year: int, *, top_n: int | None = None) -> dict:
        """GET /v1/snapshot/year/{year} — rich world view at a year."""
        params = {"top_n": top_n} if top_n else None
        return self._get(f"/v1/snapshot/year/{int(year)}", params)

    def stats(self) -> dict:
        """GET /v1/stats — aggregate statistics."""
        return self._get("/v1/stats")

    def compare(self, id_a: int, id_b: int) -> dict:
        """GET /v1/compare/{a}/{b} — side-by-side."""
        return self._get(f"/v1/compare/{int(id_a)}/{int(id_b)}")

    def types(self) -> list:
        """GET /v1/types — entity type enum."""
        return self._get("/v1/types")

    def continents(self) -> list:
        """GET /v1/continents — continents with entity counts."""
        return self._get("/v1/continents")

    def health(self) -> dict:
        """GET /health — service health."""
        return self._get("/health")

    # ─── Internal ───────────────────────────────────────────────────

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        clean = _drop_none(params) if params else None
        try:
            r = self._client.get(self.base_url + path, params=clean)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise AtlasPIError(
                f"HTTP {e.response.status_code} for {path}: {e.response.text[:200]}",
                status_code=e.response.status_code,
            ) from e
        except httpx.HTTPError as e:
            raise AtlasPIError(f"Network error for {path}: {e}") from e

    def _get_text(self, path: str) -> str:
        try:
            r = self._client.get(self.base_url + path)
            r.raise_for_status()
            return r.text
        except httpx.HTTPError as e:
            raise AtlasPIError(f"Error fetching {path}: {e}") from e


# ─── Async client (mirrors sync API) ────────────────────────────────


class _AsyncEntitiesNS:
    def __init__(self, parent: AsyncAtlasPI) -> None:
        self._p = parent

    async def list(self, **params: Any) -> dict:
        return await self._p._get("/v1/entities", params)

    async def get(self, entity_id: int) -> dict:
        return await self._p._get(f"/v1/entities/{int(entity_id)}")

    async def batch(self, ids: list[int]) -> dict:
        return await self._p._get(
            "/v1/entities/batch",
            {"ids": ",".join(str(int(i)) for i in ids)},
        )

    async def similar(self, entity_id: int, *, limit: int = 10, min_score: float = 0.3) -> dict:
        return await self._p._get(
            f"/v1/entities/{int(entity_id)}/similar",
            {"limit": limit, "min_score": min_score},
        )

    async def events(self, entity_id: int) -> dict:
        return await self._p._get(f"/v1/entities/{int(entity_id)}/events")

    async def periods(self, entity_id: int, *, region: str | None = None) -> dict:
        return await self._p._get(
            f"/v1/entities/{int(entity_id)}/periods",
            {"region": region} if region else None,
        )


class _AsyncEventsNS:
    def __init__(self, parent: AsyncAtlasPI) -> None:
        self._p = parent

    async def on_this_day(self, mm_dd: str) -> dict:
        return await self._p._get(f"/v1/events/on-this-day/{mm_dd}")

    async def at_date(self, iso_date: str) -> dict:
        return await self._p._get(f"/v1/events/at-date/{iso_date}")

    async def get(self, event_id: int) -> dict:
        return await self._p._get(f"/v1/events/{int(event_id)}")

    async def list(self, **params: Any) -> dict:
        return await self._p._get("/v1/events", params)


class _AsyncPeriodsNS:
    def __init__(self, parent: AsyncAtlasPI) -> None:
        self._p = parent

    async def list(self, **params: Any) -> dict:
        return await self._p._get("/v1/periods", params)

    async def by_slug(self, slug: str) -> dict:
        return await self._p._get(f"/v1/periods/by-slug/{slug}")

    async def at_year(self, year: int) -> dict:
        return await self._p._get(f"/v1/periods/at-year/{int(year)}")


class AsyncAtlasPI:
    """Asynchronous AtlasPI API client (httpx.AsyncClient-based)."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": user_agent or f"atlaspi-client/0.1.0 (+{DEFAULT_BASE_URL})"},
        )
        self.entities = _AsyncEntitiesNS(self)
        self.events = _AsyncEventsNS(self)
        self.periods = _AsyncPeriodsNS(self)

    async def __aenter__(self) -> AsyncAtlasPI:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def snapshot(self, year: int, *, top_n: int | None = None) -> dict:
        params = {"top_n": top_n} if top_n else None
        return await self._get(f"/v1/snapshot/year/{int(year)}", params)

    async def stats(self) -> dict:
        return await self._get("/v1/stats")

    async def health(self) -> dict:
        return await self._get("/health")

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        clean = _drop_none(params) if params else None
        try:
            r = await self._client.get(self.base_url + path, params=clean)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise AtlasPIError(
                f"HTTP {e.response.status_code} for {path}: {e.response.text[:200]}",
                status_code=e.response.status_code,
            ) from e
        except httpx.HTTPError as e:
            raise AtlasPIError(f"Network error for {path}: {e}") from e


def _drop_none(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}
