# ETHICS-006 — Incidente di displacement geografico nei match Natural Earth

**Data**: 2026-04-14
**Stato**: Accettato
**Autore**: Audit post-sync v6.1.1 (Claude Code)
**Impatto**: Alto — ha prodotto 133 boundary errati in produzione

## Sommario

Il 14 aprile 2026, durante l'audit post-sync di v6.1.1, ho scoperto
che **63% dei match Natural Earth (133 su 211) avevano la capitale
dell'entita' FUORI dal poligono assegnato**. In molti casi il
displacement era assurdo:

- Garenganze (regno africano 1856-1891, capitale Bunkeya in DR Congo)
  → matchato a RUS (Russia). Centroide: Siberia.
- Primer Imperio Mexicano (1821-1823, capitale Città del Messico)
  → matchato a BEL (Belgio).
- Reche/Mapuche (popolo indigeno del Cile meridionale)
  → matchato a AUS (Australia).
- Confederate States of America (1861-1865, Richmond)
  → matchato a ITA (Italia).
- Charrua (popolo indigeno del Rio de la Plata)
  → matchato a TCD (Chad).

## Causa

Il fuzzy matcher in `src/ingestion/boundary_match.py` applicava
`rapidfuzz.partial_ratio` con soglia 85% sui nomi dell'entita' e
sui nomi alt delle 200+ entita' Natural Earth. I punteggi alti
venivano generati da:

1. **Substring match su token comuni**: "Kingdom", "Empire",
   "Republic", "General" etc. producevano partial_ratio alti
   contro qualsiasi NE record con lo stesso token.
2. **Accent folding aggressivo**: caratteri non-latini normalizzati
   dalla funzione `_normalize()` diventavano stringhe corte che
   matchavano casualmente qualsiasi nome breve in Natural Earth.
3. **Nessun controllo geografico**: il matcher non verificava che
   la capitale dell'entita' fosse dentro il poligono assegnato.

L'eligibility check (year_end > 1800) non bastava: stati moderni
del XIX secolo con nomi non-latini o con token generici sono
stati matchati a paesi lontani.

## Decisione

### 1. Guardia geografica obbligatoria (implementato)

Il fuzzy match viene accettato **solo se** la capitale dell'entita'
e' contenuta nel poligono matched. Se la capitale non e' nel
poligono, il match viene rigettato e il matcher passa alla
strategia successiva (capital-in-polygon esplicito) o lascia
l'entita' senza boundary NE.

Codice:

```python
# In _try_fuzzy_match, dopo aver trovato il best match:
if entity.get("capital_lat") and entity.get("capital_lon"):
    from shapely.geometry import Point, shape
    point = Point(entity["capital_lon"], entity["capital_lat"])
    try:
        if not shape(rec["geojson"]).contains(point):
            return None  # fuzzy ha pescato, ma geograficamente sbagliato
    except Exception:
        return None
```

### 2. Cleanup dei 133 record gia' in produzione

I 133 entita' con capital OUTSIDE del poligono assegnato vengono
riportati al boundary generato (`name_seeded_boundary()` da
`boundary_generator.py`), con:
- `boundary_source = "approximate_generated"`
- `boundary_ne_iso_a3 = NULL`
- `confidence_score = 0.4`
- `notes` etiche esplicite del cleanup

I 78 record con capital INSIDE il poligono vengono mantenuti —
il loro poligono ha almeno senso geografico, anche se il confine
moderno puo' essere anacronistico rispetto all'estensione
storica (questo rientra nel trade-off accettato in ETHICS-005).

### 3. Nessun tentativo di rimatch automatico

I 133 record puliti NON vengono riassegnati automaticamente ad
altri candidati NE. Sarebbe un altro processo di matching
fuzzy, soggetto agli stessi rischi. Vengono invece lasciati
con boundary approssimativo esplicito, e un match piu' accurato
sara' compito di una pipeline successiva (es. matching per
coordinate + ISO esplicito inferito dalla geografia).

## Impatto sui dati

Prima del fix: 211 NE matches, 78 geograficamente coerenti (37%).

Dopo il fix:
- 78 NE matches conservati (capitale dentro il poligono)
- 133 entita' riassegnate a `approximate_generated` (poligono
  ellittico deterministico attorno alla capitale, seed derivato
  dal nome)
- Nessuna perdita di informazione storica (i dati non-geometrici
  restano immutati)

## Test

`tests/test_boundary_match_geographic_guard.py` — 4 test:

1. Fuzzy match accettato se capitale nel poligono.
2. Fuzzy match rigettato se capitale fuori dal poligono.
3. Fuzzy match rigettato se l'entita' non ha capitale (conservatism).
4. Fuzzy match conservato se il poligono NE contiene la capitale
   ma l'eligibility fallisce per altri motivi (consistency check).

## Lezione

**Ogni match cross-dataset basato su nomi ha bisogno di un
controllo fisico/geometrico di sanita'.** Il nome da solo non
garantisce la corrispondenza geografica. Per AtlasPI, la
capitale e' il ground truth: se il matcher propone un
poligono che non contiene la capitale, il match e' errato per
costruzione.

Prossima iterazione (v6.2): considerare anche la centroid
distance come soft-check (capitale-centroide < 500 km) per
ridurre falsi positivi in casi dove il poligono NE e' molto
grande e la capitale e' vicina al bordo.

## Vedi anche

- ETHICS-004: confini approssimativi generati
- ETHICS-005: boundary Natural Earth e anacronismo
- `src/ingestion/boundary_match.py`
- `src/ingestion/boundary_generator.py`
- `tests/test_boundary_match_geographic_guard.py`
