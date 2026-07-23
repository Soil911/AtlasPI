# ETHICS-028 — Trasparenza sulla curation AI-assistita

**Data**: 2026-07-23
**Stato**: adottato
**Innesco**: il maintainer di `tmcw/awesome-geojson` ha respinto la PR di
inclusione di AtlasPI (#77) scrivendo: *"it looks like this is getting an LLM to
produce academic citations […] slop datasets are bad and not allowed on this
list"*. Nel thread precedente (#75) lo stesso maintainer chiedeva: *"Is this even
a real person submitting PRs, or is it the vibecoding bot doing the promotion too?"*

## Il rischio di distorsione

Il rischio non è l'uso dell'AI in sé: è **descrivere il processo in modo che
sembri più umano di quanto sia**. Fino a oggi la documentazione usava
l'espressione "hand-curated" per i record non geometrici. È un'espressione
fuorviante: la maggior parte dei batch di enrichment è prodotta da agenti LLM
di ricerca, con un passaggio avversariale di verifica delle fonti e supervisione
del maintainer — ma senza revisione sistematica, record per record, da parte di
storici professionisti.

Un lettore (o un revisore accademico) che scoprisse questa differenza dopo aver
letto "hand-curated" concluderebbe correttamente di essere stato ingannato — e
avrebbe ragione. Per un progetto il cui primo valore dichiarato è "verità prima
del comfort", questo è inaccettabile a prescindere dall'esito della PR.

## Alternative considerate

1. **Non dire nulla / minimizzare** ("tanto c'è la verifica avversariale").
   Respinta: è esattamente il comfort che il progetto rifiuta per i dati storici;
   non c'è motivo di accettarlo per i metadati di processo.
2. **Contestare il giudizio del maintainer** (la verifica avversariale esiste,
   le fonti sono tipizzate, ecc.). Respinta come *risposta primaria*: i fatti sono
   veri, ma il burden of proof su un dataset AI-assistito sta su di noi, non su
   chi cura una lista. La qualità si dimostra, non si rivendica.
3. **Dichiarare il processo, ovunque, con le sue mitigazioni e i suoi limiti.**
   Adottata.

## Decisione

1. `docs/METHODOLOGY.md` §2.4 dichiara esplicitamente: curation AI-assistita,
   verifica avversariale delle citazioni, supervisione del maintainer, **assenza
   di revisione sistematica da parte di storici professionisti**, canali di
   correzione pubblici.
2. Il data paper JOHD usa la stessa formulazione (la peer review deve poter
   giudicare il processo reale, non una sua versione lusinghiera).
3. L'espressione "hand-curated" non va più usata nella documentazione del
   progetto se non per i (pochi) record effettivamente scritti a mano.
4. Le submission a liste/directory di terzi non devono nascondere la natura
   AI-assistita del progetto quando il contesto la rende rilevante.

## Follow-up aperto

- Valutare un **audit umano a campione** delle citazioni (es. 50 record estratti
  casualmente, verifica bibliografica manuale, risultati pubblicati in docs/):
  è la mitigazione più credibile verso l'esterno e ad oggi non esiste.
