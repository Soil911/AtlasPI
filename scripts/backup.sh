#!/usr/bin/env bash
# ─── AtlasPI — Backup database (SQLite + PostgreSQL auto-detect) ──
#
# Uso:
#   ./scripts/backup.sh [output_dir]
#
# Output:
#   backup/atlaspi-YYYY-MM-DD-HHMM.{db,sql.gz}
#
# Configurazione via env var (rispetta gli stessi di .env):
#   DATABASE_URL    — sqlite:///path/to/atlaspi.db | postgresql://...
#   BACKUP_DIR      — default: ./backup
#   BACKUP_RETAIN   — numero di backup da tenere (default 14)
#
# Da schedulare con cron (es: daily 03:00):
#   0 3 * * * /opt/atlaspi/scripts/backup.sh >> /var/log/atlaspi-backup.log 2>&1

set -euo pipefail

# ─── Setup ────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

# Carica .env se presente (non fatale se manca)
if [ -f ".env" ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | grep -v '^$' | xargs -d '\n' -I{} echo "{}" | tr '\n' ' ') 2>/dev/null || true
fi

BACKUP_DIR="${1:-${BACKUP_DIR:-./backup}}"
BACKUP_RETAIN="${BACKUP_RETAIN:-14}"
DATABASE_URL="${DATABASE_URL:-sqlite:///data/atlaspi.db}"
TIMESTAMP="$(date +%Y-%m-%d-%H%M)"

mkdir -p "$BACKUP_DIR"

# ─── Dispatch per tipo DB ────────────────────────────────────────
if [[ "$DATABASE_URL" == sqlite* ]]; then
  # Estrai path del file .db da "sqlite:///path/to/atlaspi.db"
  DB_PATH="${DATABASE_URL#sqlite:///}"
  if [ ! -f "$DB_PATH" ]; then
    echo "[backup] ERRORE: file SQLite non trovato: $DB_PATH" >&2
    exit 1
  fi

  OUT="$BACKUP_DIR/atlaspi-$TIMESTAMP.db"
  echo "[backup] SQLite -> $OUT"

  # .backup e' safe anche con DB live (WAL mode)
  sqlite3 "$DB_PATH" ".backup '$OUT'"
  gzip -f "$OUT"
  echo "[backup] completato: ${OUT}.gz ($(du -h "${OUT}.gz" | cut -f1))"

elif [[ "$DATABASE_URL" == postgresql* ]]; then
  OUT="$BACKUP_DIR/atlaspi-$TIMESTAMP.sql.gz"
  echo "[backup] PostgreSQL -> $OUT"

  # pg_dump leggera variabili da DATABASE_URL nativamente (>=11)
  pg_dump "$DATABASE_URL" --no-owner --no-privileges --clean --if-exists \
    | gzip -c > "$OUT"
  echo "[backup] completato: $OUT ($(du -h "$OUT" | cut -f1))"

else
  echo "[backup] ERRORE: DATABASE_URL non supportato: $DATABASE_URL" >&2
  exit 1
fi

# ─── Retention: tieni solo gli ultimi N backup ───────────────────
cd "$BACKUP_DIR"
# shellcheck disable=SC2012
# Elimina piu' vecchi di BACKUP_RETAIN, ordinati per nome (timestamp)
ls -1t atlaspi-*.gz 2>/dev/null | tail -n "+$((BACKUP_RETAIN + 1))" | while read -r old; do
  rm -f "$old"
  echo "[backup] retention: rimosso $old"
done

echo "[backup] OK ($(ls atlaspi-*.gz 2>/dev/null | wc -l) backup conservati)"
