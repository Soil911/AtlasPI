# AtlasPI — Istruzioni per Claude Code

Questo file viene letto automaticamente da Claude Code
all'inizio di ogni sessione. Contiene i valori fondamentali,
le convenzioni di sviluppo e i riferimenti etici del progetto.

---

## Cos'è questo progetto

AtlasPI è un database geografico storico strutturato,
progettato per essere consumato da agenti AI. Fornisce coordinate,
confini GeoJSON e metadati storici di entità geopolitiche in
qualsiasi epoca — ottimizzato per essere leggibile dalle macchine.

Obiettivo: colmare il gap tra i dati geografici grezzi esistenti
(Natural Earth, OpenStreetMap, Wikidata) e il formato strutturato,
affidabile e contestualizzato di cui gli agenti AI hanno bisogno.

---

## Valori fondamentali — leggili prima di scrivere qualsiasi codice

### 1. Verità prima del comfort
I dati storici spesso riguardano conquiste, genocidi, deportazioni,
cancellazioni culturali. Questi fatti vanno rappresentati con
precisione, non edulcorati.
- Se un territorio è stato occupato con la forza → il campo
  acquisition_method lo dice esplicitamente
- Se una popolazione è stata decimata → i dati demografici
  lo mostrano con le fonti
- Se un nome geografico è stato imposto cancellando quello
  originale → entrambi i nomi sono presenti
NON omettere la verità scomoda. Renderla accessibile è lo scopo.

### 2. Nessuna versione unica della storia
- I confini contestati mostrano tutte le versioni note,
  con date e fonti
- I nomi mostrano la forma nella lingua originale +
  forme in altre lingue rilevanti
- Le dispute accademiche vengono esplicitate, non risolte
  arbitrariamente
Il database non arbitra la storia. La documenta.

### 3. Trasparenza dell'incertezza
- Ogni record ha un campo confidence_score (0.0 → 1.0)
- Ogni dato ha sources[] con citazione della fonte primaria
- I record con score < 0.5 sono marcati come status: "disputed"
Un dato incerto comunicato come tale è più onesto di un dato
certo inventato.

### 4. Nessun bias geografico o culturale dominante
- I nomi dei luoghi usano la forma nella lingua locale
  come nome primario
- Le fonti devono includere storiografia non-occidentale
  dove disponibile
- Le conquiste coloniali sono descritte anche dal punto di
  vista dei conquistati

---

## Architettura del progetto

.
├── CLAUDE.md              ← questo file
├── README.md
├── LICENSE.md
├── ROADMAP.md
├── CHANGELOG.md
├── .gitignore
├── docs/
│   ├── TEMPLATES.md
│   ├── adr/               ← Architecture Decision Records
│   └── ethics/            ← decisioni etiche documentate
├── src/
│   ├── api/               ← FastAPI endpoints
│   ├── db/                ← modelli PostgreSQL + PostGIS
│   ├── ingestion/         ← pipeline importazione dati
│   └── validation/        ← confidence scoring
├── data/
│   ├── raw/               ← dati originali non modificati
│   └── processed/         ← dati normalizzati
└── tests/

---

## Convenzioni temporali

- Gli anni usano sempre interi
- Gli anni negativi rappresentano date a.C.
- Gli intervalli temporali devono usare questa convenzione
  in modo coerente in tutto il progetto
- Se una data è incerta, l'incertezza deve essere esplicitata
  nei metadati e nel confidence_score

---

## Stack tecnologico

| Componente | Tecnologia |
|---|---|
| API | FastAPI (Python) |
| Database | PostgreSQL + PostGIS |
| Cache | Redis |
| Storage GeoJSON | Cloudflare R2 |
| Deploy | Railway (MVP) |

---

## Convenzioni di codice

- Lingua del codice: inglese
- Lingua della documentazione: italiano
- Ogni funzione che tocca dati storici sensibili deve avere
  un commento # ETHICS: che spiega la scelta
- I test devono coprire i casi limite etici, non solo tecnici

Esempio corretto:
def get_territory_name(entity_id, lang="original"):
    # ETHICS: il nome primario è sempre quello originale/locale.
    # Il nome imposto da potenze coloniali è in name_colonial,
    # non come campo principale. Vedi ETHICS-001.
    ...

---

## Roadmap e versionamento obbligatori

Lo sviluppo deve sempre seguire una roadmap chiara,
incrementale e documentata.

Regole:
- usare versioni progressive: v0.0.1, v0.0.2, v0.1.0, v0.2.0, v1.0.0
- ogni versione deve avere uno scopo chiaro e limitato
- prima di implementare nuove funzionalità, aggiornare ROADMAP.md
- ogni cambiamento rilevante deve essere riflesso in CHANGELOG.md
- evitare sviluppo disordinato o aggiunte non tracciate
- ogni milestone deve essere documentata nel repository

Se una feature non appartiene chiaramente alla versione corrente,
deve essere rinviata a una versione successiva esplicitamente pianificata.

---

## Governance etica durante lo sviluppo

Se durante lo sviluppo emerge una scelta che può alterare,
semplificare o distorcere la rappresentazione storica, Claude
non deve procedere in silenzio.

In questi casi deve:
1. aprire o aggiornare un record in docs/ethics/
2. descrivere il rischio di distorsione
3. documentare le alternative considerate
4. spiegare la scelta adottata
5. solo dopo procedere con l'implementazione

Regola pratica:
se una decisione tecnica ha impatto sulla verità storica,
sulla rappresentazione di popoli, confini, nomi o conquiste,
va trattata come decisione etica documentata.

---

## Modello di distribuzione

AtlasPI segue un modello open core.

Principi:
- il repository è pubblico
- il core del progetto è open source
- la documentazione architetturale ed etica è pubblica
- gli asset premium possono includere dataset curati, servizi hosted,
  funzionalità avanzate, accesso API ad alto volume e componenti enterprise
- codice open e componenti premium devono restare chiaramente separati

Prima di pubblicare qualunque componente:
- definire la licenza del core
- verificare la compatibilità delle licenze dei dataset
- distinguere chiaramente ciò che è open da ciò che è premium

---

## Gestione operativa del repository

AtlasPI è progettato per essere sviluppato come repository pubblico su GitHub.

Claude deve:
- mantenere il repository ordinato e documentato
- creare e aggiornare roadmap, changelog e documentazione architetturale
- strutturare il lavoro in milestone e versioni progressive
- preparare il progetto per pubblicazione open core
- evitare codice non documentato o non coerente con i principi del progetto

---

## Regola d'oro

Prima di scrivere codice chiedi: "questo dato, in questo formato,
potrebbe essere usato per distorcere la comprensione storica?"
Se la risposta è sì, apri un ETHICS record prima di procedere.
