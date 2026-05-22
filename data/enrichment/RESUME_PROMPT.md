# AtlasPI Loop — Resume Prompt (for new Claude sessions)

Copy-paste this prompt into a new Claude Code session opened in AtlasPI directory
to continue the autonomous loop from where the previous session stopped.

Last update: 2026-05-22 after Phase C/D/E completed (v6.99.65 live).

---

Sei Claude che lavora autonomamente sul progetto AtlasPI (database geografico storico).
Sito live: https://atlaspi.cra-srl.com — versione attuale v6.99.65, stabile, healthcheck OK.

## 📍 Contesto essenziale (leggi PRIMA `data/enrichment/LOOP_STATE.md`)

In sessioni precedenti sono state completate Phase A/C/D/E (boundaries 297/297, cities
110→252, name_variants 3016→3060, GPT-5.5 fact-check applicato). Resta:

- **Phase B continuation**: enrichment di ~150 entità con conf 0.7-0.85 e n_sources≤3
- **Phase F visual**: tour mappa multi-epoca via Chrome MCP per verificare rendering
- **Fix URL vuoti**: 1020 sources con `url=''` da sostituire con WorldCat ISBN/DOI dove ISBN disponibile in citation
- **HF Datasets bulk**: cities aggiuntive da importare (target 300+)

## ⚙️ Infrastruttura già pronta

- **OpenAI key**: `~/.openai-atlaspi-key` (chmod 600, fuori repo). Modello: `gpt-5.5` con `reasoning_effort=low`.
- **Wrapper Python**: `scripts/chatgpt_review.py` — usa `from scripts.chatgpt_review import ask, fact_check`
- **Safe deploy**: `bash scripts/safe_deploy.sh <iter_label>` — fa push + cra-deploy + healthcheck + auto-revert su fail
- **SSH VPS**: `ssh -i ~/.ssh/cra_vps root@77.81.229.242` (root, qualsiasi comando)
- **DB query pattern**:
  ```
  ssh -i ~/.ssh/cra_vps root@77.81.229.242 "docker exec cra-atlaspi-db psql -U atlaspi -d atlaspi -c \"<SQL>\""
  ```
- **SQL apply pattern**: scrivi `.sql` in `scripts/`, poi:
  ```
  scp -i ~/.ssh/cra_vps scripts/<file>.sql root@77.81.229.242:/tmp/x.sql
  ssh -i ~/.ssh/cra_vps root@77.81.229.242 "docker cp /tmp/x.sql cra-atlaspi-db:/tmp/x.sql && docker exec cra-atlaspi-db psql -U atlaspi -d atlaspi -f /tmp/x.sql"
  ```
- **Guard file**: `src/ingestion/fix_antimeridian_and_wrong_polygons.py` ha set `MANUALLY_CURATED_IDS` (297 IDs) che protegge i boundary curati dal restart-reset. Se aggiungi/modifichi boundary di un'entità, aggiungi l'ID al set.

## 🚦 Regole rigide (da CLAUDE.md, NON violare)

- ❌ Nessun `DROP TABLE`, `git push --force`, `--no-verify` su hooks
- ❌ Nessun alembic downgrade oltre -1 senza backup pg_dump prima
- ❌ Mai toccare directory `data/raw/` o reseed senza backup
- ✅ Backup DB esiste: `/root/atlaspi-backup-pre-loop-20260521-201426.sql` su VPS
- ✅ Frontend (static/js/*) MODIFICABILE se utile
- ✅ Ogni deploy via `safe_deploy.sh` (auto-revert su healthcheck KO 3x)
- ✅ ETHICS: ogni nuova entità storica con commento `# ETHICS:` se conquista/genocidio/colonizzazione coinvolta

## 📝 Workflow per ogni iter (consolidato in 30+ iter precedenti)

1. Query DB SSH per identificare 10 entità target (es. low n_sources + conf alta)
2. Per ognuna: WebFetch academic refs (Cambridge UP, Oxford UP, Yale, Brill, ecc.)
   o canonical knowledge se Wikipedia 404
3. Scrivi `scripts/sql_phaseB_sNN.sql` con `INSERT INTO sources (entity_id, citation, url, source_type) VALUES ...` (5 refs per entità)
4. Apply via SSH (pattern sopra)
5. Bump version in `src/config.py` + `pyproject.toml` (es. v6.99.65 → v6.99.66)
6. Update `CHANGELOG.md` (entry in cima)
7. Git add + commit con messaggio descrittivo "feat(v6.99.NN): SNN — +50 sources (...)"
8. `bash scripts/safe_deploy.sh <iter>` — controlla che ritorni "deployed OK"
9. Update `data/enrichment/LOOP_STATE.md` con iteration log
10. Iter successiva

## 📊 Stato finale post-precedente sessione (verifica con SQL prima di iniziare)

- Total sources: 4317
- Entity ≥3 sources: 879 (target 90% = ~935 → +56 da fare)
- Entity ≥5 sources: 364 (target 40% = ~415 → +51 da fare)
- Cities: 252
- Name variants: 3060
- Curated boundaries: 297/297 (Phase A COMPLETE)
- Version live: v6.99.65

## 🎯 Cosa fare ADESSO

Procedi in foreground continuo (NON `ScheduleWakeup` — perso al restart Claude Code):

**Step 1** — Phase B continuation S41+. Query:
```sql
SELECT g.id, g.name_original, g.confidence_score,
       (SELECT count(*) FROM sources s WHERE s.entity_id=g.id) AS n_src
FROM geo_entities g
WHERE g.confidence_score BETWEEN 0.78 AND 0.92
  AND (SELECT count(*) FROM sources s WHERE s.entity_id=g.id) BETWEEN 2 AND 3
ORDER BY g.confidence_score DESC, n_src ASC LIMIT 15;
```
Continua a batch di 10 finché ~90% entità hanno ≥3 sources E ~40% hanno ≥5 sources.

**Step 2** — Fix URL vuoti. Query:
```sql
SELECT entity_id, citation FROM sources
WHERE (url IS NULL OR url='') AND citation ILIKE '%ISBN 978-%'
LIMIT 20;
```
Per ogni risultato estrai ISBN via regex e UPDATE url to `https://www.worldcat.org/isbn/<ISBN-no-hyphens>`.

**Step 3** — Phase F visual (se Chrome MCP disponibile, `mcp__Claude_in_Chrome__list_connected_browsers`):
- Naviga a https://atlaspi.cra-srl.com/app
- Screenshot a anni: 1, 500, 1000, 1500, 1800, 1900
- Verifica boundaries renderizzano correttamente per entità appena create
- Salva screenshots in `data/enrichment/loop_screenshots/`

**Step 4** — Aggiorna `LOOP_STATE.md` con tutti i progressi e schedula prossima iter
in foreground (NON ScheduleWakeup).

## 🛑 Fermarsi quando

- Phase B raggiunge 90%/40% target
- Context conversazione esaurito (~150K tokens)
- Healthcheck fallisce 3x consecutive (allora STOP + alert in LOOP_STATE.md)
- Clirim scrive nuovo messaggio

## 📨 Quando finisci la sessione

Riepiloga all'utente Clirim:
- Quante iter eseguite
- Quanti sources/cities/variants aggiunti
- Versione live attuale
- Cosa resta da fare per sessione successiva
- Eventuali bug/decisioni che richiedono human review

Inizia leggendo `data/enrichment/LOOP_STATE.md` per allineare il context, poi
verifica stato DB attuale via SSH, poi parti con Phase B Step 1.

Buon lavoro.
