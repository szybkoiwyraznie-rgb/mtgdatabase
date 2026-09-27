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
- `b004`–`b006`: scenariusze i sample ID `26–50` (10 + 10 + 5),
- `b007`: scenariusze i sample ID `51–60`,
- `b008`: scenariusze i sample ID `61–85` (25 sztuk),
- `b009`–`b014`: scenariusze i sample ID `86–145` (6 paczek po 10 —
  rytm „10 scenariuszy → generacja → 10 scenariuszy → generacja",
  decyzja właściciela; trwa aż do wyczerpania budżetu).

Scenariusze: `data/samples/scenarios.jsonl` (145 wpisów, status `ready`).
Wygenerowane sample: `audio/samples/1.mp3` … `145.mp3` (145 plików MP3).
Manifest generacji: `data/samples/generated-manifest.jsonl` (145 wpisów
`generated`).

HTML listening gate buduje się z tych plików przez `scripts/build_site.py`
(145 sampli), a ZIP przez `scripts/build_pack.py` (płaskie `1.mp3` … `145.mp3`).

Uwaga operacyjna: token bota Arena nie może użyć `workflow_dispatch`
(HTTP 403), więc paczki `b002`–`b014` zostały wygenerowane
przez tymczasowe, markerowane triggery push (`[generate-b00X…]` /
`[import-samples-artifact]`) w `ai-sfx-elevenlabs.yml`, usuwane po imporcie
artefaktu. Workflow na `main` pozostaje manualny (`workflow_dispatch`).
Krok generacji przy `b004–b006` był `continue-on-error`, żeby częściowe
zużycie quota i tak trafiało do artefaktu. Klucz `ELEVENLABS` działał
stabilnie dla wszystkich paczek — wszystkie 50 żądań zakończyło się
statusem `generated`.

**Quota (korekta właściciela, 2026-09-27): konto ma budżet 10 000
tokenów**, z czego po 50 samplach wykorzystano **1 145** (~23 tokeny na
sample). Po paczce `b014` (145 sampli) zużycie to szacunkowo ~3 325
tokenów. Zapas wystarcza na ~290 kolejnych sampli (katalog ma 524 fabuły,
zostało 379). Uwaga: pokrycie
całego katalogu (524 fabuły) wymagałoby łącznie ~12 000 tokenów, więc
zmiana konta/klucza będzie potrzebna mniej więcej około ID ~430. Wcześniejszy
szacunek „40–50 generacji" był mocno zaniżony.

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
2. Agent przygotowuje paczkę 10 scenariuszy, generuje przez scouta,
   i tak w pętli aż do wyczerpania budżetu (decyzja właściciela);
   jakość scenariuszy nienegocjowalna — ręcznie pisane, unikalne
   i zróżnicowane brzmieniowo.
3. Przed wydaniem quota agent uruchamia walidator i dry-run scouta.
4. Po walidacji agent uruchamia scouta ElevenLabs dla tej paczki.
5. Agent buduje/uruchamia bibliotekę HTML do odsłuchu.
6. Po odsłuchu można iterować kolejną paczkę lub regenerować pojedyncze ID.

Workflow GitHub Actions: **Generate sample batch (ElevenLabs)**. Jest manualny,
żeby generacja zużywająca tokeny (budżet konta: 10 000 tokenów, ~23/sample)
nie odpalała się bez kontroli właściciela.

## Stan liczbowy

- Katalog bieżący: 524 fabuły w `data/catalog.json` z `fabuły270926.csv`.
- Scenariusze v2: 145 gotowych wpisów (ID `1–145`, batche `b001`–`b014`).
- Wygenerowane sample v2: 145 produkcyjnych MP3
  (`audio/samples/1.mp3` … `145.mp3`).
- Stare sygnatury v1: zachowane tylko w archiwum.

## Co robić dalej

- Odsłuchać paczki `b002–b006` (ID `6–50`) w bibliotece HTML i zdecydować
  o merge'u PR.
- Kolejna paczka: `b015` (ID `146–155`) i dalej w pętli paczek po 10 aż do
  wyczerpania budżetu (~290 sampli zapasu; katalog: 379 fabuł do końca).
- Pisać scenariusze jako krótkie, jednorodne sample. Unikać słów i konstrukcji:
  `tło`, `hero`, `koda`, `warstwy`, `ambient bed`, `full scene`, `music`.
- Każdy prompt ma zawierać zakaz muzyki i mowy.
- Przed generacją zawsze uruchomić `validate_sample_scenarios.py` i dry-run
  `elevenlabs_sample_scout.py`.
- Nie wracać do ręcznych bramek v1 jako głównego flow.

Szczegóły: `docs/ai-sfx-pipeline.md`.
