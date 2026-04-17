# Reddit post drafts for AtlasPI launch

Copy-paste ready. Pick whichever subreddit fits your moment.

---

## 1. r/MachineLearning (3.5M) — posted as [P] or [D]

**Title**: `[P] I built a Historical Geography REST API designed specifically for AI agents — free, Apache 2.0, 862 entities with real GeoJSON boundaries from 4500 BCE to 2024`

**Body**:

I kept running into the same problem when building agentic apps: AI models are great at reasoning about history, but existing geo data is either modern-only (Natural Earth, OSM) or unstructured for spatial queries (Wikidata requires SPARQL, no consistent boundaries).

So I built **AtlasPI** — a REST API + MCP server with:

- **862 historical geopolitical entities** (empires, kingdoms, sultanates, dynasties, confederations)
- **490 historical events** (battles, treaties, genocides, revolutions, epidemics — with academic event types, no euphemisms like "COLONIAL_VIOLENCE" and "GENOCIDE")
- **94 dynasty chains** with explicit transition types (CONQUEST vs SUCCESSION vs REVOLUTION)
- **Real GeoJSON boundaries** from Natural Earth + aourednik/historical-basemaps (CC BY 4.0), not placeholder circles
- **48 historical periods** with region scope (no Eurocentric defaults — "Middle Ages" is labeled europe, "Edo Period" is asia_east)
- **2,400+ academic citations** baked into every record

Two things I'm proud of:

1. **`GET /v1/snapshot/year/{year}`** — returns entities + events + periods + cities + chains all active at that year in a single call. AI agents answering "what was the world like in 1250" finally have one call instead of five.

2. **`GET /v1/entities/{id}/similar`** — weighted semantic similarity over entity_type (35%), temporal overlap (30%), duration (15%), confidence (10%), status (10%). Lets agents do "find me empires comparable to the Ming Dynasty."

It's also available as an **MCP server** (`pip install atlaspi-mcp`) — 35 tools you can plug directly into Claude Desktop, Claude Code, Continue, or any MCP client.

**Ethics**: native-language primary names (Mēxihcah not "Aztec", Tawantinsuyu not "Inca"), explicit conquest labeling, contested territories with all versions, trade routes involving slavery flagged (ETHICS-010).

Free to use, no login, no API key, Apache 2.0.

- **API**: https://atlaspi.cra-srl.com
- **Interactive map**: https://atlaspi.cra-srl.com/app
- **Docs**: https://atlaspi.cra-srl.com/docs
- **Source**: https://github.com/Soil911/AtlasPI
- **LLMs.txt**: https://atlaspi.cra-srl.com/llms.txt

Would love feedback — especially on what's missing for your agentic use cases.

---

## 2. r/LocalLLaMA (1.6M) — [Resources] or [Tool]

**Title**: `Free MCP server with 862 historical entities + 490 events + real GeoJSON boundaries — plug it into Claude Desktop / your local Llama setup and ask history questions`

**Body**:

Just shipped **atlaspi-mcp** — a Model Context Protocol server that gives your Claude/local LLM setup access to 6,500 years of structured historical geography.

**35 tools** your model can call:

- `snapshot_at_year(1250)` — full world view at a year
- `find_similar_entities(entity_id=1)` — "empires like the Roman Empire"
- `on_this_day("07-14")` — events on a calendar date
- `list_historical_periods(region="asia_east")` — Tang, Song, Ming, Qing, Edo, Heian, ...
- `get_entities_batch([1,2,3,42])` — multi-fetch in one call
- `compare_entities(1, 2)` — side-by-side
- ... 29 more

**Install**:

```bash
pip install atlaspi-mcp
```

Claude Desktop config (`~/.config/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "atlaspi": {
      "command": "atlaspi-mcp"
    }
  }
}
```

Then ask your model things like:
- "Which empires existed in the Mediterranean in 300 BCE?"
- "Which dynasty chains did the Mughal Empire belong to?"
- "What major events happened on 14 July across all centuries?"

Works with Claude Desktop, Claude Code, Continue.dev, and any MCP-compatible client.

**Data is solid**: real historical boundaries (not modern country polygons), 2,400+ academic sources, confidence scores per record, explicit ethical framings (conquests labeled CONQUEST, colonial renamings documented, native-language primary names).

**Also available as**:
- REST API (free, no auth): https://atlaspi.cra-srl.com
- Python SDK: `pip install atlaspi-client`
- Interactive map: https://atlaspi.cra-srl.com/app

**Source**: https://github.com/Soil911/AtlasPI (Apache 2.0)

---

## 3. r/datasets (400k) — [Dataset]

**Title**: `[Dataset] AtlasPI — 862 historical geopolitical entities + 490 events + real GeoJSON boundaries (4500 BCE → 2024 CE), Apache 2.0`

**Body**:

**What**: A structured historical geography dataset designed for AI agents and digital humanities work. Everything that Wikidata doesn't organize well and Natural Earth doesn't cover in the temporal dimension.

**Size**:
- 862 entities (empires, kingdoms, sultanates, republics, chiefdoms, confederations, dynasties, caliphates, khanates, principalities)
- 490 events (battles, treaties, genocides, revolutions, epidemics, famines, intellectual events)
- 48 historical periods (Bronze Age → Cold War, region-scoped)
- 110 cities
- 41 trade routes
- 94 dynasty chains
- 2,400+ academic citations

**What makes it unusual**:
- **Real GeoJSON boundaries** for ~80% of entities (from Natural Earth + aourednik/historical-basemaps, academic sources)
- **Temporal dimension**: 4500 BCE → 2024 CE, with confidence scores
- **Cross-referenced**: entities link to events, events to periods, chains connect entities across time
- **Native-language primary names** (Mēxihcah not "Aztec", 漢朝 not "Han Dynasty")
- **Explicit ethical framings** — event types like GENOCIDE, COLONIAL_VIOLENCE; trade routes flagged for slavery involvement

**Access**:
- REST API (free, no auth): https://atlaspi.cra-srl.com
- Python SDK: `pip install atlaspi-client`
- GeoJSON bulk download: https://atlaspi.cra-srl.com/v1/export/geojson
- HuggingFace dataset: https://huggingface.co/datasets/atlaspi (coming soon)

**License**: Apache 2.0 (code + data)

**Docs**: https://atlaspi.cra-srl.com/about | https://atlaspi.cra-srl.com/docs

Happy to answer questions about data provenance, collection methodology, or specific use cases. Feedback welcome — especially if you spot missing coverage or inaccuracies.

---

## Tips for posting

1. **Post on weekdays 10am-2pm ET** for highest visibility
2. **Respond to early comments** in the first hour (algorithm weighs engagement)
3. **Cross-link but don't spam** — if a post hits r/MachineLearning, let it be for 24h before posting to r/LocalLLaMA
4. **If asked "is this just Wikidata?"** answer with: "No — Wikidata has partial entity metadata but no consistent historical boundaries, no cross-referenced dynasty chains, and no MCP/REST interface. AtlasPI is specifically designed for agentic workflows."
5. **For r/datasets**, use the `[Dataset]` prefix — it's the community norm
6. **For r/MachineLearning**, use `[P]` for Project or `[D]` for Discussion
