# ETHICS-001 — Geographic names: original, imposed, and contested

> **Note**: this is an English translation of [ETHICS-001-nomi-contestati.md](ETHICS-001-nomi-contestati.md). The Italian version is the authoritative one per the AtlasPI documentation policy — if the two diverge, the Italian takes precedence. This translation is provided for non-Italian-reading reviewers.

**Date**: 2026-04-11
**Status**: Accepted
**Author**: Clirim
**Impact**: High — defines how all names are stored.

## The problem

Geographic names are loaded with political history. Every choice of which name to use as "primary" is a position being taken.

Examples:
- Constantinople / Istanbul: same place, different eras
- Bombay / Mumbai: colonial name vs. original local name
- Palestine / Israel: actively contested boundaries
- Precolumbian North America: indigenous names often ignored

## Decision

Adopted data structure:

```python
class EntityName:
    name_original: str          # local name — PRIMARY FIELD
    name_original_lang: str     # ISO 639-1 code
    name_variants: list[NameVariant]

class NameVariant:
    name: str
    lang: str
    period_start: int | None    # year, negative = BCE
    period_end: int | None
    context: str                # e.g. "British colonial name"
    source: str
```

Example — Istanbul:

```json
{
  "name_original": "İstanbul",
  "name_original_lang": "tr",
  "name_variants": [
    {
      "name": "Constantinopolis",
      "lang": "la",
      "period_start": 330,
      "period_end": 1453,
      "context": "Roman-Byzantine name",
      "source": "Enciclopedia Treccani"
    },
    {
      "name": "Byzantium",
      "lang": "la",
      "period_start": -657,
      "period_end": 330,
      "context": "original Greek name of the colony",
      "source": "Thucydides, I.94"
    }
  ]
}
```

## Rationale

The name in the local language has ethical priority over names imposed by external powers. Historically imposed names are not erased — they are present as variants with explicit context.

## Open edge cases

- Names of indigenous territories without written sources → explicit note
- Territories with active disputes today → all official denominations with notes on the disputes (see ETHICS-003)

## Code impact

Any function that returns a geographic name must:
1. Return `name_original` as the primary field
2. Include `name_variants` in the complete output
3. Carry a `# ETHICS: see ETHICS-001` comment
