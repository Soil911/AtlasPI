# Lapita Label Fix — v6.99.79 (Phase H Tier 1C)

**Status**: ✅ COMPLETED in commit `1930fdd`
**Affected entities**: id=307 Lapita + any other polygon with longitude span > 180°
**Type**: Frontend (Leaflet label positioning), no DB migration required

## Problem

Lapita (id=307) is an Austronesian Lapita culture (1600 BCE - 500 BCE) covering
Bismarck Archipelago → Solomons → Vanuatu → New Caledonia → Fiji → Samoa → Tonga.

Its polygon is correctly stored as a MultiPolygon split across the antimeridian:
```json
{
  "type": "MultiPolygon",
  "coordinates": [
    [[[145.0,-2.0],[178.5,-12.0],[178.5,-22.0],[155.0,-22.0],[145.0,-12.0],[145.0,-2.0]]],
    [[[-180.0,-12.0],[-172.0,-15.0],[-172.0,-22.0],[-180.0,-22.0],[-180.0,-12.0]]]
  ]
}
```

Part 1 covers W Pacific (PNG → Fiji), part 2 covers E of dateline (Samoa/Tonga).
This is the standard GeoJSON representation for antimeridian-crossing polygons.

However, Leaflet's `layer.getBounds().getCenter()` computes the centroid of a
flat 2D bounding box (`xmin=-180, xmax=178.5`), giving:

```
center = ((-180 + 178.5) / 2, (-22 + -2) / 2) = (-0.75, -12)
```

That's longitude **-0.75°W** (Gulf of Guinea, Africa) for an entity that
should be labeled in Vanuatu. The previous PostGIS `ST_Centroid` reported
`(117°E, -14°S)` (Indian Ocean) — different algorithm, similar wrong-place
result.

## Solution

Detect antimeridian-crossing polygons by their bounding-box longitude span
exceeding 180° (impossible for any single normal polygon), then use the
entity's declared capital coordinates as the label position.

```javascript
// static/app.js (Phase H change)
const bounds = layer.getBounds();
const lonSpan = bounds.getEast() - bounds.getWest();
let center;
if (lonSpan > 180 && e.capital && e.capital.lat != null && e.capital.lon != null) {
  // Antimeridian crosser — flat-bbox center is geographically wrong.
  // Use capital coordinates as label anchor.
  center = L.latLng(e.capital.lat, e.capital.lon);
} else {
  center = bounds.getCenter();
}
```

## Why this fix is safe

- **Narrow trigger**: only activates for `lonSpan > 180°`, which only occurs
  for genuine antimeridian crossers (no false positives on normal polygons)
- **Fallback to old behavior**: if `e.capital.lat/lon` is null (rare for
  legitimate political entities), falls back to `bounds.getCenter()` — old
  behavior preserved
- **No DB change**: works entirely client-side using existing API response
  structure (`e.capital = {name, lat, lon}` already serialized)

## Affected entities

Currently in the DB only Lapita (id=307) has `lonSpan > 180`. Other Pacific
entities with multi-polygon split (e.g., Saudeleur on Pohnpei, Naoero,
Sau o Futuna) have their parts in the same hemisphere as the capital, so
their bounds-center is already correct.

In the future, when adding entities like Russian Federation, Fiji
(Eastern division), Kiribati, USA (with Aleutians + Alaska),
the same logic will route labels to capitals automatically without
further changes.

## Verification

Tested in production at https://atlaspi.cra-srl.com/app?year=-1500
after `cra-deploy atlaspi`:
- Lapita label rendered in DOM
- Position calculated from `e.capital = {lat: -17.7333, lon: 168.3167}`
  = Vanuatu (correct)
- Previous Indian-Ocean misplacement resolved

## Related code

- `static/app.js` line ~1437-1452 (Phase H change)
- `src/ingestion/fix_antimeridian_and_wrong_polygons.py` —
  `MANUALLY_CURATED_IDS` includes Lapita (id=307), preserving its
  carefully-curated split polygon from auto-reset
- API response already includes capital lat/lon — no migration needed
