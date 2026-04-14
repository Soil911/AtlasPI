"""Importazione del dataset Natural Earth (ne_10m_admin_0_countries).

Natural Earth (https://www.naturalearthdata.com/) e' un dataset cartografico
in pubblico dominio (CC0) curato dalla comunita' GIS. Il dataset
ne_10m_admin_0_countries contiene i confini degli stati moderni con
risoluzione 1:10 milioni — idoneo per coverage geopolitica contemporanea.

Questo modulo:
1. Verifica la presenza dello shapefile in data/raw/natural_earth/.
2. Se assente, stampa istruzioni di download (NON scarica automaticamente).
3. Legge lo shapefile con geopandas.
4. Normalizza i nomi e gli ISO code per il matching successivo.
5. Esporta un dump strutturato in data/processed/natural_earth_boundaries.json
   con mapping {iso_a3: {name, name_long, geojson_geometry, ...}}.

Il file processato e' poi consumato da boundary_match.py.

ETHICS:
- I confini di Natural Earth riflettono lo stato politico contemporaneo
  riconosciuto dalle Nazioni Unite. NON sono validi per stati storici
  (l'Impero Romano non ha confini italiani moderni).
- Per i territori contestati (Taiwan, Western Sahara, Kosovo, Palestina,
  Crimea), Natural Earth marca le entita' con flag specifici (ADM0_TLC,
  FCLASS_*, NOTE_BRK). Il match tiene conto di questi flag.
- Vedi ETHICS-005-boundary-natural-earth.md.

Uso:
    python -m src.ingestion.natural_earth_import
    python -m src.ingestion.natural_earth_import --shapefile path/to/file.shp
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Path conventions ───────────────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw" / "natural_earth"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DEFAULT_SHAPEFILE = RAW_DIR / "ne_10m_admin_0_countries.shp"
OUTPUT_JSON = PROCESSED_DIR / "natural_earth_boundaries.json"

# Fallback to the smaller 110m geojson already shipped in the repo —
# used in dry-run if the 10m shapefile is missing.
FALLBACK_GEOJSON = ROOT_DIR / "data" / "raw" / "natural-earth" / "ne_110m_admin_0_countries.geojson"

DOWNLOAD_INSTRUCTIONS = """
Natural Earth shapefile not found at {path}.

To download (manually — this script will NOT do it automatically):

  1. Visit:
     https://www.naturalearthdata.com/downloads/10m-cultural-vectors/

  2. Or download directly:
     https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip

  3. Unzip into:
     {raw_dir}

  4. Verify these files are present (shapefiles ship as a set):
     - ne_10m_admin_0_countries.shp
     - ne_10m_admin_0_countries.shx
     - ne_10m_admin_0_countries.dbf
     - ne_10m_admin_0_countries.prj
     - ne_10m_admin_0_countries.cpg

  5. Re-run this script.

License: Natural Earth data is in the public domain (CC0).
"""


def _ensure_directories() -> None:
    """Crea le directory di output se mancano."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def _verify_shapefile_or_instruct(shapefile_path: Path) -> bool:
    """Verifica che lo shapefile esista. Se no, stampa istruzioni di download.

    Returns:
        True se il file esiste, False altrimenti.
    """
    if shapefile_path.exists():
        return True

    logger.error("Shapefile non trovato: %s", shapefile_path)
    instructions = DOWNLOAD_INSTRUCTIONS.format(
        path=shapefile_path,
        raw_dir=RAW_DIR,
    )
    print(instructions, file=sys.stderr)
    return False


def _normalize_iso_code(code: str | None) -> str | None:
    """Normalizza un codice ISO_A3.

    Natural Earth usa '-99' per entita' non riconosciute o de-facto.
    Restituiamo None in quel caso, cosi' il matching le ignorera' via ISO.
    """
    if not code:
        return None
    code = str(code).strip().upper()
    if not code or code == "-99":
        return None
    return code


def _geometry_to_geojson(geom: Any) -> dict | None:
    """Converte una shapely.geometry in dict GeoJSON.

    Gestisce Polygon, MultiPolygon. Restituisce None per geometrie vuote.
    """
    if geom is None:
        return None
    try:
        # shapely 2.x ha __geo_interface__ disponibile su tutte le geometry
        gi = getattr(geom, "__geo_interface__", None)
        if gi:
            return dict(gi)
    except Exception:
        logger.exception("Errore nella conversione geometria a GeoJSON")
    return None


def _load_with_geopandas(shapefile_path: Path) -> dict[str, dict]:
    """Carica lo shapefile via geopandas e restituisce mapping ISO_A3 -> record."""
    try:
        import geopandas as gpd
    except ImportError as e:
        raise RuntimeError(
            "geopandas non installato. Esegui: pip install -r requirements.txt"
        ) from e

    logger.info("Caricamento shapefile: %s", shapefile_path)
    gdf = gpd.read_file(str(shapefile_path))
    logger.info("Caricate %d feature dal dataset Natural Earth", len(gdf))

    # Assicuriamoci di essere in WGS84 (EPSG:4326) — Natural Earth e' gia' in 4326,
    # ma riproiettiamo per sicurezza.
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        logger.info("Riproiezione da %s a EPSG:4326", gdf.crs)
        gdf = gdf.to_crs(epsg=4326)

    out: dict[str, dict] = {}
    for _, row in gdf.iterrows():
        iso = _normalize_iso_code(row.get("ISO_A3") or row.get("ADM0_A3"))
        if iso is None:
            # Usa NE_ID come chiave per fallback (territori non riconosciuti)
            ne_id = row.get("NE_ID")
            iso = f"NE_{ne_id}" if ne_id is not None else f"NE_{row.name}"

        geom = _geometry_to_geojson(row.geometry)
        if geom is None:
            logger.warning("Geometria vuota per %s — saltato", row.get("NAME"))
            continue

        out[iso] = {
            "iso_a3": _normalize_iso_code(row.get("ISO_A3") or row.get("ADM0_A3")),
            "iso_a2": (row.get("ISO_A2") or "").strip() or None,
            "name": row.get("NAME"),
            "name_long": row.get("NAME_LONG"),
            "name_official": row.get("FORMAL_EN") or row.get("ADMIN"),
            "sovereign": row.get("SOVEREIGNT"),
            "continent": row.get("CONTINENT"),
            "type": row.get("TYPE"),
            # ETHICS: documentiamo se l'entita' ha ambiguita' politica
            "note_brk": row.get("NOTE_BRK"),
            "wikidata_id": row.get("WIKIDATAID"),
            # Nomi multilingua (utili per matching cross-language)
            "names_alt": {
                "en": row.get("NAME_EN"),
                "es": row.get("NAME_ES"),
                "fr": row.get("NAME_FR"),
                "de": row.get("NAME_DE"),
                "it": row.get("NAME_IT"),
                "pt": row.get("NAME_PT"),
                "ru": row.get("NAME_RU"),
                "zh": row.get("NAME_ZH"),
                "ar": row.get("NAME_AR"),
                "ja": row.get("NAME_JA"),
                "tr": row.get("NAME_TR"),
                "el": row.get("NAME_EL"),
                "he": row.get("NAME_HE"),
                "fa": row.get("NAME_FA"),
                "hi": row.get("NAME_HI"),
                "ko": row.get("NAME_KO"),
                "vi": row.get("NAME_VI"),
                "id": row.get("NAME_ID"),
                "pl": row.get("NAME_PL"),
                "sv": row.get("NAME_SV"),
                "nl": row.get("NAME_NL"),
                "uk": row.get("NAME_UK"),
                "ur": row.get("NAME_UR"),
                "bn": row.get("NAME_BN"),
            },
            "geojson": geom,
            # Centroide per fallback su capitale-dentro-poligono
            "label_lon": row.get("LABEL_X"),
            "label_lat": row.get("LABEL_Y"),
        }

    # Pulisci nomi multilingua None
    for record in out.values():
        record["names_alt"] = {
            k: v for k, v in record["names_alt"].items() if v
        }

    return out


def _load_fallback_geojson() -> dict[str, dict]:
    """Fallback: carica il file ne_110m_admin_0_countries.geojson gia' presente.

    Risoluzione inferiore (1:110M invece di 1:10M) ma sufficiente per dry-run
    e test iniziali.
    """
    if not FALLBACK_GEOJSON.exists():
        raise FileNotFoundError(
            f"Ne' lo shapefile 10m ne' il fallback 110m sono presenti. "
            f"Cercato: {DEFAULT_SHAPEFILE} e {FALLBACK_GEOJSON}"
        )
    logger.warning(
        "Shapefile 10m mancante — uso fallback 110m a risoluzione inferiore: %s",
        FALLBACK_GEOJSON,
    )
    data = json.loads(FALLBACK_GEOJSON.read_text(encoding="utf-8"))

    out: dict[str, dict] = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {}) or {}
        iso = _normalize_iso_code(props.get("ISO_A3") or props.get("ADM0_A3"))
        if iso is None:
            ne_id = props.get("NE_ID") or props.get("NAME")
            iso = f"NE_{ne_id}"

        out[iso] = {
            "iso_a3": _normalize_iso_code(props.get("ISO_A3") or props.get("ADM0_A3")),
            "iso_a2": (props.get("ISO_A2") or "").strip() or None,
            "name": props.get("NAME"),
            "name_long": props.get("NAME_LONG"),
            "name_official": props.get("FORMAL_EN") or props.get("ADMIN"),
            "sovereign": props.get("SOVEREIGNT"),
            "continent": props.get("CONTINENT"),
            "type": props.get("TYPE"),
            "note_brk": props.get("NOTE_BRK"),
            "wikidata_id": props.get("WIKIDATAID"),
            "names_alt": {
                k: props.get(f"NAME_{k.upper()}")
                for k in [
                    "en","es","fr","de","it","pt","ru","zh","ar","ja","tr",
                    "el","he","fa","hi","ko","vi","id","pl","sv","nl","uk","ur","bn",
                ]
                if props.get(f"NAME_{k.upper()}")
            },
            "geojson": feat.get("geometry"),
            "label_lon": props.get("LABEL_X"),
            "label_lat": props.get("LABEL_Y"),
        }

    return out


def import_natural_earth(
    shapefile_path: Path = DEFAULT_SHAPEFILE,
    output_path: Path = OUTPUT_JSON,
    use_fallback_if_missing: bool = True,
    dry_run: bool = False,
) -> dict[str, dict]:
    """Importa Natural Earth e produce il file processato.

    Args:
        shapefile_path: Path dello shapefile .shp di Natural Earth 10m.
        output_path: Path del JSON di output.
        use_fallback_if_missing: Se True, usa il geojson 110m gia' nel repo
            quando lo shapefile 10m non e' presente. Utile per testing.
        dry_run: Se True, non scrive il file di output.

    Returns:
        Dizionario {iso_a3: record} con tutte le entita' caricate.

    Raises:
        FileNotFoundError: se ne' shapefile ne' fallback sono disponibili.
    """
    _ensure_directories()

    if shapefile_path.exists():
        countries = _load_with_geopandas(shapefile_path)
    elif use_fallback_if_missing and FALLBACK_GEOJSON.exists():
        countries = _load_fallback_geojson()
    else:
        _verify_shapefile_or_instruct(shapefile_path)
        raise FileNotFoundError(f"Shapefile mancante: {shapefile_path}")

    logger.info("Estratte %d entita' Natural Earth", len(countries))

    if dry_run:
        logger.info("[DRY RUN] Nessun file scritto. Output sarebbe stato: %s", output_path)
        # Stampa anche un breve sommario
        with_iso = sum(1 for r in countries.values() if r.get("iso_a3"))
        without_iso = len(countries) - with_iso
        logger.info("[DRY RUN] %d con ISO_A3 valido, %d senza (territori contestati/de-facto)",
                    with_iso, without_iso)
        return countries

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(countries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Scritto: %s (%d entita')", output_path, len(countries))
    return countries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--shapefile",
        type=Path,
        default=DEFAULT_SHAPEFILE,
        help=f"Path dello shapefile Natural Earth (default: {DEFAULT_SHAPEFILE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_JSON,
        help=f"Path del JSON di output (default: {OUTPUT_JSON})",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Non usare il geojson 110m come fallback se lo shapefile manca.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Non scrive l'output, solo valida il caricamento.",
    )
    args = parser.parse_args()

    try:
        import_natural_earth(
            shapefile_path=args.shapefile,
            output_path=args.output,
            use_fallback_if_missing=not args.no_fallback,
            dry_run=args.dry_run,
        )
    except FileNotFoundError as e:
        logger.error("%s", e)
        return 1
    except Exception:
        logger.exception("Errore durante l'importazione di Natural Earth")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
