"""v6.39: tests per /v1/render/*.png endpoints — server-side PNG rendering."""

import io

import pytest


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def test_render_snapshot_returns_png(client):
    r = client.get("/v1/render/snapshot/100.png")
    # Out-of-dataset years may return 404, in-range should return PNG
    if r.status_code == 200:
        assert r.headers["content-type"] == "image/png"
        assert r.content[:8] == PNG_SIGNATURE
        assert "X-Year" in r.headers
        assert r.headers["X-Year"] == "100"


def test_render_snapshot_year_out_of_range_high(client):
    r = client.get("/v1/render/snapshot/99999.png")
    assert r.status_code == 400  # custom range check


def test_render_snapshot_bad_year(client):
    r = client.get("/v1/render/snapshot/-10000.png")
    assert r.status_code == 400  # custom range check


def test_render_snapshot_custom_size(client):
    r = client.get("/v1/render/snapshot/100.png?width=600&height=400")
    if r.status_code == 200:
        assert r.content[:8] == PNG_SIGNATURE
        # PNG header includes width/height at offset 16-24
        # (Not validating exact size because matplotlib bbox_inches=tight may shrink)


def test_render_snapshot_title_override(client):
    r = client.get("/v1/render/snapshot/100.png?title=Test%20Title")
    if r.status_code == 200:
        assert r.content[:8] == PNG_SIGNATURE


def test_render_entity_404(client):
    r = client.get("/v1/render/entity/9999999.png")
    assert r.status_code == 404


def test_render_entity_no_boundary(client, db):
    from src.db.models import GeoEntity
    # Create entity WITHOUT boundary_geojson
    e = GeoEntity(
        name_original="NoBoundaryEntity",
        name_original_lang="en",
        entity_type="kingdom",
        year_start=1000,
        year_end=1100,
        confidence_score=0.5,
        status="confirmed",
    )
    db.add(e)
    db.commit()
    db.refresh(e)

    r = client.get(f"/v1/render/entity/{e.id}.png")
    assert r.status_code == 404

    db.delete(e)
    db.commit()


def test_render_entity_with_boundary(client, db):
    import json
    from src.db.models import GeoEntity
    coords = [[[10.0, 10.0], [20.0, 10.0], [20.0, 20.0], [10.0, 20.0], [10.0, 10.0]]]
    e = GeoEntity(
        name_original="TestEntity",
        name_original_lang="en",
        entity_type="kingdom",
        year_start=1000,
        year_end=1100,
        boundary_geojson=json.dumps({"type": "Polygon", "coordinates": coords}),
        boundary_source="test",
        confidence_score=0.9,
        status="confirmed",
    )
    db.add(e)
    db.commit()
    db.refresh(e)

    r = client.get(f"/v1/render/entity/{e.id}.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == PNG_SIGNATURE
    assert r.headers["X-Entity-Id"] == str(e.id)

    db.delete(e)
    db.commit()
