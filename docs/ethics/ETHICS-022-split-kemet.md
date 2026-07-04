# ETHICS-022 — Kemet: da "impero" continuo a civiltà-ombrello + entità-periodo

**Data**: 2026-07-04
**Versione**: v6.99.122
**Stato**: implementato
**Classe**: ETHICS-015 (super-aggregati), variante *ombrello* (non deprecazione)
**Metodo**: workflow di ricerca (assessment #26 + 6 entità-periodo, verdetti CORRECT)
+ cross-check ChatGPT gpt-5.5 (d/e/f/g AGREE con cautele). Log in
`data/chatgpt_review/20260704/`.
**Generatore**: `scripts/apply_kemet_split.py` → `scripts/sql_kemet_split.sql` + dual-write.

---

## Il problema

#26 `Kemet` tipizzava **3070 anni (-3100..-30) come un unico 'impero'
continuo** a conf 0.85. Due errori:

1. **Semantico**: *km.t* ("terra nera") nomina la **TERRA**, non lo stato; il
   nome nativo dello *stato* era *t3.wy* (Tawy, "le Due Terre", nel titolo
   regale *nb-t3wy*, "Signore delle Due Terre").
2. **Storico**: "un impero -3100..-30" cancella i **collassi statali reali**
   (Primo, Secondo, Terzo Periodo Intermedio) e presenta come "egiziano" il
   dominio **straniero** (Hyksos, kushita, assiro, persiano, macedone). In
   particolare il dominio kushita (XXV dinastia, -747) reso come evento
   "dell'impero egizio" è una **cancellazione inverso-coloniale** di un
   conquistatore nubiano (viola CLAUDE.md valore #4).

## Alternative considerate

1. **Deprecare #26 come Babilonia #171**: scartato — a differenza di
   Babilonia (un aggregato di *stati*), "Kemet/Antico Egitto" è una **civiltà**
   genuina e utile come ombrello. Wikidata tipizza Q11768 esattamente così
   (civilization/former country, **mai** empire). Deprecarla romperebbe
   permalink e perderebbe l'ombrello legittimo.
2. **Split completo in tutte le fasi (incl. Periodi Intermedi come entità)**:
   rinviato — le fasi di *collasso* non sono stati; modellarle come entità
   imporrebbe una falsa statualità. Le entità-periodo create sono solo le fasi
   di *statualità piena* (i tre Regni + il Regno tolemaico).

## Decisioni adottate (cautele d/e/f/g del cross-check)

### #26 → civiltà-ombrello (cautela e: AGREE)
- `entity_type`: `empire` → **`civilization`** (tipo già valido, usato da
  1 entità; documentato in API). Nome `Kemet`, span -3100..-30 e conf 0.85
  **invariati** (nome attestato, span ben delimitato: Narmer ~-3100 al low-end,
  annessione romana -30 sicura).
- `ethical_notes` riscritte: dice esplicitamente **civiltà-ombrello, NON stato
  continuo**, enumerando le rotture (i tre Periodi Intermedi = collasso statale;
  dominio Hyksos, kushita, assiro, persiano, macedone).

### Entità-periodo (cautela d: AGREE — schema `tꜣ.wy (X)`)
Nome primario = il nome attestato dello *stato* **t3.wy** con disambiguatore
tra parentesi (precedente Babilonia `𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)`):
- **`tꜣ.wy (Old Kingdom)`** -2686..-2160 (Q177819), capitale Memphis.
- **`tꜣ.wy (Middle Kingdom)`** -2055..-1650 (Q191324), capitale Itjtawy.
- **`tꜣ.wy (New Kingdom)`** -1550..-1069 (Q180568), `entity_type=empire`
  (l'unico periodo per cui "impero" è lo standard storiografico), capitale Waset.
- **`Πτολεμαϊκὴ βασιλεία`** -305..-30 (Q2320005): **dinastia macedone-greca**,
  nome greco (non t3.wy) perché stato ellenistico distinto, capitale Alessandria.

### Re-home dei 16 eventi (cautela f: AGREE)
- **12 eventi interni** (piramidi, Megiddo, Kadesh, Amarna, Popoli del Mare...)
  → spostati (eel.entity_id) all'entità-periodo corretta per anno.
- **Conquista kushita -747** (event #39): il link a Kemet resta come *terra
  conquistata* (VICTIM), ma si **AGGIUNGE** il link a **Kush #52** come
  MAIN_ACTOR — l'agentività nubiana è rappresentata, non cancellata.
- **Conquista persiana -525** (event #217): idem, aggiunto link **Xšāça #27**
  (Achemenidi) come MAIN_ACTOR.
- **Fondazione -3100** e **Alessandro -334** restano sull'**ombrello #26** —
  segnano l'inizio della civiltà e la fine del dominio nativo, non appartengono
  a una singola entità-periodo pharaonica.
- NON creata un'entità XXV dinastia (il dominio kushita è già la storia di
  Kush #52 — cautela f).

### Catena (cautela g: NO successione liscia)
Catena **"Egyptian pharaonic kingdoms: Old → Middle → New"** dei soli tre Regni;
ogni link tipizzato **RESTORATION** con nota esplicita sul **Periodo
Intermedio di collasso** interposto (FIP -2160..-2055; SIP + Hyksos
-1650..-1550, con la guerra di espulsione di Ahmose, is_violent). Il Regno
tolemaico **NON è nella catena** (750 anni di Terzo Periodo Intermedio, Periodo
Tardo e dominio straniero lo separano dal Nuovo Regno; è stato macedone
distinto). La catena NON afferma statualità continua.

## Rischi di distorsione mitigati

- **Continuità falsa**: i collassi dei Periodi Intermedi sono espliciti sui
  link; il Nuovo→Tolemaico non è incatenato.
- **Cancellazione inverso-coloniale**: l'agentività kushita (e persiana) è
  aggiunta come MAIN_ACTOR, non lasciata implicita sotto "impero egizio".
- **Terra vs stato**: km.t (civiltà/terra) come ombrello, t3.wy (stato) come
  entità-periodo — distinzione storicamente precisa.

## Follow-up

Terzo Periodo Intermedio, Periodo Tardo (Saiti, native XXVIII-XXX), Egitto
achemenide come entità proprie; poi estensione della catena oltre il Nuovo
Regno. Fase meroitica (#552 Meroe, deprecata nel merge v6.85) da ripristinare
per la catena nubiana #99.
