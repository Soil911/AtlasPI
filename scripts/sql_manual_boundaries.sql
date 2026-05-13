-- v6.99.28: Manually-curated historical boundaries for 10 entities
-- previously capped at conf=0.5 by startup guard due to wrong-polygon inheritance.
-- These boundaries are approximations based on historiographic consensus —
-- not modern administrative borders. ETHICS: confidence 0.85 reflects the
-- combination of (a) excellent academic source coverage and (b) approximate
-- boundary geometry suitable for a historical reference.

BEGIN;

-- 218 Cherokee (ᏣᎳᎩ) — Southern Appalachians, pre-Removal territory
-- (Western Carolinas, Eastern Tennessee, Northern Georgia, NE Alabama, NW South Carolina)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-85.5,36.6],[-82.3,36.6],[-82.0,35.6],[-82.5,34.8],[-83.4,34.0],[-85.0,33.7],[-86.2,34.3],[-86.5,35.4],[-85.5,36.6]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'ETHICS-002: The Cherokee Nation exemplifies the devastation of US Indian removal policy. Despite adopting Western institutions (written constitution 1827, Sequoyah''s syllabary 1821, settled agriculture, slaveholding plantation economy), they were forcibly removed via the Treaty of New Echota (1835) and Trail of Tears (1838-39), with ~4,000 of 16,000 Cherokees dying en route to Indian Territory. The boundary shown here approximates the pre-Removal Cherokee homeland in the southern Appalachians (modern W North Carolina, E Tennessee, N Georgia, NE Alabama, NW South Carolina) — a historical approximation, not a modern administrative border. [v6.99.28-manual-boundary] Replaced auto-generated capital circle with historically-informed polygon based on 19th-c. ethnographic maps (Mooney 1900, Smithsonian Handbook of NA Indians Vol 14).'
WHERE id = 218;

-- 326 Cumans/Kipchak (Кыпчак / Куман) — Eurasian steppe 900-1241
-- Pontic-Caspian steppe + Kazakh steppe, from Hungarian plain to Lake Balkhash
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[23.0,49.0],[35.0,52.0],[55.0,53.0],[75.0,50.0],[78.0,46.0],[68.0,43.0],[48.0,43.0],[37.0,44.0],[28.0,45.0],[23.0,47.0],[23.0,49.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'ETHICS-001: The Cuman-Kipchak peoples had no single self-designation; ''Cuman'' is the Byzantine/European form, ''Kipchak'' the Central Asian/Islamic form, and ''Polovtsy'' the Slavic form. They were a confederation of Turkic nomadic tribes, not a unified state — the boundary represents an approximate steppe range, not a state border. The Cuman language was the lingua franca of the western Eurasian steppe before the Mongol conquest (1237-1241). [v6.99.28-manual-boundary] Replaced auto-generated 1000km circle with historically-informed polygon spanning Pontic-Caspian steppe (Ukraine, S Russia) eastward to Lake Balkhash (Kazakhstan) — based on Vásáry (2005), Golden (1992), Sinor (1990).'
WHERE id = 326;

-- 545 Seminole — Florida peninsula + S Georgia 1715-1858
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-87.0,31.0],[-80.5,31.0],[-80.0,28.5],[-80.0,26.0],[-81.2,24.6],[-83.0,25.4],[-84.5,29.5],[-87.0,30.4],[-87.0,31.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'ETHICS-001: ''Seminole'' likely derives from the Spanish ''cimarron'' (wild/runaway) or the Muskogee ''simanoli'' (separatist). The Seminole were not a single pre-existing tribe but an ethnogenesis (1715-1818) of Creek refugees, Yamasee, Apalachee remnants, and escaped African slaves (Black Seminoles) who took refuge in Spanish Florida from English/American expansion. ETHICS-002: After the Three Seminole Wars (1817-1858), ~3,000 Seminoles were forcibly removed to Indian Territory; the survivors (~200) retreated to the Everglades and were never formally defeated. [v6.99.28-manual-boundary] Boundary covers the Florida peninsula + southern Georgia border region, the historical Seminole homeland — based on Mahon (1985), Wickman (1999).'
WHERE id = 545;

-- 580 Saxony Electorate (Kurfürstentum Sachsen) 1356-1806
-- Wettin Albertine lands: Dresden, Leipzig, Wittenberg, Meissen
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[11.0,51.6],[11.4,51.9],[12.3,52.0],[13.5,51.8],[14.7,51.6],[15.0,50.8],[14.2,50.5],[13.0,50.4],[11.8,50.6],[11.0,51.0],[11.0,51.6]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'ETHICS-001: name_original in German. Note that the Electorate of Saxony (1356-1806) is geographically distinct from the medieval Duchy of Saxony (also in this database) — the name ''Saxony'' migrated eastward through dynastic transfers, eventually denoting Wettin lands around Dresden/Leipzig/Wittenberg rather than the original Saxon homeland in NW Germany. [v6.99.28-manual-boundary] Polygon approximates the Wettin Albertine lands at the time of the Electoral title (1356) and Reformation centerpiece (Wittenberg) — based on Wilson (2016), Groß (2007), Kroll (2007).'
WHERE id = 580;

-- 581 Pfalz (Kurfürstentum Pfalz / Electoral Palatinate) 1356-1803
-- Lower Palatinate around Heidelberg + small Upper Palatinate around Amberg
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[7.5,50.0],[9.0,50.1],[9.1,49.2],[8.7,48.9],[7.9,48.9],[7.5,49.4],[7.5,50.0]]],[[[11.4,49.9],[12.6,49.9],[12.6,49.3],[11.4,49.3],[11.4,49.9]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'ETHICS-001: name_original in German; ''Pfalz'' derives from Latin ''Palatium'' (palace). ETHICS-002: The Electorate Palatinate played a catalytic role in the Thirty Years'' War when Elector Frederick V accepted the Bohemian crown (1619), triggering the imperial response and the devastation of his lands (1620 Battle of White Mountain; 1689 Nine Years'' War destruction of Heidelberg). [v6.99.28-manual-boundary] Polygon shows the two non-contiguous parts: Lower Palatinate (Heidelberg, Mannheim) and Upper Palatinate (Amberg). Boundary represents 17th-c. extent — based on Kohnle (2005), Press (1970).'
WHERE id = 581;

-- 587 Württemberg (Herzogtum Württemberg) 1495-1806
-- Modern Baden-Württemberg region (Stuttgart, Tübingen, Esslingen)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[8.5,49.6],[9.6,49.7],[9.9,49.2],[10.0,48.6],[9.7,48.1],[9.0,47.8],[8.4,48.0],[8.3,48.6],[8.4,49.3],[8.5,49.6]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'ETHICS-001: name_original in German. The duchy evolved from the earlier County of Württemberg (1143-1495). ETHICS-002: Württemberg''s estates (Landstände) maintained significant constitutional power against the dukes, producing the ''Tübinger Vertrag'' (1514) — one of the earliest formal constitutional documents in Germany. [v6.99.28-manual-boundary] Polygon approximates 16th-c. ducal extent in the Swabian region of modern Baden-Württemberg — based on Wilson (2016), Marcus (2000), Fulbrook (1983).'
WHERE id = 587;

-- 651 Normandie (Duché de Normandie) 911-1204
-- NW France: Rouen, Caen, Cherbourg, Cotentin peninsula
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-1.95,49.74],[1.50,50.06],[1.75,49.20],[1.55,48.70],[0.30,48.40],[-1.20,48.55],[-1.85,48.65],[-1.95,49.30],[-1.95,49.74]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'ETHICS: The Duchy of Normandy was established when the Viking leader Rollo (Hrólfr) was granted territory by the Frankish king Charles the Simple through the Treaty of Saint-Clair-sur-Epte (911). The duchy was annexed by the French crown after the Battle of Bouvines (1214), de facto ending the Plantagenet rule over Normandy following Philip II Augustus''s conquest in 1204. [v6.99.28-manual-boundary] Polygon approximates 12th-c. ducal extent including Cotentin peninsula, Bessin, Pays de Caux — based on Bates (1982), Crouch (2002), Power (2004).'
WHERE id = 651;

-- 655 Slesvig (Hertugdømmet Slesvig / Duchy of Schleswig) 1058-1864
-- S Jutland border region between Denmark and Holstein
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[8.10,55.42],[10.40,55.30],[10.80,54.85],[10.10,54.40],[8.30,54.65],[8.10,55.42]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'ETHICS: The Duchy of Schleswig is one of the most consequential disputed territories in Northern European history, with Danish and German national movements both claiming it as integral to their national territory. The Second Schleswig War (1864) ended Danish sovereignty; the 1920 plebiscite divided it between Denmark (northern) and Germany (southern Schleswig-Holstein). [v6.99.28-manual-boundary] Polygon represents pre-1864 ducal extent from the Eider River north to roughly the modern Danish-German border — based on Bregnsbo (2014), Lange (2003).'
WHERE id = 655;

-- 773 Coosa paramount chiefdom 1400-1600
-- NW Georgia + SE Tennessee + NE Alabama Mississippian polity
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-86.0,35.5],[-83.5,35.5],[-83.5,34.3],[-84.0,33.6],[-85.5,33.6],[-86.2,34.6],[-86.0,35.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'Coosa was a Mississippian paramount chiefdom encountered by Hernando de Soto''s expedition in 1540 and Tristán de Luna in 1560. The Spanish entradas brought epidemic disease that, together with violent tribute extraction, collapsed Coosa''s political authority within a generation. Its successor populations are ancestral to the historical Creek (Mvskoke) Confederacy and Cherokee. [v6.99.28-manual-boundary] Polygon approximates the paramount chiefdom''s 16th-c. core territory in NW Georgia, SE Tennessee, and NE Alabama — based on Hudson (1997), Smith (2000), Ethridge (2010).'
WHERE id = 773;

-- 779 Lenapehoking — Delaware homeland 1000-1763
-- Delaware River watershed: parts of NY, NJ, PA, DE, eastern MD
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-76.0,41.6],[-74.5,42.0],[-73.5,41.3],[-73.9,40.5],[-74.0,39.5],[-75.0,38.6],[-76.0,38.6],[-76.3,39.5],[-76.2,40.5],[-76.0,41.6]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL,
    boundary_aourednik_year = NULL,
    boundary_aourednik_precision = NULL,
    boundary_ne_iso_a3 = NULL,
    confidence_score = 0.85,
    ethical_notes = 'Lenapehoking (''the Land of the Lenape'') was the homeland of the Lenape (Delaware) people — comprising the Munsee in the north (lower Hudson, upper Delaware) and the Unami in the south (Delaware River valley, southern NJ, DE). The 1737 Walking Purchase (a treaty extracted through fraud by the Penn family) and successive forced removals pushed the Lenape westward through Ohio, Indiana, and finally Oklahoma/Ontario. [v6.99.28-manual-boundary] Polygon approximates the Delaware River watershed homeland prior to colonial dispossession — based on Weslager (1972), Schutt (2007), Goddard in Smithsonian Handbook NA Indians Vol 15.'
WHERE id = 779;

-- Recompute PostGIS geometry from updated GeoJSON
-- (The boundary_geom column has a trigger that auto-recomputes from boundary_geojson)
UPDATE geo_entities SET
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (218, 326, 545, 580, 581, 587, 651, 655, 773, 779)
  AND boundary_geojson IS NOT NULL;

COMMIT;

SELECT
    g.id,
    g.name_original,
    g.boundary_source,
    g.confidence_score,
    ST_NumGeometries(g.boundary_geom) AS n_polys,
    ROUND((ST_Area(g.boundary_geom::geography) / 1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g
WHERE g.id IN (218, 326, 545, 580, 581, 587, 651, 655, 773, 779)
ORDER BY g.id;
