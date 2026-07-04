# AtlasPI — Prompt per la prossima sessione (handoff 2026-07-04 sera, ultracode)

> Sessione 2026-07-04 completata: **11 release v6.99.118→126** — flag etici #240/#534
> (ETHICS-019), M1 entità-sblocco + catene (ETHICS-020), split Sri Lanka (ETHICS-021)
> e Kemet (ETHICS-022), M3 completo (EN machine-facing + on-this-day + freshness +
> pagina /why), M4 riconciliazione STRUTTURALE completa (JSON↔prod name-reconciled
> 100%) + 15 confidence review. Poi i **3 canali distribuzione ATTIVATI** (npm
> atlaspi-client 0.3.0, Bing Webmaster, HuggingFace dataset). **Linea "prodotto
> finito" ≈ 86%** (vedi memoria project_completion_baseline).

---

Riprendi AtlasPI in autonomia, in ultracode. Leggi le memorie (MEMORY.md; in
particolare project_completion_baseline, project_reconciliation_debt,
project_chain_linkage, project_enrichment_workflow) + CHANGELOG.md + ROADMAP.md.
Non fermarti tra un task e l'altro. Per OGNI task: dual-write JSON+prod, suite verde
(1293), CI verde, **backup pg_dump PRIMA di ogni SQL prod**, deploy con
`cra-deploy.sh atlaspi` + verifica /health, aggiorna CHANGELOG+ROADMAP+memoria + la
LINEA in project_completion_baseline. Per scelte etiche non banali: cross-check
ChatGPT (scripts.chatgpt_review.ask) + record in docs/ethics/.

STATO: prod v6.99.126 live su https://atlaspi.it, CI+suite verdi, 1006 entità vive
(1053 totali coi tombstone), 104 catene, 5004 fonti, integrità etica pulita.
M1/M2/M3 chiusi; M4 strutturale completa; 3 canali distribuzione attivi. Linea ≈86%.
Il resto è quasi tutto enrichment asintotico.

## ORDINE DEI TASK

1. **Coda confidence review** — 72 in `data/fixes/conf_review_queue.json` (ADR-011,
   l'unico pezzo "finibile", ~1pt → linea ~87%). Per lo più ricostruzioni archeologiche
   meso/pre-colombiane. ULTRACODE: workflow che, a lotti, fa fan-out di 1 agente-verifica
   per entità (legge le sue fonti su prod + WebSearch) che decide: (a) alzare prod al
   valore JSON se fonti + certezza di datazione lo giustificano, oppure (b) backport
   JSON→prod (abbassare il JSON) se la datazione è troppo incerta per il valore alto
   (ETHICS-013: confidence onesta). Dual-write. Chiudi la coda.

2. **Follow-up entità** da ETHICS-019/020/022: Repubblica Khmer 1970-75 (verifica se
   creata), PRK/Stato di Cambogia 1979-93 → estendi in avanti catena 126; Eritrea
   italiana → catena Medri Bahri #658; Serbia moderna 1992-/2006- → coda catena 34;
   Terzo Periodo Intermedio / Periodo Tardo egizio → estendi catena dei Regni;
   ripristino #552 Meroe (deprecata nel merge v6.85 ma è entità-fase → catena #99).
   Ricerca verificata + dual-write.

3. **Enrichment copertura** — ~200 entità <0.6 + gap geografici/temporali (collo di
   bottiglia asintotico). Workflow turnkey in project_enrichment_workflow. Valore
   marginale calante: lotti finché ha senso.

## VINCOLI OPERATIVI CRITICI

- Entità NUOVE via INSERT SQL transazionale (come `scripts/apply_m1_unlock.py`,
  `scripts/sql_babylon_split.sql`), **MAI `ingest_new_entities` su prod** (anche se i
  nomi ora combaciano, vuoi controllare gli id). Backup prima.
- ⚠️ **VINCOLO ID-ORDER DEL SEED** (scoperto v6.99.125): il seed deduplica per nome con
  semantica FIRST-POSITION + LAST-DATA. Rimuovere una PRIMA occorrenza di un nome shifta
  gli id auto-increment del fresh-seed e rompe `tests/test_v673_boundary_cleanup`. Per
  dedup/rimozioni: rimuovi SOLO occorrenze successive + merge dati nel record in prima
  posizione (`scripts/apply_shadow_dedup_v2.py`). Cambiare CONFIDENCE non shifta gli id.
- Molti JSON NON round-trippano (compatti/`\uXXXX`) → chirurgia a stringa byte-preserving;
  il match su nomi nativi con zero-width space è fragile → per le UPDATE prod usa la PK
  id, non `name_original`.
- `dangerouslyDisableSandbox` / Edit-Write per persistere (bash sandbox reverta i file
  git-tracked); console cp1252 → `PYTHONUTF8=1`.
- Fence CI da tenere verdi: `test_chain_dedup_json_audit`, `test_chain_deprecated_json_audit`,
  `test_deprecated_exclusion`, `test_database`, `test_v673_boundary_cleanup`,
  `test_confidence_status_coherence`.
- Il 301 dal vecchio dominio e la SAN `app.cra-srl.com` nel cert NON vanno mai rimossi.
- SSH prod: `ssh -i ~/.ssh/cra_vps root@77.81.229.242 "docker exec -i cra-atlaspi-db psql
  -U atlaspi -d atlaspi -v ON_ERROR_STOP=1" < file.sql`. Export prod: `psql -F'~'` (NON
  `-F'\t'`, che SSH passa letterale) verso path assoluto nella scratchpad.

## BLOCCATI (login umano)
Niente rimasto — i 3 canali (npm/Bing/HF) sono fatti. Se il dataset HF va rigenerato
dopo enrichment: `python hf-dataset/prepare_export.py` (già rate-limit-safe), poi
l'upload lo fa Clirim.

Aggiorna la LINEA in project_completion_baseline a fine sessione.
