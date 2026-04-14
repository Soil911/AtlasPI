#!/usr/bin/env bash
# scripts/fetch_raw_data.sh
# Scarica i dataset esterni necessari alla pipeline di boundary enrichment.
# I raw non sono committati nel repo per via delle dimensioni (~200MB totali).
#
# Uso:
#   bash scripts/fetch_raw_data.sh
#
# Dopo questo script puoi rieseguire:
#   python -m src.ingestion.enrich_all_boundaries
#
# Licenze:
#   - aourednik/historical-basemaps: CC BY 4.0 (attribuzione richiesta)
#   - Natural Earth: public domain (nessuna attribuzione richiesta ma gradita)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW_DIR="$ROOT_DIR/data/raw"
mkdir -p "$RAW_DIR"

echo "=== AtlasPI raw data fetch ==="
echo

# ── aourednik/historical-basemaps ─────────────────────────────────────────
AOU_DIR="$RAW_DIR/aourednik-historical-basemaps"
if [ -d "$AOU_DIR/.git" ]; then
  echo "[aourednik] gia' presente in $AOU_DIR — pull in corso..."
  git -C "$AOU_DIR" pull --ff-only || echo "  (warning: pull fallito, uso snapshot locale)"
else
  echo "[aourednik] clonazione (CC BY 4.0) da aourednik/historical-basemaps..."
  git clone --depth 1 \
    https://github.com/aourednik/historical-basemaps.git \
    "$AOU_DIR"
fi
echo

# ── Natural Earth 10m admin boundaries ────────────────────────────────────
NE_DIR="$RAW_DIR/natural_earth"
NE_URL="https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip"
NE_ZIP="$NE_DIR/ne_10m_admin_0_countries.zip"

if [ -f "$NE_DIR/ne_10m_admin_0_countries.shp" ]; then
  echo "[natural_earth] shapefile gia' presente in $NE_DIR"
else
  echo "[natural_earth] download ne_10m_admin_0_countries (public domain)..."
  mkdir -p "$NE_DIR"
  curl -fsSL "$NE_URL" -o "$NE_ZIP"
  (cd "$NE_DIR" && unzip -o ne_10m_admin_0_countries.zip)
  rm -f "$NE_ZIP"
fi
echo

echo "=== Fetch completato ==="
echo "Ora puoi eseguire:"
echo "  python -m src.ingestion.natural_earth_import"
echo "  python -m src.ingestion.enrich_all_boundaries"
