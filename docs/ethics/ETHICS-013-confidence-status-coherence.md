# ETHICS-013 — Coerenza confidence ↔ status (no "certezza inventata")

**Status**: Adottato (v6.99.88, Wave 2.4 — 2026-05-29)
**Principio**: CLAUDE.md #3 (Trasparenza dell'incertezza)
**Audit ref**: Wave 2 full-audit, finding #4 (data-integrity) / #9 (ethics-fidelity), HIGH confermato.

## Contesto

CLAUDE.md, principio 3: *"Un dato incerto comunicato come tale è più onesto di
un dato certo inventato."* Eppure la funzione `derive_status()` in
`src/validation/confidence.py` — che avrebbe dovuto derivare lo `status` dalla
`confidence_score` — era **codice morto**: mai chiamata da `seed.py` né da
`ingest_new_entities.py`, che leggono `status` verbatim dal JSON
(`data.get("status", "confirmed")`).

Conseguenza: entità con `confidence_score < 0.5` potevano avere
`status='confirmed'`. Un agente AI che filtra `?status=confirmed` riceveva dati
a bassa confidenza come se fossero vettati — **esattamente la "certezza
inventata"** che il progetto dichiara peggiore dell'incertezza onesta. In
produzione (2026-05-29): 3 entità (Sosso #981, Berbera early #1008, Tichitt
#1003, tutte conf 0.4); su un seed fresco dal JSON: ~58 (lo storico
`fix_status_coherence.py` aveva corretto la prod una tantum, ma senza cablare la
regola nel codice né correggere il JSON sorgente → ogni reseed le re-introduce).
Il problema colpisce in modo sproporzionato polities indigene/decentralizzate
(cfr. [ETHICS-009](ETHICS-009-categorie-politiche-colon-imposte-su-polities-indigene.md)).

## Rischio di distorsione

Presentare un dato a bassa confidenza come `confirmed` è una falsa garanzia di
affidabilità verso i consumatori (umani e agenti) del database. Viola
direttamente il principio 3 e mina la credibilità dell'intero dataset, il cui
valore è proprio la trasparenza dell'incertezza.

## Alternative considerate

1. **Lasciare com'è** + correggere solo la documentazione → rifiutato: perpetua
   la falsa certezza nei dati.
2. **Cablare `derive_status()` nel seed/ingest** (opzione audit) → corretto ma
   con 5+ call-site in `seed.py` da modificare singolarmente (fragile,
   error-prone), e `derive_status` deriva *tutto* lo status, rischiando di
   sovrascrivere anche `disputed`.
3. **Enforcement a livello dato via event listener SQLAlchemy** (scelto):
   `before_insert`/`before_update` su `GeoEntity` forza `confirmed`→`uncertain`
   quando `confidence < 0.5`. Chokepoint unico che copre seed, ingest, patch e
   ogni futuro write-path ORM; non può divergere; lascia `disputed` intatto.

## Decisione

- Listener `_coerce_low_confidence_status` in `src/db/models/entities.py`:
  se `confidence_score < 0.5` e `status == 'confirmed'` → `status = 'uncertain'`.
- `status='disputed'` **non** viene mai toccato: resta riservato ai territori
  contestati (ETHICS-003, cap confidence ≤ 0.7). `uncertain` ≠ `disputed`:
  il primo è "poco documentato/incerto", il secondo è "conteso tra versioni".
- Test invariante `tests/test_confidence_status_coherence.py`: nessuna entità
  con `confidence<0.5 AND status='confirmed'` nell'intero corpus seedato.
- Backfill una tantum delle 3 entità in produzione (status confirmed→uncertain).
- **Riconciliazione documentazione**: CLAUDE.md e README dicevano erroneamente
  `<0.5 ⇒ status "disputed"`. Corretto in `<0.5 ⇒ "uncertain"` (disputed
  riservato a ETHICS-003). La `confidence_score` resta assegnata dall'autore del
  batch (giudizio umano); il listener garantisce solo la coerenza dello status.

## Conseguenze

- `?status=confirmed` ora esclude correttamente le entità a bassa confidenza
  (lievemente meno risultati "confirmed", ma onesti).
- `derive_status()`/`score_completeness()` restano non usati: candidati a
  rimozione o a riuso come check di sanity in un futuro intervento (audit
  finding low, non bloccante).
- Le polities decentralizzate di [ETHICS-009](ETHICS-009-categorie-politiche-colon-imposte-su-polities-indigene.md)
  a bassa confidenza ora sono almeno marcate `uncertain` — mitigazione parziale
  in attesa della Fase 2 strutturale di ETHICS-009.
