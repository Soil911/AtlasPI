# ETHICS-003 — Contemporary disputed territories and competing denominations

> **Note**: this is an English translation of [ETHICS-003-territori-contestati-attuali.md](ETHICS-003-territori-contestati-attuali.md). The Italian version is the authoritative one per the AtlasPI documentation policy — if the two diverge, the Italian takes precedence. This translation is provided for non-Italian-reading reviewers.

**Date**: 2026-04-11
**Status**: Accepted
**Author**: Clirim
**Impact**: High — defines how AtlasPI represents territorial disputes that are still active today.

## The problem

Some territories' status is currently contested by states, local populations, international bodies, or competing historiographies. Reducing these cases to a single representation would turn the database into an instrument of political arbitration.

Examples:

- Palestine / Israel
- Crimea
- Kosovo
- Taiwan
- Western Sahara

## Decision

When a dispute is active in the present:

- no single denomination has absolute priority
- the record must include all relevant official denominations
- every denomination must carry political context, temporal context, and a source
- boundaries must be able to hold multiple competing geometries
- the record's status must explicitly reflect the dispute

Required minimum fields:

- `status = "disputed"`
- `contested_names[]`
- `contested_boundaries[]`
- `claims[]`
- `sources[]`
- `confidence_score`

## Rationale

An honest historical-geographic database does not artificially simplify live disputes. It makes competing claims, their sources, and the limits of each representation explicit.

## Open edge cases

- Disputes without uniform international recognition
- Names used by local communities but absent from state-level documentation
- Representation of `de facto` entities versus `de jure` entities

## Code impact

Every endpoint that returns disputed territories must:

1. Explicitly signal `status = "disputed"`
2. Return all relevant denominations
3. Avoid normalisations that would hide active conflicts
4. Carry a `# ETHICS: see ETHICS-003` comment at the relevant code path

## Enforcement in the v6.1.1 enrichment pipeline

Independently of match quality at any upstream source (Natural Earth, Ourednik's historical-basemaps, or academic sources), any entity with `status = "disputed"` has its `confidence_score` capped at **0.70**. This is enforced in both `_apply_natural_earth_match` and `_apply_aourednik_match` inside `src/ingestion/enrich_all_boundaries.py`, and is verified by `tests/test_ethical.py::test_disputed_entities_have_low_confidence`.

The cap reflects the principle that territorial legitimacy and geometric fidelity are orthogonal: a high-quality polygon does not grant epistemic weight to a legally contested claim.
