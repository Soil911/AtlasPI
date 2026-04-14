# atlaspi-mcp

[![PyPI version](https://img.shields.io/pypi/v/atlaspi-mcp.svg)](https://pypi.org/project/atlaspi-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/atlaspi-mcp.svg)](https://pypi.org/project/atlaspi-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The **first MCP server for historical geography**. Wraps
[AtlasPI](https://atlaspi.cra-srl.com), a structured historical-geographic
database (700+ geopolitical entities across 65,000 years), so any MCP-compatible
client — Claude Desktop, Claude Code, Cursor, Zed, etc. — can answer questions
like *"What empire ruled Egypt in 300 BC?"* with sourced, structured data
instead of hallucinating.

---

## What is AtlasPI?

AtlasPI is a structured historical-geographic database, designed to be consumed
by AI agents. It provides coordinates, GeoJSON boundaries and historical
metadata of geopolitical entities in any era. Live API and docs:
**https://atlaspi.cra-srl.com**.

This package (`atlaspi-mcp`) is the official
[Model Context Protocol](https://modelcontextprotocol.io) bridge.

---

## Install

```bash
pip install atlaspi-mcp
```

Requires Python **3.10+**.

---

## Configuration

### Claude Desktop

Edit your `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`,
Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "atlaspi": {
      "command": "python",
      "args": ["-m", "atlaspi_mcp"]
    }
  }
}
```

Restart Claude Desktop. The 8 AtlasPI tools will appear in the tools menu.

### Claude Code

Add the server to your project or user MCP config:

```bash
claude mcp add atlaspi -- python -m atlaspi_mcp
```

Or edit `~/.claude/mcp.json` (or the project-local `.mcp.json`) directly:

```json
{
  "mcpServers": {
    "atlaspi": {
      "command": "python",
      "args": ["-m", "atlaspi_mcp"]
    }
  }
}
```

### Pointing to a custom AtlasPI instance

By default the server talks to the public production API
(`https://atlaspi.cra-srl.com`). To target a self-hosted or staging instance,
set the `ATLASPI_API_URL` environment variable:

```json
{
  "mcpServers": {
    "atlaspi": {
      "command": "python",
      "args": ["-m", "atlaspi_mcp"],
      "env": {
        "ATLASPI_API_URL": "https://your-atlaspi.example.com"
      }
    }
  }
}
```

---

## Tools exposed

| Tool                | What it does                                                          |
|---------------------|-----------------------------------------------------------------------|
| `search_entities`   | Filter entities by name, year, type, continent, status                |
| `get_entity`        | Full detail (boundary, capital, sources) for an entity by ID          |
| `snapshot_at_year`  | All entities active in a given year (optionally by region/type)       |
| `nearby_entities`   | Entities near a (lat, lon) coordinate, optionally pinned to a year    |
| `compare_entities`  | Side-by-side comparison of two entities by ID                         |
| `random_entity`     | Random entity, with optional filters (great for exploration)          |
| `get_evolution`     | Timeline of territorial changes for an entity                         |
| `dataset_stats`     | Aggregate stats: totals per type, continent, status, year coverage    |

---

## Example prompts

Try these in Claude Desktop / Claude Code once the server is configured:

- *"What empire ruled Egypt in 300 BC?"*
- *"Compare the Roman Republic and the Byzantine Empire."*
- *"What was near coordinates 41.9, 12.5 in 100 AD?"*
- *"Show me the political snapshot of Europe in 1500."*
- *"Pick a random Asian khanate and tell me its history."*
- *"How did the Ottoman Empire's territory evolve over time?"*

The agent will combine multiple tools (e.g. `snapshot_at_year` -> `get_entity`
-> `get_evolution`) and answer with citations from the underlying dataset.

---

## For AI agents

AtlasPI is built specifically for retrieval by LLM agents. Each record exposes:

- `name_original` + `name_original_lang` (always the local/historical name)
- `name_variants[]` (other languages, with sources)
- `boundary_geojson` (GeoJSON polygon, ready for spatial reasoning)
- `confidence_score` (0.0 -> 1.0 — surface uncertainty, do not fake certainty)
- `sources[]` (citable references)
- `acquisition_method` for territorial events (conquest, treaty, dynastic, ...)

Workflow tip: when the user asks an open-ended historical question, call
`dataset_stats` once to ground the model on coverage, then chain
`search_entities` -> `get_entity` -> `get_evolution` for a full answer.

---

## Local testing

```bash
# install in editable mode with dev deps
pip install -e ".[dev]"

# run the unit tests
pytest

# (optional) run the live integration smoke test
ATLASPI_RUN_INTEGRATION=1 pytest -k integration

# launch the server manually (it speaks MCP over stdio)
python -m atlaspi_mcp
```

---

## Links

- AtlasPI live API: https://atlaspi.cra-srl.com
- AtlasPI source code: https://github.com/Soil911/AtlasPI
- Model Context Protocol: https://modelcontextprotocol.io

---

## License

MIT — see [LICENSE](./LICENSE).

The AtlasPI dataset itself follows an open-core model; check the main repo
for dataset licenses and attribution requirements.
