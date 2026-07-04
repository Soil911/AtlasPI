# ETHICS-021 — Split del super-aggregato Sri Lanka (#142 era un nome di re)

**Data**: 2026-07-04
**Versione**: v6.99.121
**Stato**: implementato
**Classe**: ETHICS-015 (super-aggregati di successione statale)
**Metodo**: workflow di ricerca (design dossier verificato CORRECT + 6 entità-periodo
ricercate) + cross-check ChatGPT gpt-5.5 (verdetti a/b/c AGREE; log in
`data/chatgpt_review/20260704/`).
**Generatore**: `scripts/apply_sri_lanka_split.py` → `scripts/sql_sri_lanka_split.sql`
+ dual-write JSON.

---

## Il problema

La linea singalese era rappresentata in modo gravemente scorretto:

- **#142** `name_original = 'මහා විජයබාහු'` = **il nome di un RE** (Mahā
  Vijayabāhu), non di uno stato; span assurdo `-543..1815` (2358 anni),
  conf 0.4 — un artefatto di label-sovrano di aourednik promosso a entità.
- **#386** `name_original = 'ගජබාහු'` = **un altro nome di re** (Gajabahu I,
  r. ~113-136), span 113-236, con 8 siti UNESCO generici della Sri Lanka
  ammucchiati sopra come bucket.
- **#600** `name_original` in **script KHMER corrotto** `ការ្យ​ ​សីលេន` (con
  zero-width space), span 1232-1597 — mescolava il periodo di transizione
  (Dambadeniya→Kotte) in un'unica entità con QID di Kotte.

Presentare la storia singalese attraverso nomi di re e uno script sbagliato
viola ETHICS-001 (il nome primario è quello attestato della *polity*).

## Alternative considerate

1. **Deprecare tutto e ricreare** (pattern Babilonia #171): scartato — a
   differenza di Babilonia, alcune di queste entità (#387 Polonnaruwa, #388
   Kandy, #601 Jaffna) sono già corrette e con FK; un wipe romperebbe permalink
   e catene esistenti senza guadagno.
2. **Rinominare in blocco senza ristrutturare**: scartato — non risolverebbe
   il super-aggregato #142 (span -543..1815 che divora Polonnaruwa, Kandy,
   ecc.) né il muddle Dambadeniya/Kotte di #600.
3. **Re-scope + create + chain** (scelto): re-scope chirurgico delle 2 entità
   mal-nominate ai loro periodi corretti, deprecazione dell'unica entità
   "nome di re" senza periodo proprio (#386), creazione delle 2 fasi mancanti
   (Gampola, Kotte), e una catena esplicita che documenta la successione con
   le cesure violente.

## Decisioni adottate (con le cautele del cross-check)

### Re-scope #142 → Regno di Anuradhapura
- `name_original`: `මහා විජයබාහු` → **`අනුරාධපුර රාජධානිය`** (Anurādhapura
  Rājadhāniya, attestato); `entity_type=kingdom`; `year_start -543 → -437`
  (Pandukabhaya, convenzione mainstream), `year_end 1815 → 1017` (annessione
  Chola di Rajendra I); conf 0.4 → 0.7. QID Q1965597 (già corretto =
  Anuradhapura Kingdom) invariato.
- Pulizia varianti: rimossa `Kingdom of Kandy` (è #388) e `Sinhalese Kingdom`
  (troppo generica, era il residuo del super-aggregato); tenuta `Anuradhapura
  Kingdom` (en). Aggiunte varianti per la tradizione: il **-543 (arrivo di
  Vijaya, Tambapanni)** è documentato come *tradizione* nella nota etica e in
  una variante, NON come fondazione — la cronologia lunga vs corta (437 vs 377
  a.C. per Pandukabhaya) è esplicitata, non risolta.
- territory_changes: il vecchio tc a -543 riscritto a -437 (Pandukabhaya) con
  la tradizione Vijaya annotata; il tc 993 (sacco Chola) tenuto; il tc 1815
  (colonizzazione) **eliminato** (era l'artefatto del mega-span; il 1815 è la
  caduta di Kandy #388).

### Deprecazione #386 Gajabahu + re-home
- #386 (nome di re, span coincidente con Anuradhapura) → `status=deprecated`
  con nota tombstone (ADR-005). I suoi 2 territory_changes (regno di Gajabahu)
  → re-homed a #142 come eventi interni al periodo di Anuradhapura.
- Gli **8 siti UNESCO** NON vanno tutti su Anuradhapura (sarebbe un secondo
  bucket): sono **distribuiti all'entità corretta** — Anuradhapura+Sigiriya →
  #142; Polonnaruwa → #387; Kandy+Dambulla → #388; Galle (forte coloniale),
  Sinharaja e Central Highlands (siti naturali) → `entity_id=NULL` (nessuna
  polity singola onesta). Questo è più corretto del re-home in blocco.

### Re-scope #600 → Regno di Dambadeniya
- `name_original`: script khmer corrotto → **`දඹදෙණිය රාජධානිය`**
  (Dambadeniya Rājadhāniya); `year_end 1597 → 1341`; QID **Q1589163 → Q3136869**
  (era il QID di Kotte, ora liberato per la nuova entità Kotte; Q3136869 =
  Dambadeniya). Copre la linea a capitali erranti Dambadeniya/Yapahuwa/Kurunegala.
- Varianti: rimossa `Kingdom of Kotte` (ora è entità propria); tenute
  `Kingdom of Dambadeniya` / `දඹදෙණිය රාජධානිය`.
- territory_changes: tenuto il tc di fondazione 1232; **eliminati** i tc 1412
  e 1597 (appartengono a Kotte, che ha i propri più ricchi).

### Nuove entità: Gampola (1341-1412) e Kotte (1412-1597)
- Gampola `ගම්පොල රාජධානිය` (QID Q6412581, conf 0.62): intervento militare Ming
  1411 (cattura e deportazione del re Vira Alakesvara — nominato come conquista
  armata, NON "scorta diplomatica"; letture cinese e singalese entrambe
  registrate).
- Kotte `කෝට්ටේ රාජධානිය` (QID Q1589163, conf 0.85): conquista violenta di
  Jaffna (Sapumal 1450-67), Vijayaba Kollaya 1521, assorbimento **coatto** ai
  portoghesi alla morte di Dharmapala 1597 (cliente sotto tutela militare, non
  "dono" libero — potenza coloniale nominata).

### Catena "Sinhalese kingdom trunk" (cautele b, c del cross-check)
Anuradhapura #142 → **Chola #110** (occupazione di Rajarata come
*Mummudi-sola-mandalam*, 1017-1070; tipizzata **CONQUEST straniera tamil**, con
nota esplicita che NON è una successione singalese — cautela b) → Polonnaruwa
#387 (RESTORATION 1070, Vijayabahu I espelle i Chola) → Dambadeniya #600
(CONQUEST 1215, invasione di Kalinga Māgha — anno **1215**, non 1232, che è la
consolidazione a Dambadeniya — cautela c) → Gampola → Kotte → *(Ceylon
portoghese, non ancora in DB)*. **Jaffna #601 = regno tamil PARALLELO**, catena
propria separata, NON nella linea singalese (evita la falsa nazionalizzazione
lineare — cautela c). **Kandy #388** è un ramo staccatosi da Kotte nel 1469
(già incatenato ai britannici 1815).

## Rischi di distorsione mitigati

- **Falsa linearità "trunk singalese"**: Jaffna resta parallela, Kandy ramo,
  l'occupazione Chola è un nodo straniero esplicito — la catena non riscrive
  una storia multi-etnica come lineare-singalese.
- **Nomi di re come stati**: eliminati (#142, #386, il muddle #600).
- **Assorbimento coloniale come "dono"**: la cessione di Dharmapala 1597 è
  registrata come assorbimento coatto sotto tutela portoghese.
