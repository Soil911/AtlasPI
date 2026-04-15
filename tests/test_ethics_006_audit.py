"""ETHICS-006 audit: capital-in-polygon CI guardia.

v6.3.2 — secondo livello di difesa contro regressioni del fuzzy matcher.

L'audit scansiona tutte le entità con `boundary_source != "approximate_generated"`
(cioè boundary "reali", non sintetizzate dal generator) e verifica che la
capitale dichiarata cada dentro (o entro tolleranza) il poligono assegnato.

Storia:
    v6.1.2 ha introdotto la guardia capital-in-polygon DURANTE il matching
    (vedi `src/ingestion/boundary_match.py`), eliminando 133 displaced
    matches catastrofici (Garenganze→Russia, CSA→Italia, Mapuche→Australia).
    Però non c'era nulla che impedisse a un futuro batch JSON di
    re-introdurre boundary copia-e-incolla sbagliati. Questo audit è quel
    blocco di sicurezza: se un dato sale, il test fallisce e il PR si
    blocca prima del merge.

Tolleranza (logica a due livelli):
    * Il MATCHER in `boundary_match.py` usa 50 km come soft threshold
      DURANTE il matching — per preferire un boundary vicino alla capitale
      rispetto ad alternative ambigue. Questo è giusto perché al momento
      del match abbiamo il catalogo completo delle alternative.
    * L'AUDIT (questo test) opera DOPO il fatto, sui dati già committati,
      e ha un ruolo diverso: catturare REGRESSIONI CATASTROFICHE, non
      imprecisioni minori. Nella pratica i bug etici che importa catturare
      sono wrong-country / wrong-continent copy-paste (1000+ km), non
      "la simplified-polygon-per-un-impero-di-4000km perde Cusco di 300 km".
    * Quindi `AUDIT_TOLERANCE_KM = 400 km` — sopra questa soglia è
      matematicamente impossibile una simplification noise (significa
      ~4° di latitudine o di longitudine equatoriale) e si tratta quasi
      certamente di displacement semantico.

    Casi noti sotto i 400 km (accettati come baseline):
        * Tawantinsuyu (304 km) — impero Inca 4000km di Ande, 35 vertici
        * Nhà Tây Sơn (82 km) — Vietnam, 13 vertici
        * Kemet (72 km) — Egitto, 13 vertici
        * Tu'i Tonga (68 km) — Tonga (isole), 13 vertici
        * Majapahit (61 km) — Java, 27 vertici
    Tutti `boundary_source = "historical_map"` (poligoni semplificati da
    mappe storiche). Non sono bug, sono limitazioni intrinseche della
    rappresentazione vettoriale di grandi territori pre-moderni.

Skip conditions:
    * Entità con `boundary_geojson IS NULL` — niente da verificare.
    * Entità con `boundary_source == "approximate_generated"` — il boundary
      è stato sintetizzato attorno alla capitale, quindi tautologicamente
      la capitale è dentro. Skippiamo per evitare rumore.
    * Entità con `capital_lat IS NULL OR capital_lon IS NULL` — non
      possiamo testare il contenimento senza coordinate.

Failure mode:
    Lista esplicita di violazioni (entity_id, name, boundary_source,
    distance_km) — utile per chi deve fixare i dati.
"""

from __future__ import annotations

import json

import pytest

from src.db.database import SessionLocal
from src.db.models import GeoEntity

# Audit-specific threshold (vedi docstring del modulo per la rationale).
# Più alto del matcher (50 km) perché l'audit cattura regressioni
# catastrofiche, non simplification noise.
AUDIT_TOLERANCE_KM = 400.0


def _capital_displacement_km(
    capital_lat: float, capital_lon: float, geojson_str: str
) -> float | None:
    """Restituisce 0.0 se la capitale è dentro il poligono, distanza km se fuori.

    Restituisce None se shapely non è disponibile o il GeoJSON è malformato.
    """
    try:
        from shapely.geometry import Point, shape
    except ImportError:
        return None
    try:
        geojson = json.loads(geojson_str)
        poly = shape(geojson)
        pt = Point(float(capital_lon), float(capital_lat))
        if poly.contains(pt) or poly.touches(pt):
            return 0.0
        d_deg = poly.distance(pt)
        # Conversione gradi → km: 111 km/deg lat, 111*cos(lat) km/deg lon.
        import math
        km_per_deg_lat = 111.0
        km_per_deg_lon = 111.0 * max(0.1, math.cos(math.radians(float(capital_lat))))
        return d_deg * (km_per_deg_lat + km_per_deg_lon) / 2.0
    except Exception:
        return None


def test_capital_in_polygon_for_real_boundaries():
    """Ogni entità con boundary "reale" deve avere capitale dentro/vicino al polygon.

    Se questo test fallisce, hai aggiunto (o re-importato) un'entità con
    un boundary_geojson che non è geograficamente coerente con la sua
    capitale. Cause tipiche:

        1. Copy-paste di un boundary da un'altra entità senza sostituire
           le coordinate. Fix: rigenera il boundary o aggiorna la capitale.
        2. Fuzzy match catastrofico (Garenganze→Russia). Fix: rifai il
           boundary_match con la guardia ETHICS-006.
        3. Entità con capitale storicamente migrata ma boundary aggiornato
           solo per la versione finale. Fix: marca come
           `boundary_source = "approximate_generated"` e logga in
           `ethical_notes`.

    Tolleranza: 400 km (audit hard threshold). Vedi docstring del modulo
    per la giustificazione del valore (più alto del matcher per evitare
    falsi positivi su simplification noise di empire-scale polygons).
    """
    pytest.importorskip("shapely", reason="shapely required for geometric audit")

    db = SessionLocal()
    try:
        # Solo entità con boundary "reale" (non sintetizzato), con capitale
        # e con boundary_geojson non vuoto.
        entities = (
            db.query(GeoEntity)
            .filter(GeoEntity.boundary_geojson.isnot(None))
            .filter(GeoEntity.capital_lat.isnot(None))
            .filter(GeoEntity.capital_lon.isnot(None))
            .filter(
                (GeoEntity.boundary_source != "approximate_generated")
                | (GeoEntity.boundary_source.is_(None))
            )
            .all()
        )

        violations: list[tuple[int, str, str, float]] = []
        unverifiable = 0
        verified = 0

        for e in entities:
            dist = _capital_displacement_km(
                e.capital_lat, e.capital_lon, e.boundary_geojson
            )
            if dist is None:
                unverifiable += 1
                continue
            verified += 1
            if dist > AUDIT_TOLERANCE_KM:
                violations.append(
                    (e.id, e.name_original, e.boundary_source or "<null>", dist)
                )

        # Soglia di accettabilità: nessuna violazione tollerata. Se il
        # dataset legacy ne ha alcune note (rare ma documentate), questo
        # test andrà aggiornato esplicitamente con un allow-list spiegato
        # nei commenti — meglio l'esplicito che il silenzio.
        if violations:
            preview = "\n".join(
                f"  id={vid} {name!r} src={src} displaced={dist:.1f} km"
                for vid, name, src, dist in violations[:20]
            )
            pytest.fail(
                f"ETHICS-006: {len(violations)} entità con capitale fuori dal "
                f"boundary_geojson di oltre {AUDIT_TOLERANCE_KM} km "
                f"(verified={verified}, unverifiable={unverifiable}).\n"
                f"Prime {min(len(violations), 20)}:\n{preview}\n\n"
                f"Fix: rigenera il boundary, correggi le coordinate della "
                f"capitale, oppure marca esplicitamente come "
                f"boundary_source='approximate_generated' se il polygon è "
                f"derivato dalla capitale stessa."
            )
    finally:
        db.close()


def test_capital_in_polygon_audit_runs_on_dataset():
    """Sanity check: l'audit gira su un campione non vuoto di entità.

    Se questo test fallisce significa che il dataset non ha più entità
    con boundary "reale" + capitale + shapely disponibile. Probabilmente
    indica un bug nel seed o nelle dependencies, non un bug etico.
    """
    pytest.importorskip("shapely", reason="shapely required for geometric audit")

    db = SessionLocal()
    try:
        count = (
            db.query(GeoEntity)
            .filter(GeoEntity.boundary_geojson.isnot(None))
            .filter(GeoEntity.capital_lat.isnot(None))
            .filter(GeoEntity.capital_lon.isnot(None))
            .filter(
                (GeoEntity.boundary_source != "approximate_generated")
                | (GeoEntity.boundary_source.is_(None))
            )
            .count()
        )
        assert count > 50, (
            f"Audit ETHICS-006 degenere: solo {count} entità verificabili. "
            f"Atteso > 50. Probabile bug nel seed o in shapely."
        )
    finally:
        db.close()
