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
- Entity con `boundary_source = 'approximate_generated'`: TBD (Phase A first query)
- URL duplicati (non-vuoto): 0
- Total entities in DB: 1037
- Total cities: 110

## 📒 Iteration log

| # | Time (UTC) | Phase | Action | Result | Deploy? |
|---|---|---|---|---|---|
| 0 | 2026-05-21 18:30 | Setup | Configured loop infrastructure | OK | — |

(Append new rows on each iteration. Format: `| N | ts | phase | action | result | deploy/skip |`)

## ⚠️ Errors / decisions / open questions

(Log here if something needs human attention when Clirim returns.)

- Nothing yet.

## 💰 Budget tracker

| Date | OpenAI tokens | Est. cost | Deploys | Sessions |
|---|---|---|---|---|
| 2026-05-21 | 0 | $0.00 | 0 | 0 |

## 🔧 Next iteration plan

Phase A: query DB for all entities with `boundary_source = 'approximate_generated'`, group by entity_type and historical era, prioritize the most "famous" first (= those with highest n_sources, as they have the most user interest). Draw manual polygons in batches of 10.
