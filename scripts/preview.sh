#!/bin/bash
# Build and serve the v2 sample library locally.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/import_collection.py kolekcja.csv --output data/catalog.json
python3 scripts/build_site.py --out site/generated
echo "[preview] sample library on http://0.0.0.0:3000"
exec python3 scripts/serve_site.py --port 3000 --dir site/generated
