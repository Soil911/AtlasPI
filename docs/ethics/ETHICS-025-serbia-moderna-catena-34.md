# ETHICS-025 — Serbia moderna: FR Jugoslavia + Serbia e Montenegro + Repubblica di Serbia (coda catena 34)

**Data**: 2026-07-05
**Versione**: v6.99.130
**Stato**: implementato
**Classe**: ETHICS-020 follow-up + ETHICS-003 (disputed/territorio contestato)
**Metodo**: workflow `task2-entity-research` (verdetti: FRY/S&M/RS con `fix`) +
cross-check ChatGPT gpt-5.5 (P1/P2/P3 **AGREE**). Provenance
`data/enrichment/task2_research_20260705.json`; log `data/chatgpt_review/20260705/`.
**Generatore**: `scripts/apply_task2c_serbia.py` → `scripts/sql_task2c_serbia.sql`.

---

## Il problema

La catena serba #34 terminava alla **SFRJ #231 (1945-1992)**; la storia jugoslava
post-1992 (dissoluzione, guerre, Kosovo, indipendenza montenegrina) non era rappresentata.
ETHICS-020 aveva flaggato "Serbia moderna" come follow-up.

## Decisioni adottate

### 3 entità NUOVE + coda catena 34 (seq 7..9)
- **`Савезна Република Југославија`** (FR Yugoslavia) 1992-2003, **Q838261**.
- **`Државна заједница Србија и Црна Гора`** (Serbia and Montenegro) 2003-2006, **Q37024**.
- **`Република Србија`** (Republic of Serbia) 2006-present, **Q403**.
- Catena: `… SFRJ → FRY (DISSOLUTION 1992) → S&M (REFORM 2003) → Republic of Serbia
  (SECESSION 2006)`. Confini APPROSSIMATIVI generati (nessun vicino da ereditare per
  gli stati moderni), `boundary_source=approximate_generated` (ETHICS-005).

### Correzione QID (verifier avversariale)
La ricerca aveva dato a FRY **Q37024**, che è invece *Serbia and Montenegro*
(2003-2006). Il verifier ha colto lo scambio → FRY corretto a **Q838261** (item
distinto: "Federal Republic of Yugoslavia", 1992-2003, replaced-by Q37024). Ripulite
due stringhe corrotte in una variante FRY ('Tr>eća'/'Републичка').

### ⚠️ Decisione ETHICS-003 chiave: Republic of Serbia = `confirmed`, NON `disputed`
La ricerca proponeva **status=disputed, conf 0.70** (cap ETHICS-003 per il Kosovo).
**Override** (cross-check ChatGPT P1 = AGREE): lo **Stato serbo** (membro ONU) non è
in dubbio → **status=confirmed, conf 0.9**; il cap `disputed`≤0.70 va **riservato al
TERRITORIO contestato** (il Kosovo), rappresentato come:
- un **territory_change 2008** (dichiarazione unilaterale d'indipendenza, SECESSION), e
- `ethical_notes` che registrano **entrambe le letture** (serba: Kosovo parte inalienabile,
  UDI illegittima; kosovara/parziale internazionale: stato de-facto, parere CIG 2010,
  ~110 riconoscimenti vs ~85 contati dalla Serbia) senza arbitrarle.
Marcare l'INTERO Stato serbo come disputed/0.70 avrebbe implicato falsa incertezza sulla
sua esistenza. La disputa è **localizzata**, non generalizzata.

### ETHICS-002: nominato il conflitto del Kosovo 1998-99
Le `ethical_notes` di Republic of Serbia ora **nominano per primo** il conflitto del
1998-99: le forze serbo-jugoslave dell'era Milošević condussero una **pulizia etnica**
(~850.000 albanesi kosovari espulsi, migliaia di uccisi) che innescò l'intervento NATO e
l'amministrazione ONU (UNMIK, Ris. 1244) — la disputa sullo status del 2008 non può
oscurare la storia dei perpetratori che la precede (cross-check ChatGPT P2 = AGREE).

## Rischi di distorsione mitigati

- **Falsa incertezza su uno Stato riconosciuto**: `disputed`/0.70 evitato per l'entità;
  la contestazione è localizzata al Kosovo (note + territory_change).
- **Eufemismo su una pulizia etnica**: nominata esplicitamente col perpetratore.
- **Versione unica su una disputa aperta**: entrambe le letture sul Kosovo, senza arbitrato.
- **QID errato che avrebbe collassato FRY e S&M**: corretto (Q838261 vs Q37024).

## Follow-up

Coda catena montenegrina (#130) verso la Montenegro indipendente (2006-) — non in questo
release.
