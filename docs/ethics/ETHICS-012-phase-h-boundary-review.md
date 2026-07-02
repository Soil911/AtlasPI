# ETHICS-012 — Phase H boundary review systematica e perdita di precisione apparente

**Data**: 2026-05-28
**Stato**: Accettato
**Autore**: Phase H boundary review (Claude Code, sessione singola autonoma)
**Impatto**: Alto — 340 entità polygon-fixed, confidence_score ridotta per ~280
**Riferimenti**: ETHICS-005 (Natural Earth), ETHICS-006 (fuzzy displacement),
ETHICS-009 (categorie politiche imposte)

## Sommario

Il fuzzy matcher in `boundary_match.py` (sia per aourednik che natural_earth)
aveva prodotto **~100 polygon collisions** in cui storicamente diverse entità
condividevano lo stesso polygon perché matchate ad un "super-gruppo"
culturale-linguistico nel dataset upstream.

Esempi:
- Bunyoro pre-Babito (kingdom Uganda 1300) + Bigo bya Mugenyi (sito
  archeologico Uganda 1300) + Ntusi (settlement Uganda 1000) + Mbundu
  pre-Ndongo (confederation Angola 1200) **condividevano l'intero
  polygon dell'area linguistica Bantu** (693 deg² da Camerun a Sudafrica).
- 10 polities etiopi (Sultanato di Harar, Kaffa, Awsa, Shewa, Jimma,
  Sidama, Gurage, Mengist Ityop'p'ya 1270, ecc.) condividevano il
  polygon dell'**Etiopia moderna** da Natural Earth.
- 6 stati Levantini medievali (Fatimidi 909, Ayyubidi 1171, Crociati
  1099, Ikhshididi 935, Ziridi 972, Beit al-Maqdis 1187) condividevano
  un polygon aourednik etichettato "Fatimid Caliphate".
- 5 polities antico Levante (Tadmor/Palmyra, Phoenicia, Israele, Giuda,
  Edom) condividevano un polygon etichettato "Kingdom of David and
  Solomon" — entità storicamente contestata + anacronistica per 4 su 5.

Questi mismatch erano **falsamente precisi**: implicavano che entità
storiche distinte avessero confini geografici identici, quando in realtà
nessuna evidenza storiografica lo sosteneva.

## Dilemma etico

Il fix richiedeva sostituire i polygon esistenti con cerchi attorno alla
capitale, calibrati per entity_type e ricerca storica specifica. Questa
sostituzione comporta:

**Costi**:
- Perdita di "precisione visiva" (cerchi sono visualmente meno informativi
  di polygon dettagliati)
- Perdita di forme territoriali distintive (es. confini fluviali, costiere)
- Rischio di sembrare un "downgrade" della qualità del dataset

**Benefici**:
- Eliminazione di **errore storico attivo** (polygon che mentivano sull'estensione)
- Eliminazione di **polygon collisions** (entità diverse che sembravano
  identiche sulla mappa)
- Onestà sui limiti di conoscenza (cerchio = "approssimazione attorno alla
  capitale", polygon dettagliato = "confine documentato")
- Ridotta confidence_score riflette la realtà del dato

## Decisione

### Sostituire polygon mismatched con cerchi storici (implementato)

Per ogni entità con polygon mismatched:

```sql
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(
    ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography,
    <radius_meters>
  )::geometry)),
  boundary_geom = ST_Multi(...),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = ethical_notes || E'\n\n[v6.99.79-tier-X] <documentazione>'
WHERE id = ?;
```

Il raggio è calibrato per:
1. **Entity_type**: city-state 30-80km, kingdom 100-500km, empire 500-2500km,
   archaeological site 5-30km, nomadic confederation 400-1000km
2. **Ricerca storica specifica** documentata in `ethical_notes`
3. **Capitale dichiarata** come anchor (la confidenza nel cerchio dipende
   dalla confidenza nelle coordinate della capitale)

### Confidence reduction trasparente

Tutte le entità con polygon sostituito hanno `confidence_score` ridotto a
≤0.65 (vs 0.85+ dei polygon originali "curati"). Questo riflette la realtà:
- Il cerchio è approssimativo per definizione
- Non sostituisce un polygon davvero curato (es. da mappa storica con
  confini documentati)
- L'utente vede il cerchio E vede la confidence — la combinazione
  comunica correttamente "estensione approssimativa, capitale solida"

### ETHICS notes esplicite per ogni fix

Ogni `UPDATE` aggiunge a `ethical_notes`:
1. Riferimento alla Phase H (`[v6.99.79-tier-X]`)
2. Polygon precedente erroneamente assegnato (es. "Bantou polygon (693 deg²)")
3. Reasoning storico per il nuovo cerchio (es. "Bunyoro pre-Babito Cwezi-era
   kingdom centered on Bigo/Ntusi earthworks ~200km")
4. Dove rilevante: contesto coloniale, genocidi, dispossesso (ETHICS-007)

Esempio:
```
[v6.99.79-tier1B/bantou-fix] Replaced erroneously-shared "Bantou"
linguistic polygon (entire sub-Saharan Africa) with 200km capital-based
circle around Bigo. Bunyoro pre-Babito was the Cwezi-era kingdom precursor
of Bunyoro-Kitara, centered on the Bigo/Ntusi earthwork sites in Western
Uganda. Bantu is a linguistic family (~500 languages), NOT a unified polity.
```

### Code-level regression guard

Per prevenire la re-introduzione del pattern, nuovo
`src/ingestion/boundary_collision_guard.py` rileva al boot:
- **Big groups**: ≥4 entità con polygon byte-identical
- **Super-group alerts**: stesso `boundary_aourednik_name` + >200 anni di
  span tra entità (signal molto forte di fuzzy-match error)

`tests/test_boundary_collisions_audit.py` (3 test) fa CI fence: se il
matcher upstream ricomincia a produrre questi mismatch, il PR si blocca
prima del merge.

## Decisioni di scope rifiutate

### Rifiutato: mantenere i polygon mismatched

Argomento: "Il polygon esistente, anche se sbagliato, dà più informazione
visiva di un cerchio."

Rifiutato perché:
- I polygon erano **falsi positivi attivi**: implicavano confini documentati
  dove non esistevano
- Più entità con polygon identico è MISLEADING (sembra "10 stati con stesso
  territorio" quando in realtà nessuno di loro aveva quel territorio
  specifico)
- L'utente non può distinguere tra polygon falsamente preciso e cerchio
  onestamente approssimativo — meglio essere onesti

### Rifiutato: cancellare le entità duplicate

12+ duplicati identificati (Bohemia Czech/Danish, Buyid Arabic/Persian,
Viceroyalty con/senza accento, Hashemite Hijaz word order, ecc.).

Argomento: "Cancellarle pulisce il dataset."

Rifiutato perché:
- Cancellazione perde dati dipendenti (territory_changes, sources,
  capital_history) — alcune potrebbero avere riferimenti unici
- Merge corretto richiede review caso-per-caso (alcuni "duplicati" sono
  effettivamente periodi distinti con nomi simili)
- Decisione differita: marcate con `[DUPLICATE_OF=primary_id]` in
  ethical_notes + confidence ridotta; merge in future cleanup PR
  con review umana

### Rifiutato: auto-fix nel collision guard

Argomento: "Il guard potrebbe auto-correggere le collision rilevate."

Rifiutato perché:
- Auto-correction rischia di distruggere matching legittimi (es. una
  federazione + i suoi membri legittimamente condividono territorio)
- Il guard è **informational**: logga warning, non modifica i dati
- Fix manuale con ETHICS note è preferibile a fix automatico silenzioso
  (ETHICS-002: ogni cambio territoriale ha bisogno di motivazione esplicita)

## Conseguenze accettate

### Aumento di entità con boundary_source = 'approximate_circle'

Pre-Phase-H: 0 entità con source `approximate_circle`
Post-Phase-H: 280 entità (~27% del totale 1037)

Questo è un **aumento di trasparenza**: il dataset ora dichiara
esplicitamente quante entità hanno boundary approssimativo vs curato.
Prima questa informazione era nascosta dietro polygon falsamente precisi.

### Visualizzazione "meno bella"

L'app mostrerà più cerchi e meno polygon dettagliati. Questo è accettato
come prezzo dell'onestà del dato. La roadmap futura può includere:
- Mappe storiche specifiche per entità ad alta visibilità (Wari Empire,
  Mongol Empire, ecc.) per migliorare progressivamente i polygon curati
- Distinzione visiva chiara tra cerchio e polygon (es. cerchio con
  tratteggio per indicare approssimazione)

### Dipendenza dalla qualità di capital_lat/lon

I cerchi sono ancorati alle coordinate della capitale. Se una capitale è
sbagliata, il cerchio è sbagliato.

Mitigazione: gli ETHICS notes documentano la capitale assunta. Se future
ricerche correggono la capitale, il fix è banale (`UPDATE` ricalcola il
cerchio dalle nuove coordinate).

## Lezioni per il futuro

### 1. Il matcher fuzzy ha bisogno di ulteriori guardie (IMPLEMENTATO v6.99.80)

ETHICS-006 ha aggiunto capital-in-polygon e geographic distance check.
Phase H rivela che ancora **non basta**: il matcher può ancora produrre
collision quando il polygon "matched" è ENORME (es. tutta l'Africa) — la
capitale dell'entità è dentro, ma il polygon è 100× troppo grande per
quell'entity_type.

**Status implementazione (commit 8aad160, v6.99.80):**

✅ **Area sanity check** (`_is_polygon_too_large_for_type`):
- Aggiunto in `aourednik_match.py` e `boundary_match.py`
- `TYPE_MAX_AREA_DEG2` per ogni entity_type (city-state 4 deg², kingdom
  640 deg², empire 3200 deg², earthwork-complex 0.5 deg², ecc.)
- Factor: 2× per STRICT types (city-state, principality, duchy, chiefdom,
  earthwork), 3× per altri (kingdom, empire, ecc.)
- Applicato a strategy `fuzzy_name`, `subjecto`, `partof`,
  `capital_in_polygon` — non applicato a `exact_name` (trusted)
- Test: `tests/test_aourednik_match_super_group_guard.py` +
  `tests/test_boundary_match_area_sanity.py` (29 test totali)

✅ **Super-group label blacklist** (`SUPER_GROUP_LABELS_BLACKLIST`):
- 44 entries: Bantou, Polynesians, Hittites, Cimmerians, Moche, Olmec,
  Nazca, Huari Empire, Sui Empire, Abbasid Caliphate, Achaemenid Empire,
  Parthian Empire, Sultanate of Delhi, Fatimid Caliphate, Ghaznavid
  Emirate, Chagatai Khanate, Golden Horde, Byzantine Empire, Holy Roman
  Empire, Kingdom of David and Solomon, Greek city-states, Taino,
  Amazon hunter-gatherers, Eastern North American hunter-gatherers,
  West African cereal farmers, "minor states", Annam, Qataban, Nabatean
  Kingdom, Urartu, Yemen, Mwenemutapa, Cuman-Kipchak confederation, Jin,
  Sasanian Empire, Srivijaya Empire, Pagan, Arakan, Bosnia, Toltec
  Empire, Suren Kingdom, Ur, Phrygians, Cimerians (aourednik spelling)
- Applicato in `aourednik_match.py` quando strategy ≠ `exact_name`
- L'entità legittima primaria (es. "Fatimid Caliphate" empire 909-1171)
  può comunque ottenere la sua polygon via `exact_name` strategy
- Test: spot-check di tutte le label che hanno causato Phase H regressions

⏳ **1-to-1 matching per polygon** (DEFFERED a iterazione futura):
- Richiede stato condiviso tra match calls (set di polygon già assigned)
- Più complesso, beneficio marginale ora che area + blacklist sono attivi
- Future: tracking via dict `geojson_hash → [entity_keys]` durante batch
  ingestion, alert se 3+ entity_keys condividono lo stesso hash

### 2. Il collision guard al boot è preziose

Lo stesso pattern di collision potrebbe ri-emergere con:
- Nuovi batch di ingestion JSON da future Phase
- Re-import accidentale di seed data
- Bug di refactor in boundary_match.py

Il guard al boot scopre questo gratis e logga warning visibili.

### 3. Pre-deploy backup è obbligatorio per modifiche di massa

Pre-Phase-H ho fatto:
```
docker exec cra-atlaspi-db pg_dump -U atlaspi atlaspi \
  --table=geo_entities > /root/atlaspi-boundary-backup-20260528-114032.sql
```

37MB di dump. Se Phase H avesse rotto qualcosa, rollback era 1 comando.
Pratica da formalizzare in CLAUDE.md come "obbligatorio prima di
modifiche di massa al DB".

## Conformità ETHICS

Phase H rispetta:

- **ETHICS-001**: nomi originali mantenuti (sostituito polygon, non nomi)
- **ETHICS-002**: ogni territory change (incluso il fix Phase H) è
  documentato con `change_type` esplicito via ethical_notes
- **ETHICS-003**: territori contestati (Tibet, Kashmir, Taiwan) hanno
  ricevuto polygon distinti dove necessario, status='disputed' invariato
- **ETHICS-004**: confini generati hanno `boundary_source = 'approximate_circle'`
  esplicito, confidence_score ridotto, ethical_notes documentano l'origine
- **ETHICS-005**: provenance documentata (vecchio source rimosso,
  approximate_circle nuovo, ethical_notes spiega il switch)
- **ETHICS-006**: estende l'audit ETHICS-006 (capital-in-polygon) con
  area-based check + super-group detection
- **ETHICS-007**: ETHICS notes Phase H includono linguaggio non-eufemistico
  per genocidi, colonialismo, schiavitù dove rilevante (es. CSA, Estado
  Novo, Deutsch-Ostafrika, Etat indépendant du Congo)
- **ETHICS-009**: Aboriginal Australian Nations + Indus Valley
  Civilization hanno ricevuto ETHICS notes esplicite sul rischio di
  classificazione semplicistica (250+ nazioni indigene compressa in
  "confederation", "city-state" per una civiltà urbana, ecc.)

## Status

**Implementato**: ✅ (commit b63c9c1 → 810c084, su main)
**Deployato in produzione**: ✅ (cra-deploy atlaspi, 2026-05-28)
**Collision guard attivo**: ✅ (`status: OK, 0 collision groups` in production)
**Test CI fence**: ✅ (3 test in tests/test_boundary_collisions_audit.py)
**Documentato**: ✅ (questo file + CHANGELOG v6.99.80 + LOOP_STATE.md +
phase1_screening_report.md + lapita_label_fix_notes.md)

---

## Aggiornamento 2026-05-31 — Backport JSON↔prod (Wave 2 audit #7, v6.99.93)

**Stato**: Accettato · **Tipo**: sync alla realtà-prod *già revisionata* (NON
una nuova decisione etica) · **Deploy prod**: nessuno (la prod è già corretta).

### Problema

I fix Phase H (cerchi `approximate_circle`) e una campagna **precedente** della
iter-series (`scripts/sql_iter*_boundaries.sql` + `sql_manual_boundaries.sql`,
poligoni storici `historical_approximation` disegnati a mano) erano stati
applicati **solo in produzione via SQL**, mai propagati al sorgente
`data/entities/*.json`. Poiché `seed_database()` gira solo su DB vuoto, un seed
fresco / deploy da DB vuoto **(a)** rigenerava i vecchi super-group polygon →
~22 collision group (verificato: 29 super-group alert sul JSON pre-backport) e
**(b)** perdeva i poligoni storici ricercati. Questo bloccava il fence collision
(#7) e avrebbe regredito silenziosamente ogni redeploy pulito.

### Cosa è stato sincronizzato (599 entità)

Export **read-only** da prod (`data/fixes/phase_h_backport_export.json`,
2026-05-31) → `scripts/backport_phase_h_to_json.py` aggiorna, per ogni entità,
**solo lo stato confine revisionato**:
- `boundary_geojson`, `boundary_source` (372 `approximate_circle` + 227
  `historical_approximation`), provenance aourednik/Natural-Earth;
- **`confidence_score` + `status`**: backportati INSIEME alla geometria perché
  Phase H/iter li hanno rivisti come **un'unica decisione coerente**
  (ETHICS-004/012/013) — i cerchi hanno confidence ridotta, i poligoni ricercati
  alzata, alcuni duplicati marcati `deprecated`. La sola geometria avrebbe
  lasciato **58 entità** con confidence/status incoerenti col confine.

**Matching**: 578/599 per `name_original`; 14 rename in script nativo (ETHICS-001,
es. `Гетьманщина`→`Hetmanshchyna`, `بازين`→`Bazin`) risolti con mappa
`id→nome JSON` vettata; 7 (insert prod-only / rename ambigui) **saltati** e
tracciati come follow-up. Il backport è idempotente e si rifiuta di scrivere se
il fence non è verde sul risultato.

### Sotto-decisioni etiche

1. **Cap ETHICS-003 sui territori contestati**: 6 entità `status='disputed'`
   avevano in prod confidence 0.85/0.80 (violazione *latente* della regola
   "contestati ≤ 0.70"). Il backport le **cappa a 0.70** (identico a
   `sync_boundaries_from_json`): il JSON risulta *più* conforme della prod. È una
   **correzione etica intenzionale**, non un mismatch accidentale. → La prod
   resta non-conforme su queste 6: da cappare al prossimo deploy (fuori scope —
   nessun deploy qui). Vedi follow-up #3.
2. **`status` come companion di `confidence`** (incluso `deprecated`):
   `deprecated` = duplicato/superseduto (ADR-005, accoppiato a
   `[DUPLICATE_OF=...]` in `ethical_notes` in prod) — **NON** significa "entità
   storicamente illegittima". Senza il backport di `status`, un seed fresco
   resusciterebbe duplicati fuorvianti come record validi: distorsione peggiore
   dell'omissione di un polygon.
3. **Esclusi dal backport**: `name_original` (i ~14 rename in script nativo
   restano divergenti — **debito ETHICS-001**, follow-up #2) e `ethical_notes`
   (la narrativa per-entità resta in prod + nei file tier SQL + in questo
   record; un consumatore del solo JSON ha meno contesto — accettato e
   documentato).

### Fence collision attivato (chiude audit #7)

- `tests/test_boundary_collisions_json_audit.py` — variante **PostGIS-free**
  (`detect_json_boundary_collisions`: sha256 della geometria + stesso
  `boundary_aourednik_name` con span > 200 anni) sul JSON sorgente; gira nel job
  SQLite di **ogni PR** + un test "guard-the-guard" sintetico.
- `scripts/ci_collision_check.py` — seed fresco del JSON in **PostGIS reale** +
  guard `detect_boundary_collisions`, nel job `postgres-migrations`.
- Verifica: seed fresco dal JSON backportato → **0 super-group collision** (era 29).

### Provenance enum (ETHICS-005)

`approximate_circle` e `historical_approximation` aggiunti all'enum documentale
(`tests/test_boundary_provenance.py`, `src/api/schemas.py`): erano usati in prod
dai tempi di Phase H/iter ma mancavano dalla lista valida.

### Cross-check

Decisione cross-checkata con **ChatGPT-5.5** (ethics review, log in
`data/chatgpt_review/`): verdetto **SOUND-WITH-CAVEATS**. Le caveat (loggare il
cap come correzione intenzionale; chiarire la semantica di `deprecated`; triage
prossimo dei 7 insert + sync dei nomi nativi) sono recepite qui sopra e nei
follow-up.

### Follow-up tracciati (debito; NON bloccano audit #7)

1. **Triage dei 7 insert prod-only** (`Premier Empire français`,
   `Res Publica Romana`, `சோழர் (Sangam-era)`, `افشاریان`, `Kingdom of Quito`,
   `مقديشو`, `𒆍𒀭𒊏𒆠 (Old Babylonian)`): aggiungere come entità complete al JSON
   o confermare merge. Rischio rappresentazionale: assenti dai deploy puliti
   finché non triagiati.
2. **Sync `name_original` nativo prod→JSON** per i ~14 rename (debito ETHICS-001:
   il JSON ha ancora forme latine dove la prod ha la forma locale primaria).
3. **Cappare in prod** le 6 entità `disputed` > 0.70 al prossimo deploy.

---

## Aggiornamento 2026-05-31 (#2) — Riconciliazione residua (v6.99.94)

Chiusi i follow-up **#1 e #2** sopra (script `scripts/backport_residual_to_json.py`,
input read-only `data/fixes/phase_h_residual_export.json`). Source-only, **nessun
deploy**. Il JSON ora ha **1038 entità deduplicate = totale prod** (parità di conteggio).

### Triage dei 7 "insert" → 6 ADD + 1 rename

Export completo da prod dei 7 id `SKIP` del backport v6.99.93 → triage:
- **6 entità realmente assenti dal JSON, aggiunte** in `data/entities/batch_36_prod_reconciliation.json`
  (entità complete da prod, con `ethical_notes`):
  - `Res Publica Romana` (-509..-27, distinta da `Imperium Romanum`).
  - `Premier Empire français` (1804..1815, distinta da Royaume/République).
  - `افشاریان` (Afsharidi, 1736..1796).
  - `𒆍𒀭𒊏𒆠 (Old Babylonian)` (-1894..-1595; prod la tiene distinta dalla
    Neo-Babylonian id 490). **Nota prod-debt**: prod ha ANCHE `𒆍𒀭𒊏𒆠` "combinata"
    (id 171, -1894..-539) che si sovrappone — da riconciliare in prod (follow-up #4).
  - `சோழர் (Sangam-era)` (-300..300, distinta dalla Chola medievale id 110).
  - `Kingdom of Quito` (1000..1470): **entità contestata/leggendaria**, ma prod la
    gestisce in modo responsabile — `status='disputed'`, conf 0.5, `ethical_notes`
    che documenta la narrazione di Velasco (1789) e l'assenza di evidenza
    archeologica. Aggiungerla è **conforme a ETHICS-002/003** ("mostrare tutte le
    versioni"): coesiste come entità distinta accanto a `Quitu-Cara` e `Kitu`.
- **1 era un rename mal classificato**: prod id 741 `مقديشو` È il JSON `Maqdishaw`
  (stessa sultanato 900-1600, stessa capitale). Riclassificata come rename **+
  backport del boundary** che v6.99.93 aveva mancato (era ancora `aourednik`).

### 15 rename `name_original` → script nativo (ETHICS-001)

`name_original` portato alla forma locale primaria (es. `Hetmanshchyna`→`Гетьманщина`,
`Raska`→`Србија`, `Maqdishaw`→`مقديشو`); `name_variants` sincronizzate da prod
(union, lossless — la vecchia forma latina è preservata come variante).
**Cascade integrità**: aggiornati i 2 riferimenti per-nome in file non-entità così
che il linking al seed sopravviva — `data/chains/batch_20_balkan.json` (link `Raska`)
e `data/events/batch_20_trade_exploration.json` (`entity_links` `Maqdishaw`).

### Note

- 4 insert arrivavano da prod **senza `name_variants`** (viola l'invariante JSON
  "ogni entità ha ≥1 variante"): aggiunte le forme inglesi documentate
  (First French Empire, Afsharid dynasty, Old Babylonian Empire, Early Cholas) —
  miglioria di ricercabilità. **Prod ne è privo → arricchire in prod (follow-up #5).**
- Suite completa verde (1316 passed), fence collision a **0**, ruff verde.

### Follow-up aggiornati

1. ✅ Triage 7 insert (fatto — 6 add + 1 rename).
2. ✅ Sync nomi nativi (fatto — 15 rename + cascade).
3. ✅ Cappare in prod le `disputed` > 0.70 — fatto in v6.99.107 (il set era
   cresciuto a 10 entità; cap applicato a tutte, prod SQL + verifica JSON).
4. ✅ (v6.99.107) name_variants mancanti in prod per 1037/1038/1039/1040 —
   INSERT da batch_36 nello stesso SQL.
5. ⏳ **Debito residuo scoperto 2026-07-02** (diff completo prod↔JSON):
   (a) 18 rename nativi prod-only non ancora sincronizzati nel JSON (stessa
   classe del punto 2 — es. `Rus' Kyivska`→`Русь Київська`,
   `Sakartvelos samepo`→`საქართველოს სამეფო`); (b) ~299 divergenze di
   confidence BIDIREZIONALI (batch_32 boost mai applicato a prod vs
   ricalibrazioni prod mai backportate) → serve una policy di
   riconciliazione dedicata, non un backport meccanico; (c) 30 record JSON
   con nome duplicato (semantica last-wins del seed: i primi sono
   ombreggiati e inerti — cleanup cosmetico.
4. ⏳ Prod: riconciliare le 3 entità Babilonia sovrapposte (171 combinata vs
   490 Neo + 1039 Old) — deprecare/restringere la 171.
5. ⏳ Prod: aggiungere `name_variants` ai 4 insert che ne sono privi.
