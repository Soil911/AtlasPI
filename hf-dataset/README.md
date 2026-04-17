---
license: apache-2.0
task_categories:
- question-answering
- text-retrieval
- zero-shot-classification
language:
- en
- multilingual
tags:
- history
- geography
- geojson
- historical-geography
- boundaries
- empires
- kingdoms
- ai-agents
- mcp
- digital-humanities
pretty_name: AtlasPI Historical Geography
size_categories:
- 1K<n<10K
configs:
- config_name: entities
  data_files: "entities.jsonl"
- config_name: events
  data_files: "events.jsonl"
- config_name: periods
  data_files: "periods.jsonl"
- config_name: chains
  data_files: "chains.jsonl"
---

# AtlasPI — Historical Geography Dataset

**862 historical geopolitical entities · 490 events · 48 periods · 94 dynasty chains · 110 cities · 41 trade routes**

The first open dataset specifically designed for AI agents working on
historical geography questions. Apache 2.0 licensed. Includes real GeoJSON
boundaries from academic sources, not placeholder polygons.

**Temporal range**: 4500 BCE → 2024 CE
**Geographic coverage**: all inhabited continents (Asia 31%, Africa 18%,
Americas 17%, Europe 17%, Middle East 11%, Oceania 2%)

## What makes this different from Wikidata/Natural Earth

| | Wikidata | Natural Earth | AtlasPI |
|---|---|---|---|
| Historical boundaries | ❌ | ❌ (modern only) | ✅ |
| Temporal dimension (BCE → 2024) | Partial | ❌ | ✅ |
| One-call world snapshot | ❌ (SPARQL) | ❌ | ✅ |
| Cross-referenced dynasty chains | Partial | ❌ | ✅ |
| Ethical framings per entity | ❌ | ❌ | ✅ |
| Native-language primary names | Partial | ❌ | ✅ |
| Free REST API + MCP server | ❌ | ❌ | ✅ |
| Academic sources per record | Partial | ❌ | ✅ 2,400+ |

## Example use cases for AI agents

1. **"What was the world like in 1250 CE?"** → one API call returns periods,
   entities, events, cities, chains — all active that year.
2. **"Find entities similar to the Roman Empire"** → weighted similarity over
   entity type, temporal overlap, duration, confidence, status.
3. **"On this day in history (14 July)"** → returns Bastille Day + other events
   across centuries sharing that date.
4. **"Compare the Aztec Empire and Mughal Empire"** → side-by-side structured
   response.
5. **"Which historical periods did the Byzantine Empire overlap with?"** →
   returns periods across multiple regions.

## Dataset structure

### `entities.jsonl` (862 records)

```json
{
  "id": 1,
  "name_original": "Imperium Romanum",
  "name_original_lang": "la",
  "entity_type": "empire",
  "year_start": -27,
  "year_end": 476,
  "capital": {"name": "Roma", "lat": 41.9028, "lon": 12.4964},
  "boundary_geojson": {"type": "MultiPolygon", "coordinates": [...]},
  "boundary_source": "natural_earth",
  "confidence_score": 0.95,
  "status": "confirmed",
  "name_variants": [
    {"name": "Roman Empire", "lang": "en"},
    {"name": "Ῥωμαϊκὴ Αὐτοκρατορία", "lang": "grc"}
  ],
  "sources": [...],
  "ethical_notes": "..."
}
```

### `events.jsonl` (490 records)

```json
{
  "id": 123,
  "name_original": "Armistice de Compiègne",
  "name_original_lang": "fr",
  "event_type": "TREATY",
  "year": 1918,
  "month": 11,
  "day": 11,
  "iso_date": "1918-11-11",
  "location_name": "Rethondes, France",
  "location_lat": 49.4241,
  "location_lon": 2.9013,
  "main_actor": "Marshal Ferdinand Foch ...",
  "description": "...",
  "confidence_score": 1.0,
  "ethical_notes": "...",
  "sources": [...]
}
```

### `periods.jsonl` (48 records)

Historical epochs with region scope, historiographic notes, and alternative
names (e.g., "Dark Ages" → deprecated label for "Early Middle Ages").

### `chains.jsonl` (94 records)

Dynasty / succession chains with explicit transition_type per link (CONQUEST,
SUCCESSION, REVOLUTION, etc.). No euphemisms.

## Ethical principles baked into the data

- **ETHICS-001**: Primary names in native script (Mēxihcah not "Aztec";
  Tawantinsuyu not "Inca"; 漢朝 not "Han Dynasty")
- **ETHICS-002**: Conquests labeled CONQUEST, not softened to "succession"
- **ETHICS-007**: Event types include GENOCIDE, COLONIAL_VIOLENCE,
  ETHNIC_CLEANSING — academic terminology, no euphemisms
- **ETHICS-010**: Trade routes involving slavery flagged explicitly

When using this dataset in downstream models or applications, preserve
these distinctions. Don't collapse native names to colonial exonyms.

## Access

### Via REST API (no download needed)
```python
import requests
snap = requests.get("https://atlaspi.cra-srl.com/v1/snapshot/year/1250").json()
```

### Via Python SDK
```bash
pip install atlaspi-client
```
```python
from atlaspi import AtlasPI
client = AtlasPI()
snap = client.snapshot(year=1250)
```

### Via MCP server (Claude Desktop / Claude Code)
```bash
pip install atlaspi-mcp
```

## Data sources

- Natural Earth (public domain): ne_110m_admin_0_countries
- aourednik/historical-basemaps (CC BY 4.0): 54 period snapshots
- Academic citations: Cambridge Histories, Oxford Handbooks, regional specialists

## Citation

```bibtex
@dataset{atlaspi2026,
  title = {AtlasPI: Historical Geography Dataset for AI Agents},
  author = {AtlasPI Project},
  year = {2026},
  url = {https://atlaspi.cra-srl.com},
  license = {Apache-2.0}
}
```

## Links

- **REST API**: https://atlaspi.cra-srl.com
- **Docs**: https://atlaspi.cra-srl.com/docs
- **Source**: https://github.com/Soil911/AtlasPI
- **License**: Apache 2.0
