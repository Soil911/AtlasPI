"""CI audit: every non-approximate boundary must have its capital within
tolerance of the polygon.

ETHICS-006 (v6.1.2): the Natural Earth fuzzy matcher produced 133 "displaced"
matches where the entity's capital was outside the assigned polygon
(Garenganze -> Russia, CSA -> Italy, Mapuche -> Australia).

ETHICS-006 v6.2 follow-up: after adding NE fuzzy + aourednik fuzzy geographic
guards, the DB audit found 22 additional pre-existing displaced aourednik
matches (Kerajaan Kediri -> Kingdom of Georgia at 9,000 km, Mrauk-U -> Akan
at 10,000 km). Those were reset to approximate_generated.

This test locks the invariant in: any entity with
`boundary_source in {natural_earth, aourednik}` AND valid capital coords AND
valid GeoJSON must have its capital within
BOUNDARY_DISPLACEMENT_TOLERANCE_KM (50 km) of the matched polygon.

Why 50 km and not 0 km:
  - Sweden (Stockholm) is 0.4 km off the simplified NE coast polygon.
  - Denmark-Norway, Scotland, Orissa similar cases (< 10 km offset).
  - Strict capital-in-polygon would reject these obviously correct matches.
  - 50 km catches 100% of the cross-continent disasters we observed
    empirically while tolerating coastal digitization noise.

Historical note: the test is intentionally limited to natural_earth +
aourednik. Sources historical_map / academic_source are manually curated
and cover edge cases (overseas colonies, vassal-suzerain pairs) where the
capital-in-polygon invariant isn't always meaningful.
"""

from __future__ import annotations

import json

import pytest

pytest.importorskip("shapely", reason="geographic audit needs shapely")

from src.db.database import SessionLocal
from src.db.models import GeoEntity
from src.ingestion.boundary_match import _capital_distance_to_polygon_km

BOUNDARY_DISPLACEMENT_TOLERANCE_KM = 50.0
AUDITED_SOURCES = ("natural_earth", "aourednik")


def _iter_audited_rows():
    session = SessionLocal()
    try:
        rows = (
            session.query(GeoEntity)
            .filter(GeoEntity.boundary_source.in_(AUDITED_SOURCES))
            .all()
        )
        for row in rows:
            yield row
    finally:
        session.close()


def test_no_displaced_boundaries_beyond_tolerance():
    """The regression guard: no NE/aourednik match with capital >50 km from polygon."""
    offenders: list[tuple[GeoEntity, float]] = []

    for row in _iter_audited_rows():
        if row.capital_lat is None or row.capital_lon is None:
            continue
        if not row.boundary_geojson:
            continue
        try:
            geo = json.loads(row.boundary_geojson)
        except (ValueError, TypeError):
            continue
        km = _capital_distance_to_polygon_km(
            {"capital_lat": row.capital_lat, "capital_lon": row.capital_lon},
            geo,
        )
        if km is None:
            continue
        if km > BOUNDARY_DISPLACEMENT_TOLERANCE_KM:
            offenders.append((row, km))

    if offenders:
        lines = [
            f"{len(offenders)} entities have capital >"
            f"{BOUNDARY_DISPLACEMENT_TOLERANCE_KM} km from their matched polygon.",
            "This indicates either a displaced fuzzy match (ETHICS-006) or a "
            "semantically wrong exact-name match. Either fix the data or run:",
            "  python -m src.ingestion.rematch_approximate  # reset + rematch",
            "",
            "First 20 offenders:",
        ]
        for row, km in sorted(offenders, key=lambda x: -x[1])[:20]:
            ao = row.boundary_aourednik_name or row.boundary_ne_iso_a3
            lines.append(
                f"  id={row.id} src={row.boundary_source} "
                f"{row.name_original!r} -> {ao!r} (capital {km:.0f} km off polygon)"
            )
        pytest.fail("\n".join(lines))


def test_no_null_source_with_real_polygon():
    """If an entity has a real GeoJSON polygon, its boundary_source must not
    be NULL — otherwise the API exposes provenance=None which breaks
    consumers that gate on ETHICS-005 source tiers.
    """
    session = SessionLocal()
    try:
        rows = (
            session.query(GeoEntity)
            .filter(
                GeoEntity.boundary_geojson.isnot(None),
                GeoEntity.boundary_source.is_(None),
            )
            .all()
        )
        offenders = [(r.id, r.name_original) for r in rows]
    finally:
        session.close()

    if offenders:
        sample = ", ".join(f"id={eid} {name!r}" for eid, name in offenders[:5])
        pytest.fail(
            f"{len(offenders)} entities have boundary_geojson but NULL "
            f"boundary_source — ETHICS-005 provenance gap. Samples: {sample}"
        )


def test_tolerance_constant_is_reasonable():
    """Meta-test: the tolerance threshold hasn't been silently widened.

    If someone relaxes the guard to a much larger value (say 500 km),
    this test flags it — 500 km is enough to re-introduce regional
    misalignment between vassal states and suzerains.
    """
    assert BOUNDARY_DISPLACEMENT_TOLERANCE_KM <= 100.0, (
        f"Displacement tolerance of {BOUNDARY_DISPLACEMENT_TOLERANCE_KM} km "
        "is too permissive — at that distance, a vassal state's capital "
        "could land inside the suzerain's polygon (see ETHICS-006). "
        "Keep it at 50 km unless you have a documented ADR."
    )
    assert BOUNDARY_DISPLACEMENT_TOLERANCE_KM >= 10.0, (
        f"Displacement tolerance of {BOUNDARY_DISPLACEMENT_TOLERANCE_KM} km "
        "is too strict — it rejects legitimate coastal digitization "
        "noise (Sweden/Stockholm ~0.4 km, Scotland/Edinburgh ~6 km)."
    )
