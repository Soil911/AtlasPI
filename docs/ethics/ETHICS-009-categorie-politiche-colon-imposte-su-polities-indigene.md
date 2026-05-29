# ETHICS-009 — Imposizione di categorie politiche coloniali su polities indigene pre-coloniali

**Status**: Adottato 2026-04-18 (v6.66)
**Autori**: AI Co-Founder + audit v2 agent 04
**Riferimenti**: CLAUDE.md §valori ETHICS-001 "Nessuna versione unica della storia" + §"Nessun bias geografico o culturale dominante"

---

## Problema identificato

L'audit v2 agent 04 ha rilevato che **l'entità id=55 Aotearoa**:
- aveva `capital = "Kororareka" (-35.26°N, 174.12°E)` per l'intero periodo 1250-1840
- `entity_type = "confederation"` per lo stesso periodo

Entrambi i campi impongono categorie politiche europee (capitale permanente, stato confederale) su una società pre-coloniale che non le aveva:

### Fatti accertati

1. **Kororareka (odierna Russell)** era un insediamento balenieri europeo fondato attorno al 1810s. Non era un sito politico Māori prima del contatto europeo, e usarlo come "capitale" per il periodo 1250-1810 è **fisicamente impossibile** (l'insediamento non esisteva).

2. **La società Māori pre-coloniale** era organizzata in *iwi* (nazioni/tribù) e *hapū* (sotto-tribù) con rangatira (chief) locali. Non esisteva un'autorità pan-Māori centralizzata, né una "confederazione" nel senso politico europeo.

3. **La Confederation of the United Tribes of New Zealand (Te Whakaminenga)** fu una confederazione formalizzata solo nel 1835 con la *Declaration of the Independence of New Zealand* — 585 anni dopo `year_start=1250` attribuito a AtlasPI. La sua sede de facto era Waitangi (non Kororareka).

**Fonti**:
- Wikipedia EN [Māori history](https://en.wikipedia.org/wiki/M%C4%81ori_history)
- Te Ara Encyclopedia of New Zealand [Māori arrival and settlement](https://teara.govt.nz/en/history/page-1)
- King M. (2003) "The Penguin History of New Zealand"
- Orange C. (1987) "The Treaty of Waitangi"

---

## Perché è un problema etico, non solo fattuale

CLAUDE.md stabilisce: *"Le conquiste coloniali sono descritte anche dal punto di vista dei conquistati"* e *"i nomi dei luoghi usano la forma nella lingua locale come nome primario"*.

Attribuire a una società pre-coloniale categorie (capitale, tipo di stato) che quella società **non riconosceva** significa:

1. **Proiettare lo sguardo coloniale**: descrivere la società indigena nei termini dello stato-nazione europeo, suggerendo implicitamente che le società senza capitale fissa o senza gerarchia centralizzata fossero "incomplete" o "primitive".

2. **Cancellare l'organizzazione indigena**: *iwi/hapū* con autorità distribuita è una forma politica legittima e stabile; ridurla a "confederazione senza capitale" è una semplificazione coloniale.

3. **Creare dati falsi**: un agente AI che interroga AtlasPI con `GET /v1/entities/55?year=1500` riceve "Kororareka" come capitale — un'affermazione falsa che il modello potrebbe ripetere autorevolmente.

---

## Alternative considerate

### Opzione A — Rimuovere capital + cambiare entity_type
- `capital = null`
- `entity_type = "decentralized_society"` (nuovo valore)
- Singola entità 1250-1840

**Pro**: minimo cambiamento schema. Comunica correttamente l'assenza di capitale.
**Contro**: il tipo "decentralized_society" non è standard; un agente AI con vocabolario limitato potrebbe non sapere come interpretarlo.

### Opzione B — Split in due entità
- Entità 55 aggiornata: **Pre-contact Māori Aotearoa** (1250-1835, capital=null, type="decentralized_society")
- Nuova entità: **Confederation of the United Tribes / Te Whakaminenga** (1835-1840, capital=Waitangi, type="confederation")

**Pro**: rispetta pienamente la cronologia storica; distingue fase pre-contatto dalla formalizzazione coloniale/intertribale.
**Contro**: richiede creazione di nuova entità + possibile update chain.

### Opzione C — Status quo con ethical_notes esteso
- Mantenere i dati esistenti ma aggiungere un ethical_notes lungo che spieghi i problemi.

**Pro**: zero rischio di regressione.
**Contro**: i campi strutturati (capital, entity_type) restano falsi; un agente AI che li consuma programmaticamente non legge ethical_notes. Violazione diretta del valore "Verità prima del comfort".

---

## Decisione

**Adottiamo Opzione B** con transizione graduale:

**Fase 1 (v6.66)** — Mitigazione immediata:
- Aggiorna entity 55 ethical_notes con ETHICS-009 reference e spiegazione completa
- NO modifica capital/entity_type ancora (evita rotture per consumer esistenti)

**Fase 2 (v6.67+)** — Split strutturale:
- Aggiorna entity 55: `year_end = 1835`, `capital = null`, `entity_type = "indigenous_society_decentralized"`
- Crea nuova entity: **Te Whakaminenga o Ngā Hapū o Nu Tireni** (name_original in Māori), 1835-1840, capital=Waitangi, entity_type="confederation"
- Aggiungi chain_link tra le due
- Aggiungi ADR `docs/adr/008-entity-type-indigenous-decentralized.md` per formalizzare il nuovo valore

---

## Regola generale derivata

**Per ogni polity che l'utente classifica come "pre-coloniale indigena":**

1. Non attribuire `capital` se la società era organizzata attorno ad autorità mobili, distribuite o itineranti (es. chieftaincies polinesiane, nomadi delle steppe, società di clan).
2. Se un "capital" esiste in letteratura, verifica che **esistesse fisicamente nel periodo dichiarato** e che fosse il centro di autorità politica (non solo religiosa/cerimoniale).
3. Se il tipo di stato europeo (empire, kingdom, republic) non descrive bene la società, usa `entity_type = "indigenous_society_decentralized"` o simile.
4. Nel campo `ethical_notes`, documenta esplicitamente le differenze tra la società pre-coloniale e la categoria usata per comodità.

**Polities da ri-auditare secondo questa regola** (campione, non esaustivo):
- Tutti i chiefdoms polinesiani in Oceania
- First Nations delle Americhe pre-1492 (es. varie confederacies)
- Polities pre-coloniali africane senza capitale fissa (Mali mansa court, già documentato in v6.65)
- Società nomadi dell'Asia centrale

---

## Impatto su `confidence_score`

Entità con capital anacronistica o entity_type mal-calzante **dovrebbero avere confidence_score ≤ 0.5** finché non risolte, e `status = "uncertain"`. Questo permette ai consumer di sapere che il dato strutturato è problematico.

---

## Change log applicato in v6.66

- `docs/ethics/ETHICS-009-categorie-politiche-colon-imposte-su-polities-indigene.md` (questo file) creato
- `entity/55 ethical_notes` aggiornato con riferimento a ETHICS-009 (v6.67)
- Audit programmato per i polity indigeni simili (v6.67+)

---

## Addendum 2026-05-29 (Wave 2.4) — stato reale della Fase 2: DIFFERITA

**Onestà di processo (audit Wave 2, finding #10, HIGH).** Una verifica a freddo
ha rilevato che la **Fase 2 strutturale dichiarata sopra NON è mai stata
implementata**, pur essendo questo record marcato "Adottato":

- `grep` nell'intero repo (data/, src/, docs/): **zero** occorrenze di
  `indigenous_society_decentralized` / `decentralized_society`.
- L'ADR previsto (`docs/adr/008-entity-type-indigenous-decentralized.md`) non
  esiste: lo slot `ADR-008` è stato riusato per `ADR-008-api-versioning.md`.
- Lo split di **Te Whakaminenga** non è avvenuto.
- L'anti-pattern **persiste in dati più recenti**: es. `batch_30_oceania.json`
  contiene `Ngati Toa / Te Ati Awa Confederation` e `Rarotongan Ariki
  Confederation` con `entity_type='confederation'`, conf 0.4.

### Perché non chiudo la Fase 2 oggi

La Fase 2 è un **progetto dati pluri-sessione** (nuovo `entity_type` nel
vocabolario + ADR + ri-audit di tutte le polities polinesiane / First Nations /
nomadi + eventuali split + chain). Forzarla in fretta rischierebbe proprio le
distorsioni che questo record vuole evitare. Va pianificata, non improvvisata.

### Mitigazione interim adottata oggi (v6.99.88)

[ETHICS-013](ETHICS-013-confidence-status-coherence.md) introduce un enforcement
a livello dato: ogni entità con `confidence_score < 0.5` (categoria in cui
ricadono molte di queste polities mal-categorizzate) ottiene automaticamente
`status='uncertain'` invece di `'confirmed'`. Non risolve il `entity_type`
sbagliato, ma **rimuove la falsa certezza** dal campo `status` — i consumer
sanno che il dato è incerto.

### Follow-up tracciato (Fase 2, non ancora schedulata)

1. Aggiungere `indigenous_society_decentralized` a `EntityStatus`/vocabolario
   entity_type + ADR dedicato.
2. Ri-audit delle polities elencate al §"Polities da ri-auditare" (Oceania,
   First Nations, nomadi) con set `status='uncertain'` finché non risolte.
3. Split di Te Whakaminenga come da Opzione B.

Questo addendum chiude il gap di **integrità del record** (un record "Adottato"
le cui azioni non erano avvenute) documentando onestamente lo stato reale,
come richiesto dalla governance etica di CLAUDE.md.
