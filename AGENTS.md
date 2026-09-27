# Instrukcje dla agentów — aktualny flow v2

Repozytorium produkuje krótkie sample dźwiękowe do fabuł z `fabuły270926.csv`.
Aktualny produkt to:

```text
audio/samples/<id>.mp3
```

Stary system v1 — tło/hero/koda/instrument, bramki odsłuchowe, biblioteki
klocków, receptury i stare sygnatury — jest wyłącznie archiwum w:

```text
archive/v1-curated-sound-design/
```

Nie rozwijaj go jako głównego flow i nie pakuj jego MP3 do ZIP-a.

## Zasady nadrzędne

1. **Jedna fabuła = jeden krótki sample**. Nie robimy pełnej sceny audio ani
   warstwowego sound designu.
2. Sample ma być jednorodny i rozpoznawalny: np. „krakanie wron”, „uderzenie
   dzwonu”, „szczęk bitwy”, „odgłos upadku”, „krótki trzask zaklęcia”.
3. Każda fabuła dostaje unikalnie opisany i unikalnie wygenerowany sample.
4. Scenariusze pisz małymi paczkami, zwykle ok. 10 sztuk, w
   `data/samples/scenarios.jsonl`. Nie idź na ilość kosztem jakości.
5. Każdy prompt musi zabraniać muzyki i mowy. Unikaj: `background`, `tło`,
   `hero`, `koda`, `warstwa`, `ambient bed`, `full scene`, `cinematic trailer`.
6. ElevenLabs API używa sekretu/env **`ELEVENLABS`**. Nie pytaj właściciela o
   klucz w czacie i nie zapisuj go w repo.
7. Token wystarcza mniej więcej na 40–50 generacji, więc generuj małymi
   paczkami i korzystaj z `--dry-run` przed właściwym scoutem.
8. Pages i sandbox preview pokazują bibliotekę z `audio/samples`, budowaną przez
   `scripts/build_site.py`.
9. ZIP buduje `scripts/build_pack.py`; domyślnie pakuje tylko `audio/samples`.

## Pętla pracy

Po nowym CSV/TSV:

```bash
python scripts/validate_stories.py fabuły270926.csv
python scripts/import_collection.py fabuły270926.csv --output data/catalog.json
python scripts/prepare_sample_batch.py --limit 10
```

Następnie agent dopisuje scenariusze do `data/samples/scenarios.jsonl`.
Format jednego wiersza:

```json
{"story_id":"1","title":"Dunland Crebain","sample_scenario":"ostre krakanie kruka pikującego nad skalnym wąwozem","prompt":"A single sharp raven caw diving over a rocky ravine, close and dark, 2 seconds, no music, no speech.","duration_seconds":2.0,"status":"ready","batch":"b001"}
```

Przed generacją:

```bash
python scripts/validate_sample_scenarios.py data/samples/scenarios.jsonl
python scripts/elevenlabs_sample_scout.py --batch b001 --limit 10 --dry-run
```

Generacja:

```bash
ELEVENLABS=... python scripts/elevenlabs_sample_scout.py --batch b001 --limit 10
```

Publikacja/test:

```bash
python scripts/build_site.py --out site/generated
python scripts/build_pack.py --output build/samples-latest.zip
python scripts/serve_site.py --port 3000 --dir site/generated
```

Walidacja przed commitem:

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

## Raport końcowy

Podaj krótko:

- ile scenariuszy dopisano,
- ile MP3 wygenerowano,
- gdzie jest HTML preview/ZIP,
- czy CI przeszło,
- następny krok.
