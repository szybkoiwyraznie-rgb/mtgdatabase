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
źródła/zdarzenia. Nie prosimy o tło, kodę ani pełną scenę. Muzyka jest
dozwolona tam, gdzie karta ją implikuje (lutnia, chór, róg bojowy, taniec) —
deklaruje się ją polem `music_allowed` i nazwanym instrumentem (decyzja
właściciela 2026-10-05; bezwzględny zakaz muzyki był błędem dokumentacji).

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
- Zakaz mowy w każdym prompcie; muzyka dozwolona przez `music_allowed`
  z nazwanym instrumentem/źródłem.
- Unikać „ambient bed”, „cinematic trailer”, „full soundscape”.
- Długość 3–5 s dla sampli archetypowych (cel właściciela z 2026-10-05:
  dźwięk rozpoznawalny jak ryk smoka, dzwon czy krakanie); starsze wpisy
  mają 2–2,5 s i będą przepisywane partiami.
- Każdy sample ma być unikalny dla fabuły, ale prosty do rozpoznania.

## Audyt korpusu

Dwa skrypty, oba tylko **raportują** — żaden nic nie nadpisuje:

```bash
python scripts/audit_samples_audio.py --output /tmp/audio-audit.json
python scripts/audit_samples_full.py \
    --json data/samples/audio-audit-<data>-fullscan.json \
    --markdown docs/audits/<data>-audio-audit-fullscan.md \
    --previous data/samples/audio-audit-<poprzedni>.json
```

- `audit_samples_audio.py` — szybki skan obwiedni: ucięty start/koniec, cisza,
  peak, rozjazd długości.
- `audit_samples_full.py` — pełny skan: LUFS (BS.1770-4), true peak,
  rozkład energii w pasmach (infradźwięki, brak treści powyżej 250 Hz),
  offset DC, tonalność i heurystyka mowy (prompty zabraniają muzyki i mowy),
  odciski log-mel do wykrywania bliźniaków oraz kontrola unikalności tekstów
  scenariuszy. Generuje JSON z metrykami i gotowy raport Markdown.

Zależności audytu (`numpy`, `scipy`, `soundfile`) nie są potrzebne w CI —
instaluje się je lokalnie:

```bash
python -m venv .venv && .venv/bin/pip install numpy scipy soundfile
```

## Postprodukcja korpusu

```bash
python scripts/postprocess_samples.py --dry-run
python scripts/postprocess_samples.py --report data/samples/postprocess-<data>.json
```

Jedyny skrypt, który **nadpisuje** pliki w `audio/samples/` (albo pisze do
`--out-dir`). Łańcuch na plik:

1. filtr górnoprzepustowy Butterwortha 2. rzędu (zerofazowy `sosfiltfilt`):
   25 Hz dla wszystkich, 45 Hz dla ID oflagowanych w audycie jako
   `sub_dominant` — usuwa offset DC i infradźwięki, które zjadały headroom,
2. pomiar LUFS (BS.1770-4) i wzmocnienie do wspólnego celu `--target-lufs`
   (domyślnie −20) z limitem `--max-gain-db` (domyślnie +15 dB; wyżej wychodzi
   szum tła zamiast treści),
3. limiter true peak na obwiedni z nadpróbkowaniem 4× (sufit `--ceiling-dbtp`,
   domyślnie −1 dBTP),
4. zapis MP3 VBR jakość 0 i **weryfikacja na zapisanym pliku** (ponowny pomiar
   LUFS/true peak + SNR transkodowania), do 3 prób z rosnącym zapasem.

Ważne: koder MP3 podbija true peak o kilka dziesiątych dB, więc limiter celuje
w sufit pomniejszony o `--encoder-headroom` (domyślnie 0,7 dB). Bez tego przy
sufticie −1 dBTP część plików wychodzi nad sufit.

Operacja jest odwracalna przez `git checkout -- audio/samples`. Nie wolno
transkodować już przetworzonych plików ponownie — każda korekta parametrów
zaczyna się od przywrócenia oryginałów z gita.

### Warstwa audytu w bibliotece HTML

`build_site.py --audit <plik.json>` (domyślnie ostatni fullscan) dokłada do
każdej karty metryki (LUFS, peak, true peak, długość treści) i kolorowe flagi,
a nad listą pasek filtrów. Dzięki temu odsłuch „tylko podejrzanych” to jedno
kliknięcie zamiast szukania po ID. Brak pliku audytu = biblioteka bez flag,
jak wcześniej.
