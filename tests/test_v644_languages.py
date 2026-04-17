"""v6.44: tests per HistoricalLanguage + /v1/languages endpoints."""

import pytest


def test_list_languages_returns_seed_data(client):
    """Il seed tramite lifespan ha popolato le 30 lingue core."""
    r = client.get("/v1/languages?limit=200")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 20, f"expected seed languages, got {data['total']}"


def test_list_languages_filter_family(client):
    r = client.get("/v1/languages?family=Indo-European&limit=50")
    assert r.status_code == 200
    langs = r.json()["languages"]
    assert len(langs) > 0
    for l in langs:
        assert "Indo-European" in (l.get("family") or "")


def test_list_languages_filter_vitality(client):
    r = client.get("/v1/languages?vitality_status=endangered")
    assert r.status_code == 200
    langs = r.json()["languages"]
    for l in langs:
        assert l["vitality_status"] == "endangered"


def test_languages_at_year(client):
    """Languages at year=0 (CE boundary) — Latin, Greek, Sanskrit, Old Chinese, etc."""
    r = client.get("/v1/languages/at-year/0")
    assert r.status_code == 200
    langs = r.json()["languages"]
    names = [l["name_original"] for l in langs]
    assert any("Latina" in n or "Latin" in n for n in names)


def test_languages_at_year_invalid(client):
    r = client.get("/v1/languages/at-year/99999")
    assert r.status_code == 400


def test_language_families_endpoint(client):
    r = client.get("/v1/languages/families")
    assert r.status_code == 200
    families = r.json()
    # Seed has multiple families
    assert len(families) >= 3


def test_get_language_404(client):
    r = client.get("/v1/languages/9999999")
    assert r.status_code == 404


def test_language_ethical_notes_present(client):
    """Colonial suppression cases documented."""
    r = client.get("/v1/languages?limit=200")
    langs = r.json()["languages"]
    with_ethics = [l for l in langs if l.get("ethical_notes")]
    # Seed should have multiple entries with ethical_notes (Hawaiian, Nahuatl, Kurdish, Aramaic, etc.)
    assert len(with_ethics) >= 5
