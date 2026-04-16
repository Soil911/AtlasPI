"""atlaspi-mcp — MCP server per AtlasPI.

Espone gli endpoint REST di AtlasPI (https://atlaspi.cra-srl.com) come
tools del Model Context Protocol, utilizzabili da Claude Desktop, Claude
Code e qualsiasi altro client MCP-compatibile.

Per evitare import pesanti al solo `import atlaspi_mcp`, l'API pubblica
si limita ai metadati. I sotto-moduli (server, client, tools) vanno
importati esplicitamente quando servono.
"""

__version__ = "0.6.1"

__all__ = ["__version__"]
