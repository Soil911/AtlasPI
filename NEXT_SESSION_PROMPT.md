# AtlasPI — Prompt per la prossima sessione (handoff 2026-07-04)

> ## ✅ AGGIORNAMENTO 2026-07-04 sera — sessione autonoma completata (v6.99.118→124)
> Tutto committato, testato (suite 1293 verde), CI verde, deployato su prod. 8 release:
> - **v6.99.118** — ETHICS-019: fix mislabel #240 (→ Kampuchea Democratica `កម្ពុជាប្រជាធិបតេយ្យ`,
>   QID Q330988) e #534 (→ `Anpi an Ayiti`, empire, variante `Empire d'Haïti`). ✅ Task 1+2.
> - **v6.99.119** — M3 lingua: ~450 stringhe machine-facing IT→EN (OpenAPI/errori/tag/docstring
>   Pydantic), secoli `BCE`, on-this-day/at-date con `entities` eager (chiude N+1). ✅ parte Task 4(M3).
> - **v6.99.120** — M1/ETHICS-020: 8 entità-sblocco nuove + rename nativo Lan Xang #128 (era thai);
>   catene 34/123-126/130 estese + 3 nuove (Saudi/Nepal/Taqali). Scoperta: Mahdiyya #736 e Medri
>   Bahri #658 esistevano già (coda rename M4). ✅ Task 3.
> - **v6.99.121** — ETHICS-021: split Sri Lanka (#142 era nome di re → Anuradhapura; #386 deprecata;
>   #600 → Dambadeniya; +Gampola +Kotte; catena Sinhalese trunk). ✅ parte Task 3(split).
> - **v6.99.122** — ETHICS-022: split Kemet (#26 empire→civilization ombrello; 4 entità-periodo
>   tꜣ.wy Old/Middle/New + Πτολεμαϊκὴ βασιλεία; 16 eventi ri-organizzati con agentività kushita/
>   persiana; catena 3 Regni). ✅ parte Task 3(split).
> - **v6.99.123** — M3: freshness conteggi README/OpenAPI (1006 entità live, 104 catene, 5000+ fonti)
>   + nuova pagina `/why` "Why AtlasPI, not Wikidata?" (4 query comparate reali). ✅ Task 4(M3) completo.
> - **v6.99.124** — M4: sincronizzati 14 rename nativi prod-only (JSON latino→nativo + variante
>   romanizzazione + cascata refs). ✅ parte Task 5(M4).
>
> **RESTA (M4, il track più lungo, lowest-leva)**: 3 rename (incl. #413 Dar Fur = doppio record JSON
> = anche ombreggiato); **87 confidence in coda** `data/fixes/conf_review_queue.json` (tutte ancora
> json>prod, servono fonti verificate per alzare prod — ADR-011, a lotti ~10); **~30 ombreggiati**;
> **61 JSON-only** mai seedate. Vedi memoria `project_reconciliation_debt` (metodo diff riusabile).
> Follow-up entità: PRK Cambogia 1979-89, Eritrea italiana, Serbia moderna, Terzo Periodo Intermedio/
> Periodo Tardo egizio, ripristino #552 Meroe (deprecata, in realtà entità-fase) per catena #99,
> Repubblica Khmer 1970-75 (creata in M1). Cross-check ETHICS usato ovunque (ETHICS-019→022 documentati).
>
> ⚠️ **`ingest_new_entities` resta pericoloso** finché #413 e i JSON-only non sono chiusi.

---

## (Piano originale sotto — parzialmente superato dalle release di cui sopra)

Riprendi AtlasPI e **lavora in autonomia, in background, senza interromperti per
chiedere conferme**. Prendi decisioni sensate; per le scelte etiche non banali usa il
cross-check ChatGPT (`scripts.chatgpt_review.ask`) e documenta in un record `docs/ethics/`.
Per OGNI task completato: dual-write JSON+prod, suite verde, CI verde, backup, deploy,
aggiorna CHANGELOG + ROADMAP + memoria. NON fermarti tra un task e l'altro: procedi lungo
la lista in ordine di priorità finché non l'hai esaurita (o finché non resta solo roba
bloccata da login umano — vedi §BLOCCATI).

## Stato di partenza (verificato 2026-07-04)
- **Prod sana a v6.99.117**, dominio pubblico **https://atlaspi.it** (cutover fatto il
  2026-07-03; il vecchio `atlaspi.cra-srl.com` fa 301 permanente — NON rimuoverlo mai).
- CI verde, suite ~1293 verde, tutto committato/pushato su `Soil911/AtlasPI` main.
- **Dati**: 1039 entità (993 vive, 46 deprecate), tutte con boundary; 99 catene (321 link);
  643 eventi, 55 periodi, 252 città, 1249 siti, 105 sovrani, 29 lingue; 4928 fonti.
  Confidence: 245 ≥0.85 · 207 [0.7,0.85) · 339 [0.6,0.7) · 175 [0.5,0.6) · 27 <0.5.
  **Integrità etica pulita**: 0 violazioni ETHICS-013, 0 disputed sopra il cap 0.70.
- **M2 (discoverability) quasi chiusa**: atlaspi.it, GSC verificato+sitemap, registry MCP
  ufficiale (`io.github.Soil911/atlaspi` via workflow OIDC), IndexNow, DOI 21191521,
  PyPI atlaspi-mcp 0.10.1 / atlaspi-client 0.3.0, Matomo siteId 2, PR awesome-mcp #9219.

## Roadmap seguita
Tesi 2026-07-02 (in `ROADMAP.md`): dati solidi, il collo di bottiglia era la trovabilità.
Ordine per leva **M2 › M3 › M1 › M4 › enrichment**. M2 è fatta → tocca M3/M1.

---

## TASK AUTONOMI — falli tutti, in quest'ordine

### 1. Flag etici (PRIORITÀ MASSIMA — verità storica rappresentata male)
- **#240 Cambogia** ⚠️ il più delicato. `name_original='សាធារណរដ្ឋខ្មែរ'` (= *Repubblica Khmer*,
  regime di Lon Nol 1970-75) ma `year_start=1975, year_end=1979` = anni della **Kampuchea
  Democratica** (Khmer rossi, regime del **genocidio cambogiano**, ~1.5-2M morti; nome atteso
  `កម្ពុជាប្រជាធិបតេយ្យ`). Ispeziona il record completo su prod, verifica con WebSearch date/nomi
  dei due regimi, e **controlla cosa referenzia #240** (eventi, chain_links, ecc.) prima di
  decidere fra: (a) correggere nome→Kampuchea Democratica con note sul genocidio; (b) correggere
  anni→1970-75 tenendo Khmer Republic; (c) creare entrambe le entità. La scelta dipende dai ref.
  ETHICS record + dual-write + backup. C'è un chip/task già flaggato per questo.
- **#534 Haiti**. È il *Primo Impero* di Dessalines (1804-1806) ma ha `name_original='Repiblik
  Dayiti'` (errato: era un IMPERO, non una repubblica; kreyòl ibrido). Rename via ETHICS-001 con
  fonti (atteso *Anpi an Ayiti* / *Empire d'Haïti*). Nota: già documentato in ETHICS-017 §8 e
  nella catena "Haitian state" (batch_36). Dual-write.

### 2. M1 — entità-sblocco + catene rimanenti
Crea le entità mancanti (INSERT SQL transazionale su prod + record JSON in `data/entities/`,
fonti VERIFICATE via WebSearch, boundary anche approssimato, confidence onesta), poi incatena:
- **Lan Xang** (1354-1707) → predecessore dei 3 regni lao (catene Vientiane/Luang Prabang/Champasak in batch_35).
- **Regno dei Serbi, Croati e Sloveni** (1918-1929/41) → serve alla catena serba #34 (i cui link
  'Jugoslavija' non risolsero mai) E come successore del Montenegro (catena batch_36).
- **Cambogia post-angkoriana** (Longvek/Oudong, 1431-1863) → estende all'indietro la catena
  cambogiana (batch_35, oggi 2-link deliberatamente corta per evitare il salto Khmer 1431→1863).
- **Regno Ndebele** (1838-1893) → successore dei Rozwi (catena "Zimbabwe plateau southwestern", batch_34).
- **Emirato di Dirʿiyya** (1744-1818) + **Emirato di Najd** (1824-1891) → poi incatena **Saudi #253**.
- **Nepal repubblicano** (2008-) → poi incatena **Gorkha #399**.
- **Stato Mahdista** (1885-1899) → poi incatena **Taqali #411**.
- **Medri Bahri** (ምድሪ ባሕሪ, altopiano eritreo ~1450-1890) → da ETHICS-018 (la sua variante fu
  rimossa da Aksum, va creata come entità propria).
⚠️ Le entità nuove vanno via **INSERT SQL transazionale** (come `scripts/sql_babylon_split.sql`):
`ingest_missing_entities`/`ingest_new_entities` NON girano al boot e su prod creerebbero duplicati.

### 3. Split super-aggregati (ETHICS record PRIMA)
- **Sri Lanka #142**: conf 0.4, `name_original='මහා විජයබාහු'` = **nome di un RE** (Vijayabāhu),
  non dello stato. Design con record ETHICS (classe ETHICS-015) prima di toccare: la linea è
  Anuradhapura → Polonnaruwa → … → Kandy (#388 già esiste). NON splittare popoli indigeni continui.
- **Kemet #26**: valutazione split (ETHICS record). Fase meroitica nativa (vedi note catena #99).

### 4. M3 — Agent-UX dimostrabilmente superiore
- **Lingua machine-facing**: 404 / summary OpenAPI / messaggi d'errore sono in italiano →
  strategia lingua esplicita (EN per il machine-facing, IT resta per le ethical_notes narrative).
- **on-this-day**: payload magro / N+1 (già iniziato in v6.99.109, completare).
- **Freshness release**: README con conteggi vecchi, dist/ SDK stantii → allineare ai conteggi reali.
- **Pagina/benchmark "perché AtlasPI e non Wikidata"** con query comparate reali.

### 5. M4 — Riconciliazione JSON↔prod (fresh-seed ≡ prod)
- **87 confidence in coda** `data/fixes/conf_review_queue.json`: review manuale a lotti ~10, con
  fonti verificate prima di alzare la conf prod (policy ADR-011). Riusa `scripts/reconcile_confidence.py`.
- **17 rename nativi prod-only** (pattern = backport Wadai v6.99.110: string-surgery + variant latina).
- **30 record JSON ombreggiati** (last-wins) da pulire; **61 entità JSON-only** mai seedate.

### Track continuo — enrichment coda <0.6 (~202 entità, valore marginale calante)
Solo se le priorità sopra sono esaurite. Workflow turnkey in memoria `project_enrichment_workflow`.

---

## §BLOCCATI — richiedono un login umano di Clirim (NON tentare in background)
Se li incontri, saltali e lasciali documentati — non fermare il resto del lavoro:
- **Bing Webmaster**: bing.com/webmasters → Sign in con Google (albian.soil@gmail.com) → Import da GSC.
- **npm**: serve `NPM_TOKEN` nei secrets GitHub; poi push tag `sdk-js-v0.3.0` pubblica atlaspi-client su npm.
- **HuggingFace**: upload del dataset (`hf-dataset/` pronto) — login HF.

## Note operative critiche (INVARIATE)
- **Deploy**: `/c/Users/cliri/bin/cra-deploy.sh atlaspi` (l'auto-deploy GitHub è inaffidabile);
  verifica `curl https://atlaspi.it/health` post-deploy.
- **SQL prod**: `ssh -i ~/.ssh/cra_vps root@77.81.229.242 "docker exec -i cra-atlaspi-db psql -U atlaspi -d atlaspi -v ON_ERROR_STOP=1" < file.sql`.
  **Backup `pg_dump` PRIMA** di ogni SQL di scrittura su prod.
- **Dual-write SEMPRE** (JSON in `data/` + prod SQL, identici). Entità nuove = INSERT SQL transazionale.
- ⚠️ **NON** lanciare `ingest_new_entities`/`ingest_missing_entities` su prod (creerebbe duplicati).
- **Bash sandbox reverta i file git-tracked** → usa `dangerouslyDisableSandbox` o gli strumenti
  Edit/Write per persistere. Console cp1252 → `PYTHONUTF8=1` per Python con nomi non-ASCII.
- **File JSON**: molti NON round-trippano (compatti / `\uXXXX`-escaped) → chirurgia a stringa per
  edit puntuali (vedi `scripts/reconcile_confidence.py`, `cascade_chain_refs_to_primary.py`).
- **Fence CI da tenere verdi**: `test_chain_dedup_json_audit`, `test_chain_deprecated_json_audit`,
  `test_deprecated_exclusion`, `test_database` (le deprecate sono escluse dal check name_variants).
- **CI verde + suite verde + backup PRIMA di toccare prod.** Cross-check ChatGPT-5.5 per decisioni etiche.
- **MCP registry**: si ri-pubblica da solo via `.github/workflows/publish-mcp-registry.yml` (OIDC)
  a ogni push di `mcp-server/server.json` — se cambi versione MCP, aggiorna anche lì.
- **Dominio**: 301 dal vecchio host e SAN nel cert `app.cra-srl.com` da NON rimuovere mai
  (wheel PyPI/npm e DOI immutabili puntano al vecchio host). `sites-enabled/cra-srl` sul VPS è un
  FILE REGOLARE (non symlink): patcharlo direttamente e ri-sincronizzare in sites-available.
