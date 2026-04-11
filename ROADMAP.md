# Roadmap AtlasPI

## Principi di roadmap

- sviluppo incrementale
- versionamento esplicito
- scope limitato per ogni release
- prima la base etica e architetturale, poi il codice applicativo
- nessuna feature fuori roadmap senza aggiornamento esplicito di questo file

## Versioni previste

### v0.0.1
Fondazione del progetto:
- CLAUDE.md
- README.md
- LICENSE.md
- ROADMAP.md
- CHANGELOG.md
- docs/adr/
- docs/ethics/
- docs/TEMPLATES.md
- struttura repository iniziale

### v0.0.2
Bootstrap tecnico minimo:
- pyproject o requirements
- configurazione base FastAPI
- struttura iniziale src/
- struttura iniziale tests/
- .gitignore
- convenzioni base di progetto

### v0.1.0
Primo scheletro applicativo:
- endpoint healthcheck
- configurazione database
- modello iniziale entità geografica
- schema risposta API iniziale
- prime validazioni di struttura

### v0.2.0
Primo flusso dati:
- pipeline importazione dataset demo
- normalizzazione minima
- primo record interrogabile via API
- primi test tecnici ed etici

### v0.3.0
Primo nucleo storico:
- supporto year nelle query
- supporto name_original e name_variants
- supporto confidence_score
- supporto sources

### v0.4.0
Primo nucleo geopolitico:
- boundary_geojson
- capital
- territory_changes
- status confirmed|uncertain|disputed

### v0.5.0
Primo dataset demo coerente:
- piccola collezione di entità storiche
- validazione documentata
- note etiche nei casi sensibili

### v0.6.0
Preparazione alpha pubblica:
- documentazione migliorata
- quality pass
- review etica
- review architetturale
- definizione licenza core

### v1.0.0
Prima release pubblica stabile del core.

---

## Roadmap post-v4.5 — Verso il prodotto completo

### v4.6 — UX Polish & Deep Linking
Come utente: "Ho trovato un'entità interessante, voglio condividerla" / "Voglio usare la tastiera"
- Sezioni dettaglio collassabili (click per espandere/chiudere)
- Scorciatoie tastiera (Esc chiude dettaglio, ↑↓ naviga risultati)
- URL state management (?entity=5&year=1500&lang=en)
- Tooltip mappa arricchiti (tipo, confidence bar, periodo)

### v4.7 — Filtro Continente & Contemporanei in UI
Come utente: "Studio la storia africana, mostrami solo l'Africa" / "Chi c'era ai tempi dei Romani?"
- Filtro per continente/regione
- Tab contemporanei nel pannello dettaglio
- Icone tipo entità nei risultati e sulla mappa
- Mini-preview al hover sulla mappa

### v4.8 — Tema & Raffinamento Visivo
Come utente: "Presento questo a lezione, serve il light mode" / "Serve più contrasto"
- Toggle dark/light mode con localStorage
- Contrasto colori migliorato (WCAG AAA dove possibile)
- Label mappa scalati per zoom
- Print stylesheet

### v5.0 — Timeline Interattiva & Confronto (major)
Come storico: "Voglio vedere la storia scorrere" / "Confronta Impero Romano e Ottomano"
- Timeline clickabile (click su barra → dettaglio)
- Endpoint /v1/compare/{id1}/{id2}
- Modalità confronto in UI (fianco a fianco)
- Playback temporale (animazione attraverso gli anni)

### v5.1 — Condivisione & Embedding
Come blogger/docente: "Voglio incorporare questa mappa nel mio sito"
- Pulsante condivisione (copia URL con stato)
- Modalità embed (/embed?year=1500 — UI minimale)
- Permalink per entità
- Meta OG dinamici per entità

### v5.2 — Developer Experience
Come sviluppatore AI: "Dammi esempi di come usare l'API"
- Endpoint /v1/random (entità casuale)
- Snippets codice nelle docs OpenAPI (Python, JS, curl)
- Messaggi errore migliorati
- API changelog endpoint

### v5.3 — Espansione Dati
Come istituzione: "40 entità non bastano, serve più copertura"
- Espansione a 55+ entità
- Migliore diversità geografica (Oceania, Sudest Asiatico, America precolombiana)
- Più cambi territoriali e fonti per entità esistenti

### v5.4 — Hardening Produzione
Come CTO: "È pronto per la produzione? Posso fidarmi?"
- 130+ test (nuovi edge case, integration, a11y)
- Ottimizzazione performance
- Security hardening
- Documentazione finale
- Rilancio server
