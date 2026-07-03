# ETHICS-018 — Dedup del trunk etiope (#22/#100) e merge Aksum latino→nativo (#853→#51)

**Data**: 2026-07-03 · **Stato**: decisione presa (ok di Clirim) + eseguita (v6.99.112).
**Correlati**: ETHICS-001 (nomi nativi primari), ETHICS-002 (transizioni esplicite),
ADR-005 (deprecated merge policy, v6.85), v6.99.101 (chain dedup), ETHICS-015 /
v6.99.106 (pattern re-homing ref), v6.99.107 (coerenza deprecati).
**Cross-check**: ChatGPT-5.5 (log in `data/chatgpt_review/20260703/`) — 2 correzioni
recepite, vedi §"Correzioni dal cross-check".

## Contesto

Prod conteneva DUE catene per la stessa successione statale dell'altopiano
etiope-eritreo:
- **#22 "Ethiopian State Trunk"**: Aksum → Zagwe → Impero solomonico, ma col nodo
  Aksum = **#853 "Aksum"**, duplicato in caratteri latini; senza D'mt.
- **#100 "Ethiopian state trunk: D'mt → Aksum → Solomonic restoration"**: con D'mt
  (#799 ደዐመተ) e l'Aksum nativo (#51 መንግሥተ አክሱም), ma SENZA la dinastia Zagwe —
  con una nota che ne dichiarava l'assenza dal dataset, oggi falsa (#491 ዛግዌ
  esiste ed era linkata in #22) — e con i metadati di transizione in convenzione
  invertita (transition sull'entità uscente anziché su quella subentrante).

L'entità **#853** è un duplicato di **#51** sfuggito al merge v6.85 perché privo di
`wikidata_qid` (quel dedup lavorava per Q-ID condiviso). Effetto visibile: negli
anni 100-940 la mappa rendeva **due polygon Aksum sovrapposti** (historical_map di
#51 + aourednik di #853) e il nome latino compariva a pari titolo del Ge'ez.

## Rischio di distorsione

1. **Continuità fantasma contata due volte** (classe v6.99.101): la stessa
   successione presentata agli agenti come due lignaggi distinti.
2. **Doppio Aksum** confirmed con boundary sovrapposti; nome latino a pari titolo
   del nativo (viola ETHICS-001).
3. **Cancellazione della Zagwe**: scegliere la variante #100 così com'era avrebbe
   omesso la dinastia Zagwe — ripetendo la storiografia solomonica che la tratta
   da parentesi illegittima. La Zagwe (Lalibela) è una dinastia legittima e sta
   nel trunk.
4. **Continuità D'mt→Aksum sovra-asserita**: il link attraversa un gap
   archeologico di ~500 anni (D'mt si dissolve ~400 a.C., consolidamento aksumita
   ~100 d.C.) — asserirlo senza caveat inventerebbe continuità.

## Alternative considerate

- **A. Tenere entrambe le catene**: respinta — duplicazione semantica.
- **B. Sopravvive #100**: respinta — omette la Zagwe, convenzione link invertita,
  permalink più recente.
- **C. Sopravvive #22 estesa a 4 nodi nativi, #100 eliminata**: SCELTA.
- **Per #853**: delete respinto (ADR-005: permalink preservati) → deprecation +
  re-homing ref a #51, come v6.85/v6.99.106.

## Correzioni dal cross-check (ChatGPT-5.5, recepite)

1. **Aksum→Zagwe NON è CONQUEST**: gli Zagwe non conquistarono Aksum — emersero
   dalla frammentazione successiva al collasso (tradizione di Gudit/Yodit
   ~940-960; dinastia Zagwe propriamente datata ~1137 in molte cronologie).
   Tipo corretto nel vocabolario esistente: **DISSOLUTION** (il potere passa
   attraverso il collasso del predecessore — stesso pattern URSS→successori),
   `is_violent=true` per la tradizione del sacco di Gudit, dichiarata come
   contesa nelle note. L'anno 940 marca la fine di Aksum, non l'inizio Zagwe.
2. **La variante 'Medri Bahri' NON migra a #51**: designa una polity successiva
   distinta (altopiano costiero eritreo, ~XV-XIX sec.), non Aksum. Tenerla come
   alias di Aksum fuorvierebbe gli agenti e creerebbe collisione quando Medri
   Bahri verrà creata come entità propria. → **eliminata** con motivazione;
   **Medri Bahri aggiunta alla coda entità-da-creare**.

## Scelta adottata (eseguita in v6.99.112)

Catena unica **#22** a 4 nodi in convenzione canonica, tutti con nome nativo:
**ደዐመተ → መንግሥተ አክሱም (SUCCESSION 100, gap dichiarato) → ዛግዌ (DISSOLUTION 940,
violent, Gudit contesa) → የኢትዮጵያ ንጉሠ ነገሥት መንግሥት (REVOLUTION 1270, Kebra Nagast
dichiarato mito di legittimazione)**. Confidence catena 0.8→**0.7** (l'anello
D'mt è debole: l'incertezza si dichiara). #100 hard-delete (precedente
v6.99.101; audit trail = questo record + CHANGELOG + SQL versionato). #853
deprecated con pointer; ref ri-homati a #51 (evento Ezana/Meroe, 3 varianti
EN/IT, fonte primaria delle iscrizioni di Ezana — fonte indigena, coerente col
valore "storiografia non-occidentale" —, 5 territory_changes; le 3 fonti
accademiche duplicate restano sul record deprecato come da precedente).
La territory_change #93 di #51 (conflava conversione 325 + campagna di Meroe)
è **eliminata**: superseduta dalle più precise 2424 (325, religiosa) e 2425
(350, Meroe). Fix collaterale: `year_start` JSON di #51 era −400 (inglobava
il gap D'mt) → allineato al valore prod corretto (100).

## Follow-up

- Creare l'entità **Medri Bahri** (ምድሪ ባሕሪ, altopiano eritreo ~1450-1890) —
  aggiunta alla coda in `docs/structural-tracks-plan.md`.
- Anni di #51 (year_end 960) vs transizione 940 vs Zagwe start 900: overlap
  dichiarato nelle note del link, NON ricalibrato silenziosamente; eventuale
  ricalibrazione = item enrichment separato.
- Visual check post-deploy (CLAUDE.md): mappa ad anno ~500, un solo polygon Aksum.
