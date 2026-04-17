# atlaspi-client

Official Python client for the **AtlasPI Historical Geography API** — free,
public, no-auth REST API with 862 historical entities, 490 events, 94 dynasty
chains from 4500 BCE to 2024.

## Install

```bash
pip install atlaspi-client
```

## Quick start

```python
from atlaspi import AtlasPI

client = AtlasPI()  # defaults to https://atlaspi.cra-srl.com

# What was happening in 1250?
snapshot = client.snapshot(year=1250)
for period in snapshot["periods"]["items"]:
    print(f"{period['name']} ({period['region']})")

# Find similar entities
similar = client.entities.similar(entity_id=1, limit=5)
for ent in similar["similar"]:
    print(ent["name_original"], ent["similarity_score"])

# Events on a specific calendar day
today = client.events.on_this_day("07-14")  # Bastille Day
for event in today["events"]:
    print(f"{event['year']}: {event['name_original']}")

# Batch fetch (N entities in one round-trip)
batch = client.entities.batch([1, 2, 3, 42, 100])
print(f"Got {batch['found']} of {batch['requested']} entities")

# Full detail with all fields
entity = client.entities.get(1)
print(f"{entity['name_original']} ({entity['year_start']}-{entity['year_end']})")
print(f"Boundary: {entity['boundary_source']} ({entity['confidence_score']})")
```

## Async support

```python
import asyncio
from atlaspi import AsyncAtlasPI

async def main():
    async with AsyncAtlasPI() as client:
        snap = await client.snapshot(year=1500)
        similar = await client.entities.similar(entity_id=1)

asyncio.run(main())
```

## Key endpoints

The client mirrors AtlasPI's endpoint taxonomy:

- `client.entities.*` — entities (list, get, batch, similar, periods, events, etc.)
- `client.events.*` — events (list, get, on_this_day, at_date, periods)
- `client.periods.*` — periods (list, get, by_slug, at_year)
- `client.chains.*` — dynasty chains
- `client.cities.*` — cities
- `client.routes.*` — trade routes
- `client.search.*` — fuzzy + advanced search
- `client.snapshot()` — world snapshot at year
- `client.stats()` — aggregate statistics
- `client.export.*` — GeoJSON, CSV bulk export

See [API docs](https://atlaspi.cra-srl.com/docs) for the full endpoint catalog.

## License

Apache 2.0.

## Source

- GitHub: https://github.com/Soil911/AtlasPI
- API: https://atlaspi.cra-srl.com
- Issues: https://github.com/Soil911/AtlasPI/issues
