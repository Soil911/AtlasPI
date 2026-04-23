# AtlasPI v7.0 Benchmark

Misura se AtlasPI migliora accuracy di Claude su domande storiche
vs Claude senza tools (A/B test con LLM-as-judge).

## Decisioni pre-run fissate (v7.0)

- **Primary LLM**: Claude Sonnet 4.5
- **Judge**: Claude Opus 4.5 (modello più forte per imparzialità)
- **Billing**: CRA business ANTHROPIC_API_KEY
- **Threshold success tier**:
  - `< +5pp` → ❌ FAIL (revisione strategy drastica)
  - `+5 a +12pp` → ⚠️ WEAK (investigate coverage vs UX MCP)
  - `+12 a +20pp` → ✅ ACCEPTABLE (procedere v7.1-v7.4)
  - `> +20pp` → 🟢 STRONG (push adoption + case study)
- **Upgrade rule**: se overall WEAK ma ≥1 categoria ≥ +20pp, specialty strength da raccontare

## Setup

```bash
# 1. Install deps
pip install -r scripts/benchmark/requirements.txt

# 2. Export API key (CRA business)
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Verify AtlasPI live (should return v6.92+)
curl https://atlaspi.cra-srl.com/health
```

## Dry-run (5 seed questions, ~$0.20)

Per verificare setup + harness + HTTP tool calls contro AtlasPI:

```bash
python -m scripts.benchmark.benchmark_runner --dry-run --output scripts/benchmark/results/dryrun-$(date +%Y%m%d-%H%M%S)
```

Atteso output:
- `raw_responses.jsonl` — ogni Q × {baseline, atlaspi}
- `evaluations.jsonl` — judge verdict
- `report.md` — tabella aggregata

Se dry-run passa: le 5 seed questions dovrebbero mostrare AtlasPI accuracy
molto migliore di baseline (es. SEED-002 capital Ottoman 1400 — baseline
dice Istanbul, AtlasPI dice Edirne).

## Full benchmark (100 questions, ~$15)

```bash
# Attendere questions-bank generato da agent v7.0.2
python -m scripts.benchmark.benchmark_runner \
    --questions scripts/benchmark/questions/questions-bank-v1.json \
    --output scripts/benchmark/results/full-$(date +%Y%m%d-%H%M%S)
```

## Cost estimate

Per run (Claude Sonnet 4.5 + Claude Opus 4.5 judge):
- Baseline: 100 Q × ~500 tok in + ~300 tok out = ~$0.50
- AtlasPI: 100 Q × ~1500 tok in (incl. tool outputs) + ~400 tok out = ~$2.00
- Judge: 100 × 2 evals × ~700 tok in + ~200 tok out = ~$10.00
- **Totale: ~$12-15**

## Interpretation

Apri `results/<timestamp>/report.md`. La tabella "Overall delta" contiene
il verdetto automatico basato sul tier.

Esempio output atteso:

```
## Overall delta

| Metric | Baseline | AtlasPI | Delta |
|---|---|---|---|
| Accuracy | 62% | 76% | **+14 pp** |
| Hallucinations avg | 0.8 | 0.3 | -0.5 |

**Verdict**: ✅ ACCEPTABLE — valore misurabile. Procedere v7.1-v7.4.

## By category

| Category | n | Baseline | AtlasPI | Delta |
|---|---|---|---|---|
| factual | 30 | 70% | 78% | +8 pp |
| spatial | 20 | 55% | 85% | **+30 pp** ← killer feature
| temporal | 20 | 58% | 72% | +14 pp |
| relational | 15 | 65% | 73% | +8 pp |
| critical | 15 | 70% | 85% | +15 pp |
```

La categoria con delta più alto (qui `spatial`) è il "specialty strength"
da usare in marketing.

## Files

- `benchmark_runner.py` — main entry
- `agents/baseline_agent.py` — Claude senza tools
- `agents/atlaspi_agent.py` — Claude con 5 MCP-like tools (search, get_entity,
  snapshot_year, get_rulers, events_at) che chiamano AtlasPI REST API live
- `judges/accuracy_judge.py` — Claude Opus come judge, output JSON strict
- `questions/seed_questions.json` — 5 dummies per dry-run
- `questions/questions-bank-v1.json` — 100 questions (generate da v7.0.2 agent)
