"""Estrazione confini reali da dataset storici.

Fonti:
- Natural Earth (ne_110m_admin_0_countries) — confini moderni, pubblico dominio
- aourednik/historical-basemaps — confini storici, GeoJSON per periodo

ETHICS: i confini estratti sono approssimazioni accademiche.
Il campo boundary_precision documenta il livello di accuratezza.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


def _load_geojson(filepath: Path) -> dict | None:
    if not filepath.exists():
        logger.warning("File non trovato: %s", filepath)
        return None
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def _find_feature(data: dict, name: str) -> dict | None:
    """Cerca una feature per NAME (case-insensitive)."""
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        feat_name = props.get("NAME") or ""
        if feat_name.lower() == name.lower():
            return feat
    return None


def _find_features_multi(data: dict, names: list[str]) -> list[dict]:
    """Cerca multiple features e unisce le geometrie."""
    found = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        feat_name = (props.get("NAME") or "").lower()
        if feat_name in [n.lower() for n in names]:
            found.append(feat)
    return found


def _simplify_coordinates(coords, max_points: int = 200) -> list:
    """Riduce il numero di punti se eccessivo per non appesantire il DB."""
    if isinstance(coords[0][0], (int, float)):
        # Simple ring
        if len(coords) <= max_points:
            return coords
        step = max(1, len(coords) // max_points)
        simplified = coords[::step]
        if simplified[-1] != coords[-1]:
            simplified.append(coords[-1])
        # Assicura chiusura del poligono
        if simplified[0] != simplified[-1]:
            simplified.append(simplified[0])
        return simplified
    else:
        return [_simplify_coordinates(ring, max_points) for ring in coords]


def extract_geometry(data: dict, name: str, max_points: int = 200) -> dict | None:
    """Estrae e semplifica la geometria per un nome dato."""
    feat = _find_feature(data, name)
    if not feat:
        return None

    geom = feat.get("geometry", {})
    geom_type = geom.get("type")

    if geom_type == "Polygon":
        coords = [_simplify_coordinates(ring, max_points) for ring in geom["coordinates"]]
        return {"type": "Polygon", "coordinates": coords}
    elif geom_type == "MultiPolygon":
        coords = []
        for polygon in geom["coordinates"]:
            simplified_polygon = [_simplify_coordinates(ring, max_points) for ring in polygon]
            coords.append(simplified_polygon)
        return {"type": "MultiPolygon", "coordinates": coords}

    return geom


def merge_geometries(data: dict, names: list[str], max_points: int = 200) -> dict | None:
    """Unisce le geometrie di multiple features in un MultiPolygon."""
    features = _find_features_multi(data, names)
    if not features:
        return None

    all_polygons = []
    for feat in features:
        geom = feat.get("geometry", {})
        if geom["type"] == "Polygon":
            coords = [_simplify_coordinates(ring, max_points) for ring in geom["coordinates"]]
            all_polygons.append(coords)
        elif geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                coords = [_simplify_coordinates(ring, max_points) for ring in polygon]
                all_polygons.append(coords)

    if len(all_polygons) == 1:
        return {"type": "Polygon", "coordinates": all_polygons[0]}
    return {"type": "MultiPolygon", "coordinates": all_polygons}


def extract_from_natural_earth(name: str, iso_a3: str | None = None) -> dict | None:
    """Estrae confini moderni da Natural Earth."""
    filepath = DATA_DIR / "natural-earth" / "ne_110m_admin_0_countries.geojson"
    data = _load_geojson(filepath)
    if not data:
        return None

    for feat in data["features"]:
        props = feat.get("properties", {})
        if iso_a3 and props.get("ISO_A3") == iso_a3:
            return feat["geometry"]
        if (props.get("NAME") or "").lower() == name.lower():
            return feat["geometry"]

    return None


# ─── Mappatura entità AtlasPI → dataset ─────────────────────────

ENTITY_MAPPINGS = {
    "Imperium Romanum": {
        "file": "historical-basemaps/world_100.geojson",
        "name": "Roman Empire",
        "source": "aourednik/historical-basemaps, world_100",
        "precision": "academic_approximate",
    },
    "Osmanlı İmparatorluğu": {
        "file": "historical-basemaps/world_1500.geojson",
        "name": "Ottoman Empire",
        "source": "aourednik/historical-basemaps, world_1500",
        "precision": "academic_approximate",
    },
    "İstanbul": {
        "type": "point",
        "source": "coordinate note",
        "precision": "exact",
    },
    "Tawantinsuyu": {
        "file": "historical-basemaps/world_1500.geojson",
        "name": "Inca Empire",
        "source": "aourednik/historical-basemaps, world_1500",
        "precision": "academic_approximate",
    },
    "British Raj": {
        "file": "historical-basemaps/world_1900.geojson",
        "name": "British Raj",
        "source": "aourednik/historical-basemaps, world_1900",
        "precision": "academic_approximate",
    },
    "فلسطين / ישראל": {
        "file": "natural-earth/ne_110m_admin_0_countries.geojson",
        "name": "Israel",
        "source": "Natural Earth ne_110m (confini moderni contestati)",
        "precision": "modern_approximate",
    },
    "Republika e Kosovës": {
        "file": "natural-earth/ne_110m_admin_0_countries.geojson",
        "name": "Kosovo",
        "source": "Natural Earth ne_110m (confini moderni contestati)",
        "precision": "modern_approximate",
    },
    "Ἀθῆναι": {
        "file": "historical-basemaps/world_100.geojson",
        "name": "Greece",  # fallback, historical basemap doesn't have Attica alone
        "source": "Confini approssimativi della regione attica",
        "precision": "estimated",
    },
    "ᠶᠡᠬᠡ ᠮᠣᠩᠭᠣᠯ ᠤᠯᠤᠰ": {
        "file": "historical-basemaps/world_1300.geojson",
        "names": ["Great Khanate", "Chagatai Khanate", "Ilkhanate", "Khanate of the Golden Horde"],
        "source": "aourednik/historical-basemaps, world_1300 (khanati unificati)",
        "precision": "academic_approximate",
    },
    "Kongo dia Ntotila": {
        "file": "historical-basemaps/world_1500.geojson",
        "name": "Congo",
        "source": "aourednik/historical-basemaps, world_1500",
        "precision": "academic_approximate",
    },
}


def extract_all_boundaries() -> dict[str, dict]:
    """Estrae tutti i confini reali per le entità mappate.

    Returns: {entity_name_original: {"geojson": ..., "source": ..., "precision": ...}}
    """
    results = {}

    for entity_name, mapping in ENTITY_MAPPINGS.items():
        if mapping.get("type") == "point":
            # Skip points — keep existing coordinate
            continue

        filepath = DATA_DIR / mapping["file"]
        data = _load_geojson(filepath)
        if not data:
            logger.warning("Non riesco a caricare %s per %s", mapping["file"], entity_name)
            continue

        if "names" in mapping:
            geom = merge_geometries(data, mapping["names"])
        else:
            geom = extract_geometry(data, mapping["name"])

        if geom:
            results[entity_name] = {
                "geojson": geom,
                "source": mapping["source"],
                "precision": mapping["precision"],
            }
            logger.info("Estratto confine per: %s (%s punti)", entity_name,
                        _count_points(geom))
        else:
            logger.warning("Nessun confine trovato per: %s (cercato '%s' in %s)",
                           entity_name, mapping.get("name", mapping.get("names")), mapping["file"])

    return results


def _count_points(geom: dict) -> int:
    """Conta punti in una geometria."""
    if geom["type"] == "Polygon":
        return sum(len(ring) for ring in geom["coordinates"])
    elif geom["type"] == "MultiPolygon":
        return sum(
            sum(len(ring) for ring in polygon)
            for polygon in geom["coordinates"]
        )
    return 0
