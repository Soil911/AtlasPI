#!/bin/bash
# v6.79 audit v4 Round 9: nightly Wikidata drift check
#
# Esegue il drift check Wikidata in modalità --offline (cache locale)
# ogni notte alle 03:00 UTC. Genera report in /tmp/atlaspi_drift_<date>.md
# e logga summary su syslog (tag: atlaspi-drift) per alerting eventuale.
#
# Setup:
#   sudo cp scripts/nightly_drift_check.sh /etc/cron.daily/atlaspi-drift
#   sudo chmod +x /etc/cron.daily/atlaspi-drift
# OR
#   sudo crontab -e
#   0 3 * * * /opt/cra/atlaspi/scripts/nightly_drift_check.sh
#
# Variables:
#   ATLASPI_CONTAINER (default: cra-atlaspi)
#   DRIFT_REPORT_DIR (default: /var/log/atlaspi)

set -euo pipefail

CONTAINER="${ATLASPI_CONTAINER:-cra-atlaspi}"
REPORT_DIR="${DRIFT_REPORT_DIR:-/var/log/atlaspi}"
DATE=$(date +%Y%m%d)
REPORT="${REPORT_DIR}/drift_${DATE}.md"
DATAFILE="${REPORT_DIR}/drift_${DATE}.json"
PATCHES="${REPORT_DIR}/drift_${DATE}_autofix.json"

mkdir -p "$REPORT_DIR"

logger -t atlaspi-drift "Starting nightly drift check ($(date -Iseconds))"

# Run drift check in --offline mode (uses cached Wikidata data, no network calls)
# If cache is stale (> 7 days), re-fetch online
if docker exec "$CONTAINER" test -f /app/scripts/wikidata_cache/.last_refresh; then
    LAST_REFRESH=$(docker exec "$CONTAINER" cat /app/scripts/wikidata_cache/.last_refresh 2>/dev/null || echo "0")
    NOW=$(date +%s)
    AGE=$((NOW - LAST_REFRESH))
    if [ "$AGE" -gt 604800 ]; then
        logger -t atlaspi-drift "Cache > 7 days old, refreshing..."
        docker exec "$CONTAINER" python -m scripts.wikidata_drift_check \
            --refresh-cache 2>&1 | logger -t atlaspi-drift
    fi
fi

# Run the drift check
docker exec "$CONTAINER" python -m scripts.wikidata_drift_check \
    --offline \
    --out-report "/tmp/$(basename "$REPORT")" \
    --out-data "/tmp/$(basename "$DATAFILE")" \
    --out-patches "/tmp/$(basename "$PATCHES")" \
    2>&1 | tee -a "$REPORT_DIR/cron.log" | logger -t atlaspi-drift

# Copy outputs to host
docker cp "$CONTAINER:/tmp/$(basename "$REPORT")" "$REPORT" 2>/dev/null || true
docker cp "$CONTAINER:/tmp/$(basename "$DATAFILE")" "$DATAFILE" 2>/dev/null || true
docker cp "$CONTAINER:/tmp/$(basename "$PATCHES")" "$PATCHES" 2>/dev/null || true

# Compare with previous day: if HIGH count increased, log alert
YESTERDAY=$(date -d 'yesterday' +%Y%m%d)
PREV_REPORT="${REPORT_DIR}/drift_${YESTERDAY}.md"
if [ -f "$PREV_REPORT" ]; then
    TODAY_HIGH=$(grep -oP '^- HIGH: \K\d+' "$REPORT" 2>/dev/null || echo "0")
    YESTERDAY_HIGH=$(grep -oP '^- HIGH: \K\d+' "$PREV_REPORT" 2>/dev/null || echo "0")
    DIFF=$((TODAY_HIGH - YESTERDAY_HIGH))
    if [ "$DIFF" -gt 0 ]; then
        logger -t atlaspi-drift "ALERT: HIGH drift count increased by $DIFF (yesterday=$YESTERDAY_HIGH, today=$TODAY_HIGH)"
    fi
fi

# Cleanup old reports (keep 30 days)
find "$REPORT_DIR" -name "drift_*.md" -mtime +30 -delete 2>/dev/null || true
find "$REPORT_DIR" -name "drift_*.json" -mtime +30 -delete 2>/dev/null || true

logger -t atlaspi-drift "Nightly drift check completed"
