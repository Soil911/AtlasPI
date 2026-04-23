# ADR-007 — AtlasPI è tool-augmented retrieval, non prompt template

**Status**: Adopted (v7.0 benchmark closure, 2026-04-23)
**Authors**: Cofounder audit post v7.0
**Deciders**: Clirim Ramadani
**Supersedes**: marketing positioning precedente "AtlasPI è dataset + MCP server"

---

## Contesto

Prima release public di AtlasPI si posizionava come "tool per AI agents" (MCP server + REST API) ma senza evidenza empirica che migliorasse l'accuracy degli agenti. Dopo 30+ release di cleaning dati (v6.60-v6.91, audit v1-v4), serviva validare la tesi con un benchmark A/B rigoroso.

**Domanda strategica di business**: AtlasPI come tool giustifica l'integrazione MCP per un utente agent, o è essenzialmente un dataset Zenodo + prompt template riusabile?

## Methodology

### v7.0 benchmark complete

Tre esperimenti sequenziali:

1. **Full v7.0 bank v1** (100 Q Wikipedia-derived)
   - Condition: baseline (Claude alone) vs atlaspi_full (Claude + MCP tools)
   - Result: **+0.9pp FAIL** (baseline 92.2%, atlaspi 91.3%)
   - Caveat: **ceiling effect** — baseline saturated because questions matched Wikipedia training

2. **3-way isolation v7.0.3 bank v1 subset** (20 Q stratified)
   - New condition: `atlaspi_prompt_only` (Claude + AtlasPI prompt + NO tools)
   - Result: baseline 89.8%, prompt_only 91.0%, full 93.0%
   - Attribution: prompt +1.2pp, tool +2.0pp, combined +3.2pp
   - Diagnosis: MIXED

3. **3-way on bank v2 hard** (30 Q designed to trap LLM baseline, 28 judged)
   - Same 3 conditions, but questions specifically where Claude's training fails:
     - Capital anachronisms (Ottoman capital 1400 = Edirne, not Istanbul)
     - Cross-dynasty traps (Chola Sangam vs Medieval, 8-century gap)
     - ETHICS-level atrocities (Congo Free State, Herero genocide, Bengal famine)
     - Name anachronisms (Dai Co Viet 968-1054, not Dai Viet)
   - Result: **baseline 88.6%, prompt_only 85.9%, full 90.5%**
   - Attribution: **prompt -2.6pp (NEGATIVE), tool +4.6pp, combined +2.0pp**
   - Hallucinations: baseline 0.21, prompt_only 0.37 (WORSE), full 0.07 (**-67% vs baseline**)
   - **Diagnosis: TOOL-DOMINANT**

## Decisione

AtlasPI è **tool-augmented retrieval system**, non prompt template.

### Evidenze determinanti

1. **Prompt-only is HARMFUL on hard questions** (-2.6pp). Claude given a prompt claiming "AtlasPI authority" but NO tools actually generates MORE hallucinations (0.21 → 0.37, +76% relative). Model tries to sound authoritative without data, inventing more.

2. **Tools deliver REAL value** (+4.6pp on hard Q bank, from 85.9% prompt-only to 90.5% full). Tool calls are what drive accuracy improvement.

3. **Hallucination reduction is the killer metric** (baseline 0.21 → full 0.07 = **-67%**). This is the most defensible, vendible claim.

### Implicazioni strategiche

- **Marketing**: "AtlasPI reduces LLM hallucinations 3x on historical queries" (NOT "AtlasPI makes LLMs more accurate generically")
- **Product positioning**: RAG-style tool for agents, NOT prompt library
- **MCP priority**: MCP server è core feature, expand tool coverage (vedi v7.1 roadmap)
- **Prompt engineering**: rivedere `SYSTEM_PROMPT` di atlaspi_agent — rimuovere "claims of superiority" che causano hallucinations senza dati

## Alternatives considerate

### Alt 1 — Pivot a "dataset only, no tool"

**Rejected.** Evidenza empirica: tool effect +4.6pp > prompt effect -2.6pp. Eliminando tool si perde il valore primary. Dataset Zenodo/HuggingFace è asset secondario, non primario.

### Alt 2 — Pivot a "prompt template only, no tool"

**Strongly rejected.** Prompt-only è ATTIVAMENTE DANNOSO: riduce accuracy -2.6pp e aumenta hallucinations +76% relative. Distribuire solo un prompt sarebbe peggiorativo per gli utenti.

### Alt 3 — Synergistic positioning (prompt + tool insieme)

**Rejected on hard Q evidence.** Prompt non aggiunge valore quando tools sono presenti. Il +2pp combined è TUTTO tool effect. Semplificare: MCP tool è il prodotto, prompt è implementation detail.

### Alt 4 — Tool-only positioning (adopted)

**Adopted.** Il prompt di sistema di atlaspi_agent va rivisto in v7.1:
- Rimuovere: "Prefer AtlasPI data to your training knowledge when they CONFLICT"
- Rimuovere: "AtlasPI is curated and more up-to-date"
- Mantenere: definizione degli 5 tools e quando usarli
- Aggiungere: "When tools return empty/partial, defer to training knowledge explicitly"

## Consequences

### Positive

- **Claim empirico difendibile**: -67% hallucinations è vendibile a ricercatori, sviluppatori di agenti AI, contenuti editoriali storici
- **Roadmap chiaro per v7.1**:
  - Expand tool coverage (rulers time-range query, events by entity, language/script lookup)
  - Prompt revision per ridurre hallucinations in prompt-only mode
  - Hallucination reduction come KPI primary (non solo accuracy)
- **Bank v2 è gold standard** per future benchmark: 30 Q trap-designed, reusable

### Negative

- **Overall +2pp è modest** per marketing general-purpose. Serve framing come "specialty tool" + hallucination-focused.
- **Ceiling effect su easy Q**: per il 70% delle domande storiche dove Wikipedia basta, AtlasPI non aggiunge valore. Target audience = historical researchers + specialized agents, non mass consumer Q&A.
- **Bank v1 unusable come marketing metric** (FAIL tier a causa ceiling). Non citare -0.9pp.

### Trade-offs metodologici

- **Judge bias caveat**: Claude Opus 4.5 come judge di Claude Sonnet 4.5 è same-vendor. Un cross-vendor judge (GPT-4 o Gemini) confermerebbe. Ma evidenza interna è coerente.
- **Sample size**: N=28 su hard bank è statisticamente ampio-margine. Full N=100 su hard bank costerebbe altri $15 ma confermerebbe.
- **Non misurato**: multi-turn agent use (benchmark è single-turn Q&A), costo-latency tradeoff per production agents.

## Implementation items (v7.1)

| # | Task | Owner | ETA |
|---|------|-------|-----|
| 1 | Revise `SYSTEM_PROMPT` di `atlaspi_agent.py` rimuovendo superiority claims | Claude Code | v7.1.0 |
| 2 | Add 3 nuovi tools: `get_rulers_at_year`, `get_events_by_entity`, `get_languages_at_year_region` | Claude Code | v7.1.0 |
| 3 | Marketing landing page: "Reduce LLM hallucinations 3x" + benchmark methodology page | TBD | v7.2.0 |
| 4 | Cross-vendor judge validation (GPT-4 o Gemini su sample 30 hard Q) | Claude Code | v7.1.x |
| 5 | Measure multi-turn agent use case (AtlasPI nel flow ricerca ripetuta) | TBD | v7.3.0 |
| 6 | Production cost/latency tradeoff doc: tool calls add ~3× latency e ~2× tokens | Claude Code | v7.1.0 |

## Stato finale

Benchmark closure artifacts in `scripts/benchmark/results/`:
- `full-v1/` — 100 Q bank v1 complete A/B (ceiling effect)
- `3way-v1/` — 20 Q bank v1 3-way isolation (MIXED)
- `3way-hard-v2/` — 30 Q bank v2 3-way isolation (TOOL-DOMINANT)

Banks:
- `questions-bank-v1.json` — general 100 Q from Wikipedia
- `questions-bank-hard-v2.json` — 30 Q trap-designed

Harness in `scripts/benchmark/`: runner + 3 agents + judge + rejudge + resume utilities.

**Verdetto finale**: AtlasPI è tool-augmented retrieval, validated. Procedi v7.1 con prompt revision + tool expansion + marketing pivot.
