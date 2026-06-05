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
