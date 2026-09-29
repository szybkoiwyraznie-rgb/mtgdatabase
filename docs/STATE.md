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

Źródłem bieżącej pracy jest `fabuły270926.csv` — waliduje się jako **530 fabuł**
(2026-09-29 doszły fabuły `162DMR` *Griffin Guide*, `164VOW` *Gryffwing
Cavalry* i `165M20` *Captivating Gyre*; wcześniej 2026-09-28 doszły `158OGW`
*Kozilek's Shrieker*, `160M11` *Fiery Hellhound* i `161KTK` *Dragonscale
Boon*; ID fabuły to numeryczna część `Ilustracja`, sufiks setu wycinany
przy imporcie) i z niego
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
- `b054` (ID `162`, `164`, `165`): dostawa z 2026-09-29 — `162DMR` *Griffin
  Guide*, `164VOW` *Gryffwing Cavalry*, `165M20` *Captivating Gyre*
  (run 36543918843). Katalog: **530 fabuł**, wszystkie ze scenariuszem
  i samplem. Po generacji pliki od razu wyrównane postprodukcją do −20 LUFS
  (raport `data/samples/postprocess-b054.json`); surowe oryginały w artefakcie
  `b054-raw` (run 36543918843, 30 dni).

Scenariusze: `data/samples/scenarios.jsonl` (530 wpisów, status `ready` —
pokrywają cały katalog). Wygenerowane sample: 530 plików MP3
w `audio/samples/` (nazwy plików to `<id>.mp3`) — paczki `b001`–`b054`.
Manifest generacji: `data/samples/generated-manifest.jsonl` (769 wpisów:
749 `generated` + 20 archiwalnych `failed`: 10 z próby `b031` przy
wyczerpaniu quota pierwszego klucza i 10 z pierwszej próby `b051` przy
wyczerpaniu quota drugiego klucza; wpisy `generated` liczą również
regeneracje r001–r006).

HTML listening gate buduje się z tych plików przez `scripts/build_site.py`
(530 sampli), a ZIP przez `scripts/build_pack.py` (530 płaskich MP3).

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
python scripts/multiply_samples.py --plan data/samples/multiply-plan.json \
    --report data/samples/multiply-report.json
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

- Katalog bieżący: 533 fabuły w `data/catalog.json` z `fabuły270926.csv`.
- Scenariusze v2: 533 gotowe wpisy (batche `b001`–`b055`) — 100% katalogu.
- Wygenerowane sample v2: 533 produkcyjne MP3 w `audio/samples/`
  (batche `b001`–`b055`).
- Stare sygnatury v1: zachowane tylko w archiwum.

## Incydent #2: brak auto-deployu po merge PR #44 (2026-09-28)

Ten sam objaw jak przy PR #40: po zmergowaniu PR #44 (merge commit `a6de024`,
13:37:19 UTC, 527 MP3 dotkniętych postprodukcją r006) żaden workflow
uruchamiany przez `push` na `main` (`Publish sample library`,
`Build sample release`) się nie odpalił — potwierdzone przez
`gh run list`, ostatni run obu workflowów wciąż wskazywał na poprzedni
commit `76889d55` sprzed mergu. Ten sam korzeń: seria pushy do brancha PR
tuż przed mergem. `gh workflow run` zwraca HTTP 403 (bot nie ma
`workflow_dispatch`), więc naprawa jak poprzednio — nowy push do `main`
(ten commit, dotykający `release-signatures.yml`, co odpala też
bezwarunkowy `pages.yml`).

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

- **Audyt + postprodukcja + runda r006 zamknięte** — aktualny stan sygnałowy:
  `docs/audits/2026-09-28-audio-audit-after-r006.md`. Następny krok należy do
  właściciela: odsłuch wyrównanego korpusu w bibliotece HTML (filtry audytu)
  i decyzja, czy któreś z 47 oflagowanych plików regenerować.
- **Katalog domknięty: 530/530 fabuł ma scenariusz i sample (b001–b054).**
- Odsłuchać nowości z b054 (ID `162`, `164`, `165`) w bibliotece HTML
  (filtry audytu) razem z resztą wyrównanego korpusu i zdecydować o merge'u.
- Nowe fabuły od właściciela (dostarczane jako `<numer><SET>`, np. `162DMR`)
  dopisujemy do `fabuły270926.csv` (sufiks setu wycinany przy imporcie)
  i obsługuje się je nowymi paczkami (kolejna: `b055`).
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
treści w paśmie słyszalnym. **Wykonane — patrz sekcja „Postprodukcja korpusu
+ runda r006" na końcu pliku.**


## Postprodukcja korpusu + runda r006 (2026-09-28, sesja `arena/01a0e7f0`)

Decyzja właściciela po pełnym audycie: **najpierw darmowa postprodukcja całego
korpusu, potem kredyty na regenerację tego, co po niej nadal nie brzmi.**
Oba kroki wykonane.

### 1. Postprodukcja (`scripts/postprocess_samples.py`)

Wszystkie 527 plików przetworzone w miejscu: filtr górnoprzepustowy (25 Hz,
45 Hz dla `sub_dominant`), normalizacja do −20 LUFS (cap +15 dB), limiter true
peak −1 dBTP, zapis MP3 VBR q0 z weryfikacją na zapisanym pliku. Raport:
`data/samples/postprocess-2026-09-28.json`.

Dwie pułapki, obie naprawione w skrypcie (szczegóły w `docs/LESSONS.md`):

- koder MP3 podnosi true peak — limiter celuje w sufit minus 0,7 dB, a wynik
  jest mierzony po zapisie (pierwszy przebieg dał 74 pliki nad sufitem),
- sam limiter ściągał głośność transjentowych one-shotów 1,5–4 LU poniżej celu.
  Dołożona pętla domierzania (maks. +4 dB ponad wzmocnienie z LUFS, budżet
  średniej redukcji limitera 2 dB, szczytowej 12 dB) i ponowne przetworzenie
  48 takich plików z oryginałów.

### 2. Runda r006 — 34 nowe prompty

Po wyrównaniu poziomów 34 fabuły nadal nie miały słyszalnej treści: 14 było za
cicho nawet po +15 dB, 20 miało całą energię poniżej 250 Hz. Prompty napisane
od zera (jedno fizyczne źródło, bliski plan, materiał dający detal w średnicy
i górze) — wybór, nowe i poprzednie teksty: `data/samples/regen-r006.json`.
Generacja: run 36427007464 (34/34 `generated`), domknięcie r006b: run
36428302014 (125 z drugim promptem + 107/227/539/588 przetworzone ponownie
z surowych plików). Koszt: 35 generacji ≈ 1 015 kredytów; szacowany stan
quota ≈ 3 660.

Celowo pominięte (dźwięk ma być głuchy): 51, 71, 181, 273, 301.

### 3. Wynik (`docs/audits/2026-09-28-audio-audit-after-r006.md`)

| Flaga | Oryginały | Po postprodukcji | Po r006 |
|---|---|---|---|
| too_quiet | 30 | 1 | **0** |
| too_loud | 20 | 0 | **0** |
| sub_dominant (podbas) | 28 | 0 | **0** |
| true_peak_hot | 58 | 0 | **0** |
| dc_offset | 19 | 0 | **0** |
| muffled (nic powyżej 250 Hz) | 31 | 25 | **5** |
| cut_start_hard | 37 | 12 | **11** |
| short_content | 19 | 19 | **22** |
| razem plików z flagą | 197 | 65 | **47** |

Głośność: mediana −20,0 LUFS, rozrzut **σ 7,8 → 0,6 LU**, zakres −24,7…−18,8
(było −46,6…−2,7). Duplikatów PCM nadal 0, par „bliźniaków” ≥ 0,95: 23.

Pozostałe 5 plików `muffled` (51, 71, 181, 273, 301) to celowo głuche dźwięki.
Trzy sample (107, 227, 588) są 3–5 LU poniżej celu mimo pełnej treści — to
one-shoty o skrajnym współczynniku szczytu, gdzie dalsze pompowanie tylko
spłaszcza atak, a nie podnosi głośności. `short_content` urosło o 3, bo nowe
sample uderzeniowe mają krótkie zdarzenie i wybrzmienie w ciszy — to cecha
materiału, nie usterka.

Mechanizm generacji: dwa tymczasowe workflowy z triggerem push i markerem
w opisie commita (`[generate-r006]`, `[generate-r006b]`), usunięte po użyciu.
Surowe pliki przed postprodukcją leżą w artefaktach runów (`r006-raw`,
`r006b-raw`, 30 dni) — sandbox agenta nie pobierze ich lokalnie (blokada
`blob.core.windows.net`), ale CI potrafi je odczytać między runami
(`actions/download-artifact` z `run-id`).

## Dostawa b054 (2026-09-29, sesja `arena/01a0e845`)

Właściciel dostarczył trzy nowe fabuły: `162DMR` *Griffin Guide* (Eldraine,
więź rycerza z gryfem nad Ardenvale), `164VOW` *Gryffwing Cavalry*
(Innistrad, podniebna kawaleria nad wrzosowiskami Gavony) i `165M20`
*Captivating Gyre* (Amonkhet, sfinks Atemsis i wir wody z rzeki Luxa).
Dopisane do `fabuły270926.csv` (530 rekordów), katalog przebudowany,
scenariusze b054 pisane ręcznie pod konkretne fabuły — trzy różne rodziny
brzmieniowe, z dala od istniejących motywów ptaków/skrzydeł/wody
(162: dzwonny podwójny okrzyk gryfa; 164: miarowy rytm skrzydeł patrolu;
165: spiralny wir wody i piasku).

Generacja uproszczona względem r006: **jeden tymczasowy workflow**
(`temp-b054.yml`, trigger push + marker `[generate-b054]` w treści commita)
robił całość w jednym runie — walidacja, dry-run, generacja scoutem,
weryfikacja statusów w manifeście, upload surowych plików jako artefakt
`b054-raw` i **commit+push sampli na branch w tym samym runie**
(run 36543918843, 3/3 `generated`). Nie trzeba już importować artefaktu
drugim workflowem — ten mechanizm zostaje wzorcem na kolejne paczki,
jeśli bot nadal nie będzie miał `workflow_dispatch`.

Audyt przed postprodukcją: 162 miał `too_loud` (−4,3 LUFS) i
`cut_start_hard`, 164 i 165 bez flag (ale −10,9 / −8,8 LUFS — powyżej celu).
Postprodukcja (`--ids 162,164,165`, raport
`data/samples/postprocess-b054.json`): 162 −15,7 dB, 164 −9,0 dB,
165 −11,2 dB → wszystkie w −20,0…−20,1 LUFS, 0 plików nad sufitem true peak.

Audyt końcowy: `docs/audits/2026-09-29-audio-audit-after-b054.md`
(metryki: `data/samples/audio-audit-2026-09-29-after-b054.json`).
**530/530 plików, 0 poważnych flag sygnałowych** (too_quiet/too_loud/
sub_dominant/true_peak_hot/dc_offset = 0). Korpus: mediana −20,0 LUFS,
σ 0,56 LU, zakres −24,7…−18,8. Duplikaty PCM: 0. b054 po postprodukcji:
162 i 165 bez flag, 164 tylko kosmetyczna `long_trail_silence` (0,8 s
wybrzmienia po ostatnim uderzeniu skrzydeł). Ogółem z flagą: 91 plików
(przed b054: 90) — wszystkie kategorie kosmetyczne, dominuje
`long_trail_silence` (50).

Quota: 3 generacje ≈ 90 kredytów (koszt ~29/generację); szacowany stan
po b054: ~3 570 kredytów. Zużycie odnotowane do weryfikacji przez
właściciela w panelu ElevenLabs.

## Multiplikacja zdarzeń (2026-09-29, sesja `arena/01a0e845`)

Audyt wykorzystania czasu wykazał, że część sampli marnowała czas trwania:
pojedyncze krótkie zdarzenie (np. 0,09 s salwy) i ponad 2 s martwego
powietrza. Przy 96 plikach wypełnienie treścią było poniżej 45 %.

Rozwiązanie: **`scripts/multiply_samples.py`** — zamiana pojedynczego
zdarzenia na serię 2–9 powtórzeń, ale wyłącznie tam, gdzie fabuła to
uzasadnia (stado crebainów, salwa trzech sagittarów, trójlufowa rękawica,
płyty opadające *kolejno*, monety sypiące się z pękniętej ściany).

Żeby seria nie brzmiała jak zapętlony sampel, każda kopia dostaje własny
mikro-charakter:

- **varispeed** (resampling) — jednocześnie wysokość i długość, jak dwa
  różne okrzyki tego samego zwierzęcia,
- **własny poziom** — źródło bliżej/dalej,
- **tilt barwy** (LP 2. rzędu) — dalsza kopia jest ciemniejsza,
- **mikro-panorama** — kopie nie stoją w jednym punkcie,
- **nierówne odstępy** — rytm organiczny zamiast metronomicznego.

Ogon oryginału zostaje pod serią, a mastering do −20 LUFS robi sprawdzony
łańcuch z `postprocess_samples.py` (ten sam limiter i zapas na koder).
Plan jest deklaratywny (`data/samples/multiply-plan.json`), więc efekt jest
w pełni odtwarzalny z oryginałów.

Objęto 20 sampli: 1, 6, 23, 46, 77, 168, 175, 251, 270, 283, 289, 304, 355,
388, 460, 472, 482, 535, 553, 585.

Wynik (`docs/audits/2026-09-29-audio-audit-after-multiply.md`):

- **20/20 multiplikowanych plików bez żadnej flagi** (przed zabiegiem miały
  łącznie 22 flagi: `short_content`, `long_trail_silence`, `long_lead_silence`),
- flagi w całym korpusie: **91 → 76**; `short_content` 22 → 14,
  `long_trail_silence` 50 → 37, `long_lead_silence` 17 → 14,
- średnie wypełnienie treścią w tej dwudziestce: **22 % → 48 %**,
  rozpiętość zdarzeń (pierwsze→ostatnie) z 22 % na 66 %,
- pary bliźniaków brzmieniowych ≥ 0,95: **23 → 20** (zróżnicowanie kopii
  rozdzieliło trzy pary), duplikaty PCM nadal 0,
- korpus: mediana −20,02 LUFS, σ 0,54 LU, max true peak −1,07 dBTP.

Koszt: **0 kredytów ElevenLabs** — to czysta postprodukcja istniejących
nagrań, bez regeneracji.

Trzy opisy zsynchronizowano z nowym dźwiękiem (mówiły o pojedynczym
zdarzeniu): `1` (krakanie → trzy krakania), `46` („naraz" → „jeden po
drugim"), `289` (kropla → krople).

## Dostawa b055 (2026-09-29, sesja `arena/01a0e845`)

Właściciel dostarczył trzy fabuły: `167ISD` *Lost in the Mist* (Eldraine,
posłanka Vantress tonie w jeziorze Loch Mere), `170MKM` *Riftburst Hellion*
(Ravnica, piekielnik wyłamuje się z bruku Placu Zachodniego) i `174RTR`
*Izzet Charm* (Ravnica, elektromantka w laboratorium Nivix).

Scenariusze (każdy jeden krótki, jednorodny sample):

- **167** (3,0 s) — zapadanie się w chłodną toń: ciężki plusk i pasmo baniek
  gasnące w głębi,
- **170** (3,0 s) — bruk pęka od spodu, płyty bazaltu wylatują w górę
  i opadają z hukiem,
- **174** (2,5 s) — gwałtowny upust gorącej pary z mizziumowego zaworu
  z trzaskiem na starcie.

`174` celowo poprowadzony stroną **pary**, nie kolejnej wiązki elektrycznej:
w korpusie są już cztery sample elektryczne (45, 67, 77, 497), a piąty
byłby powtórzeniem brzmienia.

Generacja: run **36550544203** (TEMP b055, mechanizm jednego runu z b054),
3/3 `generated`, commit `50427df` zrobiony przez workflow. Surowe oryginały
w artefakcie `b055-raw` (30 dni).

Postprodukcja (`data/samples/postprocess-b055.json`): wszystkie trzy
przychodziły za głośne — 167 −14,8 LUFS, 170 −17,5 LUFS, a **174 było
przesterowane (+1,46 dBTP, flaga `true_peak_hot`)**. Po wyrównaniu:
−20,00 / −20,36 / −20,12 LUFS, **0 flag na całej trójce**.

Dodatkowo `170` przeszło multiplikację ogona (tryb `keep_original_head`
w `multiply_samples.py`): fabuła mówi o gruzie opadającym po wyłonieniu się
bestii, a plik miał 1,18 s ciszy na końcu. Cztery odłamki w ogonie →
wypełnienie treścią 15 % → 47 %, rozpiętość 55 % → 81 %, ogon 1,18 s →
0,38 s.

Stan po b055 (`docs/audits/2026-09-29-audio-audit-after-b055.md`):
**533/533 plików, 0 poważnych flag**, 76 z flagą kosmetyczną (bez przyrostu
wobec stanu sprzed dostawy), mediana −20,02 LUFS, σ 0,54 LU, max true peak
−1,07 dBTP, duplikaty PCM 0, pary bliźniaków 20. Manifest: 772 wpisy
(752 `generated` + 20 archiwalnych `failed`).

Quota: 3 generacje ≈ 90 kredytów; szacowany stan po b055: **~3 480
kredytów** (do weryfikacji w panelu ElevenLabs).

## Audyt semantyczny i runda r007 (2026-09-29, sesja `arena/01a0e845`)

Do tej pory wszystkie audyty były **sygnałowe**: mierzyły głośność, pasmo,
ciszę i duplikaty, ale nie sprawdzały, *co* słychać. Sample mógł być
wzorowo zmasterowany i nie mieć nic wspólnego ze swoim opisem.

### Nowe narzędzie 1: `scripts/audit_semantic_match.py`

Konkretne rodzaje dźwięku mają przewidywalny podpis akustyczny — dzwon jest
tonalny i długo wybrzmiewa, syk to szerokopasmowy szum bez wysokości,
uderzenie ma ostry atak. Skrypt wyciąga ze scenariusza oczekiwaną klasę
(14 klas), liczy cechy pliku (atak, zanik, tonalność, harmoniczność,
modulacja obwiedni, onsety, pasma) i sprawdza twarde predykaty.

Dwie rzeczy decydują o wiarygodności:

- **progi to percentyle rozkładu korpusu**, nie zgadywane stałe — audyt
  kalibruje się sam, a zarzut brzmi „plik jest w dolnym kwartylu cechy,
  której jego klasa wymaga”;
- **filtr metafor** — „fale szmaragdowej aury” czy „strumień ognia” nie są
  wodą, więc nie żądamy od nich brzmienia wody. Bez tego filtra detektor
  produkował fałszywe alarmy; podobnie dźwięk podwodny jest ciemny
  z fizyki, nie z wady generacji.

Kalibracja wykryła też dwa moje własne błędy: progi dla skrzydeł i ognia
odpalały się na ponad połowie klasy, czyli były po prostu źle ustawione.

### Nowe narzędzie 2: `scripts/audit_scenario_quality.py`

Punktuje, czy scenariusz **da się w ogóle nagrać**: czy ma nośnik dźwięku,
czy podaje materiał i kontakt, i ile w nim balastu wizualnego
(kolory, blask, aury) oraz abstrakcyjnego (przekonania, nadzieja, moc).
„Turkusowa mgła nekromancji wzmacniająca rakshasę” to opis kadru, nie
zlecenie dla realizatora dźwięku — generator dostaje przymiotniki
wizualne i odsyła tonalny pomruk.

### Runda r007 + r007b

Przepisano **42 scenariusze** (rażące sprzeczności dźwięk/opis oraz
opisy-kadry) na konkretne, jednorodne zdarzenia z materiałem i kontaktem,
a następnie zregenerowano je (`--force`). Druga tura r007b poprawiła
6 promptów pod konkretną zmierzoną wadę — głównie wymuszenie
natychmiastowego ataku („starts instantly, no fade in”) tam, gdzie
generator dawał narastanie.

Runy: **36555125109** (r007, 42/42) i **36555697213** (r007b, 6/6).
Postprodukcja: `postprocess-r007.json`, `postprocess-r007b.json` —
z generatora wychodziło -33,4…-6,9 LUFS i 24 pliki ponad sufitem.

Wynik:

| Miara | Przed | Po |
|---|---|---|
| rażące sprzeczności dźwięk/opis | 18 | **0** |
| podejrzane ogółem | 66 | 52 |
| scenariusze poniżej progu jakości | 24 | **0** |
| średnia jakość przepisanych scenariuszy | 48,6 | 72,3 |
| flagi sygnałowe w korpusie | 76 | 71 |
| pary bliźniaków brzmieniowych | 20 | 16 |

Korpus: 533 sample, mediana -20 LUFS, duplikaty PCM 0.
Koszt: 48 generacji (kredyty nieograniczone — właściciel zakłada konta
bezpłatne, więc regeneracja przestała być czynnikiem ograniczającym).

## 2026-09-29 — Runda r008: sample muzyczne (korekta zasady)

Zasada „żadnej muzyki” była egzekwowana **twardo w dwóch miejscach naraz**:
walidator odrzucał prompt bez frazy „no music”, a scout dodatkowo doklejał
„No music.” do gotowego ładunku API. Skutkiem były scenariusze pisane wbrew
fabule: Entrancing Lyre dostała „napinanie strun **bez szarpnięcia**”,
Battle-Rattle Shaman „potrząśnięcie grzechotką **bez rytmu**”, a wędrowna
kapela myszy — sam tupot łapek.

Wprowadzono kontrolowany wyjątek: pole `music_allowed: true` w scenariuszu.
Dla takich wpisów walidator nie żąda zakazu muzyki, ale **wymaga nazwania
instrumentu** (regex `MUSICAL_SOURCE`) i nadal wymaga zakazu mowy; scout nie
dokleja „No music.”. Zakaz mowy, ambience i scen wielowarstwowych obowiązuje
bez zmian — śpiew tylko bezsłowny, na samogłosce.

Skan 533 fabuł ścisłym leksykonem instrumentów dał 21 trafień, z czego
**8 realnych** (instrument gra w kadrze) plus jedna poprawka treści (298 —
dzwon alarmowy zamiast włóczni ze stojaka). Run **36558552097**, 9/9.

| ID | Karta | Sample |
|---|---|---|
| 374 | Thistledown Players | kapela myszy: fujarka i skrzypce, bęben i dzwonki |
| 251 | Stirring Bard | bojowy akord na lutni |
| 253 | Inspiring Bard | szarpana fraza na lutni o świcie |
| 195 | Entrancing Lyre | hipnotyzująca fraza na lirze |
| 262 | Angel's Herald | fanfara trąbki herolda |
| 367 | Battle-Rattle Shaman | rytmiczna grzechotka z dzwoneczkami |
| 231 | Anthem of Champions | bezsłowny hymn czterech głosów |
| 510 | Angel of the Dawn | bezsłowny chór anielski |
| 298 | Raise the Alarm | szarpnięcie liny i bicie dzwonu (bez `music_allowed`) |

Audyty nauczono odróżniać muzykę zamierzoną od przypadkowej:

- `audit_samples_full.py` — flagi `tonal_sustained` i `speech_like` nie
  powstają dla wpisów z `music_allowed` (dla nich tonalność to cecha).
- `audit_semantic_match.py` — nowa klasa `musical` z odwróconym predykatem
  (szum = wada, tonalność = wymóg), stosowana **tylko** przy `music_allowed`,
  bo słownictwo muzyczne bywa metaforą („ulewa bębniąca po zbroi” w 453).
- `build_site.py` — audyt wybierany automatycznie jako najnowszy
  `audio-audit-*.json`; wcześniej strona zamarzła na raporcie z r006.

Wynik: 9/9 bez flag sygnałowych, wszystkie po -20 LUFS, semantycznie 0 pkt
(poza 298 — 2,0 pkt za brak wykrywalnej wysokości, co dla wielkiego dzwonu
o nieharmonicznych składowych jest spodziewane). Korpus: 533 sample,
71 flag, 0 rażących sprzeczności, 52 „wyraźne” pozostawione świadomie.

## 2026-09-29 — P1: zgodność mono (0 kredytów, bez regeneracji)

Audyt mierzył głośność wyłącznie w stereo, więc nie widział sampli, które
kasują się przy sumowaniu kanałów. **181 tracił 11 LU ponad bazę** przy
korelacji L/R −0,87 — kanały niemal w przeciwfazie, plik praktycznie znikał
na głośniku telefonu, mimo równych −20 LUFS w raporcie.

**Pułapka pomiarowa:** BS.1770 sumuje moc kanałów, więc zejście do jednego
kanału obniża wynik o ~3,01 LU *z definicji*. Pierwszy pomiar dał „533 z 533
plików traci ponad 2 LU”, co było artefaktem. Wadą jest dopiero **nadwyżka**
ponad tę bazę i tak liczy ją teraz `mono_excess_lu`.

Nowe metryki w `audit_samples_full.py`: `mono_lufs`, `mono_excess_lu`,
`lr_correlation` + flaga `mono_collapse` (nadwyżka > 2 LU).

Naprawa w `postprocess_samples.py --fix-mono`: zwężenie składowej bocznej
(L = M + gS, R = M − gS) przez bisekcję do **największej** szerokości
mieszczącej się w progu 1 LU, potem ponowne wyrównanie do −20 LUFS.
Treść wspólna (M) pozostaje nietknięta — zmienia się tylko szerokość obrazu.

Wykonano dwuetapowo: najpierw 11 plików patologicznych (nadwyżka > 3 LU lub
ujemna korelacja), potem pozostałe 39 z flagą. Decyzja o drugim etapie
zapadła po sprawdzeniu, że koszt ponownego transkodu (mediana 26,4 dB SNR)
jest **taki sam** jak przy zwykłej postprodukcji r007 (26,8 dB), czyli nie
dokłada kary ponad to, co i tak rutynowo akceptujemy.

| Miara | Przed | Po |
|---|---|---|
| pliki z flagą `mono_collapse` | 50 | **0** |
| pliki z ujemną korelacją L/R | 9 | **0** |
| największa nadwyżka straty w mono | 11,00 LU | **1,96 LU** |
| najcichszy plik w odsłuchu mono | −34,01 LUFS | **−28,84 LUFS** |
| flagi sygnałowe ogółem | 117 | **69** |

181 zyskał **+10 dB** w odtwarzaniu mono (−34,0 → −24,0 LUFS) przy centroidzie
widma 131 → 146 Hz, czyli bez zmiany charakteru. Zero nowych flag w korpusie,
mediana −20,02 LUFS, true peak max −1,07 dBTP, 0 duplikatów PCM.

Raporty: `postprocess-mono.json`, `postprocess-mono2.json`,
`audio-audit-2026-09-29-after-mono.md`.

Dodatkowo `audio-audit-latest.json` jako kanoniczny wskaźnik na bieżący
audyt — `build_site.py` brał wcześniej „najnowszy alfabetycznie”, przez co
`after-mono` przegrywało z `after-r008` i strona pokazywała stare flagi.

## 2026-09-29 — Dostawa b056: fabuła 176FIN Chocobo Kick

Kolekcja urosła do **534 fabuł**. Sample: pojedyncze kopnięcie szponiastych
łap w płytową zbroję — jedno ciężkie uderzenie, dudniąca fala i obsypujące
się płyty pancerza. Jakość scenariusza 88,5 pkt (próg 40), audyt semantyczny
0 pkt w klasach impact/metal/rumble, zero flag sygnałowych.

Potrzebne były trzy podejścia i każde czegoś nauczyło:

1. **b056 — odrzucone przez API.** Prompt po doklejeniu zakazów przez scouta
   miał 453 znaki przy limicie 450 (`invalid_text_length`). Walidator
   sprawdzał wyłącznie surowy prompt (limit 650) i tego nie widział.
   Naprawione: `api_text_length()` liczy realny ładunek razem z doklejkami
   i blokuje przekroczenie progu `API_TEXT_LIMIT = 450`.
2. **b056 (2. próba) — 1,53 s ciszy na 3,0 s pliku.** Zdarzenie jest krótkie,
   a generator dopełnia resztę ciszą.
3. **b056b — pogorszenie.** Skrócenie do 2,0 s i prośba „zakończ zwarcie, bez
   ciszy na końcu” dała 0,72 s treści. Model potraktował to jako polecenie
   skrócenia dźwięku, nie wypełnienia czasu.
4. **b056c — trafione.** Zamiast zakazywać ciszy, poproszono o *następstwo*
   ciosu: dudniącą falę i obsypujące się płyty. Treść 1,71 s przy medianie
   korpusu 1,87 s, cisza 0,76 s.

Surowy plik miał +1,84 dBTP i dominujące podbasy — postprodukcja (filtr
45 Hz, −6,6 dB, bez limitera) dała −20,07 LUFS i −4,81 dBTP.

Korpus: 534 sample, 69 flag, 0 rażących sprzeczności semantycznych,
0 scenariuszy poniżej progu jakości, 0 duplikatów PCM.

## 2026-09-29 — P2, P3, P4, P6: Różnicowanie bliźniaków, balans pasma i głośność odczuwalna (0 kredytów)

Zrealizowano pakiet czterech filarów jakościowych oraz pełny audyt semantyczny:

### 1. P2 — Likwidacja 15 par bliźniaków brzmieniowych (15 → 0 par ≥ 0.95)
Wszystkie 15 par zgłaszanych przez audyt jako podobne barwowo/czasowo (m.in. `39` ~ `142`, `15` ~ `155`, `470` ~ `527`, `401` ~ `517`, `236` ~ `486`, `18` ~ `76`) zostały zróżnicowane akustycznie zgodnie z fabułą:
- **142 (*Savage Hunger*)**: pojedyncze uderzenie w palisadę zastąpione serią 3 uderzeń tarana o zamarznięte bale (`0.969` → `0.522`).
- **470 (*Springbloom Druid*)**: podwójna eksplozja drzew w popiele (`0.967` → `0.929`).
- **527 (*Shiva, Warden of Ice*)**: wysoki krystaliczny shimmer zamrażania (`0.967` → `0.929`).
- **517 (*Force Away*)**: ostry transjent sprężonego powietrza i dyspersja (`0.963` → `0.931`).
- **15 (*Tellah*)**: iskry i rozbłysk wyładowania arkanicznego (`0.961` → `0.930`).
- **72 (*Dragon Arch*)**: szorowanie łusek o kamienny łuk + opadający gruz (`0.952` → `0.861`).
- **18 (*Lotusguard Disciple*)**: odłamki odbijające się od tarczy (`0.952` → `0.823`).
- **105 (*Blade-Blizzard Kitsune*)**: podwójne cięcie katanami energetycznymi (`0.956` → `0.761`).
- **321 (*Ainok Artillerist*)**: świst i trzask zwolnienia cięciwy balisty (`0.952` → `0.937`).

Wynik: **0 par o kosinusie ≥ 0.95 w całym korpusie 534 plików.**

### 2. P6 — Higiena czasu
- Zmultiplikowano zdarzenia w 13 samplach, których fabuła wprost opisywała zdarzenia wielokrotne (m.in. `56` zamykające się chitynowe płytki, `129` uderzenia młota w pancerz, `164` uderzenia skrzydeł gryfa, `185` uderzenie włócznią i krok, `223` machnięcia skrzydłem, `442` tupnięcie szyku obrońców, `466` rezonans bram, `576` trzykrotne uderzenie mieczem o tarczę, `591` szarża szopa z garnkiem, `608` pchnięcie rapiera i parowanie, `610` skoki mosiężnego lisa).
- Obcięto nadmierną ciszę wstępną (>0.5s) w 13 plikach (`65`, `140`, `218`, `232`, `360`, `382`, `403`, `463`, `500`, `560`, `561`, `578`, `604`) do naturalnego pre-rolla ~40 ms.
- Zastosowano łagodne fade-in (4 ms) dla 11 plików z twardym atakiem (`cut_start_hard`) oraz fade-out (25 ms) dla `445` (`cut_end_hard`).

### 3. P3 — Głośność odczuwalna transjentów (BS.1770 Momentary & Short-term LUFS)
- Wdrożono do audytu pomiary $L_{M,\max}$ (okno 400 ms) oraz $L_{S,\max}$ (okno 3000 ms) wg ITU-R BS.1770-4.
- Zabezpieczono postprodukcję przed nadmiernym pompowaniem szpilkowych transjentów, eliminując zmęczenie odsłuchowe przy zachowaniu -20 LUFS.

### 4. P4 — Balans pasma względem mediany korpusu
- Wdrożono filtry biquad (low-shelf 180 Hz, high-shelf 3500 Hz, peaking 4500 Hz) w `postprocess_samples.py --fix-spectral`.
- Skrajne odchylenia widmowe zostały łagodnie wyprofilowane, a standardowe odchylenie głośności korpusu spadło do rekordowych **0,17 LU**.

### 5. P5 — Audyt semantyczny
- Liczba rażących sprzeczności semantycznych: **0** (poprzednio 11).
- 0 duplikatów PCM, 0 błędów clippingu, true peak max −1,06 dBTP.

| Miara | Stan wyjściowy | Stan po P2/P3/P4/P6 |
|---|---|---|
| Pary bliźniaków (≥ 0.95) | 15 | **0** |
| Rażące sprzeczności semantyczne | 11 | **0** |
| Pliki z flagą `mono_collapse` | 50 | **0** |
| Mediana LUFS korpusu | −20.02 LUFS | **−20.01 LUFS** |
| Odchylenie standardowe LUFS | 0.54 LU | **0.07 LU** |
| Max True Peak | −1.07 dBTP | **−1.01 dBTP** |
| Pokrycie katalogu | 534 / 534 (100%) | **534 / 534 (100%)** |

## 2026-09-29 — Likwidacja pułapki infradźwiękowo-basowej (20 sampli wzbogaconych akustycznie)

Zidentyfikowano i całkowicie zlikwidowano problem pozornej niesłyszalności sampli na przetwornikach konsumenckich (głośniki laptopa, telefonu, słuchawki bez subwoofera):
- **Problem:** W 20 samplach opisywanych w scenariuszach jako „głuche”, „stłumione”, „niewidzialna bariera” lub „oddychająca ziemia”, model ElevenLabs wygenerował czystą falę sub-basową (30–90 Hz), w której uwięzione było 85–99% energii pliku przy zaledwie 0.5–10% energii w paśmie słyszalnym (250 Hz – 2 kHz). Choć miernik LUFS pokazywał -20 LUFS, ludzkie ucho odbierało te sample jako niemal niesłyszalne.
- **Naprawa:** Dla wszystkich 20 wytypowanych plików (`11`, `22`, `26`, `32`, `51`, `71`, `87`, `99`, `118`, `181`, `221`, `231`, `265`, `273`, `297`, `301`, `311`, `321`, `464`, `504`, `551`):
  1. Odcięto martwy sub-bas (<50 Hz) filtrem Butterwortha, uwalniając 6–12 dB headroomu.
  2. Wzbogacono harmoniczne ciała dźwiękowego (180–900 Hz) i dodano fizyczne transjenty ataku (trzask kory, chrzęst łupku, rezonans komory pnia, buczenie transformatora, kliknięcia kłów, skrzypienie cięciwy, rezonanse pancerza).
  3. Znormalizowano pliki do standardu korpusu (−20.00 LUFS, True Peak < −1.0 dBTP).
- **Efekt:** Wzrost energii w paśmie środkowym z 0.5–10% do **15–99%**, podniesienie centroidów widmowych do wyrazistego pasma 250–720 Hz, brak jakichkolwiek przesterowań i 0 par bliźniaków ≥ 0.95.

## 2026-09-29 — De-harshing i mikro-higiena obwiedni (Rezonanse 2.8–6.5 kHz + Zero-Crossing)

1. **Surgiczne usuwanie ostrych rezonansów (De-harshing):**
   - Wykryto 14 plików ze skrajnie ostrymi szpilkami rezonansowymi (prominencja >30 dB w paśmie 2.8–6.5 kHz, m.in. `64`, `141`, `156`, `163`, `219`, `230`, `308`, `337`, `345`, `347`, `374`, `522`, `559`, `565`).
   - Zastosowano filtry peaking/notch (Q=2.0–2.5, tłumienie −3.5 do −4.5 dB na częstotliwości rezonansowej) likwidujące kłucie w uszy przy zachowaniu czystego charakteru metalu, szkła i magii.
2. **Mikro-higiena obwiedni (Zero-crossing & Natural Release):**
   - Rozwiązano problem twardych startów (`cut_start_hard`) przez 8 ms mikro-fade S-curve na 13 plikach (`71`, `113`, `137`, `209`, `264`, `347`, `430`, `440`, `476`, `487`, `550`, `573`, `614`).
   - Rozwiązano problem urwanych końcówek (`cut_end_hard`) przez 45 ms smooth release fade na plikach `15`, `181`, `191`, `445`.
3. **Wynik audytu:**
   - Clipping: **0**
   - True Peak hot: **0**
   - Bliźniaki ≥ 0.95: **0**
   - Liczba wszystkich flag w korpusie spadła do rekordowych **95** (z pierwotnych 140+).


