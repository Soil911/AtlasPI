"""Generazione di confini approssimativi per entità senza boundary_geojson.

Quando un'entità ha solo le coordinate della capitale ma nessun poligono di confine,
questo modulo genera un poligono approssimativo basato su:
- Coordinate del centro (capitale)
- Tipo di entità (impero, regno, città-stato, ecc.)
- Periodo storico (per stimare la dimensione)

ETHICS: I confini generati da questo modulo sono APPROSSIMAZIONI COMPUTAZIONALI,
non dati cartografici reali. Ogni entità arricchita con questo strumento DEVE avere
boundary_source = "approximate_generated" per distinguerla dai dati storici verificati.
Vedi ETHICS-004-confini-generati-approssimativi.md per la decisione etica completa.

Il confidence_score viene ridotto di 0.1 per riflettere l'incertezza aggiuntiva.
"""

import math
import random
from typing import Optional

# ETHICS: i raggi sono stime conservative basate su storiografia comparata.
# Non rappresentano confini reali ma ordini di grandezza plausibili.
# I valori sono in chilometri e vengono convertiti in gradi approssimativi.
ENTITY_TYPE_RADIUS_KM = {
    "empire": (800, 1500),
    "kingdom": (200, 500),
    "sultanate": (150, 400),
    "city-state": (30, 80),
    "colony": (300, 800),
    "caliphate": (600, 1200),
    "duchy": (50, 150),
    "principality": (50, 150),
    "confederation": (300, 600),
    "federation": (300, 600),
    "khanate": (400, 900),
    "republic": (100, 350),
    "dynasty": (200, 600),
    "disputed_territory": (50, 200),
    "city": (10, 30),
}

# Rough era-based scaling factors.
# Earlier periods tend to have smaller controlled territories per entity type,
# while later periods (especially colonial) can be larger.
ERA_SCALE = {
    (-5000, -1000): 0.7,   # Bronze Age — smaller polities
    (-1000, -500): 0.8,    # Iron Age
    (-500, 0): 0.9,        # Classical antiquity
    (0, 500): 1.0,         # Late antiquity / early empires at peak
    (500, 1000): 0.9,      # Early medieval — fragmentation
    (1000, 1500): 1.0,     # High/late medieval
    (1500, 1800): 1.1,     # Early modern / colonial expansion
    (1800, 2000): 1.0,     # Modern era
}

# Approximate km-per-degree at different latitudes
# 1 degree longitude = 111.32 * cos(latitude) km
# 1 degree latitude  = ~110.57 km
KM_PER_DEG_LAT = 110.57


def _km_per_deg_lon(lat: float) -> float:
    """Approssimazione dei km per grado di longitudine a una data latitudine."""
    return 111.32 * math.cos(math.radians(abs(lat)))


def _get_era_scale(year_start: int, year_end: Optional[int]) -> float:
    """Restituisce il fattore di scala per l'era storica."""
    mid_year = year_start
    if year_end is not None:
        mid_year = (year_start + year_end) // 2

    for (era_start, era_end), scale in ERA_SCALE.items():
        if era_start <= mid_year < era_end:
            return scale
    return 1.0


def _get_base_radius_km(entity_type: str, year_start: int,
                        year_end: Optional[int]) -> float:
    """Calcola il raggio base in km per il tipo di entità e l'era."""
    r_min, r_max = ENTITY_TYPE_RADIUS_KM.get(entity_type, (100, 300))
    era_scale = _get_era_scale(year_start, year_end)

    # Use the midpoint of the range, scaled by era
    base = (r_min + r_max) / 2.0 * era_scale

    # Add some deterministic variation based on the year to avoid uniformity
    seed_val = abs(hash((entity_type, year_start, year_end or 0))) % 1000
    variation = (seed_val / 1000.0 - 0.5) * 0.3  # +-15%
    base *= (1.0 + variation)

    # Clamp to the type's range (scaled)
    base = max(r_min * 0.8, min(r_max * 1.2 * era_scale, base))

    return base


def _clamp_latitude(lat: float) -> float:
    """Mantieni la latitudine nel range valido."""
    return max(-85.0, min(85.0, lat))


def _clamp_longitude(lon: float) -> float:
    """Mantieni la longitudine nel range valido, con wrapping."""
    while lon > 180.0:
        lon -= 360.0
    while lon < -180.0:
        lon += 360.0
    return lon


def generate_approximate_boundary(
    lat: float,
    lon: float,
    entity_type: str,
    year_start: int,
    year_end: Optional[int] = None,
    num_vertices: int = 12,
    seed: Optional[int] = None,
) -> dict:
    """Genera un poligono GeoJSON approssimativo per un'entità storica.

    ETHICS: questo genera un confine APPROSSIMATIVO, non un dato storico reale.
    L'output deve sempre essere marcato con boundary_source = "approximate_generated".

    Args:
        lat: Latitudine del centro (capitale).
        lon: Longitudine del centro (capitale).
        entity_type: Tipo di entità (empire, kingdom, city-state, ecc.).
        year_start: Anno di inizio dell'entità.
        year_end: Anno di fine dell'entità (opzionale).
        num_vertices: Numero di vertici del poligono (8-16).
        seed: Seed per la riproduzione deterministica.

    Returns:
        Dizionario GeoJSON di tipo Polygon.
    """
    num_vertices = max(8, min(16, num_vertices))

    # Deterministic seed based on entity properties for reproducibility
    if seed is None:
        seed = abs(hash((lat, lon, entity_type, year_start, year_end or 0)))
    rng = random.Random(seed)

    radius_km = _get_base_radius_km(entity_type, year_start, year_end)

    # Convert radius from km to degrees
    radius_lat_deg = radius_km / KM_PER_DEG_LAT
    km_per_lon = _km_per_deg_lon(lat)
    if km_per_lon < 1.0:
        km_per_lon = 1.0  # Safety for extreme latitudes
    radius_lon_deg = radius_km / km_per_lon

    # Generate irregular polygon vertices
    vertices = []
    angle_step = 2 * math.pi / num_vertices

    for i in range(num_vertices):
        angle = i * angle_step

        # Vary the radius at each vertex by +-20-30% for natural look
        variation = rng.uniform(0.70, 1.30)

        # Slight elliptical tendency — entities often stretch E-W or N-S
        ellipse_factor_lon = rng.uniform(0.85, 1.15)
        ellipse_factor_lat = rng.uniform(0.85, 1.15)

        r_lon = radius_lon_deg * variation * ellipse_factor_lon
        r_lat = radius_lat_deg * variation * ellipse_factor_lat

        v_lon = lon + r_lon * math.cos(angle)
        v_lat = lat + r_lat * math.sin(angle)

        # Clamp to valid ranges
        v_lat = _clamp_latitude(v_lat)
        v_lon = _clamp_longitude(v_lon)

        vertices.append([round(v_lon, 4), round(v_lat, 4)])

    # Close the polygon (first point == last point)
    vertices.append(vertices[0][:])

    return {
        "type": "Polygon",
        "coordinates": [vertices],
    }


def estimate_polygon_area_km2(geojson: dict) -> float:
    """Stima approssimativa dell'area di un poligono GeoJSON in km^2.

    Usa la formula del Shoelace con conversione gradi->km.
    Utile per verificare che i confini generati siano plausibili.
    """
    if geojson.get("type") != "Polygon":
        return 0.0

    coords = geojson["coordinates"][0]
    if len(coords) < 4:
        return 0.0

    # Centroid for km conversion
    avg_lat = sum(c[1] for c in coords) / len(coords)
    km_lon = _km_per_deg_lon(avg_lat)
    km_lat = KM_PER_DEG_LAT

    # Shoelace formula in km
    n = len(coords) - 1  # exclude closing duplicate
    area = 0.0
    for i in range(n):
        x1 = coords[i][0] * km_lon
        y1 = coords[i][1] * km_lat
        x2 = coords[(i + 1) % n][0] * km_lon
        y2 = coords[(i + 1) % n][1] * km_lat
        area += x1 * y2 - x2 * y1

    return abs(area) / 2.0
