# Acknowledgments

AtlasPI's quality depends on the generosity of people who read its data,
methodology, and ethics framework with a critical eye and share what they
find. This file records their contributions with their consent.

If you have reviewed, corrected, or advised on AtlasPI and are not yet
listed here, please tell us (`clirim@cra-srl.com` or open a pull request
against this file). Anonymity on request is always respected.

---

## Upstream datasets

AtlasPI would not exist without:

- **Natural Earth** (<https://www.naturalearthdata.com/>) — public-domain
  vector basemaps. The post-1800 administrative boundaries in AtlasPI are
  derived from Natural Earth's Admin-0 dataset under its public-domain
  dedication.
- **André Ourednik and contributors** for
  [`historical-basemaps`](https://github.com/aourednik/historical-basemaps)
  — timestamped world-boundary GeoJSON snapshots covering −123000 to
  2010 CE, released under CC BY 4.0. The vast majority of AtlasPI's
  pre-1800 polygon coverage is derived from this dataset.
- **OpenStreetMap contributors** for geographic reference data under
  the [Open Database License](https://opendatacommons.org/licenses/odbl/).
- **Wikidata contributors** for structured entity metadata under CC0.

Each derived polygon carries its upstream attribution in the
`boundary_source`, `boundary_aourednik_name`, and `boundary_ne_iso_a3`
fields so that any returned boundary can be traced back to its source
feature.

---

## Academic reviewers

*Reviewers who have read the methodology, paper draft, or ethics
framework and provided substantive feedback will be named here with
their permission, alongside the version of AtlasPI they reviewed.*

*The list is currently empty because pre-submission review outreach
(see `docs/outreach-draft.md`) is just beginning as of v6.1.1
(2026-04-14). Any reviewer who prefers not to be named publicly will
be acknowledged anonymously by discipline (e.g. "a medievalist
specialising in the Islamic Mediterranean").*

---

## Data contributors

*Contributors who have opened issues, submitted pull requests, or
otherwise corrected individual entities will be named here as the
project grows. See `CONTRIBUTING.md` for how to contribute a
correction.*

---

## Infrastructure and tooling

AtlasPI is built on free-and-open-source software. Notable dependencies
that deserve acknowledgment beyond their `pyproject.toml` entry:

- **FastAPI** (Sebastián Ramírez and contributors) — the web framework
- **SQLAlchemy** (Mike Bayer and contributors) — the ORM
- **Alembic** — schema migrations
- **pytest** — the test runner that keeps this thing honest
- **Sentry** — exception monitoring (via the open-source Python SDK)

---

## Funding and hosting

AtlasPI is self-funded by **CRA (Cra Srl)**, which operates the hosted
instance at <https://atlaspi.cra-srl.com> at its own cost. No external
grants have been received to date.

---

## A note on ethics framework

The five ETHICS records in `docs/ethics/` codify decisions that could
have gone differently. The framework is not novel scholarship; it
reflects long-standing conversations in historical GIS, postcolonial
history, and digital humanities about how to encode uncertainty,
contestation, and historical violence without sanitisation. We
acknowledge that intellectual debt even when it cannot be cited to a
single source.
