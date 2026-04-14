# ETHICS-005 — Boundary da Natural Earth e territori contestati

**Data**: 2026-04-14
**Stato**: Accettato
**Autore**: Pipeline boundary enrichment (Claude Code)
**Impatto**: Alto — definisce come e quando applicare confini moderni
(Natural Earth) a entita' AtlasPI, e come gestire i territori contestati.

## Contesto

AtlasPI contiene 752 entita' geopolitiche dal 4500 a.C. al 2024. Solo
~23% (174) ha boundary reali derivati da fonti cartografiche storiche
(`historical-basemaps`). Il restante 76% ha boundary `approximate_generated`
o non ha boundary affatto.

Per migliorare la coverage qualitativa (60%+ con dati reali), introduciamo
una pipeline che usa Natural Earth (https://www.naturalearthdata.com/),
dataset cartografico in pubblico dominio (CC0), per matchare le entita'
*moderne* con i confini di stati contemporanei.

## Rischio principale: anacronismo

Applicare confini moderni a stati antichi e' una distorsione storica grave.
Esempi di errori da evitare:
- Imperium Romanum (27 a.C. - 476 d.C.) → Italia moderna: ERRATO.
  L'impero romano si estendeva da Britannia a Mesopotamia.
- Tawantinsuyu (Inca, 1438-1533) → Peru moderno: ERRATO.
  L'impero copriva anche Ecuador, Bolivia, parte di Cile e Argentina.
- Khanato di Persia → Iran moderno: ERRATO.
  I confini sono profondamente diversi.

## Decisione: vincolo di eligibilita'

Solo entita' che soddisfano UNO dei seguenti criteri possono essere
candidate al match con Natural Earth:

1. **Year_end > 1800**: l'entita' termina dopo la nascita del sistema
   degli stati-nazione moderni. Esempio: Imperio Espanol (1492-1976).
2. **Year_end == None E year_start > 1700**: l'entita' e' "ancora viva" e
   nasce in epoca pre-moderna prossima. Esempio: Konungariket Sverige
   (1523-presente).

Per tutte le altre entita' (year_end <= 1800), si usa esclusivamente
`name_seeded_boundary` di `boundary_generator.py` con confidence_score 0.4
e `boundary_source = "approximate_generated"` (vedi ETHICS-004).

## Strategie di matching (in ordine di priorita')

1. **ISO_A3 esplicito**: se l'entita' AtlasPI ha campo `iso_a3` o
   menzione `ISO: XYZ` in `ethical_notes`, match diretto.
   Confidence: 1.0.
2. **Match esatto sul nome**: confronto case-insensitive e accent-folded
   tra `name_original`/`name_variants` e i nomi Natural Earth (NAME,
   NAME_LONG, FORMAL_EN, SOVEREIGNT, e tutti i NAME_xx multilingua).
   Confidence: 1.0.
3. **Fuzzy match** (rapidfuzz) con soglia 85%. Usa il MAX di ratio,
   token_set_ratio e partial_ratio per robustezza ai nomi multi-parola.
   Confidence: score / 100.
4. **Capitale dentro il poligono**: se la capitale (lat/lon) e' contenuta
   in UN solo poligono moderno (no ambiguita'), match per inclusione
   geografica. Confidence: 0.6.

## Rischio secondario: territori contestati

Natural Earth marca alcuni territori come contestati. Quando il match
ricade su uno di questi, AtlasPI non sceglie un lato: documenta la
disputa.

Codici ISO contestati gestiti esplicitamente (`DISPUTED_ISO_CODES` in
`boundary_match.py`):

| ISO_A3 | Territorio | Disputa |
|--------|-----------|---------|
| TWN | Taiwan | Sovranita' contesa con la RPC |
| ESH | Western Sahara | Marocco vs RASD/Polisario |
| PSE | Palestina | Occupazione israeliana, status ONU "stato osservatore" |
| XKO | Kosovo | Riconoscimento parziale (Serbia non riconosce) |
| CYN | Cipro Nord | Riconosciuta solo dalla Turchia |
| KAS | Kashmir | Disputa India-Pakistan-Cina |
| SOL | Somaliland | De facto indipendente, non riconosciuta |

Quando una di queste viene matchata:
- L'entita' AtlasPI MANTIENE il suo `status` originale (spesso `disputed`).
- Una nota etica viene aggiunta a `ethical_notes`:
  `ETHICS-005: boundary da Natural Earth (ISO XYZ, name). Territorio
   contestato — vedi ETHICS-005-boundary-natural-earth.md`.
- Il `confidence_score` non viene aumentato sopra 0.7 anche se il match
  e' esatto, perche' la rappresentazione cartografica stessa e' contestata.

### Caso particolare: Taiwan

AtlasPI puo' rappresentare Taiwan in modi diversi a seconda dell'anno:
- Come parte dell'impero Qing (1683-1895)
- Come colonia giapponese (1895-1945)
- Come Repubblica di Cina (1912-presente)
- In disputa con la RPC (1949-presente)

Il match Natural Earth fornisce il poligono *fisico* dell'isola,
che e' indipendente dalla disputa di sovranita'. La disputa va
documentata nei `name_variants`, `claims[]`, `ethical_notes` e
`status='disputed'`.

### Caso particolare: Israele/Palestina

AtlasPI distingue tra:
- L'entita' moderna `Israel` (1948-presente) → ISO ISR
- L'entita' moderna `State of Palestine` / territori palestinesi → ISO PSE

Natural Earth ha sia ISR che PSE come feature distinte. Il match va
fatto con CAUTELA: se l'entita' AtlasPI si chiama p.es. "فلسطين / ישראל"
(rappresentazione duale storica), va trattata manualmente o lasciata
con boundary generato — il match automatico forzerebbe una scelta.

## Trasparenza nel dato

Ogni boundary aggiunto via NE viene marcato con:

```json
{
  "boundary_geojson": { "type": "Polygon|MultiPolygon", ... },
  "boundary_source": "natural_earth",
  "boundary_ne_iso_a3": "ITA",
  "confidence_score": 0.85,  // o piu' basso se fuzzy/capital
  "ethical_notes": "...ETHICS-005: boundary da Natural Earth..."
}
```

Il campo `boundary_source` distingue:
- `historical_map` — confine derivato da dati cartografici storici reali
- `natural_earth` — confine derivato da Natural Earth (stato moderno)
- `academic_source` — confine da pubblicazioni accademiche
- `approximate_generated` — boundary generato computazionalmente

## Idempotenza

La pipeline `enrich_all_boundaries.py` e' idempotente:
- I boundary `historical_map` / `academic_source` non vengono MAI toccati.
- I boundary `natural_earth` non vengono MAI sovrascritti.
- Solo i `approximate_generated` possono essere upgradati a `natural_earth`
  se viene trovato un match valido (questo e' un miglioramento monotono
  della qualita' del dato).
- Boundary mancanti o di tipo Point vengono sempre rigenerati o matchati.

## Backup obbligatori

Prima di ogni modifica, lo script crea un backup `.bak` accanto al file
batch originale. Il backup viene sovrascritto al run successivo (e' un
backup "ultima esecuzione", non versioning storico — quello e' affidato
a git).

## Modulo responsabile

- `src/ingestion/natural_earth_import.py` — caricamento shapefile
- `src/ingestion/boundary_match.py` — matching strategies
- `src/ingestion/enrich_all_boundaries.py` — pipeline end-to-end

## Principi CLAUDE.md applicati

- **Principio 1 (Verita' prima del comfort)**: rifiutiamo l'anacronismo
  anche quando renderebbe il dataset "piu' completo".
- **Principio 2 (Nessuna versione unica della storia)**: i territori
  contestati ottengono note esplicite, non vengono "risolti" via match.
- **Principio 3 (Trasparenza dell'incertezza)**: `confidence_score`
  modulato per strategia (1.0 esatto, 0.6 capital-in-polygon),
  `boundary_source` esplicito, ethical_notes per i disputed.
- **Principio 4 (Nessun bias)**: gli stessi criteri si applicano a
  Italia/Iran/Cina/USA — nessuna deroga geografica.
