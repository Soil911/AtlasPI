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

### 1. Il matcher fuzzy ha bisogno di ulteriori guardie

ETHICS-006 ha aggiunto capital-in-polygon e geographic distance check.
Phase H rivela che ancora **non basta**: il matcher può ancora produrre
collision quando il polygon "matched" è ENORME (es. tutta l'Africa) — la
capitale dell'entità è dentro, ma il polygon è 100× troppo grande per
quell'entity_type.

Future hardening (da implementare in iterazione successiva):
- **Area sanity check**: rifiutare match se `polygon_area > 3× type_ceiling`
  (es. city-state non può matchare polygon > 100k km²)
- **Specifica boundary_aourednik_name blacklist**: nomi come "Bantou",
  "Polynesians", "West African cereal farmers", "Eastern North American
  hunter-gatherers" sono cultural-zone labels, non political polygons —
  mai matchare a singoli stati
- **Required: 1-to-1 matching per polygon**: se 2+ entità sono già matchate
  allo stesso polygon, rifiutare la terza match e marcare per review

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
