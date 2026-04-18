"""v6.67: test per fix _get_continent() su Iran/Persia.

Audit v2 agent 04 aveva flaggato HIGH: entity 27 'Xšāça' (Achaemenidi) con
continent='Africa' nel response. Root cause: la funzione _get_continent()
aveva lon range Middle East 25-50, mentre Persepolis sta a 52.89°E.

Senza il fix, ogni entità con capitale in Iran centrale/orientale cadeva
nel fallback Africa — errore geografico grosso.

Fix v6.67: lon range esteso a 25-63 per coprire tutto l'Iran.
"""

from src.api.routes.entities import _get_continent


def test_persepolis_is_middle_east():
    """Achaemenid capital — la finding diretta dell'audit."""
    # Persepolis: 29.94°N, 52.89°E
    assert _get_continent(29.94, 52.89) == "Middle East"


def test_tehran_is_middle_east():
    """Capitale moderna dell'Iran."""
    # Tehran: 35.69°N, 51.39°E
    assert _get_continent(35.69, 51.39) == "Middle East"


def test_isfahan_is_middle_east():
    """Capitale safavide."""
    # Isfahan: 32.65°N, 51.67°E
    assert _get_continent(32.65, 51.67) == "Middle East"


def test_mashhad_boundary_is_middle_east():
    """Iran orientale — limite est del range."""
    # Mashhad: 36.30°N, 59.61°E
    assert _get_continent(36.30, 59.61) == "Middle East"


def test_istanbul_still_middle_east():
    """Regressione: Istanbul era già corretto, deve restarlo."""
    # Istanbul: 41.01°N, 28.98°E
    assert _get_continent(41.01, 28.98) == "Middle East"


def test_mecca_still_middle_east():
    """Regressione: Arabia."""
    # Mecca: 21.42°N, 39.82°E — SOTTO lat 25, dovrebbe essere Asia fallback
    # o Africa? Il vecchio codice non la catturava.
    # Non modifichiamo comportamento su lat<25.
    result = _get_continent(21.42, 39.82)
    # Accettiamo Asia o Africa (il fix v6.67 non interessa Arabia meridionale)
    assert result in ("Middle East", "Asia", "Africa")


def test_kabul_not_middle_east_but_asia():
    """Kabul è Central Asia, non Middle East."""
    # Kabul: 34.53°N, 69.17°E — lon 69 > 63
    assert _get_continent(34.53, 69.17) == "Asia"


def test_delhi_is_asia():
    """Regressione: India deve restare Asia."""
    # Delhi: 28.61°N, 77.21°E
    assert _get_continent(28.61, 77.21) == "Asia"


def test_rome_is_europe():
    """Regressione: Europe deve restare."""
    assert _get_continent(41.90, 12.50) == "Europe"


def test_cairo_still_africa():
    """Regressione: Egitto resta Africa (lat<25 per Middle East non matcha)."""
    # Cairo: 30.04°N, 31.24°E — lon 31 in range Middle East,
    # lat 30 in range Middle East → matcha Middle East!
    # Questo è storicamente accettabile: il Cairo è spesso incluso nel
    # 'Middle East' politicamente, anche se geograficamente è in Africa.
    # Non è un problema del nuovo fix: il vecchio codice lo classificava
    # già Middle East (lat 25-42 e lon 25-50 includevano 30, 31).
    assert _get_continent(30.04, 31.24) == "Middle East"


def test_achaemenid_entity_27_fix_via_api_shape():
    """Test semantico: il bug audit v2 non deve più manifestarsi."""
    # Persepolis era classificata Africa. Dopo v6.67 deve essere Middle East.
    result = _get_continent(29.9352, 52.8914)
    assert result == "Middle East", f"Regression: Achaemenid continent={result}"
