# AtlasPI v7.0 Benchmark — Report A/B
Generated: 2026-04-23T14:11:44.653194
Total questions: 5 (judged: 5)

## Overall delta

| Metric | Baseline (Claude solo) | AtlasPI (Claude + tools) | Delta |
|---|---|---|---|
| Accuracy | 83.0% | 94.0% | **+11.0 pp** |
| Hallucinations (avg per question) | 0.4 | 0.0 | -0.40 |

**Verdict**: ⚠️ WEAK — margine ridotto. Investigate: coverage dataset o UX MCP?

## By category

| Category | n | Baseline | AtlasPI | Delta |
|---|---|---|---|---|
| critical | 1 | 100.0% | 100.0% | **+0.0 pp** |
| factual | 1 | 100.0% | 70.0% | **-30.0 pp** |
| relational | 1 | 95.0% | 100.0% | **+5.0 pp** |
| spatial | 1 | 30.0% | 100.0% | **+70.0 pp** |
| temporal | 1 | 90.0% | 100.0% | **+10.0 pp** |

## By epoch

| Epoch | n | Baseline | AtlasPI | Delta |
|---|---|---|---|---|
| 1000-1500 | 2 | 97.5% | 85.0% | **-12.5 pp** |
| 1500-1800 | 1 | 100.0% | 100.0% | **+0.0 pp** |
| 500-1000 | 1 | 30.0% | 100.0% | **+70.0 pp** |
| 500BCE-500CE | 1 | 90.0% | 100.0% | **+10.0 pp** |

## By region

| Region | n | Baseline | AtlasPI | Delta |
|---|---|---|---|---|
| Africa | 1 | 90.0% | 100.0% | **+10.0 pp** |
| Asia | 1 | 95.0% | 100.0% | **+5.0 pp** |
| ME | 3 | 76.7% | 90.0% | **+13.3 pp** |
