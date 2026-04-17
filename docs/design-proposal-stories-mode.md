# Design Proposal — "AtlasPI Stories" mode

**Status**: Proposta, **NON implementata**. Scritta su richiesta user il 17 aprile 2026.
**Target**: v7.0 eventualmente, se ci convince dopo discussione.

---

## TL;DR

AtlasPI oggi è un **explorer database**: arrivi sulla mappa vuota, devi sapere cosa cercare, selezioni anno, entità, filtri. Funziona bene per chi ha già un interesse specifico ("voglio vedere l'Impero Ottomano nel 1500"). **Fallisce con l'utente curioso che non sa da dove partire**.

La proposta è aggiungere una **seconda modalità** `/app/stories` che inverte il flusso: invece di partire dalla mappa vuota, parte da **narrazioni precompilate** che l'utente clicca e vede animate.

---

## Il problema che non risolviamo oggi

Un utente arriva su https://atlaspi.cra-srl.com/app e vede:

1. Mappa mondiale con ~1000 poligoni random
2. Slider anno fisso a 1500
3. Sidebar con filtri tecnici (continent, entity_type, status)
4. Nessun "hook narrativo"

**Reazione tipica**: curiosità iniziale 5 secondi, poi bounce. Niente ti dice "wow, guarda qui". Serve background storico per apprezzare.

Il prodotto comunica "database" invece di "storie". Chi cerca database sei un API user (già coperto dalla REST). Chi arriva sull'app senza background storico **non sa perché dovrebbe rimanere**.

---

## La proposta: Stories mode (pagina parallela, non sostitutiva)

Nuova route `/stories` che mostra una **galleria di narrazioni**, ognuna:
- 1 titolo accattivante + thumbnail
- Durata stimata (es. "3 minuti")
- Difficoltà (★ principiante / ★★ intermedio / ★★★ avanzato)
- Preview testuale 1 riga

Click su una story → esperienza **cinema-like**:
- Mappa full-screen
- Audio narrator (opzionale, TTS o voice recorded)
- Timeline che avanza automaticamente
- Entity che appaiono / scompaiono / si espandono secondo lo script
- Eventi si pin-ppano alla data giusta
- Pulsanti "Pausa" / "Indietro 10s" / "Approfondisci questa entità"

### Storie proposte per v7 (MVP 8 stories)

1. **"La caduta di Roma in 60 secondi"** (3 min) — 300→500 CE, ETHICS su migrazioni barbariche vs "invasioni"
2. **"Come l'Islam cambiò il mondo"** (5 min) — 600→800 CE, dalla Mecca all'Andalusia
3. **"La frattura del 1453"** (3 min) — Costantinopoli, fine Medioevo
4. **"L'età delle Scoperte — il lato nascosto"** (7 min) — 1492→1650, ETHICS colonial violence esplicito
5. **"Imperi pre-colombiani"** (5 min) — Maya, Aztechi, Inca, NON come "civiltà perdute" ma come stati reali
6. **"Il Mongolo"** (6 min) — Genghis → Kublai, lo stato più grande della storia
7. **"L'Africa che non ti hanno insegnato"** (8 min) — Mali, Songhai, Great Zimbabwe, Mutapa
8. **"Il secolo breve"** (10 min) — 1914→1991, crolli imperi + Guerra Fredda

---

## Perché è meglio dell'attuale

| Metrica | Explorer (oggi) | Stories (proposta) |
|---|---|---|
| Time-to-wow | 30+ sec (se si sa cercare) | 10 sec (click, parte storia) |
| Bounce rate | alta per naif | bassa (hook narrativo) |
| Shareability | media (link a entity specifica) | alta (link a story = virale) |
| AI-native | alta (backend) | altissima (Ask Claude integrato nello script) |
| Educational value | alta SE sai cosa cercare | alta SEMPRE |
| SEO | medio (path tecnici) | alto (titoli narrativi indicizzabili) |

---

## Integrazione AI — il vero killer

Ogni story ha un pulsante **"Chiedi a Claude"** contestuale: durante "La caduta di Roma", click → copia prompt con:

```
Sto guardando la storia della caduta di Roma (395-476 CE) su AtlasPI.
Al momento sono a: anno 410, Sacco di Roma da parte di Alarico.

Approfondisci:
1. Perché i Visigoti si sono convertiti all'arianesimo?
2. Come la frattura tra Chiesa di Roma e Costantinopoli si aggrava in questo periodo?
3. Mostrami 2 eventi contemporanei fuori Europa (Cina, India, Africa).

Dati: https://atlaspi.cra-srl.com/v1/snapshot/year/410
```

Claude (con MCP AtlasPI integrato) **risponde usando i dati reali**. Questa è la combinazione che nessun altro ha.

---

## Scope effort

**Minimo 40 ore di lavoro focalizzato**:

- Story format JSON (~3 ore): schema per script narrativi (year, caption, map-action, highlight-entity, pause, audio-url).
- Story runner JS (~8 ore): componente che esegue lo script, coordina map state, gestisce pausa/play.
- 8 storie content (~16 ore): 2 ore per story = research + scripting + timing.
- Audio narration (~opzionale, 8 ore se TTS free, più se voice actor)
- UI gallery + thumbnails (~5 ore).

**Effort totale**: 5-7 giorni uomo (o 2-3 giorni di Claude Code + review).

---

## Rischi e contro

- **Content-heavy**: ogni story è un piccolo documentary. Non si fanno in automatico, servono decisioni editoriali.
- **ETHICS-crucial**: "La caduta di Roma" e "Età delle Scoperte" sono politiche. Serve validazione storiografica per evitare angle nazionalisti o revisionisti.
- **Mantenimento**: storie diventano stale se il dataset cambia sotto (es. correggo entity → lo script va ricontrollato).
- **Accessibility**: auto-play problematico — serve toggle, pause obbligatorio, transcript per deaf/hard-of-hearing.

---

## Perché NON lo faccio subito (stima 2 settimane)

Il livello di investimento richiesto è simile a un vero prodotto. Va fatto DOPO:
1. Il lancio pubblico vero (post Reddit + post blog + video demo)
2. Un feedback reale di utenti (abbiamo traffico?)
3. Una scelta strategica: "facciamo prodotto" vs "facciamo API + dataset"

Se la crescita post-lancio mostra che **l'audience è database-users** (sviluppatori, ricercatori) → non fare Stories, rimanere focused su API/SDK.

Se la crescita mostra **audience curiosa/educational** (studenti, content creators, scuole) → Stories è il prodotto giusto.

**La mia scommessa**: ~60% likely che Stories sia la mossa giusta post-lancio. Oggi (pre-lancio) è prematuro.

---

## Alternative più leggere che potremmo fare SUBITO

Se vogliamo l'effetto "storia" senza investire 40 ore, 3 quick wins:

### A. **Landing page "tour"** (effort 4h)
Invece della mappa diretta, `/app` parte con un overlay animato che mostra mappa mondiale che cambia da -4500 a 2024 in 30 secondi (time-lapse), poi si ferma su oggi e dice "Ora prova tu". Educational ma implementabile.

### B. **"Random interesting entity" button** (effort 1h)
Header button "🎲 Sorprendimi" che chiama `/v1/random?confidence=0.8` e apre quell'entity con un testo breve tipo "Lo sapevi che esisteva...?"

### C. **"On this day in history" widget** (effort 2h)
Banner in home che ogni giorno mostra "Oggi in MM-DD è successo: {event.name_original} ({event.year})" con link. Richiama visitatori ritornanti.

---

## Raccomandazione finale

**Opzione raccomandata**: non toccare oggi, **rivalutare dopo il lancio pubblico** quando abbiamo:
- 100+ utenti reali
- Feedback qualitativo
- Metriche bounce/engagement

Nel frattempo fare le **3 quick wins** (A + B + C) che testano l'ipotesi "narrative hook funziona" senza investimento pesante. Se A/B/C muovono le metriche → investi in Stories vero.

Se vuoi che faccia A/B/C subito, me lo dici e li implemento in v6.52 (tempo stimato: 7 ore totali).
