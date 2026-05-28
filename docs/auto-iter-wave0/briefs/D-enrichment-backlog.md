# Wave 0 / D — Enrichment backlog

Date: 2026-05-28
Agent: Wave 0 D (general-purpose, background, SSH read-only)
Duration: ~4.2 min
Status: completed

---

## Sessioni completate

Da `git log`, l'enrichment è arrivato fino a **S50** (commit `df82aef` v6.99.74, "Phase B S50 + Phase F visual tour COMPLETE", 2026-05-23). Numerazione non perfettamente lineare: ultima `S47`→`S50` (gap S48-49 nel naming, ma copertura concettuale completa). Dalle sessioni iniziali S1 (v6.99.0, commit `e1c87be`) a S50, ~49 commit "session". Memoria utente indica S1→S34 done a v6.99.27 — **memoria stale**: in realtà S35-S50 di Phase B (+~800 fonti) sono già state fatte.

Successive a Phase B: **Phase G** (G1-G5, feedback layer/telemetry/badge/citations/reputation) e **Phase H** (boundary review v6.99.79-80, +200 capitali, 59 polygon placeholder→reali, 0 area-sanity violations).

## Statistiche DB (prod, snapshot 2026-05-28)

- **Totale entità**: 1038 (status: 722 confirmed, 239 uncertain, 33 disputed, 44 deprecated)
- **Boundary coverage**: 1038/1038 = **100%** (NESSUNA entità senza boundary_geojson)
- **Capital coverage**: 1038/1038 = 100% (post-Phase H)
- **Wikidata QID coverage**: 715/1038 = 69% (323 entità senza QID → backlog Phase I?)
- **Sources**: 4819 totali, 5.46 media/entità, **0 entità con 0 fonti**

**Per type (top)**:
| type | n | avg conf |
|---|---|---|
| kingdom | 361 | 0.66 |
| confederation | 143 | 0.61 |
| empire | 125 | 0.73 |
| city-state | 93 | 0.67 |
| republic | 55 | 0.78 |
| sultanate | 50 | 0.65 |
| dynasty | 35 | 0.63 |

**Confidence distribution (bucket /10)**: b3:1, b4:4, b5:59, **b6:186**, b7:333, b8:125, b9:297, b10:33 → mediana ~0.7; **~250 entità sotto 0.6** (~24%).

**Period distribution** (anni inizio):
- Preistoria/Antichità (-65000 → -500): 124 entità — coverage sparsa
- Classico (-500 → 500): 170 entità
- Medioevo (500 → 1500): 774 entità (densa)
- Modernità (1500-1900): 261 entità
- **Gap critici**: -8000→-2000 (solo 13 entità: Neolitico/early Bronze) e -65000→-8000 (8 entità: Paleo); 2000+ vuoto.

**Geografica (capitale, lat/lon band)**: bilanciato N_Subtropic/EurAfrica (196), N_Tropics/EurAfrica (135), N_Subtropic/Asia (124). Sotto-rappresentati: Pacific (25), S_Hemi_Far (10), N_Temperate/Asia (9 — Siberia/Mongolia).

**Chains**: 367 chain definite, 222 entità collegate, **816 entità (78.6%) ORFANI da chain_links** — gap enorme.

**Events**: 643 storici, **280 unlinked (43.5%)** — backlog ETHICS-007 ancora grosso. Top tipi unlinked: BATTLE (44), INTELLECTUAL_EVENT (38), FOUNDING_STATE (33), TECHNOLOGICAL_EVENT (24), REVOLUTION (19).

## Top 30 priority per S35+ (entità confirmed con conf<0.7 + srcs<5)

| # | name | type | conf | period | razionale |
|---|---|---|---|---|---|
|1|Sosso (id 981)|kingdom|0.40|1180-1235|Sahel pre-Mali, alta visibilità storica|
|2|سلطنة الداجو (Daju, 1032)|sultanate|0.25|1200-1400|conf più bassa DB|
|3|Ngoenyang (888)|kingdom|0.30|638-1292|SE Asia, antenata Lanna|
|4|Mahā Vijayabāhu Sri Lanka (142)|kingdom|0.40|-543-1815|durata 2358 anni, super-aggregato|
|5|الدولة الأموية Umayyad (173)|empire|0.40|661-750|empire chiave Islam classico, solo 3 srcs!|
|6|मराठा साम्राज्य Maratha (111)|empire|0.40|1674-1818|empire-mondo, solo 3 srcs|
|7|غوریان Ghurid (342)|empire|0.40|879-1215|alimentò Delhi Sultanate|
|8|ᠵᠡᠭᠦᠨᠭᠠᠷ Zunghar (145)|empire|0.40|1634-1755|ultimo nomade dell'Asia Centrale|
|9|ᠬᠠᠵᠠᠷ Qajar (604)|khanate|0.40|1634-1771|nomenclatura/datazione incerta|
|10|ዛግዌ Zagwe (491)|dynasty|0.40|900-1270|Etiopia, costruì Lalibela|
|11|Kerajaan Sunda (688)|kingdom|0.40|669-1579|maritime Indonesia, 910 anni|
|12|Kerajaan Kediri (668)|kingdom|0.40|1042-1222|Java classica|
|13|Tarumanagara (670)|kingdom|0.40|358-669|earliest Hindu Java|
|14|鲜卑 Xianbei (290)|confederation|0.40|93-234|antenata Wei/Tang|
|15|Muisca (860)|confederation|0.40|600-1541|civiltà pre-Colombo Colombia|
|16|Wagadou/Ghana (146)|empire|0.45|300-1200|empire fondante Sahel|
|17|Σογδιανή Sogdia (349)|confederation|0.45|-500-1000|Silk Road, 1500 anni|
|18|מלכות הורדוס Herod (617)|kingdom|0.40|-37-6|key 2nd Temple period|
|19|Mycenae 𐀖𐀏𐀙 (274)|kingdom|0.55|-1600-1100|Bronze Age core greco|
|20|Akkad 𒀀𒅗𒁲𒆠 (169)|empire|0.55|-2334--2154|first world empire!|
|21|Neo-Babylon 𒆳𒆍𒀭𒊏𒆠 (490)|empire|0.55|-626--539|Nabucodonosor|
|22|Saba سبأ (188)|kingdom|0.50|-1200-275|Arabia Felix, queen Sheba|
|23|Mixtec/Bēnizàa Zapotec (195, 196)|kingdom|0.50/0.55|pre-Colombo|Mesoamerica core|
|24|Taiping 太平天國 (452)|kingdom|0.50|1851-1864|20M morti, civil war più grande|
|25|Mamluk Jerusalem (511)|kingdom|0.50|1187-1229|Salahuddin retake|
|26|Tywysogaeth Cymru Wales (92)|kingdom|0.50|1216-1283|Llywelyn period|
|27|Cuzcatan Pipil (550)|kingdom|0.40|900-1528|El Salvador pre-Hispanic|
|28|Diaguita (539)|confederation|0.40|-400-1665|Andes meridionali|
|29|Lenca (551)|confederation|0.40|-1000-1539|Honduras|
|30|Sangam Chola சோழர் (1040)|kingdom|0.50|-300-300|early Tamil polity|

## Gap critici

**Temporali**:
- **Neolitico/early Bronze (-8000 → -2000)**: solo 13 entità. Manca Çatalhöyük, Vinča, Cucuteni, Halaf, Ubaid, early Mehrgarh.
- **Paleolitico**: meaningful per cultural_region/civilization (solo 1!).

**Geografici**:
- **N_Temperate Asia** (Siberia/Mongolia steppe): 9 entità — manca Xiongnu epoch detail, Donghu, Yenisei Kyrgyz, Tuvan polities.
- **Pacific** (25): Polynesia/Melanesia ancora sotto-rappresentata.
- **S Hemi Far** (10): Patagonia/Tierra del Fuego/Maori South Island.

**Strutturali**:
- **816 entità (78%) NON in chain_links** → genealogia/successione dinastica massivamente assente.
- **280 eventi unlinked (43%)** — ETHICS-007 ancora aperto, soprattutto BATTLE (44).
- **323 senza wikidata_qid** (31%) — riducono interop con LOD esterni.

## Raccomandazione S35 (= S51 numerica reale)

**Focus**: **"Eurasia Classical Empires deep-enrichment + chain linkage"** — batch 10 entità targeting i tier-1 deficit:

Batch proposto (10):
1. Umayyad (173) - upgrade srcs 3→10, conf 0.40→0.75
2. Maratha (111) - srcs 3→10, conf 0.40→0.75
3. Ghurid (342)
4. Zagwe (491) + chain Aksum→Zagwe→Solomonic
5. Akkad (169) - canonical fount
6. Neo-Babylon (490)
7. Mycenae (274)
8. Saba (188)
9. Xianbei (290) + chain → Wei
10. Wagadou/Ghana (146) + chain Ghana→Mali→Songhai

**Razionale**:
- **Impatto**: 9/10 sono empire/kingdom super-visibili. Lift confidence medio ~0.45→0.75 (+30pp su entità ad alto traffico API).
- **Sforzo**: ~45 min, fonti ben note (Brill, Cambridge Histories, JSTOR).
- **Completeness gain**: chiude 10 di 36 kingdom <3 srcs (28% di quel cluster). Crea/estende 3 dynasty chains (Aksum-Solomonic, Mesopotamia, West African empires) attaccando 30+ entità orfane secondarie.
- **Bonus ETHICS-007**: collegare 5-10 eventi BATTLE non-linked agli stessi entity → smaltimento parallelo del backlog eventi.

**Alternative scartate**: Pacific/Polynesia (impatto basso, fonti scarse); Neolitico (timeframe S36+, richiede consulenza archeologica). Vanno schedulate ma non per S35.
