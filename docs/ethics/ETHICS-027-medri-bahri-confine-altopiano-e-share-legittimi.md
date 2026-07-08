# ETHICS-027 — Medri Bahri: confine altopiano (non Eritrea moderna) + share legittimi Cambogia

**Data**: 2026-07-08
**Versione**: v6.99.133
**Stato**: implementato
**Classe**: ETHICS-005 (approssimazione confini) + ETHICS-002/026 (colonialismo) +
ETHICS-014 (shared-polygon re-classification) + valori CLAUDE.md §2 (nessuna versione
unica) e §3 (trasparenza incertezza)
**Origine**: AI Co-Founder daily run — suggestion #94 (`geometric_bug`, ACCEPTED) e
#95 (`consistency_bug`, ACCEPTED).

---

## Contesto

Il co-founder analyzer ha segnalato (accettati da Clirim) due bug shape-level e una
incoerenza temporale cross-resource. L'analisi ha distinto **un bug reale** da **un
falso positivo** e **una deriva JSON↔prod**.

## Decisione 1 — Medri Bahri #658: confine ERI moderno → altopiano (BUG REALE)

### Il problema
Medri Bahri (ምድረ ባሕሪ, regno cristiano d'altopiano, 1137-1879) aveva
`boundary_source=natural_earth`, `boundary_ne_iso_a3=ERI`: gli era stato assegnato via
**country-code matching** il poligono dell'**Eritrea moderna** (Natural Earth). Doppio
problema:

1. **Anacronismo**: i confini dell'Eritrea moderna sono demarcazioni coloniali del
   XX secolo (linea col Sudan, tripoint di Gibuti), impossibili per un regno medievale.
2. **Estensione**: proietta all'indietro il *contenitore coloniale*. Le stesse
   `territory_changes` del record documentano un'estensione **d'altopiano** — «tra il
   fiume Mareb e la costa» — con la **costa (Massawa, Arkiko) presa dagli Ottomani nel
   1557** e i **bassopiani occidentali** (Barka/Gash; popoli Beja, Kunama, Nara) mai
   parte del regno cristiano. Il poligono ERI era inoltre **byte-identico** a
   #1067 Colonia Eritrea (share flaggato).

### Scelta adottata
Confine sostituito con un'**approssimazione del nucleo d'altopiano** (Hamasien, Serae,
Akele Guzai; ~19.000 km² vs ~121.000 km² dell'Eritrea moderna), poligono a 9 vertici
tra 14,35–15,85°N e 38,2–39,6°E (esclude bassopiani occidentali e piana costiera/Massawa).
`boundary_source=historical_approximation` (→ esente da re-extract di
`enrich_all_boundaries` / cleanup NE / startup guard), `boundary_ne_iso_a3=NULL`,
confidence **0.6** (invariata: incertezza esplicita), status `uncertain` (invariato).

### Mitigazione del rischio di distorsione (CLAUDE.md §2)
Non si sostituisce «una versione con un'altra». Le `ethical_notes` esistenti — che
riportano **sia** la lettura nazionalista eritrea (Medri Bahri come tradizione politica
eritrea distinta) **sia** quella etiope (provincia vassalla d'altopiano) — sono
**preservate**. Vi si **appende** una nota di provenienza che (a) spiega che il confine
precedente era l'outline moderno auto-assegnato (anacronismo + fuzzy-match), (b) chiarisce
che la nuova geometria è un'approssimazione low-confidence del **nucleo durevolmente
controllato**, **non** un'aggiudicazione della rivendicazione territoriale massimale.

### #1067 Colonia Eritrea — invariata
La Colonia Eritrea (1890-1941) mantiene il poligono Eritrea-piena: i confini moderni
**derivano** dalla demarcazione coloniale italiana, quindi l'outline è appropriato per la
colonia (conf 0.9). Il fix di #658 risolve anche il flag di share (le due entità non sono
più byte-identiche).

## Decisione 2 — Cambogia #256/#1062/#1063: share LEGITTIMO (falso positivo)

Il gruppo condivide un poligono perché #256 (Regno di Cambogia moderno, 1953-,
`natural_earth` KHM) è l'ancora legittima e **#1062 Repubblica Popolare di Kampuchea
(1979-89)** e **#1063 Stato di Cambogia (1989-93)** occupavano **lo stesso territorio
nazionale** (confini cambogiani stabili dal 1953). Condividere il confine è
*storicamente corretto*; perturbarlo sarebbe **falsa precisione**, non un fix.

L'analyzer non poteva distinguere «stati successori su confini identici» da «fuzzy-match»
perché un membro ha sorgente raw (`natural_earth`). Aggiunto un allowlist di gruppo
`REVIEWED_LEGITIMATE_SHARED_GROUPS` in `scripts/ai_cofounder_analyze.py` (mirror di
`MANUALLY_CURATED_IDS` a livello di gruppo): un gruppo shared è soppresso se il suo set di
owner è sottoinsieme di un gruppo revisionato-legittimo. Nessuna modifica geometrica.

## Decisione 3 — Evento #424 (First Intermediate Period): relink Kemet #26

`consistency_bug` #95: l'evento #424 «whm mswt tpy» (First Intermediate Period,
DISSOLUTION_STATE, -2181..-2055) era linkato a #1057 *Middle Kingdom* (-2055..-1650) →
mismatch temporale (l'evento **precede** l'entità). Il JSON sorgente linka a **"Kemet"**,
che il resolver mappa esattamente a **#26 Kemet** (-3100..-30); la produzione era andata
in **deriva** verso #1057 (artefatto della ristrutturazione egizia ETHICS-023). Link di
produzione ri-puntato a **#26 Kemet** (l'FIP è un periodo di frammentazione trans-dinastico
nel continuum Kemet): risolve il mismatch **e** riconcilia prod↔JSON. Nessuna modifica JSON
(già "Kemet"); l'ingester è idempotente e non si auto-correggeva.

## Provenienza tecnica
- JSON: `data/entities/batch_21_horn_africa_balkans.json` (#658).
- SQL prod: `UPDATE geo_entities … WHERE id=658;` + `UPDATE event_entity_links … WHERE id=568;`
- Analyzer: `scripts/ai_cofounder_analyze.py::analyze_geometric_bugs`.
- Backup pre-modifica: `/root/atlaspi-backup-cofounder-20260708-101139.sql`.

## Follow-up
- Estensione Medri Bahri: rivedere se il nucleo d'altopiano vada allargato verso nord
  (Bogos/Keren) alla luce di fonti specifiche; per ora conservativo e low-confidence.
- Coda dedup shared-polygon: valutare se altri stati-successori moderni (es. catene
  novecentesche) richiedano lo stesso trattamento allowlist.
