"""Server MCP atlaspi-mcp.

Espone i tools definiti in :mod:`atlaspi_mcp.tools` su stdio usando la
libreria ufficiale ``mcp`` (Anthropic).

L'entry point :func:`main` e' invocato sia da ``python -m atlaspi_mcp``
che dal console_script ``atlaspi-mcp`` definito in pyproject.toml.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from atlaspi_mcp import __version__
from atlaspi_mcp.client import AtlasPIClient, AtlasPIClientError, get_base_url
from atlaspi_mcp.tools import ToolDefinition, get_tool, get_tools

logger = logging.getLogger("atlaspi_mcp")


def _build_mcp_tool(definition: ToolDefinition) -> Tool:
    """Converte una :class:`ToolDefinition` interna nel tipo MCP ``Tool``."""
    return Tool(
        name=definition.name,
        description=definition.description,
        inputSchema=definition.input_schema,
    )


def _format_payload(payload: Any) -> str:
    """Serializza un payload arbitrario in JSON pretty per il modello.

    Usa ``ensure_ascii=False`` per preservare nomi storici non latini
    (es. arabo, cinese, cirillico) cosi' come arrivano dall'API.
    """
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)


def _format_error(exc: Exception) -> str:
    """Formatta un errore in modo che l'agente AI possa leggerlo."""
    if isinstance(exc, AtlasPIClientError):
        if exc.status_code is not None:
            return f"AtlasPI API error (HTTP {exc.status_code}): {exc}"
        return f"AtlasPI API error: {exc}"
    return f"Unexpected error in atlaspi-mcp tool: {type(exc).__name__}: {exc}"


def build_server(client: AtlasPIClient | None = None) -> Server:
    """Costruisce e configura l'oggetto ``Server`` MCP.

    Il parametro ``client`` permette l'iniezione di un client custom
    (utile nei test). In produzione il server costruisce il proprio
    client al momento dell'avvio.
    """
    server: Server = Server("atlaspi-mcp")
    shared_client = client

    @server.list_tools()
    async def _list_tools() -> list[Tool]:
        return [_build_mcp_tool(t) for t in get_tools()]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        try:
            definition = get_tool(name)
        except KeyError:
            return [TextContent(type="text", text=f"Unknown tool: {name!r}")]

        active_client = shared_client or AtlasPIClient()
        try:
            payload = await definition.handler(active_client, arguments or {})
            return [TextContent(type="text", text=_format_payload(payload))]
        except Exception as exc:  # noqa: BLE001 — ritorniamo l'errore al modello
            logger.exception("tool %s failed", name)
            return [TextContent(type="text", text=_format_error(exc))]
        finally:
            if shared_client is None:
                await active_client.aclose()

    return server


async def _run() -> None:
    """Loop principale: stdio transport + MCP server."""
    logger.info(
        "atlaspi-mcp v%s starting (base_url=%s)", __version__, get_base_url()
    )
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Entry point sincrono per console_scripts e ``python -m``."""
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.info("atlaspi-mcp stopped by user")


if __name__ == "__main__":
    main()
