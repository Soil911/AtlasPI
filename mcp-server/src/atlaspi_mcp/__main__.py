"""Entry point per `python -m atlaspi_mcp`.

Avvia il server MCP su stdio. Tutta la logica e' in `server.main`.
"""

from atlaspi_mcp.server import main

if __name__ == "__main__":
    main()
