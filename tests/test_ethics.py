"""Test etici — verificano i principi documentati in docs/ethics/.

Questi test non sono tecnici: verificano che il database
rispetti i valori fondamentali del progetto.
"""


class TestEthics001NomiOriginali:
    """ETHICS-001: i nomi originali hanno priorit\u00e0."""

    def test_name_original_is_local_language(self, client):
        """Il nome primario deve essere nella lingua locale, non in inglese."""
        response = client.get("/v1/entities")
        data = response.json()
        for e in data["entities"]:
            # Nessun name_original dovrebbe essere puramente in inglese
            # per entit\u00e0 non anglofone
            if e["name_original_lang"] != "en":
                # Verifica che il nome non sia la versione inglese
                english_names = [
                    v["name"] for v in e["name_variants"] if v["lang"] == "en"
                ]
                if english_names:
                    assert e["name_original"] not in english_names, (
                        f"L'entit\u00e0 '{e['name_original']}' usa il nome inglese come primario. "
                        f"Dovrebbe usare il nome nella lingua originale (ETHICS-001)."
                    )

    def test_all_entities_have_name_variants(self, client):
        """Ogni entit\u00e0 deve avere almeno una variante di nome."""
        response = client.get("/v1/entities")
        data = response.json()
        for e in data["entities"]:
            assert len(e["name_variants"]) > 0, (
                f"'{e['name_original']}' non ha name_variants. "
                f"Servono per mostrare i nomi in altre lingue (ETHICS-001)."
            )


class TestEthics002ConquisteEsplicite:
    """ETHICS-002: le conquiste devono essere esplicite, non edulcorate."""

    def test_territory_changes_have_explicit_type(self, client):
        """Ogni cambio territoriale deve avere un change_type esplicito."""
        response = client.get("/v1/entities")
        data = response.json()
        for e in data["entities"]:
            for tc in e["territory_changes"]:
                assert tc["change_type"] != "", (
                    f"Cambio territoriale senza tipo per '{e['name_original']}' "
                    f"anno {tc['year']}. Vedi ETHICS-002."
                )
                assert tc["change_type"] != "UNKNOWN", (
                    f"Cambio territoriale 'UNKNOWN' per '{e['name_original']}' "
                    f"anno {tc['year']}. Deve essere specificato (ETHICS-002)."
                )

    def test_no_euphemistic_language(self, client):
        """Le descrizioni non devono usare linguaggio eufemistico."""
        forbidden = ["pacificazione", "civilizzazione", "scoperta di terre"]
        response = client.get("/v1/entities")
        data = response.json()
        for e in data["entities"]:
            for tc in e["territory_changes"]:
                if tc["description"]:
                    desc_lower = tc["description"].lower()
                    for word in forbidden:
                        assert word not in desc_lower, (
                            f"Linguaggio eufemistico '{word}' trovato in "
                            f"'{e['name_original']}', anno {tc['year']}. "
                            f"Vedi ETHICS-002."
                        )


class TestEthics003TerritorContestati:
    """ETHICS-003: i territori contestati devono essere espliciti."""

    def test_disputed_entities_exist(self, client):
        """Il dataset deve includere almeno un territorio contestato."""
        response = client.get("/v1/entity?status=disputed")
        data = response.json()
        assert data["count"] >= 1, (
            "Nessun territorio contestato nel dataset. "
            "Il database deve documentare anche le dispute attive (ETHICS-003)."
        )

    def test_disputed_entities_have_low_confidence(self, client):
        """I territori contestati devono avere confidence_score contenuto."""
        response = client.get("/v1/entity?status=disputed")
        data = response.json()
        for e in data["entities"]:
            assert e["confidence_score"] <= 0.7, (
                f"'{e['name_original']}' \u00e8 'disputed' ma ha confidence {e['confidence_score']}. "
                f"Un territorio contestato non pu\u00f2 avere alta confidenza (ETHICS-003)."
            )

    def test_disputed_entities_have_ethical_notes(self, client):
        """I territori contestati devono avere note etiche."""
        response = client.get("/v1/entity?status=disputed")
        data = response.json()
        for e in data["entities"]:
            assert e["ethical_notes"], (
                f"'{e['name_original']}' \u00e8 'disputed' senza note etiche. "
                f"I territori contestati richiedono contesto (ETHICS-003)."
            )


class TestConfidenceScore:
    """Principio 3: trasparenza dell'incertezza."""

    def test_all_entities_have_confidence(self, client):
        """Ogni entit\u00e0 deve avere un confidence_score."""
        response = client.get("/v1/entities")
        data = response.json()
        for e in data["entities"]:
            assert 0.0 <= e["confidence_score"] <= 1.0, (
                f"'{e['name_original']}' ha confidence_score "
                f"{e['confidence_score']} fuori range 0-1."
            )

    def test_all_entities_have_sources(self, client):
        """Ogni entit\u00e0 deve avere almeno una fonte."""
        response = client.get("/v1/entities")
        data = response.json()
        for e in data["entities"]:
            assert len(e["sources"]) > 0, (
                f"'{e['name_original']}' non ha fonti. "
                f"Ogni dato deve essere tracciabile (principio 3)."
            )
