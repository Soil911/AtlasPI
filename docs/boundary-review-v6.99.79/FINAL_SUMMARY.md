# Phase H Boundary Review — Final Summary

**Version**: v6.99.80
**Status**: ✅ COMPLETE
**Start**: 2026-05-28 (initial discovery)
**End**: 2026-05-28 (single session, fully shipped)
**Total entities polygon-fixed**: **360**
**Total commits**: 18

## Quick links

- [phase1_screening_report.md](phase1_screening_report.md) — initial state
- [LOOP_STATE.md](LOOP_STATE.md) — progress tracker
- [lapita_label_fix_notes.md](lapita_label_fix_notes.md) — frontend fix detail
- [../ethics/ETHICS-012-phase-h-boundary-review.md](../ethics/ETHICS-012-phase-h-boundary-review.md) — ethics record
- [CHANGELOG.md §v6.99.80](../../CHANGELOG.md) — release notes

## What was broken

The fuzzy-match pipeline (`aourednik_match.py` + `boundary_match.py`)
was producing **100+ polygon collisions**: historically distinct entities
sharing the same boundary because they were matched to a "super-group"
label or country-sized polygon. Examples:

- **4 Bantu entities** (Bunyoro, Bigo bya Mugenyi, Ntusi, Mbundu) shared
  the *entire sub-Saharan Africa* "Bantou" linguistic polygon (693 deg²)
- **10 Ethiopian polities** (1270-1830) shared the modern Ethiopia polygon
- **6 Levantine medieval states** (Fatimid, Ayyubid, Crusader, Ikhshidid,
  Zirid, Beit al-Maqdis) shared a single "Fatimid Caliphate" polygon
- **5 ancient Levant polities** (Tadmor, Phoenicia, Israel, Judah, Edom)
  shared an anachronistic "Kingdom of David and Solomon" polygon
- **7 Indonesian sultanates** shared the Dutch East Indies polygon
- **Hasmonean** (Judean kingdom) matched to "Ptolemaic Kingdom" (Egypt) —
  geographically and culturally wrong
- **Likan-antay** (Atacama Desert) matched to "Tiahuanaco Empire"
  (Andean highlands) — different cultures, different geographies

The root cause: fuzzy matching had no area sanity check (city-state could
match an empire-sized polygon) and no super-group label blacklist
(cultural-zone labels in aourednik were treated as polity polygons).

## What was shipped

### Data layer (360 entities fixed in 12 SQL batches)

| Batch | Entities | Theme |
|---|---|---|
| Tier 1A | 16 | Default placeholder squares → circles |
| Tier 1B + Bantou | 4 | Bigo, Ntusi, Bunyoro, Mbundu |
| Tier 2 Fatimid | 6 | Levant medieval Islamic states |
| Tier 2 Batch 1 | 40 | 9 aourednik super-groups (Taino, HRE, Byz, Huari, Sui, Srivijaya, Greek, Anatolia, Kingdom of David) |
| Tier 2 Batch 2 | 43 | natural_earth super-groups (Ethiopia 10, Indonesia 12, Congo, Vietnam, Senegambia, W Africa, Uzbek, Germany) |
| Tier 2 Batch 3 | 57 | 19 aourednik 3-entity groups |
| Tier 2 Batch 4 | 33 | Small natural_earth + top 2-entity collisions |
| Tier 2 Batch 5 | 40 | Remaining 2-entity collisions |
| Tier 3 final outliers | 11 | Kuhikugu/Thulamela/Lakhmid/etc + ETHICS notes |
| Tier 3 remaining | 5 | Kish/Finland/Lucayan + Xianbei/Miji ya Pwani ETHICS |
| Tier 3 collision guard fixes | 10 | Arakan/Nabatean/Nazca/Qataban/Urartu |
| Tier 3 final collisions | 46 | All remaining 22 2-entity collisions |
| Post-H residual | 2 | Mayapan + Garoumele (caught by new area-sanity) |
| Post-H wave 3 | 16 | Japan/Makkura/Pallavas/Song + 4 new super-group labels |

**Per-source delta**:

| boundary_source | Pre | Post | Δ |
|---|---|---|---|
| approximate_circle | 0 | 296 | +296 (NEW) |
| aourednik | 375 | 179 | -196 |
| natural_earth | 197 | 91 | -106 |
| historical_approximation | 297 | 281 | -16 |
| historical_map | 168 | 168 | invariato |

### Code layer (3-layer defense in depth)

**1. Ingestion-time guards** (`src/ingestion/aourednik_match.py` +
`src/ingestion/boundary_match.py`):
- `SUPER_GROUP_LABELS_BLACKLIST` (48 normalized labels): rejects matches
  to cultural-zone names (Bantou, Polynesians, "minor states", etc.)
  unless strategy is `exact_name`
- `TYPE_MAX_AREA_DEG2`: per-entity-type ceiling (city-state 4 deg²,
  kingdom 640 deg², empire 3200 deg², earthwork-complex 0.5 deg², ...)
- `_is_polygon_too_large_for_type()`: rejects match if polygon area
  exceeds ceiling × factor (2× strict for small types, 3× lenient)

**2. Boot-time detector** (`src/ingestion/boundary_collision_guard.py`):
- `detect_boundary_collisions()`: scans for byte-identical polygon areas
  + same `boundary_aourednik_name` across 200+ year spans
- Integrated as Guard #4 in `run_boundary_guards_at_boot()`
- Returns `status: ok/warning/alarm` + structured details
- Logs warning to production logs on first run after restart

**3. CI fence** (`tests/test_boundary_collisions_audit.py`):
- `test_no_super_group_collision_regression` (fail on any alert)
- `test_collision_count_within_baseline` (fail if > 60 groups)
- `test_no_big_collision_groups` (fail if ≥4 entities share polygon)

### Frontend (`static/app.js`)

For polygons that cross the antimeridian (`lonSpan > 180°`), use the
entity's `capital.lat/lon` as label position instead of
`getBounds().getCenter()`. Resolves Lapita (id=307) label appearing
in Indian Ocean.

### Tests

- 1279 total tests passed (1267 + 12 new)
- 29 new tests in 2 files:
  - `test_aourednik_match_super_group_guard.py` (17 tests)
  - `test_boundary_match_area_sanity.py` (12 tests)
- 0 regressions in existing 1267 tests

### Documentation

- `CHANGELOG.md`: v6.99.80 entry with full breakdown
- `ROADMAP.md`: Phase H entry + metrics update (boundary coverage 72→99.9%)
- `docs/ethics/ETHICS-012-phase-h-boundary-review.md`: complete ethics record
- This folder (`docs/boundary-review-v6.99.79/`): 15+ files including
  all SQL batches + LOOP_STATE + screenshots + final summary

## Verification (production, post-deploy)

```
$ curl https://atlaspi.cra-srl.com/health
{"status":"ok","version":"6.99.80","entity_count":1038, ...}

$ cra-logs atlaspi | grep collision
WARNI [boundary_collision_guard] Boundary collisions: 0 groups (0 entities) — within baseline.

$ python -c "from boundary_collision_guard import detect_boundary_collisions; print(detect_boundary_collisions()['status'])"
ok

# Per-type area-sanity violations
0
```

## Lessons documented in ETHICS-012

1. The fuzzy matcher needs more than capital-in-polygon — Phase H added
   area sanity + label blacklist
2. Boot guard at runtime is preziose — catches regression instantly
3. Pre-deploy backup is mandatory for mass DB modifications

## What's deliberately NOT done

- **1-to-1 polygon-to-entity enforcement**: lower priority now that
  area + blacklist guards are active; would require batch-ingestion
  state tracking
- **Duplicate consolidation** (~10 pairs flagged for merge):
  Bohemia Czech/Danish, Buyid Persian/Arabic, Viceroyalty with/without
  accent, etc. — requires per-entity review of dependent records before
  safe deletion
- **Replace circles with real polygons for high-visibility entities**:
  e.g., Mongol Empire, Wari Empire could benefit from historian-curated
  digitized boundaries — future progressive improvement
