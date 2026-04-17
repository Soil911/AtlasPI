# AtlasPI v6.33.0 — SDKs, batch endpoint, metrics, discoverability

Hey there — here's what's new.

## 📦 Official SDKs published

```bash
pip install atlaspi-mcp       # MCP server (Claude Desktop, Claude Code, Continue)
pip install atlaspi-client    # Python REST SDK
npm install atlaspi-client    # JavaScript/TypeScript SDK (coming next)
```

### Python example

```python
from atlaspi import AtlasPI

client = AtlasPI()

# What was happening in 1250 CE?
snap = client.snapshot(1250)
for period in snap["periods"]["items"]:
    print(f"{period['name']} ({period['region']})")

# Batch fetch — N entities in one round-trip
batch = client.entities.batch([1, 2, 3, 42, 100])
# Events on a calendar day
today = client.events.on_this_day("07-14")  # Bastille Day
```

### JavaScript example

```ts
import { AtlasPI } from "atlaspi-client";

const client = new AtlasPI();
const snap = await client.snapshot(1250);
const batch = await client.entities.batch([1, 2, 3, 42]);
```

### MCP server example (Claude Desktop)

```json
{
  "mcpServers": {
    "atlaspi": {
      "command": "atlaspi-mcp"
    }
  }
}
```

Now your Claude can answer "what empires existed in 300 BCE?" with structured data.

## 🚀 New API endpoints

- **`GET /v1/entities/batch?ids=1,2,3`** — batch fetch (max 100). For timelines and comparisons.
- **`GET /metrics`** — Prometheus-format operational metrics. Scrape-friendly.

## 🤖 AI Co-Founder analyzer: 2 new categories

After this release, the daily AI check (cron @ 04:00 UTC) also looks at:

- **Geometric bugs**: polygons crossing the antimeridian, oversized polygons for entity type, shared polygons across entities. Caught 82 real bugs in first prod run — 53 auto-fixed.
- **Cross-resource consistency**: events linked to entities outside their temporal range, events without sources, inverted year ranges.

The infamous "USA label rendering over France" bug is now a thing of the past, and automated guards prevent recurrence.

## 🔍 AI agent discoverability

Launched to make the project unmistakable to AI agents (ChatGPT mistakenly called it an "internal corporate portal" — now it's explicit):

- `/llms.txt` — AI-agent sitemap standard
- `/.well-known/ai-plugin.json` — OpenAI plugin spec
- `/.well-known/mcp.json` — MCP discovery manifest
- `/about` — public explainer page
- `/faq` — FAQ with FAQPage JSON-LD

## 📊 Dataset stats

- **862** historical entities
- **497** events (+22 this release)
- **55** historical periods (+7)
- **94** dynasty chains
- **46.7%** date coverage for on-this-day
- **2,400+** academic source citations

## 🧪 Quality

- **1043 tests** passing
- **52/52 endpoints** smoke test passing
- **Zero known bugs** (geometric, consistency, endpoint level)
- **9 AI analyzers** running daily
- **Startup guards** for boundary integrity

## 🛠️ Infrastructure

- Daily cron (04:00 UTC): analyze → implement-accepted → smoke test
- GitHub Actions CI/CD: lint + test on every push, auto-publish on tag
- PyPI Trusted Publishers for both Python packages

## 📝 Full changelog

See [CHANGELOG.md](CHANGELOG.md) for complete list of changes.

## 🔗 Links

- **API**: https://atlaspi.cra-srl.com
- **Docs**: https://atlaspi.cra-srl.com/docs
- **About**: https://atlaspi.cra-srl.com/about
- **FAQ**: https://atlaspi.cra-srl.com/faq
- **Interactive map**: https://atlaspi.cra-srl.com/app
- **PyPI packages**:
  - https://pypi.org/project/atlaspi-client/
  - https://pypi.org/project/atlaspi-mcp/

Thanks for reading. If you use AtlasPI in your project, open an issue and tell us — we love seeing what people build.
