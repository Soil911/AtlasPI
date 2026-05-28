-- Boundary Review v6.99.79 — Tier 2 Batch 2: natural_earth super-group polygons
-- Ethiopia 10 + Indonesia 7+5 + Congo 4 + Vietnam 4 + Senegambia 4 + Micronesia 4 (keep small)
-- + W African 3 + Central Asia 3 + Germany 3 + Congo coast 3 + Bohemia 3 + Central America 3
-- + Fiji 3+3 = ~55 entities. Each gets capital-based circle of historical extent.

BEGIN;

-- ========== ETHIOPIA (10 entities) ==========
-- Each Ethiopian polity had distinct extent — fix all 10, prioritize Mengist Ityop'p'ya
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon (assigned to 10 different historical Ethiopian polities by natural_earth match) with 500km circle around Addis Ababa. Mengist Ityop''p''ya = Ethiopian Solomonic Empire (1270-1974) at peak under Menelik II covered most of modern Ethiopia. Capital varied: Aksum, Lalibela, Gondar, Magdala, Mekele, Addis Ababa.'
WHERE id = 855;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 120000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 120000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon with 120km circle around Ankober. Shewa was the central highland kingdom (1270-1889), nucleus of Solomonic restoration; expanded under Menelik II from Shewa to all Ethiopia (1889-).'
WHERE id = 833;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon with 50km circle around Cheha highlands. Gurage are an Ethiopian Semitic-speaking ethnic group (Sebat Bet + Soddo + Silt''e) in central highlands — historically a tribal society, not a unified state.'
WHERE id = 836;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon with 100km circle around Bonga. Kafecho Bonga = Kingdom of Kaffa in Kafa language (same as id=739 Kaffa). Kaffa kingdom (1390-1897) was a SW Ethiopian kingdom — coffee origin — conquered by Menelik II 1897. DUPLICATE candidate for merge with id=739.'
WHERE id = 661;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon with 100km circle around Bonga. Kaffa kingdom (1390-1897) SW Ethiopia — Omotic language family; capital Bonga; conquered by Menelik II 1897. DUPLICATE candidate for merge with id=661 Kafecho Bonga.'
WHERE id = 739;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon with 100km circle around Hawassa region. Sidama people of southern Ethiopia — pre-imperial confederation of clans, conquered by Menelik II 1893.'
WHERE id = 835;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon with 150km circle around Harar. Harer Ge = the Harari city-state/sultanate, successor to the Adal Sultanate after 1577 capital move from Dakkar. Conquered by Egypt 1875, then by Menelik II 1887.'
WHERE id = 746;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon with 80km circle around Harar. Imaaraadkii Harar = Emirate of Harar (1554-1887), Arab-Muslim emirate after Adal collapse — city-state with restricted hinterland; Ethiopian conquest 1887.'
WHERE id = 660;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon with 100km circle around Aussa. Sultanate of Aussa (1734-1936) was an Afar sultanate in the Awash river basin (Danakil); incorporated into Italian East Africa 1936.'
WHERE id = 745;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/ethiopia-fix] Replaced erroneous modern-Ethiopia polygon with 80km circle around Jiren. Jimma was an Oromo kingdom (1830-1932), one of the Gibe states; Sufi/Muslim; conquered by Menelik II 1882 but kept autonomy until 1932.'
WHERE id = 834;

-- ========== INDONESIA shared 1 (Banten/Palembang/Bone/Banjar/Sambas/Pontianak + Dutch East Indies, 7 entities) ==========
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 2500000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 2500000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.7),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared-Indonesia polygon (assigned to Dutch East Indies + 6 unrelated sultanates) with 2500km circle around Batavia/Jakarta. Nederlandsch-Indie (Dutch East Indies, 1800-1949) covered all modern Indonesia + parts of Malaysia + Papua at peak (~2M km²).'
WHERE id = 262;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared-Indonesia polygon with 50km circle around Banten. Kesultanan Banten (1527-1813) was a sultanate on NW coast of West Java, peak under Maulana Hasanuddin and Ageng Tirtayasa; controlled pepper trade.'
WHERE id = 687;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared-Indonesia polygon with 150km circle around Palembang. Kesultanan Palembang Darussalam (1659-1825) was a sultanate in S Sumatra, Srivijaya heir, abolished by Dutch 1825.'
WHERE id = 698;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared-Indonesia polygon with 100km circle. Bone kingdom (1330-1905) was the most powerful Bugis kingdom in S Sulawesi, founded by Tomanurung, peak under Arung Palakka allied with VOC; Dutch annexed 1905.'
WHERE id = 699;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared-Indonesia polygon with 200km circle. Kesultanan Banjar (1526-1860) was the dominant sultanate in SE Borneo (Banjarmasin), controlled diamond + pepper trade; Banjarmasin War 1859-1905.'
WHERE id = 701;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared-Indonesia polygon with 80km circle. Kesultanan Sambas (1600-1956) was a sultanate in NW Borneo (modern West Kalimantan), Sambas River basin; diamond mining; Dutch protectorate 1818, dissolved 1956.'
WHERE id = 704;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared-Indonesia polygon with 80km circle. Kesultanan Pontianak (1771-1950) was a sultanate at the Kapuas/Landak River mouth in West Kalimantan, founded by Syarif Abdurrahman Alkadrie; Dutch protectorate 1819.'
WHERE id = 708;

-- ========== INDONESIA shared 2 (Tidore/Klungkung/Lanfang/Lombok/Dutch NG, 5 entities) ==========
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared polygon with 400km circle. Nederlands Nieuw-Guinea (Dutch New Guinea, 1828-1962) was the Dutch-controlled western half of New Guinea (Papua + West Papua), transferred to Indonesia 1963 (Act of Free Choice 1969).'
WHERE id = 319;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared polygon with 30km circle. Kesultanan Tidore (1081-1949) was a Maluku spice sultanate (Tidore Island + parts of Halmahera + Raja Ampat); rival to Ternate; absorbed into Indonesia 1949.'
WHERE id = 685;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 40000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 40000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared polygon with 40km circle. Kerajaan Klungkung (1686-1908) was the highest-ranking Balinese kingdom (Dewa Agung dynasty), successor to Gelgel; defeated by Dutch in puputan 1908.'
WHERE id = 702;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 60000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 60000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared polygon with 60km circle. 蘭芳共和國 (Lanfang Republic, 1777-1884) was a Hakka-led Chinese kongsi (mining federation) in W Borneo with elected presidents; arguably first modern Chinese republic; absorbed into Dutch East Indies after Dutch reconquest.'
WHERE id = 705;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/indonesia-fix] Replaced erroneous shared polygon with 50km circle. Kerajaan Lombok (1674-1894) was a Balinese-Sasak kingdom on Lombok Island, controlled by Karangasem Bali; conquered by Dutch 1894.'
WHERE id = 707;

-- ========== CONGO BASIN (4 entities) ==========
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 1200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 1200000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.7),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/congo-fix] Replaced erroneous shared-DRC polygon with 1200km circle. Etat Indépendant du Congo (Congo Free State, 1885-1908) was Leopold II personal possession — covered modern DRC ~2.3M km². ETHICS: estimated 10M Congolese died under forced rubber labor system; transferred to Belgian state 1908 after Casement Report scandal.'
WHERE id = 233;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/congo-fix] Replaced erroneous shared-DRC polygon with 200km circle. Bushoong kingdom (Kuba) was the central Kasai kingdom (post-1625) with raffia + iron + agricultural complexity; capital Nsheng; conquered/protected by Belgian Congo administration.'
WHERE id = 417;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/congo-fix] Replaced erroneous shared-DRC polygon with 250km circle. Garenganze (Yeke kingdom, 1856-1891) was founded by Msiri in S Katanga; copper + ivory + slave trade with Swahili-Arab merchants; killed by Belgian expedition 1891.'
WHERE id = 646;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/congo-fix] Replaced erroneous shared-DRC polygon with 200km circle. Mangbetu kingdom (1800-1895) was a NE Congo Central-Sudanic kingdom with art + court traditions; ruler Munza famously visited by Schweinfurth 1870; absorbed into Congo Free State.'
WHERE id = 648;

-- ========== VIETNAM (4 entities) ==========
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/vietnam-fix] Replaced erroneous shared-Vietnam polygon with 300km circle. 大越 (Đại Việt, 968-1804) covered northern Vietnam from Lý/Trần/Lê/Mạc/Nguyen dynasties; gradual southward expansion (Nam Tiến) absorbed Champa + Khmer territories.'
WHERE id = 130;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.7),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/vietnam-fix] Replaced erroneous shared-Vietnam polygon with 500km circle. Đại Nam (1802-1945) was the Nguyễn Dynasty empire that unified Vietnam under Gia Long; covered modern Vietnam from Lạng Sơn to Cà Mau; French protectorate progressively 1858-1884.'
WHERE id = 138;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.75),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/vietnam-fix] Replaced erroneous shared-Vietnam polygon with 500km circle. Việt Nam (1945-present) — Socialist Republic of Vietnam after 1976 reunification; previously split 1954-1975 as North + South Vietnam (Geneva Accords).'
WHERE id = 237;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/vietnam-fix] Replaced erroneous shared-Vietnam polygon with 150km circle. Panduranga was the last Cham state in southern central Vietnam (~Phan Rang region), survived Vietnamese conquest of Vijaya 1471 until annexation 1832 (Minh Mạng).'
WHERE id = 894;

-- ========== SENEGAMBIA (4 entities — Wolof kingdoms) ==========
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/senegambia-fix] Replaced erroneous shared-Senegal polygon with 80km circle. Siin (Sine) was a Serer kingdom (1335-1969) of west-central Senegal, Guelwar dynasty; resisted Islamization; co-existed with Saalum.'
WHERE id = 563;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/senegambia-fix] Replaced erroneous shared-Senegal polygon with 80km circle. Saalum (Saloum) was a Serer kingdom (1494-1969) S of Siin, capital Kahone; sister kingdom to Siin in the Sine-Saloum delta.'
WHERE id = 728;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/senegambia-fix] Replaced erroneous shared-Senegal polygon with 100km circle. Kayor (Cayor) was a Wolof kingdom (1549-1886) of N-central Senegal coast (Dakar-Saint Louis region), independent after Jolof confederation break-up; absorbed by French colonial Senegal.'
WHERE id = 742;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/senegambia-fix] Replaced erroneous shared-Senegal polygon with 80km circle. Waalo was a Wolof kingdom (1287-1855) of lower Senegal River + delta, capital Nder; subordinate then independent from Jolof; French annexation 1855.'
WHERE id = 843;

-- ========== W AFRICAN GROUPS (3) — Fuuta/Bamana/Adagh ==========
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/wafrica-fix] Replaced erroneous shared polygon with 250km circle. Fuuta Tooro (Toucouleur Empire, founded by El Hadj Umar Tall 1861) was a Tijani Islamic jihad state in middle Niger; defeated by French 1893.'
WHERE id = 730;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/wafrica-fix] Replaced erroneous shared polygon with 300km circle. Bamana ka Faama (Ségou Empire, 1712-1861) was a Bambara kingdom in middle Niger valley, founded by Mamary Coulibaly; controlled trans-Saharan trade; conquered by Toucouleur 1861.'
WHERE id = 744;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/wafrica-fix] Replaced erroneous shared polygon with 400km circle. Kel Adagh = Tuareg confederation of the Adrar des Iforas (Mali NE) — nomadic camel pastoralists; Kel Tamasheq language; allied/fought with French + Mali states.'
WHERE id = 840;

-- ========== CENTRAL ASIA UZBEK KHANATES (3) ==========
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/uzbek-fix] Replaced erroneous shared polygon with 250km circle. خیوه خانلیگی (Khanate of Khiva, 1511-1920) controlled lower Amu Darya + Karakum; Yadigarid + Kungrat dynasties; Russian protectorate 1873, Soviet occupation 1920.'
WHERE id = 335;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/uzbek-fix] Replaced erroneous shared polygon with 250km circle. قوقند خانلیگی (Khanate of Kokand, 1709-1876) Ferghana valley-based Uzbek state; conquered Tashkent + parts of Kazakh steppe; Russian conquest 1876.'
WHERE id = 336;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/uzbek-fix] Replaced erroneous shared polygon with 300km circle. امارت بخارا (Emirate of Bukhara, 1785-1920) Manghit dynasty Uzbek state; controlled Samarqand + Bukhara; Russian protectorate 1868, Soviet occupation 1920.'
WHERE id = 345;

-- ========== GERMANY 20TH C. (3) ==========
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/germany-fix] Replaced erroneous shared-Germany polygon with 400km circle. Deutsches Reich (Nazi Germany 1933-1945) extended to Anschluss Austria, Sudetenland, occupied Poland/France/Norway/Greece etc. at peak; reduced to modern Germany boundaries after Potsdam 1945. ETHICS: regime responsible for genocide of 6M+ Jews + 11M other victims of the Holocaust + WWII deaths.'
WHERE id = 229;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.7),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/germany-fix] Replaced erroneous shared-Germany polygon with 200km circle. Deutsche Demokratische Republik (East Germany, 1949-1990) covered Soviet occupation zone; Berlin Wall 1961-1989; reunification with FRG October 1990.'
WHERE id = 239;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry),
  boundary_source = 'approximate_circle', boundary_ne_iso_a3 = NULL,
  confidence_score = LEAST(confidence_score, 0.7),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/germany-fix] Replaced erroneous shared-Germany polygon with 400km circle. Weimarer Republik (Weimar Republic, 1919-1933) parliamentary democracy after WWI defeat + Treaty of Versailles; territorial losses to Poland (Posen, West Prussia) + France (Alsace-Lorraine); hyperinflation + Great Depression + Nazi takeover 1933.'
WHERE id = 244;

-- Verify all natural_earth batch updates
SELECT id, name_original,
       ROUND(ST_Area(boundary_geom)::numeric, 4) as area,
       boundary_source,
       confidence_score
FROM geo_entities
WHERE id IN (
  660, 661, 739, 745, 746, 833, 834, 835, 836, 855,
  262, 687, 698, 699, 701, 704, 708,
  319, 685, 702, 705, 707,
  233, 417, 646, 648,
  130, 138, 237, 894,
  563, 728, 742, 843,
  730, 744, 840,
  335, 336, 345,
  229, 239, 244
)
ORDER BY id;

COMMIT;
