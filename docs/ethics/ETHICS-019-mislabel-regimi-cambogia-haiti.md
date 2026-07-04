# ETHICS-019 — Mislabel di regime: #240 Kampuchea Democratica e #534 Primo Impero di Haiti

**Data**: 2026-07-04
**Versione**: v6.99.118
**Stato**: implementato
**Origine**: flag ETHICS-017 §8 (audit catene Class-1, batch_35/36)
**Cross-check**: ChatGPT gpt-5.5 (log in `data/chatgpt_review/20260704/ask.jsonl`) — AGREE su entrambe le decisioni

---

## Caso 1 — Entità #240: nome della Repubblica Khmer su un record della Kampuchea Democratica

### Rischio di distorsione

Il record #240 aveva `name_original = 'សាធារណរដ្ឋខ្មែរ'` (*Sathéaranakrâth Khmêr*,
"Repubblica Khmer" — il regime di Lon Nol, 1970-1975) ma **tutto il resto del
record descrive la Kampuchea Democratica** (Khmer rossi, 1975-1979):

- `year_start=1975, year_end=1979`, capitale Phnom Penh;
- `ethical_notes` sul genocidio cambogiano (1.5-2M morti, S-21, Killing Fields);
- link all'evento #101 (genocidio cambogiano, 1975-1979);
- name variants già corrette: `Democratic Kampuchea` (en), `កម្ពុជាប្រជាធិបតេយ្យ` (km);
- `wikidata_qid = Q1054184` = Khmer Republic (sbagliato, coerente col solo nome).

La distorsione è grave in entrambe le direzioni: **attribuiva implicitamente il
genocidio al regime sbagliato** (la Repubblica Khmer, che ne fu la vittima
militare) e **anonimizzava il regime responsabile** (la Kampuchea Democratica
compariva solo come variante). Origine probabile: il bootstrap Wikidata v6.69
fece match del nome (score 0.95) senza pesare la contraddizione con gli anni.

### Alternative considerate

1. **(a) Rename → Kampuchea Democratica** (scelta): allinea il nome all'unica
   lettura coerente con anni, evento, note etiche, varianti e territory_changes.
2. **(b) Shift anni → 1970-75** tenendo il nome Khmer Republic: avrebbe
   orfanizzato l'evento genocidio (1975-79) e reso false le note etiche e i
   territory_changes (conquista di Phnom Penh 1975, invasione vietnamita 1979).
   Scartata.
3. **(c) Creare entrambe le entità ora**: la Repubblica Khmer (1970-75) merita
   un record proprio, ma è *enrichment additivo*, non parte del fix del
   mislabel. Rinviata alla coda M1 (nota sotto).

### Scelta adottata

- `name_original`: `សាធារណរដ្ឋខ្មែរ` → **`កម្ពុជាប្រជាធិបតេយ្យ`** (*Kampuchea
  Prâcheathippadey*, nome ufficiale khmer della Kampuchea Democratica).
- `wikidata_qid`: `Q1054184` → **`Q330988`** (Democratic Kampuchea).
- La variante km ora ridondante col primario è riconvertita nella
  **romanizzazione** `Kampuchea Prâcheathippadey` (lang `km-Latn`, precedente:
  `ar-Latn` in batch_11).
- Il nome "Repubblica Khmer" **NON resta come variante**: è uno stato diverso,
  non una denominazione alternativa della Kampuchea Democratica (conferma
  cross-check).
- `year_start=1975` mantenuto con la **convenzione del periodo di regime**
  (controllo khmer rosso dal 17 aprile 1975); nota esplicita aggiunta alle
  `ethical_notes`: il nome di stato fu proclamato formalmente con la
  costituzione del **gennaio 1976** (raccomandazione del cross-check per
  evitare che si inferisca l'esistenza formale del nome dal 1975).
- Nota dell'event-link #109 aggiornata (non parla più di "predecessor Khmer
  Republic" come spiegazione del mismatch).

### Follow-up (coda M1)

Creare l'entità **Repubblica Khmer (1970-1975)** come record proprio, con
`wikidata_qid=Q1054184`, per colmare il gap 1970-75 fra #256 (Regno di
Cambogia, 1953-) e #240.

---

## Caso 2 — Entità #534: il Primo Impero di Haiti etichettato "repubblica"

### Rischio di distorsione

Il record #534 (1804-1806, Dessalines) aveva `name_original = 'Repiblik
Dayiti'`: **errato due volte**. (1) Lo stato di Dessalines dal 22 settembre
1804 era un **impero** (incoronazione come Giacomo I, costituzione imperiale
del 20 maggio 1805: «Empire d'Haïti», grafia d'epoca *Empire d'Hayti*); la
parola "Repiblik" nega la forma istituzionale reale. (2) La grafia era un
ibrido kreyòl non attestato. Inoltre `entity_type='kingdom'` era impreciso.

### Alternative considerate

1. **Primario kreyòl `Anpi an Ayiti`** (scelta): forma **attestata** nel kreyòl
   moderno per il Primo Impero; mantiene il principio ETHICS-001 (lingua
   locale/vernacolare primaria) e il precedente del record gemello #209 (ht).
2. **Primario francese `Empire d'Haïti`**: più fedele ai documenti d'epoca (la
   costituzione del 1805 è in francese; l'ortografia kreyòl è novecentesca),
   ma il francese era la lingua scritta dell'élite, non il vernacolo della
   popolazione appena uscita dalla schiavitù. Il cross-check la giudica
   "defensible" ma concorda che, data la policy ETHICS-001 e il precedente
   #209, il kreyòl attestato è preferibile. Resta come **variante** (fr).

### Scelta adottata

- `name_original`: `Repiblik Dayiti` → **`Anpi an Ayiti`** (ht, attestato;
  esplicitato nelle note che l'ortografia kreyòl è moderna, non del 1805).
- `entity_type`: `kingdom` → **`empire`**.
- Nuova variante: **`Empire d'Haïti`** (fr, 1804-1806, nome ufficiale della
  costituzione imperiale del 1805, grafia d'epoca *Empire d'Hayti*).
- Varianti esistenti conservate: `Empire of Haiti (Dessalines)` (en), `Hayti`
  (en, grafia d'epoca), `Ayiti` (tnq, nome taíno).

### Non affrontato qui

- **#209 `Républik Ayiti`** resta un ibrido grafico (kreyòl corretto:
  *Repiblik d Ayiti*) — rename separato in coda M4 (17 rename nativi), come da
  ETHICS-017 §8.

---

## Dual-write

| Dove | #240 | #534 |
|---|---|---|
| Entità JSON | `data/entities/batch_05_modern.json` | `data/entities/batch_15_americas_caribbean.json` |
| Catene JSON | `data/chains/batch_35_class1_asia_pacific.json` (flag narrativo) | `data/chains/batch_36_class1_atlantic_europe.json` (link + flag) |
| Eventi JSON | `data/events/batch_04_modern.json` (link + nota) | `data/events/batch_07_americas.json` (link) |
| Rulers JSON | — | `data/rulers/batch_01_global_expansion.json` (Toussaint) |
| Wikidata | `data/wikidata/v669_qid_high_confidence.json` + `prod_qid_state.txt` | — |
| Prod SQL | `scripts/sql_ethics019_mislabel_fix.sql` (transazionale, backup pg_dump prima) | idem |

Gli export storici in `data/fixes/` (snapshot di prod a una data) NON sono
stati modificati: documentano lo stato passato.
