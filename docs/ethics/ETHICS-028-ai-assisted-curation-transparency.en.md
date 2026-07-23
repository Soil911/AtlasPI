# ETHICS-028 — Transparency about AI-assisted curation

> **Note**: this is the English record of [ETHICS-028-trasparenza-curation-ai.md](ETHICS-028-trasparenza-curation-ai.md). The Italian version is the authoritative one per the AtlasPI documentation policy — if the two diverge, the Italian takes precedence. This translation is provided for non-Italian-reading reviewers, because the failure this record documents happened in English, in public.

**Date**: 2026-07-23
**Status**: Adopted
**Author**: Clirim (maintainer)
**Impact**: High — concerns the honesty of the project's self-description, not the data itself.

## What happened

The maintainer of `tmcw/awesome-geojson` rejected AtlasPI's inclusion PR (#77), writing: *"it looks like this is getting an LLM to produce academic citations […] slop datasets are bad and not allowed on this list"*. In an earlier thread (#75) the same maintainer had asked: *"Is this even a real person submitting PRs, or is it the vibecoding bot doing the promotion too?"* — a fair question, since the project's internal promotion playbook was sitting in the public repository for anyone to read.

At the time of the rejection, parts of the project documentation described the dataset as **"hand-curated"**. That claim was false.

## The wrong claim vs. the actual process

The distortion risk here is not the use of AI itself: it is **describing the process as more human than it is**.

What the documentation said: *hand-curated*.

What the process actually is: most enrichment batches are produced by **LLM research agents** that propose metadata and candidate citations; every batch then passes an **adversarial verification step** whose sole task is to reject citations that do not exist or do not support the claim; structural CI fences guard referential integrity; and the **maintainer supervises** the pipeline and its outputs. There is, however, **no systematic record-by-record review by professional historians**. LLM-produced bibliographies carry a documented fabrication risk.

A reader — or an academic reviewer — who discovered this gap after reading "hand-curated" would rightly conclude they had been misled. For a project whose first stated value is "truth before comfort", that is unacceptable regardless of the PR's outcome.

## Alternatives considered

1. **Say nothing / downplay** ("the adversarial verification exists anyway").
   Rejected: this is exactly the comfort the project refuses for historical data;
   there is no reason to accept it for process metadata.
2. **Dispute the maintainer's judgment** (adversarial verification exists,
   sources are typed, etc.). Rejected as the *primary* response: those facts are
   true, but the burden of proof for an AI-assisted dataset lies on us, not on
   the person curating a list. Quality is demonstrated, not claimed.
3. **Disclose the process, everywhere, with its mitigations and its limits.**
   Adopted.

## Decision

1. `docs/METHODOLOGY.md` §2.4 states explicitly: curation is AI-assisted, with
   adversarial citation verification and maintainer supervision, and **without
   systematic review by professional historians**; public correction channels
   are listed.
2. The JOHD data paper uses the same wording — peer review must be able to judge
   the actual process, not a flattering version of it.
3. The expression **"hand-curated" is retired** from the project's documentation,
   except for the (few) records genuinely written by hand.
4. Third-party submissions (lists, directories) must not obscure the AI-assisted
   nature of the project where the context makes it relevant.
5. **Promotion is paused** — no new list submissions, no launch posts, no journal
   submission — until the human citation audit (see Remediation) is published.
6. **Sensitive public communications** (PR comments, replies to maintainers) are
   written and posted by the maintainer personally. AI agents may prepare drafts;
   they do not speak for the project.

## Remediation

The most credible external mitigation is a **human audit of the citations** — not
another automated pass. Protocol and sample live in
[`docs/academic-audit/`](../academic-audit/CITATION-AUDIT.md): a deterministic,
publicly reproducible random sample of records is drawn from the production API,
and the maintainer verifies each sampled citation by hand against three criteria
(the work exists; the bibliographic details are correct; the work supports the
record). Results will be published in the same folder, **including failures**.

Until that audit is published, the honest description of AtlasPI's citations is:
**machine-verified, not human-audited**.

## Accountability

The misleading wording was published under the maintainer's responsibility. The
error is not attributable to any AI tool: tools do not sign documentation —
maintainers do. The public commitment made in the rejection thread ("reorganize
the plan and review the critical points before pushing anything else") is
honored by this record, by the disclosure in the README, and by the audit
protocol above.
