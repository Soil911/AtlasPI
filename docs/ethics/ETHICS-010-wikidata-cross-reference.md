# ETHICS-010 — Wikidata come cross-reference, non come autorità

**Data**: 2026-04-18 (v6.69 audit v4 Fase A)
**Scope**: uso del campo `geo_entities.wikidata_qid` e dello script di drift detection (Fase B) per confrontare AtlasPI con Wikidata.

---

## Contesto

Audit v2 (20 entità auditate manualmente contro fonti accademiche, agosto 2025)
ha rilevato ~45% error rate su metriche MED+HIGH. Audit manuale non scala a 1034 entità. Abbiamo bisogno di uno **strumento di drift detection sistematico** che segnali discrepanze a basso costo.

La soluzione v6.69: cross-reference automatico con Wikidata.

Ma Wikidata **NON è neutrale**:
- **Bias occidentale sui nomi**: il label "English" è spesso privilegiato; nomi di regni pre-coloniali sono frequentemente in forma inglese o colonizzatrice
- **Convention BCE/CE differenti**: Wikidata usa astronomical year numbering (anno 0 esiste), mentre AtlasPI usa convention storica (1 BCE = anno precedente 1 CE)
- **Fondazione/dissoluzione dispute**: Roman Empire inception è vista variamente come -27 (Ottaviano), -31 (Actium), -44 (Cesare), -509 (fine Monarchia), 1 (fine Trionvirato) — Wikidata arbitrariamente adotta UNA versione
- **Category schema occidentale**: P31 `instance_of` ha Q48349 (empire) come categoria top; polity non-occidentali (es. Inca Tawantinsuyu) sono istanze di Q3024240 (entità statale storica, molto generico) perché il concetto europeo di "impero" non calza
- **Struttura disuguale**: entità famose (Roma, Cina) hanno P36, P625, P571, P576 coerenti; entità meno famose hanno solo alcune, o nessuna

## Decisione

### 1. Wikidata Q-ID è solo un identificatore di riferimento

Il campo `geo_entities.wikidata_qid` è un **cross-reference per drift detection**. NON è:
- Una fonte autoritativa
- Un campo da copiare automaticamente
- Un override di dati AtlasPI

### 2. Nessun autofix sulle date

Le discrepanze `year_start` / `year_end` tra AtlasPI e Wikidata sono **sempre** flaggate per review manuale, mai autofixate. Se Wikidata dice Roman Empire inception=709 BCE (ab urbe condita) e AtlasPI dice -27 (Ottaviano Augustus), entrambi possono essere difendibili con fonti — non è una scelta algoritmica.

### 3. Autofix limitato a typo meccanici

L'unico autofix accettato in Fase B è la correzione di **typo evidenti** nelle coordinate:
- swap lat ↔ lon (comune errore di data entry)
- sign flip (errore di casella positive/negative)

Condizione: `km_diff > 1000km` E il flip produce `< 20km` diff con Wikidata. Una discrepanza di 50km può essere una scelta legittima (es. capitale antica in posizione diversa da quella moderna), non un typo.

### 4. Trasparenza nel bootstrap

Lo script `scripts/wikidata_bootstrap.py`:
- Salva il match con score e `match_reasons` (esatti, non opachi)
- Flagga per review manuale ogni match con `score < 0.85`
- Mantiene tutti gli alternativi nei risultati JSON (non solo il top)
- Penalizza ambiguità: se 2 candidati hanno score simile (es. Roman Empire vs Roman Republic), lo score viene ridotto

### 5. Continued sovereignty di AtlasPI

Dopo la Fase A/B, le discrepanze diventano **opportunità di verifica**, non di correzione cieca:
1. Il drift check produce un report `fase_b_drift_report.md`
2. Ogni HIGH discrepancy diventa un record in Fase C per analisi umana
3. AtlasPI può adottare la posizione Wikidata SOLO se le fonti primarie lo supportano — altrimenti lo status rimane con `ethical_notes` che spiega la divergenza

## Esempi pratici

### Esempio 1 — Cahokia

Ipotesi: AtlasPI dice Cahokia year_start=600, Wikidata dice 1050.

- **Non autofix**: archeologia ha intervalli di datazione diversi a seconda della scuola
- **Flag HIGH**: delta > 50y
- **Review umana**: se la fonte AtlasPI è archeologicamente solida (es. Pauketat 2004), manteniamo 600 + aggiungiamo `ethical_notes: "Wikidata usa 1050 (Mississippian period tardi); AtlasPI usa 600 per includere Mound Builders earlier phase."`

### Esempio 2 — Nome capitale

Ipotesi: AtlasPI dice capital="Cusco", Wikidata dice P36→"Cuzco".

- **Non autofix**: trascrizione quechua letterale "Qusqu" vs spelling colonialism "Cuzco" vs spelling post-coloniale "Cusco"
- **Flag MED**: labels non matchano esattamente
- **Review umana**: adottiamo "Qosqo" o "Qusqu" (ETHICS-001 dice name_original in lingua locale)

### Esempio 3 — Coordinate typo

Ipotesi: AtlasPI dice capital_lat=12.5, capital_lon=41.9 per Roma (lat/lon swapped).

- **Autofix**: km_diff da Wikidata (41.9, 12.5) è ~3300km; swap riduce a <1km
- **Applica**: `capital_lat=41.9028, capital_lon=12.4964`
- **Audit log**: "v6.70 audit_v4 Fase B: coord typo lat↔lon swap detected, Wikidata Q2277 confirms"

## Implementazione

- Migration: `alembic/versions/015_wikidata_qid.py`
- Script: `scripts/wikidata_bootstrap.py` (Fase A), `scripts/wikidata_drift_check.py` (Fase B)
- Report: `docs/audit/fase_a_report.md` (Fase A), `docs/audit/fase_b_drift_report.md` (Fase B)
- API: campo `wikidata_qid` nel `EntityResponse`
- Patch pipeline: `scripts/apply_data_patch.py` accetta `wikidata_qid` in whitelist

## Riferimenti

- CLAUDE.md §2 "Nessuna versione unica della storia"
- CLAUDE.md §3 "Trasparenza dell'incertezza"
- ETHICS-001 (nomi in lingua locale come primari)
- ETHICS-009 (categorie politiche imposte)
- [Wikidata Terms of Use](https://meta.wikimedia.org/wiki/Terms_of_use) — CC0 per i dati, attribuzione consigliata ma non obbligatoria
