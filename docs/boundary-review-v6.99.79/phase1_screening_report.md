# Boundary Review v6.99.79 — Fase 1: Screening automatico

Data: 2026-05-28
Database: produzione (cra-atlaspi-db @ 77.81.229.242)
Entità totali con boundary: ~1037 / 1038

## Sommario esecutivo

Lo screening automatico ha identificato **3 classi distinte di problemi** che colpiscono almeno **160 entità** sulle 1037 con boundary.

| Classe | Severità | Entità impattate |
|---|---|---|
| Antimeridian crossers | CRITICO | 1+ (Lapita confermato) |
| Polygon collisions (entità storiche diverse condividono polygon) | ALTO | ~120 (in 20+ gruppi) |
| Default placeholder polygons (quadrati 1/2/3 deg²) | ALTO | 12+ |
| Outliers di area (> 3× mediana per tipo) | MEDIO | 60+ |
| Centroide-capitale lontano (> 3000 km) | ALTO | 12 (incluse Lapita e Russia moderna che è OK) |

Metodologia: query PostGIS su `boundary_geom`, calcolo bbox, area, distanza centroide↔capitale, conteggio vertici.

---

## 1. Antimeridian crossers

### id=307 Lapita (confederation, -1600)
- bbox: `[-180, -22] → [178.5, -2]` (width 358.5°)
- Capitale: Vanuatu (168.3°E, -17.7°S) — esatta
- Area calcolata: 520.5 deg² (in realtà piccola Oceania ma resa enorme dal bbox)
- Source: `historical_approximation`, confidence 0.45
- **Fix necessario**: split del MultiPolygon su antimeridian o "shift" delle coordinate per usare 0-360°.
- Il fix v6.99.58 (in `fix_antimeridian_and_wrong_polygons.py`) probabilmente non gestisce questo specifico caso. Da verificare.

---

## 2. Polygon collisions (entità storiche diverse condividono lo stesso polygon)

Query: `GROUP BY ROUND(ST_Area, 4) HAVING COUNT(*) >= 2`

### Tier critico (5+ entità con stessa area)

**Area 93.1307 deg² — 10 entità (Etiopia)**
| id | name | type | year | source |
|----|------|------|------|--------|
| 660 | Imaaraadkii Harar | sultanate | 1554 | natural_earth |
| 661 | Kafecho Bonga | kingdom | 1390 | natural_earth |
| 739 | Kaffa | kingdom | 1390 | natural_earth |
| 745 | Sultanat Awsa | sultanate | 1734 | natural_earth |
| 746 | Harer Ge | sultanate | 1520 | natural_earth |
| 833 | Shewa | kingdom | 1270 | natural_earth |
| 834 | Jimma | kingdom | 1830 | natural_earth |
| 835 | Sidaama | confederation | 1500 | natural_earth |
| 836 | Gurage | tribal_nation | 1300 | natural_earth |
| 855 | Mengist Ityop'p'ya | empire | 1270 | natural_earth |

→ Tutti hanno il **polygon dell'Etiopia moderna**. Storicamente errato per tutti.

**Area 148.1358 deg² — 7 entità (Indonesia)**
| id | name | type | year | source |
|----|------|------|------|--------|
| 262 | Nederlandsch-Indie | colony | 1800 | natural_earth |
| 687 | Kesultanan Banten | sultanate | 1527 | natural_earth |
| 698 | Kesultanan Palembang Darussalam | sultanate | 1659 | natural_earth |
| 699 | Bone | kingdom | 1330 | natural_earth |
| 701 | Kesultanan Banjar | sultanate | 1526 | natural_earth |
| 704 | Kesultanan Sambas | sultanate | 1600 | natural_earth |
| 708 | Kesultanan Pontianak | sultanate | 1771 | natural_earth |

→ Polygon Indonesia coloniale assegnato a sultanati locali. Errato.

**Area 170.5407 deg² — 6 entità (Levante medievale, aourednik!)**
| id | name | type | year |
|----|------|------|------|
| 174 | الدولة الفاطمية (Fatimid) | empire | 909 |
| 175 | الدولة الأيوبية (Ayyubid) | empire | 1171 |
| 470 | Regnum Hierosolymitanum (Crusader) | kingdom | 1099 |
| 481 | الإخشيديون (Ikhshidid) | dynasty | 935 |
| 496 | بنو زيري (Zirid) | dynasty | 972 |
| 511 | مملكة بيت المقدس العربية | kingdom | 1187 |

→ Critico: **aourednik è il dataset curato**. Sei stati con territori molto diversi (Egitto, Levante, Maghreb, Tunisia) hanno la stessa geometria. Bug nel seed o nella pipeline aourednik?

**Area 14.4068 deg² — 6 entità (Caraibi)**
- Taino, Xaragua, Borikén, Quisqueya, Cuba cacicazgos, Jamaica cacicazgos
- Source: aourednik. Tutti chiefdom/confederation Taino con stesso polygon.

**Area 153.0786 deg² — 5 entità (Indonesia/Pacifico)**
- Nederlands Nieuw-Guinea, Kesultanan Tidore, Kerajaan Klungkung, 蘭芳共和國 (Lanfang), Kerajaan Lombok
- Bali, Lombok, Borneo, Nuova Guinea, Maluku — 5 isole/regioni diverse.

**Area 14.8870 deg² — 5 entità (Levante antico, aourednik)**
- Tadmor (Palmyra), Phoenicia, Israele, Giuda, Edom

### Tier alto (3-4 entità con stessa area)

**Area 693.6493 deg² — 3 entità**
| id | name | type | year |
|----|------|------|------|
| 994 | Bunyoro pre-Babito | kingdom | 1300 |
| 996 | Bigo bya Mugenyi | earthwork-complex | 1300 |
| 1030 | Mbundu pre-Ndongo | confederation | 1200 |

→ Bunyoro è Uganda, Mbundu è Angola, Bigo bya Mugenyi è un sito archeologico (~5 km²!). 693 deg² assurdo per tutti tre.

**Area 373.5156 — 4 entità** (Cina dinastie del Sud: 隋朝, 隋以前北朝, 北周, 陳朝)

**Area 189.5152 — 4 entità (Africa centrale)**
- Etat indépendant du Congo, Bushoong, Garenganze, Mangbetu

**Altri gruppi 3-4 entità**: 71.99 (Anatolia ellenistica), 27.94 (Vietnam), 16.29 (Senegambia), 9.40 (Balcani), 6.00 (mix globale), 1.50 (default), 0.05 (Micronesia)

---

## 3. Default placeholder polygons (historical_approximation)

Pattern scoperto: rectangoli con dimensioni esatte attorno alla capitale.

| Area | bbox W×H | N entità |
|---|---|---|
| 1.0 deg² | 1.0 × 1.0 | 5 |
| 3.0 deg² | 2.0 × 1.5 | 4 |
| 1.5 deg² | 1.5 × 1.0 | 3 |
| 2.25 deg² | 1.5 × 1.5 | 5 (richiede conferma) |

### Esempi area 1.0 deg² (5 entità in continenti DIVERSI)
- 788 Haak'u (USA New Mexico)
- 790 Hopituh Shi-nu-mu (USA Arizona)
- 938 Paquimé (Mexico Chihuahua)
- 954 Cañari (Ecuador)
- 961 Izapa (Mexico Chiapas)

### Esempi area 2.25 deg² (5 entità)
- 409 Sultanat Ifat (Etiopia)
- 528 Poverty Point (USA Louisiana)
- 531 Wanka/Huanca (Peru)
- 682 Chinook Illahee (USA Washington)
- 881 Ma-i (Filippine)

→ Generatore di placeholder che crea quadrati attorno alla capitale, indipendente dalla cultura/storia reale.

---

## 4. Top 20 outliers per area (escluso antimeridian)

Ratio = area / mediana per quel entity_type. Soglia critica > 5.

| id | name | type | year | area | ratio | source | conf |
|----|------|------|------|------|-------|--------|------|
| 277 | हड़प्पा / Indus | city-state | -3300 | 124.88 | 129.74 | hist_approx | 0.5 |
| 309 | Aboriginal Australian Nations | confederation | -65000 | 1113.25 | 75.70 | hist_approx | 0.6 |
| 266 | Российская Федерация | republic | 1991 | 2884.19 | 54.14 | natural_earth | 0.85 |
| 418 | Miji ya Pwani | city-state | 800 | 51.75 | 53.77 | hist_approx | 0.5 |
| 230 | СССР | empire | 1922 | 5705.00 | 53.41 | hist_approx | 0.5 |
| 1030 | Mbundu pre-Ndongo | confederation | 1200 | 693.65 | 47.17 | aourednik | 0.85 |
| 896 | قۇچۇ Qocho | kingdom | 856 | 764.61 | 43.69 | aourednik | 0.7 |
| 35 | བོད Tibet | disputed_territory | 1950 | 124.75 | 40.99 | hist_map | 0.75 |
| 994 | Bunyoro pre-Babito | kingdom | 1300 | 693.65 | 39.64 | aourednik | 0.55 |
| 326 | Кыпчак Cuman | confederation | 900 | 416.00 | 28.29 | hist_approx | 0.85 |
| 1027 | Yoruba early polities | confederation | 1000 | 403.36 | 27.43 | aourednik | 0.85 |
| 972 | Tiahuanaco-Chiripa-Pukara | cultural_region | -800 | 394.96 | 27.07 | aourednik | 0.65 |
| 970 | Salinar | cultural_region | -400 | 394.96 | 27.07 | aourednik | 0.55 |
| 16 | Российская Империя | empire | 1721 | 2852.71 | 26.71 | hist_map | 0.85 |
| 897 | 甘州回鶻 Ganzhou Uyghur | kingdom | 848 | 435.95 | 24.91 | aourednik | 0.85 |
| 454 | 南詔 Nanzhao | kingdom | 738 | 435.95 | 24.91 | aourednik | 0.6 |
| 9 | ᠶᠡᠬᠡ ᠮᠣᠩᠭᠣᠯ Mongol Empire | empire | 1206 | 2513.11 | 23.53 | hist_map | 0.75 |
| 900 | Ta-hua-lo | polity | 1225 | 52.02 | 23.12 | aourednik | 0.7 |
| 674 | Theloal | kingdom | 700 | 375.86 | 21.48 | aourednik | 0.6 |
| 207 | Brasil Colônia | colony | 1500 | 707.10 | 21.29 | natural_earth | 0.85 |

**Note critiche**:
- **id=277 Harappa classificata "city-state"** → era una civiltà urbana enorme, entity_type errato (ma area corretta)
- **id=897 甘州回鶻 (Cina NW) + id=454 南詔 (Yunnan) stessa area** → polygon collision tra regioni completamente diverse
- **id=266 Russia moderna**: ratio 54× mediana ma il dato è corretto (Russia È enorme)
- **id=230 URSS**: 5705 deg² è plausibile per URSS, ma solo 13 punti = polygon estremamente semplificato
- **id=970/972 cultural_region in Sudamerica**: stesso polygon condiviso per due culture diverse

---

## 5. Piano di azione

### Tier 1 — Fix immediati (questa sessione)
1. ✅ ~~Screening report (questo file)~~
2. Lapita antimeridian (id=307)
3. Bigo bya Mugenyi (id=996) — restringere a area reale
4. Default polygon collisions (12 entità con polygon placeholder identici)

### Tier 2 — Investigazione + fix di gruppo
5. 10 entità etiopi (natural_earth Ethiopia modern shared)
6. 7 entità Indonesia (natural_earth shared)
7. 6 entità Levante medievale (aourednik anomalia!)
8. 6 entità Caraibi (aourednik shared)
9. 5 entità Levante antico (aourednik shared)
10. 4-5 dinastie cinesi del Sud (aourednik shared)

### Tier 3 — Revisione visiva
11. Top 50 outliers via app screenshot
12. Spot-check di un campione random di 30 entità per validazione

### Tier 4 — Ridocumentazione
13. ETHICS record sulla classification: Aboriginal Australian Nations come single confederation
14. ETHICS record sulla classification: Harappa come city-state
15. Aggiornare confidence_score per le entità con polygon collisions: ridurre a < 0.5
