"""ADR-005 (v6.99.107): le entità deprecate non leakano nei risultati discovery.

# ETHICS: deprecated = duplicato/superseduto (merge v6.85 + ETHICS-015).
# Un duplicato che riappare in snapshot/search/similar/nearby "resuscita"
# una versione doppia della storia (bug live: /v1/snapshot/year/-500
# includeva l'Achemenide duplicato id 847; /v1/search/fuzzy il 414).
# I permalink /v1/entities/{id} restano invece accessibili (ADR-005).

Le fixture arrivano dal seed JSON reale: dopo il backport-status v6.99.107
il test-DB contiene i duplicati deprecati veri (es. 'هخامنشیان', gemello
dell'Achemenide 'Xšāça'; 'سلطنت مغلیہ', gemello Mughal di 'مغلیہ سلطنت').
"""

import pytest

from src.db.models import GeoEntity

DEPRECATED_TWIN = "هخامنشیان"          # Achaemenid duplicate (prod id 847)
CANONICAL_TWIN = "Xšāça"               # Achaemenid primary (prod id 27)


@pytest.fixture
def twin_ids(db):
    dep = db.query(GeoEntity).filter(GeoEntity.name_original == DEPRECATED_TWIN).first()
    canon = db.query(GeoEntity).filter(GeoEntity.name_original == CANONICAL_TWIN).first()
    assert dep is not None and canon is not None, "fixture: gemelli achemenidi assenti dal seed"
    assert dep.status == "deprecated", "fixture: backport status non applicato al seed"
    return dep.id, canon.id


def _assert_no_deprecated(items, id_key="id", status_key="status", dep_id=None):
    for it in items:
        if status_key in it:
            assert it[status_key] != "deprecated", f"deprecated leaked: {it}"
        if dep_id is not None and id_key in it:
            assert it[id_key] != dep_id, f"deprecated id leaked: {it}"


class TestDiscoveryExclusion:
    def test_world_snapshot_excludes_deprecated(self, client, twin_ids):
        dep_id, _ = twin_ids
        r = client.get("/v1/snapshot/year/-400")
        assert r.status_code == 200
        data = r.json()
        top = data["entities"]["top_by_confidence"]
        _assert_no_deprecated(top, dep_id=dep_id)

    def test_year_snapshot_excludes_deprecated(self, client, twin_ids):
        dep_id, _ = twin_ids
        r = client.get("/v1/snapshot/-400")
        assert r.status_code == 200
        _assert_no_deprecated(r.json()["entities"], dep_id=dep_id)

    def test_fuzzy_search_excludes_deprecated(self, client, twin_ids):
        dep_id, _ = twin_ids
        r = client.get("/v1/search/fuzzy", params={"q": DEPRECATED_TWIN})
        assert r.status_code == 200
        results = r.json()["results"]
        _assert_no_deprecated(results, dep_id=dep_id)

    def test_autocomplete_search_excludes_deprecated(self, client, twin_ids):
        dep_id, _ = twin_ids
        r = client.get("/v1/search", params={"q": DEPRECATED_TWIN})
        assert r.status_code == 200
        _assert_no_deprecated(r.json()["results"], dep_id=dep_id)

    def test_advanced_search_excludes_deprecated_by_default(self, client, twin_ids):
        dep_id, _ = twin_ids
        r = client.get("/v1/search/advanced", params={"q": DEPRECATED_TWIN})
        assert r.status_code == 200
        _assert_no_deprecated(r.json()["results"], dep_id=dep_id)

    def test_legacy_entity_endpoint_optin(self, client, twin_ids):
        dep_id, _ = twin_ids
        r = client.get("/v1/entity", params={"name": DEPRECATED_TWIN})
        assert r.status_code == 200
        assert all(e["id"] != dep_id for e in r.json()["entities"])
        r2 = client.get(
            "/v1/entity", params={"name": DEPRECATED_TWIN, "include_deprecated": "true"}
        )
        assert any(e["id"] == dep_id for e in r2.json()["entities"]), (
            "include_deprecated=true deve riesporre il record (ADR-005 opt-in)"
        )

    def test_similar_excludes_deprecated_twin(self, client, twin_ids):
        dep_id, canon_id = twin_ids
        r = client.get(f"/v1/entities/{canon_id}/similar")
        assert r.status_code == 200
        payload = r.json()
        items = payload.get("similar") or payload.get("results") or []
        _assert_no_deprecated(items, dep_id=dep_id)

    def test_contemporaries_exclude_deprecated(self, client, twin_ids):
        dep_id, canon_id = twin_ids
        r = client.get(f"/v1/entities/{canon_id}/contemporaries")
        assert r.status_code == 200
        _assert_no_deprecated(r.json()["contemporaries"], dep_id=dep_id)

    def test_timeline_data_excludes_deprecated(self, client, twin_ids):
        dep_id, _ = twin_ids
        r = client.get("/v1/timeline-data")
        assert r.status_code == 200
        _assert_no_deprecated(r.json()["entities"], dep_id=dep_id)

    def test_nearby_excludes_deprecated(self, client, db, twin_ids):
        dep_id, _ = twin_ids
        dep = db.query(GeoEntity).filter(GeoEntity.id == dep_id).first()
        if dep.capital_lat is None or dep.capital_lon is None:
            pytest.skip("gemello deprecato senza coordinate capitale")
        r = client.get(
            "/v1/nearby",
            params={"lat": dep.capital_lat, "lon": dep.capital_lon, "radius": 50},
        )
        assert r.status_code == 200
        payload = r.json()
        items = payload.get("results") or payload.get("entities") or []
        _assert_no_deprecated(items, dep_id=dep_id)

    def test_export_csv_optin(self, client, twin_ids):
        dep_id, _ = twin_ids
        r = client.get("/v1/export/csv")
        assert r.status_code == 200
        assert f"\n{dep_id}," not in r.text
        r2 = client.get("/v1/export/csv", params={"include_deprecated": "true"})
        assert f"\n{dep_id}," in r2.text

    def test_random_never_deprecated(self, client):
        # 15 estrazioni: con ~40 deprecati su ~1040 il leak emergerebbe presto
        for _ in range(15):
            r = client.get("/v1/random")
            assert r.status_code == 200
            assert r.json()["status"] != "deprecated"


class TestTransparencyPreserved:
    def test_detail_by_id_still_returns_deprecated(self, client, twin_ids):
        dep_id, _ = twin_ids
        r = client.get(f"/v1/entities/{dep_id}", params={"exclude_geometry": "true"})
        assert r.status_code == 200, "ADR-005: i permalink dei deprecati restano accessibili"
        assert r.json()["status"] == "deprecated"

    def test_stats_keep_deprecated_bucket_visible(self, client):
        r = client.get("/v1/stats")
        assert r.status_code == 200
        data = r.json()
        assert data["status_counts"].get("deprecated", 0) > 0, (
            "trasparenza: il bucket deprecated non va nascosto dalle stats"
        )
        live_sum = sum(v for k, v in data["status_counts"].items() if k != "deprecated")
        assert data["total_entities"] == live_sum, (
            "total_entities deve riconciliarsi con la somma dei bucket non-deprecated"
        )

    def test_aggregation_keeps_deprecated_in_by_status(self, client):
        r = client.get("/v1/aggregation")
        assert r.status_code == 200
        by_status = {row["status"]: row["count"] for row in r.json()["by_status"]}
        assert by_status.get("deprecated", 0) > 0
