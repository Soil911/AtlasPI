# ETHICS-023 — Egitto/Nubia: Terzo Periodo Intermedio + Periodo Tardo come entità-fase + ripristino Meroe #552

**Data**: 2026-07-05
**Versione**: v6.99.128
**Stato**: implementato
**Classe**: ETHICS-015 (entità-fase) — follow-up diretto di ETHICS-022 (split Kemet)
**Metodo**: workflow di ricerca `task2-entity-research` (research + refuter avversariale;
verdetti `pass` per entrambe le entità egizie) + cross-check ChatGPT gpt-5.5 (AGREE
su tutte e 3 le decisioni, con raffinamenti applicati). Provenance in
`data/enrichment/task2_research_20260705.json`; log in `data/chatgpt_review/20260705/`.
**Generatore**: `scripts/apply_task2a_egypt.py` → `scripts/sql_task2a_egypt.sql` + dual-write.

---

## Il problema (follow-up ETHICS-022)

ETHICS-022 (split Kemet) creò l'ombrello `Kemet` #26 + le entità-fase dei tre
Regni (`tꜣ.wy (Old/Middle/New)`) e la catena 137 "Old → Middle → New", ma
**rinviò esplicitamente** come entità: il Terzo Periodo Intermedio, il Periodo
Tardo e il ripristino della fase meroitica (#552 Meroe, deprecata per errore nel
merge v6.85). ETHICS-022 argomentava che *le fasi di collasso non sono stati* e
non andavano modellate come entità. Questo record **raffina** quella posizione e
chiude i follow-up.

## Decisioni adottate

### 1. `tꜣ.wy (Third Intermediate Period)` — entità-fase di una fase FRAMMENTATA
- -1069..-664, Q212728, `entity_type=period`, **conf 0.62 (deliberatamente bassa)**.
- **Raffinamento di ETHICS-022**: modellare una fase *frammentata* come UNA entità
  è ammesso solo con tre garanzie che impediscono di affermare falsa statualità:
  (a) `ethical_notes` che dichiarano ESPLICITAMENTE la non-unità (21a din. tanita
  a nord vs Sommi Sacerdoti tebani; dinastie libiche 22a-24a; 25a din. kushita/
  nubiana); (b) confidence bassa (0.62); (c) transizione in catena tipizzata
  **DISSOLUTION**, non successione liscia. Cross-check ChatGPT: AGREE con queste
  condizioni.
- **Agentività nubiana (CLAUDE.md valore #4)**: le note dicono che la 25a dinastia
  kushita **ribaltò** la precedente dominazione egizia del Nuovo Regno sulla Nubia —
  non è un "invasione straniera" da eufemizzare.

### 2. `tꜣ.wy (Late Period)` — Saiti + conquiste persiane
- -664..-332, Q621917, `entity_type=period`, conf 0.82.
- Transizione in catena **RESTORATION** (riunificazione saitica), `is_violent=true`:
  seguì il sacco assiro di Tebe (**663 a.C.**, Assurbanipal — data corretta dal
  cross-check, non 664; consolidamento di Psamtik I entro ~656 a.C.). `ethical_notes`
  nominano le due conquiste achemenidi (Cambise -525, Artaserse III -343) e quella
  macedone (-332), senza eufemismi.

### 3. Ripristino Meroe #552 — correzione del mis-merge v6.85
- #552 era stata **deprecata nel merge v6.85** come presunto "duplicato" di Kush
  #52 (assunzione di QID Q241790 condiviso). È in realtà la **fase meroitica
  distinta** del Regno di Kush → **un-deprecated** (status `confirmed`, conf 0.60)
  e reintegrata nella catena nilotica #99 dopo Napata, transizione **REFORM**
  (spostamento del baricentro reale/sepolcrale verso Meroe entro ~-300; Meroe era
  già rilevante prima e Napata mantenne peso religioso — precisazione del cross-check).
- **`wikidata_qid` lasciato null**: Q241790 designa l'intero Regno di Kush (già
  su #52); Q3654 è la *città/sito* Meroë, non la fase-stato. Riusare uno dei due
  ricreerebbe il falso-duplicato o un mismatch → null è la scelta onesta
  (cross-check AGREE).
- Le `ethical_notes` di prod (che avevano annotazioni "DUPLICATE merged/deprecated"
  ora false) sono state **convergenti** al testo pulito del JSON + una nota di
  ripristino: JSON ≡ prod.

## Catene estese

- **137 (Regni faraonici)**: Old → Middle → New → **(Third Intermediate)** →
  **(Late Period)**. I collassi ora sono NODI espliciti (DISSOLUTION), non salti.
  (Il Regno tolemaico resta NON incatenato: stato macedone distinto — invariato da
  ETHICS-022.)
- **99 (Nilotica/Kush)**: Kerma → Kush → Napata → **Meroe**.

## Convenzioni

- **ETHICS-001**: `name_original` normalizzato allo schema dei fratelli `tꜣ.wy (X)`
  (lang `egy`); i nomi inglesi di periodizzazione ("Third Intermediate Period of
  Egypt", "Late Period of ancient Egypt") sono varianti, non primari.
- **ETHICS-005**: confini INHERITATI da vicini reali e documentato: TIP ← #1058
  (Nuovo Regno, Egitto+Nubia, coerente col dominio kushita), Periodo Tardo ← #1057
  (Medio Regno, core egizio, coerente con l'Egitto saitico). `boundary_source =
  historical_approximation`.

## Rischi di distorsione mitigati

- **Falsa statualità di una fase frammentata**: conf bassa + note di non-unità +
  DISSOLUTION.
- **Cancellazione inverso-coloniale**: agentività kushita (25a din.) nominata.
- **Errore di dato persistente**: il mis-merge v6.85 di Meroe è corretto, non
  lasciato come tombstone fuorviante.

## Follow-up

- Duplicato Ptolemaico #178 (in catena) vs #1059 (creato nel Kemet split, orfano,
  stesso Q2320005): dedup separato (deprecare #1059 + re-home fonti) — NON in questo
  release. Estensione catena 137 oltre il Periodo Tardo (→ Tolemaico) resta rinviata.
