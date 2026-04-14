# ETHICS-002 — Disputed boundaries and methods of acquisition

> **Note**: this is an English translation of [ETHICS-002-confini-e-conquiste.md](ETHICS-002-confini-e-conquiste.md). The Italian version is the authoritative one per the AtlasPI documentation policy — if the two diverge, the Italian takes precedence. This translation is provided for non-Italian-reading reviewers.

**Date**: 2026-04-11
**Status**: Accepted
**Author**: Clirim
**Impact**: High — defines how conquests and conflicts are represented.

## The problem

Historical boundaries are never neutral lines. They represent wars, imposed treaties, deportations, and the erasure of entire peoples. A database that shows only the geographic polygon without context is technically accurate but historically dishonest.

A concrete danger: an AI agent generating a map of the Roman Empire might do so in a neutral or celebratory tone, without the user understanding that those boundaries were reached through the military conquest of dozens of peoples.

## Decision

Every entity has `territory_changes[]` with these mandatory types:

```
CONQUEST_MILITARY   = military conquest
TREATY              = treaty (even if imposed)
PURCHASE            = purchase
INHERITANCE         = inheritance
REVOLUTION          = internal revolution
COLONIZATION        = colonization of inhabited territories
ETHNIC_CLEANSING    = documented ethnic cleansing
GENOCIDE            = recognised genocide
CESSION_FORCED      = forced cession
LIBERATION          = liberation from occupation
UNKNOWN             = unknown (to be minimised)
```

Example — Roman conquest of Gaul:

```json
{
  "year": -51,
  "region": "Gaul",
  "change_type": "conquest_military",
  "description": "Conquest by Julius Caesar (58-50 BCE). Ancient sources estimate 1-3 million dead. Modern historiography considers the figures probably exaggerated but indicative of large-scale violence.",
  "population_affected": 1000000,
  "sources": ["Caesar, De Bello Gallico",
              "Goldsworthy, Caesar (2006)"],
  "confidence_score": 0.75
}
```

## Application rules

DO NOT use euphemistic language:
- "pacification" → use "military conquest" or "repression"
- "civilisation" → use "colonisation" with context
- "discovery" for already-inhabited lands → never use this term

Include demographic data when available.
Include the perspective of the conquered when possible.
For events recognised as genocides, use the correct term.

## Code impact

```python
# ETHICS: every territorial change must have an explicit change_type.
# Do not use language that minimises violent conquests.
# See ETHICS-002.

if change.change_type == "UNKNOWN":
    logger.warning(
        f"Territory change for {entity_id} has unknown type. "
        "Review historical sources before publishing."
    )
```
