# Wave 1.1 — Admin containment: inventory + design

Date: 2026-05-28
Status: design (pre-implementation, awaiting ChatGPT cross-check)

---

## Inventory: chi chiama `/admin/*`

### 1. Browser admin UI (deve continuare a funzionare per Clirim)
- **`static/admin/brief.html`** (dashboard cofounder):
  - POST `/admin/ai/analyze`, `/admin/ai/implement-accepted`
  - POST `/admin/ai/suggestions/{id}/{accept|reject|implement}`
  - GET `/admin/coverage-report`, `/admin/insights`, `/admin/ai/status`, `/admin/ai/suggestions?limit=500`
- **`/admin/analytics`** HTML page (server-rendered in `analytics.py`) con JS embedded:
  - GET `/admin/analytics/data?scope=...`
  - GET `/admin/dev-ips`, POST `/admin/dev-ips/mark-current`, DELETE `/admin/dev-ips/{id}`

### 2. Cron giornaliero (deve continuare a funzionare automaticamente)
- **`scripts/daily_ai_check.sh`** @ root crontab `0 4 * * *`:
  - POST `https://atlaspi.cra-srl.com/admin/ai/analyze`
  - POST `https://atlaspi.cra-srl.com/admin/ai/implement-accepted`
  - Default BASE: `https://atlaspi.cra-srl.com` (pubblico, via nginx)
  - Variabile env `ATLASPI_BASE` può override

### 3. Docs UI pubblico (⚠️ DEVE NON essere accessibile)
- **`static/docs-ui/index.html`** righe 1162-1237: intera sezione "Admin & Insights API" con bottoni "Try it" su GET `/admin/insights`, `/admin/coverage-report`, `/admin/suggestions`
- Chiunque visiti `https://atlaspi.cra-srl.com/docs-ui` può chiamarli
- **Problema**: leak operational state (traffic patterns, data quality reports, AI-generated suggestions)

### 4. Traffico osservato in nginx log (ultimi 100k + storici)
- **IP 87.31.247.202** → 103 hit recenti + 767 storici → operatore admin (= Clirim probabile)
  - Solo GET legittimi (analytics/data, ai/suggestions, ai/status, dev-ips, coverage-report, insights)
  - Nessun POST/DELETE distruttivo da IP esterno
- **Scan attacks** (404): `/admin/config.php`, `/admin/vendor/phpunit/.../eval-stdin.php`, `/admin/index.html`
- **Side finding fuori scope**: `/api/admin/agent/stats` ritorna 500 ripetutamente (probabilmente integrazione CRA-AGENT rotta — annotare per dopo)
- **Cron POST non visibile in nginx log** → significa che daily_ai_check.sh O non è girato recentemente, O passa via Docker direct, O log range troppo corto

### 5. Pattern auth esistente nel repo
- **`src/api/routes/feedback.py:258-273`** — `_check_admin_token(request) -> bool`:
  - Legge `X-Admin-Token` header
  - Confronta con `os.getenv("ATLASPI_ADMIN_TOKEN")` via `hmac.compare_digest`
  - Failsafe: se env vuota → tutti negati
- Usato in: `PATCH /v1/feedback/{id}` (feedback.py:611), `POST /citations/refresh` (citations.py:236)

---

## Design proposto (Option C: layered)

### Core dependency `src/api/deps.py` (NEW FILE)

```python
"""Authentication dependencies for AtlasPI admin endpoints.

# ETHICS: questa logica protegge endpoint che possono modificare/leakare
# stato interno (cache flush, AI suggestions, dev-ip dashboard). Failsafe:
# se ATLASPI_ADMIN_TOKEN non è settato → tutti bloccati (closed-by-default).
# Vedi docs/auto-iter-wave0/wave-1-1/inventory-and-design.md.
"""
import base64
import hmac
import os
from fastapi import HTTPException, Request


def verify_admin(request: Request) -> None:
    """Auth multi-channel: token header OR Basic Auth OR IP allowlist.
    
    Order:
    1. X-Admin-Token header (curl/cron friendly)
    2. Authorization: Basic admin:<token> (browser friendly, auto-cached)
    3. Client IP in ADMIN_ALLOWED_IPS env (CSV, default: "127.0.0.1")
    
    Raises 401 with WWW-Authenticate Basic so browser prompts on first visit.
    """
    expected = os.getenv("ATLASPI_ADMIN_TOKEN", "").strip()
    if not expected:
        # Failsafe — nothing passes if token not configured
        raise HTTPException(
            status_code=401,
            detail="Admin endpoint not configured (ATLASPI_ADMIN_TOKEN unset)",
            headers={"WWW-Authenticate": 'Basic realm="AtlasPI Admin"'},
        )
    
    # 1. X-Admin-Token header (preferred for programmatic)
    token = request.headers.get("X-Admin-Token", "").strip()
    if token and hmac.compare_digest(token.encode("utf-8"), expected.encode("utf-8")):
        return
    
    # 2. Authorization: Basic <b64(user:token)>
    authz = request.headers.get("Authorization", "")
    if authz.startswith("Basic "):
        try:
            decoded = base64.b64decode(authz[6:]).decode("utf-8", errors="replace")
            if ":" in decoded:
                _, password = decoded.split(":", 1)
                if hmac.compare_digest(password.encode("utf-8"), expected.encode("utf-8")):
                    return
        except (ValueError, UnicodeDecodeError):
            pass  # malformed → fall through to 401
    
    # 3. IP allowlist (for cron from localhost, Docker bridge, etc.)
    allowed = os.getenv("ADMIN_ALLOWED_IPS", "127.0.0.1").strip()
    allowed_ips = {ip.strip() for ip in allowed.split(",") if ip.strip()}
    client_host = request.client.host if request.client else ""
    if client_host and client_host in allowed_ips:
        return
    
    # All checks failed
    raise HTTPException(
        status_code=401,
        detail="Admin authentication required",
        headers={"WWW-Authenticate": 'Basic realm="AtlasPI Admin"'},
    )
```

### Application in `src/main.py`

Currently admin routers are included via:
```python
app.include_router(admin_cache.router)
app.include_router(admin_cofounder.router)
app.include_router(admin_insights.router)
app.include_router(analytics.router)  # this has /admin/analytics/* + /admin/dev-ips/*
```

Change to:
```python
from src.api.deps import verify_admin

admin_deps = [Depends(verify_admin)]
app.include_router(admin_cache.router, dependencies=admin_deps)
app.include_router(admin_cofounder.router, dependencies=admin_deps)
app.include_router(admin_insights.router, dependencies=admin_deps)
app.include_router(analytics.router, dependencies=admin_deps)
```

### Cron update `scripts/daily_ai_check.sh`

Aggiungere lettura token + header. Mantengo backward-compat: se env unset, il cron usa IP allowlist (localhost/VPS).

```bash
# (in env section)
TOKEN_HEADER=""
if [ -n "${ATLASPI_ADMIN_TOKEN:-}" ]; then
  TOKEN_HEADER="-H X-Admin-Token: $ATLASPI_ADMIN_TOKEN"
fi

# in curl calls (both POST)
curl -sS $TOKEN_HEADER -X POST "$BASE/admin/ai/analyze" ...
```

Plus on the VPS, load the env from `/opt/cra/.env.atlaspi` at cron time (add `source` line or use systemd cron equivalent).

### Docs-ui cleanup `static/docs-ui/index.html`

**Remove entire section** `id="admin"` (righe ~1162-1237). Replace with comment:
```html
<!-- Admin & Insights API: internal use only, requires authentication.
     Removed from public docs. Contact maintainer for access. -->
```

### Env var nuova `.env.atlaspi` (production)

Aggiungere (opzionale, default = "127.0.0.1"):
```
ADMIN_ALLOWED_IPS=127.0.0.1
```

Per supportare cron via nginx (se IP risulta essere il VPS public 77.81.229.242), aggiungere anche quello:
```
ADMIN_ALLOWED_IPS=127.0.0.1,77.81.229.242
```

Da verificare con test concreto su VPS.

---

## Cosa NON cambio in Wave 1.1 (scope creep)

- Refactor di `_check_admin_token` in feedback.py/citations.py → usano già auth, lasciare per Wave 2
- Aggiungere audit log dedicato per admin attempts → middleware existente già logga; estendere in Wave 2
- Rate limit specifico per admin → Wave 2
- `/api/admin/agent/*` 500 (CRA-AGENT integration) → fuori scope (separato)

---

## Test plan

### Locale (pre-deploy)
1. Senza `ATLASPI_ADMIN_TOKEN` env → tutti `/admin/*` ritornano 401 (failsafe)
2. Con `ATLASPI_ADMIN_TOKEN=test123` + curl `/admin/cache-stats` no auth → 401
3. + curl `-H "X-Admin-Token: test123"` → 200
4. + curl `-u admin:test123` (Basic) → 200
5. + curl con IP non-allowlist → 401
6. + curl da 127.0.0.1 (locale, default allowlist) → 200
7. Public endpoint `/v1/entities/light?limit=10` → 200 (non rotto)
8. `/health` → 200

### Smoke produzione (post-deploy)
1. `curl -i https://atlaspi.cra-srl.com/health` → 200
2. `curl -i https://atlaspi.cra-srl.com/v1/entities/light?limit=10` → 200
3. `curl -i https://atlaspi.cra-srl.com/admin/cache-stats` → 401 con WWW-Authenticate
4. `curl -i https://atlaspi.cra-srl.com/admin/cache-stats -H "X-Admin-Token: <real>"` → 200
5. Browser open `/admin/brief` → prompt Basic Auth → enter user=admin, pass=`<TOKEN>` → load OK
6. JS calls inside dashboard funzionano (Basic Auth cached)
7. Cron simulation: `ssh ... 'bash /opt/cra/atlaspi/scripts/daily_ai_check.sh'` → success
8. `/docs-ui` → admin section sparita

### Visual (chrome-devtools-mcp)
- Open `/admin/brief` con browser autentificato → schermata identica a prima del fix
- Open `/docs-ui` → nessuna sezione admin

---

## Stop conditions specifiche

- **Smoke #4 fail (token corretto ma 401)**: significa env var non leggibile dal container → STOP, debug
- **Smoke #6 fail (browser auth ok ma JS fetch 401)**: significa fetch non sta passando credentials → STOP, fix fetch options
- **Cron simulation fail**: STOP, decidere se cron deve usare token o se basta IP allowlist (verificare quale IP arriva a nginx)
- **Public docs-ui ancora mostra admin section dopo deploy**: cache CDN browser → invalidare manualmente

---

## Rollback

Branch + commit isolato. Se qualcosa va male:
```bash
git revert HEAD
git push
cra-deploy atlaspi
```
Nessuna migration DB, nessun dato modificato — rollback istantaneo.

---

## Files che toccherò

| File | Type | Description |
|---|---|---|
| `src/api/deps.py` | NEW | `verify_admin` dependency |
| `src/main.py` | EDIT | Apply `dependencies=admin_deps` su 4 include_router |
| `static/docs-ui/index.html` | EDIT | Remove "Admin & Insights API" section (~75 lines) |
| `scripts/daily_ai_check.sh` | EDIT | Add `X-Admin-Token` header conditionally |
| `CHANGELOG.md` | EDIT | New entry v6.99.81 |
| `docs/auto-iteration-log.md` | EDIT | Wave 1.1 outcome |

Niente Alembic migration. Niente nuove dipendenze pip. Niente file static rinominati.
