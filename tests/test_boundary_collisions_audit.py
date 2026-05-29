"""Phase H boundary collision audit: CI guard against super-group polygon regression.

v6.99.79 — third level of defense (after ETHICS-006 audit + capital-in-polygon).

Background:
    Phase H boundary review (May 2026) discovered ~250 entities with polygon
    collisions caused by aourednik + natural_earth fuzzy-matching errors.
    Historical entities like "Bunyoro pre-Babito" got matched to "Bantou"
    (all sub-Saharan Africa), "Fatimid Caliphate" was assigned to 6 different
    Levantine states (Ikhshidids, Zirids, Ayyubids, Crusader Jerusalem, etc.),
    "Sui Empire" polygon was assigned to 4 pre-Sui dynasties, etc.

    After fixes, the DB went from ~100 collision groups (worst: 10 entities
    sharing modern Ethiopia polygon) to ~40 minor collisions (mostly known
    duplicates flagged for merge).

    This audit catches REGRESSIONS — if a future ingestion re-introduces
    the super-group matching pattern, CI fails before the PR can merge.

Thresholds:
    * MAX_COLLISION_GROUPS = 60 — current baseline is ~40, jump to >60
      signals regression
    * MAX_BIG_GROUP_SIZE = 4 — single group of 4+ entities sharing polygon
      is suspect (was 10 for Ethiopia pre-fix)
    * No super-group alerts — any entity group sharing same
      boundary_aourednik_name AND spanning >200 years is a strong
      regression signal (different polities should NOT share aourednik
      match label across centuries)

Failure mode:
    Pytest output lists the colliding groups with entity names and
    boundary_aourednik_name — fix by either:
      a) Updating the matcher to reject this super-group label
      b) Adding the entities to MANUALLY_CURATED_IDS with distinct circles
      c) Marking duplicates for merge in a follow-up cleanup PR
"""

from __future__ import annotations

import pytest

MAX_COLLISION_GROUPS = 60  # baseline post-Phase-H is ~40
MAX_BIG_GROUP_SIZE = 4  # group of 4+ entities sharing polygon = suspect


def test_no_super_group_collision_regression():
    """No new super-group collision regressions vs Phase H baseline.

    A "super-group collision" is when N >= MAX_BIG_GROUP_SIZE entities share
    a byte-identical polygon AND share the same boundary_aourednik_name.

    Examples of historical regressions caught by this test:
      * 10 Ethiopian polities (1270-1830) sharing modern Ethiopia polygon
      * 7 Indonesian sultanates sharing Dutch East Indies polygon
      * 6 medieval Levantine states sharing "Fatimid Caliphate" polygon
      * 4 Bantu-area kingdoms (Bunyoro, Bigo, Ntusi, Mbundu) sharing
        entire sub-Saharan-Africa "Bantou" polygon

    Skip when DB unavailable (CI without Postgres container).
    """
    try:
        from src.db.database import is_postgres
    except ImportError:
        pytest.skip("src.db.database not importable")
    if not is_postgres:
        pytest.skip("PostgreSQL required for boundary collision audit (PostGIS)")

    from src.ingestion.boundary_collision_guard import detect_boundary_collisions

    result = detect_boundary_collisions()
    if result.get("status") == "skip":
        pytest.skip(result.get("reason", "guard skipped"))

    super_group_alerts = result.get("super_group_alerts", [])
    if super_group_alerts:
        msg_lines = [
            f"REGRESSION: {len(super_group_alerts)} super-group polygon collisions detected.",
            "",
            "Each group below is N entities sharing the SAME boundary_aourednik_name",
            "AND spanning > 200 years — this is the exact pattern Phase H fixed.",
            "Fix: update src/ingestion/boundary_match.py to reject these super-group",
            "labels, or update the entities to MANUALLY_CURATED_IDS with distinct circles.",
            "",
        ]
        for alert in super_group_alerts[:5]:
            msg_lines.append(
                f"  • '{alert['boundary_aourednik_name']}' (years "
                f"{alert['year_range'][0]} to {alert['year_range'][1]}) "
                f"shared by {alert['n_entities']} entities:"
            )
            for name in alert["names"][:5]:
                msg_lines.append(f"      - {name}")
            if alert["n_entities"] > 5:
                msg_lines.append(f"      ... and {alert['n_entities'] - 5} more")
        pytest.fail("\n".join(msg_lines))


def test_collision_count_within_baseline():
    """Total polygon-collision groups must stay below MAX_COLLISION_GROUPS.

    Post-Phase-H baseline: ~40 minor collisions (mostly known duplicate
    pairs flagged for merge). Allowable drift up to MAX_COLLISION_GROUPS=60.

    A jump beyond signals that a new ingestion batch added many entities
    matched to wrong polygons via fuzzy match.
    """
    try:
        from src.db.database import is_postgres
    except ImportError:
        pytest.skip("src.db.database not importable")
    if not is_postgres:
        pytest.skip("PostgreSQL required")

    from src.ingestion.boundary_collision_guard import detect_boundary_collisions

    result = detect_boundary_collisions()
    if result.get("status") == "skip":
        pytest.skip(result.get("reason", "guard skipped"))

    total_groups = result.get("total_groups", 0)
    assert total_groups <= MAX_COLLISION_GROUPS, (
        f"Collision group count {total_groups} exceeds baseline {MAX_COLLISION_GROUPS}. "
        f"Phase H reduced this from 100+ to ~40 — jump indicates ingestion regression. "
        f"big_groups={result.get('big_groups_count', 0)} "
        f"super_group_alerts={result.get('super_group_alert_count', 0)}"
    )


def test_no_big_collision_groups():
    """No single polygon should be shared by 4+ entities (suspect fuzzy match).

    Known acceptable exceptions (legitimate sharing as of Phase H):
      - Cultural-zone polygons with their primary cultural-zone entity AND
        member sub-units (e.g., Wari Empire + 0 members because we corrected
        all to circles).

    If this test fails, investigate the listed group — likely fuzzy-match
    regression.
    """
    try:
        from src.db.database import is_postgres
    except ImportError:
        pytest.skip("src.db.database not importable")
    if not is_postgres:
        pytest.skip("PostgreSQL required")

    from src.ingestion.boundary_collision_guard import detect_boundary_collisions

    result = detect_boundary_collisions()
    if result.get("status") == "skip":
        pytest.skip(result.get("reason", "guard skipped"))

    big_groups = result.get("big_groups", [])
    if big_groups:
        msg_lines = [
            f"REGRESSION: {len(big_groups)} polygons shared by {MAX_BIG_GROUP_SIZE}+ entities.",
            "",
            "Investigate each group — likely fuzzy-match error in ingestion.",
            "Fix: split per-entity polygons or document as legitimate sharing.",
            "",
        ]
        for grp in big_groups[:5]:
            msg_lines.append(
                f"  • Area {grp['area_deg2']:.2f} deg² shared by "
                f"{grp['n_entities']} entities:"
            )
            for name in grp["names"][:5]:
                msg_lines.append(f"      - {name}")
            if grp["n_entities"] > 5:
                msg_lines.append(f"      ... and {grp['n_entities'] - 5} more")
        pytest.fail("\n".join(msg_lines))
