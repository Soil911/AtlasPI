# ETHICS-014 — Classificazione dei poligoni condivisi (no "falso bug" su stati successivi e nomi-varianti)

**Status**: Adottato (v6.99.96 — 2026-06-03)
**Principio**: CLAUDE.md #1 (Verità prima del comfort), #2 (Nessuna versione
unica della storia), #3 (Trasparenza dell'incertezza)
**Ref**: AI Co-Founder suggestion #77 ("Align geometric analyzer with auto-fix
+ handle shared-polygon duplicates"); [ETHICS-004](ETHICS-004-confini-generati-approssimativi.md)
(confini generati approssimativi), [ETHICS-006](ETHICS-006-natural-earth-fuzzy-displacement.md)
(fuzzy displacement).

## Contesto

L'analizzatore geometrico (`analyze_geometric_bugs`) segnalava come bug ogni
gruppo di entità che condividono lo stesso `boundary_geojson` byte-per-byte,
nella convinzione (vera nell'era v6.30) che un poligono condiviso = errore di
fuzzy-match in cui una seconda entità eredita il poligono nazionale di un'altra.

La suggestion #77 chiedeva di estendere il fixer per "resettare l'entità
secondaria a un cerchio basato sulla capitale" per 6 gruppi (13 entità).

**Verifica in produzione (2026-06-03)**: dei 13 ID citati nella suggestion solo
**1** coppia condivide ancora un poligono (1032 Daju / 1033 Tunjur); gli altri
11 hanno già confini distinti, corretti durante le wave di enrichment
successive alla creazione della suggestion (2026-05-24). Allargando l'analisi,
i gruppi a poligono condiviso oggi sono **23**, e quasi tutti sono **legittimi**:

- **Stesso popolo, due traslitterazioni/lingue**: 218 ᏣᎳᎩ / 859 Tsalagi
  (Cherokee); 197 Muyska / 860 Muisca; 296 吐谷浑 / 465 吐谷渾 (Tuyuhun);
  491 ዛግዌ / 854 Zagwe; 145 / 605 Zunghar; 219 Mvskoke / 726 Muscogee.
- **Stati successivi sullo stesso territorio/capitale** (stesso cerchio
  generato dalla stessa capitale): 251 Iran Pahlavi / 252 Rep. Islamica
  (Teheran); 229 Reich / 244 Weimar (Berlino); 878 Đinh / 879 Lê (Hoa Lư);
  271 Regno di Giuda / 511 Regno di Gerusalemme; 444 Heian / 446 Muromachi
  (Kyōto); 489 Hegiaz / 500 hashemita.

La premessa della suggestion (condiviso ⇒ errore) **non è più valida**. Per
1032/1033 le due entità hanno **capitale identica** (14.14, 23.7): rigenerare
un "cerchio sulla capitale" per la secondaria produrrebbe un cerchio
**identico** — zero miglioramento — distruggendo al contempo una geometria
`historical_approximation` curata manualmente (entrambe in `MANUALLY_CURATED_IDS`).

## Rischio di distorsione

Procedere alla lettera con la suggestion avrebbe:

1. **Cancellato confini storicamente corretti**: due stati che realmente
   occuparono lo stesso territorio in epoche diverse condividono legittimamente
   un'approssimazione. Forzare confini distinti dove le fonti non li
   supportano è *inventare* dati — l'opposto del principio #3.
2. **Appiattito la rappresentazione di nomi-varianti**: trattare ᏣᎳᎩ e Tsalagi
   come "duplicato da correggere" nega che siano lo stesso popolo (principio #2).
3. **Generato rumore perpetuo**: 34 entità segnalate, 0 risolte dal fixer →
   ogni run ripropone lavoro non azionabile.

## Alternative considerate

1. **Eseguire la suggestion alla lettera** (reset secondarie a cerchio
   capitale) → **rifiutato**: ineffrattivo (capitali condivise ⇒ cerchi
   identici) e distruttivo (cancella geometrie curate); viola #2 e #3.
2. **Differenziare a mano i confini di Daju/Tunjur** → rinviato: è lavoro di
   *enrichment* con fonti, non un auto-fix. Senza fonti dedicate, un confine
   distinto sarebbe inventato. Annotato come follow-up, non eseguito ora.
3. **Riclassificare i poligoni condivisi nell'analizzatore** (scelto): un
   gruppo condiviso è *azionabile* solo se ≥1 membro NON è curato e NON ha una
   sorgente di piccola-approssimazione benigna (`approximate_circle`,
   `historical_approximation`, `historical_map`, `manual`, `aourednik_curated`,
   `approximate_generated`). Le condivisioni benigne (co-locazione di stati
   successivi, traslitterazioni alternative) vengono **soppresse**; restano
   segnalate solo le condivisioni con sorgente a eredità grezza (poligono
   nazionale Natural-Earth/aourednik condiviso tra proprietari) — gli unici
   bug reali, già coperti dai reset oversize/wrong-polygon del fixer.

## Decisione

- `analyze_geometric_bugs` allineato al fixer (v6.99.96):
  - salta `MANUALLY_CURATED_IDS` + `CURATED_BOUNDARY_SOURCES`;
  - soglia oversize = ceiling × 3.0 (2.5 per `STRICT_TYPES`), identica al fixer,
    al posto del vecchio 1.5× (la banda 1.5×→3.0× segnalava senza mai correggere);
  - area in km² via proiezione **equiareale geodetica** (pyproj/WGS84), che
    elimina il bias polare del vecchio calcolo `gradi² × 111²` (Russia stimata
    35.5M km² vs ~17M reali);
  - condivisioni di poligono riclassificate come sopra.
- Il fixer **non** esegue reset ciechi su poligoni condivisi: la logica resta
  documentata nell'analizzatore (nota nel docstring del fixer).
- Daju (1032) / Tunjur (1033): la condivisione è storicamente difendibile (due
  sultanati predecessori del Darfur, stessa regione e capitale nei nostri dati);
  un confine distinto richiede fonti dedicate → **follow-up di enrichment**, non
  fabbricato qui.
- Test invariante: `tests/test_v6996_geometric_alignment.py` verifica
  soppressione delle condivisioni benigne, skip dei curati, calcolo equiareale,
  e che le condivisioni a eredità grezza restino segnalate.
