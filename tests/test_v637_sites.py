"""v6.37: tests per /v1/sites endpoint family (ArchaeologicalSite).

Verifica:
- CRUD base del modello in SQLite
- GET /v1/sites (paginato, con filtri)
- GET /v1/sites/types (enum con counts)
- GET /v1/sites/unesco (shortcut filter)
- GET /v1/sites/nearby (haversine)
- GET /v1/sites/{id} (detail + 404)
- Validazioni: lat/lon range, confidence range
- ETHICS-009: nome originale primario, name_variants con context coloniale
"""

import json

import pytest

from src.db.models import ArchaeologicalSite


# ─── Helpers ─────────────────────────────────────────────────────────

def _insert_test_site(
    db,
    name: str = "Pompeii",
    name_lang: str = "la",
    lat: float = 40.75,
    lon: float = 14.49,
    site_type: str = "ruins",
    date_start: int | None = -200,
    date_end: int | None = 79,
    unesco_id: str | None = None,
    unesco_year: int | None = None,
    status: str = "confirmed",
) -> ArchaeologicalSite:
    site = ArchaeologicalSite(
        name_original=name,
        name_original_lang=name_lang,
        latitude=lat,
        longitude=lon,
        site_type=site_type,
        date_start=date_start,
        date_end=date_end,
        unesco_id=unesco_id,
        unesco_year=unesco_year,
        confidence_score=0.9,
        status=status,
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


def _cleanup_test_sites(db):
    """Remove test sites to isolate tests."""
    db.query(ArchaeologicalSite).delete()
    db.commit()


# ─── Tests: model CRUD ───────────────────────────────────────────────

def test_archaeological_site_insert_roundtrip(db):
    _cleanup_test_sites(db)
    site = _insert_test_site(db, name="Pompeii")
    assert site.id is not None
    assert site.name_original == "Pompeii"
    assert site.latitude == 40.75
    assert site.confidence_score == 0.9
    _cleanup_test_sites(db)


def test_archaeological_site_with_unesco(db):
    _cleanup_test_sites(db)
    site = _insert_test_site(
        db,
        name="Pompei area (UNESCO)",
        unesco_id="829",
        unesco_year=1997,
    )
    assert site.unesco_id == "829"
    assert site.unesco_year == 1997
    _cleanup_test_sites(db)


def test_archaeological_site_check_constraint_lat(db):
    """lat > 90 → DB check constraint deve fallire."""
    _cleanup_test_sites(db)
    with pytest.raises(Exception):
        db.add(ArchaeologicalSite(
            name_original="Invalid",
            name_original_lang="xx",
            latitude=100.0,  # INVALID
            longitude=0.0,
            site_type="other",
            confidence_score=0.5,
            status="confirmed",
        ))
        db.commit()
    db.rollback()
    _cleanup_test_sites(db)


# ─── Tests: API endpoints ────────────────────────────────────────────

def test_list_sites_empty(client, db):
    _cleanup_test_sites(db)
    r = client.get("/v1/sites")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["sites"] == []


def test_list_sites_with_fixture(client, db):
    _cleanup_test_sites(db)
    _insert_test_site(db, name="Pompeii", lat=40.75, lon=14.49)
    _insert_test_site(db, name="Stonehenge", lat=51.179, lon=-1.826, site_type="megalithic")
    r = client.get("/v1/sites")
    assert r.status_code == 200
    names = [s["name_original"] for s in r.json()["sites"]]
    assert "Pompeii" in names
    assert "Stonehenge" in names
    _cleanup_test_sites(db)


def test_list_sites_filter_site_type(client, db):
    _cleanup_test_sites(db)
    _insert_test_site(db, name="TestRuins", site_type="ruins")
    _insert_test_site(db, name="TestTemple", site_type="temple")
    r = client.get("/v1/sites?site_type=temple")
    assert r.status_code == 200
    names = [s["name_original"] for s in r.json()["sites"]]
    assert "TestTemple" in names
    assert "TestRuins" not in names
    _cleanup_test_sites(db)


def test_list_sites_year_filter(client, db):
    _cleanup_test_sites(db)
    # Old site: 500 BCE - 200 CE
    _insert_test_site(db, name="OldSite", date_start=-500, date_end=200)
    # Modern site: 1800 CE - ongoing
    _insert_test_site(db, name="ModernSite", date_start=1800, date_end=None, lat=0, lon=0)
    # Query year 1900: should get ModernSite, not OldSite
    r = client.get("/v1/sites?year=1900")
    names = [s["name_original"] for s in r.json()["sites"]]
    assert "ModernSite" in names
    assert "OldSite" not in names
    # Query year 0: should get OldSite
    r = client.get("/v1/sites?year=0")
    names = [s["name_original"] for s in r.json()["sites"]]
    assert "OldSite" in names
    assert "ModernSite" not in names
    _cleanup_test_sites(db)


def test_list_sites_unesco_only(client, db):
    _cleanup_test_sites(db)
    _insert_test_site(db, name="UnescoSite", unesco_id="829")
    _insert_test_site(db, name="NonUnescoSite", unesco_id=None)
    r = client.get("/v1/sites?unesco_only=true")
    names = [s["name_original"] for s in r.json()["sites"]]
    assert "UnescoSite" in names
    assert "NonUnescoSite" not in names
    _cleanup_test_sites(db)


def test_site_types_endpoint(client, db):
    _cleanup_test_sites(db)
    _insert_test_site(db, name="S1", site_type="ruins")
    _insert_test_site(db, name="S2", site_type="ruins")
    _insert_test_site(db, name="S3", site_type="temple")
    r = client.get("/v1/sites/types")
    assert r.status_code == 200
    data = r.json()
    by_type = {row["site_type"]: row["count"] for row in data}
    assert by_type.get("ruins") == 2
    assert by_type.get("temple") == 1
    _cleanup_test_sites(db)


def test_unesco_shortcut(client, db):
    _cleanup_test_sites(db)
    _insert_test_site(db, name="U1", unesco_id="1", unesco_year=1979)
    _insert_test_site(db, name="U2", unesco_id="2", unesco_year=1985)
    _insert_test_site(db, name="NonU", unesco_id=None)
    r = client.get("/v1/sites/unesco")
    assert r.status_code == 200
    data = r.json()
    names = [s["name_original"] for s in data["sites"]]
    assert "NonU" not in names
    assert len(names) == 2
    # Order: newer inscription first
    assert data["sites"][0]["unesco_year"] >= data["sites"][1]["unesco_year"]
    _cleanup_test_sites(db)


def test_sites_nearby(client, db):
    _cleanup_test_sites(db)
    # Rome
    _insert_test_site(db, name="Colosseum", lat=41.89, lon=12.49)
    # Napoli
    _insert_test_site(db, name="Pompeii", lat=40.75, lon=14.49)
    # London (far)
    _insert_test_site(db, name="Stonehenge", lat=51.179, lon=-1.826)

    # Search within 300 km of Rome → should find Colosseum (~0km) + Pompeii (~190km)
    r = client.get("/v1/sites/nearby?lat=41.9&lon=12.5&radius=300")
    data = r.json()
    names = [s["name_original"] for s in data["sites"]]
    assert "Colosseum" in names
    assert "Pompeii" in names
    assert "Stonehenge" not in names
    # Ordered by distance
    assert data["sites"][0]["distance_km"] < data["sites"][1]["distance_km"]
    _cleanup_test_sites(db)


def test_get_site_detail_and_404(client, db):
    _cleanup_test_sites(db)
    site = _insert_test_site(db, name="TestSite")
    r = client.get(f"/v1/sites/{site.id}")
    assert r.status_code == 200
    assert r.json()["name_original"] == "TestSite"

    r = client.get("/v1/sites/999999")
    assert r.status_code == 404
    _cleanup_test_sites(db)


def test_site_with_name_variants_and_sources(client, db):
    """ETHICS-009: colonial renaming documented."""
    _cleanup_test_sites(db)
    site = ArchaeologicalSite(
        name_original="Uluru",
        name_original_lang="pjt",  # Pitjantjatjara
        latitude=-25.345,
        longitude=131.036,
        site_type="sacred_site",
        date_start=-4000,
        date_end=None,
        unesco_id="447",
        unesco_year=1987,
        confidence_score=0.95,
        status="confirmed",
        ethical_notes="ETHICS-009: colonial name 'Ayers Rock' imposed 1873; dual-name policy 1993; climbing ban 2019 returning full control to Aṉangu traditional owners",
        name_variants=json.dumps([
            {"name": "Ayers Rock", "lang": "en", "context": "colonial imposition 1873-1993"},
            {"name": "Uluru / Ayers Rock", "lang": "en", "context": "dual-name 1993-2002"},
        ], ensure_ascii=False),
        sources=json.dumps([
            {"citation": "Mountford, C.P. (1965). Ayers Rock: Its People, Their Beliefs, and Their Art.", "source_type": "academic"},
        ], ensure_ascii=False),
    )
    db.add(site)
    db.commit()
    db.refresh(site)

    r = client.get(f"/v1/sites/{site.id}")
    data = r.json()
    assert data["name_original"] == "Uluru"
    assert data["name_original_lang"] == "pjt"
    assert len(data["name_variants"]) == 2
    assert data["name_variants"][0]["name"] == "Ayers Rock"
    assert "colonial" in data["name_variants"][0]["context"]
    _cleanup_test_sites(db)
