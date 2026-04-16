"""Tests for Historical Periods v6.27.

Tests:
  - GET /v1/periods — list, filter, pagination
  - GET /v1/periods/types — enum
  - GET /v1/periods/regions — enum
  - GET /v1/periods/at-year/{year} — range query
  - GET /v1/periods/by-slug/{slug} — slug lookup
  - GET /v1/periods/{id} — detail
  - Data integrity: slugs unique, years valid
  - Ethics: historiographic notes, alternative names present
"""

import json


# ═══════════════════════════════════════════════════════════════════
# 1. GET /v1/periods (list + filter)
# ═══════════════════════════════════════════════════════════════════


def test_list_periods_returns_200(client):
    r = client.get("/v1/periods")
    assert r.status_code == 200
    d = r.json()
    assert "total" in d
    assert "periods" in d
    assert d["total"] >= 30


def test_list_periods_has_required_fields(client):
    r = client.get("/v1/periods?limit=1")
    d = r.json()
    assert len(d["periods"]) == 1
    p = d["periods"][0]
    for key in ("id", "name", "slug", "period_type", "region",
                "year_start", "year_end", "confidence_score", "status"):
        assert key in p


def test_list_periods_ordered_by_year(client):
    r = client.get("/v1/periods?limit=500")
    d = r.json()
    years = [p["year_start"] for p in d["periods"]]
    assert years == sorted(years)


def test_filter_by_region_europe(client):
    r = client.get("/v1/periods?region=europe")
    d = r.json()
    assert d["total"] >= 5
    for p in d["periods"]:
        assert p["region"] == "europe"


def test_filter_by_period_type_era(client):
    r = client.get("/v1/periods?period_type=era")
    d = r.json()
    assert d["total"] >= 1
    for p in d["periods"]:
        assert p["period_type"] == "era"


def test_filter_by_year_returns_periods_containing_year(client):
    # 1500 should include Renaissance, Late Middle Ages, Early Modern, Ottoman Classical Age
    r = client.get("/v1/periods?year=1500")
    d = r.json()
    assert d["total"] >= 3
    for p in d["periods"]:
        assert p["year_start"] <= 1500
        assert p["year_end"] is None or p["year_end"] >= 1500


def test_filter_by_year_bce(client):
    # -500 (500 BCE) should include Iron Age, Archaic Period, Roman Republic, etc
    r = client.get("/v1/periods?year=-500")
    d = r.json()
    assert d["total"] >= 1
    for p in d["periods"]:
        assert p["year_start"] <= -500


def test_pagination_works(client):
    r1 = client.get("/v1/periods?limit=5&offset=0")
    r2 = client.get("/v1/periods?limit=5&offset=5")
    d1 = r1.json()
    d2 = r2.json()
    assert len(d1["periods"]) == 5
    assert len(d2["periods"]) >= 1
    # No overlap
    ids1 = {p["id"] for p in d1["periods"]}
    ids2 = {p["id"] for p in d2["periods"]}
    assert not (ids1 & ids2)


# ═══════════════════════════════════════════════════════════════════
# 2. GET /v1/periods/types and /v1/periods/regions
# ═══════════════════════════════════════════════════════════════════


def test_types_endpoint(client):
    r = client.get("/v1/periods/types")
    assert r.status_code == 200
    d = r.json()
    assert "types" in d
    # Expect multiple types
    assert len(d["types"]) >= 3
    assert "age" in d["types"]


def test_regions_endpoint(client):
    r = client.get("/v1/periods/regions")
    assert r.status_code == 200
    d = r.json()
    assert "regions" in d
    assert "europe" in d["regions"]
    assert "global" in d["regions"]


# ═══════════════════════════════════════════════════════════════════
# 3. GET /v1/periods/at-year/{year}
# ═══════════════════════════════════════════════════════════════════


def test_at_year_returns_200(client):
    r = client.get("/v1/periods/at-year/1500")
    assert r.status_code == 200
    d = r.json()
    assert d["year"] == 1500
    assert "total" in d
    assert "periods" in d


def test_at_year_1789_includes_enlightenment(client):
    r = client.get("/v1/periods/at-year/1789")
    d = r.json()
    slugs = {p["slug"] for p in d["periods"]}
    assert "age-of-enlightenment" in slugs


def test_at_year_negative(client):
    """BCE years work (negative integers)."""
    r = client.get("/v1/periods/at-year/-500")
    assert r.status_code == 200
    d = r.json()
    assert d["year"] == -500


def test_at_year_region_filter(client):
    r = client.get("/v1/periods/at-year/1500?region=europe")
    d = r.json()
    for p in d["periods"]:
        assert p["region"] == "europe"


# ═══════════════════════════════════════════════════════════════════
# 4. GET /v1/periods/by-slug/{slug}
# ═══════════════════════════════════════════════════════════════════


def test_by_slug_bronze_age(client):
    r = client.get("/v1/periods/by-slug/bronze-age")
    assert r.status_code == 200
    d = r.json()
    assert d["slug"] == "bronze-age"
    assert d["name"] == "Bronze Age"
    assert "description" in d
    assert d["year_start"] == -3300


def test_by_slug_has_detail_fields(client):
    r = client.get("/v1/periods/by-slug/bronze-age")
    d = r.json()
    # Full detail fields expected
    for key in ("description", "historiographic_note", "alternative_names", "sources"):
        assert key in d


def test_by_slug_edo_period_has_native_name(client):
    """Japanese period should have native name."""
    r = client.get("/v1/periods/by-slug/edo-period")
    d = r.json()
    assert d["name_native"] == "江戸時代"
    assert d["name_native_lang"] == "ja"


def test_by_slug_not_found_returns_404(client):
    r = client.get("/v1/periods/by-slug/nonexistent-period-xyz")
    assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# 5. GET /v1/periods/{id}
# ═══════════════════════════════════════════════════════════════════


def test_period_detail_by_id(client):
    # Get first period to know an id
    r_list = client.get("/v1/periods?limit=1")
    first_id = r_list.json()["periods"][0]["id"]

    r = client.get(f"/v1/periods/{first_id}")
    assert r.status_code == 200
    d = r.json()
    assert d["id"] == first_id
    assert "description" in d


def test_period_detail_not_found(client):
    r = client.get("/v1/periods/999999")
    assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# 6. Data integrity
# ═══════════════════════════════════════════════════════════════════


def test_all_slugs_are_unique(client):
    r = client.get("/v1/periods?limit=500")
    d = r.json()
    slugs = [p["slug"] for p in d["periods"]]
    assert len(slugs) == len(set(slugs))


def test_years_are_consistent(client):
    """year_end >= year_start when both are defined."""
    r = client.get("/v1/periods?limit=500")
    d = r.json()
    for p in d["periods"]:
        if p["year_end"] is not None:
            assert p["year_end"] >= p["year_start"], f"{p['name']}: {p['year_start']} > {p['year_end']}"


def test_confidence_scores_in_range(client):
    r = client.get("/v1/periods?limit=500")
    d = r.json()
    for p in d["periods"]:
        assert 0.0 <= p["confidence_score"] <= 1.0


# ═══════════════════════════════════════════════════════════════════
# 7. Ethics (historiographic annotations)
# ═══════════════════════════════════════════════════════════════════


def test_early_middle_ages_has_alternative_names(client):
    """Early Middle Ages should list 'Dark Ages' as deprecated alt."""
    r = client.get("/v1/periods/by-slug/early-middle-ages")
    d = r.json()
    alt_names = d.get("alternative_names") or []
    names_list = [a.get("name") for a in alt_names]
    assert "Dark Ages" in names_list


def test_age_of_discovery_has_ethical_note(client):
    """Age of Discovery should have ETHICS framing in historiographic_note."""
    r = client.get("/v1/periods/by-slug/age-of-discovery")
    d = r.json()
    assert d.get("historiographic_note") is not None
    assert "ETHICS" in d["historiographic_note"] or "colonial" in d["historiographic_note"].lower()


def test_pre_columbian_has_ethical_note(client):
    """Pre-Columbian Era should acknowledge Eurocentric framing."""
    r = client.get("/v1/periods/by-slug/pre-columbian-era")
    d = r.json()
    assert d.get("historiographic_note") is not None
    note = d["historiographic_note"].lower()
    assert "eurocentric" in note or "indigenous" in note or "contact" in note


# ═══════════════════════════════════════════════════════════════════
# 8. Classic period lookups (smoke tests for famous periods)
# ═══════════════════════════════════════════════════════════════════


def test_bronze_age_found(client):
    r = client.get("/v1/periods/by-slug/bronze-age")
    d = r.json()
    assert d["year_start"] == -3300
    assert d["year_end"] == -1200


def test_cold_war_found(client):
    r = client.get("/v1/periods/by-slug/cold-war")
    d = r.json()
    assert d["year_start"] == 1947
    assert d["year_end"] == 1991


def test_warring_states_period_has_chinese_name(client):
    r = client.get("/v1/periods/by-slug/warring-states-period")
    d = r.json()
    assert d["name_native"] == "戰國時代"
    assert d["region"] == "asia_east"


# ═══════════════════════════════════════════════════════════════════
# 9. v6.29: Non-European period diversification
# ═══════════════════════════════════════════════════════════════════


def test_africa_periods_exist(client):
    """v6.29: Africa periods added."""
    r = client.get("/v1/periods?region=africa")
    d = r.json()
    assert d["total"] >= 3
    slugs = {p["slug"] for p in d["periods"]}
    assert "mali-empire-era" in slugs
    assert "aksumite-empire-era" in slugs


def test_southeast_asia_periods_exist(client):
    """v6.29: Southeast Asia periods added."""
    r = client.get("/v1/periods?region=asia_southeast")
    d = r.json()
    assert d["total"] >= 3
    slugs = {p["slug"] for p in d["periods"]}
    assert "angkor-period" in slugs
    assert "majapahit-period" in slugs


def test_americas_periods_expanded(client):
    """v6.29: Americas now has Classic Maya, Aztec, Inca, Mississippian."""
    r = client.get("/v1/periods?region=americas")
    d = r.json()
    assert d["total"] >= 4
    slugs = {p["slug"] for p in d["periods"]}
    assert "classic-maya-period" in slugs
    assert "aztec-imperial-period" in slugs
    assert "inca-imperial-period" in slugs


def test_aztec_has_nahuatl_name(client):
    """Aztec period uses Mexica (Nahuatl) as native name."""
    r = client.get("/v1/periods/by-slug/aztec-imperial-period")
    d = r.json()
    assert d["name_native"] == "Mēxihcah"
    assert d["name_native_lang"] == "nah"


def test_angkor_has_khmer_name(client):
    r = client.get("/v1/periods/by-slug/angkor-period")
    d = r.json()
    assert d["name_native"] == "យុគអង្គរ"


def test_regions_enum_has_more_regions(client):
    """v6.29: regions enum now includes africa, asia_southeast."""
    r = client.get("/v1/periods/regions")
    d = r.json()
    assert "africa" in d["regions"]
    assert "asia_southeast" in d["regions"]


def test_periods_more_balanced(client):
    """v6.29: no single region dominates by 10x; europe share drops."""
    r = client.get("/v1/periods?limit=500")
    d = r.json()
    from collections import Counter
    regions = Counter(p["region"] for p in d["periods"])
    total = sum(regions.values())
    # Europe should be < 50% of periods
    assert regions.get("europe", 0) / total < 0.5
    # Total should have grown (v6.27 had 33, v6.29 adds 15)
    assert total >= 45
