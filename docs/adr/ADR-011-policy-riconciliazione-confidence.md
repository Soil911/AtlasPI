# ADR-011 — Policy di riconciliazione confidence JSON↔prod

**Data**: 2026-07-03 · **Stato**: approvata da Clirim ed eseguita (v6.99.113).
**Contesto**: M4 / ETHICS-012 follow-up #5 · **Correlati**: ETHICS-003 (cap
disputed 0.70), ETHICS-013 (conf<0.5 → uncertain), ADR-005 (merge policy),
memoria `project_reconciliation_debt`.

## Problema

286 entità avevano `confidence_score` divergente tra la vista JSON effettiva
(last-wins su `data/entities/*.json`, ciò che vedrebbe un fresh-seed) e prod
(ciò che vedono gli agenti). Cause: sessioni enrichment applicate a prod con
fonti ma mai backportate al JSON (la maggioranza), il boost `batch_32` mai
applicato a prod (2 righe disputed), ricalibrazioni JSON recenti mai deployate
(il seed non gira su DB popolato).

## Decisione (per classi, con audit obbligatorio)

1. **Nessun allineamento silenzioso**: ogni modifica passa da
   `scripts/reconcile_confidence.py` (dry-run di default) che scrive l'audit
   log versionato in `data/fixes/conf_reconciliation_audit_<data>.json`.
2. **prod_higher (197)** → **prod vince**: backport JSON:=prod. La confidence
   prod è quella calibrata con fonti verificate nelle sessioni enrichment
   (le fonti VIVONO in prod: 3-8 sources per entità); il JSON era rimasto
   indietro. Fixa in automatico anche le 3 righe JSON che violavano
   ETHICS-013 (İstanbul #3, Cantona #642, Tlaxcallan #643: conf<0.5 con
   status confirmed).
3. **json_higher in `batch_32_confidence_boost.json`** e vincente nel
   last-wins (2: Крим #25, KKTC #39) → **JSON vince**: UPDATE su prod.
   Entrambe disputed con valori ≤0.70 (cap ETHICS-003 rispettato).
4. **json_higher residuo (87)** → **coda di review manuale**
   (`data/fixes/conf_review_queue.json`): nessuna scrittura automatica in
   NESSUNA direzione. Deviazione conservativa rispetto alla bozza iniziale
   (che prevedeva "prod vince" anche qui): abbassare il JSON senza review
   violerebbe il principio "mai abbassare silenziosamente"; il matching
   meccanico con le spec enrichment non ha trovato evidenza per nessuna
   riga (0 match), quindi TUTTE vanno a review con fonti alla mano, a lotti
   di ~10 nelle sessioni enrichment.
5. **Guardrail hard** (per riga, sullo stato risultante): rifiuto se
   `conf<0.5` con status `confirmed` (ETHICS-013) o `conf>0.70` con status
   `disputed` (ETHICS-003). Esito run 2026-07-03: 0 righe rifiutate.
6. **Fuori scope**: i 17 rename nativi prod-only (track M4 separato — il
   backport Wadai v6.99.110 è il pattern); le 61 entità JSON-only mai
   seedate (vietato `ingest_new_entities` su prod: creerebbe duplicati).

## Meccanica (vincoli tecnici)

- Molti file JSON non round-trippano (formato compatto / `\uXXXX`-escaped) →
  **chirurgia a stringa** sul solo record effettivo: span dei record via
  `raw_decode`, sostituzione del solo `confidence_score` a profondità 1
  (mai quelli annidati in territory_changes), valore atteso verificato
  prima della scrittura, verifica di rilettura dopo.
- SQL prod generato con lock ottimistico (`WHERE id=… AND
  confidence_score=<old>`) + guard finale in transazione.
- Verifica post-run: ricalcolo divergenze → residuo atteso = sola coda
  manuale (87).

## Conseguenze

- Fresh-seed e prod ora coerenti sulla confidence per 199/286 righe; le
  87 residue sono tracciate ed esauribili nelle sessioni enrichment.
- Il debito M4 residuo scende a: 17 rename nativi, 87 confidence in coda,
  30 record ombreggiati, 61 JSON-only.
