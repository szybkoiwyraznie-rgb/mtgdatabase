# Stan produkcji — AI SFX v2

Ostatnia aktualizacja: **2026-09-27** (sesja `arena/01a0dd2c-mtgdatabase`).

## Aktualna decyzja produktu

Projekt zaczyna nowy flow od zera. Stary ręczny sound design v1 — biblioteki
klocków, bramki odsłuchowe, receptury, tła/hero/kody/instrumenty i stare MP3 —
został przeniesiony do:

```text
archive/v1-curated-sound-design/
```

Nie trafia do aktualnego ZIP-a ani Pages.

Nowy produkt: dla każdej fabuły powstaje **jeden krótki, jednorodny sample**
w stylu „krakanie wron”, „uderzenie dzwonu”, „szczęk bitwy”, „odgłos upadku”.
To nie jest wielowarstwowa scena z tłem i kodą.

## Aktywne ścieżki

- `fabuły270926.csv` — właściciel wrzuca nową kolekcję jako commit.
- `data/catalog.json` — katalog generowany z CSV/TSV przez `scripts/import_collection.py`.
- `data/samples/scenarios.jsonl` — ręcznie pisane małe paczki scenariuszy sampli.
- `data/samples/generated-manifest.jsonl` — manifest generacji scouta ElevenLabs.
- `audio/samples/<id>.mp3` — aktualne wygenerowane sample produkcyjne.
- `site/generated/` — biblioteka HTML do sandboxa i Pages.
- `build/samples-latest.zip` — płaski ZIP z `<id>.mp3`.

## Aktywne narzędzia

```bash
python scripts/validate_stories.py fabuły270926.csv
python scripts/import_collection.py fabuły270926.csv --output data/catalog.json
python scripts/prepare_sample_batch.py --limit 10
python scripts/validate_sample_scenarios.py data/samples/scenarios.jsonl
python scripts/elevenlabs_sample_scout.py --batch b001 --limit 10 --dry-run
ELEVENLABS=... python scripts/elevenlabs_sample_scout.py --batch b001 --limit 10
python scripts/build_site.py --out site/generated
python scripts/build_pack.py --output build/samples-latest.zip
python scripts/serve_site.py --port 3000 --dir site/generated
```

Sekret GitHub/API nazywa się **`ELEVENLABS`**. Nie używać dawnej nazwy
`ELEVENLABS_API_KEY`.

## Workflow

1. Właściciel commituję nowy `fabuły270926.csv`.
2. Agent przygotowuje małą paczkę ok. 10 scenariuszy w
   `data/samples/scenarios.jsonl`; nie iść na ilość kosztem jakości.
3. Po walidacji agent uruchamia scouta ElevenLabs dla tej paczki.
4. Agent buduje/uruchamia bibliotekę HTML do odsłuchu.
5. Po odsłuchu można iterować kolejną paczkę lub regenerować pojedyncze ID.

Workflow GitHub Actions: **Generate sample batch (ElevenLabs)**. Jest manualny,
bo token wystarcza mniej więcej na 40–50 generacji i klucz będzie wymieniany.

## Stan liczbowy po resecie

- Katalog bieżący: 510 fabuł w `data/catalog.json`.
- Scenariusze v2: 0 produkcyjnych wpisów po resecie.
- Wygenerowane sample v2: 0 produkcyjnych MP3 po resecie.
- Stare sygnatury v1: zachowane tylko w archiwum.

## Co robić dalej

- Czekać na nowy CSV/TSV od właściciela albo, jeśli właściciel każe pracować na
  obecnym katalogu, zacząć od `python scripts/prepare_sample_batch.py --limit 10`.
- Pisać scenariusze jako krótkie, jednorodne sample. Unikać słów i konstrukcji:
  `tło`, `hero`, `koda`, `warstwy`, `ambient bed`, `full scene`, `music`.
- Każdy prompt ma zawierać zakaz muzyki i mowy.
- Nie wracać do ręcznych bramek v1 jako głównego flow.

Szczegóły: `docs/ai-sfx-pipeline.md`.
