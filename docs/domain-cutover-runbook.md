# Runbook cutover dominio: atlaspi.cra-srl.com → atlaspi.it

**Stato**: preparato 2026-07-03 sul branch `domain-atlaspi-it` (repo-side completo).
**Gate**: DNS di atlaspi.it delegato e propagato (al momento della scrittura: NXDOMAIN —
Clirim deve configurare al registrar: **A `atlaspi.it` → 77.81.229.242** e
**A/CNAME `www.atlaspi.it`** → stesso IP/apex).

## Pre-condizioni (verificare TUTTE)

```bash
# 1. DNS risolve all'IP del VPS (da due resolver)
nslookup -type=A atlaspi.it 8.8.8.8      # atteso: 77.81.229.242
nslookup -type=A www.atlaspi.it 8.8.8.8
# 2. CI verde sul branch, suite verde in locale
# 3. Backup DB fresco (pg_dump) — non ci sono migration ma è la regola
```

## Sequenza cutover (ordine obbligatorio)

### 1. VPS — nginx server block per il dominio nuovo (HTTP only, per la ACME challenge)

Creare `/etc/nginx/sites-available/atlaspi` (file DEDICATO — quello attuale
`cra-srl` è condiviso con app/agent, non toccarlo se non per il 301 al passo 4):

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name atlaspi.it www.atlaspi.it;

    location / {
        proxy_pass http://127.0.0.1:10100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/atlaspi /etc/nginx/sites-enabled/atlaspi
nginx -t && systemctl reload nginx
```

### 2. VPS — certificato Let's Encrypt (certbot aggiunge l'HTTPS + redirect HTTP→HTTPS)

```bash
certbot --nginx -d atlaspi.it -d www.atlaspi.it
# scegliere redirect HTTP→HTTPS quando chiesto; poi:
nginx -t && systemctl reload nginx
curl -sI https://atlaspi.it/health   # atteso 200 (serve ancora il codice vecchio: ok)
```

⚠️ NON rimuovere la SAN `atlaspi.cra-srl.com` dal cert condiviso di
`app.cra-srl.com`: serve TLS valido sul vecchio host finché esiste il 301
(= a tempo indefinito: i wheel PyPI/npm già pubblicati hanno il vecchio
dominio cotto dentro).

### 3. VPS — env (`/opt/cra/.env.atlaspi`)

```
PUBLIC_BASE_URL=https://atlaspi.it
CORS_ORIGINS=https://atlaspi.it,https://www.atlaspi.it,https://app.cra-srl.com,https://agent.cra-srl.com
```

(⚠️ memoria progetto: `docker compose restart` NON ricarica env_file —
serve `up -d --force-recreate` o il `cra-deploy` del passo 5.)

### 4. VPS — 301 permanente dal vecchio host

Nel file condiviso `/etc/nginx/sites-available/cra-srl`, sostituire il blocco
`location /` del server `atlaspi.cra-srl.com` (HTTPS) con:

```nginx
    return 301 https://atlaspi.it$request_uri;
```

(lasciare il server block HTTP→HTTPS esistente com'è). Poi `nginx -t && systemctl reload nginx`.

### 5. Merge + deploy

```bash
git checkout main && git merge --no-ff domain-atlaspi-it
git push origin main            # CI deve essere verde
/c/Users/cliri/bin/cra-deploy.sh atlaspi
```

### 6. Verifiche post-cutover

```bash
curl -sS https://atlaspi.it/health | python -m json.tool          # 200, versione nuova
curl -sI https://atlaspi.cra-srl.com/v1/entities | head -3        # 301 → atlaspi.it
curl -s  https://atlaspi.it/llms.txt | head -20
curl -s  https://atlaspi.it/sitemap.xml | head -5                 # <loc> con atlaspi.it
curl -s  https://atlaspi.it/.well-known/mcp.json | python -m json.tool | head
curl -sS https://atlaspi.it/v1/entities?limit=1 -H "Origin: https://atlaspi.it" -i | grep -i access-control
# healthcheck del workflow deploy.yml ora punta a atlaspi.it → verificare che il
# prossimo run "Deploy to production" non fallisca il curl
```

### 7. Post-cutover (stessa settimana)

- **Release pacchetti** (nuovi default = atlaspi.it): `atlaspi-mcp` 0.10.0 (PyPI),
  `atlaspi-client` 0.3.0 (PyPI), `atlaspi-client` 0.3.0 (npm — PRIMA rebuild di
  `sdk-js/dist`: `npm run build` in sdk-js/, il dist committato va rigenerato).
- **GitHub repo**: campo *website* → https://atlaspi.it (UI GitHub, manuale).
- **Zenodo**: i metadata dei record esistenti (19581784/85) sono editabili dalla
  UI — aggiornare il link "Live service" nella description (opzionale, il 301 copre).
- **M2 submissions** (ora sbloccate, UNA volta col dominio definitivo):
  MCP registry, Google Search Console + Bing Webmaster (proprietà atlaspi.it),
  backlink iniziali (awesome-lists), Matomo (server + site id — decisione hosting).
- **Monitoraggio 301**: `cra-logs` + access log nginx del vecchio host per stimare
  quando il traffico legacy si esaurisce (mai sotto zero: DOI/wheel immutabili).

## Cosa contiene già il branch (repo-side, fatto)

- 195 sostituzioni dominio su 66 file load-bearing (runtime, static, .well-known,
  CI, docs, pacchetti, script, test) — whitelist esplicita, artefatti storici esclusi.
- Refactor: `embed.py` e `_LLM_PROBE_POINTER.docs` usano `PUBLIC_BASE_URL`
  (dominio runtime in un solo posto: `src/config.py` + env).
- FAQ riscritta (non più "hosted at the sponsor's domain"; 301 documentato).
- Bump versioni pacchetti: mcp 0.10.0, sdk-py 0.3.0, sdk-js 0.3.0.
- `.zenodo.json`/`CITATION.cff` già puntati al dominio nuovo (prossima release).
- Esclusi di proposito: CHANGELOG, docs/audit, handoff/, data/briefings,
  research_output (artefatti storici — il vecchio dominio lì è corretto).
