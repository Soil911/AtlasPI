"""Backport prod-only boundary state into the JSON source — Wave 2 audit #7.

Context
-------
Two SQL-only enrichment campaigns were applied directly to the production DB and
never propagated to ``data/entities/*.json``:

  * Phase H (``docs/boundary-review-v6.99.79/*.sql``): 372 entities whose
    colliding super-group polygons were replaced with capital circles
    (``boundary_source='approximate_circle'``). See ETHICS-012.
  * iter-series (``scripts/sql_iter*_boundaries.sql`` + ``sql_manual_boundaries.sql``):
    227 entities given hand-drawn historical polygons
    (``boundary_source='historical_approximation'``).

Because ``seed_database()`` only runs on an empty DB, a fresh seed / empty-DB
deploy reproduces the OLD super-group polygons (~22 collision groups, verified)
and loses the hand-drawn enrichments. This blocked the boundary-collision CI
fence (audit #7) and would silently regress any clean redeploy.

What this does
--------------
Reads a read-only export of prod's divergent rows
(``data/fixes/phase_h_backport_export.json`` — see its README) and copies, for
each matched entity, ONLY the reviewed boundary state:

    boundary_geojson, boundary_source,
    boundary_aourednik_name/year/precision, boundary_ne_iso_a3,
    confidence_score, status

``confidence_score`` + ``status`` travel WITH the geometry because Phase H/iter
revised them as one coherent decision (ETHICS-004/012/013): circles had
confidence reduced; researched polygons had it raised; a few duplicates were
marked ``deprecated``. Backporting geometry alone would leave 58 entities
incoherent (verified).

NOT touched: ``name_original`` (prod has since converted ~14 to native script
per ETHICS-001 — a separate names-sync concern), ``ethical_notes`` (the
per-entity narrative stays in prod + the tier SQL + ETHICS-012), and every other
field.

Matching
--------
578/599 match by ``name_original``. 14 are native-script renames in prod resolved
to their JSON (Latin) name by a vetted, id-keyed map (``RENAME_BY_ID``). 7 are
ambiguous renames or prod-only inserts (``SKIP_IDS``) left untouched — additive
entities absent from JSON that do not affect the collision fence; tracked as a
follow-up. Matching is intentionally explicit (no fuzzy auto-matching) because it
writes historical boundaries.

Idempotent: re-running after a successful apply changes nothing. The apply step
refuses to write unless the PostGIS-free fence is green on the result.

Usage
-----
    python -m scripts.backport_phase_h_to_json --dry-run   # report + fence, no write
    python -m scripts.backport_phase_h_to_json             # apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_DIR = ROOT / "data" / "entities"
EXPORT = ROOT / "data" / "fixes" / "phase_h_backport_export.json"

# Reviewed boundary state synced from prod. See module docstring for the rationale
# behind including confidence_score + status.
BOUNDARY_FIELDS = (
    "boundary_geojson",
    "boundary_source",
    "boundary_aourednik_name",
    "boundary_aourednik_year",
    "boundary_aourednik_precision",
    "boundary_ne_iso_a3",
    "confidence_score",
    "status",
)

# ETHICS-003: contested territories cannot exceed this confidence. Prod has 6
# disputed entities that slipped past enrichment with confidence > 0.70 (a latent
# prod bug). The backport must not write a value the project's own rule forbids,
# so we cap on the way in — identical to sync_boundaries_from_json. (Prod itself
# should be capped at the next deploy; out of scope here — NO prod deploy.)
DISPUTED_CONFIDENCE_CAP = 0.70

# Native-script renames done in prod (ETHICS-001) -> the JSON entity's current
# (Latin) name_original. Keyed by prod id (stable, ASCII). Each target is verified
# present in data/entities/*.json (the script aborts otherwise) and was
# corroborated by capital coordinates + period.
RENAME_BY_ID = {
    678: "Hetmanshchyna",                 # Гетьманщина — Cossack Hetmanate
    584: "Despotovina Srbije",            # Деспотовина Србија — Serbian Despotate
    665: "Zeta",                          # Зета
    679: "Polatskaye Knyastva",           # Полацкае княства — Principality of Polotsk
    667: "Raska",                         # Србија (1083, principality) — medieval Raška
    747: "Bazin",                         # بازين
    988: "Hammadids",                     # بنو حماد
    986: "Banu Midrar",                   # بنو مدرار
    985: "Dawla al-Rustamiyya",           # رستميون — Rustamid imamate
    705: "Lanfang Gongheguo",             # 蘭芳共和國 — Lanfang Republic
    1006: "Makhzumi Sultanate of Shewa",  # سلطنة شوا
    1009: "Mogadishu Sultanate early",    # سلطنة مقديشو
    1033: "Tunjur",                       # التنجر ("the Tunjur" — disambiguates shared capital)
    1032: "Daju Sultanate",               # سلطنة الداجو
}

# Prod-only inserts + ambiguous renames left untouched (additive; absent from
# JSON; do not affect the collision fence). Tracked as a names/entities follow-up.
SKIP_IDS = {
    530,   # 'Kingdom of Quito' — ambiguous (Quitu-Cara / Kitu)
    741,   # 'مقديشو' — ambiguous (Ajuuraan / Maqdishaw)
    1034,  # 'Res Publica Romana' — distinct polity from Imperium Romanum (insert)
    1037,  # 'Premier Empire français' — distinct from Royaume/Republique (insert)
    1038,  # 'افشاریان' — Afsharids (no JSON capital match; insert)
    1039,  # '𒆍𒀭𒊏𒆠 (Old Babylonian)' — ambiguous Babylon period entity
    1040,  # 'சோழர் (Sangam-era)' — no JSON capital match (insert)
}


def _set_field(ent: dict, key: str, value) -> bool:
    """Update in place (preserves key order). Add only meaningful (non-None) new
    keys so we never introduce spurious nulls. Returns True if the entity changed.
    """
    if key in ent:
        if ent[key] != value:
            ent[key] = value
            return True
        return False
    if value is not None:
        ent[key] = value
        return True
    return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Backport Phase H + iter boundaries JSON<-prod (audit #7).")
    parser.add_argument("--dry-run", action="store_true", help="Report + fence check; write nothing.")
    args = parser.parse_args(argv)

    # Native-script entity names are printed in the report; force UTF-8 so a
    # Windows cp1252 console (or any non-UTF-8 stream) cannot crash the run.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

    with open(EXPORT, encoding="utf-8") as fh:
        export = json.load(fh)

    # Build target map: json_name_original -> export row.
    target: dict[str, dict] = {}
    skipped: list[dict] = []
    capped_disputed = 0
    for r in export:
        if r["id"] in SKIP_IDS:
            skipped.append(r)
            continue
        # ETHICS-003 cap (see DISPUTED_CONFIDENCE_CAP).
        if r.get("status") == "disputed" and (r.get("confidence_score") or 0) > DISPUTED_CONFIDENCE_CAP:
            r["confidence_score"] = DISPUTED_CONFIDENCE_CAP
            capped_disputed += 1
        json_name = RENAME_BY_ID.get(r["id"], r["name_original"])
        target[json_name] = r
    expected = len(target)

    files = sorted(p for p in ENTITIES_DIR.glob("*.json") if not p.name.endswith(".bak"))
    parsed: dict[Path, list] = {}
    applied_names: set[str] = set()
    per_file_changes: dict[str, int] = {}
    for path in files:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        parsed[path] = data
        n_changed = 0
        for ent in data:
            name = ent.get("name_original")
            row = target.get(name)
            if row is None:
                continue
            applied_names.add(name)
            if any(_set_field(ent, f, row.get(f)) for f in BOUNDARY_FIELDS):
                n_changed += 1
        if n_changed:
            per_file_changes[path.name] = n_changed

    unmatched_targets = sorted(set(target) - applied_names)

    print(f"Export rows: {len(export)}  | targets: {expected}  | skipped (insert/ambiguous): {len(skipped)}")
    print(f"Matched in JSON: {len(applied_names)} / {expected}  | disputed capped to {DISPUTED_CONFIDENCE_CAP}: {capped_disputed}")
    if unmatched_targets:
        print("ERROR: target names not found in data/entities/*.json (bad RENAME_BY_ID?):")
        for n in unmatched_targets:
            print("   ", repr(n))
        return 2
    print("Per-file entities changed:")
    for fn, n in sorted(per_file_changes.items()):
        print(f"   {fn}: {n}")
    print("Skipped (prod-only insert / ambiguous rename — out of scope, follow-up):")
    for r in skipped:
        print(f"   id={r['id']} {r['name_original']!r} ({r['boundary_source']})")

    # PostGIS-free fence self-check on the resulting (deduped, last-wins) union.
    union: dict[str, dict] = {}
    for path in files:
        for ent in parsed[path]:
            union[ent.get("name_original")] = ent
    from src.ingestion.boundary_collision_guard import detect_json_boundary_collisions

    res = detect_json_boundary_collisions(list(union.values()))
    print(
        f"\nFENCE (PostGIS-free) on result: super_group_alerts={res['super_group_alert_count']} "
        f"big_groups={res['big_groups_count']} status={res['status']}"
    )
    for a in res["super_group_alerts"]:
        print(f"   SUPER '{a['boundary_aourednik_name']}' x{a['n_entities']} {a['year_range']}: {a['names'][:6]}")
    for g in res["big_groups"]:
        print(f"   BIG x{g['n_entities']}: {g['names'][:6]}")

    if args.dry_run:
        print("\nDRY-RUN: no files written.")
        return 0
    if res["status"] != "ok":
        print("\nABORT: fence not green after backport — refusing to write. Investigate above.")
        return 3

    # Write back with exact working-tree formatting: ensure_ascii=False, indent=2,
    # CRLF, no trailing newline (git autocrlf=true stores LF -> content-only diff).
    written = 0
    for path in files:
        if path.name not in per_file_changes:
            continue
        text = json.dumps(parsed[path], ensure_ascii=False, indent=2).replace("\n", "\r\n")
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        written += 1
    print(f"\nWrote {written} files. Backport applied to {len(applied_names)} entities.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
