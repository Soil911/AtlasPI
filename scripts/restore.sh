#!/usr/bin/env bash
# ─── AtlasPI — Restore database da backup ─────────────────────────
#
# Uso:
#   ./scripts/restore.sh <backup_file>
#
# Esempi:
#   ./scripts/restore.sh backup/atlaspi-2026-04-14-0300.db.gz
#   ./scripts/restore.sh backup/atlaspi-2026-04-14-0300.sql.gz
#
# ATTENZIONE: sovrascrive il database corrente. Richiede conferma.

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Uso: $0 <backup_file>" >&2
  exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
  echo "[restore] ERRORE: file non trovato: $BACKUP_FILE" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

if [ -f ".env" ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | grep -v '^$' | xargs -d '\n' -I{} echo "{}" | tr '\n' ' ') 2>/dev/null || true
fi

DATABASE_URL="${DATABASE_URL:-sqlite:///data/atlaspi.db}"

# Conferma esplicita prima di sovrascrivere
echo "[restore] Stai per ripristinare: $BACKUP_FILE"
echo "[restore] Target DATABASE_URL: $DATABASE_URL"
read -r -p "[restore] CONFERMA? (type 'yes' to proceed): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "[restore] annullato."
  exit 0
fi

if [[ "$DATABASE_URL" == sqlite* ]]; then
  DB_PATH="${DATABASE_URL#sqlite:///}"
  TMP="$(mktemp)"

  if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" > "$TMP"
  else
    cp "$BACKUP_FILE" "$TMP"
  fi

  # Backup del DB corrente prima di sovrascriverlo
  if [ -f "$DB_PATH" ]; then
    SAFE="${DB_PATH}.pre-restore.$(date +%s)"
    cp "$DB_PATH" "$SAFE"
    echo "[restore] DB corrente salvato in: $SAFE"
  fi

  mv "$TMP" "$DB_PATH"
  echo "[restore] SQLite ripristinato in $DB_PATH"

elif [[ "$DATABASE_URL" == postgresql* ]]; then
  if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | psql "$DATABASE_URL"
  else
    psql "$DATABASE_URL" < "$BACKUP_FILE"
  fi
  echo "[restore] PostgreSQL ripristinato"

else
  echo "[restore] ERRORE: DATABASE_URL non supportato: $DATABASE_URL" >&2
  exit 1
fi

echo "[restore] OK — riavvia l'app per rileggere i dati."
