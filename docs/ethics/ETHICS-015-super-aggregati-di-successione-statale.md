# ETHICS-015 — Super-aggregati di successione statale: decomposizione di Babilonia #171

**Data**: 2026-06-05 · **Stato**: decisione presa (deprecare #171); esecuzione del
re-homing dei riferimenti in corso/pianificata (dual-write JSON + prod).
**Decisa con**: Clirim. **Correlati**: ETHICS-001 (nomi locali), ETHICS-002 (transizioni),
[[project_chain_linkage]].

## Contesto

L'entità **#171 𒆍𒀭𒊏𒆠 ("Babilonia", −1894..−539, confidence 0.65)** è un *super-aggregato*:
una singola entità che copre **1355 anni** e collassa dinastie genuinamente distinte
(Antica/Amorita, Cassita, Caldea/Neo-babilonese) in un unico "impero babilonese continuo".

I periodi maggiori esistono già come entità precise e confermate:
- **#1039 Old Babylonian** (−1894..−1595, 0.78) — Prima Dinastia / Hammurabi
- **#811 𒌭𒀸𒋗 Cassiti / Karduniaš** (−1595..−1155, 0.85)
- *(gap −1155..−626: interregno post-cassita / dominazione assira; #817 Assiria −850..−616)*
- **#490 𒆳𒆍𒀭𒊏𒆠 Neo-Babylonian** (−626..−539, 0.78) — Caldea / Nabucodonosor

## Rischio di distorsione

Mostrare "Babilonia" come un impero unico e continuo dal 1894 a.C. al 539 a.C. **falsa la
storia**: nasconde le conquiste e le cesure (sacco ittita −1595, dominazione cassita,
conquista assira, indipendenza caldea, caduta persiana −539) e presenta come continuità
politica ciò che fu una sequenza di stati diversi con rotture violente. È esattamente il
tipo di aggregazione che il progetto rifiuta (verità prima del comfort; nessuna versione
unica e levigata della storia).

## Distinzione fondamentale (cosa NON è super-aggregato)

⚠️ Span lungo ≠ super-aggregato. I **popoli/confederazioni indigene continue** (Noongar,
Wiradjuri, chiefdom del Pacifico, Selk'nam, ecc.) hanno span enormi ma sono *correttamente*
una sola entità long-lived: splittarli imporrebbe una periodizzazione coloniale esterna
(CLAUDE.md valore #4). Si decompongono SOLO gli aggregati di **successione statale** che
conflano polities distinte (Babilonia, Sri Lanka #142, Kemet #26, Sidone #507).

## Alternative considerate

1. **Deprecare #171 + ri-home dei riferimenti** ✅ SCELTA. `status='deprecated'`; i
   riferimenti vanno riassegnati alle entità-periodo corrette; la continuità "babilonese"
   resta documentata dalla **catena #88** (Sumer→Akkad→Babilonia→Assiria→Neo-Babilonia→
   Achemenidi), che è il luogo giusto per la continuità (una *catena*, non una *entità*).
2. **Narrow #171** all'interregno −1155..−626 (Seconda Dinastia di Isin): scartata — periodo
   minore/frammentato, e richiede comunque di spostare i ref dei periodi Antico/Neo.
3. **Lasciare #171 con una nota**: scartata — il super-aggregato resterebbe sulla mappa.

## Decisione e piano di re-homing (per data)

`#171` → `status='deprecated'`. Catena **#88 seq2**: `#171` → **#1039** (Old Babylonian).
I 14 riferimenti riassegnati così:

| Riferimento | Anno | → Entità |
|---|---|---|
| Evento #448 sacco ittita (fine Antica) | −1595 | #1039 Old |
| Evento #455 Tūkulti-Ninurta conquista Babilonia cassita | −1225 | #811 Cassiti |
| Evento #213 massacro di Sennacherib | −689 | #490 Neo |
| Evento #214 caduta di Ninive | −612 | #490 Neo |
| Evento #215 distruzione del Primo Tempio (Gerusalemme) | −586 | #490 Neo |
| Evento #216 caduta di Babilonia (Ciro) | −539 | #490 Neo |
| Sovrano #61 Hammurabi (Prima Dinastia) | −1792 | #1039 Old |
| Città #15 Bābilim | (−2300..100) | #1039 Old |
| territory_change #416 fondazione Prima Dinastia | −1894 | #1039 Old |
| territory_change #417 distruzione Tempio di Gerusalemme | −586 | #490 Neo |
| territory_change #418 conquista di Ciro | −539 | #490 Neo |
| 3 sources + 3 name_variants (metadata generale "Babilonia") | — | restano su #171 deprecato (basso valore; rischio dup con #1039/#490 se spostate) |

## Esecuzione (dual-write per evitare divergenza JSON↔prod — lezione S51/ETHICS-012)

Tocca ~6 sorgenti JSON + prod SQL:
- `data/entities/batch_03_africa_mideast.json` — #171 `status='deprecated'` + 3 `territory_changes`
  annidati spostati a #1039/#490.
- `data/chains/...` (catena #88) — link #171 → #1039.
- `data/events/*.json` (4 file) — i 6 eventi: `entity_links[].entity_name_original` da "𒆍𒀭𒊏𒆠"
  al nome dell'entità-periodo (#1039 = "𒆍𒀭𒊏𒆠 (Old Babylonian)", #490 = "𒆳𒆍𒀭𒊏𒆠", #811 = "𒌭𒀸𒋗").
- sorgenti ruler (#61) e city (#15) — `entity_name`/`entity_id` → #1039.
- prod SQL: `UPDATE` di chain_links/event_entity_links/historical_rulers/historical_cities/
  territory_changes + `UPDATE geo_entities SET status='deprecated' WHERE id=171`. Transazionale.

**Verifica post-esecuzione**: #171 deprecato e fuori da ogni catena; i 6 eventi (inclusi quelli
eticamente sensibili — Gerusalemme −586, deportazione) restano visibili su entità VIVE (#1039/#490/
#811), non persi; fresh-seed riproduce lo stesso stato (zero divergenza); orfani/conteggi coerenti.
```python
# guard: nessun ref residuo a #171 a parte sources/name_variants
assert refs_to(171, except_tables=['sources','name_variants']) == 0
```

---

## Emendamento 2026-07-02 (in esecuzione) — 4 correzioni trovate verificando il piano contro prod

La verifica pre-esecuzione (snapshot completo del grafo di riferimenti su prod) ha trovato
che il piano approvato conteneva un errore storico e tre imprecisioni operative.

### 1. Evento #213 (massacro di Sennacherib, −689) → NUOVA entità, non #490

**Errore nel piano**: assegnava l'evento #213 a #490 Neo-Babilonese — che nasce nel −626.
Un re-homing lì sarebbe **anacronistico di 63 anni** (il piano avrebbe introdotto esattamente
il tipo di falsificazione che lo split vuole eliminare). Nessuna entità copre la Babilonia
−1155..−626 (periodo post-cassita / dominazione assira).

**Alternative considerate**:
- (a) #490 con nota "anacronistico" → scartata: dato consapevolmente falso, contro il valore #1.
- (b) lasciare il link sul #171 deprecato → scartata: viola il criterio di verifica di questo
  stesso record ("eventi su entità VIVE").
- (c) **creare l'entità mancante** ✅ SCELTA: **"𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)"** (kingdom,
  −1155..−626, capitale Babilonia, confidence 0.62). È la periodizzazione storiografica
  standard, non una nostra invenzione: Brinkman, *A Political History of Post-Kassite
  Babylonia, 1158–722 B.C.* (Analecta Orientalia 43, 1968); Frame, *Babylonia 689–627 B.C.:
  A Political History* (Nederlands Historisch-Archaeologisch Instituut, 1992); Beaulieu,
  *A History of Babylon, 2200 BC–AD 75* (Wiley-Blackwell, 2018) — tutte verificate reali.
  Le ethical_notes dell'entità dichiarano esplicitamente che NON è un regno indipendente
  continuo (dinastie native frammentate, poi "doppia monarchia" assira dal −729 con
  Tiglath-Pileser III; distruzione della città per mano di Sennacherib −689; guerra civile
  di Šamaš-šuma-ukin −652..−648). Il nome usa il prefisso KUR (𒆳 = "terra di", coerente con
  #490): l'entità è la Babilonia territoriale, non la sola città. Anno di inizio −1155
  approssimato (letteratura: 1158/1157/1155 secondo la cronologia adottata).
  **Cross-check ChatGPT-5.5** (log `data/chatgpt_review/20260702/ask.jsonl`): conferma la
  periodizzazione come standard e difendibile, conferma span ed entity_type con nota
  esplicita, suggerimenti (nome territoriale, vittima=città nelle note evento) integrati.
  La catena #88 NON viene modificata oltre il re-point di seq2 già approvato (la nuova
  entità non è un nodo del "trunk imperiale"; opzione documentata, non esercitata).

### 2. territory_changes #417/#418 → DELETE, non move

#490 possiede GIÀ i propri territory_changes per −586 (Giudea, pop. 50.000) e −539
(conquista di Ciro): spostarvi le copie di #171 avrebbe creato **duplicati** (doppio
conteggio della deportazione in qualsiasi aggregazione). Le righe #417/#418 vengono
eliminate (JSON + prod); il contenuto informativo resta, già più dettagliato, su #490.
Nota: le due stime di population_affected divergevano (20.000 su #171 vs 50.000 su #490)
— resta la stima di #490, coerente con la letteratura che colloca le deportazioni
complessive 586+597 a.C. in decine di migliaia; la divergenza è registrata qui.

### 3. Ruler #61 Hammurabi: aggiornare anche `entity_name_fallback`

Il piano muoveva solo `entity_id`; il campo `entity_name_fallback` ('𒆍𒀭𒊏𒆠') avrebbe
continuato a mostrare il nome del super-aggregato. Si aggiorna a '𒆍𒀭𒊏𒆠 (Old Babylonian)'.

### 4. Città Bābilim (historical_cities #15): divergenza JSON↔prod preesistente

Il JSON sorgente puntava a "Māt Akkadī" (riferimento MORTO: nessuna entità ha quel nome →
il fresh-seed lasciava entity_id NULL, mentre prod ha #171 via backfill SQL). Si riallinea
il JSON a '𒆍𒀭𒊏𒆠 (Old Babylonian)' (= #1039, come da piano). **Caveat documentato**: la
città (−2300..100) attraversa TUTTI i periodi; lo schema supporta un solo entity link —
l'associazione a #1039 privilegia il periodo della capitale di Hammurabi; il ruolo
multi-periodo resta descritto nelle ethical_notes della città stessa.
