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
| 1 | 2026-05-21 18:55 | A | 10 boundaries Tier-1 batch 1 + GPT-5.5 fact-check Balhae | v6.99.29 deployed, 20 curated/277 approximate | ✓ |
| ⚠️ | 2026-05-21 19:00 → 2026-05-22 13:54 | — | **GAP ~19h**: Claude Code restart (PC update v1.8555.0) → scheduled wakeup lost | manual resume by Clirim | — |
| 2 | 2026-05-22 14:00 | A | 10 boundaries Tier-1 batch 2 (Kilwa, Ajuran, Mvskoke, Oirats, Crusader Tripoli, Kamarupa, Khotan, Karakhanid, Dutch Brazil, Tekrur) | v6.99.30 deployed, 30 curated/267 approximate | ✓ |
| 3 | 2026-05-22 14:40 | A | 10 boundaries Tier-1 batch 3 (Lithuania GD, Choctaw, Daura, Mrauk-U, Gobir, Bono-Manso, Mandan, Hessen, Brandenburg, Marovo) | v6.99.31 deployed, 40 curated/257 approximate | ✓ |
| 4 | 2026-05-22 15:00 | A | 10 boundaries (Apalachee, Etalwa, Shawnee, Amu, Tokelau, Haudenosaunee proto, Cirebon, Roviana, Sachapuyas, Milagro-Quevedo) | v6.99.32, 50/237 | ✓ |
| 5 | 2026-05-22 15:15 | A | 10 boundaries (Kurland, Tlaxcallan, Niue, Moundville, Hidatsa, Madja-as, Cotabato, Gelgel, Kong, Begho) | v6.99.33, 60/227 | ✓ |
| 6 | 2026-05-22 15:25 | A | 10 boundaries (Mafia, Balanguingui, Namayan, Tumbatu, Brabant, Engaruka, Chwaka, Savoy, Butaritari, Three Fires) | v6.99.34, 70/217 | ✓ |
| 7 | 2026-05-22 15:35 | A | 10 boundaries (Denmark, Flanders, Pomerania, Saxony Duchy, Meissen, Wallachia, Mvita, Pemba, Sofala, Vumba Kuu) | v6.99.35, 80/207 | ✓ |
| 8 | 2026-05-22 15:45 | A | 10 boundaries (Liao, Assyria, Pagan, Funan, Sparta, Calakmul, Zeila, Muzo, Beikthano, Kintamani) | v6.99.36, 90/197 | ✓ |
| 9 | 2026-05-22 15:50 | A | 10 boundaries (Bulgaria I, Kassite, Maya cities, Garamantes, Dʿmt, Dedan) | v6.99.37, **100/187 MILESTONE** | ✓ |
| 10 | 2026-05-22 15:55 | A | 10 boundaries (Istanbul, Bavaria, Maʿīn, Gerrha, Mitla, Cantona, Nuuchahnulth, Salakanagara, Teuchitlán, Manda) | v6.99.38, 110/177 | ✓ |
| 11 | 2026-05-22 16:00 | A | 10 boundaries (Koumbi Saleh, Palenque, Lucayan, Tayma, Tres Zapotes, Edessa, Marajoara, Paracas, Qedar, Tongva) | v6.99.39, 120/167 | ✓ |
| 12 | 2026-05-22 16:05 | A | 10 boundaries (Marshalls, Isin, Yamhad, Copan, Yaxchilan, Huexotzinco, Halin, Maghreb emirates Rustamid/Midrarid/Hammadid) | v6.99.40, 130/157 | ✓ |
| 13 | 2026-05-22 16:10 | A | 10 boundaries (Polotsk, Wiradjuri, Noongar, Shewa, Cocle, Quirigua, Wadan, Oualata, Chamorro, Wallis) | v6.99.41, 140/147 | ✓ |
| 14 | 2026-05-22 16:15 | A | 10 boundaries **50% MILESTONE** (USSR, Aboriginal Aus nations, Marshall Is., Punt, Tunjur, Pulotu, Chiripa, Futuna, Kulin, Yolŋu) | v6.99.42, **150/137** | ✓ |
| 15 | 2026-05-22 16:20 | A | 10 boundaries (Chamorro, Ugarit, Xochicalco, El Tajin, Aguateca, Spiro, Kuna, Shilluk, Kuba, Shanga) | v6.99.43, 160/127 | ✓ |
| 16 | 2026-05-22 16:25 | A | 10 boundaries (Scythia, Epirus, Corinth, Catalhoyuk, Dilmun, Navajo, K'iche', Tsalagi, Uxmal, Nojpeten) | v6.99.44, **170/117 (59%)** | ✓ |

### 🎉 SESSION SUMMARY (turno 2026-05-22 14:00 → 16:25, 16 iter consecutive)

**Phase A progress**: 20/287 → 170/287 (7% → 59%) = **+150 boundaries curate in un turno**
**Deploys**: v6.99.29 → v6.99.44 (16 sub-versioni)
**Tutti i deploy passati healthcheck — zero auto-revert**
**Schema versioning corretto, MANUALLY_CURATED_IDS guard rispettato a ogni restart**

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
| 2026-05-21 | ~700 (Balhae fact-check) | $0.005 | 1 (v6.99.29) | iter 1 |

## 🔧 Next iteration plan

**Iter 2 — Phase A tier-1 batch 2**:
Same workflow as iter 1, but skip already-curated IDs.
Query: `SELECT id, name_original, entity_type, year_start, year_end, capital_name,
confidence_score, (SELECT count(*) FROM sources s WHERE s.entity_id=g.id) AS n_src
FROM geo_entities g WHERE boundary_source = 'approximate_generated'
ORDER BY n_src DESC, confidence_score DESC LIMIT 15`.

Next 10 candidates expected: Vumba Kuu (1017), Tu'i Tonga (44),
Cumans (already curated), Maui (749), Roviana (755), Marovo (756), Mvskoke (219),
Mojinda Mxikodewinan (778), Chahta Yakni (782), Shawanwaki (780),
Mottama (904), Kintamani (891), Phayao (889), Pate (825), Malindi (823),
Sugbu (366), Cebu, Bono-Manso (1014), Damot (832), Chanka (952), etc.

(Note: many of these already have manual boundaries from S29-S33;
double-check before re-curating. Some entries may have been left as
`approximate_generated` intentionally because city-state polygons are
inherently uncertain — use Tier 3 strategy for them.)

**Iteration cadence**: ~30 min between fires.
**Target per iter**: 10 boundaries + 1-2 GPT-5.5 fact-checks + 1 deploy.

**End condition**: when ≥150 entity in 'historical_approximation' (target halfway),
or when Phase B (sources enrichment) starts taking over.

## Cumulative iter stats

- **Iter 1**: 10 boundaries + 1 fact-check + 1 deploy. v6.99.29 live.
- Status: **20/287 (7%) Phase A complete**
