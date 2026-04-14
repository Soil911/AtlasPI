# ETHICS-005 — Natural Earth boundaries and disputed territories

> **Note**: this is an English translation of [ETHICS-005-boundary-natural-earth.md](ETHICS-005-boundary-natural-earth.md). The Italian version is the authoritative one per the AtlasPI documentation policy. If the two diverge, the Italian takes precedence.

**Date**: 2026-04-14
**Status**: Accepted
**Author**: boundary-enrichment pipeline (authored by the project maintainer with Claude Code)
**Impact**: High — defines when and how modern Natural Earth boundaries may be applied to AtlasPI entities, and how disputed territories are handled in that process.

## Context

AtlasPI contains 747 geopolitical entities spanning 4500 BCE to 2024. Before the v6.1.1 enrichment pipeline, only ~23% (174) had real boundaries derived from historical cartographic sources (via Ourednik's `historical-basemaps`). The remaining ~76% had `approximate_generated` boundaries or none at all.

To raise qualitative coverage beyond 60% with real data, a pipeline was introduced that matches *modern* AtlasPI entities against Natural Earth (<https://www.naturalearthdata.com/>), a public-domain (CC0) cartographic dataset of contemporary state boundaries.

## Primary risk: anachronism

Applying modern boundaries to ancient states is a serious historical distortion. Examples of errors to avoid:

- **Imperium Romanum** (27 BCE – 476 CE) → modern Italy: WRONG. The Roman Empire extended from Britain to Mesopotamia.
- **Tawantinsuyu** (Inca, 1438-1533) → modern Peru: WRONG. The empire also covered Ecuador, Bolivia, and parts of Chile and Argentina.
- **Khanate of Persia** → modern Iran: WRONG. The boundaries are profoundly different.

## Decision: eligibility constraint

Only entities that satisfy ONE of the following criteria may be candidates for matching against Natural Earth:

1. **`year_end > 1800`**: the entity ends after the emergence of the modern nation-state system. Example: *Imperio Español* (1492-1976).
2. **`year_end == None` AND `year_start > 1700`**: the entity is "still alive" and originates in the near pre-modern era. Example: *Konungariket Sverige* (1523-present).

For every other entity (`year_end ≤ 1800`), only `name_seeded_boundary` from `boundary_generator.py` is used, with `confidence_score = 0.4` and `boundary_source = "approximate_generated"` (see ETHICS-004).

## Matching strategies (in priority order)

1. **Explicit ISO_A3**: if the AtlasPI entity carries an `iso_a3` field or an `ISO: XYZ` mention in `ethical_notes`, match directly. Confidence: 1.0.
2. **Exact name match**: case-insensitive and accent-folded comparison between `name_original` / `name_variants[]` and the Natural Earth names (`NAME`, `NAME_LONG`, `FORMAL_EN`, `SOVEREIGNT`, and all `NAME_xx` multilingual fields). Confidence: 1.0.
3. **Fuzzy match** (via `rapidfuzz`) at threshold 85%. Uses `MAX(ratio, token_set_ratio, partial_ratio)` for robustness with multi-word names. Confidence: `score / 100`.
4. **Capital-in-polygon**: if the entity's capital (lat/lon) is contained in exactly one modern polygon (no ambiguity), match by geographic inclusion. Confidence: 0.6.

## Secondary risk: disputed territories

Natural Earth marks some territories as contested. When a match lands on one of these, AtlasPI does not pick a side — it documents the dispute.

Explicitly handled disputed ISO codes (`DISPUTED_ISO_CODES` in `boundary_match.py`):

| ISO_A3 | Territory | Dispute |
|--------|-----------|---------|
| TWN | Taiwan | Sovereignty contested with the PRC |
| ESH | Western Sahara | Morocco vs. SADR/Polisario |
| PSE | Palestine | Israeli occupation, UN "observer state" status |
| XKO | Kosovo | Partial recognition (Serbia does not recognise) |
| CYN | Northern Cyprus | Recognised only by Turkey |
| KAS | Kashmir | India–Pakistan–China dispute |
| SOL | Somaliland | De facto independent, unrecognised |

When one of these is matched:

- The AtlasPI entity KEEPS its original `status` (often `disputed`).
- An ethics note is appended to `ethical_notes`: `ETHICS-005: boundary from Natural Earth (ISO XYZ, name). Contested territory — see ETHICS-005-natural-earth-boundaries.*.md`.
- `confidence_score` is not raised above 0.7 even on an exact match, because the cartographic representation itself is contested.

### Special case: Taiwan

AtlasPI may represent Taiwan differently depending on the year:

- As part of the Qing Empire (1683-1895)
- As a Japanese colony (1895-1945)
- As the Republic of China (1912–present)
- In dispute with the PRC (1949–present)

The Natural Earth match provides the *physical* polygon of the island, which is independent of the sovereignty dispute. The dispute itself is documented in `name_variants`, `claims[]`, `ethical_notes`, and `status = 'disputed'`.

### Special case: Israel / Palestine

AtlasPI distinguishes between:

- The modern entity `Israel` (1948–present) → ISO ISR
- The modern entity `State of Palestine` / Palestinian territories → ISO PSE

Natural Earth has both ISR and PSE as distinct features. Matching must be done with CAUTION: if the AtlasPI entity is named, e.g., "فلسطين / ישראל" (dual historical representation), it must be handled manually or left with a generated boundary — automatic matching would force a choice.

## Data transparency

Every boundary added via Natural Earth is tagged with:

```json
{
  "boundary_geojson": { "type": "Polygon|MultiPolygon", ... },
  "boundary_source": "natural_earth",
  "boundary_ne_iso_a3": "ITA",
  "confidence_score": 0.85,
  "ethical_notes": "...ETHICS-005: boundary from Natural Earth..."
}
```

The `boundary_source` field distinguishes:

- `historical_map` — boundary derived from real historical cartographic data
- `natural_earth` — boundary derived from Natural Earth (modern state)
- `aourednik` — boundary from a named feature in Ourednik's timestamped snapshots (v6.1.1+)
- `academic_source` — boundary from academic publications
- `approximate_generated` — boundary generated computationally

## Idempotence

The `enrich_all_boundaries.py` pipeline is idempotent:

- `historical_map` / `academic_source` / `natural_earth` boundaries are NEVER overwritten.
- `approximate_generated` boundaries can be upgraded to `natural_earth` or `aourednik` if a valid match is found (this is a monotonic quality improvement).
- Missing boundaries or `Point` geometries are always regenerated or matched.

## Mandatory backups

Before every modification, the script creates a `.bak` backup next to the original batch file. The backup is overwritten on the next run (it is a "last-run backup", not historical versioning — the latter is handled by git).

## Responsible modules

- `src/ingestion/natural_earth_import.py` — shapefile loader
- `src/ingestion/boundary_match.py` — matching strategies
- `src/ingestion/aourednik_match.py` — temporal matcher for Ourednik's historical-basemaps (v6.1.1)
- `src/ingestion/enrich_all_boundaries.py` — end-to-end pipeline

## Alignment with CLAUDE.md principles

- **Principle 1 (Truth before comfort)**: anachronism is refused even when it would make the dataset "more complete".
- **Principle 2 (No single version of history)**: disputed territories receive explicit notes and are never silently "resolved" by a match.
- **Principle 3 (Transparency of uncertainty)**: `confidence_score` is modulated per strategy (1.0 exact, 0.6 capital-in-polygon, ≤ 0.7 for disputed regardless), `boundary_source` is explicit, `ethical_notes` documents disputes.
- **Principle 4 (No bias)**: the same criteria apply to Italy / Iran / China / USA — no geographic exception.
