# AtlasPI Autonomous Loop — State Tracker

**Started**: 2026-05-21 20:14 CET (Clirim away ~3-4 days)
**End target**: 2026-05-25
**Mode**: ScheduleWakeup ~40 min, foreground iteration, GPT-5.5 dual-review enabled
**Owner**: claude (autonomous)

This file is the persistent memory bridge through context compactions.
At each iteration: (a) read this file first, (b) work, (c) update this file with progress.

## ✅ Settings (immutable for this run)

| Setting | Value |
|---|---|
| OpenAI model | `gpt-5.5` (reasoning_effort=low) |
| OpenAI key | `~/.openai-atlaspi-key` (chmod 600, out of repo) |
| Deploy frequency | max 12/day, healthcheck-required |
| Safety on deploy fail | auto-revert + skip iteration |
| Frontend changes | allowed (static/js/* + backend) |
| Backup DB | `/root/atlaspi-backup-pre-loop-20260521-201426.sql` (57 MB) on VPS |

## 🎯 Phase tracker

- [x] **Phase 0** — Setup (this file, chatgpt_review.py, gitignore, backup) — 2026-05-21 20:30
- [ ] **Phase A** — Boundary cleanup: find all `approximate_generated` entities, draw manual polygons
- [ ] **Phase B** — Enrichment S35+ (target 90% ≥3 src, 40% ≥5 src, 5000+ sources)
- [ ] **Phase C** — New entities (cities 110→250, events, routes)
- [ ] **Phase D** — Analytics-driven gap closure (top 404s, top low-result queries)
- [ ] **Phase E** — GPT-5.5 dual review batches (continuous)
- [ ] **Phase F** — Visual tour + URL polish (continuous)

## 📊 Baseline (before loop)

- Version: v6.99.28
- Total sources: 4017
- Entity con ≥3 sources: 852 (85%)
- Entity con ≥5 sources: 304 (30.4%)
- Entity con conf ≥0.85: 351
- Entity con `boundary_source = 'approximate_generated'`: **287 (27.6%)** — TARGET Phase A
- URL duplicati (non-vuoto): 0
- Total entities in DB: 1038
- Total cities: 110

### Phase A strategy

287 entità con boundary approssimato è troppo per disegno 100% manuale in 3-4 giorni.
Prioritizzo:
1. **Tier 1** (≤80 entities): n_sources ≥ 5 OR conf ≥ 0.70 — disegno polygon storico
2. **Tier 2** (~100 entities): n_sources 3-4 — uso boundary parent (es. dynastia precedente) se esiste, altrimenti polygon più approssimativo
3. **Tier 3** (~100 entities): n_sources ≤ 2 — lascio cerchio + nota ethical "boundary approximate by design, primary sources insufficient for accurate polygon"

## 📒 Iteration log

| # | Time (UTC) | Phase | Action | Result | Deploy? |
|---|---|---|---|---|---|
| 0 | 2026-05-21 18:30 | Setup | Configured loop infrastructure | OK | — |
| — | 2026-05-21 18:30 | Launch | Loop launched, ScheduleWakeup +1800s | scheduled | — |

(Append new rows on each iteration. Format: `| N | ts | phase | action | result | deploy/skip |`)

**IMPORTANT for resuming after PC restart**: if you (Claude) wake up and notice
this session was reopened after a Claude Code restart, re-issue ScheduleWakeup
immediately to resume the cadence, then proceed with Phase A iter 1.

## ⚠️ Errors / decisions / open questions

(Log here if something needs human attention when Clirim returns.)

- Nothing yet.

## 💰 Budget tracker

| Date | OpenAI tokens | Est. cost | Deploys | Sessions |
|---|---|---|---|---|
| 2026-05-21 | 0 | $0.00 | 0 | 0 |

## 🔧 Next iteration plan

**Iter 1 — Phase A tier-1 batch 1**:
1. SQL query for top-10 entities with `boundary_source='approximate_generated'`
   ordered by `(n_sources DESC, confidence_score DESC)`
2. For each: research historical territory via WebFetch or canonical knowledge
3. Patch `WRONG_POLYGON_FIXES` to add new entity IDs to `MANUALLY_CURATED_IDS`
4. Write SQL UPDATE with proper GeoJSON polygon + `boundary_source='historical_approximation'`
5. Run via SSH → docker cp → psql
6. (Optional) Send 1-2 random new boundaries to gpt-5.5 for fact-check
7. `bash scripts/safe_deploy.sh <iter_num>`
8. If safe_deploy returns 0: bump version, append iteration row to this file
9. If safe_deploy returns 1: log auto-revert in this file, continue next iteration
10. Schedule next iteration: `ScheduleWakeup(delaySeconds=1800, ...)` (30 min)

**Iteration cadence**: ~30 min between fires (cache miss but workable).
Each iteration aims to ship 1 batch of 10 entities (~50 sources + boundaries).

**End condition**: when LOOP_STATE.md shows Phase A complete + Phase B caught up,
or when Clirim writes a new message (he returns).
