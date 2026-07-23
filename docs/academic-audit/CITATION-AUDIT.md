# AtlasPI — Human Citation Audit

> This document is deliberately written in English (the project's documentation
> is otherwise in Italian): its audience is external reviewers. Context:
> [ETHICS-028 (EN)](../ethics/ETHICS-028-ai-assisted-curation-transparency.en.md).

## Why this audit exists

AtlasPI's non-boundary records are curated with an AI-assisted pipeline
(LLM research agents + adversarial citation verification + maintainer
supervision — see [METHODOLOGY §2.4](../METHODOLOGY.md)). LLM-produced
bibliographies carry a documented fabrication risk, and machine verification of
that risk is itself machine work. Until a **human** has checked a random sample
of citations, the honest status of AtlasPI's citations is *machine-verified,
not human-audited* — and that is what the project's README says.

This audit is the remediation committed to in ETHICS-028 after the
`tmcw/awesome-geojson` rejection (2026-07-23). Its results will be published in
this folder **whatever they show, including failures**.

## Sampling protocol

The sample is drawn by [`scripts/citation_audit_sample.py`](../../scripts/citation_audit_sample.py)
from the **public production API** (`https://atlaspi.it`), with no credentials,
so anyone can re-draw it and check it matches the committed CSV:

1. Fetch all entities (`GET /v1/entities`) and all events (`GET /v1/events`);
   sort each list by numeric `id` ascending.
2. Seed a PRNG with the fixed string **`atlaspi-audit-2026-07`**
   (Python `random.Random("atlaspi-audit-2026-07")`).
3. Draw **40 entities**, then **10 events** (`rng.sample` on the sorted ID
   lists, in that order).
4. Sort the sampled IDs ascending; for each record in that order, fetch its
   detail (`GET /v1/entities/{id}` / `GET /v1/events/{id}`) and pick **one**
   citation with `rng.choice(sources)`.
5. Write `docs/academic-audit/sample-2026-07.csv` (UTF-8).

A record with an empty `sources[]` would appear in the CSV with an empty
citation and a `NO SOURCES` note — that would be a finding, not grounds for
exclusion. (As of the draw date, production reports 100% source coverage.)

Reproducibility is scoped to the dataset state: the dataset keeps growing, so a
re-draw against a later state may differ. The committed CSV is the frozen
sample; it was drawn on **2026-07-23** against production **v6.99.138**
(1,015 entities, 643 events).

To re-draw:

```bash
python scripts/citation_audit_sample.py
```

## What is verified, and by whom

**Verifier: the maintainer (Clirim), by hand** — library catalogues (WorldCat,
Google Books/Scholar, publisher pages, DOI resolution), not LLMs. Each sampled
citation is judged on three criteria, filled into the CSV:

| Column | Question | Allowed values |
|---|---|---|
| `exists` | Does the cited work exist at all? | `yes` / `no` |
| `biblio_correct` | Are author(s), title, year, publisher/venue correct? | `yes` / `minor` (typos, wrong edition year ≤2 off) / `no` |
| `supports_record` | Is the work plausibly a source for *this* record's claims? | `yes` / `partial` / `no` |
| `notes` | Free text: what was checked, where, and what was found | — |

`exists = no` on any row is a **fabricated citation** and will be reported as
such. `supports_record` is judged on scope (does the work cover this polity /
event / period), not on page-level verification, which a single maintainer
cannot do for 50 records across dozens of languages — this limit is stated
here deliberately.

## Publication commitment

- The filled CSV replaces the empty-columns version in this folder when the
  audit is complete.
- A `RESULTS-2026-07.md` summary will report pass/fail counts per criterion,
  every failure verbatim, and the corrective action taken (source replaced,
  record corrected, or record removed).
- If the failure rate is material, that number goes in the README next to the
  disclosure — not buried here.
