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
    "search_entities",
    "get_entity",
    "snapshot_at_year",
    "nearby_entities",
    "compare_entities",
    "random_entity",
    "get_evolution",
    "dataset_stats",
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
    """Tutti e 8 i tools canonici sono registrati."""
    names = {t.name for t in get_tools()}
    assert names == EXPECTED_TOOL_NAMES, (
        f"Missing or unexpected tools: {names ^ EXPECTED_TOOL_NAMES}"
    )
    # Bonus: nessun duplicato
    assert len(get_tools()) == len(EXPECTED_TOOL_NAMES)


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
