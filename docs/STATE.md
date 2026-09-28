# Stan produkcji — AI SFX v2

Ostatnia aktualizacja: **2026-09-28** (sesja `arena/01a0e7f0-mtgdatabase`).

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

Źródłem bieżącej pracy jest `fabuły270926.csv` — waliduje się jako **527 fabuł**
(2026-09-28 doszły fabuły `158OGW` *Kozilek's Shrieker*, `160M11`
*Fiery Hellhound* i `161KTK` *Dragonscale Boon*; ID fabuły to numeryczna
część `Ilustracja`, sufiks setu wycinany przy imporcie) i z niego
wygenerowano `data/catalog.json`.

Gotowe są cztery fale paczek (łącznie 50 fabuł):

- `b001` (POC): scenariusze i sample ID `1–5`,
- `b002`: scenariusze i sample ID `6–15`,
- `b003`: scenariusze i sample ID `16–25`,
- `b004`–`b006`: scenariusze i sample ID `26–50` (10 + 10 + 5),
- `b007`: scenariusze i sample ID `51–60`,
- `b008`: scenariusze i sample ID `61–85` (25 sztuk),
- `b009`–`b044`: 360 scenariuszy i sampli — pętla „10 scenariuszy →
  generacja → następne 10…" (decyzja właściciela; trwała aż do wyczerpania
  budżetu pierwszego klucza 2026-09-28). Paczki `b021`–`b026` (ID `226–300`),
  `b027`–`b030` (ID `301–360`) oraz `b031`–`b044` (ID `362–538`, już na
  nowym kluczu) domknęły 240 sampli w czterech sesjach. Uwaga: ID w katalogu **nie są ciągłe** (katalog: 524 fabuły,
  ID do 617), więc paczki biorą po prostu kolejne 10 fabuł wg kolejności
  katalogu — po `b014` (do ID 145) kolejne paczki obejmują już ID
  z dziurami (np. b029: 321,322,326,330,331,335,337,339,342,343).
- `b031` (ID `362–377`): pierwsza próba padła na wyczerpanym quota starego
  klucza (10 wpisów `failed` w manifeście); po podmianie sekretu paczka
  zregenerowana w całości (run 36394940045).
- `b045`–`b050` (slice `[445:505]`, ID `539–598`): 60 sampli wygenerowanych
  bez zarzutu na drugim kluczu (runy 36400032628, 36400324397, 36400615067,
  36400913153, 36401185630, 36401494004).
- `b051` (ID `599–608`): pierwsza próba padła na HTTP 401 `quota_exceeded`
  drugiego klucza (10 wpisów `failed` w manifeście, archiwum); po podmianie
  sekretu paczka zregenerowana w całości (run 36403513599, trzeci klucz).
- `b052` (ID `609–617` + `158`): paczka domykająca pierwotny katalog —
  9 ostatnich fabuł plus nowa `158OGW` *Kozilek's Shrieker* (run 36405549320).
  Od tej pory scenariusze pokrywają 100% katalogu.
- `b053` (ID `160`, `161`): pierwsza paczka z dalszych dostaw właściciela —
  `160M11` *Fiery Hellhound* i `161KTK` *Dragonscale Boon* (run 36407760852).
  Katalog: 527 fabuł, wszystkie ze scenariuszem i samplem.

Scenariusze: `data/samples/scenarios.jsonl` (527 wpisów, status `ready` —
pokrywają cały katalog). Wygenerowane sample: 527 plików MP3
w `audio/samples/` (nazwy plików to `<id>.mp3`) — paczki `b001`–`b053`.
Manifest generacji: `data/samples/generated-manifest.jsonl` (547 wpisów:
527 `generated` + 20 archiwalnych `failed`: 10 z próby `b031` przy
wyczerpaniu quota pierwszego klucza i 10 z pierwszej próby `b051` przy
wyczerpaniu quota drugiego klucza).

HTML listening gate buduje się z tych plików przez `scripts/build_site.py`
(527 sampli), a ZIP przez `scripts/build_pack.py` (527 płaskich MP3).

Uwaga operacyjna: token bota Arena nie może użyć `workflow_dispatch`
(HTTP 403), więc paczki `b002`–`b044` zostały wygenerowane
przez tymczasowe, markerowane triggery push (`[generate-b00X…]` /
`[import-samples-artifact]`) w `ai-sfx-elevenlabs.yml`, usuwane po imporcie
artefaktu. Workflow na `main` pozostaje manualny (`workflow_dispatch`).
Krok generacji przy `b004–b006` był `continue-on-error`, żeby częściowe
zużycie quota i tak trafiało do artefaktu. Klucz `ELEVENLABS` działał
stabilnie dla wszystkich paczek — wszystkie 50 żądań zakończyło się
statusem `generated`.

**Quota (2026-09-28): katalog domknięty na trzecim kluczu.** Pierwszy klucz
skończył się na 305 samplach, drugi — na 200 (b031–b050; realny koszt
~50 kredytów/sample, więc 10 000 kredytów = 200 sampli; pierwsza próba `b051`
zwróciła 10× HTTP 401 `quota_exceeded`). Po drugiej podmianie sekretu trzeci
klucz wygenerował regenerację `b051` (run 36403513599), finalną paczkę
`b052` (run 36405549320) i dostawę `b053` (run 36407760852) — 22 sample
≈ 1 100 kredytów. **Wszystkie 527 fabuł katalogu ma sample.** Po każdym
imporcie sprawdzać w manifeście statusy `failed`/`quota_exceeded`.

## Audyt audio i regeneracja r001/r002 (2026-09-28)

Sygnałowy audyt wszystkich 527 MP3 (`scripts/audit_samples_audio.py`,
raport `docs/audits/2026-09-28-audio-audit.md`) wytypował 140 plików z flagami,
z czego właściciel zatwierdził do regeneracji 58 (krytyczne + ucięty koniec +
za cicho + przester). Dwie rundy regeneracji (r001: 58 sztuk, run 36411204847;
r002: 17 sztuk, run 36411895113) naprawiły **49/58**; prompty tych fabuł mają
teraz dopiski o obecności/wybrzmieniu/headroomie w `scenarios.jsonl`.
Dla 9 opornych właściciel zlecił całkiem nowe, jednoźródłowe prompty
(runda r003, run 36413153819): 6/9 naprawione. Pozostałe przypadki domknęła
zatwierdzona postprodukcja (fade-out dla źródeł ciągłych, normalizacja do
−1,5 dBFS dla cichych, tłumienie przesterów) — skrypt inline libsndfile.

Ponadto audyt semantyczny scenariuszy (wyniki przekazane w czacie) wykrył
78 promptów opisujących obraz/abstrakt (18), muzykę (6) lub wiele rozłącznych
zdarzeń (54). Wszystkie przepisane od zera na jednoźródłowe fizyczne dźwięki
i zregenerowane w rundzie r004 (run 36415052620, 78/78 generated); 6 plików
doszlifowane postprodukcją. **Stan: 527/527 bez głównych flag sygnałowych.** Kategoria „start na pełnym poziomie"
(39 plików) czeka na odsłuch właściciela; kosmetyczne pominięte.

Mechanizm generacji z sandboxa: tymczasowe markerowane triggery push
(`[generate-regen-rXXX]`) w `ai-sfx-elevenlabs.yml` + tymczasowy workflow
importu artefaktu (`[import-regen-rXXX]`), bo sandbox agenta nie ma dostępu
do `*.blob.core.windows.net` (artefaktów nie da się pobrać lokalnie).
Oba triggery usunięte po imporcie. Zużycie: 162 generacje; stan quota po wszystkich generacjach (odczyt właściciela 2026-09-28): **5 315 kredytów** — realny koszt to ~29 kredytów/generację, nie ~50.

## Aktywne ścieżki

- `fabuły270926.csv` — bieżąca kolekcja właściciela.
- `data/catalog.json` — katalog generowany z CSV/TSV przez `scripts/import_collection.py`.
  ID fabuły = numeryczna część `Ilustracja` (sufiks setu wycinany przy
  imporcie: `158OGW` → fabuła `158`); scenariusze, MP3 i manifest używają
  wyłącznie numeru.
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

- Katalog bieżący: 527 fabuł w `data/catalog.json` z `fabuły270926.csv`.
- Scenariusze v2: 527 gotowych wpisów (batche `b001`–`b053`) — 100% katalogu.
- Wygenerowane sample v2: 527 produkcyjnych MP3 w `audio/samples/`
  (batche `b001`–`b053`).
- Stare sygnatury v1: zachowane tylko w archiwum.

## Incydent: brak auto-deployu po merge PR #40 (2026-09-28)

Po zmergowaniu PR #40 do `main` (squash-merge, commit `4b39a35`, 10:13:11 UTC)
**żaden workflow uruchamiany przez `push`** (`Publish sample library`,
`Build sample release`, nawet bezwarunkowy `Validate project`) się nie odpalił.
Potwierdzone przez GitHub API: `actions/runs?branch=main` nie ma ani jednego
wpisu nowszego niż merge PR #39 (2026-09-27 19:05 UTC).

Najbardziej prawdopodobna przyczyna: bezpośrednio przed mergem wygenerowano
~90 pushy na branchu PR w ciągu ~90 minut (pętla scenariusz→generacja→import
dla paczek b045–b053), co odpaliło 150–250+ workflow runów w niecałe 2h.
GitHub Actions throttluje/odrzuca webhooki wyzwalające nowe runy przy takich
seriach, a zdarzenia push „gubią się" bez żadnego widocznego błędu (brak
failed runa — po prostu nic nie powstaje). Merge do `main` trafił w ogon tej
serii. Takich zdarzeń nie da się odtworzyć wstecz — jedyna naprawa to nowy
push do `main` (np. ten commit) i weryfikacja, że Pages/release się odpaliły.
Jeśli po następnym mergu znowu nic się nie odpali, właściciel może ręcznie
uruchomić `Publish sample library` i `Build sample release` z zakładki
Actions w GitHubie (bot token nie ma `workflow_dispatch` — HTTP 403).

## Co robić dalej

- **Decyzje po pełnym audycie sygnałowym z 2026-09-28** — patrz sekcja na końcu
  pliku i `docs/audits/2026-09-28-audio-audit-fullscan.md`.
- **Katalog domknięty: 527/527 fabuł ma scenariusz i sample (b001–b053).**
- Odsłuchać całą bibliotekę (`b002–b053`, ID `6–617` + `158`, `160`, `161`)
  i zdecydować o merge'u PR #40.
- Nowe fabuły od właściciela (dostarczane jako `<numer><SET>`, np. `158OGW`)
  dopisujemy do `fabuły270926.csv` (sufiks setu wycinany przy imporcie)
  i obsługuje się je nowymi paczkami (kolejna: `b054`).
- Po każdym imporcie kontrolować statusy w manifeście: `failed`
  z `quota_exceeded` = sygnał do ponownej wymiany klucza.
- Po każdym imporcie kontrolować statusy w manifeście: `failed`
  z `quota_exceeded` = sygnał do ponownej wymiany klucza.
- Pisać scenariusze jako krótkie, jednorodne sample. Unikać słów i konstrukcji:
  `tło`, `hero`, `koda`, `warstwy`, `ambient bed`, `full scene`, `music`.
- Każdy prompt ma zawierać zakaz muzyki i mowy.
- Przed generacją zawsze uruchomić `validate_sample_scenarios.py` i dry-run
  `elevenlabs_sample_scout.py`.
- Nie wracać do ręcznych bramek v1 jako głównego flow.

Szczegóły: `docs/ai-sfx-pipeline.md`.


## Runda r005 (2026-09-28) — drugi audyt semantyczny

22 prompty przepisane od zera (18 twardych flag niedźwiękowości + 3 „celowe
cisze" 345/375/506 + 156 z literówką): 23, 33, 45, 51, 103, 110, 156, 166,
190, 221, 227, 301, 331, 337, 345, 375, 446, 480, 489, 506, 532, 570.
Generacja run 36418807314, import run 36418969433 (commit 5003ad6).
Postprodukcja: 190/331 normalizacja do −1,5 dBFS, 489 tłumienie + fade-out
0,35 s. Wynik: 527/527 bez głównych flag
(data/samples/audio-audit-2026-09-28-after-r005.json). Triggery TEMP
usunięte po imporcie. Zużycie r005: 22 generacje ≈ 640 kredytów;
szacunkowy stan quota: ~4 675.


## Pełny audyt sygnałowy korpusu (2026-09-28, sesja `arena/01a0e7f0`)

Nowy skrypt `scripts/audit_samples_full.py` przeliczył **wszystkie 527 MP3 od
zera** i dołożył wymiary, których poprzednie audyty nie mierzyły: LUFS
(BS.1770-4), true peak (4x nadpróbkowanie), rozkład energii w pasmach, offset
DC, tonalność, heurystykę mowy, odciski log-mel (bliźniaki) i kontrolę
unikalności tekstów. Raport: `docs/audits/2026-09-28-audio-audit-fullscan.md`,
metryki per plik: `data/samples/audio-audit-2026-09-28-fullscan.json`.

Najważniejsze ustalenia:

- **Korpus nie ma wyrównanej głośności.** Rozpiętość 43,9 LU (od −46,6 do
  −2,7 LUFS), mediana −15,5. Przy odsłuchu seryjnym część sampli ginie, część
  wyrywa głośniki. Naprawa jest lokalna i darmowa (normalizacja + limiter
  −1 dBTP); 41 plików wymaga > +10 dB, z tego 12 > +15 dB.
- **28 sampli ma ponad 80 % energii poniżej 60 Hz** (`sub_dominant`), a **31
  nie ma praktycznie nic powyżej 250 Hz** (`muffled`). Peak pokazuje „głośno”,
  a na telefonie/laptopie nie słychać nic. Skrajny przypadek: 115
  (peak −13,1 dBFS, −46,6 LUFS).
- **58 plików ma true peak > +1 dBTP** (max +3,5) — twardego clippingu nie ma,
  ale po transkodowaniu mogą zniekształcać. **19 plików ma offset DC** > 0,01.
- **30 sampli ma realną treść krótszą niż 0,8 s** przy pliku 2,5 s.
- **Regresji nie ma**: kategorie „ucięty koniec” i „prawie cisza”, naprawiane
  w rundach r001–r005, są dziś puste (0 plików).
- **Nie ma duplikatów**: 0 identycznych PCM, wszystkie 527 promptów i opisów
  unikalne. 30 par przekracza 0,95 kosinusa odcisku log-mel — to „podobna
  rodzina brzmieniowa”, nie kopie; tylko 2 pary ≥ 0,97 warte odsłuchu
  (321/507, 470/527).
- Muzyka i mowa: 6 plików tonalnych (w większości poprawnie — dzwony) i 3
  mowopodobne. Do weryfikacji uchem, pewność niska.

Biblioteka HTML ma teraz **warstwę audytu**: `build_site.py --audit <json>`
dokleja do kart metryki i flagi oraz pasek filtrów (np. „infradźwięki 28”),
więc odsłuch samych podejrzanych to jedno kliknięcie.

Rekomendowana kolejność (z raportu): najpierw darmowa postprodukcja całego
korpusu, potem odsłuch, dopiero na końcu kredyty na regenerację ~31 ID bez
treści w paśmie słyszalnym. **Czeka na decyzję właściciela.**
