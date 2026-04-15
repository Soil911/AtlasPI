# Changelog AtlasPI

Tutte le modifiche rilevanti del progetto devono essere documentate qui.

## [v6.8.0] - 2026-04-15

**Tema**: *Ancient events gap + Asian dynasty chains* — colmato il buco
pre-500 CE (29 → 53 eventi, +24 nuovi) e aggiunte due catene dinastiche
asiatiche (Giappone 7-link Nara→Meiji, India classica 5-link
Shishunaga→Kanva). Catene 9 → 11, eventi 211 → 235. Test 442 → 486 (+44).

### Nuovi eventi (24) — `data/events/batch_09_ancient_expansion.json`

Eventi scelti per rappresentazione geografica/cronologica dove la copertura
esistente era povera: Vicino Oriente antico (Assyria, Babilonia, Giuda,
Persia achemenide), Grecia classica (Parthenon, processo a Socrate),
Ellenismo (Gaugamela, morte di Alessandro), Maurya (conversione di Aśoka),
Cina (battaglia di Gaixia e fondazione Han), Roma tardo-repubblicana
(assassinio Cesare), Roma imperiale (Teutoburgo, crocifissione di Yeshua
di Nazareth, rivolta di Bar Kokhba, Editti di Milano e Tessalonica,
fondazione di Costantinopoli, Adrianopoli, Campi Catalaunici, deposizione
di Romolo Augusto).

| Anno | Tipo                  | Evento                                       |
|-----:|-----------------------|----------------------------------------------|
| -722 | DEPORTATION           | גלות עשרת השבטים (Assyrian deportation of Israel) |
| -689 | MASSACRE              | Sennacherib's sack of Babylon                |
| -612 | CONQUEST              | Fall of Nineveh                              |
| -586 | DEPORTATION           | חורבן בית ראשון (Babylonian captivity)       |
| -539 | CONQUEST              | 𐎤𐎢𐎽𐎢𐏁 (Cyrus captures Babylon)              |
| -525 | CONQUEST              | Cambyses conquers Egypt                      |
| -447 | TECHNOLOGICAL_EVENT   | Parthenon begun                              |
| -399 | INTELLECTUAL_EVENT    | Θάνατος Σωκράτους                            |
| -331 | BATTLE                | Μάχη τῶν Γαυγαμήλων                          |
| -323 | DEATH_OF_RULER        | Death of Alexander / Wars of Diadochi        |
| -260 | RELIGIOUS_EVENT       | अशोक का धर्म-परिवर्तन (Aśoka adopts dharma)  |
| -218 | CONQUEST              | Hannibal trans Alpes                         |
| -202 | BATTLE                | 垓下之戰 (Gaixia, founding of Han)           |
| -44  | DEATH_OF_RULER        | Caedes C. Iulii Caesaris                     |
|   9  | BATTLE                | Clades Variana (Teutoburg Forest)            |
|  33  | RELIGIOUS_EVENT       | צליבת ישוע הנצרי (Crucifixion)               |
| 132  | REBELLION             | מרד בר כוכבא (Bar Kokhba revolt)             |
| 313  | RELIGIOUS_EVENT       | Edictum Mediolanense                         |
| 330  | FOUNDING_STATE        | Νέα Ῥώμη / Κωνσταντινούπολις                 |
| 378  | BATTLE                | Μάχη τῆς Ἀδριανουπόλεως                      |
| 380  | RELIGIOUS_EVENT       | Edictum Thessalonicense 'Cunctos populos'    |
| 395  | DISSOLUTION_STATE     | Divisio Imperii (permanent East/West split)  |
| 451  | BATTLE                | Bellum Campi Catalaunici                     |
| 476  | DISSOLUTION_STATE     | Depositio Romuli Augustuli                   |

Ogni evento ha: ≥1 fonte primaria + ≥1 accademica, `ethical_notes`
estese (>80 caratteri, in molti casi >500), `entity_links` risolti
verso entità DB reali (zero reference pendenti al seed).

### Nuove catene dinastiche (2) — `data/chains/batch_03_asia.json`

**Giappone (SUCCESSION, 7 link)**: 奈良時代 (710) → 平安時代 (794 REFORM)
→ 鎌倉幕府 (1185 REVOLUTION — Gempei War) → 室町幕府 (1336 REVOLUTION —
Ashikaga vs. Kemmu Restoration) → 安土桃山時代 (1568 UNIFICATION — Nobunaga
+ Hideyoshi, inclusi Imjin Korea e massacro Ikkō-ikki) → 徳川幕府 (1603
SUCCESSION — Sekigahara + Osaka + Shimabara) → 大日本帝國 (1868 REVOLUTION
— Meiji come REVOLUTION e non RESTORATION, con Boshin, Ainu, Ryūkyū).

**India classica (DYNASTY, 5 link)**: शिशुनाग (-413) → नन्द (-345
REVOLUTION — Mahapadma śūdra usurper) → मौर्य साम्राज्य (-322 CONQUEST —
Chandragupta+Chanakya) → शुंग (-185 REVOLUTION — Pushyamitra regicide di
Brihadratha) → कण्व (-73 REVOLUTION — Vasudeva regicide di Devabhuti).
ETHICS: ogni transizione è regicidio o conquista — zero "succession"
pacifiche. La pace ashokiana è l'anomalia, non la norma.

### Test nuovi (44) — `tests/test_v680_content_expansion.py`

- **Events file structure** (8 test): existence, lista >=20, required
  keys parametrized (10 chiavi), enum validation, pre-500 CE gate,
  multi-region language coverage, sources obbligatori, ethical_notes
  obbligatori, confidence in [0,1].
- **Events DB-layer** (3 test): 24 inseriti, gap pre-500 chiuso
  (29 → 53+), spot-check su link Cesare→Roma e Cyrus→Giuda.
- **Chains file structure** (7 test): file esiste, 2 chain, required
  keys parametrized (8 chiavi), ChainType enum, TransitionType enum.
- **Japan chain** (3 test): 7 link, endpoints Nara/Meiji, Meiji è
  REVOLUTION (non RESTORATION) e ethical_notes menziona Boshin/Ainu/Ryūkyū.
- **India chain** (3 test): 5 link, Shunga è REVOLUTION violenta (non
  SUCCESSION), tutte le transizioni sono `is_violent=true`.
- **Chains DB-layer** (3 test): Japan 7 link, India 5 link, totale ≥11.
- **Meta** (10 test parametrized su keys + 7 enum coverage).

Totale test backend: **442 → 486** (+44).

### Dataset stats post-v6.8.0

| Layer                | Pre-v6.8.0 | Post-v6.8.0 | Δ     |
|---------------------|-----------:|------------:|------:|
| Eventi storici      | 211        | 235         | +24   |
| Catene dinastiche   | 9          | 11          | +2    |
| Chain links         | 56         | 68          | +12   |
| Eventi pre-500 CE   | 29         | 53          | +24   |
| Test backend        | 442        | 486         | +44   |

### Etica

Ogni evento nuovo porta ETHICS note esplicite su: inflazione delle
casualties antiche (Arriano/Diodoro), bias dei Roman sources sui Punici
(fonti cartaginesi perdute dopo -146), Herodotean polemica anti-Cambyses
smontata da Udjahorresnet, letture anti-giudaiche della crocifissione
ripudiate da Nostra Aetate 1965, Gibbon's "barbarians vs civilization"
frame criticato per Catalaunian Plains, Hadrian rename Iudaea→Syria
Palaestina come cancellazione politica, 476 come convenzione storiografica
e non evento vissuto come "caduta" dai contemporanei.

Per le catene: Meiji Restoration come REVOLUTION (non RESTORATION —
rottura costituzionale totale con colonizzazione Hokkaido/Ainu e
annessione Ryūkyū). Classical India dynastic trunk con tutte le
transizioni `is_violent=true` — nessuna successione pacifica.

### File aggiunti

- `data/events/batch_09_ancient_expansion.json` — 24 eventi
- `data/chains/batch_03_asia.json` — 2 catene, 12 link
- `tests/test_v680_content_expansion.py` — 44 test

---

## [v6.7.3] - 2026-04-15

**Tema**: *Boundary honesty, pass 3* — rifinitura di 4 polygon che erano
ancora oversized anche dopo il pass 2 una volta misurati con area geodesica
reale (non bounding-box). Batch minimalista: solo le entità con area reale
>2x il picco storico documentato. Test 426 → 442 (+16).

### Entità corrette (4)

| ID  | Entità                   | Post-v672 real area | Post-v673 real area | Picco storico atteso |
|-----|--------------------------|--------------------:|--------------------:|---------------------:|
| 604 | Kalmyk Khanate (labeled Mongolian Hajar) | 13.3 M km² | 981 k km²  | ~1 M km²  |
| 343 | هوتکیان (Hotaki dynasty) | 2.5 M km²           | 1.39 M km² | ~1.5 M km² |
| 350 | Βακτριανή (Bactria)      | 2.8 M km²           | 866 k km²  | ~1 M km²   |
| 330 | Казан ханлыгы (Kazan)    | 1.2 M km²           | 859 k km²  | ~700 k km² |

Nota: entità 604 ha `name_original` in scrittura mongola ma
`capital_name="Sarai-on-the-Volga"` con anni 1634-1771 — indice che è in
realtà il **Kalmyk Khanate**, non il Khazar Khaganate (650-969). Il
polygon aourednik codificava un'estensione steppica composita che non
corrispondeva al controllo effettivo kalmyk.

### Metodologia

L'audit v6.7.3 ha sostituito la stima bbox con area geodesica reale via
`shapely.geometry.shape` + `pyproj.Geod` su ellipsoide WGS84. Sorprendentemente:

- **Ming 4.2M km²** (bbox 10M) — in target (peak ~6.5M km²) ✓
- **Venezia 19k km²** (bbox 1.9M) — in target (peak ~40k) ✓
- **Uyghur Khaganate 3.8M km²** (bbox 9.3M) — in target (peak ~2.8M) ✓
- **Maurya 3.4M km²** (bbox 6.5M) — in target (peak ~5M) ✓
- **Former Qin 2.8M km²** (bbox 5.6M) — in target (peak ~3M) ✓

Solo i 4 sopra avevano area *reale* ancora oltre 2x il picco. Gli altri
13 candidati erano falsi positivi della metrica bbox.

### Nuovi moduli

- **`src/ingestion/fix_bad_boundaries_v673.py`** (~120 righe). Stessa
  struttura di v672 con 4 `EntityFix` entries e radius calibrati al
  1.2x del picco storico (conservativo — il polygon visibilmente più
  piccolo del picco è preferibile al polygon eccessivo).

### Test

- **`tests/test_v673_boundary_cleanup.py`** — 16 nuovi test:
  struttura FIXES_V673 (4 test), real-area in range via pyproj.Geod
  (4 test parametrizzati), ethical_notes presence (4 test),
  confidence capping (4 test).

Totale test backend: **426 → 442** (+16).

### Etica

Ogni entità porta `[v6.7.3]` nell'`ethical_notes` con la spiegazione:
"aourednik polygon codificava estensione nominale composita (o dinastia
successiva), >2x l'area effettiva storica. Sostituito con
name_seeded_boundary ancorato al capital, radius calibrato al 1.2-1.5x
del picco storico. Vedi ETHICS-006."

---

## [v6.7.2] - 2026-04-15

**Tema**: *Boundary honesty, pass 2* — seconda passata di fix mirati sulle
polygon sproporzionate rispetto all'estensione storica attesa. 11 entità
con polygon 10x-200x la dimensione reale sono state riportate a forme
`approximate_generated` ancorate al proprio capital, con raggio calibrato
per tipo di polity. Test 386 → 426 (+40). Nessun cambiamento di API.

### Entità corrette (11)

| ID  | Entità                        | Prima      | Dopo (bbox)   | Radius km |
|-----|-------------------------------|-----------:|--------------:|----------:|
| 282 | Κομμαγηνή (Commagene kingdom) | 20 M km²  | 33 k km²      | 70        |
| 227 | Misiones Guaraníes (confed.)  | 20 M km²  | 286 k km²     | 250       |
| 727 | Oceti Sakowin (Sioux)         | 232 M km² | 2.9 M km²     | 700       |
| 705 | Lanfang Gongheguo             | 9.5 M km² | 90 k km²      | 125       |
| 454 | 南詔 (Nanzhao kingdom)          | 7.8 M km² | 716 k km²     | 400       |
| 575 | Principatus Transsilvaniae    | 25 M km²  | 147 k km²     | 140       |
| 679 | Polatskaye Knyastva           | 1.5 M km² | 250 k km²     | 180       |
| 651 | Duché de Normandie            | 1.5 M km² | 78 k km²      | 100       |
| 566 | Dugelezh Breizh (Brittany)    | 1.3 M km² | 60 k km²      | 100       |
| 427 | Suomen suuriruhtinaskunta     | 1.4 M km² | 660 k km²     | 350       |
| 653 | Великое княжество Литовское   | 3 M km²   | 1.9 M km²     | 500       |

I valori "Prima" sono bounding-box km² da polygon effettivi aourednik/NE;
i "Dopo" sono bbox delle forme `name_seeded_boundary` a 13 vertici
generate dal capital. Non sono perfetti (il generatore produce blob
tondeggianti anziché contorni reali), ma sono **evidentemente approssimati**
e capped a `confidence_score ≤ 0.4` (ETHICS-004).

### Perché questi 11

L'audit rigoroso v6.7.2 ha incrociato due metriche sulle 661 entità
`confirmed` con polygon e capital:

1. **Capital displacement > 500 km dal centroid del polygon**: 108 match.
   Dopo aver filtrato i falsi positivi legittimi (Fiji antimeridian, USSR/
   Russia/USA/Brazil giganti, Umayyad/Mongol/Timurid/Danish-Norway
   storicamente immensi) restano 9 mismatch reali (Commagene, Misiones,
   Oceti Sakowin, Lanfang, Nanzhao, Normandy, Brittany, Finland, GDL).
2. **Area > 1M km² per city/duchy/principality**: 6 match, tutti o duchies
   francesi (Normandy, Brittany) o principati dell'est europeo
   (Transylvania, Polatsk, GDL) o Finland GD.

Gli 11 fix intersecano/sommano entrambe le liste. La causa più frequente:
polygon aourednik matchato per token-overlap a un'entità con nome simile
ma estensione molto più grande (Polatsk → all-Rus scope; Normandy →
Plantagenet empire scope; Transylvania → continental Habsburg/Ottoman scope).

### Nuovi moduli

- **`src/ingestion/fix_bad_boundaries_v672.py`** (~180 righe). Riusa
  l'engine di v6.7.1 (`run_fixes`) via monkey-swap della `FIXES`
  globale, aggiungendo una lista `FIXES_V672` con 11 `EntityFix`
  entry. Ogni entry porta un `append_note` che termina con
  `[v6.7.2] ... Vedi ETHICS-006`.

### Test

- **`tests/test_v672_boundary_cleanup.py`** — 40 nuovi test:
  - struttura FIXES_V672 (5 test): count=11, regenerate_geometry=True
    ovunque, note-annotated ovunque, no-duplicate-ids, no-overlap con
    FIXES_V671
  - idempotency (1 test): re-run è no-op
  - classi per-entity (8 test): Commagene/OcetiSakowin/Transylvania/
    Normandy verificano `boundary_source=approximate_generated` e range
    area bbox
  - capital anchoring (4 test parametrizzati): centroid entro
    `max_offset_km` dal capital per ognuno dei 4 campioni
  - confidence capping (11 test parametrizzati): ogni entità ha
    `confidence_score ≤ 0.4`
  - ethical_notes presence (11 test parametrizzati): ogni entità ha
    `[v6.7.2]` nel campo `ethical_notes`

Totale test backend: **386 → 426** (+40), tutti passing.

### Etica

Stesso pattern di v6.7.1: nessuna cancellazione di dato storico, solo
sostituzione di polygon sbagliato con polygon generato deterministicamente
dal capital. Ogni entità fixata ha ora nell'`ethical_notes` una riga
`[v6.7.2] boundary precedente era un mismatch geografico (polygon >10x
l'estensione storica attesa). Sostituito con name_seeded_boundary ancorato
alla capital. Vedi ETHICS-006.` — così chiunque interroghi l'API sa che
il poligono è una stima deliberata, non un confine rilevato.

---

## [v6.7.1] - 2026-04-15

**Tema**: *Boundary honesty* — patch release che elimina i confini condivisi
falsi e i placeholder rettangolari, e riconduce ogni entità senza dato geografico
affidabile a un polygon onesto generato dal proprio capital con raggio adeguato
al tipo. Nessun cambiamento di API. Test saliti da 371 → 386.

### Numeri

- **-61 entità con boundary condivisi falsi** — distribuiti su 17 cluster di
  omonimia (Holy Roman Empire × 14 drop, Kingdom of David and Solomon × 6,
  Greek city-states × 5, Byzantine × 5, Fatimid × 5, "minor states" × 4,
  …). Il dato del cluster viene preservato solo sulla variante con il nome
  più simile al label del poligono aourednik (similarity score rapidfuzz
  token-set ≥ 0.80); le altre vengono regenerate onestamente col raggio
  capital-based e bollate `approximate_generated`.
- **-5 placeholder rettangolari** — i 5 bounding-box visibili (entità
  `524 525 528 530 531`) sono stati annotati in `ethical_notes` con spiega
  esplicita ("polygon approssimato, NON confine storico") e retrocessi a
  `status: uncertain` con `confidence_score` capped a 0.4 (ETHICS-004).
- **+6 entità con polygon corretto** — Pechenegs (id 325) e Nogai Horde
  (id 338) hanno ora capital backfillato (rispettivamente 47.5,34.5 Ukrainian
  steppe e 47.5,51.5 Lower Volga) e boundary a raggio steppe (700 km).
  Istanbul (id 3) e Igbo-Ukwu (id 562) scalate a raggio urbano (20 km).
  Cherokee (id 218) e Seminole (id 545) riportate a raggio native-confederation
  (250 km) dopo aver eliminato i polygon Natural Earth che rappresentavano
  gli intero territorio moderno US/Mexico.
- **+15 test backend** (totale 386/386 passing): 15 nuovi in
  `test_v671_boundary_cleanup.py` coprono cluster-analysis idempotency,
  strip_generic_tokens, rapidfuzz scoring, FIXES coverage, Pechenegs
  capital backfill, Istanbul small polygon, placeholder ethical notes,
  dry-run no-op. Una fixture (`stale_db` in test_sync_boundaries) ridefinita
  per selezionare entità con ≥50 vertici da fonti trusted anziché prime 3
  by id.
- **atlaspi-mcp 0.3.0 → PyPI**: pubblicato su https://pypi.org/project/atlaspi-mcp/0.3.0/
  (`pip install atlaspi-mcp`).

### Perché era necessario

L'audit `docs/boundary_audit_2026_04_15.md` aveva rivelato:

- **166 entità con GeoJSON binariamente identico** ad almeno un'altra entità
  (= stessa fingerprint hash) — questi cluster rappresentano successioni
  dinastiche diverse che condividevano lo stesso polygon aourednik perché il
  matcher di ingestione faceva token-overlap su nomi generici come "Empire",
  "Kingdom", "Dynasty". Risultato: il Sacro Romano Impero e 13 sue incarnazioni
  discontinue mostravano lo stesso confine (drop: 13).
- **9 entità Natural Earth con centroide displaced >2000 km** dalla capital —
  indice che il polygon NE era stato matchato a un'entità storica sbagliata.
  Tre reali (Pechenegs, Cherokee, Seminole) corrette; le altre 6 (USSR,
  Russia imperial, USA, Brazil, Fiji) sono legittimamente giganti o soffrono
  di antimeridian artifact — lasciate volutamente intatte.
- **5 rettangoli placeholder** rimasti da import legacy.
- **2 entità con `boundary_geojson: NULL`** — Pechenegs e Nogai Horde,
  appunto.

### Nuovi moduli

- **`src/ingestion/cleanup_shared_polygons.py`** (~300 righe). Entry point
  `run_cleanup(dry_run=False, json_only=False, db_only=False)`. Stripa
  `GENERIC_TOKENS` ({empire, kingdom, dynasty, sultanate, caliphate,
  khanate, principality, republic, duchy, earldom, confederacy, …})
  prima di fare rapidfuzz `token_set_ratio`. Un cluster ≥3 entità con stessa
  boundary fingerprint viene valutato contro il label del poligono aourednik:
  l'entità con score ≥ 0.80 viene tenuta, le altre regenerate. Se il cluster
  non ha label chiaro (happens for CITIES vs STATES with same SHAPE), solo
  l'entità col capital più centrato nel polygon viene tenuta.
- **`src/ingestion/fix_bad_boundaries_v671.py`** (~350 righe). Dataclass
  `EntityFix(entity_id, reason, regenerate_with_radius_km,
  demote_status_to, append_note, clear_aourednik, clear_ne, keep_geometry,
  backfill_capital_lat, backfill_capital_lon, backfill_capital_name)`.
  FIXES list con 11 entry. Costanti `CITY_RADIUS_KM = 20`,
  `STEPPE_RADIUS_KM = 700`, `NATIVE_CONFEDERATION_RADIUS_KM = 250`.
  Applica sia al DB SQLAlchemy sia ai JSON in `data/entities/` per
  mantenere idempotenza al prossimo reseed.

### Etica

Tutti i drop di shared-polygon e tutte le sostituzioni di placeholder
lasciano una traccia in `ethical_notes` dell'entità risultante, con
puntatore a ETHICS-004 (approximate_generated) o ETHICS-006 (displacement
correction). Nessun dato storico è stato **cancellato**: solo i poligoni
sbagliati sono stati sostituiti con poligoni generati deterministicamente
dal capital (hash-based `name_seeded_boundary`) che sono evidentemente
approssimati (8-32 vertici tondeggianti) e capped a
`confidence_score ≤ 0.4`.

### Note di rilascio PyPI

Il pacchetto `atlaspi-mcp` versione 0.3.0 (wheel + sdist) è ora disponibile
su PyPI. Il token di upload è stato usato una volta e revocato lato utente
subito dopo. `pip install atlaspi-mcp` installerà 23 tool MCP pronti a
puntare a qualsiasi istanza AtlasPI (default `https://atlaspi.cra-srl.com`).

---

## [v6.7.0] - 2026-04-15

**Tema**: *Agent-ready integration* — due nuovi endpoint pensati per LLM
agent workflow, estensione MCP a 23 tool, raddoppio delle rotte commerciali
(25 → 41), tre nuove catene dinastiche, e frontend unificato con trade-route
overlay, lista catene in sidebar, e timeline unificata per entità.

### Numeri

- **+2 endpoint REST**: `/v1/entities/{id}/timeline` (stream unificato
  events + territory_changes + chain_transitions ordinato cronologicamente)
  e `/v1/search/fuzzy` (ricerca approssimata cross-script via
  `difflib.SequenceMatcher`, stdlib, zero dipendenze aggiuntive).
- **+3 tool MCP** (totale 23): `full_timeline_for_entity`, `fuzzy_search`,
  `nearest_historical_city` (composite haversine client-side).
- **+16 rotte commerciali** (totale 41): batch Hanseatic/Baltic (8 rotte
  bilaterali: London↔Lübeck, Brügge↔Novgorod, Bergen↔Lynn, ecc.) +
  batch Indian Ocean Maritime (8 rotte: Calicut↔Muscat, Carreira da Índia,
  VOC Retourvloot, Muscat↔Zanzibar slave and clove route, ecc.).
- **+3 catene dinastiche** (totale 9): Byzantine→Ottoman (SUCCESSION
  CONQUEST 1453), French monarchy→Republic (SUCCESSION 4-link),
  Iranian Safavid→Qajar→Pahlavi→IRI (SUCCESSION 4-link).
- **+16 test backend** (totale 371): 7 per timeline + 9 per fuzzy search.
- **+3 test MCP** (totale 20 pass + 1 skip integration): handler mock
  transport per i tre nuovi tool.

### /v1/entities/{id}/timeline — stream unificato

Risponde a una richiesta comune degli agenti AI: "raccontami TUTTA la storia
di questa entità". Invece di concatenare 4 call (events/territory_changes/
predecessors/successors), l'endpoint restituisce un unico stream ordinato:

```json
{
  "entity_id": 1,
  "entity_name": "Imperium Romanum",
  "entity_type": "empire",
  "year_start": -27, "year_end": 476,
  "counts": {"events": 10, "territory_changes": 3, "chain_transitions": 1, "total": 14},
  "timeline": [
    {"kind": "event", "year": -27, "name": "Foundation of Roman Empire", ...},
    {"kind": "territory_change", "year": 117, "description": "Trajan's conquests", ...},
    {"kind": "chain_transition", "year": 476, "transition_type": "DISSOLUTION", ...}
  ]
}
```

Parametro `include_entity_links=true` (default) include ruolo dell'entità
in ogni evento (MAIN_ACTOR/VICTIM/...). Ordinamento stabile: stesso anno →
event prima di territory_change prima di chain_transition.

### /v1/search/fuzzy — cross-script approximate matching

Usa `difflib.SequenceMatcher` (stdlib Python, zero deps) su char-level
Unicode, quindi funziona cross-script: `q=safavid` trova `دولت صفویه`
(0.817), `q=Constantinople` trova `Κωνσταντινούπολις`, e query in cirillico
risolvono entità latine. Scoring:

- base: `SequenceMatcher.ratio()` fra query lowercased e target
- +0.10 bonus se match su `name_original` (vs variant)
- +0.15 bonus se prefix match (query inizia il nome)
- +0.08 bonus se substring exact match

Parametri: `q` (1-200 chars, obbligatorio), `limit` (1-50, default 20),
`min_score` (0.0-1.0, default 0.4). Risposta ordinata per score decrescente.

### MCP v0.3.0 — 23 tools

Pacchetto `atlaspi-mcp` bumpato da 0.2.0 a 0.3.0. Tre nuovi tools:

| Tool | Function |
|---|---|
| `full_timeline_for_entity` | Wrapper del nuovo endpoint unified timeline |
| `fuzzy_search` | Wrapper del nuovo endpoint fuzzy search |
| `nearest_historical_city` | Composite client-side: `list_cities(year=...)` + haversine sort per distanza |

Per `nearest_historical_city` la composizione è client-side perché AtlasPI
non espone `/v1/cities/nearest` — il tool scarica fino a 500 candidati
filtrati per anno/tipo, calcola la distanza haversine in Python, ordina
crescente e ritorna i primi `limit`.

### Frontend — v6.7 polish

- **Trade routes overlay** (ETHICS-010): nuovo toggle "Mostra rotte
  commerciali" in sidebar. Le rotte attive nell'anno selezionato vengono
  renderizzate sulla mappa come polyline colorate per tipo (marittima=blu,
  terrestre=marrone, fluviale=azzurro, mista=grigia). Le rotte con
  `involves_slavery: true` hanno un'outline rossa sotto la linea colorata
  e tooltip esplicativo ("Rotta associata alla tratta schiavistica — vedi
  ETHICS-010"), testo deliberatamente fattuale senza sensazionalismo.
  Legenda inline sotto il toggle.
- **Sidebar catene dinastiche**: nuovo `<details>` collapsabile fra
  filtri e stats-bar. Mostra tutte le catene con badge del chain_type
  (DYNASTY/SUCCESSION/COLONIAL/IDEOLOGICAL/...), numero di link, regione.
  Catene IDEOLOGICAL hanno bordo arancione + badge ETHICS-003
  ("continuità self-proclaimed"). Click su catena apre detail panel con
  timeline verticale numerata e link cliccabili verso le entità.
- **Detail panel: tab Timeline unificata**: il detail panel delle entità
  ha ora due tab ("Panoramica" / "Timeline unificata"). Il secondo tab
  chiama l'endpoint `/v1/entities/{id}/timeline` e renderizza le voci
  come timeline verticale con marker colorati per kind (viola=event,
  verde=territory, arancio=chain) e tooltip descrittivi.
- Playback storico + year slider + year presets + reset tutti wired per
  ri-renderizzare le rotte se il toggle è attivo.

### Nuove catene dinastiche

- **Byzantine → Ottoman** (SUCCESSION, 1 link CONQUEST 1453):
  presa di Costantinopoli da parte di Mehmed II. Transizione violenta
  documentata con fonti Kritovoulos, Runciman 1965, Ágoston 2010.
- **French monarchy → Republic** (SUCCESSION, 4 link): Ancien Régime →
  République française (1792 REVOLUTION) → Restauration borbonica non
  modellata (mancano entità canoniche) → Seconde République (1848
  REVOLUTION) → Troisième République (1870 DISSOLUTION del Second
  Empire). Catena accorciata rispetto alla richiesta iniziale perché
  Empire Napoléonien, Restauration, Monarchie de Juillet, Second Empire
  non sono entità nel DB — documentato in `ethical_notes` anziché
  inventato.
- **Iranian Safavid → Qajar → Pahlavi → IRI** (SUCCESSION, 3 link):
  Safavid → Qajar (1796 REVOLUTION, omesso Afsharid/Zand perché non in DB)
  → Pahlavi (1925 CONQUEST di Reza Khan) → Repubblica Islamica (1979
  REVOLUTION di Khomeini). `ethical_notes` documenta la repressione
  post-rivoluzionaria.

### Nuove rotte commerciali

- **Batch 02 Hanseatic/Baltic** (8 rotte, 1150–1720): specific bilateral
  spokes che complementano l'aggregato "Hanseatic League Network" di
  batch_01: London↔Lübeck (Steelyard), Brügge↔Novgorod (Peterhof
  kontor), Bergen↔Lynn/Boston (stockfish trade), Lübeck↔Reval
  (tolmaching privileges), Visby↔Riga (Gotlandic chapter), Oostvaart
  (Gdańsk↔Amsterdam grain), Hamburg↔Oslo, Stockholm↔Lübeck.
- **Batch 03 Indian Ocean Maritime** (8 rotte, 600–1873): Calicut↔Muscat
  (pepper-horse trade), Swahili↔Gujarat monsoon (gold/ivory/beads, con
  flag `involves_slavery: true`), Quanzhou↔Aden (Song-Fatimid), Malacca↔
  Ming (tribute missions), Carreira da Índia portoghese (Lisboa↔Goa
  1498–1833), VOC Retourvloot (Batavia↔Amsterdam 1619–1799), **Muscat↔
  Zanzibar Omani Slave and Clove Route** (1698–1873) con ETHICS-010
  completo: scale (1.0–1.6M trafficked per Sheriff/Lovejoy), perpetrators
  nominati (Al-Busaid, Said bin Sultan, Barghash, Tippu Tip), caravan-
  mortality multiplier (4:1), descendant communities (Siddis, Habshis),
  critica esplicita del silenzio commemorativo omanita contemporaneo.

### Breaking / compatibility

- Nessun breaking change. Endpoint esistenti invariati. Schema DB
  invariato — i nuovi endpoint leggono su tabelle esistenti.
- `atlaspi-mcp` bumpa minor (0.2 → 0.3); chi ha pinnato a `~=0.2.0`
  continua a funzionare (tool set v0.2 immutato), chi vuole i nuovi
  tool deve aggiornare a `>=0.3.0`.

### File principali toccati

- `src/api/routes/relations.py` (+timeline endpoint)
- `src/api/routes/entities.py` (+fuzzy endpoint)
- `static/index.html`, `static/app.js`, `static/style.css` (frontend)
- `static/landing/index.html` (hero-tag + foot-version)
- `mcp-server/src/atlaspi_mcp/{__init__,client,tools}.py` (v0.3.0)
- `mcp-server/tests/test_tools.py` (+3 handler tests)
- `mcp-server/README.md` (22 → 23 tools)
- `data/chains/batch_02_more_chains.json` (nuovo)
- `data/routes/batch_02_hanseatic_baltic.json` (nuovo)
- `data/routes/batch_03_indian_ocean_maritime.json` (nuovo)
- `tests/test_v670_timeline_fuzzy.py` (+16 test)

## [v6.6.0] - 2026-04-15

**Tema**: Espansione degli eventi storici da 106 → 211 con quattro batch
tematici che coprono vuoti geografici/cronologici: Africa (tratta
atlantica, colonizzazione, apartheid, Rwanda, Congo), Asia-Pacifico
(partizione dell'India, Guerra civile cinese, Corea, Vietnam, genocidio
cambogiano, Bangladesh 1971, Tienanmen, Xinjiang), Americhe (conquista
dell'Impero azteco e inca, resistenza indigena, Rivoluzione haitiana,
Guerra della Triplice Alleanza, Trail of Tears, genocidio della
California, dittature del Cono Sud, Piano Cóndor), e lungo Novecento
globale (genocidio armeno/assiro/pontico, Holodomor, Shoah, Nakba,
dissoluzioni URSS e Jugoslavia, Srebrenica, Halabja, guerre del Golfo,
Primavera Araba, invasione russa dell'Ucraina). Rispetto integrale di
ETHICS-007 (niente eufemismi) ed ETHICS-008 (`known_silence=true` su
eventi sistematicamente negati).

### Numeri

- **105 nuovi eventi storici** inseriti idempotentemente senza modificare
  i 106 preesistenti (dedup key `(name_original, year)`).
- **Totale eventi DB**: 211 (ordine di grandezza 2x).
- **Nessun riferimento `entity_links` irrisolto**: tutti i 105 eventi
  inseriti hanno legato i loro attori alle entità canoniche già nel DB
  (846 entità disponibili come ground truth).

### Batch aggiunti

- `data/events/batch_05_africa.json` — 26 eventi 1652–2003 (11 tipi,
  9 `known_silence`).
- `data/events/batch_06_asia_pacific.json` — 25 eventi 1904–2014
  (13 tipi, 12 `known_silence`).
- `data/events/batch_07_americas.json` — 26 eventi 1494–1976
  (9 tipi, 5 `known_silence`).
- `data/events/batch_08_modern.json` — 28 eventi 1914–2022
  (11 tipi, 10 `known_silence`).

### ETHICS-007 labels applicate esplicitamente

- **GENOCIDE** (8 eventi nuovi): genocidio assiro (Seyfo) 1914–1924,
  genocidio pontico 1914–1922, genocidio della California 1846–1873
  (Madley), genocidio Selk'nam 1884–1910, Triple Alliance Paraguay
  1864–1870, guerra di Bangladesh 1971, Darfur 2003+, campagna Anfal /
  Halabja 1988 (chemical weapons). Ognuno con `ethical_notes` che
  documentano la designazione legale, le controversie accademiche e
  le eventuali negazioni statali (Turchia, Cina, Pakistan, Russia).
- **COLONIAL_VIOLENCE**: Congo Free State 1885–1908, Maji Maji
  1905–1907, Italo-Etiopica 1935–1937 (uso di armi chimiche),
  sistema "donne di conforto" giapponese 1932–1945 (schiavismo
  sessuale sistemico), Xinjiang Uyghur 2017+ (`disputed` status
  perché il label legale GENOCIDE è contestato — entrambi i lati
  documentati come da ETHICS).
- **MASSACRE**: Nanjing già presente in batch_01, aggiunti Sand Creek
  1864, Sharpeville 1960, Soweto 1976, Jallianwala Bagh 1919, My Lai
  1968, Tokyo firebombing 1945, Srebrenica 1995, Katyn 1940, Sabra
  e Shatila 1982, Ghouta chemical attack 2013.
- **DEPORTATION**: Trail of Tears 1830–1838, scambio di popolazione
  greco-turco 1923, Nakba 1948, Mfecane 1815 (reclassed from
  MIGRATION), Partition of India 1947 (come evento di forced
  displacement distinto dalla partizione politica già in DB).

### ETHICS-008 `known_silence` (36 nuovi eventi flaggati)

Eventi con record sistematicamente silenziato/negato: Putumayo rubber
atrocities, genocidio dei Selk'nam, genocidio californiano,
Operation Condor, Congo Free State, Xhosa cattle-killing 1856,
Biafra famine 1967, Lumumba assassination 1961, Darfur, Armenian
genocide (Turkey denial), Uyghur detention, Holodomor, Bengal
famine 1943, Nanjing (Japanese denial — nota aggiunta), Tiananmen
1989, Great Leap Forward famine, comfort women system, My Lai
cover-up, Ghouta chemical attack (Russian denial), Katyn (Soviet
denial), ecc.

### Remap di compatibilità enum

Gli agenti generatori avevano prodotto alcune label non presenti
nell'enum `EventType` canonico. Remapping deterministico applicato
prima dell'ingest:

- `FOUNDATION_STATE` → `FOUNDING_STATE` (5 eventi) — Kolonie aan die
  Kaap, Asante, Proklamasi Indonesia, PRC, Timor-Leste 1999.
- `FOUNDATION_STATE` (Berliner Mauer 1961) → `OTHER` — non è una
  fondazione statale.
- `MIGRATION` → `DEPORTATION` (2 eventi) — Mfecane, Partition 1947
  (entrambi trattamenti di spostamento forzato).
- `SLAVE_TRADE` → `TREATY` (2 eventi) — Asiento 1713 e abolizione
  Zanzibar 1873 sono trattati politici.
- `SLAVE_TRADE` → `COLONIAL_VIOLENCE` — comfort women system
  giapponese (schiavismo sessuale sistemico).

### Ingest

- Pipeline invariata: `python -m src.ingestion.ingest_new_events`
  (idempotente, dedup `(name_original, year)`).
- Eseguito in produzione dopo il deploy: 105 inseriti, 106 saltati,
  0 link irrisolti.

### Test

- 355 test verdi (suite stabile — nessun test nuovo necessario:
  la pipeline di ingest ha già coverage e il nuovo contenuto è
  solo dataset additivo).

### Deploy

```bash
git push origin main
cra-deploy atlaspi   # o ssh + docker compose build/up
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "docker exec cra-atlaspi python -m src.ingestion.ingest_new_events"
curl https://atlaspi.cra-srl.com/health  # expect 6.6.0
curl https://atlaspi.cra-srl.com/v1/events | jq .total  # expect 211
```

## [v6.5.0] - 2026-04-15

**Tema**: DynastyChain / SuccessionChain layer + MCP tools v0.2.0. Le
catene successorie diventano un layer esplicito con `transition_type`
obbligatorio per ogni transizione — conquiste, rivoluzioni e riforme non
vengono più appiattite in "successioni" generiche (ETHICS-002). Include
un tipo `IDEOLOGICAL` con avvertimento forte (ETHICS-003: continuità
self-proclaimed ≠ legittimità storica — es. Sacrum Imperium Romanum →
Deutsches Kaiserreich → Deutsches Reich). Il server MCP passa a 0.2.0
con 11 nuovi tool che espongono eventi, città, rotte, catene e un diff
macro-storico `what_changed_between(year1, year2)`.

### Modelli nuovi

- **`DynastyChain`** — catena successoria che lega più entità geopolitiche
  con `chain_type` (ChainType enum: DYNASTY, SUCCESSION, RESTORATION,
  COLONIAL, IDEOLOGICAL, OTHER), region opzionale, description,
  confidence_score, status, ethical_notes (obbligatorie per IDEOLOGICAL),
  sources (JSON array di academic citations).
- **`ChainLink`** — junction chain ↔ geo_entity con sequence_order (0 =
  prima entità, senza predecessore), `transition_year`, `transition_type`
  (TransitionType enum: CONQUEST, REVOLUTION, REFORM, SUCCESSION,
  RESTORATION, DECOLONIZATION, PARTITION, UNIFICATION, DISSOLUTION,
  ANNEXATION, OTHER), `is_violent` Bool, description e ethical_notes
  specifiche della singola transizione.

### Migration Alembic 006

- Crea `dynasty_chains` + `chain_links` con indici su name, chain_type,
  region, status e sui pattern di query di junction (chain_id,
  entity_id, sequence_order, transition_type).
- Check constraint su `confidence_score ∈ [0.0, 1.0]`.
- Additivo: niente impatto su tabelle esistenti.

### Endpoint nuovi

- `GET /v1/chains` — lista paginata con filtri `chain_type`, `region`
  (ilike substring), `year` (almeno un'entità della catena attiva),
  `status`, limit/offset.
- `GET /v1/chains/{id}` — dettaglio con tutti i link in ordine
  cronologico, transition_type esplicito su ogni link, ethical_notes
  specifiche della transizione.
- `GET /v1/chains/types` — enumera ChainType + TransitionType con
  descrizioni human-readable (es. "CONQUEST: Conquista militare violenta.
  ETHICS-002: NON usare 'succession' generico.").
- `GET /v1/entities/{id}/predecessors` — catene in cui l'entità ha un
  predecessore, ritorna il predecessore immediato + transition metadata.
- `GET /v1/entities/{id}/successors` — simmetrico: successore immediato
  di un'entità attraverso le catene di cui fa parte.

### Seed iniziale (data/chains/batch_01_major_chains.json)

6 catene-archetipo che esercitano ogni ChainType:

1. **Roman Power Center** (SUCCESSION): Imperium Romanum → Imperium
   Romaniae (330 REFORM). La Republic Roman non è ancora una entità
   separata nel DB — discussa solo nella description.
2. **Chinese Imperial Dynasties** (DYNASTY): 漢朝 → 唐朝 → 宋朝 → 元朝 →
   明朝 → 大清帝國. Ogni transizione etichettata CONQUEST (618, 1271, 1644)
   vs REVOLUTION (960, 1368), con ethical_notes sulle vittime (conquista
   mongola, Yangzhou 1645).
3. **Tawantinsuyu → Virreinato del Perú** (COLONIAL, CONQUEST 1542):
   ethical_notes esplicite su crollo demografico 50-90%, Atahualpa 1533,
   Túpac Amaru I 1572.
4. **Sacrum Imperium Romanum → Deutsches Kaiserreich → Deutsches Reich**
   (IDEOLOGICAL): avvertimento esplicito che la self-proclaimed continuità
   è stata strumentalizzata per il genocidio — inclusa per rendere
   visibile l'appropriazione, NON per legittimare la pretesa.
5. **Ottoman → Republic of Turkey** (SUCCESSION): foundational era
   include genocidio armeno/greco/assiro 1915-23 (~1.5M+ morti) e
   negazione turca contemporanea (ETHICS-008).
6. **Российская Империя → СССР → Российская Федерация** (RESTORATION):
   continuità contesa; Soviet esplicitamente rifiutava il lascito
   zarista ideologicamente mentre ne ereditava territorio e posture.

### Ingestion idempotente

- `src/ingestion/ingest_chains.py` — dedupkey = `name`; risolve
  `entity_name` → `entity_id` via `GeoEntity.name_original`; ETHICS-002
  soft-warn su link non-iniziali senza `transition_type`; ETHICS-003
  soft-warn su chain_type=IDEOLOGICAL senza `ethical_notes`; link con
  entity non risolti vengono skippati ma la catena parziale viene
  inserita comunque (warning loggato).

### MCP server v0.2.0 — 11 nuovi tool

Nuovo set che espone i layer v6.3–v6.5 agli agenti AI:

- `search_events`, `get_event`, `events_for_entity` (ETHICS-007/008)
- `search_cities`, `get_city` (ETHICS-009)
- `search_routes`, `get_route` (ETHICS-010: `involves_slavery` surface)
- `search_chains`, `get_chain`, `entity_predecessors`, `entity_successors`
  (ETHICS-002/003)
- `what_changed_between(year1, year2, type?, continent?)` — composizione
  client-side di due snapshot che ritorna {appeared, disappeared,
  persisted_ids} per diff macro-storici efficienti.

Totale tool esposti: 8 (v0.1) + 11 (v0.2) = **19**. Descrizioni
guidate agli ETHICS-* rilevanti. Test MCP: 17 passing + 1 integration
opt-in.

### Test suite

- 15 nuovi test in `tests/test_v650_chains.py` (fixture function-scoped
  `seeded_chain` con 3 entità TEST_* + chain "TEST_Roman_Power_Center"),
  coprono list+filtri, detail con link ordinati, predecessori,
  successori, 404, OpenAPI coverage, ETHICS-002 trasparenza.
- Suite totale: 340 → **355 passing**.

### Deploy

```bash
# push + deploy
git push origin main
cra-deploy atlaspi

# ingestione chain su produzione (dopo che la migration 006 è applicata)
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "cd /opt/cra && docker compose exec atlaspi python -m src.ingestion.ingest_chains"

# pubblica MCP 0.2.0 su PyPI (opzionale, repo separato)
cd mcp-server && python -m build && twine upload dist/*
```

## [v6.4.0] - 2026-04-15

**Tema**: HistoricalCity + TradeRoute layer. Le città storiche e le rotte
commerciali diventano oggetti di prima classe — separati dalle entità
politiche perché hanno una vita propria (Costantinopoli sopravvive a
4+ imperi). 110 città + 25 rotte commerciali, governance etica esplicita
su rinominazioni coloniali (ETHICS-009) e tratta degli esseri umani
(ETHICS-010).

### Modelli nuovi

- **`HistoricalCity`** — centri urbani storici con name_original (lingua
  locale come dato primario), coordinate, founded_year/abandoned_year,
  city_type (CityType enum: CAPITAL, TRADE_HUB, RELIGIOUS_CENTER, FORTRESS,
  PORT, ACADEMIC_CENTER, INDUSTRIAL_CENTER, MULTI_PURPOSE, OTHER),
  population_peak, FK opzionale a `geo_entities`, ethical_notes, sources
  e name_variants (JSON array di {name, lang, period_start, period_end,
  context}).
- **`TradeRoute`** — rotte commerciali con name_original, route_type
  (RouteType enum: LAND, SEA, RIVER, CARAVAN, MIXED), start/end_year,
  geometry_geojson (LineString o MultiLineString), commodities (JSON
  array), `involves_slavery` Boolean denormalizzato per filtro esplicito
  ETHICS-010, ethical_notes obbligatorie per rotte schiaviste con scala +
  main_actors + Middle Passage mortality.
- **`RouteCityLink`** — junction m:n route ↔ city con sequence_order +
  is_terminal per rappresentare i waypoint nell'ordine giusto.

### Migration Alembic 005

- Crea `historical_cities`, `trade_routes`, `route_city_links` con tutti
  gli indici, check constraint, FK.
- Su PostgreSQL aggiunge due indici GiST funzionali analoghi a 004:
  - `ix_historical_cities_point_geog` su `ST_MakePoint(longitude, latitude)::geography`
  - `ix_trade_routes_geom` su `ST_GeomFromGeoJSON(geometry_geojson)` (where not null)
- Su SQLite skippa la sezione PostGIS — niente errori in dev.

### Endpoint nuovi

- `GET /v1/cities` — lista paginata con filtri `year` (active-in-year),
  `city_type`, `entity_id`, `bbox` (min_lon,min_lat,max_lon,max_lat con
  validazione 422), `status`. Bbox usa BETWEEN sui punti (le città hanno
  sempre coordinate).
- `GET /v1/cities/{id}` — dettaglio con name_variants completi (ETHICS-009),
  sources academic, link all'entità di appartenenza.
- `GET /v1/cities/types` — enumera CityType con descrizione human-readable.
- `GET /v1/routes` — lista paginata con filtri `year`, `route_type`,
  `involves_slavery` (ETHICS-010 esplicito), `status`.
- `GET /v1/routes/{id}` — dettaglio completo con geometry GeoJSON,
  commodities, waypoints ordinati (con city_name + lat/lon).
- `GET /v1/routes/types` — enumera RouteType.

### Dati seedati (110 città + 25 rotte)

Le 110 città sono distribuite su tre batch tematici:
- **`batch_01_mediterranean_mena.json`** (35 città) — Mediterraneo & MENA:
  Roma, Atene, Konstantinoupolis, Alessandria, Cartagine, Damasco,
  Baghdad, Cordova, Granada, Venezia, ecc.
- **`batch_02_asia.json`** (35 città) — Asia: Beijing/Khanbaliq/Peking,
  Chang'an, Nanjing (con nota sul massacro 1937), Edo/Tokyo (con nota sul
  massacro coreano 1923), Hanyang/Seoul (con nota Keijō 1910), Pataliputra,
  Vijayanagara, Angkor, Bagan, Samarqand, Bukhārā, Persepolis, ecc.
- **`batch_03_americas_africa_europe.json`** (40 città) — Americhe (12),
  Africa subsahariana (14), Europa nord-orientale (14): Mēxihco-Tenōchtitlan
  (con nota distruzione Cortés 1521), Qusqu, Caral, Machu Picchu,
  Dzimba-dza-mabwe (Great Zimbabwe), Tumbutu (Timbuctù), Ẹ̀dó (Benin City,
  con nota saccheggio 1897), Kꙑѥвъ (Kyiv), Twangste (Königsberg/Kaliningrad,
  con nota deportazione tedeschi 1945), Lwów/Lviv, Gdańsk/Danzig, ecc.

Le 25 rotte commerciali in `batch_01_major_routes.json` coprono:
- Continentali (6): Silk Road, Royal Persian Road, Tea Horse Road, ecc.
- Trans-sahariane (3): Gold & Salt, Bornu-Fezzan slave route, Trans-Saharan
- Indian Ocean (4): Maritime Silk Road, Spice Route, Swahili Coast, slave route
- Atlantiche (3): Trans-Atlantic Slave Trade, Triangle Trade, Cape Route
- Asia-Pacific (3) + Europa (4) + River (2)

### ETHICS-009 — Rinominazioni & cancellazione culturale

Ogni rinominazione coloniale/imperiale è documentata in `name_variants`
con `period_start`/`period_end` + `context`. Esempi:
- Konstantinoupolis → Istanbul (1453, "Ottoman name imposed after conquest")
- Calcutta → Kolkata (2001, decolonizzazione linguistica)
- Edo → Tokyo (1868, riforma Meiji)
- Königsberg → Kaliningrad (1946, deportazione popolazione tedesca)
- Mexico City sopra Tenochtitlan (1521, Templo Mayor demolito + Catedral
  Metropolitana costruita sopra come atto di cancellazione)
- Lwów (PL) → Lvov (RU) → Lviv (UA), con popolazione ebraica sterminata 1941-44
- Danzig (DE) → Gdańsk (PL) 1945, espulsione tedeschi
- Twangste (Old Prussian) → Königsberg → Kaliningrad

### ETHICS-010 — Tratta degli esseri umani come categoria di prima classe

Cinque rotte hanno `involves_slavery=True` e `"humans_enslaved"` in
commodities (mai "slaves" come termine — riduce la persona alla categoria):
- Trans-Saharan Slave Route, Bornu-Fezzan, Indian Ocean Slave Route,
  Trans-Atlantic Slave Trade, Triangle Trade.

`Trans-Atlantic Slave Trade` ethical_notes (604 parole, fonte Eltis &
Richardson SlaveVoyages) include: scala (12.5M imbarcati / 10.7M sbarcati /
~1.8M morti nel Middle Passage), date (1501-1866, picco anni 1780),
totali per nazione (Portoghese ~5.8M, Britannico ~3.3M, ecc.),
compagnie nominate (Royal African Company, WIC, Companhia do Grão-Pará),
cause di mortalità, polities africane partecipanti, conseguenze
demografiche/economiche/razziali a lungo termine, movimento per le
riparazioni.

`?involves_slavery=true` filtra esattamente queste 5 rotte. Routes con
slave content secondario (Volga, Stato da Mar, Nile, Via Appia, Varangian)
documentano la tratta in ethical_notes ma NON sono flaggate per evitare
diluizione della categoria.

### Test

- **+19 test** in `tests/test_v640_cities_and_routes.py` (321 → 340).
- Coverage: list/filter (year, type, bbox, involves_slavery, entity_id),
  detail, 404, ETHICS-009 name_variants su Konstantinoupolis, ETHICS-010
  Trans-Atlantic ethical_notes (Middle Passage + millions), OpenAPI doc.
- Full suite verde su SQLite in ~54s.

### Naming transparency (Silk Road & co.)

Silk Road, Grand Trunk Road, Columbian Exchange, Tea Horse Road, Maritime
Silk Road hanno `ethical_notes` che documentano l'origine moderna del nome
(Richthofen 1877, British colonial, Crosby 1972, ecc.) — i partecipanti
storici NON usavano queste etichette. Evita confusione tra storiografia
moderna e auto-designazione storica.

### Deploy

```bash
git push origin main
cra-deploy atlaspi
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "cd /opt/cra && docker compose exec atlaspi python -m src.ingestion.ingest_cities_and_routes"
```

L'ingestione su prod parte vuota (tabelle create dalla migration 005),
quindi inserisce 110+25 senza skip. Verifica:
```bash
curl -s https://atlaspi.cra-srl.com/v1/cities?limit=1 | jq .total
curl -s https://atlaspi.cra-srl.com/v1/routes?involves_slavery=true | jq '.total, .routes[].name_original'
```

---

## [v6.3.2] - 2026-04-15

**Tema**: PostGIS deep work — indici spaziali GiST, bbox filter
geograficamente corretto su `/v1/entity` e `/v1/entities`, e una seconda
linea di difesa ETHICS-006 contro regressioni del fuzzy matcher.

### PostGIS deep work — indici spaziali

- **Alembic `004_postgis_indexes`** — aggiunge due indici GiST funzionali:
  - `ix_geo_entities_capital_geog` su `ST_MakePoint(capital_lon, capital_lat)::geography`
    con `WHERE capital_lat IS NOT NULL AND capital_lon IS NOT NULL`.
    Accelera `ST_DWithin()` su `/v1/nearby` da full-scan a lookup indicizzato.
  - `ix_geo_entities_boundary_geom` su `ST_GeomFromGeoJSON(boundary_geojson)`
    con `WHERE boundary_geojson IS NOT NULL`. Accelera `ST_Intersects()` su
    bbox query.
  - Entrambi gli indici sono **espression indexes**: la query DEVE usare
    la stessa espressione per poter usare l'indice.
- **Compatibilità SQLite**: la migration skippa silenziosamente sul dialetto
  `sqlite`. Niente PostGIS, niente indici, nessun errore in dev.
- **Rollback**: `alembic downgrade -1` droppa entrambi gli indici (su
  Postgres) o è no-op (su SQLite).

### Bbox filter su `/v1/entity` e `/v1/entities`

Nuovo query parameter opzionale `bbox=min_lon,min_lat,max_lon,max_lat`
(formato Mapbox / OSM / RFC 7946).

- **PostGIS path** (prod): `ST_Intersects(ST_GeomFromGeoJSON(boundary_geojson),
  ST_MakeEnvelope(...,4326))` con OR fallback su capital-point per entità
  senza boundary. Usa gli indici GiST appena creati per query
  sub-millisecondo.
- **SQLite path** (dev/CI): pure capital-point `BETWEEN` filter. Meno
  accurato (non include entità il cui polygon interseca il bbox ma la
  cui capitale è fuori), ma sufficiente per test logici e deduplicazione.
- **Validazione**: formato malformato, arity sbagliata, lat fuori [-90,90],
  lon fuori [-180,180], min>max → tutti restituiscono `422` con messaggio
  chiaro. 10 test nuovi in `tests/test_v632_bbox.py`.
- **Componibilità**: bbox si combina con `year`, `type`, `status`, `limit`
  — è un ulteriore filtro, non un override.

### ETHICS-006 — CI guardia capital-in-polygon

Nuovo test in `tests/test_ethics_006_audit.py` — seconda linea di difesa
contro regressioni del fuzzy matcher (v6.1.2 risolse 133 displaced matches
eliminando Garenganze→Russia, CSA→Italia, Mapuche→Australia, ma non c'era
nulla che impedisse a un futuro batch di re-introdurli).

- Scansiona tutte le entità con `boundary_source != "approximate_generated"`
  e verifica che la capitale dichiarata cada dentro (o entro tolleranza)
  il poligono assegnato.
- **Tolleranza a due livelli documentata**:
  - `boundary_match.py`: 50 km (soft, durante il match).
  - `test_ethics_006_audit.py`: 400 km (hard, post-fact audit). Il ruolo
    dell'audit è catturare regressioni catastrofiche (wrong-continent
    copy-paste, 1000+ km), non simplification noise (empire su 4000 km
    rappresentato con 35 vertici → capitale 300 km fuori dal poligono
    semplificato).
- Skippa entità senza `shapely` (graceful), senza capitale, senza boundary.
- Failure mode verbose: lista ID + nome + source + distanza per le prime
  20 violazioni, istruzioni di fix.

### Test suite

- **+13 test** (308 → 321): 10 bbox + 2 ETHICS-006 audit + 1 sanity check.
- Full suite pulita su SQLite in ~43s.

### Deploy workflow

```bash
# 1. push
git push origin main

# 2. deploy (migration 004 gira automaticamente al boot)
cra-deploy atlaspi

# 3. verifica indici (Postgres only)
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "docker exec cra-atlaspi-db psql -U atlaspi -d atlaspi -c '\\di ix_geo_entities_*'"
```

Nessun backfill di dati — solo index creation (idempotente via `IF NOT EXISTS`).

---

## [v6.3.1] - 2026-04-15

**Tema**: Expansion eventi storici 31 → 106, chiudendo il gap tra "scheletro
v6.3" (batch_01_core) e la copertura tematica prevista dalla roadmap.
La governance ETHICS-007/008 è già codificata in v6.3.0; questa patch
aggiunge dati all'interno dello stesso contratto.

### Nuovi batch di eventi storici (+75 eventi)

- **`batch_02_ancient.json`** — 25 eventi, 9 `known_silence`, 14 `event_type`
  distinti, range -2560 → -216 (Great Pyramid, Sea Peoples, Kadesh, Qin
  book-burning, Kalinga, Cartago `GENOCIDE`, Meroë fall, Pompeii).
- **`batch_03_medieval.json`** — 25 eventi, 7 `known_silence`, 15 tipi
  distinti, range 632 → 1644 (morte di Muhammad, Karbala, Baghdad 1258 con
  perdita Bayt al-Hikma, Samalas 1257, Zheng He, An Lushan, Taíno genocide,
  Alhambra Decree come `ETHNIC_CLEANSING`, Valladolid debate, Imjin War).
- **`batch_04_modern.json`** — 25 eventi, 9 `known_silence`, 11 tipi
  distinti, range 1757 → 2004 (Plassey, Bastille, Trail of Tears, genocidio
  Tasmaniano, An Gorta Mór, genocidio circasso, Congo Free State, Katyn,
  Hiroshima-Nagasaki come `MASSACRE`, Indonesia 1965-66 `GENOCIDE`,
  Cambogia, East Timor, Srebrenica, WWW proposal, tsunami 2004).

### ETHICS-007 judgment calls esplicitati nei batch

- Cartago -146 come `GENOCIDE` (non "distruzione"): intento senatoriale
  documentato, scala proporzionale, eliminazione culturale/demografica.
  Frame tradizionale flaggato come "solo prospettiva romana".
- Alhambra Decree 1492 come `ETHNIC_CLEANSING` con `main_actor` = Isabella
  + Ferdinand (ordine di stato, non migrazione spontanea).
- Hiroshima/Nagasaki 1945 come `MASSACRE` per targeting civile;
  `TECHNOLOGICAL_EVENT` menzionato in `ethical_notes`.
- Trail of Tears come `ETHNIC_CLEANSING` (non `DEPORTATION`) con governo
  federale USA come `main_actor` esplicito.
- An Gorta Mór con governo UK come `main_actor` (causazione politica
  documentata in Parliamentary Papers).
- Indonesia 1965-66 `GENOCIDE` con targeting etnico-cinese + politicida PKI.

### Tooling idempotente per produzione

- **`src/ingestion/ingest_new_events.py`** — mirror di `ingest_new_entities.py`
  per la tabella `historical_events`. Chiave dedup `(name_original, year)`.
  Inserisce solo eventi nuovi, log dei link a entità irrisolte (senza
  bloccare). Sicuro per esecuzione ripetuta su DB produzione.

### Deploy workflow (invariato)

```bash
# 1. push
git push origin main

# 2. deploy
cra-deploy atlaspi

# 3. backfill eventi (seed_events_database skippa se tabella non vuota)
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "cd /opt/cra && docker compose exec atlaspi python -m src.ingestion.ingest_new_events"
```

### Stats

- **Eventi**: 31 → 106 (+242%)
- **known_silence=true**: 7 → ~28
- **Regioni coperte**: estensione a Americhe pre-colombiane, Africa
  sub-sahariana, SE asiatico, Pacifico — già presenti nelle entità,
  ora anche negli eventi
- **Test**: 308 (invariato, stessi 25 test v6.3 verificano la nuova scala)
- **Schema / migrations / API**: nessun cambiamento — solo dati aggiuntivi

### Known issues

- 2 `entity_name_original` references nei nuovi batch non risolvono contro
  il DB (eventi che coinvolgono entità storiche minori non ancora seedate).
  Loggato come debug, non bloccante per ingest.

---

## [v6.3.0] - 2026-04-15

**Tema**: Events layer + entity expansion 747→846. Da database di *entità*
geopolitiche a database di *entità + eventi storici*, con ETHICS-007 e
ETHICS-008 come contratto semantico. L'obiettivo: dare agli agenti AI
accesso strutturato non solo a *dove esistevano* gli imperi, ma *cosa è
successo dentro e tra di loro* — incluso ciò che è stato cancellato.

### v6.3 Events layer (NEW)

Tre nuove tabelle (migrazione Alembic `003_historical_events`):

- **`historical_events`** — eventi discreti (battaglie, trattati, epidemie,
  genocidi, eruzioni, carestie). Campi obbligatori: `name_original` (ETHICS-001),
  `event_type`, `year`, `description`. Campi ETHICS: `main_actor` (voce attiva,
  richiesto per tipologie violente), `casualties_low`/`casualties_high` con
  `casualties_source`, `known_silence` + `silence_reason`, `ethical_notes`,
  `confidence_score`, `status`.
- **`event_entity_links`** — junction N:M evento↔entità con ruolo esplicito
  (MAIN_ACTOR, VICTIM, PARTICIPANT, AFFECTED, WITNESS, FOUNDED, DISSOLVED).
- **`event_sources`** — bibliografia per evento (incluso ORAL_TRADITION,
  ARCHAEOLOGICAL, INDIRECT_REFERENCE oltre ai tipi esistenti).

**EventType enum (31 valori, ETHICS-007)**: nessun eufemismo. I termini usati
dalla storiografia accademica sono mantenuti letteralmente: GENOCIDE,
COLONIAL_VIOLENCE, ETHNIC_CLEANSING, MASSACRE, DEPORTATION, FAMINE —
e NON "pacification", "incident", "population exchange", "food crisis".

**ETHICS-008 known_silence**: flag booleano per eventi la cui documentazione
contemporanea è assente, cancellata o deliberatamente soppressa (Operation
Legacy britannico, Herero-Nama con diari tedeschi distrutti, Holodomor con
statistiche URSS soppresse). Gli agenti AI possono filtrare esplicitamente
questi casi via `?known_silence=true` per ricerca sui silenzi archivistici.

### Nuovi endpoint `/v1/events/*` (4)

- `GET /v1/events` — lista con filtri year_min/year_max/event_type/status/known_silence + paginazione
- `GET /v1/events/{id}` — detail con entity_links, sources, ethical_notes
- `GET /v1/events/types` — enumera EventType + EventRole con descrizioni ETHICS-007
- `GET /v1/entities/{id}/events` — reverse lookup eventi di un'entità, filtro per role

Tutti con Cache-Control pubblico (30min lista, 1h detail, 24h types).

### Seed eventi `data/events/batch_01_core.json` (30 eventi)

Copertura di 17 EventType distinti con 7 casi `known_silence=true`.
Esempi selezionati per dimostrare ogni categoria + forzare compliance
ETHICS-007 sul seed stesso:

- Violenza organizzata nominata: Genocidio armeno, Holodomor, Shoah,
  Genocidio ruandese, Genocidio Herero-Nama, Massacro di Nanchino
- Silenzi documentati: Library of Alexandria, Operation Legacy,
  Herero-Nama (diari distrutti), Holodomor (statistiche soppresse),
  Bengal Famine 1943, Armenian Genocide (archivi ottomani purged)
- Catastrofi naturali: Tambora 1815, Lisbon 1755, Jōgan tsunami 869
- Eventi positivi: Dichiarazione diritti 1789, Rivoluzione haitiana,
  Westphalia 1648 (con contesto: "end of religious wars for Europe,
  start of Westphalian sovereignty exported coercively worldwide")

### Entity expansion: 747 → 846 (+99 net, +100 lordi, 6 dedup)

Quattro batch tematici generati da agenti paralleli con istruzioni ETHICS:

- `batch_25_oceania_expansion.json` (25): Tonga, Samoa, Hawaii, Aotearoa,
  Rapa Nui, Marshall Is., Guam/Chamorro, Tahiti, Fiji, Papua, Vanuatu, ...
- `batch_26_precolumbian_expansion.json` (25): Muisca, Mapuche, Tiwanaku,
  Chimú, Moche, Taíno, Pueblos, Iroquois Conf., Mississippian, Zapotec, ...
- `batch_27_me_preislamic_expansion.json` (25): Ebla, Mari, Elam, Urartu,
  Lydia, Nabataeans, Parthia, Palmyra, Hatra, Kingdom of Aksum, ...
- `batch_28_africa_expansion.json` (25): Kanem-Bornu, Benin, Dahomey,
  Luba, Lunda, Ashanti, Sokoto Caliphate, Adal Sultanate, Ajuran, ...

Tutti i batch applicano ETHICS-002 (conquiste documentate), ETHICS-004
(nomi indigeni come primari, coloniali come varianti), con sorgenti
accademiche primarie (Thornton 1992, Mann 2005, Reid 2012, Iliffe 2017, ...).

### Test suite 283 → 308 (+25 v6.3)

`tests/test_v63_events.py` copre:
- Seed popola tabella eventi + link entità risolti
- Filtri API: year, event_type, status, known_silence (true/false), paginazione
- Enum completezza: tutti gli EventType presenti, nessun eufemismo
- ETHICS-007: ogni evento violento ha `main_actor`; ruoli esplicitati nei link
- ETHICS-008: ogni `known_silence=true` ha `silence_reason` non vuoto
- Integrità: confidence in [0,1], casualties_low <= casualties_high
- Seed idempotente (doppia chiamata non duplica)

### Compatibilità

Nessun breaking change. Tutte le tabelle v6.x pre-esistenti restano
identiche. Migrazione Alembic 003 è additiva (tre CREATE TABLE + indici).
Downgrade disponibile.

---

## [v6.2.0] - 2026-04-14

**Tema**: PostGIS deep work + re-matching conservativo post-ETHICS-006.
Chiusura dei follow-up rimasti in v6.1.2 (fuzzy aourednik sbilanciato,
exact_name senza tolleranza, coverage 209 `approximate_generated` da
rivalutare) + migrazione di `/v1/nearby` da O(n) Python haversine a
`ST_DWithin` geography indicizzabile.

### PostGIS-native `/v1/nearby` (src/api/routes/entities.py)

- **Prima (v6.1.x)**: full-scan Python + haversine su ogni riga con
  `capital_lat/lon IS NOT NULL`. Costo O(n), n=747 gia' percepibile
  (~40 ms p95) e non scalabile oltre ~5000 entita'.
- **Ora (v6.2)**: path dual — se `is_postgres()`, esegue `ST_Distance`
  + `ST_DWithin` su `ST_MakePoint(lon, lat)::geography` con filtro
  `radius_m` e ordinamento nativo. Include filtro anno nello stesso
  round-trip SQL. Fallback SQLite conserva il path haversine.
- **Header debug**: `X-Distance-Algorithm: postgis | haversine` per
  osservabilita' ops (nessuna modifica al payload pubblico).
- **Performance osservata**: p95 20 ms su prod (vs ~180 ms prima).
  Indicizzabile via GiST su `ST_MakePoint(capital_lon, capital_lat)`
  quando il volume superera la soglia utile.

### Re-matching conservativo (src/ingestion/rematch_approximate.py, nuovo)

Modulo idempotente per ri-valutare le 209 entita' finite in
`approximate_generated` dopo l'ETHICS-006 cleanup. Retry SOLO strategie
forti (NE ISO + NE exact_name + aourednik exact/fuzzy name), MAI NE
fuzzy — la strada che generava i 133 displacement dell'incidente.

- **Filtro AOUREDNIK_ACCEPTED_STRATEGIES** = `{exact_name, fuzzy_name}`.
  Escluso capital_in_polygon / capital_near_centroid / subjecto / partof:
  assegnano il poligono del contenitore/suzerain, non dell'entita'
  (es. Republica Ragusina → Ottoman Empire: capitale Dubrovnik davvero
  dentro poligono ottomano 1600, ma Dubrovnik ≠ Impero Ottomano).
- **Fuzzy_name geo-guard** (ETHICS-006 estesa a aourednik):
  `_capital_in_geojson` richiesto come per NE fuzzy. Blocca casi tipo
  Hausa Bakwai (Nigeria) → Maya city-states (Mesoamerica).
- **Exact_name 50 km tolerance**: `_capital_distance_to_polygon_km`
  accetta se capitale e' dentro il poligono OPPURE entro 50 km dal
  bordo. Motivo: Sweden/Stockholm 0.4 km off coastal polygon (legittimo)
  vs Mrauk-U/Akan 10.000 km off (chiaramente errato). 50 km cattura
  100% dei cross-continent empirici tollerando il rumore coastal.
- **JSON write-back**: `_apply_upgrades_to_json()` propaga ogni upgrade
  DB nei `data/entities/batch_*.json` cosi' un re-seed riproduce lo
  stato pulito. `--sync-json-from-db` CLI per backfill dopo cleanup.
- **CLI Windows-safe**: `sys.stdout = io.TextIOWrapper(..., utf-8)` per
  nomi non-latini (Россия, မြောက်ဦးခေတ်, ...).

### Cleanup post-v6.1.2 DB pollution

Audit DB ha rivelato 22 righe aourednik pre-esistenti con capitale
>50 km dal poligono (v6.1.1 ingestion senza geo-guard):
- Mrauk-U (Burma) → Akan (West Africa) a 10.066 km
- Kerajaan Kediri (Java) → Kingdom of Georgia (Caucasus) a 8.888 km
- Ghurids (Afghanistan) → Huari Empire (Peru) a 15.302 km
- Imbangala (Angola) → Mangala (Australia??) a 11.340 km

Totale 22+7 displaced aourednik reset a `approximate_generated` con
`name_seeded_boundary()` + confidence cap 0.4 (ETHICS-004). Coverage
72% → **73%** (7 recuperati da exact_name post-rematch > 7 cleanup).

### Centroid-distance soft check per NE fuzzy (src/ingestion/boundary_match.py)

- **Nuova costante** `FUZZY_CENTROID_MAX_KM = 500.0`: secondo filtro
  dopo capital-in-polygon nel NE fuzzy. Rifiuta match dove la capitale
  e' dentro il poligono per accidente (es. enclaves oltremare) ma il
  centroide e' >500 km lontano.
- **Nuovo helper** `_capital_to_centroid_km(entity, geojson)` con
  conversione deg→km lat/lon-aware (cos(lat) per longitudine).
- **Nuovo helper** `_capital_distance_to_polygon_km(entity, geojson)`:
  0 se dentro, km se fuori, None se indeterminabile. Usato dal
  re-matcher per la tolleranza 50 km su exact_name aourednik.

### CI audit — regressione geografica bloccata automaticamente

- **tests/test_boundary_provenance_audit.py** (nuovo, 3 test):
  - `test_no_displaced_boundaries_beyond_tolerance`: ogni riga con
    `boundary_source in {natural_earth, aourednik}` deve avere la
    capitale entro 50 km dal poligono. 0 offenders al commit.
  - `test_no_null_source_with_real_polygon`: se c'e' boundary_geojson,
    boundary_source non puo' essere NULL (ETHICS-005 provenance gap).
  - `test_tolerance_constant_is_reasonable`: meta-test contro
    rilassamento silenzioso (10 ≤ tolerance ≤ 100 km).
- **tests/test_boundary_match_geographic_guard.py** esteso con 3 test
  nuovi per il soft centroid check: `_capital_to_centroid_km` unit
  test, fuzzy-rejected-when-centroid-too-far (exclave in Africa vs
  centroide europeo), fuzzy-accepted-when-centroid-close.

### Metriche v6.2.0

| Metrica | v6.1.2 | v6.2.0 |
|---------|--------|--------|
| Test totali | 272 | **281** (+9) |
| Boundary coverage (NE+aourednik+historical_map) | 72% | **73%** |
| `/v1/nearby` p95 | ~180 ms | ~20 ms |
| Righe aourednik displaced (>50 km) | 22 (hidden) | 0 (audited) |
| AOUREDNIK_ACCEPTED_STRATEGIES | — | `{exact_name, fuzzy_name}` |
| EXACT_NAME_DISPLACEMENT_TOLERANCE_KM | — | 50.0 |

### Files

- `src/config.py`: APP_VERSION 6.1.2 → 6.2.0
- `src/api/routes/entities.py`: `_nearby_postgis()`, path dual, header
  debug `X-Distance-Algorithm`
- `src/ingestion/boundary_match.py`: `FUZZY_CENTROID_MAX_KM`,
  `_capital_to_centroid_km`, `_capital_distance_to_polygon_km`
- `src/ingestion/rematch_approximate.py`: **nuovo** (603 righe)
- `tests/test_boundary_provenance_audit.py`: **nuovo** (146 righe)
- `tests/test_boundary_match_geographic_guard.py`: +102 righe
  (centroid tests)
- `data/entities/*.json`: sync dal DB post-cleanup, 14 file, 7 reset
  aourednik→approximate_generated via `name_seeded_boundary()`

---

## [v6.1.2] - 2026-04-14

**Tema**: Correctness-over-coverage — fix ETHICS-006 (displacement geografico
fuzzy matcher) + hardening del deploy (rimozione volume stale).

### ETHICS-006 — Guardia geografica sul fuzzy matcher

- **Incidente**: audit post-sync v6.1.1 ha trovato **133 su 211** match
  Natural Earth (63%) con la capitale dell'entita' FUORI dal poligono
  assegnato. Esempi catastrofici:
  - Garenganze (regno africano 1856-1891, capitale Bunkeya in DR Congo)
    → matchato a RUS con centroide in Siberia
  - Primer Imperio Mexicano (1821-1823, capitale Ciudad de México)
    → matchato a BEL (Belgio)
  - Mapuche/Reche (popolo indigeno del Cile meridionale)
    → matchato a AUS (Australia)
  - Confederate States of America (1861-1865, Richmond VA)
    → matchato a ITA (Italia)
- **Root cause**: `rapidfuzz.partial_ratio` al 85% faceva pattern-matching
  su token generici ("Kingdom", "Empire", "Republic", "General") e su
  stringhe corte post-normalization di nomi non-latini.
- **Fix** (`src/ingestion/boundary_match.py`): aggiunta guardia
  `_capital_in_geojson()` che rigetta ogni match fuzzy O exact-name se
  la capitale dell'entita' non e' contenuta nel poligono candidato. Se
  l'entita' non ha coordinate di capitale, il fuzzy viene rifiutato
  conservativamente (non si puo' validare geograficamente).
- **Cleanup** (`src/ingestion/cleanup_displaced_ne_matches.py`, nuovo):
  script idempotente che ricostruisce i 133 poligoni errati con
  `name_seeded_boundary()` (ETHICS-004), resettando `boundary_source =
  "approximate_generated"`, azzerando i campi NE/aourednik e cappando
  il confidence a 0.4. Default dry-run per sicurezza.
- **Impact data** (v6.1.1 → v6.1.2):
  - natural_earth: 212 → 78 (solo quelli con capitale nel poligono)
  - aourednik: 290 (invariato)
  - historical_map: 168 (invariato)
  - approximate_generated: 76 → 209 (+133 dall'escalation dal NE errato)
  - Coverage "real boundaries": 93% → **72%** — *volontaria regressione*:
    l'integrita' geografica vince sulla coverage cosmetica.
- **Test** (`tests/test_boundary_match_geographic_guard.py`, 8 nuovi):
  - Predicato puro `_capital_in_geojson` (4 test: inside/outside/
    missing coords/malformed geometry)
  - Regressione Garenganze → RUS rigettato
  - Russian Empire → RUS accettato (plausible + geografic sound)
  - Exact-name match rispetta la guardia (entita' fake "Russia" con
    capitale in Congo rigettata)
  - Fuzzy rifiutato se l'entita' non ha capital coords
- **Documentazione etica**: `docs/ethics/ETHICS-006-natural-earth-fuzzy-displacement.md`
  con incidente, causa, decisione, impatto, lezione ("ogni match
  cross-dataset basato su nomi ha bisogno di un controllo fisico").
  Roadmap v6.2: centroid-distance soft-check come secondo filtro.

### Ops hardening — `/app/data` non e' piu' un volume (ADR-003)

- **Bug osservato**: durante il sync post-v6.1.1 `cra-deploy` faceva
  correttamente `git pull` + `docker compose build` (nuovi JSON nel
  layer immagine), ma il named-volume `atlaspi-appdata:/app/data`
  mascherava il contenuto image con i file stali del primo `up`.
  Il sync in produzione non vedeva gli aggiornamenti finche' non si
  `docker cp`-pava manualmente i file nel volume.
- **Fix**: rimosso il mount `atlaspi-appdata:/app/data` (prod) e
  `app-data:/app/data` (repo standalone). I batch JSON e i dataset
  raw (Natural Earth, historical-basemaps) vivono esclusivamente nel
  layer immagine via `COPY --chown=atlaspi:atlaspi data/ data/` nel
  `Dockerfile`. Il volume `cra_atlaspi-appdata` e' stato rimosso dal
  daemon produzione dopo tarball di backup.
- **Deploy idempotente**: ogni `docker compose up -d atlaspi` dopo
  rebuild garantisce che `/app/data/` rifletta il commit deployato.
  Tag immagine == stato dataset. Rollback atomico.
- **Documentazione**: `docs/adr/ADR-003-bake-data-in-image.md` con
  contesto, problema, alternative scartate (entrypoint-rsync, bind
  mount host, riscrittura volume al deploy), conseguenze.

### Academic credibility — Zenodo DOI mintato

- **Repo reso pubblico** (`github.com/Soil911/AtlasPI`) + toggle Zenodo
  attivato su `https://zenodo.org/account/settings/github/`.
- **GitHub Release v6.1.2** ricreata per triggare il webhook Zenodo
  post-attivazione (la prima Release era stata creata prima del
  webhook e non era stata catturata).
- **DOI mintato**: concept `10.5281/zenodo.19581784` (tutte le versioni,
  risolve sempre all'ultima), version v6.1.2 `10.5281/zenodo.19581785`.
- **Aggiornamenti di citazione**: `CITATION.cff` con campo `identifiers`,
  `README.md` con badge DOI Zenodo + BibTeX aggiornato, `docs/paper-draft.md`
  con DOI in tabella dataset + submission checklist aggiornata.
- **Submission JOHD**: il blocker "DOI minted via Zenodo for cited dataset
  version" nella checklist interna e' ora spuntato.

## [v6.1.1] - 2026-04-14

**Tema**: Boundary coverage jump (23% → 93%) via matcher aourednik + fix
ETHICS-003 compliance su entita' contestate + performance export.

### Boundary enrichment — salto di qualita' dati

- Nuovo modulo **`src/ingestion/aourednik_match.py`** per il matching
  contro **aourednik/historical-basemaps** (CC BY 4.0, 53 snapshot
  timestamped da -123000 a 2010 CE). Risolve il gap pre-1800 che
  Natural Earth non puo' coprire.
- Matching rigoroso a 5 livelli: `exact_name` → `SUBJECTO` (suzerain) →
  `PARTOF` → `fuzzy_name` (soglia 80%) → `capital_in_polygon`
  (point-in-polygon ray casting, prefer smallest container) →
  `capital_near_centroid` (stretto, 250km — solo fallback estremo).
- **Point-in-polygon implementato senza shapely** (ray casting + bbox
  pre-filter + hole exclusion). ETHICS: la capitale dentro il poligono
  e' una prova geografica reale, non un'approssimazione.
- **Pipeline arricchimento** (`enrich_all_boundaries.py`): ordine ora
  NE → aourednik → generated. Idempotente, con `.bak` per ogni file.
  Flag `--skip-aourednik` per test isolati.
- **Tracciamento fonte** per ogni match aourednik: campi
  `boundary_aourednik_name`, `boundary_aourednik_year`,
  `boundary_aourednik_precision` + annotazione `ethical_notes`.
- **313 entita'** arricchite con boundary aourednik (41.6% del dataset).
- **Coverage totale**: 699/752 boundary reali (**93.0%**, da 23%):
  - natural_earth: 212 (28.2%)
  - aourednik: 313 (41.6%)
  - historical_map (manuali): 174 (23.1%)
  - approximate_generated: 51 (6.8%)
  - nessun boundary (manca capitale): 2 (0.3%)

### Fix ETHICS-003 (territori contestati)

- **BUG risolto**: `_apply_natural_earth_match` e `_apply_aourednik_match`
  potevano alzare il `confidence_score` sopra 0.7 anche per entita'
  `status = "disputed"`. Violava ETHICS-003. Ora e' cappato
  esplicitamente: la certezza geografica non risolve la disputa storica.
- Tre entita' gia' salvate con conf > 0.7 sono state riallineate a 0.7:
  Reino de la Araucania y Patagonia (e altre 2 modern disputed).

### Performance

- **`/v1/export/geojson`** riscritto per evitare double-JSON-encoding.
  Il boundary nel DB e' gia' una stringa JSON valida: ora viene embedded
  direttamente nella FeatureCollection invece di `json.loads` + `json.dumps`.
- Nuovi parametri: `?geometry=full|centroid|none`:
  - `full` (default) — poligoni completi, bulk export (~10s per 48MB)
  - `centroid` — Point delle capitali, 200x piu' veloce (<500ms)
  - `none` — solo properties, ideale per indicizzazione
- **`/v1/random` ottimizzato**: prima selezionava TUTTI i candidati con
  eager-loading (48MB di boundary!), poi pickava uno. Ora query ID-only,
  selezione random, eager-load del solo scelto. Da ~3s a <300ms.

### Academic credibility

- **`CITATION.cff`**: metadata di citazione formale per GitHub/Zenodo.
  Autore, versione, licenza, keyword, referenze dataset (Natural Earth +
  aourednik) con attribuzione CC BY 4.0.
- **`.zenodo.json`**: config per archivio Zenodo DOI-minted. Rende
  AtlasPI citabile in letteratura accademica.

### Test

- **260 test totali** (da 233). Aggiunto `test_geojson_export_full_under_15s`
  e riadattato `test_geojson_export_centroid_under_500ms` per riflettere
  la nuova API dell'export.
- Fix 3 regressioni: ETHICS-003 disputed confidence, export performance,
  random performance — tutti i nuovi test verdi.
- Nuova **spot-check regression suite** (`tests/test_spotcheck_top10.py`,
  11 test): blocca le soglie di qualita' boundary per le 10 entita' ad
  alta visibilita' accademica (Roma, Ottomani, Mongoli, Incas, Tokugawa,
  Mughal, Bizantino, Qing, Abbasidi, Azteco). Floor di vertici e
  confidence conservativi — un bug della pipeline che declassasse un
  MultiPolygon a 18 vertici fallirebbe immediatamente il CI. Fixture
  `_enrich_test_boundaries` replica il comportamento di produzione
  (lifespan `update_all_boundaries()`) nel test DB.
- Fix `test_health.py`: assertion versione allineata a 6.1.1 (era stale 6.1.0).
- Nuova **sync regression suite** (`tests/test_sync_boundaries.py`, 11 test):
  copre i predicati puri di riconciliazione (count vertices, should_upgrade),
  la modalita' dry-run, l'idempotenza, e il rispetto di ETHICS-003 cap.

### Boundary reconciliation (post-seed fix)

- **Diagnosi**: audit prod-vs-batch rivela che **419/747 entita' (56%)**
  in produzione conservano confini seeded pre-v6.1.1 (13 vertici) anche
  se i batch JSON contengono poligoni reali multi-centinaia di vertici.
  Root cause: `seed_database()` gira solo su DB vuoto e `update_all_boundaries()`
  copre solo la narrow ENTITY_MAPPINGS (~10 entita'). I 313 arricchimenti
  aourednik non propagano al DB in esecuzione.
- Nuovo modulo **`src/ingestion/sync_boundaries_from_json.py`** +
  CLI `python -m src.ingestion.sync_boundaries_from_json [--dry-run]`.
  Riconciliazione monotona: solo upgrade, mai downgrade. Idempotente.
  Rispetta ETHICS-003 (disputed ≤ 0.70) e richiede un guadagno ≥ 20%
  in vertici per evitare churn da differenze di simplification.
- **Documentazione operativa** in `docs/OPERATIONS.md` con ricetta
  completa (backup Postgres + dry-run + sync).

### Boundary provenance — esposizione schema (ETHICS-005)

- **Gap diagnosticato**: i campi `boundary_source`, `boundary_aourednik_*`,
  `boundary_ne_iso_a3` esistevano nei batch JSON ma non erano persistiti
  nel DB ne' esposti dall'API. Un consumatore non poteva distinguere un
  poligono reale da uno generato senza ispezionare il GeoJSON.
- **Migration `002_boundary_provenance`** (Alembic): aggiunge 5 colonne
  nullable a `geo_entities` (`boundary_source`, `boundary_aourednik_name`,
  `boundary_aourednik_year`, `boundary_aourednik_precision`,
  `boundary_ne_iso_a3`). Puramente additiva, downgrade testato.
- **Modello SQLAlchemy** esteso (`src/db/models.py`).
- **Seeder** (`src/db/seed.py`) ora popola le 5 colonne dai batch JSON
  in fase di seed iniziale.
- **Sync reconciliation** (`sync_boundaries_from_json.py`) propaga
  i 5 campi insieme alla geometria upgrade.
- **Schema Pydantic** (`EntityResponse`) espone i 5 campi con
  description ETHICS-005 esplicita.
- **Serializer** (`_entity_to_response`) passa i 5 campi al Response.
- **4 nuovi test** (`tests/test_boundary_provenance.py`):
  presenza dei campi nella response, valori `boundary_source` nell'enum
  ETHICS-005, scala `boundary_aourednik_precision` (0-3, vedi sotto),
  consistenza metadata aourednik.

### Bug fix — PRECISION_CONFIDENCE invertito

- **Bug latente scoperto** durante la stesura dei test boundary provenance.
  Il dict `PRECISION_CONFIDENCE` in `aourednik_match.py` mappava
  `2 -> 0.80, 1 -> 0.65, 0 -> 0.45`, ignorando completamente il valore 3
  (che e' la **tier piu' alta** dello scale aourednik upstream secondo
  il README di `historical-basemaps`: `1 = approssimato, 2 = moderatamente
  preciso, 3 = determinato da legge internazionale`). I valori 3 finivano
  nel fallback a 0.45 (lo stesso di precision=0), facendo apparire 17
  entita' nel dataset (es. Rzeczpospolita Obojga Narodow, Republiek der
  Zeven Verenigde Nederlanden) come confidence-equivalenti a poligoni
  approssimati quando in realta' avevano la precisione massima.
- **Fix**: dict ribilanciato correttamente: `3 -> 0.85, 2 -> 0.70,
  1 -> 0.55, 0 -> 0.45`. Applicabile alle entita' arricchite in futuro;
  i valori esistenti nel DB di produzione restano stale finche' non si
  rilancia `enrich_all_boundaries`. Documentato in CHANGELOG perche'
  riguarda la trasparenza dell'incertezza (ETHICS).

### Community & academic infrastructure

- **`CONTRIBUTING.md`** (nuovo): guida specifica per segnalare errori
  di boundary/nome/data, proporre correzioni schema, contribuire batch
  entita' regionali. Esplicita la policy ETHICS-003 (disputed cap) e la
  policy ETHICS-001/002 (no revisionismo su nomi e conquiste).
- **`ACKNOWLEDGMENTS.md`** (nuovo): scaffolding per i reviewer academic
  che forniranno feedback pre-submission. Chiude la promessa gia'
  presente in `docs/outreach-draft.md` template D.
- **`CODE_OF_CONDUCT.md`** (nuovo): Contributor Covenant v2.1 standard +
  addendum academic integrity (no citation hallucination, disagreement
  with evidence only, rispetto per storie contese).
- **GitHub issue templates** (`.github/ISSUE_TEMPLATE/`):
  - `boundary-correction.md` (entity/boundary corrections con policy
    esplicita su fonti primarie e ETHICS-003)
  - `bug-report.md` (repro + ambiente)
  - `config.yml` (disabilita issue vuote, punta a email per domande
    metodologiche e a Discussions per conversazioni aperte)
- **`docs/paper-draft.md`** aggiornato:
  - Test count 234 -> 260
  - Pipeline Ourednik riscritta per riflettere i 5 matcher reali
    (exact/SUBJECTO/PARTOF/fuzzy/capital-in-polygon) invece del
    modello semplificato "3 matchers" che era inaccurato
  - Precision scale allineata al README upstream aourednik (1=approx,
    2=moderate, 3=international law) invece dello 0/1/2 sbagliato

### File modificati (principali)

- `src/ingestion/aourednik_match.py` (nuovo, ~450 righe; PRECISION_CONFIDENCE fix)
- `src/ingestion/enrich_all_boundaries.py` (pipeline estesa)
- `src/ingestion/sync_boundaries_from_json.py` (nuovo, riconciliazione monotona)
- `src/api/routes/export.py` (perf + nuovi flag)
- `src/api/routes/entities.py` (random perf + serializer provenance)
- `src/api/schemas.py` (EntityResponse + 5 campi provenance)
- `src/db/models.py` (5 colonne provenance)
- `src/db/seed.py` (seeder provenance-aware)
- `alembic/versions/002_boundary_provenance.py` (nuovo, additive)
- `src/config.py` (version 6.1.1)
- `tests/test_performance.py`
- `tests/test_boundary_provenance.py` (nuovo, 4 test)
- `tests/test_sync_boundaries.py` (nuovo, 11 test)
- Tutti i `data/entities/batch_*.json` (boundary arricchiti con .bak)
- `CITATION.cff`, `.zenodo.json` (nuovi)
- `CONTRIBUTING.md`, `ACKNOWLEDGMENTS.md`, `CODE_OF_CONDUCT.md` (nuovi)
- `.github/ISSUE_TEMPLATE/{boundary-correction,bug-report}.md` + `config.yml` (nuovi)
- `docs/paper-draft.md` (aggiornamenti test count + metodologia aourednik)

## [v6.1.0] - 2026-04-14

**Tema**: Reliability + Discoverability post-deploy. Il sito e' online su
https://atlaspi.cra-srl.com — questa release lo rende **affidabile** e
**scopribile dagli agenti AI**.

### Reliability — Production hardening

- **Sentry SDK** integrato (opt-in via `SENTRY_DSN`). Cattura eccezioni
  FastAPI/SQLAlchemy/Starlette + log >= ERROR. Modulo `src/monitoring.py`
  con interfaccia idempotente. Inattivo by default (zero overhead in dev).
- **Health check esteso** (`/health`):
  - status: `ok` | `degraded` | `down` (era solo "ok")
  - sotto-checks: database, seed, sentry
  - uptime_seconds, check_duration_ms, sentry_active, environment
  - HTTP 503 se database down (le altre situazioni restano 200 per non
    confondere monitoring tools che leggono `status` dal body)
- **Backup automatico**:
  - `scripts/backup.sh` — auto-detect SQLite vs PostgreSQL, retention 14gg
  - `scripts/restore.sh` — ripristino con conferma + safe-copy del DB corrente
  - Sidecar Docker Compose schedulato 03:00 daily
- **Smoke test post-deploy** (`scripts/smoke_test.sh`): 14 endpoint critici
  verificati con curl + jq, exit code 0/1 per CI/CD
- **Operations runbook** (`docs/OPERATIONS.md`): quick actions per incident,
  setup UptimeRobot/Sentry, troubleshooting comuni, baseline performance
- **Logging rotation** in docker-compose: 10MB x 3 file
- **Rate limiting davvero attivo**: aggiunto `SlowAPIMiddleware` (prima
  configurato ma non applicato — bug silenzioso scoperto in audit)

### SEO base

- **`/robots.txt`** con allow esplicito per AI crawler (GPTBot, ClaudeBot,
  anthropic-ai, Google-Extended, PerplexityBot, CCBot)
- **`/sitemap.xml`** con priorita' per homepage, app, docs, embed
- **`PUBLIC_BASE_URL`** configurabile via env (default
  `https://atlaspi.cra-srl.com`)

### Discoverability — MCP Server

Nuovo pacchetto Python **`atlaspi-mcp`** in `mcp-server/`:

- 8 tools MCP che wrappano l'API REST: `search_entities`, `get_entity`,
  `snapshot_at_year`, `nearby_entities`, `compare_entities`,
  `random_entity`, `get_evolution`, `dataset_stats`
- Configurabile via `ATLASPI_API_URL` (default produzione)
- Compatibile con **Claude Desktop** e **Claude Code**
- README con quick start, badge PyPI/Python/License, esempi prompt
- 10 test pytest, 1 di integrazione live opzionale
- Pronto per pubblicazione su PyPI

### Landing page inglese

- **`static/landing/index.html`** — landing dedicata in inglese, separata
  dalla mappa interattiva italiana (`/app`)
- 9 sezioni: hero, why, demo embed, MCP setup, API examples (curl/Python/JS
  con copy-to-clipboard), use cases, stats, for AI agents, footer
- SEO completo: 10 OG tags, Twitter card, JSON-LD `WebApplication` +
  `Dataset` (per Google Dataset Search), hreflang, canonical
- Vanilla HTML/CSS/JS — zero dipendenze, zero tracker, zero CDN esterni
- Atteso Lighthouse: SEO 100, Performance 95+, Accessibility 95+
- Routing: `/` → landing, `/app` → mappa (la vecchia root e' ora a `/app`)

### Boundary coverage — Pipeline pronta

Infrastruttura per portare la coverage dal 23% al 60%+ in v6.1.1:

- **`src/ingestion/natural_earth_import.py`** — carica shapefile NE 10m
  (fallback a 110m gia' nel repo) e produce mapping name → polygon
- **`src/ingestion/boundary_match.py`** — 4 strategie:
  ISO_A3 → exact name multilingua → fuzzy rapidfuzz>=85% → capital-in-polygon
- **`src/ingestion/enrich_all_boundaries.py`** — pipeline end-to-end
  idempotente con dry-run e backup `.bak`. Non sovrascrive boundary
  `historical_map`/`academic_source` mai
- **ETHICS-005** documenta il rischio di anacronismo (boundary moderno su
  entita' antica) e la gestione di confini contestati (Taiwan, Western
  Sahara, Palestina, Kosovo, Cipro Nord, Kashmir, Somaliland)
- Coverage proiettata: 40-50% dopo prima esecuzione, 60%+ con NE 10m + tutti
  i match installati. **Esecuzione rinviata** a v6.1.1 per separare commit
  di codice da commit di dati.

### Test

- **233 test totali** (208 v5.8 + 25 nuovi v6.1)
- Nuovo file `tests/test_v61_features.py`:
  - `TestExtendedHealthCheck` (8 test) — campi nuovi, sotto-checks, status
  - `TestSEOEndpoints` (4 test) — robots.txt e sitemap.xml serviti
  - `TestMonitoringModule` (4 test) — Sentry off-by-default, no raise
  - `TestBackupScripts` (5 test) — script presenti, contenuto corretto
  - `TestConfigDefaults` (3 test) — Sentry DSN sicuro, base URL HTTPS
- Conftest aggiornato: `RATE_LIMIT=100000/minute` per evitare 429 in test

### Dipendenze

- Aggiunte: `sentry-sdk[fastapi]>=2.0.0`, `geopandas>=0.14.0`,
  `shapely>=2.0.0`, `rapidfuzz>=3.0.0`
- Dockerfile aggiunge `sqlite3`, `postgresql-client`, `curl`, `jq`
  per gli script operativi

### Documentazione

- `docs/OPERATIONS.md` — runbook operativo
- `docs/ethics/ETHICS-005-boundary-natural-earth.md` — anacronismo e contesi
- `docs/boundary_coverage_report.md` — analisi attuale + scenari proiettati
- `scripts/README.md` — istruzioni per backup/restore/smoke
- `mcp-server/README.md` — quick start integrazione Claude
- `ROADMAP.md` riorganizzata: v6.0 deploy completato, v6.1 in corso,
  v6.2 PostgreSQL (rinviata), v6.3 distribuzione, v6.4 monetization

### Bugfix

- `SlowAPIMiddleware` mancante: rate limiting non era applicato a nessuna
  route (silently broken). Ora i `60/minute` di default funzionano davvero.
- `static/index.html` footer mostrava ancora v5.8.0 dopo bump.

---

## [v5.8.0] - 2026-04-12

### API — Nuovi endpoint e filtri avanzati
- **`/v1/random` con filtri**: parametri opzionali `type`, `year`, `status`, `continent`
  per ottenere entita' casuali filtrate (es. `/v1/random?type=empire&year=1500`)
- **`/v1/aggregation`**: nuovo endpoint con statistiche aggregate per secolo (etichette romane),
  tipo, continente e status — ideale per dashboard e analisi AI
- Totale endpoint: **21** (da 19)

### Frontend — Cluster markers e mini-timeline
- **Leaflet.markercluster**: i marker delle capitali ora si raggruppano a zoom basso,
  con cluster colorati per densita' (small/medium/large). I poligoni GeoJSON restano visibili
- **Mini-timeline canvas**: nel pannello dettaglio, un canvas interattivo mostra la durata
  dell'entita' con marcatori diamante per ogni cambio territoriale. Tooltip on hover con
  anno, tipo e regione. Colori: verde=espansione, rosso=contrazione, blu=altro
- Stili cluster personalizzati per tema scuro

### Dataset — Espansione a 746 entita'
- **batch_22**: Southeast Asia e Indonesia (26 entita' — Ayutthaya, Dai Viet, Sukhothai, etc.)
- **batch_23**: Americhe pre-colombiane e coloniali (19 entita' — Gran Colombia, Comancheria, etc.)
- **batch_24**: Africa medievale e moderna (19 entita' — Jolof, Zanzibar, Mahdist State, etc.)
- Dedup automatico: 11 duplicati rimossi dai nuovi batch

### Test — 208 test totali
- 23 nuovi test in `test_v58_features.py`:
  - `TestFilteredRandom`: 7 test (filtri tipo/anno/status, combinati, 404, cache)
  - `TestAggregation`: 9 test (struttura, somme coerenti, ordinamento secoli, time_span)
  - `TestDataExpansion`: 4 test (conteggio, tipi, continenti, no duplicati)
  - `TestEvolutionForTimeline`: 3 test (dati canvas timeline)
- Fix test performance random (200ms -> 500ms per query filtrata)

---

## [v5.7.0] - 2026-04-11

### Dataset — Espansione massiva a 682 entita'
- **682 entita' uniche** da 22 batch file (batches 00-21)
- **2.022 fonti accademiche**, **2.041 varianti nome**, **1.899 cambi territoriali**
- Nuovi batch: East Asia (28), Crusader/Islamic (43), Americas/Caribbean (39),
  Africa Kingdoms (14), Europe Medieval (22), South/Central Asia (26), Ancient/Classical (20),
  Mesoamerica/Pacific (25), Horn of Africa/Balkans (25)
- Pulizia: 29 duplicati rimossi con dedup cross-batch automatizzato
- Seed fix: population_affected string-to-int conversion nel seed
- Validazione completa: nessun tipo entita' invalido, nessuno status invalido

### API — Nuovo endpoint evolution
- **`/v1/entities/{id}/evolution`**: cronologia completa di un'entita'
  - Timeline ordinata per anno con tutti i cambiamenti territoriali
  - Sommario: conteggio espansioni, contrazioni, fonti, varianti
  - ETHICS: change_type preservato senza eufemismi

### Frontend — Map capital markers
- **Marker capitali sulla mappa**: tutte le entita' con coordinate capitale
  ora appaiono sulla mappa, anche senza confini GeoJSON
- Label nomi entita' sopra i marker capitali
- Stile CSS migliorato: scrollbar personalizzate, focus visible, hover animations
- Source type styling nel pannello dettaglio
- Stats bar e info grid con layout migliorato

### Test — 185 test passano
- **19 nuovi test** in `test_v57_features.py`:
  - Evolution endpoint (6 test): timeline, ordinamento, sommario, 404, campi
  - Capital data (2 test): copertura coordinate, validazione range
  - Data quality expanded (9 test): 600+ entita', 1800+ fonti, diversita'
  - Cache headers (2 test): max-age, no-cache su random

### Infrastruttura
- Version bump a 5.7.0
- README aggiornato: badge, conteggi, nuovo endpoint nella tabella API
- Lint clean (ruff), 0 errori

---

## [v5.6.0] - 2026-04-11

### API — Nuovi endpoint intelligenti
- **`/v1/nearby`**: ricerca per prossimita' geografica (lat, lon, raggio, anno)
  - Distanza Haversine dalle coordinate capitale
  - Risultati ordinati per distanza, filtrabili per anno
- **`/v1/snapshot/{year}`**: stato del mondo in un anno specifico
  - Sommario per tipo, continente, status
  - Filtrabile per tipo e continente
- Totale: **18 endpoint REST** (da 16)
- OpenAPI aggiornata con esempi per i nuovi endpoint

### Frontend — Autocomplete & UX
- **Ricerca autocomplete**: dropdown con suggerimenti in tempo reale
  - Evidenziazione match nel testo, navigazione con frecce
  - Mostra varianti di nome quando il match e' su un alias
  - Chiusura con Esc, selezione con Enter/click
- **Tasto destro sulla mappa**: popup "Entita' vicine" con distanze
  - Usa `/v1/nearby` con l'anno corrente dello slider
- **Barra di caricamento**: progress bar visiva durante fetch entita'
- **Compare view**: i18n completo, layout refactored
- **Aiuto tastiera**: aggiornato con nuove funzionalita'
- OG meta aggiornata: "550+ entita'"

### Dataset — Espansione fase 3
- **587 entita' storiche** (da 441) — 18 batch JSON
- 5 nuovi batch:
  - **Asia Orientale espansa (29)**: Yamato, Nara, Heian, Kamakura, Muromachi, Sui, 
    Northern Wei, Nanzhao, Dali, State of Chu, Three Kingdoms (Wu, Shu, Wei), 
    Uyghur Khaganate, Tibetan Empire, Tuyuhun, Ainu Mosir
  - **Crociate/Islam espanso (46)**: Kingdom of Jerusalem, County of Tripoli, 
    Principality of Antioch, County of Edessa, Latin Empire, Hamdanids, Buyids, 
    Zengids, Ghaznavids, Samanids, Idrisids, Aghlabids, Marinids, Hafsids, 
    Sultanate of Rum, Caliphate of Cordoba, Nasrid Granada, Rashidun Caliphate
  - **Americhe/Caraibi espanso (45)**: Taino, Maroons, Apache, Navajo, Seminole, 
    Metis Nation, Republic of Texas, CSA, Empire of Brazil, Pirate Republic Nassau, 
    Mosquitia, Cahokia, Mesa Verde, Kingdom of Quito, vicereami coloniali
  - **Regni africani (25)**: Buganda, Bunyoro, Rwanda, Burundi, Lunda, Mutapa, 
    Ndongo, Matamba (Queen Nzinga), Loango, Kano, Dagbon, Futa Jallon, Jolof, 
    Bambara/Segou, Wadai, Baguirmi, eSwatini
  - **Europa medievale (25)**: Brittany, Navarre, Pisa, Brandenburg, Saxony, 
    Bavaria, Naples, Two Sicilies, Savoy, Sardinia-Piedmont, Croatia, 
    Epirus, Trebizond, Second Bulgarian, Georgia, Livonian Order, Courland, 
    Transylvania, Grand Duchy of Lithuania, Catalonia
- Fix dati: rimosso duplicato Balhae, corretto despotate -> principality
- Merge batch duplicati (14, 15) con dedup automatico
- 1683 fonti accademiche, 1530 cambi territoriali documentati

### Test
- **166 test tutti verdi** (23 nuovi per v5.6)
  - 8 test `/v1/nearby`: coordinate, distanza, raggio, anno, ordinamento
  - 9 test `/v1/snapshot`: sommario, filtri, anno antico/moderno
  - 6 test autocomplete: ricerca, varianti, unicode, limiti
- Lint ruff pulito

## [v5.5.1] - 2026-04-11

### Frontend — UI Polish & Precision
- **Caricamento completo entita'**: paginazione automatica (era troncato a 100)
- **Fix scroll mappa**: scrollWheelZoom disabilitato di default, si attiva al click
  - Hint visivo "Clicca sulla mappa per abilitare lo zoom" quando si tenta lo scroll
- **Pannello dettaglio migliorato**:
  - Griglia informazioni (tipo, periodo, durata, capitale con coordinate, regione)
  - Tag continente con icona accanto a status badge
  - Indicatore affidabilita' dettagliato (alta/bassa con colore)
  - Info confini: tipo geometria (Point/Polygon/MultiPolygon), numero vertici/regioni
  - Coordinate capitale visibili
  - Sezione fonti con icone per tipo (academic, primary, archaeological, etc.)
  - Messaggio quando confini non disponibili
- **Slider anno esteso**: da -3100 a -4500 a.C. per le nuove entita' antiche
- **Preset anno aggiuntivo**: pulsante 4500 a.C.
- **Testi aggiornati**: footer v5.5, OG meta "255+ entita'", anno minimo corretto

### Dataset — Espansione fase 2
- **441 entita' storiche** (da 258) — 13 batch JSON regionali
- 6 nuovi batch da agenti paralleli:
  - **Oceania/Pacifico (25)**: Aboriginal nations, Maori iwi, Pacific island kingdoms
  - **Asia Centrale/Steppe (30)**: Sciti, Parti, Timuridi, Khanati dell'Asia Centrale
  - **Sudest Asiatico (25)**: Majapahit, Srivijaya, Lan Xang, Dai Viet, Champa
  - **Subcontinente Indiano (25)**: Pandya, Kakatiya, Polonnaruwa, Ahom, Sikh Empire
  - **Africa espansa (23)**: Great Zimbabwe, Mapungubwe, Lozi, Merina, Rozwi
  - **Europa espansa (23)**: Kyivan Rus', Toscana, Milano, Sardegna, Teutonic Order
- 1332 fonti accademiche, 1190 cambi territoriali documentati
- Fix dati: population_affected convertiti da stringa a intero, entity_type corretti

### Test
- 143 test tutti verdi
- Fix ETHICS-003: disputed entities con confidence <= 0.7
- Fix data quality: varianti nome per territori contestati

## [v5.5.0] - 2026-04-11

### Dataset — Espansione massiva
- **255 entita' storiche** (da 55) — copertura globale da -4500 a.C. al 2024
- 200 nuove entita' organizzate in 6 batch regionali:
  - **Europa (45)**: Francia, Inghilterra, Svezia, Danimarca, Norvegia, Portogallo,
    Commonwealth Polacco-Lituano, Ungheria, Macedonia, Sparta, Prussia, Austria,
    Serbia, Bulgaria, Stato Pontificio, Aragona, Castiglia, Visigoti, Ostrogoti,
    Lombardi, Novgorod, Moscovia, Genova, Firenze, Svizzera, Borgogna, Sicilia,
    Ragusa, Hanse, Paesi Bassi, Carolingi, Scozia, Irlanda, Galles, Valacchia,
    Moldavia, Montenegro, Albania, Boemia, Impero Tedesco, Austria-Ungheria, Italia
  - **Asia (36)**: Shang, Zhou, Qin, Han, Tang, Song, Yuan, Ming, Gupta, Chola,
    Maratha, Delhi Sultanate, Vijayanagara, Kushan, Goguryeo, Baekje, Goryeo,
    Joseon, Timuridi, Parti, Sasanidi, Selgiuchidi, Liao, Jin, Xia, Ryukyu,
    Lan Na, Lan Xang, Pagan, Dai Viet, Pallava, Rashtrakuta, Pala, Funan, Balhae
  - **Africa/Medio Oriente (30)**: Ghana, Kanem-Bornu, Ashanti, Dahomey, Sokoto,
    Oyo, Luba, Kilwa, Ajuran, Sumer, Akkad, Assiria, Babilonia, Ittiti, Omayyadi,
    Fatimidi, Ayyubidi, Mamelucchi, Seleucidi, Tolomei, Nabatei, Palmira, Himyar,
    Mitanni, Urartu, Elam, Almoravidi, Almohadi, Lydia, Media
  - **Americhe (31)**: Olmechi, Maya, Teotihuacan, Toltechi, Zapotechi, Mixtechi,
    Muisca, Wari, Chimu, Moche, Caral-Supe, Tiwanaku, Purepecha, Puebloani,
    Nuova Spagna, Peru', Brasile, 13 Colonie, Haiti, Comanche, Lakota, Cherokee,
    Creek, Quilombo dos Palmares, Missioni Gesuite Guarani
  - **Stati moderni (35)**: Germania nazista, URSS, Jugoslavia, Cecoslovacchia,
    Congo Belga, India, Pakistan, Bangladesh, Vietnam, PRC, DDR, Khmer Rouge,
    Sudafrica apartheid, Rhodesia, USA, Francia, Coree, Turchia, Iran, Arabia
    Saudita, Israele, Iraq, Irlanda, Finlandia, AOF, Indocina francese
  - **Mondo antico (25)**: Fenici, Israele, Giuda, Troia, Minoici, Micenei,
    Sciti, Sarmati, Harappa, Bitinia, Pergamo, Bosforo, Galazia, Commagene,
    Dacia, Corinto, Siracusa, Colchide, Armenia, Xiongnu, Dilmun, Mauretania
- 15 tipi di entita': empire, kingdom, republic, confederation, city-state,
  dynasty, colony, disputed_territory, sultanate, khanate, principality,
  duchy, caliphate, federation, city
- Copertura 7 regioni: Europa (68), Asia (60), Medio Oriente (46),
  Africa (41), Americhe (38), Oceania (1), Altro (1)
- 678 fonti accademiche, 544 cambi territoriali documentati
- ETHICS-003: tutti i territori contestati con confidence <= 0.7

### Frontend
- Icone per 6 nuovi tipi entita': sultanate, khanate, principality, duchy, federation, city

### Test
- 143 test tutti verdi (aggiornati threshold per 255+ entita')
- Lint ruff pulito

## [v5.4.0] - 2026-04-11

### Dataset
- 55 entita' storiche — copertura globale da -3100 a.C. al 2014
- 15 nuove entita' focalizzate su regioni sottorappresentate:
  Majapahit, Srivijaya, Hawaii, Tonga, Mapuche, Cahokia,
  Great Zimbabwe, Benin, Silla, Champa, Aksum, Kush,
  Khwarezmian, Ayutthaya, Aotearoa (Maori)
- Copertura Oceania, Sudest Asiatico, America precolombiana

### API (16 endpoint)
- /v1/entity, /v1/entities, /v1/entities/{id}, /v1/search
- /v1/types, /v1/stats, /v1/continents
- /v1/random (entita' casuale)
- /v1/compare/{id1}/{id2} (confronto strutturato)
- /v1/entities/{id}/contemporaries, /v1/entities/{id}/related
- /v1/export/geojson, /v1/export/csv, /v1/export/timeline
- /health, /embed

### Frontend
- Deep linking completo (?entity=5&year=1500&type=empire&continent=Europe)
- Scorciatoie tastiera (Esc, frecce, /, ?)
- Sezioni dettaglio collassabili con animazioni smooth
- Tooltip arricchiti con confidence bar e icone tipo
- Contemporanei caricati async nel pannello dettaglio
- Filtro per continente con chip e icone regione
- Icone emoji per tipo entita' (empire, kingdom, etc.)
- Dark/light mode toggle con persistenza localStorage
- Time playback (animazione attraverso gli anni)
- Timeline clickabile (click per saltare a un anno)
- Modalita' confronto tra due entita'
- Pulsante condivisione (copia permalink)
- Pagina embed (/embed) per iframe
- Print stylesheet migliorato
- i18n completo IT/EN con nuove chiavi

### Infrastruttura
- 143 test (tecnici, etici, sicurezza, edge cases, performance, data quality, v5 features)
- OpenAPI description con code snippets (Python, JS, curl)
- Tags organizzati per sezione
- GZip + CORS + rate limit + security headers
- Docker + CI + logging strutturato

## [v4.5.0] - 2026-04-11

### Dataset
- 40 entità storiche — copertura globale da -3100 a.C. al 2014
- 7 territori contestati (Palestina, Kosovo, Taiwan, Sahara Occ., Crimea, Tibet, Cipro Nord)
- Nuove: Kemet, Achemenide, Spagnolo, Britannico, SRI, Abbaside,
  Giappone imperiale, Lituania, Zulu, Cartagine, Maurya, Gran Colombia, Haudenosaunee

### API (12 endpoint)
- /v1/entity (search + filter + sort + pagination)
- /v1/entities (list + sort + pagination)
- /v1/entities/{id} (dettaglio)
- /v1/search (autocomplete leggero)
- /v1/types (tipi disponibili)
- /v1/stats (statistiche dataset)
- /v1/entities/{id}/contemporaries (overlap temporale)
- /v1/entities/{id}/related (correlate per tipo/periodo)
- /v1/export/geojson (FeatureCollection)
- /v1/export/csv (tabellare)
- /v1/export/timeline (visualizzazione)
- /health (stato servizio)

### Frontend
- Timeline interattiva con canvas (sotto la mappa)
- Filtro per tipo (chip), ordinamento, barra statistiche
- Export buttons (GeoJSON, CSV, API)
- i18n italiano/inglese con toggle
- Responsive (mobile/tablet)
- Accessibilità WCAG 2.1 AA

### Infrastruttura
- GZip compression middleware
- 100 test (tecnici, etici, sicurezza, edge cases, performance, data quality)
- Performance test: tutti gli endpoint < 500ms
- Data quality test: completezza, diversità, coerenza
- Docker + CI + CORS + rate limit + security headers

## [v3.0.0] - 2026-04-11

### Dataset
- 25 entità storiche (da 10) — copertura 6 continenti
- 5 territori contestati: Palestina/Israele, Kosovo, Taiwan, Sahara Occ., Crimea
- 15 nuove: Bizantino, Mughal, Safavide, Tokugawa, Qing, Russo, Azteco, Mali,
  Songhai, Khmer, Venezia, Etiope, Taiwan, Sahara Occ., Crimea
- Confini reali da aourednik/historical-basemaps (7 periodi: 100-1900)
- Confini moderni da Natural Earth (110m)

### API
- Nuovi endpoint: /v1/search (autocomplete), /v1/types, /v1/stats
- Filtro per entity_type su /v1/entity
- Ordinamento: sort=name|year_start|confidence, order=asc|desc
- Paginazione completa su tutti gli endpoint

### Frontend
- Chip filtro per tipo (empire, kingdom, city, etc.)
- Dropdown ordinamento
- Barra statistiche dataset live
- Responsive (mobile/tablet)
- Accessibilità WCAG 2.1 AA
- Skeleton loader, spinner, error toast

### Infrastruttura
- 68 test (tecnici + etici + sicurezza + edge cases + API avanzata)
- 0 errori lint (ruff)
- Docker + docker-compose
- GitHub Actions CI
- Logging strutturato + rate limiting + CORS + security headers

## [v2.0.0] - 2026-04-11

### Infrastruttura produzione
- configurazione ambiente con .env e pydantic-settings
- Docker: Dockerfile multi-stage + docker-compose.yml
- CORS middleware configurabile
- security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
- logging strutturato (JSON per produzione, testo per sviluppo)
- request_id univoco su ogni richiesta
- error handling centralizzato con formato errore standard
- rate limiting (60 req/min con slowapi)

### API hardening
- input validation: year (-4000..2100), name (max 200), status enum
- paginazione su tutti gli endpoint lista (limit/offset)
- cache headers (Cache-Control: public, max-age=3600)
- OpenAPI documentation con descrizioni e esempi
- errori strutturati {error, detail, request_id}

### Database
- supporto duale SQLite (dev) / PostgreSQL (prod) via DATABASE_URL
- connection pooling per PostgreSQL
- indici compositi su (year_start, year_end), status, name_variants.name
- CheckConstraint su confidence_score (0.0-1.0)
- enum Python per status, change_type, source_type
- seed idempotente (non duplica al riavvio)

### Frontend
- responsive design: desktop, tablet, mobile
- skeleton loader durante caricamento
- spinner nel pannello dettaglio
- error toast con auto-dismiss
- sidebar collassabile su mobile
- accessibilita' WCAG 2.1 AA: aria-label, roles, keyboard navigation
- debounce sulla ricerca (300ms)
- cache client-side dei dettagli entita'
- noscript fallback

### Test (56 test)
- test infrastruttura: health check, database type, request_id
- test paginazione: default, custom, offset, beyond results
- test validazione: year range, name length, invalid status, negative offset
- test edge cases: anno negativo, Unicode, arabo, risultati vuoti
- test integrita' DB: seed idempotenza, cascade config, confidence range
- test sicurezza: CORS preflight, security headers, errori strutturati
- test etici: ETHICS-001/002/003 tutti verificati

### DevOps
- GitHub Actions CI: lint (ruff) + test (pytest) + build Docker
- .dockerignore ottimizzato
- .env.example documentato

### Documentazione
- docs/API.md: documentazione completa endpoint con esempi curl
- docs/DEPLOYMENT.md: guida deploy locale, Docker, PostgreSQL
- OpenAPI interattivo su /docs e /redoc

## [v1.1.0] - 2026-04-11

### Cambiato
- confini sostituiti con dati reali da fonti accademiche (8 su 10 entita')
- fonti: aourednik/historical-basemaps (world_100, world_1300, world_1500, world_1900)
- fonti: Natural Earth ne_110m (Kosovo, Israele/Palestina)
- confini reali: linee solide sulla mappa; approssimazioni: linee tratteggiate
- layout CSS corretto: sidebar non coperta dalla mappa
- aggiunto banner di qualita' dati nella sidebar
- aggiunto overlay informativo sulla mappa
- tema visivo piu' professionale (ispirato GitHub dark)
- tooltip sulla mappa con confidence score
- nomi entita' visibili direttamente sulla mappa
- ricerca live durante la digitazione
- slider anno con aggiornamento in tempo reale
- pannello dettaglio con avviso specifico su fonte dei confini

### Aggiunto
- pipeline estrazione confini (src/ingestion/extract_boundaries.py)
- script aggiornamento confini (src/ingestion/update_boundaries.py)
- dati grezzi in data/raw/ (Natural Earth, historical-basemaps)

## [v1.0.0] - 2026-04-11

### Aggiunto
- API REST completa (FastAPI) con endpoint /v1/entity, /v1/entities, /health
- modelli ORM: GeoEntity, NameVariant, TerritoryChange, Source
- 10 entità storiche demo con metadati etici completi
- interfaccia web con mappa Leaflet, ricerca, filtri per anno e status
- pannello dettaglio con nomi, varianti, cambi territoriali, fonti, note etiche
- sistema di confidence_score con validazione e derivazione status
- pipeline di importazione dati da JSON
- 26 test (tecnici + etici) tutti passanti
- documentazione completa (CLAUDE.md, README, ROADMAP, ADR, ETHICS)

### Entità demo incluse
- Imperium Romanum, Osmanlı İmparatorluğu, İstanbul
- Tawantinsuyu (Impero Inca), British Raj
- Palestina/Israele (disputato), Kosovo (disputato)
- Ἀθῆναι (Atene antica), Impero Mongolo, Regno del Kongo

## [v0.0.1] - 2026-04-11

### Aggiunto
- documentazione fondazionale del progetto
- ADR iniziali
- ETHICS records iniziali
- template per decisioni future
- struttura repository fondazionale
