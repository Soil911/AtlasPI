#!/usr/bin/env bash
# ─── AtlasPI — Smoke test post-deploy ─────────────────────────────
#
# Verifica rapida che i 10 endpoint critici rispondano correttamente.
# Exit code 0 se tutto ok, 1 se almeno un check fallisce.
#
# Uso:
#   ./scripts/smoke_test.sh                          # testa localhost:10100
#   ./scripts/smoke_test.sh https://atlaspi.cra-srl.com
#   BASE_URL=http://staging.example.com ./scripts/smoke_test.sh
#
# Pensato per girare dopo ogni deploy. Da integrare nei workflow CI/CD.

set -euo pipefail

BASE_URL="${1:-${BASE_URL:-http://localhost:10100}}"
FAILED=0
PASSED=0

# ─── Helpers ─────────────────────────────────────────────────────
green() { printf "\033[32m%s\033[0m" "$1"; }
red()   { printf "\033[31m%s\033[0m" "$1"; }
gray()  { printf "\033[90m%s\033[0m" "$1"; }

check() {
  local name="$1"
  local url="$2"
  local expected_code="${3:-200}"
  local jq_assert="${4:-}"

  local response
  local status
  response=$(curl -s -w "\n__STATUS__%{http_code}" --max-time 10 "$url" 2>&1 || true)
  status=$(echo "$response" | grep -oP '__STATUS__\K\d+' | tail -1)
  local body
  body=$(echo "$response" | sed 's/__STATUS__.*//g')

  if [ "$status" != "$expected_code" ]; then
    red "  FAIL"
    echo " $name — got HTTP $status, expected $expected_code"
    gray "    URL: $url"
    echo
    FAILED=$((FAILED + 1))
    return 1
  fi

  # Optional jq assertion on response body
  if [ -n "$jq_assert" ]; then
    if ! echo "$body" | jq -e "$jq_assert" >/dev/null 2>&1; then
      red "  FAIL"
      echo " $name — jq assertion failed: $jq_assert"
      gray "    URL: $url"
      echo
      FAILED=$((FAILED + 1))
      return 1
    fi
  fi

  green "  PASS"
  echo " $name"
  PASSED=$((PASSED + 1))
  return 0
}

# ─── Test battery ────────────────────────────────────────────────
echo "Smoke test: $BASE_URL"
echo

check "root UI"                 "$BASE_URL/"                               200
check "health — ok or degraded" "$BASE_URL/health"                         200  '.status | IN("ok","degraded")'
check "health — DB connected"   "$BASE_URL/health"                         200  '.database | contains("connected")'
check "health — entity_count>0" "$BASE_URL/health"                         200  '.entity_count > 0'
check "stats"                   "$BASE_URL/v1/stats"                       200  '.total_entities > 0'
check "entities list"           "$BASE_URL/v1/entities?limit=5"            200  '.entities | length > 0'
check "snapshot 1500"           "$BASE_URL/v1/snapshot/1500"               200  '.entities | length > 0'
check "aggregation"             "$BASE_URL/v1/aggregation"                 200  '.total > 0'
check "random"                  "$BASE_URL/v1/random"                      200  '.id > 0'
check "nearby Rome 100 AD"      "$BASE_URL/v1/nearby?lat=41.9&lon=12.5&year=100"  200
check "docs"                    "$BASE_URL/docs"                           200
check "openapi spec"            "$BASE_URL/v1/openapi.json"                200  '.info.title == "AtlasPI"'
check "robots.txt"              "$BASE_URL/robots.txt"                     200
check "sitemap.xml"             "$BASE_URL/sitemap.xml"                    200

echo
if [ $FAILED -eq 0 ]; then
  green "OK"
  echo ": $PASSED checks passed"
  exit 0
else
  red "FAIL"
  echo ": $FAILED failed, $PASSED passed"
  exit 1
fi
