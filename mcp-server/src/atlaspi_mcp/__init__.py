"""atlaspi-mcp — MCP server per AtlasPI.

Espone gli endpoint REST di AtlasPI (https://atlaspi.it) come
tools del Model Context Protocol, utilizzabili da Claude Desktop, Claude
Code e qualsiasi altro client MCP-compatibile.

Per evitare import pesanti al solo `import atlaspi_mcp`, l'API pubblica
si limita ai metadati. I sotto-moduli (server, client, tools) vanno
importati esplicitamente quando servono.
"""

from importlib.metadata import PackageNotFoundError, version as _installed_version

try:
    # Fonte unica di verita': la versione dichiarata in pyproject.toml e
    # pubblicata su PyPI. Prima era hard-coded qui e derivava (0.9.0 mentre
    # il package era gia' 0.10.1), finendo nel log di avvio.
    __version__ = _installed_version("atlaspi-mcp")
except PackageNotFoundError:  # eseguito dai sorgenti senza installazione
    __version__ = "0.0.0+source"

__all__ = ["__version__"]
