# Wave 0 / B — Data quality audit

Date: 2026-05-28
Agent: Wave 0 B (general-purpose, background, SSH read-only)
Duration: ~5.5 min
Status: completed

---

## 7+1+1 analyzers panoramica (sono 9, non 7 come da CLAUDE.md)

`scripts/ai_cofounder_analyze.py`:

| # | Analyzer | Funzione | File:line |
|---|---|---|---|
| 1 | `analyze_geographic_gaps` | Regioni < 40% media e <50 entità | :167 |
| 2 | `analyze_temporal_gaps` | Ere con 0 eventi o <30% media | :196 |
| 3 | `analyze_low_confidence` | Entità/eventi con `confidence_score<0.4` | :241 |
| 4 | `analyze_missing_boundaries` | Entità senza `boundary_geojson` | :295 |
| 5 | `analyze_orphan_entities` | Entità non in chain (solo se ≥85%) | :329 |
| 6 | `analyze_failed_searches` | 404 ripetuti + query 200ms verified-empty | :358 |
| 7 | `analyze_date_coverage_gaps` | Mesi con <5 giorni coperti per on-this-day | :507 |
| 8 | `analyze_geometric_bugs` (v6.31) | bbox>180°, area>ceiling, shared polygons | :580 |
| 9 | `analyze_cross_resource_consistency` (v6.32) | event/entity year mismatch, inverted year_end, day-no-month, unsourced events | :747 |

## Risultati per analyzer (snapshot DB prod)

**Totale**: 1038 entità, 643 eventi, 91442 API requests negli ultimi 30g.

1. **geographic_gaps**: nessun gap reale. Media ≈148/regione. "Other" (13) escluso. Distrib: Africa/MidEast 271, Europa 212, Asia E/SE 187, Asia C/S 132, Americhe N 132, Americhe S/C 91. **Pattern sano**.
2. **temporal_gaps**: nessuna era con 0 eventi. Media eventi/era ≈58. Soglia <30% & <10: `Pre-3000BCE` borderline (12 eventi, 18 entità — passa). **Sotto-densità**: 1000-500 BCE (25 ev/50 ent), 500-1 BCE (35 ev/69 ent), 1-500 CE (32 ev/59 ent).
3. **low_confidence**: **5 entità** sotto 0.4. 0 eventi sotto 0.4.
4. **missing_boundaries**: **0** entità senza boundary. Coverage perfetta.
5. **orphan_entities**: 816/1038 orfani = **78.6%** → sotto soglia 85% → analyzer NON triggera. Il 21.4% è in chain. Nascosto ma osservabile.
6. **failed_searches**: solo **3 path 404 ripetuti** (`/v1/.env`, `/v1/mcp`, `/v1/models`) — scan/probe non demand reale.
7. **date_coverage_gaps**: 223 unique-day pairs. **Nessun mese <5 giorni**. Min Feb=9, max Apr=Oct=24.
8. **geometric_bugs**: **2 antimeridian-crossers** (id=754 Sau o Futuna, id=307 Lapita). **7 city-state oversized** (id=277 Harappa 1.5M km², id=418 Miji ya Pwani 638k km², 5 altri). **2 principality/duchy oversized** (id=653 Lituania 1.5M km² `principality`, id=427 Finlandia 762k km² `duchy`). **1 chiefdom oversized** (id=757 Kiriwina 469k km²). **23 hash-duplicati di polygon** (≈46 entità) — quasi tutti alt-language pair legittimi.
9. **consistency_bugs**: **0** issues. **Pulito.**

## Top 20 issues globali

| # | Analyzer | Entity/Issue | Severity | Hint fix |
|---|---|---|---|---|
| 1 | geometric | id=754 Sau o Futuna bbox 360° | HIGH | run `fix_antimeridian_and_wrong_polygons` |
| 2 | geometric | id=307 Lapita bbox 358° | HIGH | idem |
| 3 | geometric | id=277 Harappa `city-state` 1.54M km² | HIGH | rivedere entity_type → `civilization`/`cultural_region` |
| 4 | geometric | id=653 Lituania `principality` 1.53M km² | HIGH | retype → `grand_duchy`/`kingdom` |
| 5 | geometric | id=427 Finlandia `duchy` 762k km² | MED | retype → `grand_duchy` |
| 6 | geometric | id=418 Miji ya Pwani `city-state` 638k km² | MED | retype → `confederation` |
| 7 | geometric | id=757 Kiriwina `chiefdom` 469k km² | MED | check polygon source |
| 8 | geometric | id=160/414 Hausa Bakwai/Birane Hausa `city-state` 200k km² | MED | retype → `confederation` |
| 9 | geometric | id=941 Haudenosaunee `city-state` 138k km² | MED | retype → `confederation` |
| 10 | low_conf | id=1032 سلطنة الداجو (Dajo Sultanate) 0.25 | MED | fonti primarie |
| 11 | low_conf | id=747 بازين 0.30 | MED | idem |
| 12 | low_conf | id=888 Ngoenyang 0.30 | MED | fonti SE-Asian |
| 13 | low_conf | id=881 Ma-i 0.35 | MED | fonti Filippine |
| 14 | low_conf | id=39 KKTC (Cipro Nord) 0.35 + disputed | LOW | OK come disputed |
| 15 | orphan | 816/1038 entità (78.6%) non in chain | MED | sotto 85% soglia |
| 16 | temporal | era 1000-500 BCE: 25 ev / 50 ent | LOW | events Babilonia tarda, Hallstatt |
| 17 | temporal | era 500-1 BCE: 35 ev / 69 ent | LOW | Roma repub., Han |
| 18 | temporal | era 1-500 CE: 32 ev / 59 ent | LOW | crisi III sec., Sasanidi |
| 19 | date_cov | Febbraio: 9 unique-days (min) | LOW | events Feb |
| 20 | geometric | 23 polygon-hash duplicates | LOW | audit 1-volta |

## Pattern emersi

1. **Quality "verde" su metadata, problemi solo geometrici.** Tutti i 5 analyzer metadata classici sono silenziosi o quasi: dataset maturo. L'unico backlog reale è **shape-level** (analyzer #8) — conferma esattamente il warning di CLAUDE.md sui metadata-only check.
2. **Mismatch entity_type/polygon-size sistematico per pre-modern entities.** Harappa/Hausa/Haudenosaunee classificati `city-state` ma sono in realtà civiltà/confederazioni multi-area. Lituania come `principality` quando era *Grand Duchy*. Indica una **tassonomia entity_type troppo Europa-centrica**.
3. **Le 5 low-confidence non sono "errori"** — sono entità correttamente marked `uncertain`/`disputed` (Dajo Sultanate, Bazin, Ngoenyang, Ma-i, KKTC). Confidence basso = trasparenza dell'incertezza funzionante (CLAUDE.md valore #3).
4. **Chain coverage 21.4%** è la cosa che l'analyzer NON segnala (soglia 85% troppo permissiva).
5. **API traffic sano** (91k requests, 99.97% 200/204). I 404 sono security scan, non utenti.
6. **Feb/Nov/Dec sotto la media on-this-day** (9, 16, 16 vs media 19). Non triggera soglia ma sono i mesi naturali da rafforzare.

## 3 raccomandazioni quick per Wave 1

1. **Run `fix_antimeridian_and_wrong_polygons` su id=754 e 307**: due bug visivi noti, auto-fix esistente, zero rischio. Stessa categoria del bug v6.31 USA→Francia. **15 minuti, alta resa.**
2. **Audit entity_type per le 7-10 entità oversized** (Harappa, Lituania, Finlandia, Miji ya Pwani, Hausa Bakwai/Birane Hausa, Haudenosaunee, Kiriwina). Non cambiare poligoni — cambiare solo `entity_type` per coerenza scala. Considerare aggiungere tipi `grand_duchy` e `civilization` se mancanti. **~1 ora, alto valore semantico.**
3. **Abbassare soglia `analyze_orphan_entities` da 85% → 70%** (o introdurre tier intermedio "warning" a 70-85%). Attualmente il 78.6% di orfani è invisibile al pipeline. **Modifica 1 riga + run targeted enrichment.**

Bonus low-cost: aggiungere 5-10 eventi datati a Feb/Nov/Dec per bilanciare on-this-day.

**File chiave**:
- `scripts/ai_cofounder_analyze.py` (tutti analyzer)
- `src/ingestion/fix_antimeridian_and_wrong_polygons.py` (auto-fix #1+2)
