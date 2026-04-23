# 3-Way Isolation Test (v7.0.3)

Sample: 20 questions (stratified by category)

## Accuracy per condition

| Condition | Accuracy | Hallucinations | N |
|---|---|---|---|
| baseline (Claude only) | 89.8% | 0.05 | 20 |
| atlaspi_prompt_only | 91.0% | 0.00 | 20 |
| atlaspi_full (prompt + tools) | 93.0% | 0.00 | 20 |

## Attribution

- **Prompt effect** (prompt_only - baseline): **+1.2pp**
- **Tool effect** (full - prompt_only): **+2.0pp**
- **Combined effect** (full - baseline): **+3.2pp**

**Diagnosis**: MIXED: unclear attribution

