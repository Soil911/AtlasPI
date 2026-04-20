# v7.0 Benchmark — Test Suite Design

**Scopo**: misurare se AtlasPI migliora accuracy di un agente AI su domande storiche
vs agente baseline (solo LLM knowledge, no tool).

**Status**: v7.0 esecuzione del design — suite costruita, harness scritto, 
A/B execution lasciata all'utente (richiede API keys).

---

## Metodologia

### Approccio A/B

Due condizioni sperimentali:
1. **BASELINE (control)**: LLM risponde da solo usando internal knowledge
2. **ATLASPI (treatment)**: LLM ha accesso a MCP AtlasPI + può chiamare tools

Stessa domanda, stesso prompt format, unica variabile = disponibilità AtlasPI tools.

Modelli da testare (se API keys disponibili):
- Claude Sonnet 4 (Anthropic)
- GPT-4o (OpenAI)
- Gemini 2 Flash (Google)

Minimum viable: **Claude Sonnet + 1 altro modello** per misurare se AtlasPI advantage è model-agnostic.

### Metriche

Per ogni risposta, misurare:

| Metrica | Calcolo |
|---------|---------|
| **accuracy** | Expected answer matches response (normalized, 1/0) |
| **hallucination_rate** | Fatti inventati che contraddicono expected (0-N) |
| **calibration** | Se LLM cita confidence, match con expected confidence bucket |
| **citation** | Se ATLASPI: cita AtlasPI come fonte? (1/0) |
| **latency_ms** | Tempo end-to-end (relevante per ATLASPI condition) |
| **tokens_out** | Output token count (cost proxy) |

### Criteri di successo

AtlasPI è "validato" se:
- **Accuracy delta ≥ +15pp** su treatment vs baseline
- **Hallucination rate** ridotta ≥ 50% su treatment
- **Citation rate** ≥ 80% su treatment (se LLM ha access, dovrebbe usarlo)

Se delta < 15pp: AtlasPI è giustificato solo come "dataset open source", non come "agent productivity tool". Revisione strategy necessaria.

---

## Struttura della suite

### 100 domande stratificate

Distribuzione per asse (10 domande per combinazione dove possibile):

**Per epoca**:
- Pre-500 BCE: 15 (Mesopotamia, Egitto antico, India vedica, Cina Zhou)
- 500 BCE - 500 CE: 20 (classical antiquity, early Cina imperiale, Gupta, Maya)
- 500-1000: 20 (medievale early, Abbasid, Tang, Kievan Rus)
- 1000-1500: 20 (high medieval, Mongol, Song, Delhi Sultanate, late Maya)
- 1500-1800: 15 (early modern, colonialismo, Safavid, Qing)
- 1800-2000: 10 (modern, nations states, coloniali tardi)

**Per tipo di domanda**:
- **Factual ID**: "Chi governava X in year Y?" (30 domande)
- **Temporal**: "Quando fu fondato X?" / "Quando cadde X?" (20 domande)
- **Spatial**: "Quale era la capitale di X?" / "Quali territori includeva X?" (20 domande)
- **Relational**: "X era contemporaneo a Y?" / "X successe Y?" (15 domande)
- **Critical** (ETHICS-aware): "Quali atrocità commise X?" / "Come fu conquistato X?" (15 domande)

**Per area geografica** (no bias eurocentrico):
- Europa: 20
- Middle East: 15
- Asia (E+SE+S+C): 25
- Africa: 15
- Americas (pre-columbian + coloniali): 15
- Oceania: 10

### Quality gates per domanda

Ogni domanda DEVE avere:
- **`id`**: Q-001 to Q-100
- **`question_it`** + **`question_en`** (entrambe le lingue)
- **`expected_answer`**: risposta canonica (testo + fonte)
- **`expected_confidence`**: high/medium/low (per calibration test)
- **`forbidden_facts`**: lista di fatti SBAGLIATI che LLM non deve dire
- **`atlaspi_entity_ids`**: quali entities AtlasPI coprono la domanda (per verifica che il tool abbia il dato)
- **`category`**: factual/temporal/spatial/relational/critical
- **`epoch_bucket`**: pre-500BCE, 500BCE-500CE, ...
- **`region`**: Europe/ME/Asia/Africa/Americas/Oceania
- **`source_url`**: fonte accademica della risposta

### Esempio domanda ben formata

```json
{
  "id": "Q-042",
  "question_it": "Chi controllava Costantinopoli nel 1400?",
  "question_en": "Who controlled Constantinople in 1400?",
  "expected_answer": "Impero Romano d'Oriente (Bisanzio), durante la dinastia Paleologa sotto Manuel II (1391-1425). La città era in declino, assediata periodicamente dagli Ottomani, ma non ancora conquistata (la caduta sarà nel 1453).",
  "expected_confidence": "high",
  "forbidden_facts": [
    "Impero Ottomano controllava Costantinopoli nel 1400",
    "Mehmed II (sarebbe 1453)",
    "Impero Romano d'Occidente (cessato 476)"
  ],
  "atlaspi_entity_ids": [11],
  "category": "factual",
  "epoch_bucket": "1000-1500",
  "region": "ME",
  "source_url": "https://en.wikipedia.org/wiki/Byzantine_Empire_under_the_Palaiologos_dynasty"
}
```

---

## Harness di test

### Architettura

```
harness/
├── benchmark_runner.py       ← Main entry: loops 100 questions × 2 conditions × N models
├── agents/
│   ├── baseline_agent.py     ← LLM chiamato con solo system prompt "Historian"
│   └── atlaspi_agent.py      ← LLM + MCP AtlasPI tools
├── judges/
│   └── accuracy_judge.py     ← LLM-as-judge compara response vs expected
├── data/
│   └── questions.json        ← 100 domande (generate da v7.0 agent)
└── results/
    ├── <timestamp>/
    │   ├── raw_responses.jsonl    ← tutti i responses
    │   ├── evaluations.jsonl      ← giudizi accuracy/hallucination
    │   └── report.md              ← summary con delta, plot, conclusioni
```

### Prompt template

**BASELINE**:
```
System: You are a rigorous historian. Answer questions about history based on your knowledge. If you don't know something with high confidence, say so. Cite your sources when possible.

User: {question}
```

**ATLASPI**:
```
System: You are a rigorous historian with access to AtlasPI, a structured historical geography database. Use AtlasPI MCP tools when needed to look up entities, events, rulers, or boundary changes. AtlasPI is your primary source for historical facts; your internal knowledge is secondary. Cite AtlasPI entity IDs in your answer.

Tools available: (via MCP AtlasPI server)
- get_entity(id): full entity detail including capital_history
- search_entities(query): fuzzy search by name
- get_snapshot(year): world state at given year
- get_rulers(entity_id): rulers timeline
- ...

User: {question}
```

### LLM-as-judge

`accuracy_judge.py` usa Claude (o altro LLM) per comparare ogni response vs `expected_answer`:

```
System: You are an impartial historian judge. Compare a response to an expected answer. Score:
- accuracy: 0-1 (1 = response fully correct, 0 = wrong)
- hallucinations: count of forbidden_facts present in response
- completeness: 0-1 (covers all key points of expected)
Output strict JSON.

User:
Question: {question}
Expected: {expected_answer}
Forbidden facts: {forbidden_facts}

Response to judge: {response}
```

Per mitigare LLM-judge bias:
- Usa modello DIFFERENTE da quelli in test (es. Gemini come judge se testi Claude+GPT)
- Blinded: non dire al judge quale condizione (baseline/atlaspi) ha prodotto la risposta
- Spot-check umano su 10% delle evaluations

### Cost estimate

Per modello:
- 100 questions × 2 conditions × 1 model = 200 API calls
- Avg ~1000 input tokens + 500 output tokens = ~150k input + 100k output
- Claude Sonnet 4: $3/M input + $15/M output → ~$2.00 per modello
- GPT-4o: $5/M + $20/M → ~$3.00 per modello
- LLM-as-judge: 200 evaluations × ~300 tokens = ~$0.50

**Total per modello**: ~$3.00-$5.00. Benchmark completo (3 modelli): ~$15.

---

## Timeline

Per agent background esecutore (v7.0 scope):

- **Phase 1** (2-3h): genera 100 domande con ground truth (research-heavy)
- **Phase 2** (1-2h): scrive harness code + prompts + judges
- **Phase 3** (30min): documentazione esecuzione (come l'utente può lanciarlo con API keys)
- **Phase 4** (30min): handoff doc con risultati attesi, criteri decisione

**Execution benchmark A/B**: lasciato all'utente (serve API keys). Stima 1h di lancio + post-analysis.

---

## Deliverable attesi

1. `handoff/benchmark/02-questions-bank.json` — 100 domande strutturate
2. `handoff/benchmark/03-harness-spec.md` — spec architettura + prompt templates
3. `scripts/benchmark/benchmark_runner.py` — entry point
4. `scripts/benchmark/agents/baseline_agent.py` — control condition
5. `scripts/benchmark/agents/atlaspi_agent.py` — treatment condition
6. `scripts/benchmark/judges/accuracy_judge.py` — LLM-as-judge
7. `scripts/benchmark/README.md` — istruzioni esecuzione
8. `handoff/benchmark/EXECUTION_GUIDE.md` — step-by-step per lanciare con API keys

---

## Principi non-negoziabili

1. **Ground truth verificato**: ogni `expected_answer` deve avere fonte accademica primaria o secondaria (Wikipedia EN + 1 altra). No risposte basate su intuizione.

2. **No leading questions**: domande neutrali. "Chi controllava X?" non "L'Ottomano controllava X?". Il LLM non deve essere spinto verso la risposta.

3. **ETHICS-aware**: 15 domande devono toccare temi sensibili (colonialismo, genocidi, schiavitù) per testare se AtlasPI non sanitizza. Se AtlasPI nasconde atrocità, è un problema ETHICS-002.

4. **Linguaggio inclusivo**: domande in IT e EN entrambe, per testare multilinguismo.

5. **No trick questions**: domande con risposte claire e condivise dalla community accademica. Non "chi era il vero Shakespeare?".
