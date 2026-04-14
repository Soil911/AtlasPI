# Contributing to AtlasPI

Thanks for considering a contribution. AtlasPI is a structured historical
geographic database; its quality depends on careful review by people who
know the history better than any automated pipeline can. Contributions
from historians, geographers, and scholars of any region or period are
especially welcome.

This document covers the three most common contribution types:

1. [Reporting a data issue](#1-reporting-a-data-issue) (wrong boundary,
   wrong name, wrong dates, wrong source)
2. [Proposing a code or schema change](#2-proposing-a-code-or-schema-change)
3. [Adding a new entity or regional batch](#3-adding-a-new-entity-or-regional-batch)

If you are evaluating AtlasPI for a paper, review, or derivative
dataset, see also:

- `README.md` — overview and quick start
- `docs/METHODOLOGY.md` — data pipeline and confidence scoring
- `docs/paper-draft.md` — the JOHD-style data paper draft
- `docs/ethics/` — the five ETHICS records governing data decisions
- `CITATION.cff` — how to cite

---

## 1. Reporting a data issue

> **TL;DR**: open a GitHub issue using the **Boundary / entity correction**
> template. Include one primary source citation.

Almost every contribution starts here. AtlasPI prefers a narrow, citable
correction over a long critique. A good data issue has:

- The entity's `id` or `name_original` (search the API to find it)
- A single, specific claim ("the eastern boundary in 1450 CE should reach
  the Volga, not the Don"; "the capital was *Vijayanagara*, not *Hampi*"; …)
- **At least one primary or recognised academic source** for the correction.
  Wikipedia alone is not sufficient, but a Wikipedia article that cites a
  specific academic source is a fine starting point — include the downstream
  citation.
- For boundary corrections: a pointer to a better polygon source is
  ideal — a Natural Earth field, a Ourednik `historical-basemaps` feature
  name / snapshot year, an academic atlas plate, or a hand-drawn GeoJSON
  attached to the issue.

### Policy on disputed territories

AtlasPI does not arbitrate contemporary territorial disputes. If you
believe an entity's `status: "disputed"` flag is wrong, please read
`docs/ethics/ETHICS-003-disputed-territories.en.md` before opening the
issue. The confidence cap at 0.70 for disputed entities is intentional
and will not be relaxed on a per-entity basis; what can change is the
list of which entities carry the flag.

### What we will not change

- Entity names in their original language (`name_original`) — by design,
  never overridden by a colonial or exonymic form. See ETHICS-001. You
  can add an entry to `name_variants[]` with historical context instead.
- Narrative euphemisms in `territory_changes[]` — the type enum includes
  `CONQUEST_MILITARY`, `GENOCIDE`, `FORCED_MIGRATION`, and similar. We do
  not accept rewrites that soften these to neutral language. See ETHICS-002.

---

## 2. Proposing a code or schema change

- For non-trivial changes (new endpoint, new schema field, new ingestion
  stage), please open an issue describing the design before you write a
  pull request. We'd rather help shape the proposal than reject a finished
  PR.
- All existing tests must pass: `python -m pytest tests/ -q` (260 tests as
  of v6.1.1). New tests are expected for new behaviour.
- Migrations use Alembic (`alembic/versions/`). Additive migrations
  (`batch_alter_table` ADD COLUMN, nullable) are strongly preferred; any
  destructive change needs explicit justification and a documented
  rollback path.
- Python style: the project is conservative — `from __future__ import
  annotations`, explicit `Session` typing, docstrings in Italian for
  internal modules and English for user-facing ones. This mirrors the
  split declared in `CLAUDE.md`.

---

## 3. Adding a new entity or regional batch

Entity records live as JSON in `data/entities/batch_*.json` and are
loaded on an empty database by `src/db/seed.py`. The schema is
documented in `docs/METHODOLOGY.md §3` (record structure) and in
`src/api/schemas.py`.

A minimum acceptable entity record has:

- `name_original`, `name_original_lang`, `entity_type`, `year_start`,
  `year_end` (nullable)
- At least one academic source in `sources[]`
- A capital (`capital_name`, `capital_lat`, `capital_lon`) unless the
  polity genuinely had none
- A `confidence_score` that honestly reflects the source quality; leave
  the boundary to the enrichment pipeline if you are not hand-drawing one
- `status`: `confirmed` unless the polity's territorial claims are
  contemporarily contested (see ETHICS-003)

After adding a batch:

```bash
python -m src.ingestion.enrich_all_boundaries --dry-run
python -m src.ingestion.enrich_all_boundaries
python -m pytest tests/
```

Regional diversity is a design priority (see ETHICS-001). Batches
focused on under-represented regions (pre-colonial Africa, pre-Columbian
Americas, Oceania, non-Han East Asia, Islamic West Africa, etc.) are
particularly welcome.

---

## Pull request checklist

- [ ] Tests pass locally (`python -m pytest tests/ -q`)
- [ ] New tests accompany any new behaviour
- [ ] If the change touches historical representation, an ETHICS record
      is linked or a new one is drafted (see `docs/TEMPLATES.md`)
- [ ] If the change adds a schema field, `docs/METHODOLOGY.md §3` and
      `src/api/schemas.py` are both updated
- [ ] `CHANGELOG.md` has an entry describing the change

---

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md) v2.1.

## Licence

By submitting a contribution you agree it will be licensed under
Apache-2.0 (code and API) or CC BY 4.0 (entity records and derived
geometries), matching the terms of the project.

## Attribution

Reviewers and contributors who provide feedback that materially
improves the dataset or methodology will be named in `ACKNOWLEDGMENTS.md`
with their consent. Anonymity on request is always respected.

## Contact

For questions that are not appropriate as a public issue: clirim@cra-srl.com
