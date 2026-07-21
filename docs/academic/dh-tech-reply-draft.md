# Bozza risposta a @maehr — PR dh-tech/awesome-digital-humanities #76

> **Contesto**: il 18/07 il maintainer ha chiesto: *"Is there any peer reviewed
> publication that uses your project or other kind of academic validation?"*
> **Da postare da Clirim** (è il suo progetto e la sua voce). Rivedi e adatta.
>
> **Principio**: rispondere con onestà. Non abbiamo una pubblicazione peer-reviewed.
> Fingere il contrario o essere vaghi in un contesto accademico è il modo più veloce
> per perdere credibilità. La forza della risposta sta nel mostrare *rigore
> verificabile* e un percorso concreto, non nel millantare validazione.

---

## Testo proposto (inglese, da incollare come commento sulla PR)

Thanks for the thoughtful question — and the honest answer is **no: there is no
peer-reviewed publication using AtlasPI yet.** The project is three months old
(first commit April 2026), so that would be premature to claim.

What I can offer instead is verifiable methodological transparency:

- **Documented methodology** ([`docs/METHODOLOGY.md`](https://github.com/Soil911/AtlasPI/blob/main/docs/METHODOLOGY.md)):
  boundary geometry comes from three explicitly ranked tiers (Natural Earth 10m for
  modern states, `aourednik/historical-basemaps` for pre-1800 entities, deterministic
  fallback otherwise), each with its own licence and confidence band. Upstream datasets
  are credited in `NOTICE` and fetched reproducibly rather than vendored.
- **Per-record provenance**: every entity carries `sources[]` (5,089 citations across
  the dataset) and a `confidence_score` in [0,1] that is *computed and reviewable*,
  not a black-box output. Records below 0.5 are flagged `status: "uncertain"`.
- **An explicit ethics framework**: 27 documented decision records in
  [`docs/ethics/`](https://github.com/Soil911/AtlasPI/tree/main/docs/ethics) covering
  contested names (primary name in the original language, colonial names as variants),
  conquest and genocide named rather than euphemised, disputed borders carrying
  multiple versions, and confidence caps for contested territories.
- **A "Known limitations" section** that states plainly where the data is weak:
  coarse temporal granularity (53 upstream snapshots), under-representation of
  non-state and nomadic polities, and the interpretive nature of pre-colonial
  boundaries.
- **A citable artefact**: DOI [10.5281/zenodo.19581784](https://doi.org/10.5281/zenodo.19581784),
  Apache-2.0, plus a mirrored dataset on Hugging Face.

On the validation path: I intend to submit a **data paper to the Journal of Open
Humanities Data**, for which the dataset already meets the formal prerequisites
(public repository, persistent identifier, open licence). I'd genuinely welcome
methodological criticism before that — being told what's wrong now is more useful
than after publication.

I completely understand if the list's inclusion criteria require published validation;
in that case feel free to close this PR, and I'll come back once there's something
peer-reviewed to point at.

---

## Note per Clirim

- **Non promettere date**: "intendo sottomettere" è vero e verificabile; "sarà
  pubblicato a settembre" no.
- L'ultimo paragrafo (l'offerta di chiudere la PR) è deliberato: mostra che non stai
  forzando l'inclusione. Nelle liste curate accademiche questo atteggiamento aiuta,
  non danneggia.
- Se @maehr risponde con critiche metodologiche, **è un regalo**: è esattamente il
  tipo di revisione esterna che manca al progetto, e va ringraziato e recepito.
