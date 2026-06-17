# ETHICS-016 — Floor temporale delle query (rimozione del limite -4000)

**Status**: Adottato (v6.99.104 — 2026-06-17)
**Principio**: CLAUDE.md "Cos'è questo progetto" (*qualsiasi epoca*) + #1 (Verità
prima del comfort) + #4 (Nessun bias geografico o culturale dominante)
**Origine**: AI Co-Founder suggestion #83 (accettata da Clirim) — consumatore
esterno `182.232.122.40` ha scansionato anni -4500..-4050 su `/v1/export/geojson`,
25 richieste **tutte rifiutate 422** dal validatore `year >= -4000`.

## Contesto

La missione di AtlasPI è documentare entità geopolitiche in **"qualsiasi epoca"**.
Eppure tre endpoint validavano il parametro `year` con un floor di **-4000**
(`/v1/entity`, `/v1/entities`, `/v1/export/geojson`) e di **-10000**
(`/v1/export/sites/geojson`), mentre `periods.py` usava già **-4000000**.

Questa incoerenza non era solo cosmetica: il floor -4000 **nascondeva 14 entità
che il dataset GIÀ contiene** con `year_start < -4000`. Una query per anno o un
export su quelle epoche restituiva `422 Unprocessable Entity` invece dei dati
realmente presenti. Le 14 entità (prod, 2026-06-17):

| id | nome | tipo | year_start |
|---|---|---|---|
| 309 | Aboriginal Australian Nations | confederation | -65000 |
| 316 | Papua New Guinea Highland societies | confederation | -50000 |
| 310 | Kulin Nation | confederation | -40000 |
| 311 | Yolŋu | confederation | -40000 |
| 771 | Noongar boodja | tribal_nation | -40000 |
| 317 | Solomon Islands chiefdoms | confederation | -30000 |
| 772 | Wiradjuri | tribal_nation | -20000 |
| 222 | Wôpanâak | confederation | -12000 |
| 308 | Torres Strait Islander peoples | confederation | -8000 |
| 541 | Aonikenk | confederation | -8000 |
| 519 | Selk'nam | confederation | -8000 |
| 292 | Çatalhöyük | city-state | -7500 |
| 291 | Nabta Playa | city-state | -7500 |
| 168 | 𒆠𒂗𒄀 (Kengi/Sumer) | city-state | -4500 |

## Rischio di distorsione

Il floor -4000 colpiva in modo **sproporzionato popoli indigeni e
decentralizzati** (nazioni aborigene australiane, Papua, Torres Strait, Selk'nam,
Wôpanâak) e i primi insediamenti neolitici (Çatalhöyük, Nabta Playa, Sumer).
Erano fisicamente nel database ma **invisibili** a qualunque consumatore che
filtrasse per anno o esportasse GeoJSON di un'epoca pre-4000 a.C. — una
cancellazione *de facto* delle origini più antiche dell'umanità, e proprio delle
culture meno rappresentate altrove. Viola direttamente il principio #4 (nessun
bias culturale dominante) e la promessa di "qualsiasi epoca", oltre a contraddire
[ETHICS-009](ETHICS-009-categorie-politiche-colon-imposte-su-polities-indigene.md)
sul rispetto delle polities indigene.

## Alternative considerate

1. **(b) Mantenere il floor -4000 + documentare il range / clampare lo slider
   frontend** → rifiutato: lascia 14 entità reali irraggiungibili via query/export.
   Documentare un limite arbitrario non lo rende meno una cancellazione, e
   "qualsiasi epoca" non ammette un muro al 4000 a.C.
2. **Restituire un risultato vuoto (200) invece di 422 per anni < -4000** →
   rifiutato: peggiore della verità, perché segnalerebbe "nessuna entità esiste in
   quell'epoca" quando invece esistono (Sumer -4500 ricadrebbe nel vuoto).
3. **(a) Allineare il floor a -4000000 su tutti gli endpoint** → **adottato**.
   Coerente con `periods.py`, espone i dati reali già presenti, mantiene un floor
   di sanità (-4M a.C., epoca degli ominidi) per rifiutare input palesemente
   garbage.

## Decisione adottata

Floor del parametro `year` portato a **`ge=-4000000`** in:
- `src/api/routes/entities.py` (`/v1/entity`, `/v1/entities`)
- `src/api/routes/export.py` (`/v1/export/geojson`, `/v1/export/sites/geojson`)

Già a -4000000 (invariato): `src/api/routes/periods.py`.

Test aggiornati (`tests/test_validation.py`): `test_year_too_low` ora verifica il
rifiuto **sotto** il nuovo floor (-5000000); aggiunto `test_year_pre_4000_bce_accepted`
che verifica l'accettazione di -7500 (Çatalhöyük).

## Note

Il floor -4000000 è un limite di sanità input, non un'affermazione che esistano
entità così antiche. L'incertezza delle datazioni pre-storiche resta governata da
`confidence_score` + `sources[]` per-entità ([ETHICS-013](ETHICS-013-confidence-status-coherence.md)).
