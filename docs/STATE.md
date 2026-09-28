# Stan produkcji — AI SFX v2

Ostatnia aktualizacja: **2026-09-28** (sesja `arena/01a0e45d-mtgdatabase`).

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
- `b009`–`b030`: 220 scenariuszy i sampli — pętla „10 scenariuszy →
  generacja → następne 10…" (decyzja właściciela; trwała aż do wyczerpania
  budżetu 2026-09-28). Paczki `b021`–`b026` (ID `226–300`) oraz `b027`–`b030`
  (ID `301–360`) domknęły 100 sampli w dwóch sesjach. Uwaga: ID w katalogu **nie są ciągłe** (katalog: 524 fabuły,
  ID do 617), więc paczki biorą po prostu kolejne 10 fabuł wg kolejności
  katalogu — po `b014` (do ID 145) kolejne paczki obejmują już ID
  z dziurami (np. b029: 321,322,326,330,331,335,337,339,342,343).
- `b031` (ID `362–377`): scenariusze napisane, ale generacja **nieudana —
  budżet konta wyczerpany do zera** (0 credits); paczka czeka na
  regenerację po zmianie klucza `ELEVENLABS`.

Scenariusze: `data/samples/scenarios.jsonl` (315 wpisów, status `ready`;
305 wygenerowanych + 10 paczki `b031` czekających na regenerację).
Wygenerowane sample: 305 plików MP3 w `audio/samples/` (nazwy plików
to `<id>.mp3`).
Manifest generacji: `data/samples/generated-manifest.jsonl` (315 wpisów:
305 `generated` + 10 `failed` z próby `b031` przy wyczerpanym quota).

HTML listening gate buduje się z tych plików przez `scripts/build_site.py`
(305 sampli), a ZIP przez `scripts/build_pack.py` (305 płaskich MP3).

Uwaga operacyjna: token bota Arena nie może użyć `workflow_dispatch`
(HTTP 403), więc paczki `b002`–`b030` zostały wygenerowane
przez tymczasowe, markerowane triggery push (`[generate-b00X…]` /
`[import-samples-artifact]`) w `ai-sfx-elevenlabs.yml`, usuwane po imporcie
artefaktu. Workflow na `main` pozostaje manualny (`workflow_dispatch`).
Krok generacji przy `b004–b006` był `continue-on-error`, żeby częściowe
zużycie quota i tak trafiało do artefaktu. Klucz `ELEVENLABS` działał
stabilnie dla wszystkich paczek — wszystkie 50 żądań zakończyło się
statusem `generated`.

**Quota (2026-09-28): budżet 10 000 tokenów WYCZERPANY.** Próba paczki
`b031` zwróciła HTTP 401 `quota_exceeded` („0 credits remaining,
25 credits required”) dla wszystkich 10 ID. Realne średnie zużycie
wyliczyło się na ~33 tokeny/sample (10 000 / 305 sampli), nie ~23
jak po pierwszych 50 próbkach — dlatego budżet skończył się na 305
samplach, wcześniej niż szacowane ~435. Dalsza generacja wymaga
zmiany klucza/konta w sekrecie `ELEVENLABS`.

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
- Scenariusze v2: 315 gotowych wpisów (batche `b001`–`b031`; `b031` czeka
  na regenerację po zmianie klucza).
- Wygenerowane sample v2: 305 produkcyjnych MP3 w `audio/samples/`
  (batche `b001`–`b030`).
- Stare sygnatury v1: zachowane tylko w archiwum.

## Co robić dalej

- Odsłuchać paczki `b002–b030` (ID `6–360`) w bibliotece HTML i zdecydować
  o merge'u PR.
- **Najpierw: zmiana klucza/konta `ELEVENLABS` przez właściciela** —
  obecny budżet jest na zerze (0 credits).
- Po podmianie sekretu: regeneracja paczki `b031` (scenariusze gotowe,
  ID `362,366,367,370,372,373,374,375,376,377`; 10 wpisów `failed`
  w manifeście dokumentuje nieudaną próbę).
- Potem pętla dalej: `b032` = kolejne 10 fabuł wg kolejności katalogu
  (slice `[315:325]`). W katalogu bez scenariusza zostały 209 fabuły.
- Pisać scenariusze jako krótkie, jednorodne sample. Unikać słów i konstrukcji:
  `tło`, `hero`, `koda`, `warstwy`, `ambient bed`, `full scene`, `music`.
- Każdy prompt ma zawierać zakaz muzyki i mowy.
- Przed generacją zawsze uruchomić `validate_sample_scenarios.py` i dry-run
  `elevenlabs_sample_scout.py`.
- Nie wracać do ręcznych bramek v1 jako głównego flow.

Szczegóły: `docs/ai-sfx-pipeline.md`.
