# AtlasPI — Advisory Outreach Drafts

**Status**: internal drafts, not yet sent. Intended for soliciting pre-submission feedback on the v6.1.1 dataset, the paper draft, and the ethics framework from a small circle of domain experts before any public launch (per user's "no push marketing until the product is super" policy).

Each template is short by design — a busy academic should be able to decide in under 30 seconds whether to engage.

---

## Template A — Cold: historical GIS / spatial history scholar

**Subject**: AtlasPI — machine-readable historical geography, would welcome your eye on the boundary methodology

Dear Prof. *[surname]*,

I am Clirim Riza (CRA, Italy). I am writing because your work on *[concrete paper / dataset / tool]* sits very close to a project I have just put online and would benefit from your critical reading before I take it further.

AtlasPI (https://atlaspi.cra-srl.com, https://github.com/Soil911/AtlasPI) is an Apache-2.0 structured dataset of 747 historical polities from 4500 BCE to 2024, exposed via a REST API and an MCP server intended for AI-agent consumption. Boundaries are assembled through a documented three-tier pipeline (Natural Earth for modern states, Ourednik's *historical-basemaps* for pre-1800, a deterministic fallback otherwise) and every record carries an explicit confidence score and source citations. The methodology is written up in `docs/METHODOLOGY.md`, and a data-paper draft targeting JOHD is in `docs/paper-draft.md`.

I am not asking for co-authorship or a formal review. I am asking whether you would glance at the methodology document and paper draft for 20–30 minutes and tell me where the approach is clearly wrong or where a working historian would reach for the delete key. I would find that signal more valuable than any other feedback at this stage.

If useful, I am happy to pre-load a short call (15 min) or simply send the two files as PDFs.

With thanks,
Clirim Riza
CRA — clirim@cra-srl.com

---

## Template B — Warmer: digital humanities / computational history

**Subject**: A small dataset that tries to be honest about uncertainty — would love your take

Hi *[first name]*,

I have been following your work on *[project / toolkit / post]* and suspect AtlasPI will be recognisable to you.

It is a 747-entity structured historical geographic dataset, released under Apache-2.0, with an explicit ethics framework baked in: contested names carry the original-language form as primary, disputed territories are capped at confidence ≤ 0.70 regardless of source quality, generated polygons are tagged and capped at 0.40, and every record has source citations. The API is live at https://atlaspi.cra-srl.com; a JOHD-style data paper draft is in the repo.

The short version of the ask: do you think the ethics framework is honest, or is it performing honesty? Specifically — would you look at `docs/ethics/ETHICS-003-territori-contestati-attuali.md` (currently Italian — English translation available on request) and tell me whether the confidence cap mechanism is sufficient for what it claims to do?

I am at a stage where negative feedback is more useful than positive.

Cheers,
Clirim Riza
CRA — clirim@cra-srl.com
https://github.com/Soil911/AtlasPI

---

## Template C — LLM / AI agent research audience

**Subject**: Open historical geography API + MCP server for agent tool-use — would value a critical look

Dear *[name]*,

If you build or evaluate LLMs that reason over history, AtlasPI may be a useful stress test.

It is a structured dataset of 747 historical polities with a REST API, an MCP server (8 tools), and explicit confidence / source metadata on every record. The design intent was to give an AI agent exactly the kind of grounded, citation-bearing, spatially-joined response that is currently missing from Wikipedia / Wikidata / Natural Earth in isolation.

The piece I suspect you would find interesting: we cap confidence at ≤ 0.70 for entities with `status: "disputed"` regardless of how good the upstream polygon is, because territorial legitimacy and geometric fidelity are orthogonal — a claim that an LLM should not silently collapse. The mechanism is enforced in the ingestion pipeline and verified by `tests/test_ethical.py`.

I would be grateful for 15 minutes of your time on either:

1. Running the MCP server against a tool-using agent of your choice and telling me what breaks.
2. Reading the ethics framework (`docs/ethics/`) and telling me whether the constraints are ones LLM pipelines would actually respect in practice.

Live: https://atlaspi.cra-srl.com
Repo: https://github.com/Soil911/AtlasPI
Methodology: `docs/METHODOLOGY.md`

Thank you for considering.

Clirim Riza
CRA — clirim@cra-srl.com

---

## Template D — Regional / topical expert (e.g. Islamic history, East Asian history, pre-Columbian Americas)

Use this when you have found a specific weakness in your own spot-check (e.g. the Abbasid boundary is hand-drawn at 18 vertices and you suspect it under-represents Maghreb and Transoxiana at their fullest extent) and want a domain expert's eye on a **specific** record rather than the whole framework.

**Subject**: AtlasPI v6.1.1 — would you verify one entity in your area?

Dear Prof. *[surname]*,

Brief and concrete: AtlasPI (https://atlaspi.cra-srl.com) is a structured historical geographic dataset I have just put online. During a top-10 spot check I noticed that the boundary for *[specific entity]* is almost certainly too simple for serious use — the polygon is drawn from an older secondary source and does not reflect *[the specific historical insight you want to check]*.

Would you be willing to look at the entity page (https://atlaspi.cra-srl.com/v1/entities/*[id]*) and tell me either:

1. That the simplification is acceptable for a structured-data context, or
2. What the canonical citation for a better polygon would be.

No deadline, no formal review, no commitment beyond one short reply. I will acknowledge your input in the project's `ACKNOWLEDGMENTS.md` unless you prefer anonymity.

With thanks,
Clirim Riza
CRA — clirim@cra-srl.com

---

## Candidate recipient list

**Fill in before sending. The following are categories, not actual names — the goal is 4–6 recipients per category, with a 2:1 ratio of declines to responses being a normal outcome.**

### Historical GIS / spatial history
- Spatial-history scholars publishing on longue-durée mapping tools
- Authors of the HGIS / HGIS-Germany / China Historical GIS projects
- Editors of relevant journals (e.g. *Historical Methods*, *Social Science History*)

### Digital humanities / computational history
- DH scholars running grant-funded dataset projects
- Authors of widely-cited DH data papers in JOHD / *Data in Brief*
- Editors of *Digital Humanities Quarterly*

### LLM / AI agent research
- Researchers publishing on retrieval-augmented LLMs with historical domain knowledge
- MCP server authors and tool-use evaluation leads
- Digital humanities AI crossover researchers (e.g. fellows at the Alan Turing Institute)

### Regional / topical experts
- One Islamic-history scholar (for the Abbasid spot-check concern)
- One East Asian historian (Qing / Tokugawa boundary verification)
- One pre-Columbian Americas specialist (Inca / Mexica / Maya verification)
- One Sub-Saharan Africa specialist (Kongo / Mali / Songhai verification)

---

## Sending protocol

1. Do not send more than **2 cold emails per week** to avoid looking like a mass outreach campaign.
2. Personalise the `*[concrete paper / dataset / tool]*` placeholder for every single recipient — generic praise is worse than no personalisation.
3. Wait at least 2 weeks between a non-response and any follow-up.
4. Track responses in a private spreadsheet (not in the public repository).
5. Do **not** mention the JOHD submission target until the recipient has engaged — framing the ask as "review my paper" raises the perceived commitment bar.
