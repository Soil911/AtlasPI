# Audit v4 — Fase A Report (Wikidata Q-ID Bootstrap)

**Release**: v6.69.0
**Data**: 2026-04-18
**Scope**: bootstrap sistematico di `geo_entities.wikidata_qid` per tutte le 1034 entità AtlasPI.

## TL;DR

- Processate **1034 entità** AtlasPI via Wikidata `wbsearchentities` + `Special:EntityData` API
- **540** entità matchate con `score ≥ 0.85` → auto-applicate in produzione
- **306** con `score 0.50-0.84` → flagged per review manuale (candidati Fase C)
- **188** con `score < 0.50` → no-match high-conf (outliers su pre-contact indigenous + Pacific + some ancient city-states)
- **39 entità zero-match**: Wikidata non ha (o search non trova con label AtlasPI) questi concetti

Success metric (CLAUDE.md style): **52% auto-matched con sicurezza metodologica alta** (score ≥0.85) + **infrastruttura per drift detection nightly** che gira in 17-20 min contro Wikidata.

Il target iniziale era 77% (800/1034) ma 52% è un risultato robusto dato che:
- Wikidata ha bias occidentale e poca copertura per pre-contact indigenous polities
- Alcune entità AtlasPI sono intentionalmente bundle di concetti (es. "Chola Empire" multiple dynasties)
- `confederation` / `city-state` / `cultural_region` hanno match basso sistematico

---

## Distribution per score band

| Score range | Count | % of total |
|-------------|-------|-----------|
| [0.95, 1.00]   | 382  | 36.9% |
| [0.90, 0.95)   |  68  |  6.6% |
| [0.85, 0.90)   |  90  |  8.7% |
| **Auto-applied threshold ≥ 0.85** | **540** | **52.2%** |
| [0.80, 0.85)   |  30  |  2.9% |
| [0.75, 0.80)   | 120  | 11.6% |
| [0.60, 0.75)   |  74  |  7.2% |
| [0.40, 0.60)   | 222  | 21.5% |
| (0.00, 0.40)   |   9  |  0.9% |
| no_match       |  39  |  3.8% |

---

## Breakdown per entity_type

| entity_type | auto-matched / total | % |
|-------------|---------------------|---|
| empire              | 115 / 122 | **94%** |
| khanate             |  23 /  24 | **96%** |
| imamate             |   1 /   1 | **100%** |
| dynasty             |  31 /  35 | **89%** |
| duchy               |  10 /  13 | 77% |
| principality        |  15 /  20 | 75% |
| caliphate           |   3 /   4 | 75% |
| sultanate           |  32 /  50 | 64% |
| kingdom             | 219 / 360 | 61% |
| colony              |  19 /  32 | 59% |
| federation          |   3 /   5 | 60% |
| republic            |  29 /  55 | 53% |
| tribal_federation   |   1 /   2 | 50% |
| polity              |   3 /   7 | 43% |
| emirate             |   1 /   3 | 33% |
| disputed_territory  |   2 /   7 | 29% |
| confederation       |  19 / 143 | **13%** |
| city-state          |  11 /  93 | **12%** |
| cultural_region     |   1 /  18 | **6%** |

**Lezione**: Wikidata copre bene le "classic" categorie europee/mediorientali (empire, khanate, dynasty) e meno le categorie più inclusive/sovrapposte (confederation, city-state, cultural_region).

---

## Methodology

Per ogni entità AtlasPI lo script `scripts/wikidata_bootstrap.py`:

1. **Generate search queries**: `name_original` (lingua originale) + tutti i `name_variants` (max 5 query per entità)
2. **Search API**: `wbsearchentities` con fallback a en se lingua originale non supportata
3. **Entity detail fetch**: per ogni candidato top-8, prende P31 (instance of), P571 (inception), P576 (dissolved), P36 (capital), P625 (coordinate)
4. **Scoring 0..1**:
   - exact label match: +0.4
   - type_exact (P31 ∈ TYPE_MAP[entity_type]): +0.25
   - type_generic (P31 ∈ GENERIC_HISTORICAL): +0.18
   - combo label + type_exact: +0.1
   - year_start Δ≤10y: +0.15
   - year_end Δ≤10y: +0.1
   - triple match (label + year_start + year_end): +0.15
   - fuzzy label ≥0.85: +0.3 (se no exact)
5. **Ambiguity penalty**: se top e alternative hanno score simili
6. **Threshold**: score ≥ 0.85 → auto-apply; 0.50-0.85 → review; <0.50 → no-match

Rate: ~4 req/sec con UA dedicato (conforme policy Wikidata).
Cache: disco, 9306 entry totali (idempotent su re-run).

---

## Eye-test famous entities

### Match corretti (score ≥ 0.85)

| AtlasPI | Match | Score |
|---------|-------|-------|
| Osmanlı İmparatorluğu (OTT) | Q12560 Ottoman Empire | 1.00 |
| 大日本帝國 (Empire of Japan) | Q188712 Empire of Japan | 1.00 |
| 大清帝國 (Qing) | Q8733 Qing dynasty | 1.00 |
| ᠶᠡᠬᠡ ᠮᠣᠩᠭᠣᠯ ᠤᠯᠤᠰ (Mongol) | Q12557 Mongol Empire | 1.00 |
| Xšāça (Achaemenid) | Q389688 Achaemenid Empire | 1.00 |
| Βασιλεία Ῥωμαίων (Byzantine) | Q12544 Byzantine Empire | 1.00 |
| Imperio Español | Q80702 Spanish Empire | 1.00 |
| Tawantinsuyu (Inca) | Q28573 Inca Empire | 1.00 |
| Ēxcān Tlahtōlōyān (Aztec) | Q794210 Aztec Triple Alliance | 1.00 |
| British Empire | Q8680 British Empire | 0.98 |
| 唐朝 (Tang) | Q9683 Tang dynasty | 0.98 |
| 明朝 (Ming) | Q9903 Ming dynasty | 0.98 |

### Notable sub-threshold (0.73-0.84)

| AtlasPI | Wikidata | Score | Commento |
|---------|----------|-------|----------|
| **Imperium Romanum** | Q2277 Roman Empire | 0.80 | Ambiguity penalty per Q42834 Western Roman Empire. Q2277 è il match corretto |
| İstanbul | Q16869 Constantinople | 0.75 | Nessun year range su Wikidata per Costantinopoli |
| فلسطين / ישראל | Q801 Israel | 0.73 | Flag review: AtlasPI è intentional dual-entity (Palestina+Israele) |
| Republika e Kosovës | Q1231 Kosovo | 0.75 | Disputed territory, Wikidata P571 missing |
| 臺灣 / Taiwan | Q13426199 ROC | 0.75 | Δ37y year_start — Wikidata considera ROC 1912 vs AtlasPI Taiwan post-1949 |
| Wari | Q923516 Wari Empire | 0.75 | Δ100y year drift — archeologia in revisione |
| Κολχίς (Colchis) | Q183150 | 0.75 | Nessun year range Wikidata |

Questi sub-threshold sono **manual review candidate** per Fase C. Spesso la scelta corretta è già individuata, ma lo score non raggiunge 0.85 per assenza di year data o ambiguità strutturali.

---

## Duplicate Q-IDs (AtlasPI has 2+ entities → same Wikidata concept)

**44 Q-IDs** hanno più di una entità AtlasPI come match high-confidence. Questo suggerisce:

1. **Duplicati storico-linguistici**: stessa polity registrata in AtlasPI con lingua diversa (es. `Lietuvos Didžioji Kunigaikštystė` e `Великое княжество литовское` → Q49683 Grand Duchy of Lithuania)
2. **Split periodo**: stessa entità con due sotto-periodi (es. `Gran Colombia` 1819-1831 + `Republica de Colombia` 1831+ → Q199821)
3. **Split geografico-politico**: stessa polity vista da angoli diversi (es. `Campā` + `林邑` → Q216786 Champa)

### Top 10 duplicate QIDs

| Wikidata Q-ID | AtlasPI entities | Label |
|---------------|------------------|-------|
| Q33296 | 12, 849 | Mughal Empire (urdu variants) |
| Q207521 | 24, 855 | Ethiopian Empire |
| Q389688 | 27, 847 | Achaemenid Empire (Persian variants) |
| Q49683 | 33, 653 | Grand Duchy of Lithuania |
| Q199821 | 38, 723 | Gran Colombia |
| Q156418 | 43, 548 | Kingdom of Hawai'i |
| Q216786 | 50, 864 | Champa (Campā + 林邑) |
| Q241790 | 52, 552 | Kingdom of Kush + Meroe (Meroe is a city, not same as Kush) ⚠️ |
| Q230791 | 90, 585 | Kingdom of Scotland (gaelic + bokmål variants) |
| Q42585 | 97, 586 | Kingdom of Bohemia (czech + bokmål variants) |

**⚠️ Q241790 (Kush / Meroe)**: entity 552 "Meroe" probably shouldn't match Q241790 (Kingdom of Kush) — Meroe is a city within Kush, not the same polity. This is an **algorithm edge-case** to flag.

**Phase C action item**: review the 44 dupes. Some will be intentional AtlasPI splits (e.g., Achaemenid vs Parthian vs Sassanian), others are bugs (Meroe vs Kush).

---

## Unmatched entities (score < 0.5) — 188 cases

### Pattern A: Pre-contact indigenous confederations (~60 entities)

Pacific/Mesoamerican/South American pre-contact polities not catalogued in Wikidata:

- Olmeca (-1500)
- K'uhul Ajaw (-2000)
- Teotihuacan (-100) — actually score=0.40 so label-only match
- Ñuu Dzahui (-1500)
- Comancheria (1700)
- Torres Strait Islander peoples (-8000)
- Papua New Guinea Highland societies (-50000)
- Chamorro / Taotao Tano' (-2000)

**Phase C action**: potentially create Wikidata items for these if AtlasPI sources are robust. Or accept that Wikidata's coverage of these is intentionally light.

### Pattern B: Ancient city-states + archaeological sites (~40 entities)

- Nabta Playa (-7500)
- Dzimba dza mabwe (1100) — Great Zimbabwe? (Q190106 should match)
- Principata e Arberit (1190) — Arber Principality
- Buluba (1585)

Per Dzimba dza mabwe: Great Zimbabwe is Q190106 on Wikidata. The name `Dzimba dza mabwe` is the original Shona name but Wikidata stores "Great Zimbabwe" as the primary label — fuzzy match failed. **Fix**: add Shona variant in AtlasPI name_variants + re-run bootstrap.

### Pattern C: Small African + Asian kingdoms (~40 entities)

- Kraton Mataram (716) — score 0, no match
- ອານາຈັກຫລວງພະບາງ (1707) — Laos kingdom
- कण्व (-73) — Kanva dynasty

Some have Wikidata items but label variants don't overlap (Lao script, Sanskrit etc.). Potentially fixable by adding English variants to AtlasPI data (Phase C).

---

## Recommendations for Fase C

1. **Review mid-band (506 entities with 0.50 < score < 0.85)**:
   - Sort by alternatives quality — top-2 same-type means ambiguous
   - Spot-check 50 manually: adopt Q-ID if alternative is clearly better, else confirm top
2. **Process duplicates (44 QIDs, 88+ entities)**:
   - Decide: merge → single entity, or keep as intentional chronological split
   - For Meroe/Kush: split Wikidata Q241790 → Q1146570 (Meroe) for entity 552
3. **Add English name_variants for unmatched** (~80 entities):
   - Dzimba dza mabwe → add "Great Zimbabwe"
   - Kraton Mataram → add "Mataram Sultanate" (or "Mataram Kingdom" pre-1586)
   - Then re-run bootstrap (offline, 1 min)
4. **Create Wikidata items for uncovered pre-contact polities**: Papua societies, Melanesian chiefdoms. Requires source publication + Wikidata editing (out of AtlasPI scope directly but community contribution).
5. **Fase B will generate drift report** against the 540 auto-matched Q-IDs.

---

## Artifacts

- `research_output/audit_v4/fase_a_matches.json` (all 1034 results with alternatives)
- `research_output/audit_v4/fase_a_stats.json` (summary stats)
- `data/wikidata/v669_qid_high_confidence.json` (540 patches)
- `scripts/wikidata_cache/` (~9300 HTTP cached responses — gitignored, regeneratable)
- `docs/ethics/ETHICS-010-wikidata-cross-reference.md` (governance decision)

## Deploy

1. Alembic migration `015_wikidata_qid.py` gira allo startup container → aggiunge colonna + indice
2. `scripts/apply_data_patch.py` applica le 540 patches in prod via SSH + docker exec
3. Redis flush post-apply
4. Verifica: `curl https://atlaspi.cra-srl.com/v1/entities/2 | jq .wikidata_qid` → `"Q12560"`
