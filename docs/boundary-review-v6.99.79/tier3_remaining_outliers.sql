-- Boundary Review v6.99.79 — Tier 3 continuation: remaining outliers

BEGIN;

-- 168 𒆠𒂗𒄀 (Kish, Sumerian city-state) ~60km
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 60000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 60000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier3/kish-fix] Replaced oversized placeholder (11 deg² for a Sumerian city-state) with 60km circle. 𒆠𒂗𒄀 = Kish was a Sumerian city-state (~4500-1900 BCE) on the Euphrates, ~12 km E of Babylon. First Dynasty of Kish was considered most prestigious in early Sumerian king lists; alternate rule between Kish + Uruk + Ur dominated Early Dynastic period.'
WHERE id = 168;

-- 427 Suomen suuriruhtinaskunta (Grand Duchy of Finland) ~350km
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 350000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 350000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier3/finland-fix] Replaced oversized polygon (101 deg² is ~3x too large) with 350km circle around Helsinki. Suomen suuriruhtinaskunta (Grand Duchy of Finland, 1809-1917) was autonomous Russian Empire grand duchy after Finnish War, covered modern Finland (~338,000 km² = 27 deg²); independence proclaimed during Russian Revolution 1917.'
WHERE id = 427;

-- 960 Taino Lucayan (Bahamas archipelago chiefdom) ~250km
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier3/lucayan-fix] Replaced oversized polygon (46 deg² for a Bahamas chiefdom) with 250km circle. Lucayan Taino (~600-1520 CE) were the Bahamas Taino population first contacted by Columbus 1492 at Guanahani (San Salvador); Spanish slave raiders reduced population from ~40,000 to extinction by 1520. ETHICS: Lucayan Taino effectively eradicated by Spanish enslavement within 30 years of contact.'
WHERE id = 960;

-- 290 鲜卑 Xianbei (nomadic confederation) — keep area (nomadic confederations span vast areas)
UPDATE geo_entities SET
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier3-xianbei-note] Polygon kept at 247 deg² — Xianbei (~93-234 CE) were a Proto-Mongolic nomadic confederation in modern Mongolia + Inner Mongolia + N Manchuria after Xiongnu collapse; nomadic confederations legitimately span vast areas. Later Xianbei branches founded the Northern Wei + Western Wei + Northern Zhou + Sui dynasties of N China.'
WHERE id = 290;

-- 418 Miji ya Pwani (Swahili coast confederation) — keep area (genuinely long coast)
UPDATE geo_entities SET
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier3-swahili-note] Polygon kept at 52 deg² — Miji ya Pwani ("coastal cities" in Swahili) refers to the Swahili city-state confederation along E African Indian Ocean coast (Kilwa, Mombasa, Zanzibar, Pate, Mafia, Lamu, Sofala, etc.) from ~800-1505 CE; stretched ~3000 km from Mogadishu to Mozambique. Area appropriate for confederation extent. ETHICS: Portuguese conquest 1505 onwards (da Gama, Almeida, Soares de Albergaria) destroyed many Swahili cities + initiated subordination to European trade.'
WHERE id = 418;

SELECT COUNT(*) FROM geo_entities WHERE id IN (168, 290, 418, 427, 960);

COMMIT;
