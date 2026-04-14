"""Matching delle entita' AtlasPI con i confini storici di aourednik/historical-basemaps.

aourednik/historical-basemaps (https://github.com/aourednik/historical-basemaps)
e' un dataset CC BY 4.0 di mappe storiche del mondo, con geojson timestamped
per ogni epoca storica dal -123000 al 2010 CE. Ogni file world_YYYY.geojson
contiene feature polygonali per gli stati/entita' esistenti in quell'anno.

A differenza di Natural Earth (confini moderni), aourednik e' adatto al
matching di entita' PRE-1800 perche' i suoi poligoni riflettono la
geografia politica storica.

Strategia di match:

  Per ogni entita' AtlasPI con [year_start, year_end]:
    1. Seleziona lo snapshot aourednik nel range [year_start, year_end]
       piu' centrale alla vita dell'entita'. Se nessuno rientra nel range,
       scegli il piu' vicino entro una tolleranza.
    2. Dentro quello snapshot, cerca feature con match su NAME:
       a. exact (case-insensitive, accent-fold)
       b. fuzzy (rapidfuzz, soglia 80%) — soglia piu' alta di NE perche'
          i nomi storici sono piu' distintivi
       c. SUBJECTO match (per vassallaggi/suzerains)
       d. PARTOF match (se l'entita' e' parte di una super-entita' nota)
    3. Fallback: feature con centroide piu' vicino alla capitale dell'entita'.
       Usato solo se name-match fallisce e la distanza < 1000 km.

ETHICS:
  - BORDERPRECISION (0-2) in aourednik influenza il confidence_score:
    2 -> 0.80, 1 -> 0.65, 0 -> 0.45. I poligoni con precision=0 sono
    approssimazioni dichiarate dall'autore, lo rispettiamo.
  - Per territori contestati storici (Kashmir medievale, Palestina storica,
    etc.) il match e' ammesso ma viene flagged in ethical_notes.
  - Vedi ETHICS-005-boundary-natural-earth.md per la metodologia
    (applicata analogamente ad aourednik).

Licenza aourednik: CC BY 4.0 — attribuzione richiesta.
Vedi data/raw/aourednik-historical-basemaps/LICENSE.
"""

from __future__ import annotations

import json
import logging
import math
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
AOUREDNIK_GEOJSON_DIR = ROOT_DIR / "data" / "raw" / "aourednik-historical-basemaps" / "geojson"

# ─── Configuration ──────────────────────────────────────────────────────────

# Soglia fuzzy per nomi storici (piu' alta di NE perche' nomi storici
# sono piu' distintivi e meno ambigui)
FUZZY_THRESHOLD = 80

# Tolleranza anno: se non c'e' snapshot aourednik nel range [ys, ye],
# accettiamo lo snapshot piu' vicino entro questa distanza in anni.
YEAR_TOLERANCE = 100

# Distanza massima (km) per fallback capital-near-centroid
# (usato solo se point-in-polygon fallisce e l'entita' ha nomi molto parziali)
MAX_FALLBACK_DIST_KM = 250

# Se piu' poligoni contengono la capitale, scegliamo quello piu' piccolo
# (assunzione: un piccolo poligono e' piu' specifico — es. ducato dentro impero).
# Questo boost aiuta il match quando il name-match fallisce.
PREFER_SMALLER_POLYGON = True

# BORDERPRECISION -> confidence
PRECISION_CONFIDENCE = {
    2: 0.80,
    1: 0.65,
    0: 0.45,
}

# Candidate terms to skip (None features, plates, oceans)
SKIP_NAMES = {"", "none"}


# ─── Data structures ────────────────────────────────────────────────────────


@dataclass
class AourednikMatch:
    """Risultato di un match con aourednik."""
    matched: bool
    strategy: str = ""  # "exact_name" | "fuzzy_name" | "subjecto" | "partof" | "capital_near_centroid"
    confidence: float = 0.0
    aourednik_name: Optional[str] = None
    aourednik_year: Optional[int] = None
    border_precision: Optional[int] = None
    geojson: Optional[dict] = None
    rejection_reason: Optional[str] = None


# ─── Helpers ────────────────────────────────────────────────────────────────


def _normalize(s: Optional[str]) -> str:
    """Normalizza un nome: lowercase, accent-fold, strip punct."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def _year_from_filename(filename: str) -> Optional[int]:
    """Estrae l'anno da un filename aourednik.

    Esempi:
      world_1300.geojson -> 1300
      world_bc123000.geojson -> -123000
      world_bc500.geojson -> -500
      world_1492.geojson -> 1492
    """
    m = re.match(r"world_(bc)?(\d+)\.geojson", filename, re.IGNORECASE)
    if not m:
        return None
    is_bc = m.group(1) is not None
    year = int(m.group(2))
    return -year if is_bc else year


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distanza sulla sfera terrestre in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _polygon_centroid(geom: dict) -> Optional[tuple[float, float]]:
    """Calcola un centroide approssimato per un Polygon/MultiPolygon.

    Non usiamo shapely qui per leggerezza: media dei vertici di una ring.
    """
    if not geom or geom.get("type") not in ("Polygon", "MultiPolygon"):
        return None
    try:
        if geom["type"] == "Polygon":
            ring = geom["coordinates"][0]
        else:  # MultiPolygon — prendo il primo polygon, primo ring
            ring = geom["coordinates"][0][0]
        if not ring:
            return None
        lats = [p[1] for p in ring]
        lons = [p[0] for p in ring]
        return (sum(lats) / len(lats), sum(lons) / len(lons))
    except (IndexError, KeyError, TypeError):
        return None


def _ring_bbox(ring: list) -> Optional[tuple[float, float, float, float]]:
    """Bounding box (min_lon, min_lat, max_lon, max_lat) di una ring."""
    if not ring:
        return None
    try:
        lons = [p[0] for p in ring]
        lats = [p[1] for p in ring]
        return (min(lons), min(lats), max(lons), max(lats))
    except (IndexError, TypeError):
        return None


def _point_in_ring(lon: float, lat: float, ring: list) -> bool:
    """Ray casting point-in-polygon (sufficiente per ring non-self-intersecting).

    ETHICS: puramente geometrico, non risolve territori contestati — ma se la
    capitale e' dentro il poligono, il match e' molto piu' affidabile di
    'centroide piu' vicino'. Rispetta il principio di verita' prima del comfort.
    """
    if not ring or len(ring) < 3:
        return False
    n = len(ring)
    inside = False
    j = n - 1
    for i in range(n):
        try:
            xi, yi = ring[i][0], ring[i][1]
            xj, yj = ring[j][0], ring[j][1]
        except (IndexError, TypeError):
            j = i
            continue
        intersect = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersect:
            inside = not inside
        j = i
    return inside


def _point_in_geometry(lon: float, lat: float, geom: dict) -> bool:
    """Point-in-polygon per Polygon/MultiPolygon con esclusione dei holes."""
    if not geom:
        return False
    gtype = geom.get("type")
    coords = geom.get("coordinates")
    if not coords:
        return False
    try:
        if gtype == "Polygon":
            rings = coords
            # Bbox pre-filter sull'outer ring
            bbox = _ring_bbox(rings[0])
            if bbox is None:
                return False
            min_lon, min_lat, max_lon, max_lat = bbox
            if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                return False
            if not _point_in_ring(lon, lat, rings[0]):
                return False
            # Escludi se dentro un hole
            for hole in rings[1:]:
                if _point_in_ring(lon, lat, hole):
                    return False
            return True
        elif gtype == "MultiPolygon":
            for poly in coords:
                if not poly:
                    continue
                bbox = _ring_bbox(poly[0])
                if bbox is None:
                    continue
                min_lon, min_lat, max_lon, max_lat = bbox
                if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                    continue
                if _point_in_ring(lon, lat, poly[0]):
                    in_hole = any(_point_in_ring(lon, lat, h) for h in poly[1:])
                    if not in_hole:
                        return True
            return False
    except (IndexError, KeyError, TypeError):
        return False
    return False


def _polygon_area_approx(geom: dict) -> float:
    """Area approssimata (gradi quadrati, non km): sufficiente per ranking relativo."""
    if not geom:
        return 0.0
    gtype = geom.get("type")
    coords = geom.get("coordinates")
    if not coords:
        return 0.0

    def ring_area(ring: list) -> float:
        # Shoelace formula
        if not ring or len(ring) < 3:
            return 0.0
        a = 0.0
        for i in range(len(ring)):
            try:
                x1, y1 = ring[i][0], ring[i][1]
                x2, y2 = ring[(i + 1) % len(ring)][0], ring[(i + 1) % len(ring)][1]
                a += x1 * y2 - x2 * y1
            except (IndexError, TypeError):
                continue
        return abs(a) / 2.0

    try:
        if gtype == "Polygon":
            area = ring_area(coords[0])
            for hole in coords[1:]:
                area -= ring_area(hole)
            return max(area, 0.0)
        elif gtype == "MultiPolygon":
            total = 0.0
            for poly in coords:
                if not poly:
                    continue
                a = ring_area(poly[0])
                for hole in poly[1:]:
                    a -= ring_area(hole)
                total += max(a, 0.0)
            return total
    except (IndexError, KeyError, TypeError):
        return 0.0
    return 0.0


# ─── Index aourednik snapshots ───────────────────────────────────────────────


def list_snapshots() -> list[tuple[int, Path]]:
    """Elenca tutti gli snapshot aourednik ordinati per anno.

    Returns: lista di (year, filepath) ordinata.
    """
    if not AOUREDNIK_GEOJSON_DIR.exists():
        logger.error("Cartella aourednik non trovata: %s", AOUREDNIK_GEOJSON_DIR)
        return []

    snapshots = []
    for f in AOUREDNIK_GEOJSON_DIR.glob("world_*.geojson"):
        year = _year_from_filename(f.name)
        if year is not None:
            snapshots.append((year, f))
    snapshots.sort(key=lambda x: x[0])
    return snapshots


def choose_snapshot(
    year_start: int,
    year_end: Optional[int],
    snapshots: list[tuple[int, Path]],
) -> Optional[tuple[int, Path]]:
    """Sceglie lo snapshot aourednik piu' adatto per [year_start, year_end].

    Strategia:
      1. Se c'e' uno snapshot nel range [ys, ye], scegli il piu' centrale.
      2. Altrimenti, snapshot piu' vicino entro YEAR_TOLERANCE dal centro.
    """
    if year_end is None:
        year_end = year_start + 100  # euristica: entita' "vive" si assume per 100 anni

    if not snapshots:
        return None

    # Centro della vita dell'entita'
    center = (year_start + year_end) / 2

    # Snapshot dentro il range
    in_range = [(y, f) for y, f in snapshots if year_start <= y <= year_end]
    if in_range:
        # Il piu' vicino al centro
        best = min(in_range, key=lambda x: abs(x[0] - center))
        return best

    # Nessuno nel range: prendi il piu' vicino al centro entro tolerance
    nearest = min(snapshots, key=lambda x: abs(x[0] - center))
    if abs(nearest[0] - center) <= YEAR_TOLERANCE:
        return nearest

    return None


# ─── Core matching ───────────────────────────────────────────────────────────


def _load_snapshot(filepath: Path) -> list[dict]:
    """Carica un snapshot, restituisce lista di feature con props non-None."""
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.exception("Errore caricando %s", filepath)
        return []
    features = data.get("features", [])
    # Filtro feature con NAME valido
    out = []
    for feat in features:
        props = feat.get("properties") or {}
        name = props.get("NAME")
        if name and _normalize(name) not in SKIP_NAMES:
            out.append(feat)
    return out


def _entity_candidate_names(entity: dict) -> list[str]:
    """Estrae tutti i nomi possibili da un'entita' per il matching."""
    names = []
    primary = entity.get("name_original") or entity.get("name") or ""
    if primary:
        names.append(primary)
    for variant in entity.get("name_variants") or []:
        if isinstance(variant, dict):
            n = variant.get("name")
            if n:
                names.append(n)
        elif isinstance(variant, str):
            names.append(variant)
    return names


def _best_name_match(
    candidate_names: list[str],
    features: list[dict],
) -> tuple[Optional[dict], str, float]:
    """Trova la feature con miglior match di nome.

    Returns: (feature, strategy, score) — score in 0.0-1.0.
    """
    if not candidate_names or not features:
        return None, "", 0.0

    try:
        from rapidfuzz import fuzz
    except ImportError:
        fuzz = None

    norm_candidates = [_normalize(n) for n in candidate_names if n]
    norm_candidates = [n for n in norm_candidates if n]

    # Build feature lookup
    feature_names = []
    for feat in features:
        p = feat["properties"] or {}
        fn_primary = _normalize(p.get("NAME") or "")
        fn_subj = _normalize(p.get("SUBJECTO") or "")
        fn_partof = _normalize(p.get("PARTOF") or "")
        feature_names.append((feat, fn_primary, fn_subj, fn_partof))

    # 1. Exact match NAME
    for cand in norm_candidates:
        for feat, fn_p, _, _ in feature_names:
            if cand and fn_p == cand:
                return feat, "exact_name", 1.0

    # 2. Exact match SUBJECTO (suzerain)
    for cand in norm_candidates:
        for feat, _, fn_s, _ in feature_names:
            if cand and fn_s == cand:
                return feat, "subjecto", 0.9

    # 3. Exact match PARTOF
    for cand in norm_candidates:
        for feat, _, _, fn_po in feature_names:
            if cand and fn_po == cand:
                return feat, "partof", 0.8

    # 4. Fuzzy match NAME
    if fuzz is not None:
        best_feat = None
        best_score = 0.0
        for cand in norm_candidates:
            for feat, fn_p, _, _ in feature_names:
                if not fn_p:
                    continue
                score = fuzz.ratio(cand, fn_p)
                if score > best_score:
                    best_score = score
                    best_feat = feat
        if best_feat and best_score >= FUZZY_THRESHOLD:
            return best_feat, "fuzzy_name", best_score / 100.0

    return None, "", 0.0


def _capital_in_polygon(
    entity: dict,
    features: list[dict],
) -> tuple[Optional[dict], str, float]:
    """Fallback rigoroso: feature il cui poligono CONTIENE la capitale.

    ETHICS:
      - Preferiamo point-in-polygon a centroid-distance perche' garantisce
        una relazione geografica reale tra capitale ed entita'.
      - Se piu' poligoni contengono la capitale, scegliamo il piu' piccolo:
        e' piu' probabilmente un'entita' specifica (ducato, regno) piuttosto
        che un contenitore (impero sovrastante).
      - Se il point-in-polygon fallisce, cadiamo su centroid-distance con
        soglia stretta (250 km) — applicabile solo per entita' geograficamente
        isolate con capitale appena fuori dal poligono digitalizzato.

    Returns: (feature, strategy_label, score_0_to_1)
    """
    cap_lat = entity.get("capital_lat")
    cap_lon = entity.get("capital_lon")
    if cap_lat is None or cap_lon is None:
        return None, "", 0.0

    # 1. Primary: point-in-polygon, prefer smallest area
    containers = []
    for feat in features:
        geom = feat.get("geometry", {})
        if _point_in_geometry(cap_lon, cap_lat, geom):
            area = _polygon_area_approx(geom)
            containers.append((feat, area))

    if containers:
        if PREFER_SMALLER_POLYGON:
            containers.sort(key=lambda x: x[1] if x[1] > 0 else float("inf"))
        best_feat = containers[0][0]
        # ETHICS: score 0.55 — point-in-polygon prova che la capitale e'
        # geograficamente contenuta nel poligono, ma NON prova che il
        # poligono sia PRECISAMENTE quell'entita' (potrebbe essere il
        # contenitore sovrastante). La media con BORDERPRECISION la fa
        # il caller. Boundary_aourednik_name nel batch rende esplicita
        # la fonte — l'utente vede sempre da che poligono e' stato preso.
        return best_feat, "capital_in_polygon", 0.55

    # 2. Secondary: nearest centroid, strict threshold
    best_feat = None
    best_dist = float("inf")
    for feat in features:
        centroid = _polygon_centroid(feat.get("geometry", {}))
        if centroid is None:
            continue
        d = _haversine_km(cap_lat, cap_lon, centroid[0], centroid[1])
        if d < best_dist:
            best_dist = d
            best_feat = feat

    if best_feat and best_dist <= MAX_FALLBACK_DIST_KM:
        # Score degradato: 0.3 a 250km, 0.55 a 0km
        score = max(0.3, 0.55 - (best_dist / MAX_FALLBACK_DIST_KM) * 0.25)
        return best_feat, "capital_near_centroid", score
    return None, "", 0.0


def match_entity_aourednik(
    entity: dict,
    snapshots: list[tuple[int, Path]],
    snapshot_cache: dict[Path, list[dict]] | None = None,
) -> AourednikMatch:
    """Tenta il match di un'entita' AtlasPI contro aourednik.

    Args:
        entity: dict con name_original, year_start, year_end, capital_lat/lon, ...
        snapshots: output di list_snapshots()
        snapshot_cache: cache {filepath: features} per evitare re-read

    Returns: AourednikMatch
    """
    year_start = entity.get("year_start")
    year_end = entity.get("year_end")

    if year_start is None:
        return AourednikMatch(matched=False, rejection_reason="no_year_start")

    chosen = choose_snapshot(year_start, year_end, snapshots)
    if chosen is None:
        return AourednikMatch(matched=False, rejection_reason="no_snapshot_in_range")

    snap_year, snap_path = chosen

    # Load snapshot (cached)
    if snapshot_cache is not None and snap_path in snapshot_cache:
        features = snapshot_cache[snap_path]
    else:
        features = _load_snapshot(snap_path)
        if snapshot_cache is not None:
            snapshot_cache[snap_path] = features

    if not features:
        return AourednikMatch(
            matched=False,
            rejection_reason=f"snapshot_empty:{snap_path.name}",
        )

    # Try name-based matching
    candidate_names = _entity_candidate_names(entity)
    feat, strategy, score = _best_name_match(candidate_names, features)

    if feat is None:
        # Fallback: capital-in-polygon (rigoroso) o capital-near-centroid (stretto)
        feat, strategy, score = _capital_in_polygon(entity, features)
        if feat is None:
            return AourednikMatch(
                matched=False,
                aourednik_year=snap_year,
                rejection_reason="no_name_or_spatial_match",
            )

    props = feat["properties"] or {}
    border_prec = props.get("BORDERPRECISION")
    # Confidence finale: media tra score di match e score di precisione
    precision_conf = PRECISION_CONFIDENCE.get(border_prec, 0.45)
    final_confidence = (score + precision_conf) / 2.0

    return AourednikMatch(
        matched=True,
        strategy=strategy,
        confidence=round(final_confidence, 3),
        aourednik_name=props.get("NAME"),
        aourednik_year=snap_year,
        border_precision=border_prec,
        geojson=feat.get("geometry"),
    )
