# Data paper — bozza per Journal of Open Humanities Data (JOHD)

> **Stato**: BOZZA da rivedere e firmare da Clirim Ramadani.
> **Target**: [Journal of Open Humanities Data](https://openhumanitiesdata.metajnl.com/),
> formato *Data Paper*: 1.000–1.500 parole, peer-reviewed.
> **Prerequisiti formali già soddisfatti**: repository pubblico ✓, identificatore
> persistente (DOI Zenodo 10.5281/zenodo.19581784) ✓, licenza aperta (Apache-2.0) ✓.
> **Costo**: APC £1.070 — **chiedere l'esenzione in fase di invio** (progetto
> indipendente non finanziato). Se negata: pubblicare come preprint su Zenodo.
>
> ⚠️ **Conteggio attuale: 766 parole** (abstract → fine sezione 4, tabelle escluse).
> JOHD chiede **1.000–1.500**: mancano ~250-400 parole. Dove espandere, in ordine
> di utilità per un revisore:
> 1. **Sezione 2 (Method)** — descrivere il *processo di revisione* dei record:
>    come nascono le voci, cosa fa scattare una revisione della confidence, come si
>    risolve un disaccordo fra fonti. È la domanda che un revisore farà per prima.
> 2. **Sezione 4 (Reuse)** — un esempio concreto e citabile: una query reale
>    (es. `/v1/snapshot/1400`) con la risposta e cosa se ne ricava.
> 3. **Sezione 1 (Context)** — una frase su lavori correlati (Natural Earth,
>    historical-basemaps, Wikidata, Pleiades) con citazione formale: JOHD si aspetta
>    riferimenti bibliografici, che qui mancano del tutto.
>
> **Manca anche una sezione References** — obbligatoria: vanno citati formalmente
> almeno Natural Earth, aourednik/historical-basemaps e le fonti metodologiche.

---

**Title:** AtlasPI: An Agent-Readable Dataset of Historical Geopolitical Entities
with Explicit Provenance and Ethical Annotation (4500 BCE – 2024 CE)

**Author:** Clirim Ramadani (CRA S.r.l.)

---

## Abstract

AtlasPI is an open dataset of 1,015 historical geopolitical entities spanning 4500 BCE
to 2024 CE, each with GeoJSON boundary geometry, names recorded in their original
language, academic source citations, and an explicit per-record confidence score. It
further includes 643 dated historical events, 105 dynastic succession chains, 252
historical cities, 41 trade routes, 1,249 archaeological sites and 55 historical
periods. The dataset is distributed through a public REST API and a Model Context
Protocol (MCP) server, making it directly consumable by AI agents as well as by
conventional GIS and digital-humanities workflows. Its distinguishing feature is not
scale but *epistemic transparency*: provenance, uncertainty and contested
interpretations are first-class, machine-readable fields rather than prose caveats.

## (1) Context and motivation

Researchers and, increasingly, automated systems asking questions such as *"which
polities existed in the Balkans in 1400?"* face a fragmented landscape. Natural Earth
provides authoritative modern boundaries but no historical depth; `historical-basemaps`
provides historical world snapshots but no entity-level metadata; Wikidata provides
entity metadata but sparse and inconsistent geometry. None was designed to be
consumed programmatically as a coherent historical-geographic corpus.

A second gap is epistemic. Historical boundary data is inherently uncertain and often
politically contested, yet most datasets encode a single authoritative geometry with
no machine-readable signal of confidence or dispute. When such data is consumed by
automated systems — which increasingly mediate public access to historical knowledge —
that flattening is silently propagated.

AtlasPI addresses both gaps: it unifies entity metadata with geometry, and it makes
uncertainty and contestation explicit and queryable.

## (2) Method

**Entity records.** Entity metadata (name, type, temporal range, capital, sources,
territorial changes) is hand-curated. Each entity requires at least one academic
citation; the dataset currently carries 5,089 citations and 2,880 documented
territorial changes.

**Boundary geometry** is derived through a three-tier pipeline, ranked by trust and
recorded per record in a `boundary_source` field:

| Tier | Source | Applies to | Licence | Confidence band |
|---|---|---|---|---|
| 1 | Natural Earth 10m | modern states | CC0 | 0.75–0.95 |
| 2 | `aourednik/historical-basemaps` (53 snapshots) | pre-1800 entities | CC BY 4.0 | 0.45–0.80 |
| 3 | Deterministic generated polygon | unmatched entities | — | 0.40 |

Tier-2 matches additionally record the matched feature name, the snapshot year used,
and a precision grade, so that any polygon can be traced back to its upstream feature.
Upstream datasets are not vendored; they are fetched reproducibly by a documented
script, and credited in `NOTICE`.

**Confidence scoring.** Every entity carries `confidence_score ∈ [0,1]`, derived from
source tier, boundary tier, date precision and manual review. The mean across the
dataset is 0.689. Records below 0.5 are automatically flagged `status: "uncertain"`;
entities over contested territory are capped at 0.7 and flagged `status: "disputed"`
(32 records). The score is computed and auditable, not a black-box model output.

**Ethical annotation.** Twenty-seven documented decision records govern
representational choices. The four operative principles are: (i) the primary name is
the endonym — `Imperium Romanum`, `ᠶᠡᠬᠡ ᠮᠣᠩᠭᠣᠯ ᠤᠯᠤᠰ` — with colonial and exonymic
forms preserved as variants rather than as the canonical label; (ii) conquest,
displacement and genocide are named explicitly in event and territorial-change
records rather than euphemised; (iii) contested borders carry multiple documented
versions with sources, rather than an arbitrated single truth; (iv) uncertainty is
declared rather than smoothed. Each decision, including rejected alternatives, is
recorded in a versioned ethics register.

## (3) Dataset description

- **Object name:** AtlasPI Historical Geography Dataset
- **Format:** JSON and GeoJSON (REST API); JSONL (archival export)
- **Temporal coverage:** 4500 BCE – 2024 CE · **Spatial coverage:** worldwide
- **Language:** entity names in original languages and scripts; metadata and
  documentation in English
- **Licence:** Apache-2.0 · **Repository:** <https://github.com/Soil911/AtlasPI>
- **Persistent identifier:** <https://doi.org/10.5281/zenodo.19581784>
- **Mirror:** Hugging Face `clirim911/atlaspi-historical-geography`
- **Live access:** <https://atlaspi.it> — no authentication, CORS-enabled
- **Publication date:** 2026

## (4) Reuse potential

The dataset supports at least four reuse scenarios. *Historical GIS*: entity
geometries can be joined to external datasets by year and place for spatial analysis.
*Teaching*: the interactive map and the year-slider interface make boundary change
legible without GIS expertise. *Machine consumption*: the MCP server exposes 39 typed
tools, allowing AI systems to answer historical-geographic questions against cited
data rather than parametric memory — with the confidence and dispute flags available
to the consuming system. *Methodological research*: because provenance and
uncertainty are explicit, the corpus is itself an object of study for work on
epistemic transparency in cultural-heritage data.

**Known limitations** are documented alongside the data and bear restating.
Temporal granularity is coarse: 53 upstream snapshots mean that periods of rapid
change are approximated to the nearest available timestamp. Non-state polities —
nomadic confederations, khanates, ecclesiastical territories — fit polygon models
poorly and are disproportionately represented by generated geometry. Pre-colonial and
indigenous boundaries are necessarily interpretive: where sources disagree, the
dataset follows the most-cited convention and flags the record as disputed rather
than presenting a settled boundary. Capital coordinates are single point-stamps and
do not capture capitals that moved. These are not incidental caveats but structural
properties of the domain, and they are encoded in the data rather than only in prose.

---

## Note operative per la sottomissione

1. **Esenzione APC**: JOHD accetta richieste di waiver al momento dell'invio. Motivare
   con: progetto indipendente, nessun finanziamento istituzionale, dataset interamente
   aperto.
2. **Rivedere i numeri** appena prima dell'invio (crescono): `curl https://atlaspi.it/v1/stats`.
   La cifra "1.015 entità" è quella *interrogabile*; `/health` ne riporta 1.061
   perché include i record deprecati (tombstone). **Usare 1.015** ed essere pronti a
   spiegare la differenza se un revisore la nota.
3. **Verificare il template** ufficiale della rivista prima dell'invio: la struttura
   qui segue le loro sezioni, ma il template può cambiare.
4. **Se il waiver viene negato**: pubblicare questo stesso testo come preprint su
   Zenodo (costo zero, subito citabile) e riproporlo a una sede senza APC.
