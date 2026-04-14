# AtlasPI — Methodology

**Version**: 6.1.1
**Last updated**: 2026-04-14
**Status**: this document is the canonical description of how AtlasPI boundaries, names, and confidence scores are produced. Cite it alongside the dataset in academic work.

---

## 1. Scope and intent

AtlasPI is a structured dataset of 747 historical geopolitical entities (4500 BCE → 2024 CE) designed to be consumed by AI agents, ML pipelines, and researchers who need *machine-readable* historical geography.

It is **not** a primary historical source. Every record in AtlasPI is a structured *pointer* to upstream primary and secondary sources. The intended use is:

- Rapid contextual lookup (e.g. "what polities overlap this coordinate in year X?")
- Structured inputs to AI reasoning pipelines
- Teaching, prototyping, and data exploration

For monograph-grade spatial accuracy, researchers should still consult the upstream sources cited in each entity's `sources[]` array and in Section 2 below.

---

## 2. Data sources

### 2.1 Entity records

Entity metadata (name, type, time range, capital, sources, territory changes) is hand-curated in JSON files under `data/entities/`, reviewed against the four ethical principles documented in `CLAUDE.md` and the `docs/ethics/` record set. Each entity requires at least one academic citation in `sources[]`.

### 2.2 Boundary geometry

Boundary polygons come from three tiers, in decreasing order of trust:

| Tier | Source | Coverage | License | Confidence |
|------|--------|----------|---------|------------|
| 1 | **Natural Earth 10m** `ne_10m_admin_0_countries` | Modern states (year_end > 1800 OR year_start > 1700) | Public domain (CC0) | 0.75–0.95 |
| 2 | **aourednik/historical-basemaps** | Pre-1800 historical entities (53 world snapshots, bc123000 → 2010 CE) | CC BY 4.0 | 0.45–0.80 |
| 3 | Deterministic `name_seeded_boundary` (fallback) | Entities with no Tier-1/2 match | Generated | 0.40 |

The raw source datasets are not committed to the repository (~200 MB). They are fetched reproducibly via `scripts/fetch_raw_data.sh`.

### 2.3 Source attribution inside each record

Every entity carries a `boundary_source` enum with one of:

- `historical_map` — extracted from aourednik/historical-basemaps
- `natural_earth` — matched to Natural Earth 10m
- `academic_source` — hand-entered from a cited monograph or atlas
- `approximate_generated` — deterministic fallback polygon
- `aourednik` — matched via the v6.1.1 aourednik matcher (Section 3.2)

When an entity is matched via the aourednik pipeline, the following metadata is added for reproducibility:

- `boundary_aourednik_name` — the exact name of the matched feature in the source GeoJSON
- `boundary_aourednik_year` — the snapshot year used (one of 53 available)
- `boundary_aourednik_precision` — 0, 1, or 2 (see 3.2)

---

## 3. Boundary enrichment pipeline

The enrichment pipeline (`src/ingestion/enrich_all_boundaries.py`) is **monotonic**: it never downgrades an existing real boundary. Pre-existing `historical_map` / `academic_source` / `natural_earth` polygons are skipped.

For every remaining entity, the pipeline attempts:

```
  Step 1 — Natural Earth match         (only if modern-eligible per ETHICS-005)
    ↓  no match
  Step 2 — aourednik temporal match    (any era)
    ↓  no match
  Step 3 — Deterministic fallback      (name_seeded_boundary)
```

### 3.1 Natural Earth match (Tier 1)

Gated by **ETHICS-005**: only entities with `year_end > 1800` OR (`year_end` unknown AND `year_start > 1700`) are eligible. This avoids anachronism (e.g. never draw the Roman Empire with modern Italian borders).

Match strategies, tried in order:

1. **Exact name match** against Natural Earth `NAME`, `NAME_LONG`, `NAME_EN`, `NAME_DE`, `NAME_ES`, `NAME_FR`, `NAME_IT`, `NAME_PT`, `NAME_RU`, `NAME_ZH` fields (cross-language).
2. **Fuzzy match** (token-ratio ≥ 85%) via `rapidfuzz`, when installed.
3. **Capital-in-polygon**: entity's `capital_lat/lon` falls inside a Natural Earth polygon.
4. **ISO-A3 code** when stored on the entity.

Confidence after a successful match: `0.75` for fuzzy/capital strategies, `0.95` for exact name matches. Contested modern territories (Taiwan, Western Sahara, Palestine, Kosovo, Northern Cyprus, Kashmir, Somaliland) receive explicit `ethical_notes` — see `docs/ethics/ETHICS-005-boundary-natural-earth.md`.

### 3.2 aourednik temporal match (Tier 2, v6.1.1)

aourednik/historical-basemaps provides 53 timestamped world GeoJSON files. For each AtlasPI entity, the pipeline:

1. Picks the snapshot closest to `(year_start + year_end) / 2`, bounded by the entity's lifespan.
2. Tries three matchers, in decreasing precision:

| Precision | Strategy | Confidence | Notes |
|-----------|----------|------------|-------|
| 2 | Exact name match (normalized, diacritics-stripped) | 0.80 | Strongest evidence |
| 1 | Fuzzy name match (rapidfuzz ≥ 85%) | 0.65 | Strong but tolerant |
| 0 | Capital-in-polygon + smallest-container preference | 0.55 | Geographic **containment**, not identity |

**Point-in-polygon** is implemented via ray casting (no shapely dependency), with bounding-box pre-filtering and hole exclusion. When multiple polygons contain the capital, the **smallest** polygon wins (duchy > empire, for locality specificity) — this is controlled by `PREFER_SMALLER_POLYGON = True`.

**Fallback tolerance**: if no containment match is found, the nearest centroid within **250 km** of the capital is accepted, capped at confidence 0.45. The previous radius of 1000 km was rejected as too lax after review — it produced ~80% of matches via geographic proximity alone, which was not defensible for academic use.

### 3.3 Deterministic fallback (Tier 3)

For entities with no Tier-1 or Tier-2 match, `name_seeded_boundary` generates a 12-vertex polygon centered on the capital, with deterministic perturbation seeded from the entity name. This polygon is:

- Always tagged `boundary_source = approximate_generated`
- Always capped at `confidence_score = 0.40` (ETHICS-004)
- Labeled in the API response with an explicit `boundary_disclaimer`

Generated boundaries are shape-only placeholders — they must never be used for quantitative spatial analysis.

### 3.4 Ethics cap for disputed entities (ETHICS-003)

Irrespective of match quality, any entity with `status = "disputed"` has its confidence score capped at **0.70**. This reflects the principle that a territorial claim with contested legitimacy cannot carry the same epistemic weight as a uncontested record, even when its geometry is well-established.

This cap is enforced by both `_apply_natural_earth_match` and `_apply_aourednik_match` in the enrichment pipeline, and verified by `tests/test_ethical.py::test_disputed_entities_have_low_confidence`.

---

## 4. Confidence score

Every entity carries a `confidence_score` in `[0.0, 1.0]`:

| Range | Meaning |
|-------|---------|
| 0.90–1.00 | Strong primary sources, uncontested geometry |
| 0.75–0.89 | Good sources, minor uncertainty in geometry or dates |
| 0.50–0.74 | Reasonable sources, noticeable uncertainty — **default for most disputed entities** |
| 0.30–0.49 | Generated/approximate geometry, hand-curated metadata |
| < 0.30 | Fragmentary evidence — entity may be flagged `status: "disputed"` |

Scores are computed from a combination of source tier, boundary source tier, date precision, and manual review. They are reviewable and adjustable — the confidence field is not a black-box ML output.

---

## 5. Current coverage (v6.1.1)

As of the 2026-04-14 deploy:

- **747 entities total**
- **93.0% real boundary coverage** (up from 23% pre-v6.1 pipeline)
- Breakdown: ~28% Natural Earth · ~42% aourednik · ~23% historical_map legacy / academic · ~7% approximate_generated

Full coverage breakdown by entity type and period is in `docs/boundary_coverage_report.md`.

---

## 6. Known limitations

**Be honest about what this dataset cannot do.**

1. **Temporal granularity is coarse.** aourednik provides 53 snapshots over ~125,000 years. For centuries of rapid change (e.g. 19th-century Europe, Warring States China), boundaries are approximated to the nearest available timestamp.
2. **Non-state polities are underrepresented.** Khanates, nomadic confederations, and ecclesiastical territories (caliphates, prince-bishoprics) fit polygon models poorly — many are `approximate_generated`.
3. **Indigenous and pre-colonial boundaries are necessarily interpretive.** Where upstream sources disagree (or don't record), AtlasPI follows the most cited academic convention and flags `status: "disputed"` where warranted.
4. **Capital coordinates are point-stamps, not continuities.** Some capitals moved over an entity's lifespan; the dataset records the most-cited capital, not the full trajectory.
5. **Language and transliteration choices are explicit, not neutral.** Primary names follow the original language (e.g. `Imperium Romanum`, `ᠶᠡᠬᠡ ᠮᠣᠩᠭᠣᠯ ᠤᠯᠤᠰ` for the Mongol Empire); variant names are in `name_variants[]`. See ETHICS-001.

---

## 7. Reproducibility

Every boundary match is reproducible from the repository:

```bash
# Fetch upstream source data (~200 MB)
bash scripts/fetch_raw_data.sh

# Import Natural Earth
python -m src.ingestion.natural_earth_import

# Run the full enrichment pipeline (dry-run first)
python -m src.ingestion.enrich_all_boundaries --dry-run
python -m src.ingestion.enrich_all_boundaries
```

For a single entity, its `boundary_aourednik_name` and `boundary_aourednik_year` metadata (when present) are sufficient to locate the exact source feature in `aourednik/historical-basemaps/geojson/world_{year}.geojson`.

---

## 8. Ethics framework

AtlasPI's methodology is bound by five documented ethics records:

- **ETHICS-001** — Contested names and original-language primacy
- **ETHICS-002** — Representation of conquest and territorial acquisition
- **ETHICS-003** — Contemporary disputed territories (confidence cap ≤ 0.70)
- **ETHICS-004** — Approximate generated boundaries (disclaimer, confidence ≤ 0.40)
- **ETHICS-005** — Natural Earth matching and modern-only gating

Each is published under `docs/ethics/` and is enforced by both automated tests and pipeline-level code paths.

---

## 9. Citing this methodology

When citing AtlasPI in academic work, please cite both the dataset and this methodology document. See [README.md#how-to-cite](../README.md#how-to-cite) for the canonical citation string and BibTeX entry.
