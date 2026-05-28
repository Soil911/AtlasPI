-- Boundary Review v6.99.79 — Tier 1A
-- Replace default placeholder squares (1.0/1.5/2.25/3.0 deg²) with
-- historically realistic circles around capital coordinates.
-- Radius determined by entity type + historical extent research.

BEGIN;

-- Helper function: build circle UPDATE in one call
-- We do it manually per-entity since each has different radius.

-- id=788 Haak'u (Acoma Pueblo, NM) — Pueblo nation ~30km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default 1°×1° placeholder square replaced with 30km capital-based circle. Haak''u (Acoma Pueblo) was a Western Pueblo nation centered on Acoma Mesa, NM — historical influence ~30-50km. Manual review recommended for precise extent.'
WHERE id = 788;

-- id=790 Hopituh Shi-nu-mu (Hopi) — confederation ~80km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 80km circle. Hopituh Shi-nu-mu is the Hopi confederation of pueblos on Black Mesa, AZ — pre-contact range ~80-100km.'
WHERE id = 790;

-- id=938 Paquimé (Casas Grandes, Chihuahua) — site complex ~30km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 30km circle. Paquimé/Casas Grandes was a major Pueblo IV trading center in NW Mexico — direct site ~5km, regional influence ~30-50km.'
WHERE id = 938;

-- id=954 Cañari (pre-Inca Ecuador confederation) — ~100km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 100km circle. Cañari were a pre-Inca confederation in the highlands of Azuay/Cañar/Loja provinces (Ecuador) — Tomebamba capital, extent ~100-150km.'
WHERE id = 954;

-- id=961 Izapa (Soconusco MX) — small site ~15km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 15000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 15000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 15km circle. Izapa was an Olmec-Maya transition ceremonial center (1500 BCE–100 CE) in Chiapas Soconusco — site ~1km², cultural zone ~15km.'
WHERE id = 961;

-- id=965 Quimbaya (Cauca Colombia) — confederation ~80km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 80km circle. Quimbaya were a Middle Cauca culture (CE 1–1500) of central Colombia — known for goldwork; territory along Cauca River ~80-120km.'
WHERE id = 965;

-- id=977 Zazzau (Hausa city-state Zaria) — ~50km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 50km circle. Zazzau (Zaria) is one of the Hausa Bakwai city-states (originally founded ~1000 CE) in N Nigeria — city + hinterland ~50km.'
WHERE id = 977;

-- id=999 Gao-Saney (Niger River Songhai precursor) — city-state ~50km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 50km circle. Gao-Saney was a trans-Saharan trading city (7th c. CE), Songhai precursor on Niger bend — urban + agricultural hinterland ~50km.'
WHERE id = 999;

-- id=1004 Awdaghust (Saharan trade city) — ~50km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 50km circle. Awdaghust was a Saharan trade-route city (Mauritania, 8th–11th c. CE) tributary then conquered by Ghana Empire — city + oasis hinterland ~50km.'
WHERE id = 1004;

-- id=682 Chinook Illahee (Lower Columbia confederation) — ~150km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 150km circle. Chinook Illahee = Chinookan-speaking peoples of Lower Columbia River (WA/OR coast) confederation — riverine extent ~150-200km along Columbia.'
WHERE id = 682;

-- id=881 Ma-i (Mindoro Philippine polity) — ~50km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.4),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 50km circle. Ma-i was a pre-Hispanic polity mentioned in Song dynasty Chinese sources (971 CE) — likely Mindoro island; exact extent debated, confidence kept low.'
WHERE id = 881;

-- id=195 Bēnizàa (Zapotec, Oaxaca valley) — ~80km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 80km circle. Bēnizàa (Zapotec people) were centered in the Valley of Oaxaca with Monte Albán as capital (500 BCE–800 CE) — three-branch valley extent ~80km.'
WHERE id = 195;

-- id=282 Κομμαγηνή (Commagene, Hellenistic kingdom) — ~100km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 100km circle. Commagene was a Hellenistic kingdom (163 BCE–72 CE) in Upper Euphrates region (modern SE Turkey) with Samosata capital — ~100×100km territory.'
WHERE id = 282;

-- id=718 Kitu (Quito region pre-Inca kingdom) — ~50km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.4),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 50km circle. Kitu was a pre-Inca polity in the highland valley of modern Quito (Ecuador) — Quitu-Cara cultural complex, extent debated (~50km highland valley).'
WHERE id = 718;

-- id=934 Ishtmus Zoque (Tehuantepec cultural region) — ~100km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 100km circle. Ishtmus Zoque = Mixe-Zoque speaking cultural region spanning the Isthmus of Tehuantepec (Oaxaca/Veracruz/Chiapas) ~100km radius from Tuxtla.'
WHERE id = 934;

-- id=1011 Essouk-Tadmakka (Saharan trade oasis) — ~30km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1A] Default placeholder square replaced with 30km circle. Essouk-Tadmakka was a Saharan oasis trade city in Adagh des Ifoghas, Mali (8th–13th c. CE) — small city + caravanserai hinterland ~30km.'
WHERE id = 1011;

-- Verify
SELECT id, name_original,
       ROUND(ST_Area(boundary_geom)::numeric, 4) as new_area_deg,
       ST_NPoints(boundary_geom) as npoints,
       boundary_source,
       confidence_score
FROM geo_entities
WHERE id IN (788, 790, 938, 954, 961, 965, 977, 999, 1004, 682, 881, 195, 282, 718, 934, 1011)
ORDER BY id;

COMMIT;
