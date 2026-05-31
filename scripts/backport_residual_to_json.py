"""Reconcile the residual JSON↔prod divergences left by v6.99.93 — follow-up.

The v6.99.93 boundary backport (scripts/backport_phase_h_to_json.py) skipped 7
"prod-only" ids and deliberately did NOT touch name_original. Full triage of
those (see docs/ethics/ETHICS-012, input data/fixes/phase_h_residual_export.json)
resolved them into:

  * 6 genuine prod-only INSERT entities absent from the JSON source (so empty-DB
    deploys omitted them): Res Publica Romana, Premier Empire français, Afsharids,
    Old-Babylonian, Sangam-era Chola, and the (disputed, documented) Kingdom of
    Quito. Added as complete entities to data/entities/batch_36_prod_reconciliation.json.
  * 1 RENAME that had been mis-classified as an insert: prod id 741 'مقديشو' is
    JSON 'Maqdishaw' (same sultanate, 900-1600, same capital) — its boundary was
    also missed by v6.99.93, so it is both renamed AND boundary-backported here.

Plus the ETHICS-001 names debt: 14 entities whose name_original was converted to
native script IN PROD but kept the Latin form in JSON. This sets name_original to
the prod native form and syncs name_variants from prod (union, lossless — the old
Latin name is preserved as a variant).

Cascade: two non-entity files reference an old name and are updated so the seed's
name-based linking survives — data/chains/batch_20_balkan.json ('Raska') and
data/events/batch_20_trade_exploration.json ('Maqdishaw').

Source-only; NO prod deploy (prod already correct). Minimal-diff (CRLF,
ensure_ascii=False, indent=2). Idempotent. Refuses to write if the collision
fence is not green on the result.

Usage:
    python -m scripts.backport_residual_to_json --dry-run
    python -m scripts.backport_residual_to_json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_DIR = ROOT / "data" / "entities"
EXPORT = ROOT / "data" / "fixes" / "phase_h_residual_export.json"
INSERTS_FILE = ENTITIES_DIR / "batch_36_prod_reconciliation.json"

# prod id -> the CURRENT (Latin) name_original in data/entities/*.json.
RENAME_BY_ID = {
    678: "Hetmanshchyna", 584: "Despotovina Srbije", 665: "Zeta",
    679: "Polatskaye Knyastva", 667: "Raska", 747: "Bazin",
    988: "Hammadids", 986: "Banu Midrar", 985: "Dawla al-Rustamiyya",
    705: "Lanfang Gongheguo", 1006: "Makhzumi Sultanate of Shewa",
    1009: "Mogadishu Sultanate early", 1033: "Tunjur", 1032: "Daju Sultanate",
    741: "Maqdishaw",  # mis-classified as insert in v6.99.93; also boundary-backported
}
INSERT_IDS = {530, 1034, 1037, 1038, 1039, 1040}

# 4 inserts arrive from prod with zero name_variants, which violates the JSON
# invariant "every entity has >=1 variant" (tests/test_database.py). Add their
# well-documented English/romanized names — a strict searchability/ETHICS-001
# improvement. (Prod itself lacks these — enrich there as a follow-up.)
SUPPLEMENT_VARIANTS = {
    1037: [{"name": "First French Empire", "lang": "en"},
           {"name": "Napoleonic Empire", "lang": "en"},
           {"name": "Premier Empire", "lang": "fr"}],
    1038: [{"name": "Afsharid dynasty", "lang": "en"},
           {"name": "Afsharid Empire", "lang": "en"},
           {"name": "Afshariyan", "lang": "fa"}],
    1039: [{"name": "Old Babylonian Empire", "lang": "en"},
           {"name": "First Dynasty of Babylon", "lang": "en"}],
    1040: [{"name": "Early Cholas", "lang": "en"},
           {"name": "Sangam-era Chola", "lang": "en"}],
}

# id 741 'Maqdishaw' also needs the boundary it never received in v6.99.93.
BOUNDARY_FIELDS = (
    "boundary_geojson", "boundary_source", "boundary_aourednik_name",
    "boundary_aourednik_year", "boundary_aourednik_precision",
    "boundary_ne_iso_a3", "confidence_score", "status",
)
BOUNDARY_BACKPORT_IDS = {741}
DISPUTED_CONFIDENCE_CAP = 0.70  # ETHICS-003

# entity fields that make up a complete JSON entity (id is dropped on insert).
ENTITY_SCALARS = (
    "name_original", "name_original_lang", "entity_type", "year_start", "year_end",
    "capital_name", "capital_lat", "capital_lon", "boundary_geojson",
    "boundary_source", "boundary_aourednik_name", "boundary_aourednik_year",
    "boundary_aourednik_precision", "boundary_ne_iso_a3", "confidence_score",
    "status", "ethical_notes",
)

# Cascade name-ref updates: (relative path, kind, old, new). 'new' is filled with
# the native name at runtime so it always matches the renamed entity.
CASCADES = [
    ("data/chains/batch_20_balkan.json", "chain_link", "Raska", 667),
    ("data/events/batch_20_trade_exploration.json", "event_ref", "Maqdishaw", 741),
]


def _clean_variant(v: dict) -> dict:
    return {k: v[k] for k in ("name", "lang", "period_start", "period_end", "context", "source")
            if k in v and v[k] is not None}


def _union_variants(prod_variants, json_variants, old_latin) -> list[dict]:
    """prod (curated) first, then any JSON-only variant, then the displaced Latin
    name — deduped by name string. Lossless."""
    out, seen = [], set()
    for v in prod_variants:
        cv = _clean_variant(v)
        if cv.get("name") and cv["name"] not in seen:
            seen.add(cv["name"])
            out.append(cv)
    for v in (json_variants or []):
        if v.get("name") and v["name"] not in seen:
            seen.add(v["name"])
            out.append(v)
    if old_latin not in seen:
        out.append({"name": old_latin, "lang": "en", "context": "Latinized form (former name_original)"})
    return out


def _cap_disputed(ent: dict) -> None:
    if ent.get("status") == "disputed" and (ent.get("confidence_score") or 0) > DISPUTED_CONFIDENCE_CAP:
        ent["confidence_score"] = DISPUTED_CONFIDENCE_CAP


def _dump(path: Path, data) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Reconcile residual JSON↔prod (names + inserts).")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

    export = {r["id"]: r for r in json.load(open(EXPORT, encoding="utf-8"))}
    native_by_id = {i: export[i]["name_original"] for i in RENAME_BY_ID}
    latin_to_id = {latin: i for i, latin in RENAME_BY_ID.items()}

    # --- load all entity files
    files = sorted(p for p in ENTITIES_DIR.glob("*.json")
                   if not p.name.endswith(".bak") and p.name != INSERTS_FILE.name)
    parsed = {p: json.load(open(p, encoding="utf-8")) for p in files}

    # collision: native names must not already exist as another entity's name_original
    all_names = {e.get("name_original") for data in parsed.values() for e in data}

    # --- 1) renames (+ 741 boundary)
    renamed, changed_files = [], set()
    for p, data in parsed.items():
        for ent in data:
            nm = ent.get("name_original")
            if nm not in latin_to_id:
                continue
            pid = latin_to_id[nm]
            row = export[pid]
            native = native_by_id[pid]
            if native in all_names and native != nm:
                print(f"ABORT: native name {native!r} (id={pid}) already exists as another entity.")
                return 2
            ent["name_variants"] = _union_variants(row.get("name_variants", []),
                                                   ent.get("name_variants", []), nm)
            ent["name_original"] = native
            ent["name_original_lang"] = row["name_original_lang"]
            if pid in BOUNDARY_BACKPORT_IDS:
                for f in BOUNDARY_FIELDS:
                    ent[f] = row.get(f)
                _cap_disputed(ent)
            renamed.append((pid, nm, native))
            changed_files.add(p)

    # --- 2) cascade refs in chains/events
    cascade_done = []
    for rel, kind, old, pid in CASCADES:
        fp = ROOT / rel
        data = json.load(open(fp, encoding="utf-8"))
        new = native_by_id[pid]
        n = 0
        for item in data:
            if kind == "chain_link":
                for lk in item.get("links", []):
                    if lk.get("entity_name") == old:
                        lk["entity_name"] = new
                        n += 1
            elif kind == "event_ref":
                for el in item.get("entity_links", []):
                    if el.get("entity_name_original") == old:
                        el["entity_name_original"] = new
                        n += 1
        if n and not args.dry_run:
            _dump(fp, data)
        cascade_done.append((rel, old, new, n))

    # --- 3) inserts -> new batch file
    inserts = []
    for i in sorted(INSERT_IDS):
        row = export[i]
        ent = {k: row.get(k) for k in ENTITY_SCALARS}
        nv = [_clean_variant(v) for v in row.get("name_variants", [])]
        seen = {v["name"] for v in nv} | {ent["name_original"]}
        for sv in SUPPLEMENT_VARIANTS.get(i, []):
            if sv["name"] not in seen:
                nv.append(sv)
                seen.add(sv["name"])
        ent["name_variants"] = nv
        ent["territory_changes"] = row.get("territory_changes", [])
        ent["sources"] = row.get("sources", [])
        _cap_disputed(ent)
        inserts.append(ent)

    # --- report
    print(f"Renames: {len(renamed)} (incl. 741 boundary). Inserts: {len(inserts)} -> {INSERTS_FILE.name}")
    for pid, old, new in sorted(renamed):
        print(f"   rename id={pid}: {old!r} -> {new!r}")
    for rel, old, new, n in cascade_done:
        print(f"   cascade {rel}: {old!r} -> {new!r}  ({n} ref)")
    for ent in inserts:
        print(f"   insert: {ent['name_original']!r} ({ent['entity_type']}, {ent['year_start']}..{ent['year_end']}, "
              f"{ent['boundary_source']}, conf={ent['confidence_score']}, {ent['status']})")

    # --- fence self-check on the resulting union (renamed entities + inserts)
    union = {}
    for data in parsed.values():
        for e in data:
            union[e.get("name_original")] = e
    for e in inserts:
        union[e["name_original"]] = e
    from src.ingestion.boundary_collision_guard import detect_json_boundary_collisions
    res = detect_json_boundary_collisions(list(union.values()))
    print(f"\nFENCE: super_group_alerts={res['super_group_alert_count']} "
          f"big_groups={res['big_groups_count']} status={res['status']}")
    for a in res["super_group_alerts"]:
        print(f"   SUPER {a['boundary_aourednik_name']!r} x{a['n_entities']} {a['year_range']}: {a['names'][:6]}")

    if args.dry_run:
        print("\nDRY-RUN: no files written.")
        return 0
    if res["status"] != "ok":
        print("\nABORT: fence not green — refusing to write.")
        return 3

    for p in changed_files:
        _dump(p, parsed[p])
    _dump(INSERTS_FILE, inserts)
    print(f"\nWrote {len(changed_files)} entity files + {INSERTS_FILE.name} ({len(inserts)} inserts) "
          f"+ {sum(1 for *_ , n in cascade_done if n)} cascade files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
