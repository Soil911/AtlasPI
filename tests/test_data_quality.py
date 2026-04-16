"""Test di qualita' dati — verifica coerenza dell'intero dataset."""


class TestDataCompleteness:
    def test_all_entities_have_entity_type(self, client):
        r = client.get("/v1/entities?limit=100")
        for e in r.json()["entities"]:
            assert e["entity_type"], f"'{e['name_original']}' senza entity_type"

    def test_all_entities_have_valid_year_range(self, client):
        r = client.get("/v1/entities?limit=100")
        for e in r.json()["entities"]:
            if e["year_end"] is not None:
                assert e["year_end"] >= e["year_start"], (
                    f"'{e['name_original']}': year_end ({e['year_end']}) < year_start ({e['year_start']})"
                )

    def test_disputed_territories_have_notes(self, client):
        r = client.get("/v1/entity?status=disputed&limit=100")
        for e in r.json()["entities"]:
            assert e["ethical_notes"], (
                f"'{e['name_original']}' e' disputed ma senza ethical_notes"
            )

    def test_all_conquests_have_description(self, client):
        r = client.get("/v1/entities?limit=100")
        for e in r.json()["entities"]:
            for tc in e["territory_changes"]:
                if tc["change_type"] in ("CONQUEST_MILITARY", "COLONIZATION", "ETHNIC_CLEANSING", "GENOCIDE"):
                    assert tc["description"], (
                        f"'{e['name_original']}', anno {tc['year']}: "
                        f"cambio {tc['change_type']} senza descrizione"
                    )

    def test_no_duplicate_entity_names(self, client):
        r = client.get("/v1/entities?limit=100")
        names = [e["name_original"] for e in r.json()["entities"]]
        assert len(names) == len(set(names)), "Nomi entita' duplicati trovati"

    def test_confidence_distribution(self, client):
        """Il dataset deve avere varieta' di confidence scores."""
        r = client.get("/v1/entities?limit=100")
        scores = [e["confidence_score"] for e in r.json()["entities"]]
        assert min(scores) <= 0.5, "Nessun dato a bassa confidence — manca incertezza"
        assert max(scores) >= 0.8, "Nessun dato ad alta confidence"

    def test_geographic_diversity(self, client):
        """Il dataset deve coprire piu' continenti."""
        r = client.get("/v1/types")
        types = [t["type"] for t in r.json()]
        assert len(types) >= 4, f"Solo {len(types)} tipi — poca diversita'"

    def test_temporal_diversity(self, client):
        """Il dataset deve coprire almeno 3000 anni."""
        r = client.get("/v1/stats")
        d = r.json()
        span = d["year_range"]["max"] - d["year_range"]["min"]
        assert span >= 3000, f"Copertura temporale solo {span} anni"

    def test_all_sources_have_type(self, client):
        from src.db.enums import SourceType
        valid_types = {st.value for st in SourceType}
        r = client.get("/v1/entities?limit=100")
        for e in r.json()["entities"]:
            for s in e["sources"]:
                assert s["source_type"] in valid_types, (
                    f"'{e['name_original']}': fonte '{s['citation'][:30]}...' "
                    f"con tipo invalido '{s['source_type']}'"
                )

    def test_disputed_have_multiple_name_variants(self, client):
        """I territori contestati devono avere piu' varianti di nome."""
        r = client.get("/v1/entity?status=disputed&limit=100")
        for e in r.json()["entities"]:
            assert len(e["name_variants"]) >= 2, (
                f"'{e['name_original']}' e' disputed ma ha solo "
                f"{len(e['name_variants'])} variante/i di nome"
            )


class TestEthics006GeographicGuard:
    """Audit di integrita' geografica su tutto il dataset (ETHICS-006).

    Regressione guard: ogni entita' con `boundary_source = 'natural_earth'`
    deve avere la capitale DENTRO il poligono. Se fallisce, il matcher NE
    ha accettato un match sbagliato (tipo Garenganze → Russia).

    Nota: aourednik e historical_map possono avere piccole discrepanze
    ai margini del poligono (p.es. Istanbul sul Bosforo, Stoccolma su
    isola esterna a un poligono semplificato). Questi casi richiedono
    una tolleranza buffer o un'analisi caso-per-caso, rimandata a v6.2.
    """

    def test_natural_earth_boundaries_contain_capital(self, db):
        import json

        from shapely.geometry import Point, shape

        from src.db.models import GeoEntity

        rows = (
            db.query(GeoEntity)
            .filter(GeoEntity.boundary_source == "natural_earth")
            .filter(GeoEntity.boundary_geojson.isnot(None))
            .filter(GeoEntity.capital_lat.isnot(None))
            .filter(GeoEntity.capital_lon.isnot(None))
            .all()
        )

        violations: list[str] = []
        for row in rows:
            try:
                geom = json.loads(row.boundary_geojson)
                poly = shape(geom)
                point = Point(float(row.capital_lon), float(row.capital_lat))
                if not poly.contains(point):
                    violations.append(
                        f"{row.name_original!r} (id={row.id}): capital "
                        f"({row.capital_lat:.2f}, {row.capital_lon:.2f}) "
                        f"not inside NE polygon"
                    )
            except Exception as exc:  # malformed polygon etc.
                violations.append(
                    f"{row.name_original!r} (id={row.id}): geometry error {exc}"
                )

        assert not violations, (
            f"ETHICS-006 regression: {len(violations)} Natural Earth "
            f"match con capitale fuori dal poligono (tipo Garenganze→RUS):\n"
            + "\n".join(violations[:10])
            + (f"\n  ... +{len(violations) - 10} altri" if len(violations) > 10 else "")
        )

    def test_catastrophic_displacement_caught(self, db):
        """Guard contro displacement catastrofici (>8000 km, mezzo pianeta)
        anche su source non-NE. Il threshold e' volutamente alto: permette
        imperi continentali legittimi (Russia → Siberia, Denmark → Groenlandia)
        ma blocca errori tipo 'Kerajaan Kediri in Caucasus' o 'Ghurids in
        Peru' che sarebbero match cross-dataset cross-continente sbagliati.

        Casi piu' fini (2000–8000 km, ambigui) sono da risolvere con un
        audit manuale caso-per-caso; rimandato a v6.2."""
        import json
        import math

        from shapely.geometry import shape

        from src.db.models import GeoEntity

        rows = (
            db.query(GeoEntity)
            .filter(GeoEntity.boundary_source.in_(["aourednik", "historical_map"]))
            .filter(GeoEntity.boundary_geojson.isnot(None))
            .filter(GeoEntity.capital_lat.isnot(None))
            .filter(GeoEntity.capital_lon.isnot(None))
            .all()
        )

        MAX_DIST_KM = 8000.0  # half-way around the planet as hard cutoff

        def haversine_km(lat1, lon1, lat2, lon2):
            R = 6371.0
            p1, p2 = math.radians(lat1), math.radians(lat2)
            dp = math.radians(lat2 - lat1)
            dl = math.radians(lon2 - lon1)
            a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
            return 2 * R * math.asin(math.sqrt(a))

        violations: list[str] = []
        for row in rows:
            try:
                geom = json.loads(row.boundary_geojson)
                centroid = shape(geom).centroid
                dist = haversine_km(
                    row.capital_lat, row.capital_lon,
                    centroid.y, centroid.x,
                )
                if dist > MAX_DIST_KM:
                    violations.append(
                        f"{row.name_original!r} (id={row.id}, "
                        f"source={row.boundary_source}): capital "
                        f"({row.capital_lat:.1f}, {row.capital_lon:.1f}) "
                        f"is {dist:.0f}km from polygon centroid "
                        f"({centroid.y:.1f}, {centroid.x:.1f})"
                    )
            except Exception as exc:
                violations.append(
                    f"{row.name_original!r} (id={row.id}): error {exc}"
                )

        assert not violations, (
            f"CATASTROPHIC displacement: {len(violations)} match con "
            f"capitale a >8000km dal centroide del poligono (match "
            f"cross-continente, quasi certamente errato):\n"
            + "\n".join(violations[:10])
        )


class TestEthicsExtended:
    def test_colonial_entities_have_ethics_notes(self, client):
        """Entita' di tipo colony devono avere note etiche."""
        r = client.get("/v1/entity?type=colony&limit=100")
        for e in r.json()["entities"]:
            assert e["ethical_notes"], (
                f"'{e['name_original']}' e' una colonia senza note etiche"
            )

    def test_no_glorifying_language(self, client):
        """Le descrizioni non devono glorificare conquiste."""
        forbidden = ["glorioso", "civilizzazione di", "pacificaz"]
        r = client.get("/v1/entities?limit=100")
        for e in r.json()["entities"]:
            for tc in e["territory_changes"]:
                if tc["description"]:
                    desc_lower = tc["description"].lower()
                    for word in forbidden:
                        assert word not in desc_lower, (
                            f"Linguaggio glorificante '{word}' in "
                            f"'{e['name_original']}', anno {tc['year']}"
                        )
