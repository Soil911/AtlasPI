# ETHICS-026 — Eritrea: Colonia Eritrea + catena COLONIAL Medri Bahri → Eritrea italiana

**Data**: 2026-07-05
**Versione**: v6.99.131
**Stato**: implementato
**Classe**: ETHICS-020 follow-up + ETHICS-002 (oppressione coloniale dato di prima classe)
**Metodo**: workflow `task2-entity-research` (verdetto `fix`: 1 errore fattuale + 2
precisazioni di fonte). Provenance `data/enrichment/task2_research_20260705.json`.
**Generatore**: `scripts/apply_task2d_eritrea.py` → `scripts/sql_task2d_eritrea.sql`.

---

## Il problema

**Medri Bahri #658** (regno altopiano eritreo, 1137-1879) esisteva ma **non era in
nessuna catena**; l'**Eritrea italiana** mancava. ETHICS-020 aveva flaggato "Eritrea
italiana" come follow-up.

## Decisioni adottate

### 1 entità NUOVA + 1 catena NUOVA (COLONIAL)
- **`Colonia Eritrea`** (it) 1890-1941, **Q1232988**, `entity_type=colony`, conf 0.9,
  capitale Asmara. Confine INHERITATO da #658 (altopiano eritreo, ETHICS-005).
- Catena **`Eritrean state trunk: ምድረ ባሕሪ → Colonia Eritrea`**, `chain_type=COLONIAL`,
  2 link: Medri Bahri #658 → Colonia Eritrea (**CONQUEST** 1890, is_violent=true).

### Correzione fattuale (verifier avversariale)
La ricerca affermava "matrimoni misti banditi nel 1933" — **inesatto**: la legge del
1933 regolava lo **status giuridico dei figli meticci**; il divieto delle unioni
(*madamato*) è del **1937** (pene 1-5 anni) e la segregazione piena del 1939. Corretto.

### Catena deliberatamente CORTA (ETHICS-017) — non finisce al colonizzatore
Due sole entità (regno indigeno → colonia). Per **non far finire la storia eritrea alla
colonizzazione** (rischio simmetrico all'"ending at the genocide regime" di ETHICS-017),
le `ethical_notes` della catena documentano ESPLICITAMENTE l'arco successivo:
Amministrazione militare britannica (1941-52), federazione imposta dall'ONU poi
annessione da parte dell'Etiopia (1952/1962), **guerra d'indipendenza trentennale
(1961-1991, EPLF)** e indipendenza per referendum nel **1993**. Lo **Stato di Eritrea
(1993-)** e l'interregno britannico/etiope non sono ancora entità (estensione in coda).

### ETHICS-002 (COLONIAL = oppressione di prima classe)
Le note nominano il perpetratore (Regno d'Italia, poi Stato fascista), la Colonia come
**trampolino per l'invasione dell'Etiopia 1935-36**, le leggi razziali (scuole separate
1909, segregazione urbana Asmara 1916, madamato criminalizzato 1937), i ~75.000 coloni
italiani (1939) e gli ascari eritrei coscritti nelle campagne di conquista. Il nome
latino "Eritrea" (dal greco Mar Rosso) che soppiantò le designazioni indigene è
esplicitato; Medri Bahri è predecessore, non cancellato.

## Rischi di distorsione mitigati

- **Fine della storia alla colonizzazione**: arco post-1941 fino all'indipendenza 1993
  documentato nelle note (catena corta + note, ETHICS-017).
- **Eufemismo coloniale**: perpetratore e leggi razziali nominati, con date.
- **Errore fattuale (1933 vs 1937)**: corretto dal verifier.

## Follow-up

Stato di Eritrea (1993-, Q986) + interregno (Amministrazione britannica, federazione/
annessione etiope) come entità, per estendere la catena fino all'indipendenza.
