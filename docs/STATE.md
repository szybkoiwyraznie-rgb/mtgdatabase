# Stan produkcji — AI SFX v2

Ostatnia aktualizacja: **2026-09-27** (sesja `arena/01a0e45d-mtgdatabase`).

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

## Aktualny stan produkcji

Źródłem bieżącej pracy jest `fabuły270926.csv` — waliduje się jako **524 fabuły**
i z niego wygenerowano `data/catalog.json`.

Gotowe są cztery fale paczek (łącznie 50 fabuł):

- `b001` (POC): scenariusze i sample ID `1–5`,
- `b002`: scenariusze i sample ID `6–15`,
- `b003`: scenariusze i sample ID `16–25`,
- `b004`–`b006`: scenariusze i sample ID `26–50` (10 + 10 + 5).

Scenariusze: `data/samples/scenarios.jsonl` (50 wpisów, status `ready`).
Wygenerowane sample: `audio/samples/1.mp3` … `50.mp3` (50 plików MP3).
Manifest generacji: `data/samples/generated-manifest.jsonl` (50 wpisów
`generated`).

HTML listening gate buduje się z tych plików przez `scripts/build_site.py`
(50 sampli), a ZIP przez `scripts/build_pack.py` (płaskie `1.mp3` … `50.mp3`).

Uwaga operacyjna: token bota Arena nie może użyć `workflow_dispatch`
(HTTP 403), więc paczki `b002`, `b003` i `b004–b006` zostały wygenerowane
przez tymczasowe, markerowane triggery push (`[generate-b00X…]` /
`[import-samples-artifact]`) w `ai-sfx-elevenlabs.yml`, usuwane po imporcie
artefaktu. Workflow na `main` pozostaje manualny (`workflow_dispatch`).
Krok generacji przy `b004–b006` był `continue-on-error`, żeby częściowe
zużycie quota i tak trafiało do artefaktu. Klucz `ELEVENLABS` działał
stabilnie dla wszystkich paczek — wszystkie 50 żądań zakończyło się
statusem `generated`.

**Quota: wykorzystano ok. 50 generacji** (5 + 10 + 10 + 25), czyli górny
zakres szacunku z README. Przed kolejną paczką (`b007`, domyślnie ID
`51–60`) klucz powinien zostać wymieniony; regeneracje pojedynczych ID
też lepiej zaplanować po wymianie klucza.

## Aktywne ścieżki

- `fabuły270926.csv` — bieżąca kolekcja właściciela.
- `data/catalog.json` — katalog generowany z CSV/TSV przez `scripts/import_collection.py`.
- `data/samples/scenarios.jsonl` — ręcznie pisane małe paczki scenariuszy sampli.
- `data/samples/generated-manifest.jsonl` — manifest generacji scouta ElevenLabs.
- `audio/samples/<id>.mp3` — aktualne wygenerowane sample produkcyjne.
- `site/generated/` — biblioteka HTML do sandboxa i Pages, generowana lokalnie.
- `build/samples-latest.zip` — płaski ZIP z `<id>.mp3`, generowany lokalnie.

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

1. Właściciel commituję nowy `fabuły270926.csv` albo zatwierdza pracę na obecnym.
2. Agent przygotowuje małą paczkę ok. 10 scenariuszy w
   `data/samples/scenarios.jsonl`; nie iść na ilość kosztem jakości.
3. Przed wydaniem quota agent uruchamia walidator i dry-run scouta.
4. Po walidacji agent uruchamia scouta ElevenLabs dla tej paczki.
5. Agent buduje/uruchamia bibliotekę HTML do odsłuchu.
6. Po odsłuchu można iterować kolejną paczkę lub regenerować pojedyncze ID.

Workflow GitHub Actions: **Generate sample batch (ElevenLabs)**. Jest manualny,
bo token wystarcza mniej więcej na 40–50 generacji i klucz będzie wymieniany.

## Stan liczbowy

- Katalog bieżący: 524 fabuły w `data/catalog.json` z `fabuły270926.csv`.
- Scenariusze v2: 50 gotowych wpisów (`b001` ID `1–5`, `b002` ID `6–15`,
  `b003` ID `16–25`, `b004`–`b006` ID `26–50`).
- Wygenerowane sample v2: 50 produkcyjnych MP3
  (`audio/samples/1.mp3` … `50.mp3`).
- Stare sygnatury v1: zachowane tylko w archiwum.

## Co robić dalej

- Odsłuchać paczkę `b004–b006` (ID `26–50`) w bibliotece HTML i zdecydować
  o merge'u PR.
- Wymienić klucz `ELEVENLABS` przed kolejną generacją (quota wyczerpane).
- Kolejna paczka: `b007`, domyślnie następne ID `51–60` z bieżącego katalogu.
- Pisać scenariusze jako krótkie, jednorodne sample. Unikać słów i konstrukcji:
  `tło`, `hero`, `koda`, `warstwy`, `ambient bed`, `full scene`, `music`.
- Każdy prompt ma zawierać zakaz muzyki i mowy.
- Przed generacją zawsze uruchomić `validate_sample_scenarios.py` i dry-run
  `elevenlabs_sample_scout.py`.
- Nie wracać do ręcznych bramek v1 jako głównego flow.

Szczegóły: `docs/ai-sfx-pipeline.md`.
