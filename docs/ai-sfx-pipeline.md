# AI SFX v2 — krótkie jednorodne sample

To jest aktualna ścieżka produkcji. Stary flow v1 z bibliotekami klocków,
bramkami odsłuchowymi, recepturami, tłem/hero/kodą/instrumentem jest zachowany
w `archive/v1-curated-sound-design/`, ale nie bierze udziału w ZIP-ie ani Pages.

## Produkt

Dla każdej fabuły powstaje dokładnie jeden plik:

```text
audio/samples/<id>.mp3
```

To ma być **krótki, jednorodny sample**, a nie złożona scena audio. Dobre
przykłady:

- „krakanie wron”,
- „pojedyncze uderzenie dzwonu”,
- „szczęk średniowiecznej bitwy”,
- „odgłos upadku zbroi na kamień”,
- „krótki trzask zaklęcia”,
- „plusk wielkiego ciała w wodzie”.

Opis może być unikalny i konkretny dla fabuły, ale prompt ma pilnować jednego
źródła/zdarzenia. Nie prosimy o tło, kodę, muzykę ani pełną scenę.

## Dane scenariuszy

Scenariusze są ręcznie pisane małymi paczkami w:

```text
data/samples/scenarios.jsonl
```

Jeden wiersz JSON na fabułę:

```json
{"story_id":"1","title":"Dunland Crebain","sample_scenario":"ostre krakanie kruka pikującego nad skalnym wąwozem","prompt":"A single sharp raven caw diving over a rocky ravine, close and dark, 2 seconds, no music, no speech.","duration_seconds":2.0,"status":"ready","batch":"b001"}
```

Pola:

- `story_id` — numeryczne ID z katalogu,
- `title` — tytuł karty/fabuły,
- `sample_scenario` — krótki polski opis jednego dźwięku,
- `prompt` — prompt do ElevenLabs, najlepiej po angielsku,
- `duration_seconds` — zwykle 1.5–3.0, dopuszczalnie 0.8–5.0,
- `status` — `draft`, `ready`, `generated`, `rejected`,
- `batch` — etykieta paczki, np. `b001`.

Walidacja:

```bash
python scripts/validate_sample_scenarios.py data/samples/scenarios.jsonl
```

## Przygotowanie małej paczki do pisania

Po wrzuceniu nowego CSV/TSV:

```bash
python scripts/import_collection.py fabuły270926.csv --output data/catalog.json
python scripts/prepare_sample_batch.py --limit 10
```

Druga komenda wypisze następne nieopisane fabuły z narracją. Agent na tej
podstawie dopisuje 10 sensownych scenariuszy do `data/samples/scenarios.jsonl`.

## Scout ElevenLabs

Sekret/env nazywa się:

```text
ELEVENLABS
```

Dry-run bez API:

```bash
python scripts/elevenlabs_sample_scout.py --batch b001 --limit 10 --dry-run
```

Generowanie paczki:

```bash
ELEVENLABS=... python scripts/elevenlabs_sample_scout.py --batch b001 --limit 10
```

Scout:

- bierze tylko `status=ready`,
- pomija istniejące `audio/samples/<id>.mp3`, chyba że podasz `--force`,
- dopisuje manifest do `data/samples/generated-manifest.jsonl`,
- zapisuje MP3 jako `<id>.mp3`.

## HTML biblioteki i ZIP

```bash
python scripts/build_site.py --out site/generated
python scripts/build_pack.py --output build/samples-latest.zip
python scripts/serve_site.py --port 3000 --dir site/generated
```

`build_site.py` kopiuje `audio/samples/*.mp3` do `site/generated/samples/`, więc
biblioteka działa lokalnie w sandboxie i na GitHub Pages.

## GitHub Actions

Workflow ręczny:

```text
Generate sample batch (ElevenLabs)
```

Parametry:

- `batch` — np. `b001`,
- `ids` — opcjonalna lista ID,
- `limit` — domyślnie 10,
- `force` — regeneracja,
- `publish_pages` — deploy Pages tylko z `main`.

Artifact workflow zawiera ZIP, manifest i gotową bibliotekę HTML.

## Zasady jakości promptów

- Jeden prompt = jeden dźwięk, nie scena.
- Zakaz muzyki i mowy w każdym prompcie.
- Unikać „ambient bed”, „cinematic trailer”, „full soundscape”.
- Długość raczej 1.5–3 s; tylko wyjątkowo do 5 s.
- Każdy sample ma być unikalny dla fabuły, ale prosty do rozpoznania.
