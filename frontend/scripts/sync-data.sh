#!/usr/bin/env bash
# Copies pipeline outputs into frontend/src/data/.
# Run from the frontend/ directory: npm run sync-data
# Can be called from a GitHub Actions workflow after the pipeline step completes.

set -euo pipefail

PIPELINE_OUT="$(dirname "$0")/../../pipeline/data/processed"
DEST="$(dirname "$0")/../src/data"

echo "Syncing pipeline outputs → frontend/src/data ..."

cp "$PIPELINE_OUT/spending_by_period.csv"     "$DEST/"
cp "$PIPELINE_OUT/spending_by_category.csv"   "$DEST/"
cp "$PIPELINE_OUT/spending_by_vendor_size.csv" "$DEST/"
cp "$PIPELINE_OUT/metadata.json"              "$DEST/"
cp "$PIPELINE_OUT/parquet/"*.parquet          "$DEST/parquet/"

echo "Done."
echo ""
echo "Files in $DEST:"
ls -lh "$DEST" "$DEST/parquet/"
