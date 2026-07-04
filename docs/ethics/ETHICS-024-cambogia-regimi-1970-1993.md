# ETHICS-024 — Cambogia: PRK + Stato di Cambogia + estensione avanti della catena 126 (regimi 1970-1993)

**Data**: 2026-07-05
**Versione**: v6.99.129
**Stato**: implementato
**Classe**: ETHICS-020 follow-up (entità-sblocco) + ETHICS-017 (modello linea+note)
**Metodo**: workflow di ricerca `task2-entity-research` (verdetti `pass` su entrambe)
+ cross-check ChatGPT gpt-5.5 (P1 DISAGREE→split rinviato, P2 AGREE). Provenance in
`data/enrichment/task2_research_20260705.json`; log `data/chatgpt_review/20260705/`.
**Generatore**: `scripts/apply_task2b_cambodia.py` → `scripts/sql_task2b_cambodia.sql`.

---

## Il problema

ETHICS-020 aveva flaggato come follow-up la creazione della **PRK 1979-89** per
estendere in avanti la catena 126. La catena terminava a **Kingdom of Cambodia #256
(1953-present)**, con i regimi 1970-1993 solo *accennati* nelle note come "sconvolgimenti
interni alla span di #256". Due entità di quella sequenza esistevano già (Repubblica
Khmer #1044, Kampuchea Democratica #240, da v6.99.118/120) ma **non erano incatenate**;
PRK e Stato di Cambogia **mancavano**.

## Decisioni adottate

### 2 entità NUOVE (INSERT SQL transazionale + dual-write JSON)
- **`សាធារណរដ្ឋប្រជាមានិតកម្ពុជា`** (People's Republic of Kampuchea) 1979-1989,
  **Q867778** (corretto dal verifier: la ricerca aveva proposto Q853993; Q867778 è
  l'item PRK con label/inception corretti), conf 0.9, capitale Phnom Penh.
- **`រដ្ឋកម្ពុជា`** (State of Cambodia) 1989-1993, **Q2387250**, conf 0.9.
- Confini INHERITATI da #256 (Cambogia moderna, ETHICS-005).

### Catena 126 estesa avanti (seq 4..7)
`… → Kingdom of Cambodia #256 → Repubblica Khmer → Kampuchea Democratica → PRK →
Stato di Cambogia`. Tipi di transizione (tutti valori enum):
- **1970 REVOLUTION** (is_violent=false): il **colpo di stato di Lon Nol / Sirik
  Matak** (18 marzo 1970) depose Sihanouk e abolì la monarchia; incruento in sé ma
  trascinò la Cambogia nella guerra del Vietnam e innescò la guerra civile 1970-75.
- **1975 CONQUEST** (is_violent=true): i **Khmer rossi** (Pol Pot) presero Phnom
  Penh il 17 aprile 1975 → **genocidio cambogiano** (~1,5-2 milioni di morti).
- **1979 CONQUEST** (is_violent=true): l'**invasione vietnamita** (dic. 1978-gen.
  1979) rovesciò i Khmer rossi e installò la PRK. **Entrambe le letture registrate
  senza arbitrarle** (ETHICS-002 / no-single-version): l'invasione **pose fine al
  genocidio** ED era un'**occupazione militare** vietnamita con stato-cliente (truppe
  fino a sett. 1989); la Kampuchea Democratica deposta mantenne il seggio ONU col
  sostegno di Cina, USA e ASEAN. Cross-check: CONQUEST è onesto se definito
  meccanicamente come rovesciamento/occupazione militare esterna, con le note esplicite.
- **1989 REFORM** (is_violent=false): ridenominazione costituzionale PRK → Stato di
  Cambogia + riforme di mercato; fine con gli Accordi di Parigi 1991, UNTAC, restauro
  monarchico 1993.

### Ciclo del 1993 (restauro monarchico): linea + note, NON back-link
Il restauro del 1993 riporta il governo al **Kingdom of Cambodia #256** (da cui la
catena parte al 1970). L'interruzione 1970-1993 e il restauro sono **documentati** sul
link Stato-di-Cambogia e nella nota chain-level, **non** come back-link letterale
(convenzione linea-principale + note, ETHICS-017; il modello chain è lineare).

### Split di #256 CONSIDERATO ma RINVIATO (trasparenza sul cross-check)
Il cross-check ChatGPT **preferiva splittare #256** in *Kingdom of Cambodia (1953-70)*
+ *(1993-present)*, perché "1953-present" come *forma-di-stato monarchica* nasconde
l'abolizione 1970-1993. **Rinviato** come operazione separata (classe ETHICS-015):
re **Norodom Sihanouk regnò in ENTRAMBI i periodi** (1953-70 e come re restaurato
1993-2004) → il re-home di rulers/eventi è non banale e richiede una sessione dedicata.
L'interruzione è resa **esplicita** nelle note come mitigazione. Questa deviazione dal
cross-check è documentata qui (governance etica: non procedere in silenzio).

## Rischi di distorsione mitigati

- **Continuità falsa**: i quattro regimi 1970-1993 ora sono NODI espliciti con tipi di
  transizione onesti (COUP→REVOLUTION, CONQUEST, CONQUEST, REFORM), non una span liscia.
- **Sanitizzazione del genocidio**: perpetratore nominato (Khmer rossi/Pol Pot),
  cifre (~1,5-2M) sul link 1975.
- **Versione unica su una controversia geopolitica**: l'intervento vietnamita del 1979
  è reso in entrambe le letture (fine-del-genocidio / occupazione), non arbitrato.

## Follow-up

Split di #256 (1953-70 / 1993-) con re-home di Sihanouk — sessione dedicata (ETHICS-015).
