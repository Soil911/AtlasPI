# ETHICS-004 — Approximate generated boundaries

> **Note**: this is an English translation of [ETHICS-004-confini-generati-approssimativi.md](ETHICS-004-confini-generati-approssimativi.md). The Italian version is the authoritative one per the AtlasPI documentation policy — if the two diverge, the Italian takes precedence. This translation is provided for non-Italian-reading reviewers.

## Date: 2026-04-12

## Context

Out of 752 entities in the database, 525 had no polygonal boundary at all (`boundary_geojson == null`) and 53 had only a point (`"type": "Point"`). Only 174 entities had real polygons derived from historical cartographic data.

To improve map visualisation and make the database more usable by AI agents, it was decided to generate approximate boundaries for the missing entities.

*(Note: these pre-v6.1.1 figures are preserved for the historical record. After the v6.1.1 enrichment pipeline, 93% of entities carry real boundaries — see METHODOLOGY.md §5.)*

## Risk of distortion

Computationally generated boundaries are NOT real historical data. Presenting them as such would be a falsification of the historical record.

Specific risks:
- A user could confuse an approximate boundary with verified historical data
- Estimated sizes by entity type are statistical averages, not real measurements
- Empires and kingdoms had irregular boundaries dictated by geography, wars, and treaties — not by circles around the capital
- Boundaries of nomadic entities (khanates, steppe confederations) were not fixed lines but fluid zones of influence

## Alternatives considered

1. **Generate nothing** — keep only real data.
   Pro: maximum accuracy. Con: 70% of entities invisible on the map.

2. **Generate boundaries and mark them clearly** (the adopted choice).
   Pro: all entities visible, with transparency about data origin.
   Con: risk that the marker is ignored by downstream users.

3. **Use only fixed circles per type**.
   Pro: simpler. Con: even less realistic.

## Adopted choice

Option 2 with the following safeguards:

### `boundary_source` field

Every entity has a `boundary_source` field with one of the following values:
- `"historical_map"` — boundary derived from real historical cartographic data
- `"approximate_generated"` — computationally generated boundary
- `"natural_earth"` — boundary derived from the Natural Earth dataset
- `"aourednik"` — boundary derived from Ourednik's historical-basemaps (v6.1.1+)
- `"academic_source"` — boundary hand-entered from a cited academic publication

### Reduced confidence_score

Entities with approximate boundaries have their `confidence_score` capped at **0.40** to reflect the additional uncertainty. This is a hard ceiling, not a penalty subtracted from a higher score.

### Irregular polygons

Generated boundaries are not perfect circles but irregular polygons with radius variation of ±20-30% at each vertex, to avoid the impression of a precision that does not exist.

### Type-calibrated sizes

Sizes are based on comparative historiographic estimates by entity type and historical period. They do not claim to be accurate for the individual entity.

## Responsible module

- `src/ingestion/boundary_generator.py` — boundary generation
- `src/ingestion/enrich_boundaries.py` — batch enrichment (legacy)
- `src/ingestion/enrich_all_boundaries.py` — v6.1.1 unified pipeline

## CLAUDE.md principles applied

- **Principle 1** (Truth before comfort): approximate boundaries are not presented as real data
- **Principle 3** (Transparency of uncertainty): the `boundary_source` field and the confidence cap document the uncertainty
- **Principle 4** (No bias): sizes are calibrated by type, not by geographic area
