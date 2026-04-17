#!/usr/bin/env bash
# AtlasPI — daily AI check (analyze + implement-accepted + smoke test)
#
# Intended to run via cron:
#   0 4 * * * /opt/cra/atlaspi/scripts/daily_ai_check.sh >> /var/log/atlaspi-daily.log 2>&1
#
# Pipeline:
#   1. POST /admin/ai/analyze — generate new suggestions from current state
#   2. POST /admin/ai/implement-accepted — run handlers for all accepted suggestions
#   3. Smoke test — verify no endpoint regressed
#
# If any step fails, the log line is prefixed with [ERROR] and the script
# exits non-zero (so cron can email the operator).

set -euo pipefail

BASE="${ATLASPI_BASE:-https://atlaspi.cra-srl.com}"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "=== AtlasPI daily AI check @ $TIMESTAMP ==="

# 1. Analyze
echo "[1/3] POST $BASE/admin/ai/analyze"
ANALYZE_RESULT="$(curl -sS -X POST "$BASE/admin/ai/analyze" -w '\nHTTP_CODE:%{http_code}\n')"
ANALYZE_CODE="$(echo "$ANALYZE_RESULT" | grep -oP 'HTTP_CODE:\K[0-9]+' || echo 0)"
if [ "$ANALYZE_CODE" != "200" ]; then
  echo "[ERROR] analyze returned HTTP $ANALYZE_CODE"
  echo "$ANALYZE_RESULT"
  exit 1
fi
ANALYZE_JSON="$(echo "$ANALYZE_RESULT" | sed 's/HTTP_CODE:.*//')"
if command -v jq >/dev/null 2>&1; then
  TOTAL_NEW="$(echo "$ANALYZE_JSON" | jq -r '.total_new_suggestions // 0' 2>/dev/null || echo '?')"
else
  TOTAL_NEW="?"
fi
echo "    -> $TOTAL_NEW new suggestions generated"

# 2. Implement accepted
echo "[2/3] POST $BASE/admin/ai/implement-accepted"
IMPL_RESULT="$(curl -sS -X POST "$BASE/admin/ai/implement-accepted" -w '\nHTTP_CODE:%{http_code}\n')"
IMPL_CODE="$(echo "$IMPL_RESULT" | grep -oP 'HTTP_CODE:\K[0-9]+' || echo 0)"
if [ "$IMPL_CODE" != "200" ]; then
  echo "[ERROR] implement-accepted returned HTTP $IMPL_CODE"
  echo "$IMPL_RESULT"
  exit 1
fi
IMPL_JSON="$(echo "$IMPL_RESULT" | sed 's/HTTP_CODE:.*//')"
if command -v jq >/dev/null 2>&1; then
  PROCESSED="$(echo "$IMPL_JSON" | jq -r '"processed=\(.processed // 0) implemented=\(.implemented // 0) briefing=\(.briefing // 0) failed=\(.failed // 0)"' 2>/dev/null || echo '?')"
else
  PROCESSED="(jq unavailable — install to see detail)"
fi
echo "    -> $PROCESSED"

# 3. Smoke test (optional — comment out if slow in cron)
echo "[3/3] Smoke test"
if command -v python3 >/dev/null && [ -f /opt/cra/atlaspi/scripts/smoke_test_endpoints.py ]; then
  cd /opt/cra/atlaspi
  python3 -m scripts.smoke_test_endpoints --base="$BASE" 2>&1 | tail -5 | sed 's/^/    /'
else
  echo "    [skip] smoke test script not available"
fi

echo "=== daily AI check done @ $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
