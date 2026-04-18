# AtlasPI — Handoff Sessione Audit v4 Fase C

**Creato**: 2026-04-18 (post v6.70.0)
**Autore**: Sessione Fase A+B Claude Code
**Destinatario**: Sessione Claude Code successiva (Fase C)
**Scope**: structural cleanup + Wikidata drift resolution + entity merges/splits

---

## TL;DR — Stato attuale

Release completate in questa sessione:

| Release | Committed | Deployed |
|---------|-----------|----------|
| [v6.69.0](https://github.com/Soil911/AtlasPI/commit/422eb53) — Fase A: Wikidata Q-ID bootstrap | ✅ commit `422eb53` | ✅ live on VPS |
| v6.70.0 — Fase B: drift detection | ✅ da questa sessione | ✅ da questa sessione |

Dataset finale post-v6.70 (live su https://atlaspi.cra-srl.com):
- **1034 entità** (unchanged da v6.68)
- **540 con `wikidata_qid`** (52.2% cross-referenced)
- **494 `wikidata_qid IS NULL`** (review candidates + Wikidata gaps)

Fase A output:
- 540 auto-applied (score ≥ 0.85)
- 306 mid-band (0.50 ≤ score < 0.85) per review
- 188 low-score (<0.5) — spesso Wikidata gap genuine
- 39 zero-match

Fase B output:
- 300 entità con ≥1 drift (dei 540 con QID)
- 108 HIGH drift (year/coord significativi)
- 270 MED drift (capital name spesso)
- 0 autofixable applicati (tutti i drift coord >1000km sono capitali storiche diverse, non typo)

---

## Cosa è stato fatto (non rifare)

### Fase A (v6.69.0)

1. ✅ Alembic migration `015_wikidata_qid.py` → `geo_entities.wikidata_qid VARCHAR(20) NULL + INDEX`
2. ✅ `GeoEntity.wikidata_qid` nel model + `EntityResponse` schema + `_entity_to_response()` passing
3. ✅ `PATCHABLE_FIELDS["entity"]` include `wikidata_qid`
4. ✅ `scripts/wikidata_bootstrap.py` con caching, scoring 0..1, rate-limiting
5. ✅ `scripts/wikidata_cache/` (9306 entries, gitignored — rebuild con `--offline` flag)
6. ✅ 540 patches applicati in prod via `apply_data_patch.py`
7. ✅ Report `research_output/audit_v4/fase_a_report.md` + `docs/audit/fase_a_report.md`
8. ✅ ETHICS-010 decisione documentata (`docs/ethics/ETHICS-010-wikidata-cross-reference.md`)
9. ✅ 16 test unitari `tests/test_wikidata_bootstrap.py` (passing)

### Fase B (v6.70.0)

1. ✅ `scripts/wikidata_drift_check.py` con haversine + coord autofix heuristic
2. ✅ Drift check eseguito su 540 entità → 300 con drift
3. ✅ Report `research_output/audit_v4/fase_b_drift_report.md` + `docs/audit/fase_b_drift_report.md`
4. ✅ `fase_b_drift_data.json` strutturato
5. ✅ `fase_b_autofixable.json` (empty, 0 patches — coord drifts sono convention differences)
6. ✅ Commit + deploy v6.70.0

---

## Cosa resta per Fase C (in ordine di priorità)

### PRIORITY 1 — Review mid-band Wikidata matches (306 entità)

Le entità con score 0.50-0.85 hanno match probabilmente corretti ma con segnali incerti
(tipicamente: exact_label + type_exact ma senza year data, oppure year drift >10y ma < 30y).

**Source**: `research_output/audit_v4/fase_a_matches.json` — filter `0.50 <= score < 0.85`.

**Azione**:
```bash
# Extract mid-band per review
python -X utf8 -c "
import json
res = json.load(open('research_output/audit_v4/fase_a_matches.json', encoding='utf-8'))
mid = [r for r in res if 0.5 <= r['score'] < 0.85]
# sort by score DESC (high-scoring mid first)
mid.sort(key=lambda r: -r['score'])
with open('research_output/audit_v4/fase_c_midband_review.json', 'w', encoding='utf-8') as f:
    json.dump(mid, f, ensure_ascii=False, indent=2)
"
```

Per ogni entità: guardare `wikidata_label` e gli `alternatives`. Adottare il top (se plausibile)
o cambiare in un alternative. Produrre un patch JSON per `apply_data_patch.py`.

**Heuristic review**: top match of label "Kingdom of X" + AtlasPI name variant "Kingdom of X" è
di solito giusto anche a score 0.75. Dubious cases (Kosovo, Israel/Palestine, Taiwan) richiedono
maggior attenzione — sono territori politicamente carichi, Wikidata può non catturare la
prospettiva AtlasPI.

### PRIORITY 2 — HIGH drift review (108 entità)

Source: `research_output/audit_v4/fase_b_drift_report.md` Top 50 list.

**Categorie** (pattern emersi in Fase B):

**2a. Wrong QID match** (~8-10 entities):
Il matcher ha scelto un Wikidata Q-ID che non rappresenta bene l'entità AtlasPI.
Esempi da review urgente:

| Entity | Current QID | Current label | Issue |
|--------|-------------|---------------|-------|
| 552 Meroe | Q241790 | Kingdom of Kush | Meroe è capitale di Kush, non stessa polity. Sostituire con Q1146570 (Kingdom of Meroe) |
| 91 Rioghacht na hEireann | Q215530 | Kingdom of Ireland | Q215530 è post-Tudor 1542+. AtlasPI -500 è Gaelic Ireland — sostituire con Q1133950 o Q6574232 |
| 142 Mahavijayabahu | Q1530762 | Kingdom of Kandy | Kandy è 1469+, AtlasPI è Anuradhapura -543. Cercare Q3062015 (Anuradhapura Kingdom) |
| 864 林邑 | Q216786 | Champa | AtlasPI 林邑 (Linyi) è predecessore di Champa, non same. |
| 439 Gothia | Q874954 | Principality of Theodoro | AtlasPI 250 non matcha Theodoro 1300. Cercare Q1107049 (Gothia) |

**2b. Site vs Polity methodology** (~15-20 entities):
AtlasPI sta documentando la polity, Wikidata sta documentando l'archaeological site/area.
Generalmente AtlasPI è corretto, ma vale la pena aggiungere un `ethical_notes` esplicito.

Esempi:
- Entity 498 Ugarit: `ethical_notes` → "year_start -1450 riflette l'inizio del Kingdom of Ugarit;
  Wikidata Q191369 copre l'intero sito archeologico dal Neolithic -6000"
- Entity 272 Troy/Wilusa: `ethical_notes` → "year_end -1180 è fine Bronze Age Troy (Trojan War);
  Wikidata Q22647 include settlements successivi fino a età bizantina 500 CE"

**2c. Different historical capital convention** (~14 HIGH coord drift):
Nessun autofix: entrambi AtlasPI e Wikidata hanno posizioni legittime per capitali storiche
diverse. Aggiungere `ethical_notes` dove rilevante.

### PRIORITY 3 — Duplicate Q-IDs: 44 entities pointing to same QID

Source: `research_output/audit_v4/fase_a_report.md` "Duplicate Q-IDs" section.

**Decisione per ognuno**: merge o keep separate?

| QID | AtlasPI dup entities | Decisione consigliata |
|-----|---------------------|----------------------|
| Q33296 Mughal Empire | 12, 849 | Merge (stessa polity, due nomi Urdu) |
| Q207521 Ethiopian Empire | 24, 855 | Merge se periodo identico, else split con periodi diversi |
| Q389688 Achaemenid Empire | 27, 847 | Merge (Xšāça = Old Persian name, هخامنشیان = Persian/Farsi) |
| Q49683 Grand Duchy of Lithuania | 33, 653 | Merge (nomi in lituano + russo antico) |
| Q199821 Gran Colombia | 38, 723 | Keep split? (1819-1831 vs 1831 re-founded?). Verificare |
| Q156418 Kingdom of Hawai'i | 43, 548 | Merge |
| Q216786 Champa | 50, 864 | Keep split (林邑 è predecessore, Campā è Champa post-settecento) |
| **Q241790 Kingdom of Kush** | **52, 552 Meroe** | **Fix entity 552 → Q1146570 Kingdom of Meroe (vedi 2a)** |
| Q230791 Kingdom of Scotland | 90, 585 | Merge (Gaelic + Norwegian variants) |
| Q42585 Kingdom of Bohemia | 97, 586 | Merge (Czech + Norwegian) |

Lista completa nei fase_a_report.md e fase_a_matches.json filtrando per duplicate QIDs.

### PRIORITY 4 — 188 no-match entities (need review + name_variants)

Sub-categorie (da Fase A report):

**4a. Pre-contact indigenous polities (~60 entities)**:
Torres Strait Islander peoples, Comancheria, K'uhul Ajaw, Chamorro, etc.
Maggior parte NON hanno concetti equivalenti su Wikidata — lasciare `wikidata_qid = NULL`
con `ethical_notes` che spiega la lacuna. Eventualmente contribuire a Wikidata separatamente.

**4b. Label search failures (~40 entities)**:
Entità che HANNO un Q-ID su Wikidata ma il nostro search non lo trova perché l'AtlasPI
`name_original` è in script/lingua poco supportata da Wikidata search.

Esempi (verificare e aggiungere variants):
- Entity 47 `Dzimba dza mabwe` → aggiungere `name_variants: {"Great Zimbabwe", "en"}` → Q190106
- Entity 352 `Kraton Mataram` → aggiungere `{"Mataram Sultanate", "en"}` → Q1142194
- Entity 381 `कण्व` → aggiungere `{"Kanva dynasty", "en"}` → Q1281145

Dopo aggiunta variants → re-run `python -m scripts.wikidata_bootstrap --offline`
per picking up new matches.

**4c. Ancient city-states + archaeological sites (~40 entities)**:
Nabta Playa, Tu'i Ha'atakalaua, ecc. Copertura Wikidata variabile.
Alcuni hanno QID ma senza label search-friendly. Ricerca manuale + variants.

### PRIORITY 5 — Structural cleanup (original FASE_C scope)

Dalla FASE_A_B_HANDOFF originale:
- FK backfill `historical_sites.entity_id` NULL
- FK backfill `historical_cities.entity_id` NULL
- script/lang fix (45 mismatch)
- Chain reorder dove necessario
- New entities creation (per Wikidata concetti mancanti)

Questa lista è **invariate** — nessuna di queste è stata toccata in v6.69/v6.70.

### PRIORITY 6 — Nightly cron setup

Con l'infrastruttura Fase A+B pronta, setup nightly drift check:
```bash
# /etc/cron.d/atlaspi-drift
0 3 * * * root docker exec cra-atlaspi python -m scripts.wikidata_drift_check \
  --matches /app/data/wikidata/fase_a_matches.json \
  --entities /app/data/wikidata/entities_dump.json \
  --out-report /tmp/drift_$(date +\%Y\%m\%d).md \
  --out-data /tmp/drift_$(date +\%Y\%m\%d).json \
  --out-patches /tmp/drift_$(date +\%Y\%m\%d)_patches.json \
  --offline 2>&1 | logger -t atlaspi-drift
```

La modalità `--offline` usa la cache locale (già presente in container se montiamo il volume)
e non tocca Wikidata → zero cost, esegue in <1 min.

**Alert on diff**: se il drift report cambia da un giorno all'altro (nuovi HIGH), notifica.

---

## Artefatti della sessione Fase A+B

### Committed su main

- `alembic/versions/015_wikidata_qid.py` (migration)
- `src/db/models.py` (GeoEntity.wikidata_qid field)
- `src/api/schemas.py` (EntityResponse.wikidata_qid)
- `src/api/routes/entities.py` (_entity_to_response passes it)
- `scripts/apply_data_patch.py` (whitelist updated)
- `scripts/wikidata_bootstrap.py` (495 lines, scoring + caching)
- `scripts/wikidata_drift_check.py` (362 lines, haversine + coord fix heuristic)
- `tests/test_wikidata_bootstrap.py` (16 unit tests, all passing)
- `data/wikidata/v669_qid_high_confidence.json` (540 patches, reference)
- `docs/audit/fase_a_report.md`, `docs/audit/fase_b_drift_report.md`, this file
- `docs/ethics/ETHICS-010-wikidata-cross-reference.md`

### Gitignored (regeneratable)

- `scripts/wikidata_cache/` (~9300 HTTP responses, rebuild via bootstrap online run ~17 min)
- `research_output/audit_v4/*.json` (fase_a_matches, fase_b_drift_data, etc.)
- `research_output/audit_v4/*.md` (fase_a_report, fase_b_drift_report — duplicate of committed docs/audit/ versions)

### Prod state

- 540 entities in `geo_entities` have `wikidata_qid IS NOT NULL`
- Audit log `/app/data_patch_audit.log` records all 540 patches (timestamp, entity_id, rationale)
- Redis flushed post-apply

---

## Cosa NON fare in Fase C

Dagli asset del handoff originale FASE_A_B_HANDOFF.md (sezione "Cosa NON fare" per Fase A/B):
- ❌ NON riauditare entità già viste in audit_v2 — le lacune sono già note
- ❌ NON modificare `_get_continent()` — già fixed in v6.67

Nuovi per Fase C (da questa sessione):
- ❌ NON applicare drift "autofix" sulle date. Anche se Wikidata dice 1542 e AtlasPI dice -500, la scelta deve essere manuale (vedi ETHICS-010)
- ❌ NON adottare Wikidata come source-of-truth. L'obiettivo è cross-reference, non sostituzione
- ❌ NON rigenerare `scripts/wikidata_cache/` in prod — è in local dev worktree. Se Fase C ha bisogno di data nuovi, rigenera localmente poi push patch file

---

## Test run & sanity check

Per confermare lo stato, verifica:

```bash
# 1. Health live
curl -sS https://atlaspi.cra-srl.com/health | python -m json.tool
# → version 6.70.0, entity_count 1034

# 2. Sample API response ha wikidata_qid
curl -sS https://atlaspi.cra-srl.com/v1/entities/2 | python -m json.tool | grep wikidata_qid
# → "wikidata_qid": "Q12560"

# 3. Conteggio QIDs in DB
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "docker exec cra-atlaspi-db psql -U atlaspi -d atlaspi -A -t -c \
   \"SELECT COUNT(*) FROM geo_entities WHERE wikidata_qid IS NOT NULL\""
# → 540

# 4. Test suite locale
cd <worktree> && python -m pytest tests/test_wikidata_bootstrap.py -v
# → 16 passed
```

---

## Risorse

- **API Wikidata**: `https://www.wikidata.org/w/api.php` (wbsearchentities) + `https://www.wikidata.org/wiki/Special:EntityData/{qid}.json`
- **Rate limit**: 5 req/sec con UA dedicato, ~17 min per 1034 entities online, ~1 min cached
- **ETHICS-010**: `docs/ethics/ETHICS-010-wikidata-cross-reference.md`
- **Handoff originale**: `docs/audit/FASE_A_B_HANDOFF.md` (input di questa sessione)
- **Precedent audit**: research_output/audit_v2 (gitignored ma dovrebbe esistere localmente nel repo del user)

---

## Note aperte per utente

Nessuna decisione architetturale rimandata. Tutte le scelte della Fase A+B sono state prese
autonomamente seguendo il handoff + CLAUDE.md.

Un solo punto che potrebbe meritare discussione:

**Q**: Nella Fase B, abbiamo **0 autofixable**. Il conservatism scoring (km_diff > 1000 E flip produces < 20km) è forse troppo stretto? Ci sono ~14 HIGH coord drifts tra 200-1142km che sono tutti "diverse capitali storiche legittime" (Pakistan Islamabad vs Karachi, Golden Horde alternative Sarai sites) — nessuna va autofixata. Il sistema ha funzionato correttamente ma il conteggio autofixable=0 può sorprendere.

**R** (suggerita): mantenere conservative. Un autofix errato sulle coordinate potrebbe creare bug invisibili ("perché la Golden Horde è in Tatarstan invece che sulla Volga?"). Flag for review in Phase C, not autofix.

Buon lavoro per Fase C.
