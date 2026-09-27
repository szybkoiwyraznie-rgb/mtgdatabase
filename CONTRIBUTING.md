# Współpraca

Przeczytaj `AGENTS.md` przed każdą zmianą. Aktualny produkt to krótkie sample
v2 w `audio/samples/<id>.mp3`; stary system v1 jest archiwum.

## Przed rozpoczęciem

Sprawdź stan gałęzi i uruchom podstawowe walidacje. Nie wracaj do archiwalnych
bramek/receptur jako głównego flow.

## Przed zakończeniem

```bash
python -m compileall -q scripts
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/validate_stories.py fabuły270926.csv
python scripts/import_collection.py fabuły270926.csv --output /tmp/catalog.json
python scripts/validate_sample_scenarios.py data/samples/scenarios.jsonl --catalog data/catalog.json
python scripts/build_pack.py --output /tmp/samples.zip
python scripts/build_site.py --out /tmp/site-out
git diff --check
```

Nie commituj sekretów ani plików `.env`. Sekret API ElevenLabs nazywa się
`ELEVENLABS` i ma być ustawiony w GitHub Secrets albo lokalnym środowisku.
