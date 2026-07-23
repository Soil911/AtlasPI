"""Draw the deterministic citation-audit sample from the public AtlasPI API.

Protocol: docs/academic-audit/CITATION-AUDIT.md (ETHICS-028 remediation).

# ETHICS: this script exists so that ANYONE — not just the maintainer — can
# re-draw the audit sample and check it matches the committed CSV. No
# credentials, stdlib only, fixed seed, stable iteration order. The humans
# being audited must not be able to (or be suspected of) cherry-picking
# which citations get checked.

Usage:
    python scripts/citation_audit_sample.py

Output: docs/academic-audit/sample-2026-07.csv (UTF-8, LF line endings).
The verdict columns (exists, biblio_correct, supports_record, notes) are
left empty: they are filled BY HAND by the maintainer.

Reproducibility is scoped to the dataset state (the dataset keeps growing):
the committed CSV is the frozen sample, drawn 2026-07-23 against v6.99.138.
"""

from __future__ import annotations

import csv
import json
import random
import sys
import time
import urllib.request
from pathlib import Path

BASE_URL = "https://atlaspi.it"
SEED = "atlaspi-audit-2026-07"
N_ENTITIES = 40
N_EVENTS = 10
OUT_PATH = Path(__file__).resolve().parents[1] / "docs" / "academic-audit" / "sample-2026-07.csv"
USER_AGENT = "atlaspi-citation-audit/1.0 (docs/academic-audit/CITATION-AUDIT.md)"
PAGE_SIZE = 500
POLITE_DELAY_S = 0.15


def _get_json(path: str, retries: int = 3) -> dict:
    url = f"{BASE_URL}{path}"
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as err:  # noqa: BLE001 — retry any transport error
            last_err = err
            time.sleep(2**attempt)
    raise RuntimeError(f"GET {url} failed after {retries} attempts: {last_err}")


def _fetch_all_ids(resource: str, list_key: str) -> list[int]:
    """Fetch every record ID of a resource, paginating; sorted ascending."""
    ids: list[int] = []
    offset = 0
    total = None
    while total is None or len(ids) < total:
        page = _get_json(f"/v1/{resource}?limit={PAGE_SIZE}&offset={offset}")
        total = page["total"]
        batch = page[list_key]
        if not batch:
            break
        ids.extend(item["id"] for item in batch)
        offset += len(batch)
        time.sleep(POLITE_DELAY_S)
    if len(ids) != total:
        raise RuntimeError(f"{resource}: fetched {len(ids)} ids, API reports total={total}")
    if len(set(ids)) != len(ids):
        raise RuntimeError(f"{resource}: duplicate ids in listing")
    return sorted(ids)


def main() -> int:
    print(f"Fetching record listings from {BASE_URL} ...")
    entity_ids = _fetch_all_ids("entities", "entities")
    event_ids = _fetch_all_ids("events", "events")
    print(f"  {len(entity_ids)} entities, {len(event_ids)} events")

    # Draw order is part of the protocol: entities first, then events,
    # from a single PRNG seeded with the fixed public seed.
    rng = random.Random(SEED)
    sampled_entities = sorted(rng.sample(entity_ids, N_ENTITIES))
    sampled_events = sorted(rng.sample(event_ids, N_EVENTS))

    rows = []
    for record_type, resource, sampled in (
        ("entity", "entities", sampled_entities),
        ("event", "events", sampled_events),
    ):
        for record_id in sampled:
            detail = _get_json(f"/v1/{resource}/{record_id}")
            sources = detail.get("sources") or []
            if sources:
                chosen = rng.choice(sources)
                citation = chosen.get("citation", "")
                source_type = chosen.get("source_type", "")
                notes = ""
            else:
                # A record without sources is a finding, not an exclusion.
                citation, source_type, notes = "", "", "NO SOURCES"
            rows.append(
                {
                    "record_type": record_type,
                    "record_id": record_id,
                    "record_name": detail.get("name_original", ""),
                    "record_url": f"{BASE_URL}/v1/{resource}/{record_id}",
                    "citation": citation,
                    "source_type": source_type,
                    "exists": "",
                    "biblio_correct": "",
                    "supports_record": "",
                    "notes": notes,
                }
            )
            print(f"  sampled {record_type} #{record_id}: {detail.get('name_original', '')!r}")
            time.sleep(POLITE_DELAY_S)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # LF line endings + UTF-8 no BOM: byte-identical output on every platform.
    with OUT_PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
