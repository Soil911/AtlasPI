# AtlasPI: A Structured Historical Geographic Database for AI Agents

**Status**: pre-submission draft — targeting the [Journal of Open Humanities Data](https://openhumanitiesdata.metajnl.com/) (JOHD) *data paper* format. Not yet submitted. This file is intentionally kept in the repository so reviewers can track its provenance.

**Version referenced**: AtlasPI 6.1.1 (2026-04-14)

---

## Authors

Clirim Ramadani<sup>1</sup>

<sup>1</sup> CRA (Cra Srl), Italy — clirim@cra-srl.com — ORCID: *(to be provided before submission)*

**Corresponding author**: Clirim Ramadani

---

## Abstract

AtlasPI is an open-source, structured dataset of 747 historical geopolitical entities spanning 4500 BCE to 2024 CE, designed to be consumed by AI agents, retrieval-augmented language models, and digital humanities pipelines. Each entity record contains the original-language name, typed entity classification, start and end years, capital coordinates, GeoJSON boundary geometry, an explicit confidence score, 2,200+ academic source citations, and 2,000+ typed territory-change events. Boundaries are assigned through a three-tier pipeline combining Natural Earth (modern states, post-1800), Ourednik's *historical-basemaps* (pre-1800 timestamped snapshots, CC BY 4.0), and deterministic name-seeded fallbacks for entities without upstream matches. The dataset is governed by five documented ethics principles addressing contested names, conquest representation, disputed territories, approximated geometries, and Natural Earth modern-only gating. As of v6.1.1 the dataset reports 93% real-boundary coverage. AtlasPI is distributed under Apache-2.0, accessible via a public REST API, a Model Context Protocol (MCP) server, and bulk GeoJSON/CSV exports. The primary contribution is not novel historical research but a machine-readable, ethically-annotated integration of existing historiographic resources in a format that AI systems can consume at scale.

---

## (1) Overview

### Context

Contemporary AI agents performing historical reasoning face a fragmented geographic landscape: Natural Earth provides machine-readable but ahistorical shapefiles; Wikidata provides structured but spatially-incomplete records; academic atlases encode precise historical boundaries in non-machine-readable form; and specialised datasets (e.g. Ourednik's *historical-basemaps*) are timestamped but lack entity-level metadata such as confidence, source attribution, and typed territorial events.

AtlasPI was built to bridge these resources for machine consumption. The design brief was explicit: an AI agent should be able to answer *"what polities existed in the Balkans in 1400 CE?"* or *"how did the Ottoman Empire's boundaries change between 1500 and 1700?"* via a single structured API call, with every returned datum accompanied by its source citation and confidence score.

### Spatial coverage

Global. All six inhabited continents are represented. Entity density (as of v6.1.1):

| Region | Entities |
|--------|---------:|
| Asia | 195 |
| Europe | 104 |
| Americas | 85 |
| Africa | 78 |
| Middle East | 70 |
| Oceania & Pacific | 8 |

### Temporal coverage

4500 BCE (ancient Mesopotamian polities) through 2024 CE (modern states and disputed territories). Year values are stored as signed integers, with negative values denoting BCE dates. Approximately 76% of entities fall in the 500–2000 CE window, reflecting both source availability and the density of discrete polities in the post-classical era.

### Taxonomic coverage

Fifteen entity types are used: `empire`, `kingdom`, `republic`, `confederation`, `city-state`, `dynasty`, `colony`, `disputed_territory`, `sultanate`, `khanate`, `principality`, `duchy`, `caliphate`, `federation`, `city`. Types are assigned by the curator based on dominant self-description in cited sources, with disputes resolved by explicit notes rather than silent choice (per ETHICS-001).

### Ethical framework

Five records in `docs/ethics/` govern data decisions:

- **ETHICS-001** — Contested names and original-language primacy
- **ETHICS-002** — Representation of conquest and territorial acquisition
- **ETHICS-003** — Contemporary disputed territories (confidence cap ≤ 0.70)
- **ETHICS-004** — Approximate generated boundaries (confidence ≤ 0.40)
- **ETHICS-005** — Natural Earth matching and modern-only temporal gating

Each record names the risk, alternatives considered, decision rationale, and affected code paths.

---

## (2) Method

### Pipeline architecture

Entity records are authored as JSON in `data/entities/batch_*.json`. The enrichment pipeline (`src/ingestion/enrich_all_boundaries.py`) augments each record with a boundary polygon through three tiers:

1. **Natural Earth match (modern entities only).** Gated by ETHICS-005: only entities with `year_end > 1800` or with no `year_end` and `year_start > 1700` are eligible. Match strategies, in priority order: (i) exact name against NAME / NAME_LONG / NAME_EN / NAME_DE / NAME_ES / NAME_FR / NAME_IT / NAME_PT / NAME_RU / NAME_ZH fields; (ii) fuzzy match via `rapidfuzz` at ≥ 85% token ratio; (iii) capital-in-polygon test via ray casting; (iv) ISO-A3 code match when available. Successful matches receive confidence 0.75–0.95.
2. **Ourednik temporal match.** For the remaining entities, the pipeline selects the *historical-basemaps* world-snapshot GeoJSON whose timestamp is closest to the midpoint of the entity's active range, then applies five matchers in priority order: exact name (case-insensitive, accent-folded), `SUBJECTO` match (for vassalage / suzerain relationships), `PARTOF` match (for nested cultural areas), fuzzy name via `rapidfuzz` ≥ 80%, and capital-in-polygon with smallest-polygon preference (a 250 km centroid-nearest fallback is permitted only if all five matchers fail). The final confidence is the mean of (i) a match-quality score (1.0 for exact, 0.90 for fuzzy, 0.60 for capital-in-polygon) and (ii) a `BORDERPRECISION` score read directly from the upstream feature property, where aourednik documents the scale as `1 = approximate`, `2 = moderately precise`, `3 = determined by international law` (0 is a rare legacy edge case). This gives combined confidence in the 0.55–0.90 range. The smallest-polygon rule (a duchy is preferred over an empire if both contain the capital) encodes the assumption that polygon specificity correlates with intended semantic match.
3. **Deterministic fallback.** Remaining entities receive a 12-vertex polygon centered on the capital, with perturbation seeded from the entity name hash. These polygons are always tagged `approximate_generated` and capped at confidence 0.40 (ETHICS-004).

### Sampling strategy

Entity selection is purposive rather than statistical. The curator (CR) targets:

- All widely-recognised empires, caliphates, and large kingdoms of every inhabited region
- Contested and disputed territories with academic attention (to stress-test the ethics framework)
- Entities frequently referenced in AI evaluation corpora (Wikipedia-visible, MMLU-history)
- Regional diversification to avoid Euro-Atlantic bias (see ETHICS-001)

No systematic attempt is made to cover *all* historical polities; the 747-entity population is a curated sample, not a census.

### Quality control

Automated:

- **260 tests** spanning technical (API correctness, pagination, input validation), ethical (ETHICS-001/002/003 enforcement, confidence bands, disputed-entity caps), security (CORS, headers, rate-limit), performance (p95 < 500 ms on most endpoints; see below), data-quality (source completeness, regional diversity, entity type coverage), and provenance (schema exposure of `boundary_source` / aourednik trace fields, upstream precision scale conformance) dimensions.
- **Confidence band enforcement**: disputed entities cannot exceed 0.70 confidence regardless of match quality; generated boundaries cannot exceed 0.40.
- **Idempotent pipeline**: real boundaries (`historical_map`, `academic_source`, `natural_earth`) are never overwritten; only `approximate_generated` can be upgraded.

Manual:

- Every entity record requires ≥ 1 academic source in `sources[]` before acceptance.
- Top-10 entities by academic visibility are periodically spot-checked for boundary fidelity.
- ETHICS records are updated when new cases stress the framework.

### Performance characterisation

Measured against the live production instance at https://atlaspi.cra-srl.com:

| Endpoint | p95 (ms) |
|----------|---------:|
| `/v1/entity` (filtered) | ~180 |
| `/v1/entities/{id}` | ~50 |
| `/v1/nearby` | ~200 |
| `/v1/snapshot/{year}` | ~180 |
| `/v1/export/geojson?geometry=centroid` | < 500 |
| `/v1/export/geojson?geometry=full` (48 MB payload) | < 15,000 |

---

## (3) Dataset description

| Attribute | Value |
|-----------|-------|
| **Object name** | AtlasPI |
| **Data type** | Structured historical geographic database |
| **Format names and versions** | JSON (entity records), GeoJSON (boundaries), SQLite / PostgreSQL (runtime), CSV (export), OpenAPI 3.1 (API schema) |
| **Creation dates** | 2025-11 (v0.0.1) → 2026-04-14 (v6.1.1) |
| **Dataset creators** | Clirim Ramadani (curation, architecture); derived geometries from Natural Earth and Ourednik's *historical-basemaps* |
| **Language** | English (API, code, schema); Italian (internal documentation and ethics records); entity names in the original local language with variant translations |
| **License** | Apache-2.0 (source code and API); entity records CC BY 4.0; derived geometries inherit upstream licenses (Natural Earth public domain; Ourednik CC BY 4.0) |
| **Repository** | https://github.com/Soil911/AtlasPI |
| **Live instance** | https://atlaspi.cra-srl.com |
| **API docs** | https://atlaspi.cra-srl.com/docs (OpenAPI), https://atlaspi.cra-srl.com/redoc |
| **MCP server** | Python package `atlaspi-mcp`, 8 tools (to be published to PyPI) |
| **DOI** | To be minted via Zenodo on first tagged release; `.zenodo.json` included in repository |
| **Publication date** | 2026-04-14 (v6.1.1 production deploy) |

### Record structure

Each entity is a JSON object with the following fields:

- `id` (integer), `name_original` (string), `name_original_lang` (ISO-639 code)
- `entity_type` (one of 15 controlled values), `status` (`confirmed` | `disputed`)
- `year_start`, `year_end` (signed integers; negative = BCE)
- `capital` (object: `name`, `lat`, `lon`)
- `boundary_geojson` (GeoJSON `Polygon` or `MultiPolygon`)
- `boundary_source` (enum: `historical_map` | `natural_earth` | `academic_source` | `approximate_generated` | `aourednik`)
- `boundary_aourednik_name`, `boundary_aourednik_year`, `boundary_aourednik_precision` (reproducibility metadata when matched via Ourednik)
- `confidence_score` (float, 0.0–1.0)
- `name_variants[]` (list of `{name, language}`)
- `territory_changes[]` (typed events: `expansion`, `contraction`, `secession`, etc., with year and source)
- `sources[]` (list of `{citation, source_type}`; `source_type` ∈ `academic`, `primary`, `secondary`, `tertiary`)
- `ethical_notes` (optional string referencing an ETHICS record)

### Reproducibility

```bash
git clone https://github.com/Soil911/AtlasPI.git
cd AtlasPI
bash scripts/fetch_raw_data.sh            # ~200 MB of upstream data
python -m src.ingestion.natural_earth_import
python -m src.ingestion.enrich_all_boundaries --dry-run
python -m src.ingestion.enrich_all_boundaries
```

All pipeline outputs are deterministic for a given input version. The `boundary_aourednik_*` fields allow any boundary to be traced to its source feature and snapshot year.

---

## (4) Reuse potential

AtlasPI is designed for four principal reuse cases:

1. **AI agents and LLM tool use.** The REST API and MCP server expose eight structured tools (entity lookup, temporal snapshots, proximity search, comparison, evolution, aggregation) that are compatible with modern tool-using language models. The dataset is intended as an off-the-shelf geographic-historical tool for digital humanities agents and tutoring systems.
2. **Retrieval-augmented generation.** The small dataset size (< 60 MB with full geometries), rich cross-entity links (`contemporaries`, `related`, `evolution`), and explicit source citations make it suitable for retrieval corpora where factual grounding and provenance matter.
3. **Teaching.** The combination of a visual web map, structured REST API, and open data licensing supports coursework in digital humanities, historical GIS, API design, and data ethics. The documented ethics framework is itself an instructional artefact.
4. **Dataset research.** AtlasPI's three-tier enrichment pipeline and confidence-scoring mechanism are of independent methodological interest to researchers building similar integrated datasets in other domains (e.g. historical biography, epigraphy).

### Known limitations

These limitations are documented in `docs/METHODOLOGY.md §6`:

- Temporal granularity is bounded by the 53 snapshots in the upstream Ourednik dataset.
- Non-state polities (khanates, nomadic confederations, ecclesiastical territories) fit polygon models poorly and are over-represented in the `approximate_generated` tier.
- Pre-colonial and indigenous boundaries are necessarily interpretive; the dataset follows the most-cited academic convention and flags `status: "disputed"` where scholarly disagreement is substantial.
- The 747-entity dataset is a curated sample, not a comprehensive register of all historical polities.
- Capital coordinates are single-point stamps; mobile capitals are represented by their most-cited location.

---

## Acknowledgements

AtlasPI builds on the foundational work of:

- **Natural Earth** (https://www.naturalearthdata.com/) for public-domain vector basemaps.
- **André Ourednik and contributors** for the *historical-basemaps* timestamped snapshots (https://github.com/aourednik/historical-basemaps), released under CC BY 4.0.
- **OpenStreetMap contributors** for geographic reference data under the Open Database License.
- **Wikidata contributors** for structured entity metadata under CC0.

The methodological framing, ethics governance, and ongoing iteration benefit from feedback from colleagues at CRA. Specific academic reviewers and advisors will be acknowledged by name in the final submission.

---

## Competing interests

The author declares no competing interests. CRA (Cra Srl) operates the hosted instance at https://atlaspi.cra-srl.com at its own cost. Potential future premium / enterprise tiers (documented in `ROADMAP.md`) would be offered alongside the open-core dataset released under Apache-2.0 and would not restrict access to the published dataset described in this paper.

---

## Funding

AtlasPI is self-funded by CRA. No external grants have been received to date.

---

## References

*(to be finalised with full bibliographic entries before submission — the list below is indicative)*

- Ourednik, A. (2024). *historical-basemaps* [Data set]. https://github.com/aourednik/historical-basemaps
- Kelso, N. V. & Patterson, T. (2010). Introducing Natural Earth data. *Nacis Newsletter*.
- Anthropic. (2024). *Model Context Protocol specification*.
- FastAPI / Tiangolo (2024). https://fastapi.tiangolo.com/
- Per-entity academic citations are stored in each record's `sources[]` array; ~2,200 distinct citations across the dataset as of v6.1.1.

---

## Submission checklist (internal)

Before submitting to JOHD:

- [ ] ORCID assigned and added to author block
- [ ] DOI minted via Zenodo for cited dataset version
- [ ] Full bibliography formatted in target journal style (APA)
- [ ] Screenshot figure added (web UI + API response JSON side by side)
- [ ] Peer review by ≥ 1 digital humanities scholar before submission
- [ ] Competing-interests paragraph reviewed for completeness
- [ ] Final copy-edit by a native English speaker
