# AtlasPI: An Agent-Readable Dataset of Historical Geopolitical Entities with Explicit Provenance and Ethical Annotation (4500 BCE – 2024 CE)

**Author:** Clirim Ramadani
**Affiliation:** CRA S.r.l., Italy
**ORCID:** *[da inserire — vedi note]*
**Corresponding author:** clirim.ramadani1@gmail.com

---

## Abstract

AtlasPI is an open dataset of 1,015 historical geopolitical entities spanning 4500 BCE
to 2024 CE, each with GeoJSON boundary geometry, names recorded in their original
language, academic source citations, and an explicit per-record confidence score. It
further includes 643 dated historical events, 105 dynastic succession chains, 252
historical cities, 41 trade routes, 1,249 archaeological sites and 55 historical
periods. The dataset is distributed through a public REST API and a Model Context
Protocol server, making it directly consumable by automated agents as well as by
conventional GIS and digital-humanities workflows. Its distinguishing feature is not
scale but epistemic transparency: provenance, uncertainty and contested
interpretations are first-class, machine-readable fields rather than prose caveats.

**Keywords:** historical geography; historical GIS; open data; provenance;
uncertainty; digital humanities; GeoJSON; machine-readable cultural heritage

---

## (1) Context

Researchers — and, increasingly, automated systems — asking questions such as *"which
polities existed in the Balkans in 1400?"* face a fragmented landscape. Natural Earth
(Kelso & Patterson, 2010) provides authoritative modern boundaries but no historical
depth. The *historical-basemaps* collection (Ourednik, 2021) provides historical world
snapshots but no entity-level metadata. Wikidata (Vrandečić & Krötzsch, 2014) provides
entity metadata but sparse and inconsistent geometry. Gazetteers such as Pleiades
(Bagnall et al., 2006–) offer rigorous place-level scholarship for antiquity but do
not model polity extent over time. None of these was designed to be consumed
programmatically as a coherent historical-geographic corpus.

A second gap is epistemic. Historical boundary data is inherently uncertain and often
politically contested, yet most datasets encode a single authoritative geometry with
no machine-readable signal of confidence or dispute. Critical scholarship in the
digital humanities has long argued that data is never raw and that classification
choices carry political weight (Gitelman, 2013; Bowker & Star, 1999). When historical
data is consumed by automated systems — which increasingly mediate public access to
historical knowledge — that flattening is silently propagated at scale, and the
provenance that would allow a reader to contest it is lost.

AtlasPI addresses both gaps: it unifies entity metadata with geometry, and it makes
uncertainty and contestation explicit, queryable fields.

## (2) Method

**Entity records.** Entity metadata (name, type, temporal range, capital, sources,
territorial changes) is hand-curated in versioned JSON. Each entity requires at least
one academic citation; the dataset currently carries 5,089 citations and 2,880
documented territorial changes.

**Boundary geometry** is derived through a three-tier pipeline, ranked by trust and
recorded per record in a `boundary_source` field:

| Tier | Source | Applies to | Licence | Confidence band |
|---|---|---|---|---|
| 1 | Natural Earth 10m | modern states | CC0 | 0.75–0.95 |
| 2 | *historical-basemaps* (53 snapshots) | pre-1800 entities | CC BY 4.0 | 0.45–0.80 |
| 3 | Deterministic generated polygon | unmatched entities | — | 0.40 |

Tier-2 matches additionally record the matched feature name, the snapshot year used
and a precision grade, so that any polygon can be traced back to its upstream feature.
Upstream datasets are not vendored; they are fetched reproducibly by a documented
script and credited in the repository's `NOTICE` file.

**Curation and review workflow.** Records enter the dataset in one of two ways: manual
curation against cited literature, or programmatic import followed by review. Every
import is dual-written to versioned JSON and to the production database, so that the
canonical files and the served data can be reconciled and any divergence detected. A
continuous-integration suite of 1,293 tests enforces structural invariants —
referential integrity of succession chains, exclusion of deprecated records from
public endpoints, and coherence between confidence and status fields. Geometric
regressions are additionally caught by automated checks for implausible polygons, such
as boundaries crossing the antimeridian or exceeding a plausible area for the declared
entity type: a class of error that metadata validation alone does not surface.
Confidence values are revisited when new sources are added; downgrades are as common
as upgrades, and both are recorded in the version history.

**Confidence scoring.** Every entity carries `confidence_score ∈ [0,1]`, derived from
source tier, boundary tier, date precision and manual review. The mean across the
dataset is 0.689. Records below 0.5 are automatically flagged `status: "uncertain"`;
entities over contested territory are capped at 0.7 and flagged `status: "disputed"`
(32 records). The score is computed and auditable, not a black-box model output, and
the rule that produces each flag is documented rather than implicit.

**Ethical annotation.** Twenty-seven documented decision records govern
representational choices. Four operative principles apply: (i) the primary name is the
endonym — *Imperium Romanum*, ᠶᠡᠬᠡ ᠮᠣᠩᠭᠣᠯ ᠤᠯᠤᠰ — with colonial and exonymic forms
preserved as variants rather than as the canonical label; (ii) conquest, displacement
and genocide are named explicitly in event and territorial-change records rather than
euphemised; (iii) contested borders carry multiple documented versions with sources,
rather than an arbitrated single truth; (iv) uncertainty is declared rather than
smoothed. Each decision, including rejected alternatives, is recorded in a versioned
register, so that a reuser can audit not only the data but the reasoning that shaped it.

## (3) Dataset description

- **Object name:** AtlasPI Historical Geography Dataset
- **Format:** JSON and GeoJSON (REST API); JSONL (archival export)
- **Temporal coverage:** 4500 BCE – 2024 CE · **Spatial coverage:** worldwide
- **Language:** entity names in original languages and scripts; metadata and
  documentation in English
- **Licence:** Apache-2.0 · **Repository:** https://github.com/Soil911/AtlasPI
- **Persistent identifier:** https://doi.org/10.5281/zenodo.19581784
- **Mirror:** Hugging Face, `clirim911/atlaspi-historical-geography`
- **Live access:** https://atlaspi.it — no authentication, CORS-enabled
- **Publication date:** 2026

## (4) Reuse potential

The dataset supports at least four reuse scenarios. In *historical GIS*, entity
geometries can be joined to external datasets by year and place for spatial analysis,
with the confidence field available as a filter or a weight. In *teaching*, the
interactive map and year-slider interface make boundary change legible without GIS
expertise, while the disputed-status flags provide a natural entry point for
discussing contested historiography. For *machine consumption*, a Model Context
Protocol server exposes 39 typed tools, allowing automated systems to answer
historical-geographic questions against cited data rather than parametric memory —
with confidence and dispute flags available to the consuming system, so that
uncertainty can be surfaced to an end user rather than silently discarded. Finally,
because provenance and uncertainty are explicit, the corpus is itself an object of
study for *methodological research* on epistemic transparency in cultural-heritage
data.

**Known limitations** are documented alongside the data and bear restating. Temporal
granularity is coarse: 53 upstream snapshots mean that periods of rapid change are
approximated to the nearest available timestamp. Non-state polities — nomadic
confederations, khanates, ecclesiastical territories — fit polygon models poorly and
are disproportionately represented by generated geometry. Pre-colonial and indigenous
boundaries are necessarily interpretive: where sources disagree, the dataset follows
the most-cited convention and flags the record as disputed rather than presenting a
settled boundary. Capital coordinates are single point-stamps and do not capture
capitals that moved during an entity's lifespan. These are not incidental caveats but
structural properties of the domain, and they are encoded in the data rather than only
in prose.

---

## Competing interests

The author is the founder of CRA S.r.l., the company that develops and hosts AtlasPI.
The dataset and the software described here are released under the Apache-2.0 licence
and are freely available without authentication. The project follows an open-core
model: while the dataset and API described in this paper are open, the author may in
future offer commercial services (for example hosted high-volume access or curated
enterprise datasets) built on the same foundation. No such commercial component
exists at the time of writing, and none is required to access the data described here.

## Funding statement

This work received no external or institutional funding.

## Acknowledgements

AtlasPI builds on two upstream open datasets whose maintainers made this work
possible: Natural Earth, released into the public domain, and the
*historical-basemaps* collection by André Ourednik, released under CC BY 4.0. Both
are credited in the repository's `NOTICE` file.

## References

Bagnall, R. et al. (2006–). *Pleiades: A Gazetteer of Past Places*. Available at
https://pleiades.stoa.org

Bowker, G. C. & Star, S. L. (1999). *Sorting Things Out: Classification and Its
Consequences*. MIT Press.

Gitelman, L. (ed.) (2013). *"Raw Data" Is an Oxymoron*. MIT Press.

Kelso, N. V. & Patterson, T. (2010). Introducing Natural Earth Data —
naturalearthdata.com. *Geographia Technica*, 5(82–89). Available at
https://www.naturalearthdata.com

Ourednik, A. (2021). *historical-basemaps: Historical country boundaries GeoJSON*.
Available at https://github.com/aourednik/historical-basemaps

Ramadani, C. (2026). *AtlasPI: A structured historical geographic database for AI
agents* (Version 6.99) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.19581784

Vrandečić, D. & Krötzsch, M. (2014). Wikidata: a free collaborative knowledgebase.
*Communications of the ACM*, 57(10), 78–85.
