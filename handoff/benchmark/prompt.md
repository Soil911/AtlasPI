# Prompt per v7.0 Benchmark Agent

> Incollare come primo messaggio in una sessione Claude Code (o Agent SDK)
> dedicata. La sessione lavora in autonomia, produce deliverable, notifica.

---

```
Sei una sessione dedicata alla costruzione del benchmark v7.0 per AtlasPI.
Obiettivo strategico: produrre una test suite riutilizzabile che misuri se
AtlasPI migliora l'accuracy di un agente AI su domande storiche vs LLM
baseline senza tool.

Questo è "consolidamento" prima di scalare feature. Senza questo benchmark,
tutti i cleaning dati precedenti (30 release v6.60→v6.91) sono fede
non misurata.

═══════════════════════════════════════════════════════════════════
FASE 0 — Discovery + setup
═══════════════════════════════════════════════════════════════════

1. git pull (stato repo v6.91.0 stabile)
2. Leggi OBBLIGATORIAMENTE:
   - CLAUDE.md (valori, ETHICS convention)
   - handoff/benchmark/01-test-suite-design.md (metodologia + target)
   - docs/audit/FASE_C_CHIUSURA.md (cosa sa AtlasPI)
   - docs/adr/ADR-004 e ADR-005 (capital_history + deprecated merge)
3. Ispeziona lo stato live:
   - curl https://atlaspi.cra-srl.com/health
   - curl https://atlaspi.cra-srl.com/v1/entities?limit=3
   - Verifica che capital_history sia esposto (es. entity 2 Ottoman)
4. git checkout -b feature/v7.0-benchmark (se non esiste)

═══════════════════════════════════════════════════════════════════
FASE 1 — Generazione 100 domande (MAIN EFFORT)
═══════════════════════════════════════════════════════════════════

Obiettivo: produrre `handoff/benchmark/02-questions-bank.json` con 100
domande che rispettano la stratificazione di 01-test-suite-design.md §
"Struttura della suite".

Distribuzione (come da spec):
- Per epoca: 15 pre-500BCE + 20 500BCE-500CE + 20 500-1000 + 20 1000-1500
  + 15 1500-1800 + 10 1800-2000
- Per tipo: 30 factual + 20 temporal + 20 spatial + 15 relational + 15 critical
- Per regione: 20 Europa + 15 ME + 25 Asia + 15 Africa + 15 Americas + 10 Oceania

Strategia MULTI-AGENT per parallelism:

Spawn 5 agenti paralleli, uno per region, ognuno produce ~15-25 domande nel
suo quadrante geografico:

**Agent A** (Europa, 20 domande): Roma, Bisanzio, HRE, France, UK, Germania,
Italia, Russia, Polonia, Spagna, Portogallo, Venezia, Scandinavia.

**Agent B** (Middle East, 15 domande): Achaemenid, Seleucid, Parthia,
Sasanid, Abbasid, Ottomani, Safavid, Mamluk, crusader states.

**Agent C** (Asia S+SE+E+C, 25 domande): Maurya, Gupta, Chola, Vijayanagara,
Mughal, Delhi Sultanate, Tang/Song/Yuan/Ming/Qing, Khmer, Majapahit,
Mongol Empire, Timurid, Japan.

**Agent D** (Africa, 15 domande): Kush, Aksum, Mali, Songhai, Kanem-Bornu,
Zimbabwe, Ethiopia (Solomonic), Egypt dynasties, Kongo, Sokoto.

**Agent E** (Americas + Oceania, 25 domande): Maya, Aztec, Inca, Olmec,
Teotihuacan, Cahokia, Iroquois, Moche, Chimu, Aotearoa, Polynesian chiefdoms.

Ogni agent per ogni domanda:
1. Consulta Wikipedia EN + 1 fonte accademica (Britannica, WHE, Cambridge History)
2. Scrive question_it + question_en
3. Scrive expected_answer con sfumature (date, nomi, incertezze)
4. Lista forbidden_facts (errori comuni che un LLM potrebbe fare)
5. Trova atlaspi_entity_ids rilevanti via curl /v1/search?q=
6. Classifica category (factual/temporal/spatial/relational/critical)
7. Cita source_url

Validation step: aggrega output di 5 agenti, verifica:
- Totale = 100 (±2 accettabile)
- Distribuzione epochs matches target (±2 per bucket)
- Distribuzione categories matches target (±3 per category)
- No duplicate questions
- 15 domande "critical" coprono temi ETHICS reali (colonialismo, genocidi,
  schiavitù, cancellazioni culturali)
- Ogni domanda ha source_url valido

Output: `handoff/benchmark/02-questions-bank.json`

═══════════════════════════════════════════════════════════════════
FASE 2 — Harness di test (code)
═══════════════════════════════════════════════════════════════════

Struttura da creare:

```
scripts/benchmark/
├── benchmark_runner.py          ← entry point
├── agents/
│   ├── __init__.py
│   ├── baseline_agent.py        ← LLM senza tools
│   └── atlaspi_agent.py         ← LLM + MCP AtlasPI
├── judges/
│   ├── __init__.py
│   └── accuracy_judge.py        ← LLM-as-judge
├── README.md                    ← istruzioni utente
└── requirements.txt             ← dipendenze Python
```

`benchmark_runner.py` deve:
- Caricare questions.json
- Iterare: for q in questions: for condition in [baseline, atlaspi]: for model in [claude, gpt]
- Salvare raw_responses.jsonl
- Invocare judge per ogni response
- Aggregare risultati in report.md (markdown tables + insights)

`baseline_agent.py`:
- Usa SDK ufficiale del provider
- System prompt "rigorous historian"
- Nessun tool

`atlaspi_agent.py`:
- Usa SDK provider con tool calling
- System prompt "historian with AtlasPI access"
- Tool definition espone endpoints AtlasPI come functions callable:
  - `get_entity(id: int)` → calls GET /v1/entities/{id}
  - `search_entities(query: str)` → calls /v1/search?q=
  - `get_snapshot_year(year: int)` → calls /v1/snapshot/year/{year}
  - `get_rulers(entity_id: int)` → calls /v1/rulers?entity_id=
  - `get_events_at(year: int)` → calls /v1/events/at-date/
- Loop di tool calls finché LLM dichiara risposta finale

`accuracy_judge.py`:
- LLM come giudice (usa modello diverso da quelli in test per imparzialità)
- Prompt blinded (non rivela condizione)
- Output JSON strict: {accuracy: 0-1, hallucinations: int, completeness: 0-1}

Environment variables necessarie per esecuzione:
- ANTHROPIC_API_KEY
- OPENAI_API_KEY (opzionale se solo Claude)
- GOOGLE_API_KEY (opzionale)
- ATLASPI_BASE_URL (default https://atlaspi.cra-srl.com)

═══════════════════════════════════════════════════════════════════
FASE 3 — Documentazione esecuzione
═══════════════════════════════════════════════════════════════════

Scrivi `handoff/benchmark/EXECUTION_GUIDE.md`:

- Prerequisites (Python version, API keys, requirements)
- Setup: `cd scripts/benchmark && pip install -r requirements.txt`
- Dry run: `python benchmark_runner.py --dry-run` (verifica setup)
- Lancio: `python benchmark_runner.py --models claude,gpt4o --output results/$(date +%Y%m%d)`
- Cost estimate
- Come leggere report.md
- Come fare statistical significance test (scipy.stats)
- Come decidere v7.1 go/no-go basato sui numeri

═══════════════════════════════════════════════════════════════════
FASE 4 — Commit + handoff cofounder
═══════════════════════════════════════════════════════════════════

Commit atomici per fase:
- `feat(benchmark): questions bank 100 domande stratificate (Fase 1)`
- `feat(benchmark): harness runner + agents + judge (Fase 2)`
- `docs(benchmark): execution guide + cofounder review stub (Fase 3)`
- `chore: bump to v7.0.0 (benchmark suite ready)` ← version bump

Apri PR verso main, self-merge (full autonomy autorizzata).
Deploy NON necessario (scripts/benchmark è offline, no prod impact).

Scrivi `handoff/benchmark/COFOUNDER_REVIEW.md`:
- Totale domande generate + distribuzione
- Harness architecture summary
- Domande che sono state difficili da ground-truth (ambigue)
- Raccomandazioni per esecuzione (quale modello prima, quanti run)
- Rischi identificati (bias campione, etc.)

═══════════════════════════════════════════════════════════════════
MODALITÀ DI LAVORO
═══════════════════════════════════════════════════════════════════

Full autonomy. Non fermarti per conferma. Lavora in background, committa
per fase. Spawn agenti paralleli in Fase 1 per efficienza.

Principi:
- QUALITÀ > velocità. 50 domande eccellenti > 100 mediocri.
- Ogni domanda con ground truth verificato da 2 fonti.
- Ogni forbidden_fact è un errore plausibile che LLM potrebbe fare.
- ETHICS-aware: 15 domande critiche sono REALI, non sanitizzate.

Se una region agent produce meno di 10 domande, redistribuisci quota agli
altri (fallback graceful).

Se harness incontra edge case (rate limit, timeout, API error), log e
continua — il runner deve essere resilient, non bloccante.

═══════════════════════════════════════════════════════════════════
DELIVERABLE FINALE
═══════════════════════════════════════════════════════════════════

Quando hai finito, scrivi una risposta finale CONCISA con:

- PR + commit list
- Questions bank: N/100 generate, distribuzione effettiva vs target
- Harness: pronto? dry-run test passed?
- EXECUTION_GUIDE: link a file
- COFOUNDER_REVIEW: link a file
- Stima costo benchmark completo per l'utente
- Tempo execution stimato (~2h per modello)

L'utente lancerà il benchmark vero e proprio con le sue API keys, poi
aprirà sessione cofounder per analizzare risultati v7.0.

Inizia da FASE 0.
```
