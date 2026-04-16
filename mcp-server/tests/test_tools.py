"""Test suite per atlaspi-mcp.

I test sono volutamente lightweight e non richiedono rete: usano un
client httpx con :class:`httpx.MockTransport` per simulare l'API.

L'unico test che richiede rete e' marcato e skippato di default
(abilitalo con ``ATLASPI_RUN_INTEGRATION=1`` per smoke-test reale).
"""

from __future__ import annotations

import json
import os

import httpx
import pytest

from atlaspi_mcp import __version__
from atlaspi_mcp.client import (
    DEFAULT_BASE_URL,
    AtlasPIClient,
    AtlasPIClientError,
    get_base_url,
)
from atlaspi_mcp.tools import get_tool, get_tools

EXPECTED_TOOL_NAMES = {
    # v0.1 core
    "search_entities",
    "get_entity",
    "snapshot_at_year",
    "nearby_entities",
    "compare_entities",
    "random_entity",
    "get_evolution",
    "dataset_stats",
    # v0.2 events (ETHICS-007/008)
    "search_events",
    "get_event",
    "events_for_entity",
    # v0.2 cities & routes (ETHICS-009/010)
    "search_cities",
    "get_city",
    "search_routes",
    "get_route",
    # v0.2 chains (ETHICS-002/003)
    "search_chains",
    "get_chain",
    "entity_predecessors",
    "entity_successors",
    # v0.2 composite
    "what_changed_between",
    # v0.3 unified timeline + fuzzy search
    "full_timeline_for_entity",
    "fuzzy_search",
    "nearest_historical_city",
    # v0.4 events for map + on this day
    "events_for_map",
    "on_this_day",
}


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #


def _mock_transport(handler) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


def _client_with_handler(handler) -> AtlasPIClient:
    transport = _mock_transport(handler)
    httpx_client = httpx.AsyncClient(
        base_url="https://atlaspi.test",
        transport=transport,
    )
    return AtlasPIClient(base_url="https://atlaspi.test", client=httpx_client)


# ------------------------------------------------------------------ #
# Test base                                                           #
# ------------------------------------------------------------------ #


def test_package_version() -> None:
    """La versione del package e' esposta come stringa semver-like."""
    assert isinstance(__version__, str)
    assert __version__.count(".") >= 2


def test_client_initializes() -> None:
    """Il client di default usa la base URL pubblica di produzione."""
    client = AtlasPIClient()
    try:
        assert client.base_url == DEFAULT_BASE_URL
    finally:
        # client istanziato senza event loop: chiusura best-effort
        client._owns_client = False  # noqa: SLF001 — evita warning su unawaited close


def test_base_url_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """``ATLASPI_API_URL`` viene rispettata e lo slash finale rimosso."""
    monkeypatch.setenv("ATLASPI_API_URL", "https://staging.atlaspi.example/")
    assert get_base_url() == "https://staging.atlaspi.example"

    client = AtlasPIClient()
    try:
        assert client.base_url == "https://staging.atlaspi.example"
    finally:
        client._owns_client = False  # noqa: SLF001


def test_base_url_default_when_env_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Una env var vuota equivale a 'non impostata'."""
    monkeypatch.setenv("ATLASPI_API_URL", "   ")
    assert get_base_url() == DEFAULT_BASE_URL


# ------------------------------------------------------------------ #
# Tools                                                               #
# ------------------------------------------------------------------ #


def test_tool_list_complete() -> None:
    """Tutti e 25 i tools canonici v0.4 sono registrati."""
    names = {t.name for t in get_tools()}
    assert names == EXPECTED_TOOL_NAMES, (
        f"Missing or unexpected tools: {names ^ EXPECTED_TOOL_NAMES}"
    )
    # Bonus: nessun duplicato
    assert len(get_tools()) == len(EXPECTED_TOOL_NAMES)
    # v0.4 additions: esattamente 25 tools
    assert len(names) == 25


def test_search_entities_tool_schema() -> None:
    """Lo schema di search_entities espone tutti i filtri attesi."""
    tool = get_tool("search_entities")
    schema = tool.input_schema

    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False

    props = schema["properties"]
    for field in ("name", "year", "type", "continent", "status", "limit", "offset"):
        assert field in props, f"missing property {field} in search_entities schema"

    # status e' un enum vincolato ai valori dell'API
    assert set(props["status"]["enum"]) == {"confirmed", "uncertain", "disputed"}

    # year accetta a.C. (interi negativi)
    assert props["year"]["minimum"] < 0
    assert props["year"]["maximum"] >= 2000


def test_required_params_for_path_tools() -> None:
    """I tools che mappano path params dichiarano i required corretti."""
    assert get_tool("get_entity").input_schema["required"] == ["entity_id"]
    assert get_tool("snapshot_at_year").input_schema["required"] == ["year"]
    assert get_tool("get_evolution").input_schema["required"] == ["entity_id"]
    assert set(get_tool("compare_entities").input_schema["required"]) == {"id1", "id2"}
    assert set(get_tool("nearby_entities").input_schema["required"]) == {"lat", "lon"}
    # v0.2 additions
    assert get_tool("get_event").input_schema["required"] == ["event_id"]
    assert get_tool("get_city").input_schema["required"] == ["city_id"]
    assert get_tool("get_route").input_schema["required"] == ["route_id"]
    assert get_tool("get_chain").input_schema["required"] == ["chain_id"]
    assert get_tool("entity_predecessors").input_schema["required"] == ["entity_id"]
    assert get_tool("entity_successors").input_schema["required"] == ["entity_id"]
    assert get_tool("events_for_entity").input_schema["required"] == ["entity_id"]
    assert set(get_tool("what_changed_between").input_schema["required"]) == {
        "year1", "year2",
    }
    # v0.3
    assert get_tool("full_timeline_for_entity").input_schema["required"] == ["entity_id"]
    assert get_tool("fuzzy_search").input_schema["required"] == ["q"]
    assert set(get_tool("nearest_historical_city").input_schema["required"]) == {
        "lat", "lon",
    }


def test_descriptions_are_substantial() -> None:
    """Le descrizioni MCP devono essere abbastanza ricche da guidare l'agente."""
    for tool in get_tools():
        assert len(tool.description) > 80, (
            f"description for {tool.name} is too short: {tool.description!r}"
        )


# ------------------------------------------------------------------ #
# Handler con transport mockato                                       #
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_search_entities_handler_calls_correct_endpoint() -> None:
    """search_entities chiama /v1/entity con i query params corretti."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(
            200,
            json={"count": 0, "limit": 10, "offset": 0, "entities": []},
        )

    client = _client_with_handler(handler)
    try:
        tool = get_tool("search_entities")
        result = await tool.handler(
            client,
            {"name": "Roma", "year": -100, "limit": 10},
        )
    finally:
        await client.aclose()

    url = captured["url"]
    assert "/v1/entity" in url
    assert "name=Roma" in url
    assert "year=-100" in url
    assert "limit=10" in url
    assert result["entities"] == []


@pytest.mark.asyncio
async def test_dataset_stats_handler() -> None:
    """dataset_stats chiama /v1/stats e ritorna il payload tale-quale."""
    payload = {
        "total_entities": 747,
        "avg_confidence": 0.6,
        "year_range": {"min": -65000, "max": 2014},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/stats"
        return httpx.Response(200, json=payload)

    client = _client_with_handler(handler)
    try:
        result = await get_tool("dataset_stats").handler(client, {})
    finally:
        await client.aclose()

    assert result == payload


@pytest.mark.asyncio
async def test_search_events_handler_calls_correct_endpoint() -> None:
    """search_events chiama /v1/events con i filtri corretti."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"total": 0, "events": []})

    client = _client_with_handler(handler)
    try:
        result = await get_tool("search_events").handler(
            client,
            {"event_type": "GENOCIDE", "year_min": 1900, "year_max": 2000},
        )
    finally:
        await client.aclose()

    url = captured["url"]
    assert "/v1/events" in url
    assert "event_type=GENOCIDE" in url
    assert "year_min=1900" in url
    assert "year_max=2000" in url
    assert result["events"] == []


@pytest.mark.asyncio
async def test_search_chains_handler() -> None:
    """search_chains chiama /v1/chains con chain_type filter."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"total": 0, "chains": []})

    client = _client_with_handler(handler)
    try:
        result = await get_tool("search_chains").handler(
            client,
            {"chain_type": "IDEOLOGICAL"},
        )
    finally:
        await client.aclose()

    assert "/v1/chains" in str(captured["url"])
    assert "chain_type=IDEOLOGICAL" in str(captured["url"])
    assert result["chains"] == []


@pytest.mark.asyncio
async def test_entity_predecessors_handler() -> None:
    """entity_predecessors mappa sul path corretto."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        return httpx.Response(
            200,
            json={"entity_id": 42, "entity_name": "X", "predecessors": []},
        )

    client = _client_with_handler(handler)
    try:
        result = await get_tool("entity_predecessors").handler(
            client, {"entity_id": 42}
        )
    finally:
        await client.aclose()

    assert captured["path"] == "/v1/entities/42/predecessors"
    assert result["predecessors"] == []


@pytest.mark.asyncio
async def test_search_routes_involves_slavery_filter() -> None:
    """search_routes propaga il flag involves_slavery (ETHICS-010)."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"total": 0, "routes": []})

    client = _client_with_handler(handler)
    try:
        await get_tool("search_routes").handler(
            client, {"involves_slavery": True, "route_type": "SEA"}
        )
    finally:
        await client.aclose()

    url = str(captured["url"])
    assert "/v1/routes" in url
    # httpx serialises bool as "True"/"False" — accept either casing
    assert "involves_slavery=" in url
    assert "route_type=SEA" in url


@pytest.mark.asyncio
async def test_what_changed_between_composes_two_snapshots() -> None:
    """what_changed_between chiama snapshot(year1) e snapshot(year2) e diffa."""
    seen_years: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        # Path atteso: /v1/snapshot/{year}
        parts = request.url.path.strip("/").split("/")
        year = int(parts[-1])
        seen_years.append(year)
        if year == 100:
            entities = [
                {"id": 1, "name_original": "Imperium Romanum"},
                {"id": 2, "name_original": "漢朝"},
            ]
        else:  # year 500
            entities = [
                {"id": 1, "name_original": "Imperium Romanum"},
                {"id": 3, "name_original": "Imperium Romaniae"},
            ]
        return httpx.Response(200, json={"year": year, "entities": entities})

    client = _client_with_handler(handler)
    try:
        result = await get_tool("what_changed_between").handler(
            client, {"year1": 100, "year2": 500}
        )
    finally:
        await client.aclose()

    assert sorted(seen_years) == [100, 500]
    appeared_ids = [e["id"] for e in result["appeared"]]
    disappeared_ids = [e["id"] for e in result["disappeared"]]
    assert appeared_ids == [3]
    assert disappeared_ids == [2]
    assert result["persisted_ids"] == [1]
    assert result["count"]["appeared"] == 1
    assert result["count"]["disappeared"] == 1
    assert result["count"]["persisted"] == 1


@pytest.mark.asyncio
async def test_what_changed_between_rejects_equal_years() -> None:
    """year1 == year2 deve essere rifiutato."""
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        return httpx.Response(200, json={"entities": []})

    client = _client_with_handler(handler)
    try:
        with pytest.raises(ValueError):
            await get_tool("what_changed_between").handler(
                client, {"year1": 100, "year2": 100}
            )
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_full_timeline_handler() -> None:
    """full_timeline_for_entity chiama /v1/entities/{id}/timeline."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["url"] = str(request.url)
        return httpx.Response(
            200,
            json={
                "entity_id": 42,
                "entity_name": "Test",
                "entity_type": "empire",
                "counts": {
                    "events": 0,
                    "territory_changes": 0,
                    "chain_transitions": 0,
                    "total": 0,
                },
                "timeline": [],
            },
        )

    client = _client_with_handler(handler)
    try:
        result = await get_tool("full_timeline_for_entity").handler(
            client, {"entity_id": 42}
        )
    finally:
        await client.aclose()

    assert captured["path"] == "/v1/entities/42/timeline"
    assert result["timeline"] == []


@pytest.mark.asyncio
async def test_fuzzy_search_handler() -> None:
    """fuzzy_search chiama /v1/search/fuzzy con la query e i filtri."""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["url"] = str(request.url)
        return httpx.Response(
            200,
            json={
                "query": "safavid",
                "count": 1,
                "results": [
                    {
                        "id": 1,
                        "name_original": "دولت صفویه",
                        "matched_name": "دولت صفویه",
                        "matched_is_original": True,
                        "score": 0.817,
                    }
                ],
            },
        )

    client = _client_with_handler(handler)
    try:
        result = await get_tool("fuzzy_search").handler(
            client, {"q": "safavid", "limit": 5, "min_score": 0.4}
        )
    finally:
        await client.aclose()

    assert captured["path"] == "/v1/search/fuzzy"
    url = str(captured["url"])
    assert "q=safavid" in url
    assert "limit=5" in url
    assert "min_score=0.4" in url
    assert result["count"] == 1


@pytest.mark.asyncio
async def test_nearest_historical_city_sorts_by_distance() -> None:
    """nearest_historical_city calcola haversine e ordina per distanza."""
    # Roma: 41.9, 12.5
    # Candidati: Napoli (40.85, 14.26), Milano (45.46, 9.19), Firenze (43.77, 11.25)
    # Distanza attesa da Roma: Napoli (~190km) < Firenze (~230km) < Milano (~480km)
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/cities"
        return httpx.Response(
            200,
            json={
                "total": 3,
                "cities": [
                    {
                        "id": 1,
                        "name_original": "Neapolis",
                        "lat": 40.85,
                        "lon": 14.26,
                        "city_type": "PORT",
                    },
                    {
                        "id": 2,
                        "name_original": "Mediolanum",
                        "lat": 45.46,
                        "lon": 9.19,
                        "city_type": "CAPITAL",
                    },
                    {
                        "id": 3,
                        "name_original": "Florentia",
                        "lat": 43.77,
                        "lon": 11.25,
                        "city_type": "TRADE_HUB",
                    },
                ],
            },
        )

    client = _client_with_handler(handler)
    try:
        result = await get_tool("nearest_historical_city").handler(
            client, {"lat": 41.9, "lon": 12.5, "year": 100, "limit": 3}
        )
    finally:
        await client.aclose()

    assert result["count"] == 3
    names = [c["name_original"] for c in result["cities"]]
    # Napoli è la più vicina a Roma, Milano la più lontana
    assert names == ["Neapolis", "Florentia", "Mediolanum"]
    assert result["cities"][0]["distance_km"] < result["cities"][1]["distance_km"]
    assert result["cities"][1]["distance_km"] < result["cities"][2]["distance_km"]
    # Tutte le distanze devono essere in km sensati (<1000 km per Italia centrale)
    for c in result["cities"]:
        assert 0 < c["distance_km"] < 1000


@pytest.mark.asyncio
async def test_client_raises_on_http_error() -> None:
    """4xx/5xx vengono normalizzati in AtlasPIClientError."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="Not found")

    client = _client_with_handler(handler)
    try:
        with pytest.raises(AtlasPIClientError) as excinfo:
            await client.get_entity(999_999_999)
    finally:
        await client.aclose()

    assert excinfo.value.status_code == 404


# ------------------------------------------------------------------ #
# Integrazione opzionale (skippata senza network esplicito)           #
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get("ATLASPI_RUN_INTEGRATION") != "1",
    reason="integration test disabled (set ATLASPI_RUN_INTEGRATION=1 to enable)",
)
async def test_integration_real_api() -> None:
    """Smoke test contro l'API live https://atlaspi.cra-srl.com."""
    async with AtlasPIClient() as client:
        stats = await client.stats()
    assert "total_entities" in stats
    assert isinstance(stats["total_entities"], int)
    # Il dato deve essere serializzabile in JSON (requisito MCP)
    json.dumps(stats)
