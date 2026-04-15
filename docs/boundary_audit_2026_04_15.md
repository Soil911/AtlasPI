# Boundary Quality Audit — 2026-04-15

Audit script: ad-hoc Python against `data/atlaspi.db` (846 entities, 662 `confirmed`,
28 `disputed`, 156 `uncertain`).

## Executive summary

**63.6% of confirmed entities have low-quality boundaries.** Of 662 confirmed
entities: 247 (37.3%) use `aourednik` polygons flagged as `precision=1`
(approximate, large-scale, often a wrong-entity reuse), and 174 (26.3%) use
`boundary_source='approximate_generated'` — a coarse 13-point polygon generated
from capital coordinates (a rough decagon around the capital). Only 32 confirmed
entities (4.8%) have `precision=3` (international-law-grade) aourednik polygons,
73 (11.0%) have Natural Earth matches, and 133 (20.1%) have `historical_map` tier
shapes. The most serious structural issue: **166 entities share aourednik polygons
with other entities** — 13 distinct confirmed entities all carry the same "Holy
Roman Empire" polygon (Firenze, Pisa, Saxony, Savoy, Bavaria, etc. are all drawn
as the full HRE), 6 carry "Fatimid Caliphate" (including the *Kingdom of
Jerusalem*), 5 carry "Greek city-states" (Sparta, Corinth, Syracuse get the same
generic Greece polygon), and 6 carry "Kingdom of David and Solomon" (including
the city-state Tyre). Two confirmed Fijian confederations have centroids 6,283 km
from their capitals (wrong Natural Earth match). 5 entities store literal 5-point
bounding boxes. 2 confirmed entities (Pechenegs ID 325, Nogai Horde ID 338) have
`boundary_source=NULL` and no geometry at all.

## Top 20 worst offenders

| Entity | Year | Type | Reason |
|---|---|---|---|
| Ṣūr / 𐤑𐤓 (Tyre) [506] | -2750..-332 | city-state | 413,540 km² bbox; shares "Kingdom of David and Solomon" polygon with 5 others |
| Λακεδαίμων (Sparta) [66] | -900..-192 | city-state | 470,252 km² bbox; shares "Greek city-states" polygon with 4 others |
| Κόρινθος (Corinth) [285] | -800..-146 | city-state | 470,252 km² bbox; same "Greek city-states" polygon |
| Συράκουσαι (Syracuse) [286] | -734..-212 | city-state | 213,616 km² bbox; same "Greek city-states" polygon |
| Ṣīdūn / 𐤑𐤃𐤍 (Sidon) [507] | -3000..-332 | city-state | 877,970 km² bbox; shares "Hittites" polygon |
| Repubblica di Firenze [82] | 1115..1532 | republic | shares "Holy Roman Empire" polygon with 12 others |
| Schweizerische Eidgenossenschaft [83] | 1291.. | confederation | shares "Holy Roman Empire" polygon |
| Hanse [87] | 1356..1669 | confederation | shares "Holy Roman Empire" polygon |
| Comune di Pisa [567] | 1000..1406 | republic | shares "Holy Roman Empire" polygon |
| Mark Brandenburg [568] | 1157..1618 | principality | shares "Holy Roman Empire" polygon |
| Herzogtum Sachsen [569] | 804..1296 | duchy | shares "Holy Roman Empire" polygon |
| Herzogtum Baiern [570] | 555..1623 | duchy | shares "Holy Roman Empire" polygon |
| Duche de Savoie [573] | 1003..1720 | duchy | shares "Holy Roman Empire" polygon |
| Markgrafschaft Meissen [577] | 929..1423 | principality | shares "Holy Roman Empire" polygon |
| Landgrafschaft Hessen [578] | 1264..1567 | principality | shares "Holy Roman Empire" polygon |
| Hertogdom Brabant [582] | 1183..1795 | duchy | shares "Holy Roman Empire" polygon |
| Grevskabet Flandern [583] | 862..1795 | principality | shares "Holy Roman Empire" polygon |
| Herzogtum Pommern [681] | 1121..1637 | duchy | shares "Holy Roman Empire" polygon |
| Malo ni Viti (Fiji) [299] | 1815..1874 | confederation | centroid 6,283 km from capital (wrong NE match) |
| Bose Levu Vakaturaga (Fiji) [300] | 1874..2012 | confederation | centroid 6,288 km from capital (wrong NE match) |

### Other notable geometric issues (outside top-20 but structurally broken)

- **İstanbul [3]** (city, confirmed): aourednik polygon is "Phrygians" (-700),
  bbox ~462,000 km² — a historical population, not the city.
- **Igbo-Ukwu [562]** (city, uncertain): aourednik polygon is "Mandes" (900),
  bbox ~4,329,812 km² — essentially West Africa assigned to a single archaeological site.
- **Kongeriket Noreg [60]** (kingdom, uncertain): Natural Earth match returns
  15,817-pair polygon spanning lat -54° to +80° — includes Norwegian dependencies
  (Bouvet Island, Jan Mayen, Svalbard) but merges as a single outline rather than
  the Scandinavian mainland of the *Kongeriket*.
- **Seminole [545]**, **Cherokee [218]**, **USA [245]**: centroids 3,200–3,830 km
  from capitals — the NE polygon for USA uses `(48.05, -120.52)` (Washington State),
  not (38.9, -77.0) (DC); all three are the CONUS+Alaska merged multi-polygon.
- **5 confirmed/disputed entities with literal 5-point box geometries**:
  Republic of Pirates [524], Kurland Colonies [525], Poverty Point [528],
  Kingdom of Quito [530], Wanka/Huanca [531]. All flagged `historical_map` but
  are placeholder rectangles.
- **2 confirmed entities with no boundary at all**: Pechenegs [325], Nogai Ordasy [338].

## Bucket counts (scope of fix work)

| Bucket | Confirmed count | Fix path |
|---|---|---|
| `boundary_source='approximate_generated'` (13-pt buffer) | 174 | Auto: re-run `aourednik_match.py` with year-bracketing + semantic name match |
| `aourednik_precision=1` + shared polygon (same aourednik_name used ≥3×) | ~60 (166 total across all statuses) | Auto/semi: drop the match, fall back to historical_map or manual |
| `aourednik_precision=1` + unshared but generic (e.g. Istanbul→Phrygians) | ~187 | Manual: reviewer must verify each aourednik_name → entity link |
| Natural Earth centroid >2000 km from capital | 9 confirmed | Auto: add centroid-distance validator, clear `boundary_ne_iso_a3` for mismatches |
| 5-point bounding boxes | 5 | Manual: these are already low-confidence; acceptable if flagged clearly |
| NULL boundary_geojson | 2 | Manual: Pechenegs + Nogai need steppe-extent polygons from academic sources |

## Actionable fix paths

1. **Auto-fixable (~180 entities, one pass)**: rewrite `approximate_generated`
   polygons by re-running the aourednik matcher with `year_start ≤ match_year ≤ year_end`
   strictly enforced and a text-similarity threshold between `entity.name_original`
   (or any `name_variants`) and `aourednik_name` ≥ 0.5. Entities that fail the
   stricter match stay flagged as `approximate_generated` but get `status='uncertain'`
   demoted, not `confirmed`.
2. **Auto-deletable (~166 entities)**: any `aourednik_name` used by ≥3 distinct
   entities is almost certainly a wrong reuse — clear `boundary_geojson`,
   `boundary_aourednik_*` for the entity whose `name_original` doesn't text-match the
   aourednik_name. Whitelist exceptions: empires whose vassals legitimately overlap
   (e.g. HRE electors should keep smaller individual polygons, not the HRE outline).
3. **Auto-fixable centroid mismatches (9 entities)**: add a validator to
   `ingestion/aourednik_match.py` and the Natural Earth matcher that rejects any
   polygon whose centroid is >1500 km from `capital_lat/lon`. For USA/Cherokee/Seminole
   the underlying issue is using the full NE `USA` polygon — needs a tighter bbox or a
   historical-map tier polygon.
4. **Manual curation required (~187 entities)**: individually confirmed entities
   where the aourednik polygon is a plausible-but-wrong historical entity
   (Phrygians for Istanbul, Blue Horde for Muscovy, Carolingian Empire for Imperium
   Francorum). These need a human historian pass.
5. **Fiji NE match (2 entities)**: the Natural Earth polygon pulled for Fiji spans
   the antimeridian and the centroid collapses to near Africa — needs antimeridian-safe
   centroid computation OR replacement with a Pacific-local polygon.
6. **Placeholder bboxes + NULL (7 entities)**: demote all 5-point-box entities to
   `status='uncertain'` and add explicit `ethical_notes` saying "boundary is a
   placeholder rectangle, not the actual extent".
