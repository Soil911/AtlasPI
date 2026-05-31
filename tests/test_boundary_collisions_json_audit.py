"""PostGIS-free boundary-collision fence over the JSON source — Wave 2 audit #7.

This is the fast half of the collision fence (the other half is
``scripts/ci_collision_check.py``, which runs the real PostGIS guard in the
Postgres CI job). It runs on every PR inside the normal SQLite ``test`` job
because it needs no database at all: it loads ``data/entities/*.json`` exactly
the way ``seed_database()`` does (dedup, last-wins) and checks for the Phase H
super-group regression directly on the source of truth a fresh seed would load.

Background (ETHICS-012): the fuzzy boundary matcher once assigned the SAME
upstream "super-group" polygon (e.g. the whole "Bantou" linguistic area, or
modern Ethiopia) to many historically-distinct entities. Phase H + the iter
series replaced those with capital circles / hand-drawn polygons IN PROD ONLY —
so until the 2026-05-31 JSON backport a fresh seed reproduced ~22 collision
groups. This test fails if that drift ever returns: a new ingestion batch that
re-introduces a shared super-group polygon turns the suite red before merge.

It catches *byte-identical* shared polygons among the fuzzy sources
(aourednik / natural_earth), which is the precise signature of the bug. The
PostGIS job additionally covers equal-area collisions on the live geometry.
"""

from __future__ import annotations

from src.db.seed import load_all_entities
from src.ingestion.boundary_collision_guard import detect_json_boundary_collisions


def _format_failure(result: dict) -> str:
    lines = [
        f"REGRESSION: {result['super_group_alert_count']} super-group collision(s) "
        f"and {result['big_groups_count']} big shared-polygon group(s) in "
        "data/entities/*.json.",
        "",
        "This is the Phase H pattern (see docs/ethics/ETHICS-012): the fuzzy",
        "matcher assigned ONE upstream polygon to several distinct entities.",
        "Fix the offending batch (give per-entity circles / real polygons, or",
        "reject the super-group label in src/ingestion/aourednik_match.py).",
        "",
    ]
    for a in result["super_group_alerts"][:8]:
        names = ", ".join(a["names"][:5])
        more = "" if a["n_entities"] <= 5 else f" (+{a['n_entities'] - 5} more)"
        lines.append(
            f"  • '{a['boundary_aourednik_name']}' shared by {a['n_entities']} "
            f"entities spanning {a['year_range'][0]}..{a['year_range'][1]}: {names}{more}"
        )
    for g in result["big_groups"][:8]:
        names = ", ".join(str(n) for n in g["names"][:5])
        lines.append(f"  • {g['n_entities']} entities share one byte-identical polygon: {names}")
    return "\n".join(lines)


def test_json_source_has_no_super_group_collisions():
    """data/entities/*.json must not contain Phase H super-group polygon sharing."""
    entities = load_all_entities()
    assert entities, "no entities loaded from data/entities/*.json"

    result = detect_json_boundary_collisions(entities)

    assert result["super_group_alert_count"] == 0 and result["big_groups_count"] == 0, (
        _format_failure(result)
    )


def test_detector_flags_a_synthetic_super_group():
    """Guard the guard: a synthetic shared super-group polygon must be detected.

    Without this, a bug that makes the detector silently return 0 would let the
    real fence pass vacuously.
    """
    shared = {"type": "Polygon", "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]}
    entities = [
        {"name_original": "A", "boundary_source": "aourednik",
         "boundary_aourednik_name": "Bantou", "year_start": 1000, "boundary_geojson": shared},
        {"name_original": "B", "boundary_source": "aourednik",
         "boundary_aourednik_name": "Bantou", "year_start": 1400, "boundary_geojson": shared},
    ]
    result = detect_json_boundary_collisions(entities)
    assert result["super_group_alert_count"] == 1
    assert result["super_group_alerts"][0]["boundary_aourednik_name"] == "Bantou"
