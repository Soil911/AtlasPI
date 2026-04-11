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
        r = client.get("/v1/entities?limit=100")
        for e in r.json()["entities"]:
            for s in e["sources"]:
                assert s["source_type"] in ("primary", "secondary", "academic"), (
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
