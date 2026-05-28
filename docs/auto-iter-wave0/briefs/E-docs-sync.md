# Wave 0 / E — Docs sync

Date: 2026-05-28
Agent: Wave 0 E (general-purpose, background, read-only)
Duration: ~2.2 min
Status: completed

---

## ROADMAP status

- **Versione corrente dichiarata in ROADMAP "Versioni completate"**: `v6.99.80` Phase H (entry presente, 2026-05-28)
- **Però** la sezione "Roadmap attiva — Prossime release" cita ancora `v7.1` come TOP PRIORITY post-benchmark v7.0, e poi liste `v6.23`/`v6.24`/`v6.25`/`v6.26` come "prossimo" — **palese sovrapposizione semantica**: la storia di v6.99.x è andata oltre v7.0 in numerazione ma il ROADMAP tratta v6.23-v6.26 come "prossime" mentre sono in realtà skipped/incorporate in v6.99.x.
- **Versione corrente nei commit**: `v6.99.80` (ffc7b8c)
- **Tag git ultimo**: `v6.92.0` — **disallineato**: nessun tag annotato per v6.93–v6.99.80 (perso 8+ versioni di tag rispetto al CHANGELOG)
- **Tabella metriche v7.0** (riga 477-496): aggiornata parzialmente al v6.99.80 (entities 1038, boundary 99.9%), ma dice ancora "Stato attuale (2026-04-16, v6.22.0)" nell'header — data stale.
- **Milestone "in corso" dichiarata**: v6.22 — **realtà**: v6.99.80, fuori scala di ~77 minor release. Tutto il blocco "v6.23-v6.26 prossime" è effettivamente storia.

## CHANGELOG status

- **Ultima entry**: `[v6.99.80] - 2026-05-28` (Phase H) — coincide con HEAD
- **Pattern versioning**: `v6.99.NN` patch incrementale (NN=29→80 in ~2 settimane via autonomous loop). ROADMAP usa pattern v6.X.Y/v7.X minore. **Disallineamento di schema**.
- **Commit post-v6.99.80 in CHANGELOG senza propria entry sub-versionata**: 6 commit (post-H wave 2/3/4, capital coverage, ETHICS-007 links, rectangle placeholders, FINAL_SUMMARY). Sono tutti sotto-iterazioni del v6.99.80, quindi tecnicamente coperti dall'entry stessa, ma il dettaglio (es. "+59 rectangle placeholders rimossi", "+23 capitals", "11 events linked ETHICS-007") non è riflesso nella entry CHANGELOG → opaco per consumer esterno.

## ETHICS records

| ID | File | Note |
|----|------|------|
| ETHICS-001 | nomi-contestati.md + .en.md | OK |
| ETHICS-002 | confini-e-conquiste.md + .en.md | OK |
| ETHICS-003 | territori-contestati-attuali.md + .en.md | OK |
| ETHICS-004 | confini-generati-approssimativi.md + .en.md | OK |
| ETHICS-005 | boundary-natural-earth.md + .en.md | OK |
| ETHICS-006 | natural-earth-fuzzy-displacement.md | OK (no .en) |
| ETHICS-007 | eventi-storici.md | OK |
| ETHICS-008 | silenzi-e-cancellazioni.md | OK |
| ETHICS-009 | categorie-politiche-colon-imposte | OK |
| ETHICS-010 | wikidata-cross-reference.md | OK (ROADMAP riga 528 lo cita come "Tratta esseri umani") — **MISMATCH semantico**: file dice Wikidata, ROADMAP dice trafficking |
| ETHICS-011 | redesign-aplus-typography-and-color.md | OK |
| ETHICS-012 | phase-h-boundary-review.md | OK (nuovo v6.99.80) |

**Grep `# ETHICS:` in src/**: 22 ref. Tutti puntano a ETHICS-001/002/003/006/007 — **ETHICS-008/009/010/011/012 non hanno alcun riferimento in codice**. Decisioni recenti che parlano di Pechenegs capitals, rectangle placeholders, 11 events linking sono cambiamenti dati senza # ETHICS marker nel codice (ma giustamente loggate in CHANGELOG/SQL files).

**Decisioni etiche recenti SENZA record**: nessuna evidenza di gap maggiore — i 6 commit post-v6.99.80 sono coperti da ETHICS-012 (Phase H) e ETHICS-007 (events).

## ADR

`docs/adr/` esiste, **10 record** (ADR-001 → ADR-010). Più recenti: ADR-009 (v6.94.0 PostGIS geometry), ADR-010 (v6.98.0 polymorphic sources). **Phase G (Feedback, Reputation, Citation tracking, SVG badge, Agent Telemetry) v6.99.75-79 NON ha ADR** — questi sono cambiamenti architetturali significativi (nuove tabelle, write APIs MCP) senza decision record.

## docs/ structure audit

- **Atteso (CLAUDE.md)**: `docs/`, `docs/ethics/`, `docs/adr/`, `docs/TEMPLATES.md` — **tutti presenti**.
- **Extra**: `docs/audit/` (3 file FASE_A_B_HANDOFF, FASE_C_CHIUSURA), `docs/boundary-review-v6.99.79/` (40+ SQL/screenshot files), `docs/auto-iter-wave0/` (1 screenshot frontend), `docs/auto-iteration-log.md`.
- **Orfani candidati**: `screenshot.png` 702KB in docs/ root (Apr 14), `paper-draft.md`, `outreach-draft.md`, `reddit-drafts.md`, `github-release-v6.33.md` (stale, v6.33 vs v6.99.80), `boundary_audit_2026_04_15.md`, `boundary_coverage_report.md` (Apr 14, pre Phase H).

## Top 10 azioni di sync prioritizzate

1. Tag git annotato `v6.99.80` + backfill tag per v6.93–v6.99.79 (recuperare visibility release history)
2. Riscrivere blocco "Roadmap attiva" ROADMAP: rimuovere v6.23-v6.26 (assorbite), confermare v7.1/v7.2, aggiungere v7.0 alle "completate" con benchmark closure
3. Aggiornare header tabella metriche ROADMAP: "Stato attuale (2026-05-28, v6.99.80)" non più v6.22.0
4. Correggere mismatch ETHICS-010: ROADMAP riga 528 dice "Tratta esseri umani", file dice "wikidata-cross-reference" → decidere quale è canonico, ribattezzare l'altro
5. CHANGELOG: aggiungere sezione "v6.99.80 post-H follow-ups" che elenca i 6 commit (rectangle placeholders, capital coverage, events linking) per trasparenza
6. Creare ADR mancanti per Phase G (Feedback layer, Reputation, Citation tracking, Agent Telemetry, SVG badge) — almeno 2 ADR consolidati
7. Archiviare `docs/screenshot.png`, `github-release-v6.33.md`, `paper-draft.md` in `docs/archive/` o cancellare se obsoleti
8. Aggiungere `# ETHICS: ETHICS-NNN` marker in codice per i record 008/009/010/011/012 (zero ref attualmente)
9. ROADMAP: aggiornare "Versione corrente" testuale (riga 343 ancora dice "Versione corrente. v6.22")
10. Sincronizzare `docs/auto-iteration-log.md` con stato Wave 0 finale (al momento solo "launched" per i 5 agenti) — popolare risultati una volta concluso
