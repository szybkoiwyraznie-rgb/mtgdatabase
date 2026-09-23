#!/bin/bash
# Odtwarza panel odsłuchowy po resecie sandboxa (build/ i procesy nie przetrwalają tur).
# Uruchamiaj: bash scripts/preview.sh  — serwuje na porcie 8000.
# Wymaga tylko stdlib python3 (merge_catalog/build_site nie potrzebują venv).
set -e
cd "$(dirname "$0")/.."
python3 scripts/merge_catalog.py --collection kolekcja.csv --versions data/versions.json --output /tmp/catalog.json
python3 scripts/build_site.py --catalog /tmp/catalog.json --output build/site --audio-root legacy/source/jingle_output
echo '{"feedbackEndpoint": ""}' > build/site/data/config.json
echo "[preview] strona zbudowana, serwuję na porcie 8000"
exec python3 -m http.server 8000 --bind 0.0.0.0 --directory "$PWD/build/site"
