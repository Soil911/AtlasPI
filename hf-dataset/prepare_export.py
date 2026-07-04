"""Export AtlasPI dataset to JSONL files for HuggingFace upload.

Run:
    python hf-dataset/prepare_export.py
    # generates: entities.jsonl, events.jsonl, periods.jsonl, chains.jsonl

Then upload to HF with:
    huggingface-cli login
    huggingface-cli repo create atlaspi-historical-geography --type dataset
    cd hf-dataset && huggingface-cli upload atlaspi-historical-geography . --repo-type=dataset
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://atlaspi.it"
OUT_DIR = Path(__file__).resolve().parent

# Rate-limit safety: prod applica 60 req/min per IP. Throttliamo a ~50/min e
# ritentiamo sui 429 con backoff, così l'export completo (~800 GET individuali)
# non si spezza a metà.
_MIN_INTERVAL = 1.2  # secondi tra le richieste
_last_call = [0.0]


def _get(path: str) -> dict | list:
    for attempt in range(6):
        wait = _MIN_INTERVAL - (time.time() - _last_call[0])
        if wait > 0:
            time.sleep(wait)
        _last_call[0] = time.time()
        req = urllib.request.Request(BASE + path, headers={"User-Agent": "hf-export/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                print(f"GET {path}")
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                back = 5 * (attempt + 1)
                print(f"  429 rate-limited su {path} — retry tra {back}s")
                time.sleep(back)
                continue
            raise
    raise RuntimeError(f"GET {path} fallito dopo retry (429 persistente)")


def _paginated(path: str, limit: int = 100) -> list:
    """Fetch all records from a paginated endpoint."""
    all_items: list = []
    offset = 0
    while True:
        data = _get(f"{path}?limit={limit}&offset={offset}")
        items = (
            data.get("entities") or data.get("events")
            or data.get("periods") or data.get("chains")
            or []
        )
        if not items:
            break
        all_items.extend(items)
        if len(items) < limit:
            break
        offset += limit
    return all_items


def write_jsonl(filename: str, records: list) -> None:
    path = OUT_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"✓ Wrote {len(records)} records to {path.name}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print(f"Exporting AtlasPI dataset from {BASE}\n")

    # Entities — use batch to fetch full details (not just summary)
    print("[1/4] Fetching entities...")
    ent_list = _paginated("/v1/entities", limit=100)
    ent_ids = [e["id"] for e in ent_list]
    # Batch fetch full details (100 at a time)
    entities_full: list = []
    for i in range(0, len(ent_ids), 100):
        batch = ent_ids[i:i + 100]
        ids_str = ",".join(str(x) for x in batch)
        res = _get(f"/v1/entities/batch?ids={ids_str}")
        entities_full.extend(res["entities"])
    write_jsonl("entities.jsonl", entities_full)

    # Events
    print("\n[2/4] Fetching events...")
    events = _paginated("/v1/events", limit=100)
    # For each, fetch the full detail to include sources, ethical_notes, etc.
    events_full: list = []
    for ev in events:
        try:
            detail = _get(f"/v1/events/{ev['id']}")
            events_full.append(detail)
        except Exception as e:
            print(f"  ! Failed to fetch event {ev['id']}: {e}")
    write_jsonl("events.jsonl", events_full)

    # Periods
    print("\n[3/4] Fetching periods...")
    periods_list = _paginated("/v1/periods", limit=100)
    periods_full: list = []
    for p in periods_list:
        try:
            detail = _get(f"/v1/periods/{p['id']}")
            periods_full.append(detail)
        except Exception:
            periods_full.append(p)
    write_jsonl("periods.jsonl", periods_full)

    # Chains
    print("\n[4/4] Fetching chains...")
    chains_list = _paginated("/v1/chains", limit=100)
    chains_full: list = []
    for c in chains_list:
        try:
            detail = _get(f"/v1/chains/{c['id']}")
            chains_full.append(detail)
        except Exception:
            chains_full.append(c)
    write_jsonl("chains.jsonl", chains_full)

    print(f"\n✓ Export complete — files in {OUT_DIR}")
    print("\nNext steps:")
    print("  1. pip install huggingface-hub")
    print("  2. huggingface-cli login")
    print("  3. huggingface-cli repo create atlaspi-historical-geography --type dataset")
    print(f"  4. cd {OUT_DIR.name} && huggingface-cli upload atlaspi-historical-geography . --repo-type=dataset")


if __name__ == "__main__":
    main()
