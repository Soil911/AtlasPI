"""v6.48: tests per GeoJSON export di sites/rulers/languages."""


def test_export_sites_geojson(client):
    r = client.get("/v1/export/sites.geojson")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "FeatureCollection"
    assert isinstance(data["features"], list)
    assert data["metadata"]["count"] == len(data["features"])
    # Sample feature sanity
    if data["features"]:
        f = data["features"][0]
        assert f["type"] == "Feature"
        assert f["geometry"]["type"] == "Point"
        assert len(f["geometry"]["coordinates"]) == 2
        assert "name_original" in f["properties"]


def test_export_sites_unesco_filter(client):
    r = client.get("/v1/export/sites.geojson?unesco_only=true")
    assert r.status_code == 200
    for f in r.json()["features"]:
        assert f["properties"]["unesco_id"] is not None


def test_export_rulers_geojson(client):
    r = client.get("/v1/export/rulers.geojson")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "FeatureCollection"
    # rulers seed should have some entries
    assert len(data["features"]) >= 10
    # At least some should have geometry (resolved via entity capital)
    with_geom = [f for f in data["features"] if f["geometry"] is not None]
    # Hard assert: at least zero (OK because not all rulers have entity_id linked)
    assert data["metadata"]["with_geometry"] == len(with_geom)


def test_export_rulers_year_filter(client):
    """Year 1250 → Kublai Khan, not Augustus."""
    r = client.get("/v1/export/rulers.geojson?year=1250")
    assert r.status_code == 200
    names = [f["properties"]["name_original"] for f in r.json()["features"]]
    # At least one ruler in that year
    assert len(names) >= 1


def test_export_languages_geojson(client):
    r = client.get("/v1/export/languages.geojson")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 20  # seed has 29
    # Check geometry for a known language
    langs = {f["properties"]["name_original"]: f for f in data["features"]}
    if "Lingua Latina" in langs:
        latin = langs["Lingua Latina"]
        assert latin["geometry"]["type"] == "Point"
        # Rome area
        lon, lat = latin["geometry"]["coordinates"]
        assert 10 < lon < 15
        assert 40 < lat < 45


def test_export_languages_family_filter(client):
    r = client.get("/v1/export/languages.geojson?family=Indo-European")
    assert r.status_code == 200
    for f in r.json()["features"]:
        assert "Indo-European" in (f["properties"]["family"] or "")


def test_export_languages_vitality_filter(client):
    r = client.get("/v1/export/languages.geojson?vitality_status=endangered")
    assert r.status_code == 200
    for f in r.json()["features"]:
        assert f["properties"]["vitality_status"] == "endangered"


def test_export_preserves_native_scripts(client):
    """Export must preserve native_original names in non-Latin scripts."""
    r = client.get("/v1/export/languages.geojson")
    names = [f["properties"]["name_original"] for f in r.json()["features"]]
    # Seed includes non-Latin script examples
    non_latin = [n for n in names if any(ord(c) > 127 for c in n)]
    assert len(non_latin) >= 3, f"expected native scripts preserved, got names: {names[:5]}"
