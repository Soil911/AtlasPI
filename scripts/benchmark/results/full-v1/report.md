# AtlasPI v7.0 Benchmark — Report A/B
Generated: 2026-04-23T15:33:44.783248
Total questions: 100 (judged: 100)

## Overall delta

| Metric | Baseline (Claude solo) | AtlasPI (Claude + tools) | Delta |
|---|---|---|---|
| Accuracy | 92.2% | 91.3% | **-0.9 pp** |
| Hallucinations (avg per question) | 0.06 | 0.05 | -0.01 |

**Verdict**: ❌ FAIL — AtlasPI non giustifica MCP complexity. Revisione strategy drastica.

## By category

| Category | n | Baseline | AtlasPI | Delta |
|---|---|---|---|---|
| critical | 15 | 89.7% | 89.6% | **-0.0 pp** |
| factual | 26 | 96.3% | 94.8% | **-1.5 pp** |
| relational | 15 | 88.3% | 86.7% | **-1.7 pp** |
| spatial | 22 | 89.5% | 92.3% | **+2.7 pp** |
| temporal | 22 | 94.1% | 90.5% | **-3.6 pp** |

## By epoch

| Epoch | n | Baseline | AtlasPI | Delta |
|---|---|---|---|---|
| 1000-1500 | 21 | 90.5% | 91.7% | **+1.2 pp** |
| 1500-1800 | 19 | 89.5% | 90.0% | **+0.5 pp** |
| 1800-2000 | 9 | 91.7% | 88.3% | **-3.3 pp** |
| 500-1000 | 19 | 93.9% | 92.4% | **-1.6 pp** |
| 500BCE-500CE | 16 | 95.0% | 92.3% | **-2.7 pp** |
| pre-500BCE | 16 | 92.8% | 91.6% | **-1.2 pp** |

## By region

| Region | n | Baseline | AtlasPI | Delta |
|---|---|---|---|---|
| Africa | 15 | 89.7% | 92.5% | **+2.8 pp** |
| Americas | 13 | 91.9% | 90.8% | **-1.2 pp** |
| Asia | 26 | 93.1% | 92.7% | **-0.4 pp** |
| Europe | 22 | 92.3% | 89.3% | **-3.0 pp** |
| ME | 16 | 91.9% | 90.0% | **-1.9 pp** |
| Oceania | 8 | 94.4% | 93.1% | **-1.2 pp** |
