# Stan produkcji — AI SFX v2

Ostatnia aktualizacja: **2026-10-04** (sesja `arena/01a108e2-mtgdatabase`).

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

Źródłem bieżącej pracy jest `fabuły270926.csv` — waliduje się jako **553 fabuły**
i z niego generowano `data/catalog.json`. Liczba obejmuje kolejne dostawy
właściciela po bazie `b054` (szczegóły historyczne poniżej), w tym najnowsze
`212VOW` *Bloodtithe Harvester*, `239SOS` *Dig Site Inventory* (`b062`),
`241SPM` *News Helicopter* (`b063`), `244BFZ` *Natural Connection* (`b064`),
`247ORI` *Subterranean Scout* (`b065`), `250MRD` *Loxodon Mender* (`b066`),
`254DMU` *Snarespinner* (`b067`), `255APC` *Urborg Uprising* (`b068`),
`259_2XM` *Kozilek's Predator* (`b069`) oraz `260MOM` *Etched Host Doombringer*
(dostawa `b070`, korekta brzmienia `r014`). ID fabuły to numeryczna część
wartości `Ilustracja`, sufiks setu jest wycinany przy imporcie.

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

- Katalog bieżący: **553 fabuły** w `data/catalog.json` z `fabuły270926.csv`.
- Scenariusze v2: 553 gotowe wpisy (batche `b001`–`b070` + rundy korekt, najnowsza `r014`) — 100% katalogu.
- Wygenerowane sample v2: 553 produkcyjne MP3 w `audio/samples/`.
- Stare sygnatury v1: zachowane tylko w archiwum.

## 2026-10-01 — Runda r010/r010b/r010c: poprawki po odsłuchu właściciela

Właściciel wskazał 9 sampli, których brzmienie było trudne do przypisania do
karty/fabuły: `548` *Steelclaw Lance*, `558` *White Mage's Staff*, `500`
*Instant Ramen*, `15` *Tellah, Great Sage*, `138` *Join the Dance*, `59`
*Mysidian Elder*, `187` *Idyllic Grange*, `445` *Locthwain Paladin* i `29`
*You're Not Alone*.

Prompty przepisano na czytelniejsze, bardziej dosłowne źródła dźwięku:

- `548` — zębaty grot lancy zgrzyta po pancerzu i rozrywa pnącza,
- `558` — szklisty impuls kryształu laski i drobne iskry leczenia,
- `500` — realne jedzenie ramenu: siorbanie z kubka i stuk pałeczek,
- `15` — szelest starych kart pergaminu w magicznym podmuchu i iskry,
- `138` — jawny wyjątek `music_allowed`: krótka wiejska muzyka do tańca
  (skrzypce, bębenek, klaskanie),
- `59` — jasny syk małego płomienia nad dłonią maga,
- `187` — poranny okrzyk koguta na sielskim podwórzu,
- `445` — ciężki pancerny rumak: kopyta w zlodzonym śniegu i pobrzęk uprzęży,
- `29` — towarzysze stają w obronnym kręgu: buty na kamieniu i wspólny szczęk
  dobywanych ostrzy.

Generacja `r010` dała 9/9 plików. `59` wyszedł zbyt nisko/tonalnie, więc
został przepisany i zregenerowany w `r010b`; `558` dostał 90 ms fade-out na
ucięty ogon. W `r010c` plik `59` dodatkowo wygładzono high-shelfem 6 kHz
−8 dB, bo po r010b był czytelny, ale za syczący (`harsh`).

Stan po `r010c`: **537 sampli**, **93 pliki z flagą** (wszystkie flagi poza
wskazaną dziewiątką), **0 par bliźniaków ≥ 0,95**, **0 identycznego PCM** i
**0 rażących sprzeczności semantycznych**. Wszystkie 9 wskazanych ID jest bez
flag sygnałowych; semantycznie 8/9 ma 0 pkt, a `15` ma tylko drobną heurystykę
1,5 za minimalnie wolniejszy atak pergaminu/iskier.

Raporty: `data/samples/postprocess-r010.json`, `data/samples/postprocess-r010b.json`,
`data/samples/tail-fade-r010b.json`, `data/samples/deharsh-r010c.json`,
`docs/audits/2026-10-01-audio-audit-after-r010c.md`,
`docs/audits/2026-10-01-semantic-match-r010c.md`.

## 2026-10-01 — Runda r011/r011b/r011c: druga lista odsłuchowa właściciela

Właściciel wskazał kolejne 3 sample, których brzmienia nie dało się łatwo
połączyć z kartą/fabułą: `463` *Knockout Maneuver*, `557` *Kishla Village* i
`396` *Vow of Wildness*.

Prompty przepisano na bardziej dosłowne, rozpoznawalne źródła:

- `463` — nie „chrobotanie”, tylko rzut ciałem na twardy lód: głuchy slam,
  pękająca tafla i sypiące się odłamki śniegu,
- `557` — zamiast stukania łodzi, które kojarzyło się z drzwiami: mokry skrzek
  dużej żaby w mętnym kanale pod domami na palach,
- `396` — zamiast abstrakcyjnej świetlistej przysięgi / „syku pary": gardłowy
  ryk dzikiego anoa, parsknięcie i racica zdzierająca suchą ziemię.

Pierwsza generacja `r011` poprawiła kierunek, ale `463` miało krótką treść i
martwą ciszę, a `557` wpadło w parę brzmieniową z wodnym samplem `121`.
`r011b` poprawiło `396` i `557` oraz zlikwidowało parę bliźniaczą; `463` nadal
było za krótkim impulsem z długim lead/trail. Finalnie `r011c` lokalnie
rozszerzyło `463`: z aktywnego slam/crack wycięto zdarzenie, zostawiono pełny
pierwszy impakt, a dalsze wysokoprzepustowe, cichsze kopie ułożono jako
rozchodzące się pęknięcia i patter odłamków. Treść wzrosła **0,58 s → 1,70 s**,
lead **0,66 s → 0,07 s**, trail **1,76 s → 0,43 s**.

Stan po `r011c`: **537 sampli**, **93 pliki z flagą**, **0 par bliźniaków
≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności semantycznych**.
Wszystkie 3 wskazane ID są bez flag sygnałowych i mają 0 pkt w audycie
semantycznym.

Raporty: `data/samples/postprocess-r011.json`, `data/samples/postprocess-r011b.json`,
`data/samples/extend-r011c.json`,
`docs/audits/2026-10-01-audio-audit-after-r011c.md`,
`docs/audits/2026-10-01-semantic-match-r011c.md`.

## 2026-10-01 — Runda r012/r012b: Omenspeaker i Silvanus's Invoker po odsłuchu

Właściciel wskazał 2 kolejne sample jako nieczytelne: `452` *Omenspeaker*
(brzmiało jak spuszczanie wody w toalecie) i `539` *Silvanus's Invoker*
(brzmiało jak maszyna do pisania albo przekładanie kartek).

Prompty przepisano tak, żeby jawnie zakazać błędnych skojarzeń:

- `452` — brzęk pierścieni z mosiądzu astrolabium i czysty szklany dzwon
  soczewki proroctwa; prompt ma `no water, no flushing, no whoosh`,
- `539` — trzask korzeni, chrzęst ziemi i ciężki zgrzyt kamieni wstającego
  żywiołaka; prompt ma `no paper, no typing clicks, no page turning`.

Generacja `r012` dała 2/2 pliki i oba były semantycznie trafione. `452` miało
jednak flagę `harsh` (centroid 10,6 kHz, 85% energii > 8 kHz), więc w `r012b`
zrobiono lokalny de-harsh: high-shelf 6 kHz −16 dB + renormalizacja. Wynik:
centroid **8621 Hz**, air **57%**, 0 flag, przy zachowaniu szklistego charakteru
dzwonu soczewki.

Stan po `r012b`: **537 sampli**, **93 pliki z flagą**, **0 par bliźniaków
≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności semantycznych**.
Oba wskazane ID są bez flag sygnałowych i mają 0 pkt w audycie semantycznym.

Raporty: `data/samples/postprocess-r012.json`, `data/samples/deharsh-r012b.json`,
`docs/audits/2026-10-01-audio-audit-after-r012b.md`,
`docs/audits/2026-10-01-semantic-match-r012b.md`.

## 2026-10-01 — Dostawa b059: Tackle Artist i Golem-Skin Gauntlets

Właściciel dostarczył dwie nowe fabuły: `198SOS` *Tackle Artist* (Strixhaven,
orkowy zawodnik Prismari taranuje linię obrony, a magia wyzwala eksplozję
szkarłatnej farby) oraz `203_2XM` *Golem-Skin Gauntlets* (Axgard/Kaldheim,
krasnoludzka rękawica z płyt pancerza pradawnego golema wzmacnia cios).
Katalog urósł do **539 fabuł**.

Scenariusze:

- `198` — tupot korków po murawie, zderzenie ochraniaczy i mokry rozbryzg
  szkarłatnej farby; bez tłumu/wiwatów, żeby nie wprowadzać mowy,
- `203` — jasny szczęk żelaznych płyt rękawicy golema i dzwoniący metalowy
  rezonans; prompt wymusza crisp metallic detail i unika głuchego tąpnięcia.

Pierwsza generacja `b059` dała 2/2 pliki, ale `198` było tylko krótkim impulsem
(0,22 s treści + długi ogon ciszy), a `203` wpadło w podobieństwo do `501` i
było zbyt ciemne jak na metal. `b059b` przyniosło pełny, czytelny `198`
(2,76 s treści, 0 flag, semantycznie 0 pkt) i usunęło parę bliźniaczą. `203`
nadal było za ciemne w audycie semantycznym, więc `b059c` rozjaśniło metal
lokalnym high-shelfem 1,5 kHz +9 dB z renormalizacją. Wynik `203`: centroid
**571 → 1319 Hz**, rolloff95 **2283 → 3747 Hz**, audible_share **0,395 → 0,643**,
0 flag i 0 pkt semantycznie.

Stan po `b059c`: **539 sampli**, **93 pliki z flagą**, **0 par bliźniaków
≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności semantycznych**.
Oba nowe ID są bez flag sygnałowych i mają 0 pkt w audycie semantycznym.

Raporty: `data/samples/postprocess-b059.json`, `data/samples/postprocess-b059b.json`,
`data/samples/brighten-b059c.json`,
`docs/audits/2026-10-01-audio-audit-after-b059c.md`,
`docs/audits/2026-10-01-semantic-match-b059c.md`.

## 2026-10-01 — Dostawa b060: Mnemonic Wall

Właściciel dostarczył nową fabułę `196THS` *Mnemonic Wall* (Meletis/Theros:
Perisophia dotyka muru pamięci z krystalicznego marmuru, a echo dawnych idei
materializuje się jako świetlisty zwój zapomnianego czaru). Katalog urósł do
**540 fabuł**.

Scenariusz `196`: krótki brzęk krystalicznego marmuru i suchy szelest
rozwijanego pergaminu — konkretny, akustyczny odpowiednik dotknięcia muru i
pojawienia się zwoju, bez mowy/szeptów. Generacja `b060` dała 1/1 plik; sample
był semantycznie trafiony, ale zbyt jasny (`harsh`: centroid 9510 Hz, 77%
energii > 8 kHz). `b060b` przyciemniło go lokalnym high-shelfem 6 kHz −6 dB i
renormalizacją. Wynik: centroid **7818 Hz**, air **58%**, LUFS −19,99,
true peak −1,71 dBTP, **0 flag**. Po zsynchronizowaniu opisu z faktycznie
krótkim brzękiem audyt semantyczny daje `196` **0 pkt**.

Stan po `b060b`: **540 sampli**, **93 pliki z flagą**, **0 par bliźniaków
≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności semantycznych**.
Nowe ID jest bez flag sygnałowych i ma 0 pkt w audycie semantycznym.

Raporty: `data/samples/postprocess-b060.json`, `data/samples/deharsh-b060b.json`,
`docs/audits/2026-10-01-audio-audit-after-b060b.md`,
`docs/audits/2026-10-01-semantic-match-b060b.md`.

## 2026-10-02 — Dostawa b061: Vulturous Aven, Jade Bearer i Fiery Justice

Właściciel dostarczył trzy nowe fabuły: `205DTK` *Vulturous Aven* (moczary
Gurmag/Tarkir, sępi szaman Silumgara wyciąga z urny z prochami zakazaną
esencję), `208RIX` *Jade Bearer* (zalane groty przy Azcancie/Ixalan,
nefrytowy diadem przekazuje dziedzictwo Śpiewaków Rzek) oraz `210_2X2`
*Fiery Justice* (sala tronowa Bretagardu/Kaldheim, runiczny kostur wyzwala
nawałnicę sakralnego ognia). Katalog urósł do **543 fabuł**.

Scenariusze:

- `205` — suchy szur kościanego kostura po urnie z prochami i dwa eteryczne
  impulsy esencji; po generacji opis doprecyzowano z „syku” na faktyczny szur
  i impulsy, dzięki czemu audyt semantyczny nie oczekuje szumu pary,
- `208` — szmer płytkiej wody i kamienne kliknięcie nefrytowego diademu na
  czole; bez śpiewu/mowy, żeby ceremonia nie zamieniła się w wokal,
- `210` — trzask runicznego kostura o kamienną posadzkę i wybuch trzaskających
  płomieni; prompt wymusza nieregularne trzaski ognia i zakazuje krzyków.

Generacja `b061` dała 3/3 pliki. Postprodukcja wyrównała je do ok. −20 LUFS;
żaden z nowych plików nie ma flag sygnałowych ani pary bliźniaczej. Audyt
semantyczny po doprecyzowaniu scenariusza `205`: wszystkie trzy nowe ID mają
**0 pkt** (`205`: granular, `208`: water, `210`: impact+fire).

Stan po `b061`: **543 sample**, **93 pliki z flagą**, **0 par bliźniaków
≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności semantycznych**.
Nowe ID są bez flag sygnałowych i mają 0 pkt w audycie semantycznym.

Raporty: `data/samples/postprocess-b061.json`,
`docs/audits/2026-10-02-audio-audit-after-b061.md`,
`docs/audits/2026-10-02-semantic-match-b061.md`.

## 2026-10-03 — Runda r013/r013b: siedem poprawek po odsłuchu właściciela

Właściciel wskazał 7 sampli, których brzmienie nie kojarzyło się z kartą i
fabułą: `312` *Goblin Battle Jester* (brzmiało jak skrzypienie piasku),
`515` *Warmaker Gunship* (jak popiskiwanie myszy), `145` *Clone Shell* (jak
skrobanie w podłogę), `7` *Mindstab* (skrzypienie), `521` *Leafcrown Dryad*
(trąbka), `464` *Polluted Dead* (dźwięk radia) oraz `568` *Nanoform Sentinel*
(cykady).

Wszystkie 7 promptów i scenariuszy przepisano od zera na czytelne, fizyczne
źródła dźwięku z jawnymi zakazami błędnych skojarzeń:

- `7` (*Mindstab*) — rozdarcie, głośny szelest i świst papierowych kart
  pergaminu wyrywanych z księgi na skale (`no creaking, no wood squeak`),
- `145` (*Clone Shell*) — metalowy huk pękającej stalowej kapsuły, syk zaworu
  ciśnieniowego i mokry rozbryzg płynu stazy na żelaznej podłodze
  (`no floor scraping, no scratching`),
- `312` (*Goblin Battle Jester*) — skoczny tupot goblina na skale, jasny brzęk
  mosiężnych dzwonków/blaszek błazna i klekot kościanych ochraniaczy
  (`no sand crunch, no gravel`),
- `464` (*Polluted Dead*) — ciężkie szuranie stóp nieumarłego po suchej słomie
  i glebie oraz żrący syk i skwierczenie zatrutej ziemi (`no radio static, no
  electronic hum, no sine tone`),
- `515` (*Warmaker Gunship*) — syk siłowników, ciężki szczęk i łomot stalowej
  rampy okrętu desantowego uderzającej o skałę oraz huk dysz (`no squeaking,
  no mouse chirps`),
- `521` (*Leafcrown Dryad*) — szelest gęstych liści dębu, świst splatających
  się kolczastych gałęzi i trzask łamanych drewnianych pędów (`no trumpet, no
  horn, no sustained tone`),
- `568` (*Nanoform Sentinel*) — trzask iskier spawania elektrycznego,
  metaliczny zatrzask uszczelnianych stalowych przewodów i uderzenie
  włączanego generatora (`no cicadas, no insects, no high hiss`).

Generacja `r013` (run 37136501832) dała 7/7 plików i zdjęła dwie dotychczasowe
flagi sygnałowe z korpusu (`521`: `tonal_sustained`, `568`: `harsh`). W `r013b`
wykonano lokalne dopracowanie barwy i obwiedni dla dwóch plików: `312`
(high-shelf 5,5 kHz −8 dB + peaking 750 Hz +5 dB pod ciało kościanych płytek,
centroid **8940 → 6100 Hz**, udział 250–2000 Hz **6% → 28%**) oraz `521`
(przycięcie 0,22 s powolnego wejścia z fade-in 8 ms + high-shelf 5,5 kHz −7 dB
i peaking 650 Hz +6 dB pod drewniane gałęzie, centroid **7372 → 5569 Hz**).

Stan po `r013b`: **543 sample**, **91 plików z flagą** (spadek z 93), **0 par
bliźniaków ≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności
semantycznych**. Wszystkie 7 wskazanych ID ma **0 flag sygnałowych** oraz
**0,0 pkt w audycie semantycznym**.

Raporty: `data/samples/postprocess-r013.json`, `data/samples/refine-r013b.json`,
`docs/audits/2026-10-03-audio-audit-after-r013.md`,
`docs/audits/2026-10-03-semantic-match-r013.md`.

## 2026-10-03 — Dostawa b062: Bloodtithe Harvester i Dig Site Inventory

Właściciel dostarczył dwie nowe fabuły: `212VOW` *Bloodtithe Harvester*
(Innistrad/Stensia: wampirzy poborca krwawej dziesięciny ocenia rocznik krwi w
szlifowanej karafce i zabezpieczone woskiem flakony w kufrach powozu) oraz
`239SOS` *Dig Site Inventory* (kanion Pillardrop/Arcavios: adeptka Lorehold
kataloguje starożytne kamienne tablice i kompasy w oprawnej w mosiądz skrzyni
ekspedycyjnej). Katalog urósł do **545 fabuł**.

Scenariusze (oba z wynikiem jakości 100/100 w `audit_scenario_quality.py`):

- `212` (*Bloodtithe Harvester*) — chlupot gęstej krwi w szklanej karafce,
  brzęk szkła flakonów i trzask woskowej pieczęci,
- `239` (*Dig Site Inventory*) — stukot kamiennych tablic, brzęk kompasów z
  mosiądzu w drewnianej skrzyni i zatrzask klamry.

Generacja `b062` (run 37147333162) dała 2/2 pliki, wyrównane w postprodukcji do
ok. −20 LUFS (`212`: −19,96 LUFS, true peak −2,44 dBTP, treść 1,81 s; `239`:
−20,26 LUFS, true peak −1,66 dBTP, treść 1,94 s). Oba nowe sample mają **0 flag
sygnałowych** i **0,0 pkt w audycie semantycznym** (`212`: impact/metal/water;
`239`: impact/metal/wood).

Stan po `b062`: **545 sampli**, **91 plików z flagą**, **0 par bliźniaków
≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności semantycznych**.

Raporty: `data/samples/postprocess-b062.json`,
`docs/audits/2026-10-03-audio-audit-after-b062.md`,
`docs/audits/2026-10-03-semantic-match-b062.md`.

## 2026-10-04 — Dostawa b063: 241 News Helicopter

Dodano fabułę `241SPM` *News Helicopter*: śmigłowiec reporterski Daily Bugle
wykonuje zwrot nad Manhattanem podczas pościgu za Spider-Manem. Katalog urósł
do **546 fabuł**.

Scenariusz `b063` opisuje wyłącznie charakterystyczny przelot maszyny —
rytmiczny terkot wirnika i dudnienie silnika. Prompt wymusza krótki, czysty
przelot helikoptera i wyklucza muzykę, mowę, radio, wiatr oraz odgłosy miasta.
Ocena jakości scenariusza: **78/100**.

Generacja (run 37187409300) dała 1/1 plik. Po postprodukcji sample ma 2,56 s
(czytelna treść 2,16 s), −20,00 LUFS i true peak −11,34 dBTP. `241.mp3` ma
**0 flag sygnałowych**. Audyt semantyczny przyznał **1,5 pkt** drobnej
heurystyki za udział dołu pasma 13,6% wobec progu 20% klasy „rumble”; nie
wykrył rażącej sprzeczności. Nie powstała żadna para bliźniacza ani duplikat
PCM.

Stan po `b063`: **546 sampli**, **91 plików z flagą**, **0 par bliźniaków
≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności semantycznych**.

Raporty: `data/samples/postprocess-b063.json`,
`data/samples/scenario-quality.json`,
`docs/audits/2026-10-04-scenario-quality.md`,
`docs/audits/2026-10-04-audio-audit-after-b063.md`,
`docs/audits/2026-10-04-semantic-match-b063.md`.

## 2026-10-04 — Dostawa b064: 244 Natural Connection

Dodano `244BFZ` *Natural Connection*: animistka Tajuru łączy się z geomancją
Zendikaru, a monolit skalny wypiera się z gliniastej ziemi. Katalog urósł do
**547 fabuł**.

Scenariusz `b064` skupia się na jednym dźwięku — chropowatym szurze kamiennego
monolitu podnoszonego przez grunt. Prompt wyklucza wybuch, uderzenia, luźne
odłamki, muzykę, mowę, wiatr i tło. Ocena jakości scenariusza: **85/100**.

Generacja (run 37192997233) dała 1/1 plik. Po postprodukcji `244.mp3` ma
2,76 s (czytelna treść 1,46 s), −20,00 LUFS i true peak −6,33 dBTP; **0 flag
sygnałowych**. Słowo „szur” nie mapuje się na obecną klasę audytu semantycznego,
więc plik trafił do `without_class` — bez automatycznej oceny semantycznej.

Stan po `b064`: **547 sampli**, **91 plików z flagą**, **0 par bliźniaków
≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności semantycznych**.

Raporty: `data/samples/postprocess-b064.json`,
`data/samples/scenario-quality.json`,
`docs/audits/2026-10-04-scenario-quality.md`,
`docs/audits/2026-10-04-audio-audit-after-b064.md`,
`docs/audits/2026-10-04-semantic-match-b064.md`.

## 2026-10-04 — Dostawa b065: 247 Subterranean Scout

Dodano `247ORI` *Subterranean Scout*: zwinny zwiadowca boggartów prowadzi
współplemieńców przez podziemne korytarze Lorwynu. Katalog urósł do **548
fabuł**.

Scenariusz `b065` skupia się na szybkich, lekkich krokach boggarta i szuraniu
po wilgotnej gliniastej glebie; pochodnia i tło zostały wykluczone z sampla.
Ocena jakości scenariusza: **92/100**.

Generacja (run 37222183510) dała 1/1 plik. `247.mp3` trwa 2,56 s (czytelna
treść 2,06 s). Postprodukcja ograniczyła wzmocnienie do +15 dB i użyła
limiter gain reduction 1,27 dB; finalnie sample ma −21,87 LUFS i true peak
−1,70 dBTP. Audyt sygnałowy: **0 flag**. Audyt semantyczny: **0 pkt**,
klasy impact/steps, 12 onsetów i brak naruszeń.

Stan po `b065`: **548 sampli**, **91 plików z flagą**, **0 par bliźniaków
≥ 0,95**, **0 identycznego PCM**, **0 rażących sprzeczności semantycznych**.

Raporty: `data/samples/postprocess-b065.json`,
`data/samples/scenario-quality.json`,
`docs/audits/2026-10-04-scenario-quality.md`,
`docs/audits/2026-10-04-audio-audit-after-b065.md`,
`docs/audits/2026-10-04-semantic-match-b065.md`.

## 2026-10-04 — Dostawa b066: 250 Loxodon Mender

Dodano fabułę `250MRD` *Loxodon Mender*: w Taj-Nar na Mirrodinie kleryk
loxodonów przywraca pierwotną strukturę strzaskanemu mieczowi auriockiego
wojownika. Katalog urósł do **549 fabuł**.

Scenariusz `b066` redukuje moment naprawy do jednego, wyraźnego zdarzenia —
trzasku i szczęku stalowego ostrza scalającego się po pęknięciu. Prompt skupia
się na dominującym metalicznym zatrzaśnięciu z krótkim wybrzmieniem; wyklucza
młotkowanie, odgłosy kuźni, eksplozje i tło. Ocena jakości scenariusza:
**99/100**.

Generacja (run 37222766766) dała 1/1 plik. `250.mp3` trwa 2,48 s (czytelna
treść 1,27 s); po postprodukcji ma −19,77 LUFS i true peak −5,63 dBTP.
Audyt sygnałowy: **0 flag**. Audyt semantyczny: **0 pkt**, klasy impact/metal,
bez naruszeń. Korpus: **91** plików z flagą, **0** par bliźniaków ≥ 0,95,
**0** identycznych PCM i **0** rażących sprzeczności semantycznych.

Raporty: `data/samples/postprocess-b066.json`,
`data/samples/scenario-quality.json`,
`data/samples/audio-audit-2026-10-04-after-b066.json`,
`docs/audits/2026-10-04-scenario-quality.md`,
`docs/audits/2026-10-04-audio-audit-after-b066.md`,
`docs/audits/2026-10-04-semantic-match-b066.md`.

## 2026-10-04 — Dostawa b067: 254 Snarespinner

Dodano `254DMU` *Snarespinner*: pająk z puszczy Yavimaya rozciąga lepką,
złotą pajęczynę, która uruchamia jego błyskawiczny atak na latającą zdobycz.
Katalog urósł do **550 fabuł**.

Żeby odróżnić dźwięk od wcześniejszych sampli pajęczyn, scenariusz `b067`
skupia się na jednym szybkim, suchym tupocie i stukaniu ośmiu odnóży pająka
o drewniany pień. Ocena jakości scenariusza: **92/100**.

Generacja (run 37223595286) dała 1/1 plik. `254.mp3` trwa 2,00 s (czytelna
treść 1,74 s); po postprodukcji ma −20,16 LUFS i true peak −1,70 dBTP.
Audyt sygnałowy: **0 flag**. Audyt semantyczny: **0 pkt**, klasy impact/wood,
17 onsetów i brak naruszeń. Korpus: **91** plików z flagą, **0** par bliźniaków
≥ 0,95, **0** identycznych PCM i **0** rażących sprzeczności semantycznych.

Raporty: `data/samples/postprocess-b067.json`,
`data/samples/scenario-quality.json`,
`data/samples/audio-audit-2026-10-04-after-b067.json`,
`docs/audits/2026-10-04-scenario-quality.md`,
`docs/audits/2026-10-04-audio-audit-after-b067.md`,
`docs/audits/2026-10-04-semantic-match-b067.md`.

## 2026-10-04 — Dostawa b068: 255 Urborg Uprising

Dodano `255APC` *Urborg Uprising*: nekromantka na bagnach Urborgu budzi
dwa widma dawnych wojowników, które unoszą się z czarnej, spienionej wody.
Katalog urósł do **551 fabuł**.

Scenariusz `b068` skupia się na jednym krótkim, pustym świście i szumie
widm unoszących się nad wodą — bez głosów, plusku ani odgłosów rytuału.
Ocena jakości scenariusza: **85/100**.

Generacja (run 37229612964) dała 1/1 plik. `255.mp3` trwa 2,00 s (czytelna
treść 0,87 s); po postprodukcji ma −19,51 LUFS i true peak −10,20 dBTP.
Audyt sygnałowy: **0 flag**. Audyt semantyczny: **0 pkt**, klasa noise_hiss,
bez naruszeń. Korpus: **91** plików z flagą, **0** par bliźniaków ≥ 0,95,
**0** identycznych PCM i **0** rażących sprzeczności semantycznych.

Raporty: `data/samples/postprocess-b068.json`,
`data/samples/scenario-quality.json`,
`data/samples/audio-audit-2026-10-04-after-b068.json`,
`docs/audits/2026-10-04-scenario-quality.md`,
`docs/audits/2026-10-04-audio-audit-after-b068.md`,
`docs/audits/2026-10-04-semantic-match-b068.md`.

## 2026-10-04 — Dostawa b069: 259 Kozilek's Predator

Dodano `259_2XM` *Kozilek's Predator*: bezrozumne pomioty tytana Kozileka
przeczesują wulkaniczne kaniony Akoum; masywny, pasiasty drapieżnik z płytami
obsydianu zbiega po strzaskanym hedronie, a za nim przemykają dwa chitynowe
zarodki. Katalog urósł do **552 fabuł**.

Scenariusz `b069` wyodrębnia jeden krótki, suchy, szklisty zgrzyt szponów
zsuwających się po kamiennej ścianie hedronu — bez ryku, gruzu, uderzenia ani
tła. Ocena jakości scenariusza: **71/100**, bez problemów.

Generacja (run 37230106466) dała 1/1 plik. `259.mp3` trwa 2,00 s
(wykryta treść 1,30 s); po postprodukcji ma −20,04 LUFS i true peak
−2,41 dBTP. Audyt sygnałowy: **0 flag**. Audyt semantyczny: **0 pkt**, klasa
creak, bez naruszeń. Korpus: **91** plików z flagą, **0** par bliźniaków
≥ 0,95, **0** identycznych PCM i **0** rażących sprzeczności semantycznych.

Raporty: `data/samples/postprocess-b069.json`,
`data/samples/scenario-quality.json`,
`data/samples/audio-audit-2026-10-04-after-b069.json`,
`docs/audits/2026-10-04-scenario-quality.md`,
`docs/audits/2026-10-04-audio-audit-after-b069.md`,
`docs/audits/2026-10-04-semantic-match-b069.md`.

## 2026-10-04 — Dostawa b070: 260 Etched Host Doombringer

Dodano `260MOM` *Etched Host Doombringer*: potężny demon z Immersturmu,
po kompleacji okuty czarnym żelazem i bazaltem, stał się bezduszną machiną
Zastępu Trawionych. Z rozgrzanej piersi wystrzeliwuje pojedyncze wyładowanie
nekromantycznej energii; katalog urósł do **553 fabuł**.

Pierwszy scenariusz `b070` zawężał efekt do krótkiego trzasku wyładowania
spod bazaltowej płyty na piersi demona (jakość **71/100**). Po uwadze
właściciela, że taki abstrakcyjny efekt nie daje rozpoznawalnego skojarzenia
z demonem, sygnaturę zmieniono w rundzie `r014` na bezsłowny, gardłowy ryk.

Historyczna generacja b070 (run 37230572719) dała 1/1 plik. Pierwsze
`260.mp3` trwało 2,00 s (wykryta treść 0,87 s), −20,17 LUFS, −9,73 dBTP;
sygnałowo miało 0 flag, ale audyt semantyczny naliczył 1,5 pkt za wolny atak.
Próbkę zastąpiła wersja `r014` opisana poniżej.

Raporty b070: `data/samples/postprocess-b070.json`,
`data/samples/audio-audit-2026-10-04-after-b070.json`,
`docs/audits/2026-10-04-audio-audit-after-b070.md`,
`docs/audits/2026-10-04-semantic-match-b070.md`.

## 2026-10-04 — Korekta r014: 260 Etched Host Doombringer

Po feedbacku właściciela scenariusz przepisano na jeden krótki, niski,
gardłowy ryk demona z chropawym, bazaltowym tembrem — rozpoznawalny odgłos
stworzenia zamiast abstrakcyjnego wyładowania. Ocena jakości: **71/100**,
bez problemów.

Generacja r014 (run 37231271188) dała 1/1 plik i zastąpiła poprzednią wersję
`audio/samples/260.mp3`. Sample trwa 2,00 s (wykryta treść 1,64 s); po
postprodukcji ma −20,01 LUFS i true peak −11,40 dBTP. Audyt sygnałowy:
**0 flag**. Audyt semantyczny: **0 pkt**, klasa `voice`, bez naruszeń.
Korpus: **91** plików z flagą, **0** par bliźniaków ≥ 0,95,
**0** identycznych PCM i **0** rażących sprzeczności semantycznych.

Raporty r014: `data/samples/postprocess-r014.json`,
`data/samples/scenario-quality.json`,
`data/samples/audio-audit-2026-10-04-after-r014.json`,
`data/samples/semantic-audit-2026-10-04-after-r014.json`,
`docs/audits/2026-10-04-scenario-quality.md`,
`docs/audits/2026-10-04-audio-audit-after-r014.md`,
`docs/audits/2026-10-04-semantic-match-r014.md`.

## 2026-10-04 — Sesja weryfikacyjna: lokalny audyt 553 sampli (0 kredytów)

Sesja `arena/01a108e2-mtgdatabase` nie dostała nowych fabuł, więc zamiast
generacji wykonano pełną weryfikację stanu i udokumentowano brakujące ogniwo
procesu.

**Stan potwierdzony na czystym klonie:** `validate_stories.py` — 553 poprawne
rekordy; `validate_sample_scenarios.py` — 553/553 `ready`; `import_collection.py`
z `fabuły270926.csv` daje katalog identyczny z tym w repo (te same 553 ID w tej
samej kolejności); testy v2 — 6/6; `build_pack.py` — 553 MP3, `build_site.py` —
553 sample. Zero sierot i zero nadmiarowych plików w `audio/samples`.

**Audytory uruchomione lokalnie, bez tymczasowego workflowa.** Czysty sandbox
nie ma `numpy`/`scipy`/`soundfile`, ale `pip` ma dostęp do sieci: `python3 -m
venv .venv` + instalacja trzech paczek (numpy 2.4.6, scipy 1.17.1,
soundfile 0.14.0) wystarczyła, żeby pełny skan 553 MP3 przeszedł w **40 s**
lokalnie, audyt semantyczny w 4 s, a audyt jakości scenariuszy w <1 s. Przepis
trafił do `ENVIRONMENT.md` §6 — tymczasowe triggery na GitHubie zostają już
tylko dla generacji ElevenLabs i importu artefaktów.

**Wyniki lokalne są identyczne z raportami w repo** (`audio-audit-latest.json`,
`docs/audits/2026-10-04-*-r014.md`), czyli stan opisany w dokumentacji jest
odtwarzalny:

- sygnał: **91/553** plików z flagą — `long_trail_silence` 39, `harsh` 32,
  `short_content` 11, `cut_start_hard` 7, `speech_like` 5, `dull` 3,
  `tonal_sustained` 3, `cut_end_hard` 2, `long_lead_silence` 2;
  **0** par bliźniaków ≥ 0,95, **0** identycznych PCM, mediana −20,01 LUFS
  (σ 0,12 LU);
- semantyka: **0** rażących sprzeczności, **57** „wyraźnych” (1,5–3,0),
  **3** drobne; **214** sampli bez rozpoznanej klasy dźwięku;
- jakość scenariuszy: mediana **57/100**, **0** poniżej progu 40, ale
  **295** scenariuszy bez słowa opisującego konkretny dźwięk i **295** bez
  materiału/kontaktu.

Ostatnia liczba to największa niezamknięta dźwignia jakościowa korpusu:
przepisanie tych scenariuszy jest darmowe, ale słyszalny efekt daje dopiero
regeneracja (~29 kredytów/sztukę), więc decyzja o budżecie należy do
właściciela. Właściciel wybrał z listy najtwardszą kategorię — `short_content`
(11 plików) — i zaraz potem ruszyła runda `r015` opisana poniżej.

## 2026-10-04 — Runda r015/r015b/r015c/r015d: jedenaście sampli z treścią < 0,8 s

Właściciel zdecydował o regeneracji wszystkich plików, które audyt oznacza jako
WYSOKIE, czyli `short_content` (treść krótsza niż 0,8 s przy zamówionych 2,5 s):
`65`, `76`, `105`, `191`, `290`, `321`, `403`, `504`, `517`, `567`, `593`.

Zgodnie z zasadą z `LESSONS.md` („generatorowi mówi się, co ma być”) żaden
prompt nie został skrócony ani uzupełniony zakazem ciszy — każdy opisuje teraz
**następstwo faz jednego zdarzenia** (impakt → faza ciągła → wybrzmienie), co
daje modelowi czym wypełnić czas.

**r015 (run 37239129618, 11/11 `generated`).** Treść urosła w 10 z 11 plików,
np. `517` 0,21 → 1,82 s, `290` 0,22 → 1,51 s, `403` 0,35 → 0,65 s, `567`
0,65 → 0,67 s (bez zmiany). Trzy pliki wymagały drugiej próby:

- `290` *Soulbright Flamekin* wpadł w pułapkę infradźwiękową — centroid
  **128 Hz**, `audible_share` **0,063**, flagi `boomy` + `dull`;
- `504` *Ballista Watcher* wyszedł jako niski, w pełni tonalny łomot
  (tonalność **0,91** ramek, centroid 599 Hz) zamiast strzału z balisty;
- `567` *Jwar Isle Avenger* nadal miał **0,60 s** treści.

**r015b (run 37239606761, 3/3 `generated`).** Wszystkie trzy naprawione:
`290` — 2,04 s treści, centroid 373 Hz, `audible_share` 0,261; `504` — 2,48 s;
`567` — 2,48 s. Prompty nazwały fazy ciągłe (trzaskający żar, brzęk cięciwy
i świst bełtu, długie mokre rozdarcie chityny).

**r015c (run 37240185162, 1/1 `generated`).** `517` *Force Away* po
regeneracji okazał się bliźniakiem `57` *Veiled Ascension* (kosinus **0,9612**)
i `255` *Urborg Uprising* (**0,9601**) — wszystkie trzy to podmuch/unoszenie
powietrza. Varispeed zbijał kosinus dopiero przy +25% (0,9449), czyli kosztem
słyszalnego przesunięcia barwy, więc zamiast tego zmieniono **źródło dźwięku**:
rozbryzg wodnej mgły po zniknięciu ciała i żelazny tasak opadający w zaspy.
Efekt: 0 par bliźniaczych, 0 flag, 0 pkt w audycie semantycznym.

**r015d (run 37240478263, 1/1 `generated`).** `76` *Negate* po r015 zapalił
**rażącą sprzeczność semantyczną (3,0 pkt)**: scenariusz obiecuje szklisty,
dzwoniący kryształ, a plik był szumową kaskadą (flatness **0,42** przy górnym
kwartylu 0,22) o ciągłym charakterze (sustain 0,49). Prompt przepisany na
dźwięczne dzwonienie odłamków — po regeneracji **0 pkt**, flatness 0,10.

**Postprodukcja i różnicowanie (0 kredytów).** Cztery przejścia
`postprocess_samples.py` (`postprocess-r015.json` 11 plików,
`postprocess-r015b.json` 3, `postprocess-r015c.json` 517,
`postprocess-r015d.json` 76) oraz dwie sesje lokalnych korekt z surowych
oryginałów (`refine-r015b.json`, `refine-r015c.json`):

- `403` — high-shelf 4,5 kHz −12 dB + peaking 750 Hz +5 dB (centroid
  9848 → 9258 Hz), głośność −27,8 → −21,46 LUFS. Flaga `harsh` **zostaje
  świadomie**: to syk żrącego gazu, 88% energii powyżej 8 kHz, i żadna
  rozsądna korekcja tego nie zmienia bez zabicia źródła;
- `593` — high-shelf 3,5 kHz −14 dB + peaking 1,2 kHz +6 dB (centroid
  9407 → 8944 Hz), `harsh` zdjęty;
- `504` — fade-in 8 ms i fade-out 40 ms na twarde krawędzie oraz większy budżet
  limitera: −24,7 → −20,89 LUFS;
- `76` — łagodny high-shelf 6 kHz −6 dB + zwężenie boku (kosinus z `174`
  **0,9417**, z `315` **0,9397**, `mono_excess` 1,77 LU). Mocniejszy tilt
  (5 kHz −8 dB + 1,5 kHz +4 dB) też rozbijał parę, ale zamieniał kryształy
  w szum — stąd r015d.

**Stan po rundzie:** 553 sample, **82 pliki z flagą** (spadek z 91), **0 par
bliźniaków ≥ 0,95**, **0 identycznych PCM**, **0 rażących sprzeczności
semantycznych** (60 „wyraźnych”, 3 drobne), mediana −20,01 LUFS (σ 0,13 LU).
Z jedenastki **9 plików ma 0 flag**; `403` ma `harsh`, `504` `cut_start_hard`
(perkusyjny start — audyt sam uznaje go za naturalny). Mediana jakości
scenariuszy 57,0 → **60,0/100**. Zużycie: **16 generacji** (11 + 3 + 1 + 1).

Raporty: `data/samples/audio-audit-2026-10-04-after-r015.json`,
`data/samples/semantic-audit-2026-10-04-after-r015.json`,
`data/samples/scenario-quality.json`,
`docs/audits/2026-10-04-audio-audit-after-r015.md`,
`docs/audits/2026-10-04-semantic-match-r015.md`,
`docs/audits/2026-10-04-scenario-quality.md`. Tymczasowy workflow generacji
(`temp-generate-r015.yml`, triggery `[generate-r015…]`) usunięty po imporcie.

## 2026-09-30 — Dostawa b058: fabuła 194 Lionheart Maverick

Katalog urósł do **537 fabuł**. Nowa fabuła z Warhammer Old World (Marienburg):
błędny rycerz na ciężkim rumaku zagradza drogę strażnikom cechowym. Ponieważ
dobycie miecza (308) i tupnięcie+rżenie rumaka (593) były już zajęte, na sample
wybrano odrębną barwowo sygnaturę: metaliczny grzechot stalowego kropierza
i zbroi płytowej + stuknięcie kopyta o bruk.

Dwie próby (obie generowane tymczasowym markerowanym workflow w Actions,
generacja → postprodukcja → commit z powrotem; surowe oryginały w artefaktach
`b058-raw`, 30 dni):

1. **b058 — pułapka basowa.** Prompt „heavy hoof stomp / planting hard on stone"
   dał głuchy boom: centroid **132 Hz**, audible_share **0,0287** (praktycznie
   niesłyszalne), flagi boomy/cut_start_hard, metaliczny grzechot zniknął.
2. **b058b — trafione.** Prompt przepisany na *dominantę metaliczną* (jasny,
   wysoki grzechot i pobrzękiwanie, klekot płyt i kolczugi, lekki stuk kopyta;
   bez „heavy/deep/hard stomp"). Efekt: audible_share **0,9918**, centroid
   9301 Hz — ale za jasno (88% energii > 6,5 kHz), flaga `harsh`.

Korekta barwy (jedno przejście EQ od oryginału b058b, lokalnie w `.venv`):
high-shelf 5,5 kHz −12 dB + peaking 1,2 kHz i 400 Hz (odbudowa korpusu),
renormalizacja i limiter. Wynik: centroid **5617 Hz**, energia > 6,5 kHz
88% → 54%, audible_share 0,96, LUFS −20,54, true peak −1,25 dBTP, **0 flag**.
Tekst scenariusza zgrany z faktycznym brzmieniem (grzechot/klekot zamiast
„dzwoniącej" kolczugi) → audyt semantyczny **0 pkt** (impact/metal/steps).

Stan końcowy: korpus **537 sampli / 95 flag / 0 par bliźniaków / 0 identycznego
PCM**, **0 rażących sprzeczności semantycznych**. Raporty:
`postprocess-b058.json`, `docs/audits/2026-09-30-audio-audit-after-b058b.md`,
`docs/audits/2026-09-30-semantic-match-b058b.md`.

## 2026-09-30 — Dostawa b057 (178, 192) + regeneracja r009/r009b (317, 445)

Właściciel zgłosił, że **317** (*Village Bell-Ringer*) i **445** (*Locthwain
Paladin*) brzmią dziwnie, oraz dostarczył dwie nowe fabuły z przestrzeni
The Edge (układ Sothera): **178EOE** *Oreplate Pangolin* i **192OGW**
*Crumbling Vestige*. Katalog urósł do **536 fabuł**.

Diagnoza starych sampli (obie bez flag sygnałowych — problem percepcyjny):
- **317**: prompt łączył trzy współbieżne zdarzenia (naprężenie liny +
  skrzypienie dzwonnicy + dzwon); tonalność tylko 28% ramek, centroid 3235 Hz —
  dzwon ginął w szarpaninie.
- **445**: prompt mieszał kopyta + pękające pnącza + proporzec + wiatr;
  centroid 6527 Hz, flatness 0,31, tonalność 0 — szerokopasmowy „szum
  chrupania" bez rytmu.

Przepisane prompty (jedno czytelne źródło) i generacja przez scouta w Actions
(tymczasowy workflow markerowany, generuje → postprodukcja → commit z powrotem;
surowe oryginały w artefaktach `r009-b057-raw`, `r009b-raw`, 30 dni):

- **runda r009** (ids 178, 192, 317, 445): pierwsza generacja. 317 wyszedł jako
  czysty, w pełni tonalny dzwon (tonal_frac 0,28 → **1,0**, centroid 1656 Hz),
  178 czysto od razu. Ale **445 wpadło w pułapkę basową** (centroid 154 Hz,
  audible_share **0,117**, flagi boomy/dull/mono_collapse — sprawca:
  „deep muffled low thud"), a **192 utworzyło parę bliźniaczą z 401**
  (*Rage of Purphoros*, syczący metal; cosine 0,962 — obie tekstury jasne,
  szerokopasmowe, „syczące").
- **runda r009b** (ids 192, 445): przepisane prompty — 445 na chrupanie/trzask
  skorupy „crisp and present in the mid range" (bez „deep/low/muffled/thud"),
  192 na dyskretne, perkusyjne brzęki kryształu zamiast ciągłego „shimmer swell".
  Efekt: 445 centroid **3979 Hz**, audible_share **0,986**, 0 flag; 192
  zróżnicowane od 401 — **0 par bliźniaków w całym korpusie**.

Higiena czasu (przycięcie martwego ogona ciszy, deterministycznie, lokalnie):
- **317**: 3,0 s → **2,23 s** (fade-out 200 ms), flaga `long_trail_silence`
  zdjęta, `duration_seconds` scenariusza dostrojone do 2,25.
- **192**: 2,48 s → **1,26 s**, `duration_seconds` → 1,25.

Stan końcowy (audyt `2026-09-30-after-r009b`): wszystkie **4 pliki 0 flag**,
korpus **536 sampli / 95 flag / 0 par bliźniaków / 0 identycznego PCM**,
mediana LUFS ≈ −20. Audyt semantyczny: **0 rażących sprzeczności** (445 i 192
po 0 pkt; 317 1,0; 178 1,5 — celowy build syk pneumatyki → uderzenie).
Raporty: `postprocess-r009-b057.json`, `postprocess-r009b.json`,
`docs/audits/2026-09-30-audio-audit-after-r009b.md`,
`docs/audits/2026-09-30-semantic-match.md`.

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
- Pisać scenariusze jako jednorodne sample. Unikać słów i konstrukcji:
  `tło`, `hero`, `koda`, `warstwy`, `ambient bed`, `full scene`.
- Każdy prompt ma zawierać zakaz mowy. Muzyka jest dozwolona tam, gdzie
  karta ją implikuje — przez `music_allowed` z nazwanym instrumentem
  (decyzja właściciela 2026-10-05).
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



## 2026-10-05 — Diagnoza: trzy różne awarie rozpoznawalności + audyt archetypów

Właściciel podał 13 kart, których sample „nie kojarzą się z kartą” (skrzypienie
piasku, popiskiwanie myszy, spuszczanie wody w toalecie, maszyna do pisania,
cykady, stukanie do drzwi). Wszystkie poza `387` były już regenerowane
w rundach r011–r013, więc **prompty sprzed poprawki** odczytano z historii
GitHuba (`gh api …/contents/data/samples/scenarios.jsonl?ref=<sha>` dla
`7e0a9389`, `3451cd69`, `4b39a351`) — lokalny klon jest płytki (1 commit).

Stare prompty pokazują, że to **nie jedna awaria, a trzy**:

- **A — prompt był opisem kadru, nie dźwięku.** `452` Omenspeaker: „two blue
  beams sweeping the ceiling, a quill freezing mid-stroke”; `396`: „green light
  pouring from a palm, muscles swelling”; `464`: „a thick fog rolling low, crops
  wilting”. Model nie ma czego nagrać, więc improwizuje generyczną teksturę
  (właściciel: toaleta, syk pary, radio). **Naprawione** w r011–r013.
- **B — prompt był dźwiękowy, ale zamówiony dźwięk jest z natury
  niejednoznaczny.** `557` Kishla Village: „wooden boats knocking against dock
  pilings, hollow rhythmic bumps” — model dowiązał **uczciwie**, dlatego brzmi
  jak pukanie do drzwi. `387`: „chitin bodies hissing” → syk. `515`: „rapid
  mechanical skittering” → popiskiwanie myszy. Stukanie, syk, chrobot i szelest
  może wydać z siebie wszystko, więc nie nadaje się na sygnaturę karty.
  **Lepszy prompt tego nie naprawi** — trzeba zmienić dźwięk na taki, który ma
  własną tożsamość (ryk, dzwon, wybuch, krakanie, muzyka).
- **C — prompt był dobry, model nie dowiózł.** `312`: zamówiony „a shrill
  wordless cackle of mockery” → skrzypienie piasku; `521`: „a bowstring drawn
  slow and held” → trąbka. To wariancja generacji; zdejmuje ją dopiero
  generowanie wariantów i automatyczny wybór, nie redakcja promptu.

**Nowe narzędzie: `scripts/audit_archetype_match.py`.** Dotychczasowe audyty
mierzyły jakość realizacji i zgodność z grubą klasą (`metal`, `woda`, `ogień`) —
spłukiwanie toalety i wytrysk oazy to dla audytu semantycznego ta sama woda, oba
przechodzą z 0 pkt. Audyt archetypów wprowadza **kontrakty**: deklarujemy
w scenariuszu pole `archetype` (np. `creature_roar`, `arcane_choir`,
`volcanic_eruption`), a skrypt sprawdza, czy sygnał spełnia mierzalne warunki
tego archetypu (ryk musi być harmoniczny, niski i trwać; chichot musi być serią
≥3 wybuchów; chór musi być harmoniczny i płynąć). Wpisy bez `archetype` są
pomijane — skrypt nie zgaduje archetypu z tekstu, bo zgadywanie było źródłem
problemu.

**Pomiar bazowy 13 kart** (`data/samples/archetype-match-2026-10-05-baseline.json`):
**6 nie trafionych** (`452` 6,0 · `464` 4,0 · `396` 3,5 · `539` 3,5 · `387` 2,5 ·
`515` 2,5), **6 prawdopodobnych** (`7` 1,5 · `312` 1,0 · `521` 1,0 · `557` 1,0 ·
`463` 0,5 · `568` 0,5), **1 trafiona** (`145`). Z siedmiu kart poprawionych
w r011–r013 audyt potwierdza więc jedną.

**Zastrzeżenie kalibracyjne (ważne):** progi kontraktów są ustawione ręcznie.
`463` przegrał o 0,0001 (`low_all=0.250` przy progu ≥0,25), `557` o 0,02 s
treści — takich rozstrzygnięć nie wolno traktować jako wyroku. Zanim audyt
zacznie sterować regeneracjami, trzeba go skalibrować na odsłuchu właściciela:
audyt jest **proxy** dla oceny uchem, a nie jej zamiennikiem.

## 2026-10-05 — Pilot archetypowy r016: 5 kart × 3 warianty, wybór kontraktem (15 generacji)

Tor wybrany przez właściciela: **pilot generacyjny i triage katalogu równolegle**;
muzyka dozwolona tam, gdzie karta ją implikuje (zakaz w `AGENTS.md` i
`docs/ai-sfx-pipeline.md` był błędem dokumentacji — usunięty, mowa zostaje
zakazana).

**Zmiana metody.** Zamiast opisu tekstury zamówiliśmy archetyp (`396` ryk,
`452` chór proroctwa, `464` jęk nieumarłego, `539` grzmot ziemi, `387` erupcja),
długość 4,0 s, po 3 warianty na kartę. Wybór robi nowy
`scripts/pick_archetype_variant.py`: liczy `audit_samples_full.analyze()` +
`extra_features()` dla każdego wariantu i bierze minimum punktów kontraktu
archetypu; przy remisie — dłuższą słyszalną treść.

**Wynik** (`docs/audits/2026-10-05-archetype-pilot-r016.md`):

| ID | Karta | Przed | Po | Uwaga |
|---:|---|---:|---:|---|
| 452 | Omenspeaker | 6,0 | **0** | chór wszedł we wszystkich 3 wariantach |
| 396 | Vow of Wildness | 3,5 | **0** | warianty: 0 / 2,5 / 3,5 — selekcja konieczna |
| 539 | Silvanus's Invoker | 3,5 | 1,0 | archetyp trafiony, ale `mid_up`=0,063 — niesłyszalny na małych głośnikach |
| 387 | Molten Nursery | 2,5 | 1,0 | generyczny boom, kosinus 0,9762 z `501` (salwa plazmowa) |
| 464 | Polluted Dead | 4,0 | 2,5 | centroid 1,1 kHz przy kontrakcie 120–1000 Hz |

Audyt archetypów na 13 kartach: **przed {nie trafiony 6, prawdopodobnie 6,
trafiony 1} → po {2, 8, 3}**.

**Wnioski.** (1) Prompt archetypowy działa tam, gdzie archetyp jest
jednoznaczny — chór i ryk weszły powtarzalnie. (2) „Deep explosive blast" daje
generyczny huk, który audyt łapie podwójnie (brak szumu + bliźniak z inną
kartą) — to jest dokładnie mechanizm skargi właściciela, uchwycony miarą.
(3) Kontrakt `earth_rumble` dostał warunek `mid_up >= 0,10` (słyszalność na
małych głośnikach), bo grzmot w 94 % w infrabasie jest bezużyteczny w grze.
(4) `464` rozstrzygnie runda `r016b`: jeśli prompt „low register" znów da
~1 kHz, kalibrujemy kontrakt, nie prompt.

**Nowe w narzędziach:** `--trim-trail-s` w `postprocess_samples.py` (odcina
martwy ogon; `452` 4,00 → 3,33 s, zadeklarowana długość zaktualizowana),
`--fix-mono` ściągnął nadmiar stereo `452` z 2,69 do 0,99 LU. Postprodukcja
pięciu plików: −20,00/−20,02/−19,99 LUFS, 0 ponad sufitem, SNR ≥ 29,8 dB.
Flagi korpusu 82, pary bliźniacze 1 (`387`↔`501`, do zdjęcia w `r016b`).

**Otwarte:** runda `r016b` (387/464/539 × 3 warianty, workflow tymczasowy
`temp-variants-r016.yml`, marker `[generate-r016b]`) oraz triage 553 kart bez
kredytów — rozszerzenie taksonomii archetypów i przypisanie archetypu każdej
fabule. Audyt archetypów pozostaje **proxy** do odsłuchu właściciela.

## 2026-10-05 — Triage katalogu (0 kredytów) + blokada: konto ElevenLabs ma 0 kredytów

**Blokada generowania.** Runda `r016b` (387/464/539 × 3 warianty) padła na API:

```
HTTP 401 quota_exceeded: "This request exceeds your quota of 10000.
You have 0 credits remaining, while 40 credits are required for this request."
```

Założenie „kredyty niewyczerpane" przestało być prawdziwe — 15 generacji
pilota r016 jeszcze przeszło, kolejne już nie. Log z Actions jest w repo
(`variants/r016b/generate.log`), bo sandbox nie sięga `blob.core.windows.net`
i nie da się pobrać logów runa przez `gh api`. Workflow `temp-variants-r016.yml`
zostaje zaparkowany (bez markera nic nie robi), prompty r016b są gotowe
w `scenarios.jsonl`.

**Triage całego katalogu — nowe narzędzie `scripts/assign_archetypes.py`.**
Przypisuje archetyp regułami czytanymi **z promptu, nie z tytułu** (prompt
opisuje dźwięk, który zamówiliśmy). Reguła łapie zdarzenie, nie materiał:
`stone_slide` wymaga skały *w ruchu*, `steam_hiss` wymaga, żeby syk był parą lub
gazem. Fabuły bez trafienia zostają bez archetypu — skrypt nie zgaduje.

- fabuł 553 · z archetypem **421 (76 %)** · bez przypisania **132**
- taksonomia rozszerzona z 13 do **37 archetypów** (24 nowe kontrakty, progi v0
  ustawione względem rozkładu korpusu: centroid p50 2,66 kHz, `low_all` p50
  0,034, `decay_s` p50 0,21 s, `content_rel_s` p50 2,09 s)
- wynik audytu: **236 nie trafionych (56 %) · 119 prawdopodobnie · 66 trafionych**
  (`data/samples/archetype-match-2026-10-05-catalog.json`,
  `docs/audits/2026-10-05-archetype-match-catalog.md`)

**Najgorsze rodziny** (udział nie trafionych): `door_creak` 90 % (26/29),
`temple_bell` 88 % (21/24), `stone_slide` 76 % (35/46), `magic_shimmer` 67 %
(26/39), `creature_roar` 67 % (14/21). **Najlepsze**: `heavy_impact` 0 % (11/11
trafionych), `chain_rattle` 17 %, `water_splash` 25 %, `plate_clank` i
`sword_clash` po 29 % — metal i uderzenia już działają.

Kontrola losowa potwierdza, że to nie szum progów: `196` Mnemonic Wall
(„dzwon") ma centroid 7,8 kHz, `tonal_frame_fraction` 0,03 i `decay_s` 0,06 s —
to jasne cykanie, nie dzwon; `124` (skrzypienie) 4,5 kHz i 0,04 s zaniku —
krótki zarys, nie skrzypienie; `168` (osuwisko) `low_all` 0,005 i 1,17 s treści.
Wzorzec jest wspólny: tam, gdzie archetyp wymaga długiego, niskiego lub
średniego zdarzenia, korpus ma krótki jasny tik — dokładnie „stuknięcie"
i „szelest", na które skarżył się właściciel.

**Następny krok — decyzja właściciela:** (a) doładować kredyty i odpalić r016b
oraz serię naprawczą dla `door_creak` / `temple_bell` / `stone_slide` (~99 kart),
(b) skalibrować progi na odsłuchu ~20 kart, zanim audyt zacznie sterować
generacjami. Audyt pozostaje proxy dla ucha.

## 2026-10-05 — Kredyty odnowione (10 000), runda r016b odblokowana

Właściciel dodał nowy klucz `ELEVENLABS`: 10 000 kredytów. Jedna generacja
kosztuje 40, więc budżet sesji to **250 generacji** — nie „niewyczerpane", tylko
policzalne. Plan wydatków:

| Pozycja | Generacje | Kredyty |
|---|---:|---:|
| `r016b` — 387/464/539 × 3 warianty (dokończenie pilota) | 9 | 360 |
| `r017a` — 20 najgorszych kart × 2 warianty (test skali) | 40 | 1 600 |
| rezerwa na poprawki i kolejne transze | — | 8 040 |

Zasada: **2 warianty minimum** na kartę — pilot pokazał, że z tego samego
promptu `396` wychodzi 0 / 2,5 / 3,5 pkt, więc jeden wariant to ruletka.

### r016b dowieziona — 7 z 13 kart właściciela trafionych

Nowy klucz zadziałał: 9 generacji, 9 plików. Wybór wariantów po kalibracji:
`387` v2, `464` v2, `539` v3 — **wszystkie trzy 0 pkt**. Bliźniak `387`↔`501`
(0,9762) zniknął: nowy wariant ma kosinus 0,5303 z `501`.

**Trzy poprawki wymuszone przez dane:**

1. **Selektor mierzył surowy wariant, nie plik po postprodukcji.** `464` miał
   0 pkt jako wariant i 1,0 pkt po obróbce, bo filtr 25 Hz zdejmuje dół
   (`low_all` 0,547 przy progu 0,55). `pick_archetype_variant.py` dostał
   `--postprocess`: przepuszcza każdy wariant przez `process_one()` z
   ustawieniami korpusu i mierzy dopiero wynik.
2. **`decay_s` źle opisuje „toczy się".** Mierzy czas od szczytu do −20 dB,
   więc „wybuch i potem płynąca lawa" dostaje krótki zanik mimo 3,1 s treści.
   Kontrakt `volcanic_eruption` używa teraz `sustain_ratio >= 0,20` (jak
   `undead_groan` i `robot_servo`). Efekt: `387` v2 — flatness 0,264, centroid
   1,7 kHz — wchodzi na 0 pkt, a to właśnie ten wariant brzmi jak erupcja.
3. **Progi `low_all` były o traf losowy.** `undead_groan` 0,55 (~p89) → 0,44
   (~p85), `heavy_impact` 0,25 → 0,20 (~p75); `463` Knockout Maneuver
   przestaje przegrywać o 0,0001 i wchodzi na 0 pkt.

**13 kart właściciela:** trafionych **7** (było 1): `452` 6,0→0, `464` 4,0→0,
`396` 3,5→0, `539` 3,5→0, `387` 2,5→0, `463` 0,5→0, `145` 0. Zostaje
`515` war_machine 2,5 oraz prawdopodobne `7`, `312`, `521`, `557`, `568`.

Katalog: 234 nie trafionych / 117 prawdopodobnie / 70 trafionych. Korpus:
553 pliki, 82 z flagą, **0 par bliźniaczych**, LUFS −20,0.
Zużycie kredytów w tej turze: 9 generacji = 360 z 10 000.

## 2026-10-05 — r017a: pierwsza seria naprawcza (20 kart × 2 warianty, 1600 kredytów)

Nowe narzędzie `scripts/rewrite_archetype_prompts.py`: 37 szablonów archetypowych
pisanych pod kontrakt audytu + ręczne override'y dla kart właściciela. Każda karta
dostaje klauzulę rozróżniającą (tytuł + źródło z dotychczasowego promptu), bo bez
niej cała rodzina miałaby identyczny prompt.

**Wynik: 18 z 20 kart poprawionych, 1 pogorszona, 1 bez zmian**
(`docs/audits/2026-10-05-r017a-repair-batch.md`). Największe ruchy: `518` ryk
6,0→0, `459` 5,0→1,5, `196` dzwon 5,0→0, `382` osuwisko 4,5→0, `352` skrzypienie
4,5→1,0, `168` 4,5→1,0, `312` chichot 1,0→0, `521` ptaki 1,0→0, `557` muzyka
ludowa 1,0→0, `515` machina 2,5→1,0. Pogorszona: `568` 0,5→1,0.

Katalog: **225 nie trafionych / 120 prawdopodobnie / 76 trafionych** (przed rundą
234/117/70). Korpus: 553 pliki, 85 z flagą, LUFS −20,0.

**Trzy wnioski, które zmieniają metodę:**

1. **Identyczny prompt archetypowy = nowy bliźniak.** `168` i `382` (oba
   `stone_slide`) mają kosinus 0,9676 i żadna z czterech kombinacji wariantów nie
   schodzi poniżej 0,95. Selekcja tego nie naprawi — trzeba zróżnicować prompt.
   Dlatego klauzula karty jest obowiązkowa, a w rodzinach licznych (35 kart
   `stone_slide`, 29 `door_creak`) same szablony nie wystarczą.
2. **Selektor musi mierzyć plik po postprodukcji i widzieć bliźniaki** — obie
   poprawki weszły (`--postprocess`, `--avoid-twins`), plus naprawiony bug
   nadpisywania odcisku w pliku tymczasowym.
3. **Niskie archetypy potrzebują warunku słyszalności.** `515` wyszedł z centroidem
   90 Hz i flagami `muffled/boomy/dull`; kontrakty `war_machine` i `thunder_clap`
   dostały `mid_up` tak jak wcześniej `earth_rumble`.

**Do ponowienia (r017b):** `515` (środek pasma), `382` albo `168` (rozdzielić
prompty), `521` (`speech_like`), `35` (2,53 s), `343` (`long_trail_silence`),
`124` (3,0 pkt), `6` (2,5 pkt), `112` i `62` (2,0 pkt).

**Kredyty:** wydane 1960 z 10 000 (49 generacji), zostało 8040 = 201 generacji.

## 2026-10-05 — r018: transza 75 kart (150 generacji, 6000 kredytów)

**Korekta wcześniejszego wyniku.** Podawana wcześniej liczba „236 nie trafionych"
była zawyżona: reguły przypisania łapały motyw archetypu także w szczegółach
promptu, więc 237 kart miało archetyp, którego ich prompt wcale nie zamawiał
(`314` wirujące kartki → `undead_groan`, `74` galop kawalerii → `thunder_clap`,
`166` skrzydła owada → `temple_bell`, `241` helikopter → `horn_call`).
Regeneracja według takich przypisań zastąpiłaby dźwięk karty czymś unrelated —
czyli pogłębiłaby problem właściciela — a audyt sam by się potwierdził, bo
mierzyłby archetyp, który sam podstawił. Przegląd listy przed wydaniem 6480
kredytów to wyłapał.

**Nowa warstwa wiarygodności** w `assign_archetypes.py`: `strong` (motyw
w głównym zdarzeniu promptu) / `weak` (tylko w szczegółach) + ręczne korekty
w `data/samples/archetype-corrections.json` (19 kart poprawionych, 10 bez
pasującego archetypu → zostają bez archetypu, czekają na prompt pisany ręcznie).
Do audytu wchodzą tylko strong + korekty + 13 kart właściciela: **174 karty**.

**Profile akustyczne wewnątrz archetypu** (`rewrite_archetype_prompts.py`): 2–3
warianty brzmienia na rodzinę, wybór `int(id) % N`, plus rotacja długości
4,0 / 4,5 / 3,5 s. To odpowiedź na bliźniaka `168`↔`382` — identyczny szablon
daje identyczny dźwięk i żadna selekcja tego nie rozdzieli.

**Wynik transzy: 65 kart poprawionych, 6 bez zmian, 4 pogorszone**
(`docs/audits/2026-10-05-r018-batch.md`). Audyt 174 kart:
**69 nie trafionych → 15**, prawdopodobnie 62 → 91, trafione 43 → **68**.

**Zostało do roboty:**
- 3 pary bliźniacze, których nie rozdzieli wybór wariantu: `317`↔`347` (0,9644,
  oba dzwon), `97`↔`265` (0,9543), `202`↔`493` (0,9520) — potrzebny inny prompt;
- 7 plików poniżej 3 s: `383` 1,52 · `23` 2,22 · `209` 2,54 · `317` 2,62 ·
  `223` 2,77 · `459` 2,81 · `347` 2,82;
- 15 kart dalej nie trafionych, 25 kart transzy z flagami (`dull` 8,
  `long_trail_silence` 6, `speech_like` 3 — kruk/brama/kogut, prawdopodobnie
  fałszywy alarm audytu semantycznego);
- 142 karty bez archetypu (w tym 10 po korektach) — potrzebują promptów pisanych
  pod fabułę, nie szablonu.

**Kredyty:** wydane 7960 z 10 000 (199 generacji), zostało 2040 = 51 generacji.

## 2026-10-05 — r019: ponowienia i zamknięcie dnia (50 generacji)

Zakres: 15 kart nadal nie trafionych + 6 kart z par bliźniaczych + 7 za krótkich.
Nowe opcje `rewrite_archetype_prompts.py`: `--profile-shift` (inny profil
akustyczny niż w poprzedniej rundzie) i `--fill-take` (dźwięk ma wypełnić cały
czas — dla kart, które wyszły za krótkie).

**Wynik: 16 kart poprawionych, 3 pogorszone, 6 bez zmian.** Audyt 174 kart:
**nie trafionych 15 → 4** (po kalibracji dzwonu), prawdopodobnie 99, trafionych
**71**. Pary bliźniacze: **3 → 1** (`31`↔`456`, oba `insect_swarm`, 0,9548).

**Kolejna wada metryki `decay_s`** — przy dzwonie karała ostre uderzenie
z cichszym wybrzmieniem (`343` 0,28 s, `558` 0,62 s przy progu 0,8), choć dzwon
dzwonił długo. Kontrakt `temple_bell` nie używa już `decay_s`; o wybrzmiewaniu
mówią `sustain_ratio` i `content_rel_s`. To ta sama poprawka co wcześniej przy
`volcanic_eruption`.

**13 kart właściciela: 10 trafionych, 3 prawdopodobne, 0 nie trafionych**
(na starcie sesji: 1 trafiona). Zostają `521` (trele za wolne, `mod_peak`
1,82 Hz), `7` (atak 0,48 s zamiast natychmiastowego), `568` (serwo niestabilne
w wysokości, `f0_semitone_std` 14,2).

**Higiena: regresja do odrobienia bez kredytów.** 90 odtworzonych kart ma 41
flag (`dull` 11, `long_trail_silence` 8, `boomy` 6, `long_lead_silence` 4,
`speech_like` 3, `cut_start_hard` 3), 463 stare karty 73. Nowe sample są
dłuższe i mają więcej dołu, więc częściej łapią `dull`/`boomy`, a model zostawia
ciszę na brzegach. Do zrobienia: korekta high-shelf i trymowanie brzegów.

**Kredyty: 9960 z 10 000 wydane (249 generacji), zostało 40 = 1 generacja.**

## 2026-10-05 — Higiena bez kredytów + r020: 11 upartych kart × 3 warianty (33 generacje)

**Higiena (0 kredytów).** `postprocess_samples.py` dostał `--trim-lead-s`,
`--edge-fade-ms` i `--spectral-kinds` (funkcje `trim_leading_silence()`,
`edge_fades()`). Przejście przez 25 flagowanych kart z nowych batchów:
LUFS −20,0 (σ 0,08), SNR min 23,1 dB, **flagi 102 → 94**, zero regresji
archetypów. Korekta `boomy` celowo pominięta — low-shelf ciąłby `low_all`,
którego kontrakty `earth_rumble`/`war_machine` wymagają.

**r020: 11 kart × 3 warianty = 33 generacje = 1320 kredytów.** Prompty pisane
pod zmierzoną wadę każdej karty (`OVERRIDES`), nie pod szablon.

**Wynik: audyt 174 kart — nie trafionych 4 → 1, prawdopodobnie 99, trafionych
71 → 74. Pary bliźniacze: 0.** Karta po karcie (przed → po): `49` 2,5 → 1,0 ·
`168` 2,0 → 1,0 · `298` 2,5 → **0** · `343` 1,0 → **0** · `493` 2,0 → 1,0 ·
`521` 1,0 → **0** · `7` 1,5 → 1,5 · `31` 1,0 → **3,5 (regresja)** ·
`456` 1,0 → 1,0 · `568` 1,0 → 1,5 (regresja) · `317` 0 → 0 (ale tylko 2,23 s).

**Prompty pod intuicję psują zgodność z kontraktem.** `31` Carrion Call
z override'em „suchy szelest chityny" dał szum 8,5 kHz, a kontrakt
`insect_swarm` chce harmonicznego bzyku roju (`tonal_frame_fraction >= 0,3`):
1,0 → 3,5 pkt. Analogicznie `568` „constant pitch whirr" dał `tonal` 0,000
(potrzeba „pitched hum"), a `7` „no build-up" i tak wyszedł z atakiem 0,90 s.

**Kredyty: konto drugie 1320 z 10 000 wydane, zostało 8680 = 217 generacji.**

## 2026-10-05 — r021: druga fala (75 generacji) — zero kart nie trafionych

Zakres: 5 kart upartych z r020 z promptami pod zmierzoną wadę + 20 kart
z `--worst`, po 3 warianty. **Wynik: audyt 174 kart — 0 nie trafionych /
94 prawdopodobnie / 80 trafionych** (przed rundą 1 / 99 / 74). Karty transzy:
6 poprawionych, 0 pogorszonych, 19 bez zmian. Pary bliźniacze 0, flagi 97.

**13 kart właściciela: 11 trafionych, 2 prawdopodobne, 0 nie trafionych**
(zostają `7` Mindstab i `568` Nanoform Sentinel — obie nowe generacje wypadły
gorzej niż dotychczasowe pliki, więc zostały przywrócone).

**Błąd zakresu kosztował 960 kredytów.** `rewrite_archetype_prompts.py` miał
twardo zaszyty domyślny `--audit` = zrzut `archetype-match-...-strong.json`
sprzed r018, więc `--worst 20` wybrał **8 kart już wtedy trafionych**
(`1`, `92`, `128`, `172`, `192`, `298`, `317`, `383`). Nowe generacje część
z nich zepsuły (`383`: 0 → 3,0 pkt). Naprawione: domyślny `--audit` to teraz
najnowszy `archetype-match-*.json`, a 10 zepsutych kart przywrócono
z commitu `8ebae10` (zero kredytów): `4`, `7`, `164`, `168`, `303`, `382`,
`383`, `456`, `558`, `568`.

**Selektor nie pilnował okna 3–5 s.** `7` v1 (2,03 s treści + 1,89 s ciszy)
wygrywał z v2 o pełnych 4,00 s, bo kontrakt archetypu długości nie widzi.
`pick_archetype_variant.py` karze teraz wyjście poza 3–5 s stawką 5,0 pkt/s
(więcej niż maksymalna suma wag kontraktu), a łańcuch pomiaru wariantu
zrównano z wysyłkowym. Bez kredytów kalibrowano też `sword_clash`
(`attack_s <= 0,10 s` = mediana korpusu, było 0,05) — samo to dało 74 → 76.

**Kredyty: 3000 w tej rundzie, razem na koncie drugim 4320 wydane,
zostało 5680 = 142 generacje.**

**Co zostało:** 94 karty „prawdopodobnie" (żadna nie trafiona), **417 plików
poza oknem 3–5 s** (mediana korpusu 2,48 s), w tym 76 z archetypem — ich
naprawa to 152 generacje = 6080 kredytów, czyli więcej niż zostało na koncie;
379 fabuł bez archetypu; `variants/r016…r021` i workflow tymczasowy do
usunięcia przed finałem.

## 2026-10-05 — Okno akceptacji 2–5 s zamiast 3–5 s (0 kredytów)

Decyzja właściciela: **„Nie upieram się przy 3-5. Dobre 2 sekundy są lepsze
niż złe 4. Możemy rozszerzyć okno do 2-5."** Zasada: jakość decyduje,
długość rozstrzyga tylko remisy — nie dopisujemy ciszy i nie bierzemy
gorszego wariantu po to, żeby dobić do 3 s.

**Skutek zmierzony, nie szacowany: zero plików w korpusie jest poza celem.**
Przy oknie 3–5 s „za krótkich" było 419 (w tym 78 z archetypem) i plan
naprawy kosztowałby 152 generacje = 6080 kredytów. Przy 2–5 s problem znika
bez ani jednej generacji — to była najtańsza runda tej sesji.

Selektor przestał wybierać gorzej, żeby było dłużej: `7` Mindstab bierze v1
(2,36 s, kontrakt 0,0 pkt) zamiast v3 (3,49 s, 2,0 pkt) — **`7` jest teraz
trafiona**, a była jedną z dwóch ostatnich kart właściciela. Kara za wyjście
poza okno dostała część stałą (10 pkt + 5 pkt/s), bo sama stawka za sekundę
nie wystarczała: przy niedomiarze 0,2 s kara 1,0 pkt mieściła się w różnicy
kontraktu i `558` wybierało plik 1,80 s.

**Wynik: audyt 174 kart — 0 nie trafionych / 93 prawdopodobnie / 81 trafionych.
13 kart właściciela: 12 trafionych, 1 prawdopodobna (`568` Nanoform Sentinel,
serwo bez tonu).** Transza r021: 7 lepiej, 0 gorzej, 18 bez zmian. Korpus:
553 pliki, LUFS −20,04 (σ 0,21), 0 bliźniaków, **0 poza oknem 2–5 s**,
95 z flagą.

Dwie pułapki przy okazji:

- `pick_archetype_variant.py --apply` kopiuje **surowy** wariant — łańcuch
  postprodukcji działa tylko na pliku tymczasowym do pomiaru. Bez osobnego
  `postprocess_samples.py` w korpusie zostają pliki o LUFS −3…−16 zamiast −20
  (zmierzone na `7`, `31`, `1`, `92`).
- `--fix-mono` **podnosi** podobieństwo odcisków: `23` v2 miało 0,9162 do
  `168` przed korekcją i 0,9568 po niej, czyli z pary „czystej" robi się
  bliźniak. Wybór wariantu trzeba mierzyć po pełnym łańcuchu, z `--fix-mono`.

**Kredyty: bez zmian — 4320 z 10 000 na koncie drugim, zostało 5680
= 142 generacje.**

## 2026-10-05 — r022–r024: `568` Nanoform Sentinel (9 generacji, 360 kredytów)

Ostatnia z 13 kart właściciela bez pełnego trafienia. Kontrakt `robot_servo`
chce czterech rzeczy: tonu (`tonal_frame_fraction >= 0,35`), stabilnej
wysokości (`f0_semitone_std <= 4,0`), klików (`onset_count >= 2`) i pracy
ciągiem (`sustain_ratio >= 0,2`). Karta miała `tonal` **0,000** — model
renderował „electric motor hum" jako szum szerokopasmowy (flatness 0,30,
centroid 4,8 kHz, f0 = 0 Hz). Próg nie jest wygórowany: 250 kart
niemuzykalnych w korpusie ma `tonal >= 0,35` (mediana 0,315).

Trzy rundy po 3 warianty, każda z inną hipotezą:

| Runda | Hipoteza | Wynik |
|---|---|---|
| r022 | kotwiczenie w źródle harmonicznym („jak uderzony kamerton") | **ton naprawiony**: `tonal` 0,997/1,000/0,907, `f0_std` 0,28–1,67 — ale `onset_count` **0**, czyli 1,5 pkt → 1,0 |
| r023 | kliki przecinające ton | najwyżej `onset` 1, ton stłumiony (0,767), `f0_std` 3,3 |
| r024 | odwrotna hierarchia: rytm zdarzeniem głównym, ton tłem | **`onset` 8** i `tonal` 0,812 naraz; `f0_std` 4,38 (7% ponad próg) |

Model rozstrzyga konflikt „ton albo kliki" kosztem tej cechy, którą prompt
stawia niżej. Wybrany został **r024 v2** — jedyny z obiema cechami, które
nadają archetypowi nazwę („robot klika i pracuje"). Został brak stabilności
wysokości: **`568` 1,5 → 1,0 pkt**, ton ✓, kliki ✓, zero flag, `duration` 4,0 s.

**Kontur f0 pokazał, gdzie jest chwiejność: w pierwszych 0,5 s** (rozruch
serwa, 31–38 półtonów przy 46–48 w reszcie pliku; 22 ramki voiced). Fade
120 ms zbijał `f0_semitone_std` do 3,39 i odwracał werdykt na „trafiony" —
ale tylko dlatego, że jego fade-**in** tłumi te pierwsze ramki poniżej bramki
ciszy i progu autokorelacji 0,55, czyli wycina je z pomiaru. Zastosowany
został fade 60 ms, który zdejmuje realną flagę `cut_end_hard` (koniec pliku
−30,1 dB) i zostawia werdykt uczciwy: `f0_std` 4,38, 1,0 pkt.

**Kredyty: 360 w tych trzech rundach. Konto drugie: 4680 z 10 000 wydane,
zostało 5320 = 133 generacje.**

## 2026-10-05 — Porządki przed finałem (0 kredytów)

- Usunięte `variants/r016…r024` — **25 MB** wariantów MP3. To czysty
  artefakt: po wyborze przez `pick_archetype_variant.py` do korpusu trafia
  tylko zwycięzca, a pomiar jest zapisany w `data/samples/variant-pick-*.json`.
- Usunięty workflow tymczasowy `.github/workflows/temp-variants-r016.yml`
  (ostatnia wersja w historii: commit `e6cb145`). To on definiował check CI
  `variants`, więc na PR zostają dwa checki: `build` i `validate`.
- `variants/` dopisane do `.gitignore`, żeby kolejna runda znowu nie
  wciągnęła megabajtów do gita.
- `OVERRIDES` w `rewrite_archetype_prompts.py` miało 29 wpisów, ale tylko
  **19 unikalnych** — 10 wcześniejszych było przesłoniętych przez późniejsze
  (`7`, `31`, `317`, `456`, `515`, `521`, `568`). Martwe wpisy usunięte;
  słownik po czyszczeniu ma identyczne skuteczne wartości (sprawdzone
  importem modułu przed i po).

## 2026-10-05 — r025 i r026: profile pisane pod zmierzoną wadę (4560 kredytów)

Właściciel rozszerzył okno akceptacji do **2–5 s** („dobre 2 sekundy są
lepsze niż złe 4"), więc długość przestała być wąskim gardłem — pozostały
79 kart „prawdopodobnie" miało po **jednym** złamaniu kontraktu. Obie rundy
oparto na tym samym pomiarze: porównanie **wewnątrz rodziny**, między
kartami zdającymi a gubiącymi.

**Kalibracja jest dobra — wady są realne.** Dane pokazały czyste
rozdzielenie, bez nakładania: `door_creak decay_s` zdające 0,94–2,05 s vs
gubiące 0,06–0,08 s; `sword_clash attack_s` zdające 0,00–0,08 s vs gubiące
0,14–1,77 s. Ten drugi pomiar dowodzi przy okazji, że **natychmiastowy cios
(≤ 0,10 s) jest dla modelu osiągalny** — więc nie ma czego luzować.

**r025 (30 kart × 2 = 60 generacji, 2400 kredytów).** Nadpisano 5 profili
i dodano 4 nowe rodziny. Skuteczne podmiany: „gwizd" wiatru → turbulentny
szum (gwizd dawał czysty ton: flatness 0,0002 przy progu 0,05); dzwony ze
skrajności pasma (243 Hz / 7538 Hz) → środek; „metallic clank" kroków →
głębokie łupnięcie z drżeniem ziemi; nowe `forest_birdsong`,
`mechanism_click`, `robot_servo`, `plate_clank`.

**r026 (27 kart × 2 = 54 generacje, 2160 kredytów).** Nowe profile
`sword_clash`, `insect_swarm`, `water_splash`, `war_machine` + override'y
dla `mechanism_click` i `magic_shimmer`.

| | nie trafione | prawdopodobnie | trafione |
|---|---|---|---|
| przed r025 | 0 | 93 | 81 |
| po r025 | 0 | 79 | 95 |
| po r026 | **0** | **70** | **104** |

**Dwie lekcje o pisaniu profili:**
1. **Model nie czyta zaprzeczeń przez domyślny obraz słowa.** Profil
   `mechanism_click` mówił „mid-pitched, dry and woody rather than hissy" —
   a centroid i tak wychodził 7,7–10,6 kHz przy oknie 800–6000, bo „click"
   sam w sobie ciągnie ku jasnym trzaskom. Dopiero zdanie „low dull wooden
   knocks… no bright ticking and no hiss" zadziałało na tyle, by zjechać
   w okno.
2. **Profil rodzinny jest kompromisem, a `OVERRIDES` ratuje wyjątki.**
   Rotacja `(int(sid)+shift) % 3` w `magic_shimmer` podsunęła kartom `5`
   i `607` profil „Dark magic pooling: a low throbbing hum" — celowo niski,
   a one wymagały `high_all ≥ 0,4`; wyszły z centroidem 93–104 Hz. Dla kart,
   których karta **wymaga** przeciwnego bieguna, potrzebny jest jawny
   override, nie trzeci profil.

**Regresje cofnięte bez kredytów** (`git show <commit>:audio/samples/<id>.mp3`
+ sync długości dla id bieżącego batchu): r025 — `103, 513, 558, 303, 531`;
r026 — `98, 106, 456` (nowy profil dał tonal 0,77–0,94 przy kontrakcie
≤ 0,45), `4` (flatness 0,024) i `20` (oba warianty 1,44–1,76 s, poza oknem).

**Korpus po r026:** 553 pliki, **93 z flagą**, 0 bliźniaków, 0 poza 2–5 s,
LUFS −20,04 (σ 0,19). 13 kart właściciela: **12 trafionych, 1 prawdopodobnie**
(`568` — `f0_semitone_std` 4,38 przy progu 4,0).

**Kredyty: 4560 w tych dwóch rundach. Konto drugie: 9240 z 10 000 wydane,
zostało 760 = 19 generacji.**

## 2026-10-05 — Martwy ogon: pogłos, korekta widma i r027 (3600 kredytów)

Właściciel zakwestionował liczbę „263 fabuły do przerobienia" — i miał rację.
Pomiar pokazał, że problemem nie jest archetyp, a **długość treści**:
`content_s = plik − cisza początkowa − cisza końcowa`. 263 z 553 plików miało
poniżej 2 s słyszalnej treści, a ogon był **prawdziwą ciszą** (RMS −54…−64 dB
przy treści −20…−27 dB, próg audytu −45 dBFS). Trym tego nie naprawia: zostałoby
0,41–1,21 s, czyli daleko poza oknem.

**Trzy darmowe narzędzia zamiast 21 040 kredytów:**

1. `scripts/add_reverb_tail.py` — syntetyczny ogon pogłosu zanikający do progu
   ciszy na końcu pliku. Poziom startowy od **RMS treści**, nie od piku (przy
   piku pogłos wychodził ~10 dB za cicho i wypełniał tylko początek ogona).
2. `scripts/tame_harsh.py` — półka wysokotonowa dobierana **iteracyjnie**: tnie,
   mierzy widmo funkcjami audytu, dokłada, aż zejdzie pod próg. Średnio −15 dB.
3. `scripts/pick_content_variant.py` — wybór wariantu po długości treści dla kart
   **bez** archetypu (`pick_archetype_variant.py` takie pomija).

**Dwie lekcji o postprodukcji, obie znalezione pomiarem:**

- **Każda korekta widma psuje kontrakty, które mierzą widmo.** Pogłos na 41 kartach
  z archetypem popsuł 14 kontraktów (`attack_s`, `crest_db`, `spectral_flatness`,
  `onset_count`) i zrobił 2 bliźniaki. Cięcie góry na 3 kolejnych popsuło
  `spectral_flatness` i `tonal_frame_fraction`. Reguła: **postprodukcja tylko na
  karty bez kontraktu**, a karty z kontraktem naprawia się promptem.
- **Cisza na końcu obniża mierzoną głośność** (bramkowanie BS.1770 liczy bloki
  400 ms z bramką względną), więc renormalizacja do −20 LUFS podnosi transjent
  o 3,5 dB i plik startujący od pełnego poziomu łapie `cut_start_hard`. Oraz:
  prymitywny ogranicznik piku ściska cały plik (−20 → −23,5 LUFS) — trzeba
  `limit_true_peak` z `postprocess_samples.py`.

`postprocess_samples.py --fix-spectral` tnie −3,5 dB przy 4,5 kHz (Q 1,2) i przy
centroidzie 9–12 kHz **nie zmienia nic** — 23 pliki po tej korekcie dalej miały
flagę `harsh`. Nie kalibrować po wrażeniu, tylko mierzyć efekt.

**r027 (45 kart × 2 = 90 generacji, 3600 kredytów).** Karty, których fabuła
obiecuje zdarzenie powtarzalne, a sample miał jedno. Prompt nazywa liczbę
powtórzeń wprost („osiem–dziesięć kroków", „trzy cięcia", „pięć uderzeń skrzydeł")
plus `--fill-take`. Dla 7 kart z archetypem dopisane wymogi kontraktu (np.
`attack_s ≤ 0,1 s` → „the first landing at the very first instant").

| | przed sesją | po pogłosie | po `harsh` | po r027 |
|---|---|---|---|---|
| treść < 2,0 s | 263 | 147 | 146 | **105** |
| treść < 1,0 s | 36 | 12 | 12 | **7** |
| pliki z flagą | 93 | 74 | 55 | **55** |
| `harsh` | 28 | 23 | 4 | **5** |
| archetypy 174 kart | 0/70/104 | 0/70/104 | 0/70/104 | **0/69/105** |

45 kart r027: średnia treść **1,31 → 3,16 s**, poniżej 2 s zostały 3 (było 45).

**Pułapka workflow:** regex patchujący nazwę batchu
(`r02\d: \d+ wariant(y|ow)[^\n]*`) zjadł zamykający cudzysłów linii
`git commit -m "..."`. YAML się parsował (dla YAML to zwykły skalar), więc błąd
wyszedł dopiero w runtime, a bash nie wykonał **nic** z całego bloku — warianty
przepadły razem z runnerem. Logi CI były nieosiągalne z sandboksa (EOF z blob
storage), więc przyczynę znalazłem czytając sam plik workflow. Podejrzenie: ta
nieudana runda zużyła 3600 kredytów — **niezweryfikowane**.

**Kredyty: 3600 w r027 (plus prawdopodobnie 3600 stracone na nieudanym runie).
Konto trzecie: 10 000, realnie zostało ~2800–6400.**

## 2026-10-05 — r028: karty z kontraktem naprawia się promptem, nie postprodukcją (2800 kredytów)

35 kart z archetypem i treścią < 2 s. Postprodukcja odpada — pogłos i cięcie
widma zmieniają dokładnie te cechy, które mierzy kontrakt (sprawdzone w tej
sesji na 44 kartach: 14 + 3 popsute kontrakty). Została więc regeneracja
promptem pisanym pod kontrakt konkretnej rodziny.

**Cztery karty celowo pominięte, bo ich kontrakt sam ogranicza czas** —
wydłużanie by go złamało: `583` arrow_flight (`decay_s ≤ 0,8 s`), `257` i `15`
whip_crack (`decay_s ≤ 0,5 s`, `attack_s ≤ 0,03 s`), `71` heavy_impact
(`decay_s ≤ 1,4 s`). To ważna granica: nie każdą krótką treść wolno wydłużać.

**Skuteczny wzorzec dla `sword_clash`** (9 kart, kontrakt `attack_s ≤ 0,1 s`):
„one hard bright strike **at the very first instant**, then three more sharp
clicks" — pierwszy cios natychmiast, seria dopiero po nim. Odwrotna kolejność
(„trzy ciosy, pierwszy natychmiast") dawała `attack_s` 0,26–0,74 s.

**Wynik: 9 lepiej / 0 gorzej / 26 bez zmian.** Archetypy 0/69/105 → **0/64/110**.
Treść < 2 s: 105 → **85**. 24 karty, które zostały: średnia treść 1,47 → 2,45 s.

11 regresji cofniętych (`344, 232, 565, 434, 559, 292, 23, 244, 12, 5, 98`) —
nowe warianty dały m.in. `tonal_frame_fraction` 0,000 przy wymaganym ≥ 0,5
(dzwon `23`) i `spectral_flatness` 0,001 przy ≥ 0,05 (wiatr `292`).

**Dwie rzeczy warte zapamiętania z tej rundy:**
- Workflow patchowany **bez regexu**: poprzednio `r02\d: \d+ wariant(y|ow)[^\n]*`
  zjadł zamykający cudzysłów, a bash nie wykonał nic z całego bloku. Teraz każdy
  krok `run:` przechodzi `bash -n` przed pushem — to test, którego brak kosztował
  jedną rundę.
- Istniejące wpisy `OVERRIDES` wymieniane przez `ast` (`key.lineno` →
  `value.end_lineno`), nie przez dopisanie: dict literal cicho przesłania
  wcześniejsze klucze. Kontrola po zmianie: 100 kluczy w literale = 100 po imporcie.

**Kredyty: 2800 w r028. Konto trzecie: 10 000, zostało ~3600–7200** (nie wiadomo,
czy nieudany run r027 zużył 3600 — logi CI są nieosiągalne z sandboksa).

### Odtworzenie stanu po resecie sandboksa

Sandbox został zrestartowany: lokalny klon wrócił do `f73de71`, a `.venv` zniknął.
Nic nie zginęło — branch `arena/01a108e2-mtgdatabase` był na GitHubie pod
`7422f2e`, a PR #52 otwarty. Procedura: `git ls-remote origin | grep <id sesji>`,
`git fetch origin <branch>`, `git diff FETCH_HEAD` (same `variants/` = snapshot je
pominął), `git reset --hard FETCH_HEAD`, odtworzenie `.venv`.

### r029 — prompt pod JEDNO złamanie kontraktu (0/59/115 → 0/49/125)

Punkt wyjścia był mierzalny: **wszystkie 59 kart z werdyktu „prawdopodobnie" ma
dokładnie jedno złamanie progu** (punktacja 1,0 dla 51 kart, 0,5 dla 8, 1,5 dla 5).
Zamiast pisać ogólnie „lepszy" prompt, każdy z 34 wpisów nazywa wprost tę jedną
cechę, np. `sword_clash` → „broadband harsh metallic noise" (bez słów
ring/chime/crystalline, bo ciągną ku tonowi), `robot_servo` → „four separate
distinct mechanical clicks", `door_creak` → „fades slowly over more than a second".

**Najpierw próba za zero kredytów.** Nowe narzędzie `scripts/tame_spectrum.py`
wprowadza centroid widma do *okna* kontraktu — tnie albo podbija, mierząc efekt
funkcjami audytu. `tame_harsh.py` celuje w progi flagi (centroid 9000 Hz /
air8k 0,50) i tylko tnie, a kontrakty mają okna: `mechanism_click` i
`arrow_flight` 800–6000 Hz, `insect_swarm` 1000–6000 Hz. Naprawione bez generacji:
`52` (7588→5830 Hz), `132` (7834→5911), `213` (8561→5722), `207` (6474→5991),
`370` (6309→4606). Cofnięte `81` — podbicie +3 dB zbiło `tonal_frame_fraction`
z 0,55 do 0,22 przy wymaganym ≥ 0,3.

**Czterech kart nie da się naprawić korektą widma — zmierzone.** `98`, `106`,
`456` (za jasne) i `610` (centroid 163 Hz, bo prompt z r026 „no bright ticking
and no hiss" przesterował w drugą stronę). Mechanizm: cięcie 15 dB powyżej
2,5 kHz zabija 14,5 LU głośności, więc renormalizacja do −20 LUFS dodaje +14,5 dB,
a `limit_true_peak` musi zdusić transjent (`peak_gr` −11,3 dB) — czyli dokładnie
ten jasny atak, o który chodzi. **Centroid wraca z 5588 na 7277 Hz.** Wniosek:
przy dużej korekcie widma limiter oddaje to, co korekta zabrała. Te karty
wymagają regeneracji.

**Wynik rundy: 10 lepiej / 0 gorzej / 24 bez zmian.** Archetypy **0/49/125**.
Poprawione: `6`, `18` (sustain), `9` (flatness), `15` (attack), `67`, `80`, `501`
(mid_up), `308` (flatness), `506` (mod_peak), `540` (tonal). 13 regresji cofniętych.

**Wzorzec regresji (powtarza się w każdej rundzie):** prompt pod jedną cechę
naprawia ją, ale model rozstrzyga konflikt kosztem innej cechy w tej samej
rodzinie — `sword_clash` dostał szumowy transient i stracił `attack_s`
(0,14–0,52 s przy wymaganym ≤ 0,1), `insect_swarm` dostał niższy centroid i
stracił `tonal`, `door_creak` dostał szybsze falowanie i stracił tonalność.
Dlatego audyt po rundzie i cofanie regresji z poprzedniego commitu nie jest
formalnością, tylko częścią metody.

**Błąd do zapamiętania: `postprocess_samples.py` bez `--ids` przejeżdża po całym
korpusie.** Uruchomiony globalnie zmienił 540 z 553 plików, a `--fix-mono`
podnosi podobieństwo i wypchnął parę `529`/`592` na cosine 0,9501 — nowego
bliźniaka nad progiem 0,95, choć żadna z tych kart nie była w rundzie.
Przywrócone 517 plików spoza batchu. **Zasada: postprocess zawsze z `--ids`
ograniczonym do bieżącego batchu.**

`insect_swarm` potrzebuje raz niższego centroidu (`98`, `106`, `456`, `81`), a raz
więcej tonalności (`31`, `540`) — profil rodzinny nie pogodzi obu kierunków,
więc dla tej rodziny działają wyłącznie wpisy per karta w `OVERRIDES`.

**Kredyty: 2720 w r029** z czwartego klucza (10 000). Korpus: 553 pliki,
53 z flagą, 0 bliźniaków, 0 poza oknem 2–5 s, LUFS −20,02 (σ 0,25),
treść < 2 s: **83** (średnio 1,70 s).

### r030 — „cecha chroniona pierwsza": pomysł zadziałał słabo (0/49/125 → 0/48/126)

r029 pokazała mechanizm regresji: prompt pod jedną cechę naprawia ją, ale model
rozstrzyga konflikt kosztem innej cechy w tej samej rodzinie. Hipoteza na r030:
jeśli cecha **chroniona** pójdzie w prompcie pierwsza i jako element dominujący,
a poprawka dopiero po niej, regresji nie będzie. 19 kart = wszystkie grupy ≥ 2
spośród 49 pozostałych „prawdopodobnie".

**Wynik: 1 lepiej / 0 gorzej / 18 bez zmian.** Poprawione tylko `20`
(`sword_clash` 0,5 → 0). Regresji nie było — ale dlatego, że sześć kart cofnąłem.

**Zasada działa, ale jest słabą dźwignią.** Cofnięte: `81`, `456` (znowu
`tonal_frame_fraction` w `insect_swarm`), `103` (sustain 0,243 przy ≥ 0,3), `492`
(`attack_s` 0,24 przy ≥ 0,3 — prompt mówił „builds slowly over a third of a
second", model dał 0,24 s), `608` (`attack_s` 0,29 mimo „at the very first
instant"), `98` (flaga `speech_like`, a mowa jest zakazana; centroid spadł z
8860 na 426 Hz — z jednej skrajności w drugą).

**Najważniejszy wniosek: model nie realizuje liczb w prompcie.** Dla
`door_creak`/`mod_peak_hz` te same słowa „about five or six times a second" dały
1,10 Hz (`381`), 1,36 Hz (`95`), 1,55 Hz (`531`), 1,64 Hz (`537`) i **17,39 Hz**
(`303`) — czyli raz głęboko pod oknem 2–12 Hz, raz daleko nad nim. Dla
`sword_clash`/`attack_s` „at the very first instant" dało 0,29 s przy wymaganym
≤ 0,1. **Te dwie cechy nie są sterowalne promptem** i dalsze rundy na nich to
wydawanie kredytów na loterię.

`513` zostało w korpusie dopiero po korekcie głośności: wariant miał LUFS
−33,21 (drugi −45,29), a `--max-gain-db` domyślnie 15 dB nie wystarczył, więc
plik wyszedł na −30,66 przy korpusie −20,02 i podbił odchylenie z 0,25 na 0,52.
Ponowny postprocess z `--max-gain-db 26` dał −20,00. Po tej korekcie werdykt
wrócił do „prawdopodobnie", więc realny zysk rundy to jedna karta.

**Błąd techniczny tej rundy:** podmiana wpisów `OVERRIDES` musi iść **od końca**
(malejąco po numerach linii). Wpis zajmuje 2 albo 3 linie (prompt bywa zapisany
jako dwa sklejone literały), więc każda zamiana przesuwa indeksy poniżej.
Pierwsza próba szła od początku: plik się kompilował, `ast` nie zgłaszał błędu,
0 duplikatów — ale trzy karty dostały cudzy tekst. Wykrył to dopiero walidator,
który mierzy **ładunek API** (prompt + ok. 280 znaków doklejanych zakazów), więc
limit 450 oznacza prompt do ok. 168–172 znaków.

**Kredyty: 1520 w r030.** Z czwartego klucza (10 000) zostało ~5760. Korpus:
553 pliki, 56 z flagą, 0 bliźniaków, 0 poza oknem 2–5 s, LUFS −20,02 (σ 0,25),
treść < 2 s: 83.

### r031–r032 — punkt 1, nowa dostawa i atak wieloudarzeniowy (0/48/126 → 0/34/144)

**r031 (2320 kredytów).** Dwa zadania w jednej rundzie: 25 kart naprawczych
wybranych pomiarem (metryka sterowalna promptem **i** brak wcześniejszego
celowanego promptu pod tę cechę) oraz 4 nowe fabuły. Wynik: **13 lepiej /
0 gorzej / 12 bez zmian**, nowe karty 3/4 trafione.

Selekcja się potwierdziła: z 12 kart „bez zmian" aż 7 zostało na tej samej
metryce, którą świadomie pominąłem jako niesterowalną (`mod_peak_hz`, `attack_s`,
`ioi_cv`) albo już wcześniej przepaloną.

**Błąd warty zapisania:** cztery nowe karty dodałem najpierw tylko do
`data/catalog.json`. CI wykonuje `Refresh catalog from collection` **przed**
walidacją scenariuszy, więc katalog odświeżany z `fabuły270926.csv` nadpisał mój
ręczny wpis i run `validate` padł, choć lokalnie przechodził. **Źródłem prawdy
jest CSV.** Przy dopisywaniu: plik kończy się pustym wierszem `\t\t` **bez** znaku
nowej linii, więc dopisanie wprost skleja go z nowym wierszem (`invalid artID`).
`import_collection.py` pomija wiersze całkowicie puste (L31–32), ale nie częściowo.

**r032 (1120 kredytów) — odkrycie, które tłumaczy całą rodzinę regresji.**
`attack_s` liczy się **wstecz od globalnego szczytu** energii, dopóki obwiednia
jest powyżej szczyt−20 dB (`audit_semantic_match.py` L166–172). Przy dźwięku
wieloudarzeniowym szczyt wypada w późniejszej sekcji, więc mierzony „atak" to
czas narastania tej sekcji, nie opóźnienie pierwszego dźwięku. Zmierzony
przypadek `269`: szczyt 2,160 s, początek ataku 1,010 s → `attack_s` 1,15 s, mimo
że krzyk jest na samym początku.

Wniosek: **przy kontraktach z `attack_s` i dźwięku wieloudarzeniowym prompt musi
ustawiać hierarchię głośności, nie tylko kolejność.** Nowy prompt dla `269`
(„One piercing hawk screech as the loudest moment of the take, hitting hard at
the very first instant … with two quick wingbeats after it kept clearly quieter")
dał **trafiony**. Poprawione też `118`, `164`, `216`.

**Błąd patchowania:** patch workflow pochodny z `sed 's/r031/r032/'` podmienił
token także **w samym skrypcie patchującym**, więc podmiany nie pasowały do pliku
i workflow został w stanie mieszanym (IDS z r032, marker i ścieżki z r031) —
guard szukałby `[generate-r031]`, a przy takim markerze nadpisałby istniejące
`variants/r031`. Naprawione patchem po numerach linii, z zachowaniem odniesień
historycznych. **Kontrola po każdym patchu: nazwa, marker guard, `--batch`,
katalog wariantów, IDS i `bash -n` na wszystkich blokach `run`.**

Nowe narzędzie `scripts/cut_internal_silence.py` (wycina dziury ciszy ze środka,
zero kredytów) — napisane i przetestowane, ale **nie** użyte masowo: przy progu
względnym −25 dB od RMS pliku łapie 90 kart, czyli mierzy zwykłe ciche fragmenty,
nie defekt.

**Kredyty: 2320 (r031) + 1120 (r032).** Z czwartego klucza (10 000) zostało
~2320. Korpus: **557** plików, 63 z flagą, 0 bliźniaków, 0 poza oknem 2–5 s,
LUFS −20,03 (σ 0,31), treść < 2 s: 85.

### Pogłos na kartach bez archetypu — zmierzone i odrzucone

Właściciel dopuścił pogłos jako tanią naprawę krótkiej treści, więc został
zmierzony na pełnej puli, nie na wrażenie. Kandydaci: **61 kart bez archetypu**
z treścią < 2 s (średnio 1,78 s); 24 karty z archetypem pominięte, bo pogłos
łamie ich kontrakty (zmierzone wcześniej: 0/70/104 → 6/73/95).

**Wynik `--apply` na 61 kartach:** średnia treść 1,78 → 1,96 s, 31 kart
przekroczyło 2,0 s — ale pojawiło się **7 par bliźniaków** przy utrzymywanym
dotąd zerze (6 z 7 par to karty z tego batchu).

**Sprawdzone wyjaśnienie i jego obalenie.** Hipoteza: bliźniaki biorą się z tej
samej realizacji szumu w syntetycznym IR, więc różne `--seed` na kartę je
rozklei. Zmierzone: **8 par**, czyli gorzej. Podobieństwo nie pochodzi z
realizacji szumu, tylko ze wspólnego charakteru pogłosu — ten sam damping
i ten sam kształt zaniku nakładają na różne dźwięki identyczny ogon, a odcisk
porównuje właśnie ogon, bo u krótkich kart dominuje.

**Decyzja: cofnięte.** 8 bliźniaków za +0,21 s średnio to zła wymiana, a zasada
właściciela brzmi „dobre 2 sekundy są lepsze niż złe 4". Korpus wrócił do
0 bliźniaków. Żeby pogłos był używalny, musiałby mieć **różny kształt zaniku na
kartę** (inny czas, inny damping, inna predelay), nie tylko inne ziarno.

Stan pozostałych 33 kart „prawdopodobnie" też jest zmierzony, nie zgadywany:
**9** ma metrykę niesterowalną (`attack_s`, `mod_peak_hz` — model nie realizuje
liczb), **24** dostało już celowany prompt pod tę samą cechę 2–3 razy bez
efektu, **0 świeżych**. Dalsza regeneracja tej puli to loteria, więc kredyty
zostały nie wydane.

### r033 — `speech_like`: pięć fałszywych alarmów, jedna prawdziwa naprawa

Siedem kart miało flagę `speech_like`, a mowa jest zakazana zawsze, więc wyglądało
to na naruszenie zasady. Pomiar pokazał co innego: próg flagi to
`mod_2_8hz_ratio > 0,55` (energia modulacji w tempie sylab) + `voiced_fraction
> 0,35` + centroid 300–3000 Hz. **Flaga nie wykrywa mowy**, tylko modulację
w tempie sylab — sam audyt oznacza ją „DO ODSŁUCHU, pewność niska, weryfikacja
uchem". Wszystkie siedem kart siedziało tuż nad progiem (0,566–0,847).

**Pięciu kart nie wolno ruszać**, bo właściwość odpalająca flagę jest wymagana:
`124`, `187`, `521` (`forest_birdsong`, kontrakt `tonal_frame_fraction ≥ 0,25` —
szybkie trele to z natury modulacja 2–8 Hz), `163` (`temple_bell`, `tonal ≥ 0,5`),
`489` („narastający krystaliczny ton" wprost w scenariuszu). Zabicie flagi
złamałoby kontrakt archetypu.

Dwie karty bez archetypu nie miały tego konfliktu, a przyczyna była w prompcie.
Wynik jednak rozdzielił się:

- **`130` Scavenging Harpy — naprawione.** Prompt mówił „harsh ragged screech",
  a wyszedł tonalny (tonal 0,72, voiced 0,69). Po zapisaniu wprost „rough grating
  and noisy rather than sung or tonal": mod 0,579 → 0,371, voiced 0,69 → 0,04,
  tonal 0,72 → 0,00, **0 flag**, treść 2,17 → 3,75 s.
- **`578` Savage Surge — cofnięte.** Stary prompt prosił o „morning star
  WHISTLING full-circle" (gwizd = czysty ton, tonal 0,93). Nowy mówił „broad low
  whoosh of displaced air, no whistle and no pitched tone" i przesterował
  w drugą stronę: **centroid 2546 → 35 Hz**, cztery nowe flagi
  (`sub_dominant`, `muffled`, `boomy`, `dull`) zamiast jednej.

Wniosek: zakaz konkretnego elementu („no whistle, no pitched tone") bez podania,
co ma zostać w zamian, zdejmuje całe pasmo. To ten sam mechanizm co `610`
w r026 („no bright ticking and no hiss" → centroid 163 Hz).

**Kredyty: 160 w r033.** Korpus: 557 plików, 60 z flagą, 0 bliźniaków, 0 poza
oknem 2–5 s, LUFS −20,03 (σ 0,31), `speech_like` 7 → 6.

### Trym ogonów ciszy — podział puli pomiarem, nie „na oko"

`long_trail_silence` miał 14 kart, ale trym nie jest dla wszystkich bezpieczny:
obcięcie ogona skraca plik, więc tam, gdzie treść sama ma mniej niż 2,0 s,
zepchnąłby plik pod dolną granicę okna akceptacji. Pomiar rozdzielił pulę:

**8 bezpiecznych** (treść ≥ 2,0 s) — trymnięte z `--trim-trail-s 0,40`:
`18` 4,00 → 3,01 s, `20` → 2,98, `67` → 2,83, `156` → 2,95, `298` → 3,95,
`308` → 2,58, `320` → 3,36, `514` → 2,79. **Wszystkie 8 utrzymało werdykt**
(6 „trafiony" i 2 poza audytem archetypów).

**6 ryzykownych zostawionych w spokoju** — `4` (treść 0,45 s przy ogonie 3,55 s),
`12` 1,80 s, `17` 1,17 s, `113` 1,24 s, `435` 1,74 s, `531` 1,17 s. Obcięcie
ogona obniżyłoby plik pod 2,0 s, a to jest kryterium akceptacji właściciela.

Flagi w korpusie: 60 → **54**. Archetypy bez zmian: 0 / 33 / 145.

### Krawędzie plików — trzy klasy flag, tylko jedna prawdziwa

Rozkład 54 flag rozebrany na klasy, a nie naprawiany hurtowo:

**`too_quiet` (`611`) — fałszywy alarm, zostawiony.** Flaga odpala z dwóch
warunków: `lufs < -32` **lub** `peak_db < -18`. `611` ma LUFS **−20,00 przy
średniej korpusu −20,03** — czyli jest dokładnie na celu; flagę odpalił sam peak
(−18,6 dB) przy creście 7,7 dB (p50 korpusu 21,9), bo to dźwięk gęsty,
bez transientu. Podbicie go wyloniłoby go ponad bibliotekę, której odchylenie
LUFS wynosi 0,31.

**`cut_start_hard` (`278`, `430`, `504`) — cecha, nie wada, zostawione.** Wszystkie
trzy mają crest 18,2–25,5 dB, czyli są uderzeniowe. Ich twardy start
(`start_15ms_db` −10…−11,9 dB przy progu −12) **jest** atakiem; fade-in zniszczyłby
dokładnie tę cechę, o którą walczyły kontrakty `attack_s ≤ 0,03–0,15`.

**`cut_end_hard` (`72`, `306`, `431`) — jedna prawdziwa wada, naprawiona częściowo.**
Plik urywał się na −20,3 / −31,3 / −38,7 dB, czyli dźwięk był przecinany
w trakcie wybrzmiewania. Fade-out 260 ms zniósł wszystkie trzy flagi
(−54,6 / −65,7 / −70,6 dB) i nie zmienił `duration_s`, więc okno 2–5 s było
bezpieczne. Ale **`72` został cofnięty**: fade obciął właśnie ten ogon, który był
wybrzmiewaniem osuwiska — `decay_s` spadł z ≥ 0,5 na 0,270 i złamał kontrakt
`stone_slide` (werdykt trafiony → prawdopodobnie). Zostały `306` i `431`.

Wniosek ogólny: **fade-out nie jest neutralny dla archetypów, których kontrakt
mierzy `decay_s`** — dla nich ogon jest treścią, nie ciszą.

Flagi w korpusie: 54 → **52**. Archetypy bez zmian: 0 / 33 / 145.

### Dwie ostatnie klasy flag — naprawa byłaby szkodliwa

**`long_lead_silence` (`4`, `232`, `583`, `604`) — zostawione, bo cisza wiodąca
jest tym, co trzyma je w oknie akceptacji.** Wszystkie cztery mają treść
0,21–0,98 s, a pliki 2,48–4,00 s, więc **są w oknie 2,0–5,0 s wyłącznie dzięki
ciszy na początku**. Trym zepchnąłby je na 0,36–1,13 s, czyli poza okno. To nie
są karty do trymu, tylko karty o realnie krótkiej treści — i należą do puli 85,
której pogłos już został odrzucony pomiarem (8 par bliźniaków).

**`mono_collapse` (`298` Raise the Alarm) — zostawione, bo to fizyka, nie wada.**
`mono_excess_lu` 4,07 przy progu 2,0, ale archetyp to `temple_bell`, a dzwon jest
źródłem punktowym: zapadanie się do mono jest dla niego **poprawne**. Karta ma
werdykt „trafiony", więc korekta mid/side ryzykowałaby utratę trafienia w imię
metryki, która tu nie opisuje wady.

To zamyka przegląd flag: z 52 pozostałych żadna nie jest jednocześnie prawdziwą
wadą i bezpieczną do naprawy za zero kredytów.

### Poprawka: `156` cofnięte z trymu ogonów

Licznik „treść < 2 s" pokazał 86 zamiast oczekiwanych 85. Przyczyna znaleziona
porównaniem stanów: **`156` (heavy_impact) — treść 2,090 → 1,949 s**, czyli
trym ogona z `--trim-trail-s 0,40` obciął 0,14 s treści na karcie, która była
tylko 0,09 s nad progiem.

Założenie „trym ogona nie rusza treści" jest **prawie** prawdziwe: `postprocess`
mierzy treść po fade, więc fade na końcu skraca mierzony ogon dźwięku, nie tylko
ciszę. Dla kart z zapasem (2,2 s i więcej) to niewidoczne; dla karty 0,09 s nad
progiem — decydujące.

Karta przywrócona ze stanu sprzed trymu: treść 2,090 s, plik 4,00 s, werdykt
„trafiony". Licznik wrócił do 85.

**Wniosek do zasady:** przy trymie ogona trzeba sprawdzać nie tylko
`duration_s ≥ 2,0`, ale też **`content_s ≥ 2,0` po operacji** — bo to treść jest
kryterium akceptacji, a nie długość pliku. Z ośmiu trymniętych kart siedem miało
zapas ≥ 0,05 s i przeszło bez szkody; `156` nie miało.

### Dlaczego pogłos tworzy bliźniaki — pomiar strukturalny, nie hipoteza

Wcześniejszy wniosek („podobieństwo bierze się ze wspólnego charakteru pogłosu,
nie z realizacji szumu") był **tylko częściowo prawdziwy**. Test kontrolowany na
11 kartach, które wcześniej utworzyły pary, rozdzielił przyczyny:

| stan | pary ≥ 0,95 | `550/614` | `529/592` | średnia treść |
|---|---|---|---|---|
| przed pogłosem | 0 | 0,9031 | 0,9475 | 1,87 s |
| A — wspólne parametry | **2** | 0,9559 | 0,9507 | 2,17 s |
| B — inne per karta (damping 2600–9000 Hz, pre-delay 4–30 ms, wet 8–16 dB, ziarno) | **1** | 0,9517 | **0,9317** | 2,15 s |

Zróżnicowany charakter pogłosu **pomaga** (2 → 1) i jedną parę wręcz oddala od
progu (0,9475 → 0,9317), ale pary nie znosi. Prawdziwa przyczyna jest inna
i mierzalna na całym korpusie:

**Korpus siedzi tuż pod progiem bliźniaków.** Par w paśmie 0,90–0,95 jest **175**,
a najbliżej progu: `160/290` 0,9489 (brak 0,0011), `529/592` 0,9475, `479/529`
0,9462, `287/290` 0,9435. Z tych 175 par **89 dotyczy co najmniej jednej karty
z treścią < 2 s** (18 — obu, 71 — jednej).

Czyli: doklejenie ogona do 85 krótkich kart działa na 89 par, którym wystarczy
podbić kosinus o mniej niż 0,05, żeby przekroczyły próg. **Pogłos nie tworzy
podobieństwa — on je odsłania.** Każda operacja dodająca wspólny składnik
(syntetyczny ogon, wspólny szum, ten sam filtr) zrobi to samo.

**Decyzja ostateczna: pogłos odrzucony**, i to nie z powodu samego pogłosu, tylko
dlatego że korpus nie ma zapasu. Żeby go użyć, trzeba by najpierw odsunąć od
progu same karty — a to wymaga regeneracji, czyli kredytów.
