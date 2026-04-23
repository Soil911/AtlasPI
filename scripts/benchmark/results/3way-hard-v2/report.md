# 3-Way Isolation Test (v7.0.3)

Sample: 28 questions (stratified by category)

## Accuracy per condition

| Condition | Accuracy | Hallucinations | N |
|---|---|---|---|
| baseline (Claude only) | 88.6% | 0.21 | 28 |
| atlaspi_prompt_only | 85.9% | 0.37 | 27 |
| atlaspi_full (prompt + tools) | 90.5% | 0.07 | 28 |

## Attribution

- **Prompt effect** (prompt_only - baseline): **-2.6pp**
- **Tool effect** (full - prompt_only): **+4.6pp**
- **Combined effect** (full - baseline): **+2.0pp**

**Diagnosis**: TOOL-DOMINANT: value is in tool calls, prompt alone insufficient

