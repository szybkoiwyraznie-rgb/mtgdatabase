# Stan produkcji — AI SFX v2

Ostatnia aktualizacja: **2026-10-10** (sesja `arena/a9d0a113-mtgdatabase`).

> Ten plik jest **obowiązkową lekturą agenta** i musi się mieścić w limicie
> 50 000 tokenów razem z resztą plików z `docs/required-reading.md`
> (walidator `scripts/check_required_reading.py`). Dlatego trzyma tylko
> stan bieżący, reguły i indeks rund. Opisy poszczególnych rund i dostaw
> są w `docs/archive/state-*.md` i czyta się je na żądanie, nie zawsze.

## Aktualna decyzja produktu

Dla każdej fabuły powstaje **jeden krótki, jednorodny sample**: „krakanie
wron”, „uderzenie dzwonu”, „szczęk bitwy”, „odgłos upadku”. Nie robimy
wielowarstwowej sceny z tłem i kodą. Stary ręczny sound design v1 leży
w `archive/v1-curated-sound-design/` i nie trafia do ZIP-a ani Pages.

Najważniejszy wymóg właściciela: **dźwięk ma się kojarzyć z kartą.**
Czyste skrobanie, syczenie, stuknięcie czy szelest bez rozpoznawalnego
źródła to porażka, nawet jeśli metryki się zgadzają.

## Aktualny stan produkcji

- Katalog: `fabuły270926.csv` + `data/catalog.json` — **574 fabuł**
  (dopisane `341`, `348`, `350`, `351`). ID = numeryczna część
  `Ilustracja` (`341DTK` → fabuła `341`).
- Sample: **573 MP3** w `audio/samples/<id>.mp3`; **574 scenariusze**.
  Nowe: `341`, `350`, `351` mają audio; `348` jeszcze nie.
- Ostatnia dostawa: `b073` — `327BLB` *Brave-Kin Duo* (`water_splash`)
  i `328LRW` *Bog Hoodlums* (`heavy_impact`), obie **trafione, 0 flag**.
  `328` weszła z pierwszej tury; `327` dopiero po zmianie archetypu
  z `liquid_pour` na `water_splash` — patrz reguła 25.
- Poprzednia dostawa: `b072` — `324DSK` *Spineseeker Centipede*
  (`mechanism_click`) i `325TDM` *Narset's Rebuke* (`thunder_clap`),
  obie **trafione, 0 flag**; `325` wymagała 5 prób i montażu.
- Ostatnia runda: **`r101`** — `382` *Geological Appraiser*
  **2,29 → 2,89 s**. `348` cofnięta (`psychic_shriek`, attack).
  Szczegóły: `state-2026-10-10-r101.md`.
- Poprzednia runda: **`r100`** — nowa `350` *Temple of Abandon*
  **3,67 s** (`fire_crackle`, trafiony). `348` para 0,92 z `18`.
  Szczegóły: `state-2026-10-10-r100.md`.
- Poprzednia runda: **`r099`** — nowa `351` *Sporecap Spider*
  **3,84 s** (`steam_hiss`, trafiony). `350` cofnięta (dzwon).
  Szczegóły: `state-2026-10-10-r099.md`.
- Poprzednia runda: **`r098`** — nowa `341` *Pacifism* **2,66 s**
  (trafiony). `348` Impulse para 0,91 z `207`. Szczegóły:
  `state-2026-10-10-r098.md`.
- Poprzednia runda: **`r096`** — **dwie z dwóch**: `4` *Mystic
  Sanctuary* **1,14 → 1,59 s** i `150` *Balamb Garden* **2,37 →
  3,69 s** (`water_splash`). Szczegóły: `state-2026-10-10-r096.md`.
- Poprzednia runda: **`r095`** — **zero z dwóch** na nowym budżecie
  (10/10 OK). `157` i `607` już ~3 s, po łańcuchu krótsze;
  `607` para 0,94 z `329`. Szczegóły: `state-2026-10-10-r095.md`.
- Poprzednia runda: **`r094`** — **quota 0**. Dwa ułomne warianty,
  oba krótsze po łańcuchu. Generacja wstrzymana.
  Szczegóły: `state-2026-10-10-r094.md`.
- Poprzednia runda: **`r093`** — z 2 kart weszła **jedna**: `468`
  *Cacophodon* **2,85 → 3,16 s**. `177` para 0,95 z `396`.
  Szczegóły: `state-2026-10-10-r093.md`.
- Poprzednia runda: **`r092`** — **zero z dwóch**: `164` centroid;
  `72` decay. Szczegóły: `state-2026-10-10-r092.md`.
- Poprzednia runda: **`r091`** — **zero z dwóch**: `9` centroid;
  `96` po łańcuchu krótsza. Szczegóły: `state-2026-10-10-r091.md`.
- Poprzednia runda: **`r090`** — **dwie z dwóch**: `329` *Blinding
  Drone* **2,17 → 2,59 s** i `262` *Angel's Herald* **2,44 → 3,27 s**.
  Szczegóły: `state-2026-10-10-r090.md`.
- Poprzednia runda: **`r089`** — **zero z dwóch**: `5` para 0,90 z
  `98`; `163` gorszy werdykt. Szczegóły: `state-2026-10-10-r089.md`.
- Poprzednia runda: **`r088`** — **dwie z dwóch**: `18` *Lotusguard
  Disciple* **2,10 → 2,70 s** (`magic_shimmer`) i `571` *Vow of
  Flight* **2,29 → 2,64 s** (`wing_flutter`). Szczegóły:
  `state-2026-10-10-r088.md`.
- Poprzednia runda: **`r087`** — **zero z dwóch**: `12` gorszy werdykt;
  `332` +0,80 s ale para 0,90 z `558`. Szczegóły: `state-2026-10-10-r087.md`.
- Poprzednia runda: **`r086`** — **zero z dwóch**: `269` i `583`
  cofnięte (dłuższe, ale gorszy werdykt). Szczegóły: `state-2026-10-10-r086.md`.
- Poprzednia runda: **`r085`** — **dwie z dwóch**: `232` *Goblin Piker*
  **0,98 → 3,36 s** (`plate_clank`, +2,38) i `280` *Sultai Scavenger*
  **2,03 → 2,57 s** (`creature_cackle`). Obie trafione, 0 flag.
  Szczegóły: `state-2026-10-10-r085.md`.
- Poprzednia runda: **`r084`** — **zero z dwóch**: `277` i `576`
  `sword_clash` cofnięte. `277` +0,15 s (za mało); `576` dłuższe
  warianty złamały `spectral_flatness`. Szczegóły: `state-2026-10-10-r084.md`.
- Poprzednia runda: **`r083`** — z 2 kart weszła **jedna**: `250`
  *Loxodon Mender* **2,70 → 3,11 s**, `sword_clash`. `209` cofnięta
  (+0,01 s po łańcuchu — za mało). Szczegóły: `state-2026-10-10-r083.md`.
- Poprzednia runda: **`r082`** — **dwie z dwóch**: `71` *Security Rhox*
  **2,30 → 3,21 s** (`heavy_impact`) i `453` *Elgaud Inquisitor*
  **2,97 → 3,36 s** (`plate_clank`). Obie trafione, 0 flag, 0 par.
  Szczegóły: `docs/archive/state-2026-10-10-r082.md`.
- Poprzednia runda: **`r081`** — z 2 kart weszła **jedna**: `56`
  *Diplomatic Relations* **3,00 → 4,00 s**, `plate_clank`, zero flag.
  `210` *Fiery Justice* cofnięta: 5/5 złamało `low_all`. Skreślona przy
  tym materiale. `duration_seconds` wraca do 2,76 s.
- Poprzednia runda: `r059` — z 2 kart weszła **jedna**: `434`
  *Epic Experiment* urosła z **1,20 → 3,91 s** treści, kontrakt
  `war_machine` spełniony. Cena: nowy bliźniak `325-434` (0,9422).
  `232` znów cofnięta — crest 12,9–14,9 przy progu 17.
- Ostatnia paczka: **`b074`** — **7 nowych kart**, które były lukami
  w numeracji (`329`, `332`, `333`, `334`, `336`, `338`, `340`).
  Wszystkie siedem weszły **trafione i bez flag**; korpus urósł
  z 563 do **570**, a liczba flag i par nie drgnęła. Szczegóły
  w `docs/archive/state-2026-10-09-b074.md`.
- Poprzednia runda: `r080` — ta sama karta, ten sam prompt, pięć
  prób zamiast trzech. `140` *Boros Challenger* **2,70 → 3,46 s
  (+0,76)**, zero flag, kosinus 0,5561 — czyli **bardziej
  odrębna** niż poprzednia (0,6993). W `r077` ta sama `140`
  dostała trzy warianty i najdłuższy miał 2,42 s, czyli mniej niż
  obecne 2,70. Pięć prób znalazło 3,46 s tam, gdzie trzy przeszły
  obok. To pierwszy dowód, że zwiększenie liczby prób działa —
  ale tylko wtedy, gdy rozkład długości obejmuje wartość
  docelową. Druga karta, `370`, dostała pięć prób i **wszystkie
  pięć wyszło dłuższych** (3,37–3,75 s wobec 2,34), ale cztery
  nie przeszły kontraktu `arrow_flight`: zasysanie cieczy jest
  zbyt tonalne jak na świst strzały. Cofnięta.
- Poprzednia runda: `r078` — **zero z trzech**, druga pusta runda po
  `r074`. Hipoteza z `r077` (różny materiał ⇒ większa długość)
  **obalona**: brąz dał 2,64 s, kamień 3,34 s ale wszystkie trzy
  złamały `low_all`, bariera 2,35 s. Korpus znowu bez zmian
  (45 flag, 25 par, archetypy 0/30/161). Trzy kolejne hipotezy
  (łańcuch zdarzeń → czasownik uderzenia → materiał) poprawiały
  trafność, ale żadna nie okazała się przewidywalna. Uczciwy bilans
  po jedenastu rundach to **13 instalacji z 33 kart, około 40 %**.
  Przestałam szukać jednej dźwigni — wariancja modelu jest większa
  niż wszystkie moje dotychczasowe zmienne.
- Poprzednia runda: `r077` — z 3 kart weszła **jedna**: `491` *Nature's
  Embrace* **2,67 → 3,45 s (+0,78)**, `plate_clank`, zero flag.
  Wygrała jedyna karta w transzy, której materiał **nie był stalą**
  — dostała korę. Hipoteza z `r076` (że winny jest czasownik ruchu
  w otwarciu) **nie potwierdziła się**: `548` i `140` dostały
  „clashing" zamiast „turning" i „rolling" i żadna nie urosła.
  Czasownik uderzenia jest konieczny, ale nie wystarczający.
  Zamiast tego wygląda na to, że cztery stuki **stali o stal**
  brzmią dla modelu jak jeden długi dźwięk, więc nie ma powodu ich
  rozciągać. `548` idzie na odpoczynek (0/6 w dwóch rundach).
- Poprzednia runda: `r076` — z 3 kart weszła **jedna**, ale ta jedna
  wyleczyła flagę: `156` *Summary Judgment* **2,09 → 2,47 s (+0,38)**
  i koniec flagi `boomy` (w korpusie z 7 na **6**). `534` i `548`
  cofnięte, choć **osiem z dziewięciu** wariantów było trafionych —
  siedem wyszło po prostu krótszych od obecnych sampli. Wąskim
  gardłem przestał być werdykt, a została nim długość. Winne jest
  otwarcie: `548` dostała „Armoured shoulders **turning**", czyli
  złamałam własną regułę z `r074` (materiał to rzeczownik, czynność
  to czasownik) dwie rundy po tym, jak ją zapisałam.
- Poprzednia runda: `r075` — **dwie z trzech, +1,90 s**, pierwsza
  wybrana po nowej procedurze z `r074`. `216` *Armored Skaab*
  **2,53 → 3,48 s**, `567` *Jwar Isle Avenger* **2,48 → 3,43 s**,
  obie `plate_clank`, obie bez flag. `524` wreszcie trafiona (3,10 s,
  atak 0,020) po **siedmiu** nieudanych próbach — hipoteza z `r072`
  potwierdzona, winny był materiał „drawn from a scabbard" — ale
  zrobiła parę 0,9316 z kartą `243` i też nie weszła.
  Siedem z dziewięciu wariantów trafionych, najlepszy wynik werdyktów
  w serii. Flagi 38, pary 25 — bez zmian.
- Poprzednia runda: `r074` — **zero z trzech**, pierwsza pusta runda.
  260, 332 i 372 cofnięte; korpus po niej jest identyczny z korpusem
  przed nią (38 flag, 25 par, archetypy 0/30/161, ani jedna zmiana
  treści). Dwie rzeczy warte zapamiętania. Po pierwsze, **reguła 1
  działa też w górę**: 260 i 372 mają dziś sample *trafione*, a
  wszystkie sześć wariantów wyszło *prawdopodobnie* — czyli gorzej,
  mimo że każdy był dłuższy. Prawdopodobnie zamiast trafionego to
  pogorszenie, nie postęp. Po drugie, `332` v2 była najlepszym
  wariantem od tygodni (4,00 s, trafiona, zero flag) i **i tak
  poszła do kosza** — fingerprint pokazał trzy nowe pary (0,9227 /
  0,9106 / 0,9104). Wszystkie trzy warianty wpadły w jeden gęsto
  zaludniony róg: długie niskie dudnienie (317, 558, 562, 496, 241,
  23, 347 mają już między sobą pary 0,90–0,93).
- Poprzednia runda: `r072` — z 3 kart weszła **jedna**: `20` *Jeskai
  Devotee* **2,28 → 3,09 s (+0,81)**. `224` i `524` cofnięte, obie
  0/3, i obie z tego samego powodu: `attack_s` (2,11 / 0,56 / 2,04
  oraz 0,58 / 1,46 / 2,07 przy progu 0,1). Nie przegrały na długości
  — ich warianty miały 2,42–2,93 s, więcej niż obecne — tylko na tym,
  że model zaczął od czegoś miękkiego. Diagnoza: w r072 obu
  skróciłam otwarcie („A blade **on** armour" zamiast „**striking**
  armour"), żeby zmieścić się w limicie 450 znaków, i straciły
  czasownik uderzenia. **Nie skracać promptu kosztem czasownika.**
- Poprzednia runda: `r071` — **trzy z trzech**, pierwsza taka runda
  w tej serii. `608` *Skymarch Bloodletter* **2,23 → 3,63 s (+1,40)**,
  `435` *Warrior's Sword* **2,19 → 3,36 s (+1,17)**, `17` *Selhoff
  Occultist* **2,23 → 2,73 s (+0,50)** — razem **+3,07 s**. Ważniejsze
  od długości: archetypy przesunęły się z 33/158 na **30/161**, czyli
  trzy karty przeszły z *prawdopodobnie* na *trafiony*. Flagi i pary
  bez zmian (38 / 25).
- Poprzednia runda: `r070` — z 3 kart weszła **jedna, ale największa
  w tej serii**: `308` *Greatsword of Tyr* **2,06 → 3,31 s (+1,25)**,
  `sword_clash` w całości. Wzorzec
  z karty `334` (trzask, dwa długie zgrzyty, trzeci trzask) zadziałał
  na **wszystkich trzech** wariantach — pierwszy raz w tej serii
  trzy na trzy trafione. `224` dostała ten sam wzorzec i jej v2 też
  był trafiony, ale miał 2,51 s wobec obecnych 2,47 s, czyli +0,04 s
  — za mało, żeby ruszać plik. `452` cofnięta: oba trafione warianty
  były krótsze niż obecne 2,60 s, a v1 dostał jeszcze `mono_collapse`.
  Korpus bez zmian w liczbach (flagi 38, pary 25), bo jedyna
  instalacja nie dodała żadnej flagi ani pary.
- Poprzednia runda: `r069` — z 3 kart weszła **jedna**, ale za to
  wyleczyła jedną flagę: `74` *Rush of Battle* **2,76 → 3,20 s**
  (+0,44), `heavy_footsteps` w całości. Jej stary sample miał flagę
  `boomy`, nowy nie ma żadnej — korpus zszedł z 39 na **38** flag.
  `308` cofnięta, choć v1 była trafiona: miała tylko 1,66 s wobec
  obecnych 2,06 s, czyli instalacja by ją skróciła. `177` cofnięta —
  wszystkie trzy łamały `voiced_fraction` (próg 0,3), czyli nie było
  w nich głosu.
- Poprzednia runda: `r068` — z 3 kart weszły **dwie**, razem
  **+1,62 s**: `501` *Exterminator Magmarch* **2,75 → 3,80 s** i `565`
  *Mana Cylix* **2,67 → 3,24 s**, obie trafione i bez flag. `501`
  weszła za drugim razem — wystarczyło wyrzucić z promptu parę
  („steam venting"), która w r067 zamieniła machinę w syk
  (`low_all` 0,022–0,131 → teraz 0,457). `308` cofnięta: wszystkie
  trzy znów łamały `attack_s` (1,25–2,40 przy progu 0,1).
- Poprzednia runda: `r067` — z 3 kart weszły **dwie**, razem
  **+2,08 s**: `52` *Divest* **2,20 → 3,21 s** i `355` *Cathartic
  Reunion* **2,01 → 3,08 s**, obie trafione, obie bez flag i bez
  nowych par. `52` weszła za **piątym** razem — wystarczyło dopisać
  równy odstęp (`ioi_cv` z 1,33–2,23 w r066 na 0,795 w r067).
  `501` cofnięta: wszystkie trzy warianty łamały `low_all`
  (0,022–0,131 przy progu 0,35), bo „steam venting" zrobiło z
  machiny wojennej syk.
- Poprzednia runda: `r066` — z 3 kart weszła jedna, ale za to
  największy pojedynczy skok od r063: `445` *Locthwain Paladin*
  **2,27 → 3,74 s** (+1,47), kontrakt `plate_clank` w całości,
  zero flag. `52` cofnięta po raz drugi — tym razem nie na barwie,
  lecz na **rytmie**: wszystkie trzy łamały `ioi_cv` (1,33–2,23 przy
  progu 0,8), czyli mechanizm stukał nierówno. `372` cofnięta, bo jej
  najlepszy wariant dobrałby nową parę bliźniaków (0,9212 z `97`).
- Poprzednia runda: `r065` — z 3 kart weszły **dwie**, razem
  **+2,86 s**: `67` *Scorpion Sentinel* **2,12 → 3,96 s** (drugi
  wynik w historii, po `247`) i `553` *Coat with Venom*
  **2,12 → 3,14 s**. Obie dostały prompt zbudowany wyłącznie
  z rzeczowników — ani jednego przymiotnika barwy. `524` cofnięta:
  wszystkie trzy warianty łamały `attack_s` (0,22–0,55 s przy progu
  0,1), czyli „reliquary clicking open, blade springing out" dało
  powolne narastanie zamiast uderzenia.
- Poprzednia runda: `r064` — z 3 kart weszła jedna: `491`
  *Nature's Embrace* **2,13 → 2,67 s**, kontrakt `plate_clank`
  spełniony, zero nowych flag. `52` i `260` cofnięte z tego samego
  powodu, ale w przeciwnych kierunkach: `52` wyszła za jasno
  (centroid 8309–9512 przy oknie 800–6000), `260` za ciemno
  (118–166 przy oknie 150–1600). Oba prompty opisywałyBARWĘ
  przymiotnikami i model je zignorował; `491` opisywał zdarzenia
  (sześć płyt wskakujących na miejsce) i zadziałał.
- Poprzednia runda: `r063` — z 3 kart weszły **dwie**, razem
  **+3,38 s** treści, zero nowych flag i zero nowych par:
  `469` *Chained Throatseeker* **1,99 → 3,43 s** i `247`
  *Subterranean Scout* **2,06 → 4,00 s**. Obie dostały ten sam
  zabieg, który uratował `71` w r062: opis ŁAŃCUCHA zdarzeń zamiast
  jednego uderzenia. `23` cofnięta — żaden wariant nie trzyma poziomu
  (`sustain_ratio` 0,052–0,068 przy progu 0,2), a to właśnie
  wybrzmiewanie jest istotą dzwonu.
- Poprzednia runda: `r062` — z 3 kart weszła jedna, ale ta jedna była
  warta całej rundy: `71` *Security Rhox* z **1,40 → 2,30 s**, przy czym
  centroid skoczył 268 → **1157 Hz**, a udział energii powyżej 250 Hz
  z 0,223 na **0,525**. Flaga `tonal_sustained` zeszła sama. `4` i `145`
  cofnięte — żaden z sześciu wariantów nie przebił stanu obecnego.
- Poprzednia runda: `r061` — z 3 kart weszła jedna: `5`
  *Academy Journeymage* z **1,87 → 2,30 s** po fill-take i przycięciu
  ogona (które przy okazji rozbiło parę `5-164`). `98` i `71` cofnięte.
- Poprzednia runda: `r060` — z 3 kart weszły dwie: `583` *Kill Shot*
  z **0,21 → 2,66 s** i `292` *Rediscover the Way* z **1,38 → 3,22 s**.
  Kluczem była klauzula `--fill-take`, której żadna z nich nigdy nie
  dostała. `71` cofnięta: wszystkie warianty wyszły za ciemne.
- Poprzednia runda: `r058` — z 3 kart weszła jedna, najgorsza w swojej
  klasie: `113` *Welder Automaton* urosła z **1,24 → 3,96 s** treści
  (fade 150 ms domknął kontrakt). `232` i `434` cofnięte.
- Jeszcze wcześniej: `r057` — 3 z 8 kart urosły (`558` +1,91 s,
  `4` +0,69 s, `26` +0,54 s), treść < 2 s **21 → 19**, flagi 53 → 52.
- Ostatnia korekta EQ: `r058eq` — **zero kredytów**, półka widmowa na
  7 kartach: `dull` 16 → 11 (`74`, `102`, `120`, `173`, `214`; +3 dB przy
  2 kHz), `harsh` 11 → 9 (`86`, `267`; −3 dB przy 8 kHz). Flagi 52 → 46,
  pary ≥ 0,90 **23 → 22**, nowych flag 0, werdykty bez zmiany.
- Ostatnia runda korekt: `r056` — zero przyjętych (diagnoza poniżej).

Metryki korpusu (audyt `2026-10-09-after-r068`):

| metryka | wartość |
|---|---|
| pliki z flagą | **38** |
| bliźniaki ≥ 0,95 | **0** |
| identyczny PCM | **0** |
| pary ≥ 0,90 (graf kosinusowy) | **25** |
| treść < 2 s | **12** |
| poza oknem 2–5 s | **0** |
| LUFS średnio | **-20.09** (odch. 0.48) |
| archetypy nie trafiony / prawdopodobnie / trafiony | **0 / 30 / 161** |
| suma treści | **1590,99 s** |

Budżet: **drugi klucz 10 000 kredytów wgrany 2026-10-09**, wydane
  **5120**, **zostaje 4880**. Pierwszy klucz wyczerpała paczka `b074`
  (7 nowych kart). Rozbicie na rundy jest w sekcji „Stan liczbowy”.
Realny koszt to **40 kredytów za generację**; transza 2 karty po
5 wariantów = 10 generacji = **400 kredytów**, dostawa 2 kart = 160.

Mechanizm generacji: token bota Arena **nie może** użyć
`workflow_dispatch` (HTTP 403), więc generacje idą przez tymczasowy
workflow `.github/workflows/temp-variants-r016.yml`, odpalany markerem
w treści commita (`[generate-rNNN]` / `[generate-bNNN]`). Workflow
commituje warianty z powrotem na branch (`[import-rNNN]`), agent je
pobiera `git pull`, wybiera wariant i sprząta katalog `variants/`.

**Po resecie sandboxa** (zdarzyło się trzy razy w jednej sesji):
`.venv/` i `.cache/` są w `.gitignore` i giną, a repo wraca do commitu
bazowego. Kolejność odtwarzania:

```bash
git fetch origin <branch-sesji> && git reset --hard origin/<branch-sesji>
python3 -m venv .venv && .venv/bin/pip install numpy scipy soundfile pyyaml pyloudnorm resampy
# .cache/wezly.py trzeba napisać od nowa — graf par kosinusowych,
# ładuje scripts/audit_samples_full.py przez importlib Z wpisem w sys.modules
```

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
- `docs/archive/state-*.md` — historia rund i dostaw (nie jest obowiązkową lekturą).

## Aktywne narzędzia

```bash
python scripts/validate_stories.py fabuły270926.csv
python scripts/import_collection.py fabuły270926.csv --output data/catalog.json
python scripts/validate_sample_scenarios.py data/samples/scenarios.jsonl --catalog data/catalog.json
python scripts/audit_samples_full.py --json data/samples/audio-audit-YYYY-MM-DD-after-rNNN.json
python scripts/audit_archetype_match.py --audit <audyt.json> --json data/samples/archetype-match-...json
python scripts/audit_scenario_quality.py --json data/samples/scenario-quality.json
python scripts/rewrite_archetype_prompts.py --ids 1,2,3 --batch rNNN --fill-take --apply
python scripts/postprocess_samples.py --ids 1,2,3 --max-gain-db 26 --report data/samples/postprocess-rNNN.json
python scripts/build_site.py --out site/generated
python scripts/build_pack.py --output build/samples-latest.zip
python scripts/check_required_reading.py
```

Sekret GitHub/API nazywa się **`ELEVENLABS`**. Nie używać dawnej nazwy
`ELEVENLABS_API_KEY`.

## Workflow

**Dostawa nowych fabuł (batch `b0NN`)** — właściciel podaje teksty:

1. Dopisać wiersze do `fabuły270926.csv` (TSV, `\r\n`, kolumny
   `Ilustracja` / `Nazwa Karty` / `Narracja`).
2. `validate_stories.py` → `import_collection.py` (katalog rośnie).
3. Napisać `sample_scenario` (PL) i `prompt` (EN) do `scenarios.jsonl`.
4. `validate_sample_scenarios.py` — **musi wyjść z kodem 0**.
5. Przestawić `temp-variants-r016.yml` na `b0NN` (`--batch`, `IDS`,
   `variants/b0NN`, markery), commit z `[generate-b0NN]`, push.
6. Czekać na `[import-b0NN]` (`git ls-remote` co 20 s, zwykle 40–140 s).
7. Wybrać wariant po metrykach, `postprocess_samples.py`, audyty,
   `build_site.py` + `build_pack.py`, wpis do `STATE.md`, sprzątanie
   `variants/`.

**Runda korekty istniejących kart (batch `r0NN`)** — 8 kart × 2 warianty:
jak wyżej, ale prompty idą przez `rewrite_archetype_prompts.py`
(`OVERRIDES` w tym skrypcie to źródło prawdy dla regeneracji).

## Stan liczbowy

- Katalog: **570 fabuł**, scenariusze **570** (100 %), sample **570**.
- Flagi **38** łącznie (38 kart z flagą), pary ≥ 0,90 **25**,
  treść < 2 s **12**. Najczęstsze: `dull` 11, `harsh` 9, `boomy` 6,
  `speech_like` 6, `tonal_sustained` 5.
- Archetypy: **0** nie trafionych, **30** prawdopodobnie, **161** trafionych.
- Budżet: **4880 / 10 000** kredytów na drugim kluczu (r068–r078:
  11 × 360, r079: 400, r080: 400). Pierwszy klucz 10 000 zamknęły: b072 560,
  r057 640, b073 360, r058 360, r059 240, r060 360, r061 360,
  r062 360, r063 360, r064 360, r065 360, r066 360, r067 360,
  b074 840, b074b 600, b074c 480, b074d 240, b074e 120.

## Reguły i procedury

Obowiązujące dziś — wyciągnięte z rund r050–r056 i dostawy b071.

**1. Zasada ochronna.** Spadek werdyktu archetypu = powrót do starego
sample. Werdykt jest ważniejszy niż długość. Wyjątek: `292` w r055 nie
zmieniła werdyktu (1,0 pkt przed i po), a i tak została cofnięta, bo
nowy dźwięk był czystym dronem zamiast wiatru — **zamiana jednego
naruszenia na drugie przy tym samym werdykcie to nie jest postęp.**

**2. Przyrost poniżej ~0,3 s nie jest wart nowej flagi.** `469` w r056
przeszła kontrakt i zyskała 0,07 s, ale wzięłaby flagę `harsh` i skok
centroidu 5096 → 12 972 Hz. Odrzucona.

**3. Cofnięcie pliku to cofnięcie tekstu.** Gdy karta wraca do starego
sample, wracają razem: `(a)` MP3, `(b)` `duration_seconds` **i**
`(c)` `sample_scenario` + `prompt`. Punkt `(c)` był pomijany od r051 i
przez sześć rund uzbierał **36 kart**, których opis na stronie nie
odpowiadał plikowi (naprawione 2026-10-07, 0 kredytów).

**4. Dwa limity długości, dwa różne narzędzia.** Przed każdym wysłaniem:
`prompt` po doklejce `--fill-take` **≤ 450** znaków (limit API; realny
ładunek liczy `api_text_length()`, bo scout dokłada zakazy w locie) oraz
`sample_scenario` **≤ 220** znaków (`validate_sample_scenarios.py`).
**Walidator wychodzi z kodem 1 na ostrzeżeniach, nie tylko na błędach** —
lokalny `| tail` to ukrywa i CI wywala się dopiero na GitHubie.

**5. Walidator zabrania słowa „layer”.** `BANNED_LAYER_WORDS` sprawdza
oba pola, więc zapisany prompt kończy się na
`No music, no speech, no ambience bed.`, a zakaz
`No multi-layer cinematic scene.` dokłada scout w locie.

**6. Take 4,0 s, nie krócej.** r056 zmierzyła: przy take'u 2,5 s model
wypełnił 8–83 % pliku, przy 4,0 s — 31–85 %, i najdłuższe treści
powstały właśnie przy 4,0 s. `duration_seconds` to ramka, nie cel.

**7. Wzorzec promptu.** NAKAZ, nie zakaz · jawna liczba powtórzeń ·
pierwsze zdarzenie najgłośniejsze (obniża `attack_s`) · unikać słów
`deep` / `under` / `subterranean` (model robi z nich czysty sub-bas) ·
pilnować centroidu w zakresie kontraktu · dopisek `--fill-take`
(„The sound fills the whole take…”).

**8. `decay_s` = szczyt → pierwsza ramka poniżej szczyt−20 dB**
(`audit_semantic_match.py`). Zdarzenia **rozdzielone przerwami** dają
jednocześnie krótki `decay_s` (przerwa spada pod próg) i wysoki
`onset_count` — sprawdzone na `469` (decay 0,120 / onset 15) i `71`
(0,100 / 5). Ten sam wzorzec nie zadziała dla kontraktów z **dolnym**
progiem `decay_s` (np. `stone_slide` wymaga ≥ 0,5 — tam potrzeba dźwięku
ciągłego).

**9. `onset_count = 0` to dziś dominantny tryb porażki** — `113` i `434`
w r055, `232` w r056. Model robi jedną ciągłą teksturę zamiast N zdarzeń,
mimo że prompt mówi „eight clanks”. Pisz o przerwach wprost.

**10. `attack_s` rośnie, choć prompt mówi „at the very first instant”.**
`4` → 0,670 s, `269` → 0,820 s, `558` → 0,200 s w r056. Samo
sformułowanie nie wystarcza.

**11. `--apply` w `rewrite_archetype_prompts.py` nadpisuje
`duration_seconds` stałą `DURATION` (4,0).** Po każdym `--apply` trzeba
przeliczyć wartość z `sf.info()`, inaczej wychodzi `duration_mismatch`.

**12. Montaż zamiast generacji, gdy się da.** Nadmiar ciszy na krańcach
ucina `postprocess_samples.py --trim-lead-s / --trim-trail-s` (0
kredytów) — tak powstało `280.mp3` (4,00 s → 2,40 s).
`cut_internal_silence.py` wycina dziury w **środku**, nie na krańcach.

**13. Nowa karta ma większą szansę niż poprawka do poprawki.** Karty po
trzecim i czwartym podejściu (`292` — cztery, `87` — cztery) nie
wchodzą; świeże (`244`, `280`, `323`) wchodzą od razu.

**14. Check-lista zamknięcia rundy:** audyt `audit_samples_full.py` →
`audit_archetype_match.py` → graf par (`wezly.py 0.90`, musi zostać 23) →
kopie `-latest.json` → `compileall` + unittest → walidator **z kodem
wyjścia** → `build_site.py` + `build_pack.py` → wpis w `STATE.md` →
commit + push + `gh pr checks` → `git rm -r --cached variants`.

**15. Regeneracja: `--batch` musi zgadzać się z polem `batch` w
`scenarios.jsonl`.** `elevenlabs_sample_scout.py: select_rows()` filtruje
po `row["batch"]`, więc po zmianie batchu w workflow trzeba przepisać
pole w scenariuszu. Inaczej run idzie **na sucho**: `selected 0` →
`No selected ready scenario` → zero kredytów, zero plików, a log
wygląda jak udany (b072b spalił tak dwa odpalenia).

**16. Manifest nie blokuje generacji — pomijanie idzie po pliku.**
`elevenlabs_sample_scout.py` sprawdza `out_file.exists()` w katalogu
`--out`, a nie `generated-manifest.jsonl`. Czyszczenie manifestu przed
regeneracją jest więc **niepotrzebne i szkodliwe** (kasuje historię).

**17. Dopisek „The sound fills the whole take…" blokuje `crest_db`.**
`crest_db = 20log10(peak/rms)`, więc równo wypełniony take ma niski
 crest. Wzorzec `562` *Shock* (jedyne trafione `thunder_clap`): crest
18,83 przy **`audible_share` 0,478** — połowa take'u to cisza. Dla
archetypów z progiem crestu pisz wprost „…dying away into silence
before the end". Dopisek **nie jest** wymagany przez walidator.

**18. Reverb podnosi `decay_s`, ale obniża `crest_db` — konflikt,
którego kontrakt nie widzi.** `add_reverb_tail.py` na `325` dał decay
0,34 → 0,85 s, ale crest 18,61 → 15,72. Używać tylko na take'ach
z zapasem crestu ≥ 6 dB (`325` ostatecznie: 24,5 → 20,9).

**19. Kolejność montażu: reverb → postprodukcja → `tame_spectrum` →
postprodukcja.** Filtr górnoprzepustowy 25 Hz w `postprocess_samples.py`
wycina sub-bas, którym `tame_spectrum` wyrobił centroid (`325`: centroid
734 → 1017, `low_all` 0,504 → 0,302). Po korekcji trzeba puścić
postprodukcję raz jeszcze. I **`--shelf-hz` ma być tam, gdzie jest
energia**: domyślne 3500 Hz mija pasmo 250–2000 Hz, przez co korekcja
rosła z −3 dB do −15 dB i i tak nie trafiała w okno.

**20. Dobór kart do rundy po DIAGNOZIE, nie po długości.** r056 wzięła
osiem „świeżych" kart wybranych z tabeli najkrótszych — nie weszła
żadna. r057 wzięła osiem wybranych po tym, **która konkretna metryka
nie dowiozła**, i weszły trzy. Liczy się nie to, jak bardzo karta
odstaje, tylko czy wiadomo, w co uderzyć.

**21. Dwie miary treści — nie mylić ich.** `content_s` = czas pliku
minus cisza na krawędziach przy progu **bezwzględnym −45 dBFS**; to
jest „treść < 2 s" z tego pliku i z okna akceptacji 2–5 s.
`content_rel_s` = to samo przy progu **względnym** i to od niej zależy
flaga `short_content` (< 0,8 s). Po b072: **21** kart wg `content_s`,
ale tylko **7** wg `content_rel_s`. Normalizacja do −20 LUFS potrafi
`content_s` skurczyć o połowę, więc decyzję o przyjęciu wariantu
podejmujemy dopiero po `postprocess_samples.py`.

**22. Wpisy `OVERRIDES` mają dwa style zapisu** i wycinanie ich
regexem kończy się katastrofą. Część wpisów jest zwarta
(`"...", "...", False),`), część wieloliniowa (`    ),`) — regex na
`^    ),$` przeskakuje do następnego wieloliniowego i kasuje po drodze
cudze wpisy (raz wycięło 4961 znaków zamiast 355). Zakresy liczyć
przez `ast`: węzeł to **`AnnAssign`**, nie `Assign`, bo `OVERRIDES` ma
adnotację typu. Przed każdą edycją: `cp` pliku do `/tmp`.

**23. Po `git reset --hard` branch traci upstream.** `git pull`
wychodzi wtedy bez błędu, ale **nic nie pobiera** — wygenerowane
warianty czekają na serwerze, a lokalnie wygląda jakby run się nie
udał. Po każdym resecie: `git rev-parse --abbrev-ref @{u}` i w razie
`fatal: no upstream` — `git branch --set-upstream-to=origin/<branch>`.

**25. Sprawdzić, czy kontrakt archetypu jest osiągalny, zanim się w
niego wyceluje.** `liquid_pour` żąda `sustain_ratio` ≥ 0,3, a trzy
karty już do niego przypisane mają 0,085 / 0,238 / 0,379 — próg
spełnia jedna. Sześć generacji dla `327` (b073 + b073b = 360 kr)
nie doszło ani razu (najlepsze 0,120). Ten sam plik z pierwszej
tury spełniał `water_splash` w całości. Zasada: przed wyborem
archetypu zmierzyć sporną metrykę na istniejących kartach tej
klasy; jeśli większość jej nie domyka, wziąć inny archetyp dla
tego samego dźwięku.

**24. Korekcję EQ aplikować tylko tam, gdzie zdejmuje flagę.** Próba na
27 kartach (`16 dull` + `11 harsh`) dała ten sam zysk flag (52 → 46),
ale 19 kart bez zysku dorzuciło **2 nowe pary** i podbiło maksimum
kosinusa 0,9415 → 0,9461 (próg bliźniaków 0,95). Po zawężeniu do 7 kart,
które faktycznie straciły flagę: pary 23 → **22**, maksimum bez zmiany.
Zasada: korekta bez efektu to czyste ryzyko — wycinać ją z `--ids`.

## Indeks rund i dostaw

Pełne opisy w `docs/archive/`. Skrót: `pary` = liczba par ≥ 0,90,
`krótkie` = kart z treścią < 2 s.

| batch | data | wynik | archiwum |
|---|---|---|---|
| r016–r033 | 2026-10-05 | kontrakty archetypów, 69 → 0 nie trafionych | `state-2026-10-05.md` |
| r034–r037 | 2026-10-06 | różnicowanie węzłów: 175 → 81 par | `state-2026-10-06.md` |
| r038–r045 | 2026-10-06 | kolejne piętra + trym ogonów: 81 → 21 par | `state-2026-10-06.md` |
| r046–r050 | 2026-10-06 | cleanup krótkiej treści: 69 → 26 krótkich | `state-2026-10-06.md` |
| r051 | 2026-10-06 | 6 krótkich nad progiem, 2 cofnięte | `state-2026-10-06.md` |
| r052 | 2026-10-06 | 6 nad progiem, 2 cofnięte | `state-2026-10-06.md` |
| r053 | 2026-10-07 | 3 nad progiem, 5 cofniętych | `state-2026-10-06.md` |
| r054 | 2026-10-07 | 3 trafione wydłużone bez utraty werdyktu (+2,07 s śr.) | `state-2026-10-06.md` |
| r055 | 2026-10-07 | 2 przyjęte (+2,23 s i +1,86 s), 5 cofniętych | `state-2026-10-06.md` |
| r056 | 2026-10-07 | **0 przyjętych** — diagnoza: krótki take się nie wypełnia | `state-2026-10-06.md` |
| b071 | 2026-10-07 | 2 nowe karty (280, 323), obie trafione z 0 flag | `state-2026-10-06.md` |
| b072 | 2026-10-07 | 2 nowe karty (324, 325), obie trafione; 325 po 5 próbach | `state-2026-10-07.md` |
| r057 | 2026-10-08 | 3 z 8 krótkich weszły, treść < 2 s 21 → 19 | `state-2026-10-08.md` |
| r058eq | 2026-10-08 | EQ za 0 kr: 7 kart, `dull` 16 → 11, `harsh` 11 → 9, flagi 52 → 46, pary 23 → 22 | `state-2026-10-08.md` |
| b073 | 2026-10-08 | 2 nowe karty (327, 328), obie trafione z 0 flag; 327 po zmianie archetypu | `state-2026-10-08-b073.md` |
| r058 | 2026-10-08 | 3 najgorsze karty swoich klas; weszła 113 (1,24 → 3,96 s), 232 i 434 cofnięte | `state-2026-10-08-r058.md` |
| r058b | 2026-10-08 | darmowe domknięcia krawędzi: 72 i 278 bez flag, 0 kredytów | `state-2026-10-08-r058b.md` |
| r059b | 2026-10-08 | `cut_start_hard` przeliczone na skok z ciszy; 2 fałszywe alarmy zdjęte, 9 prawdziwych trzasków naprawionych | `state-2026-10-08-r059b.md` |
| r060 | 2026-10-08 | klauzula `--fill-take` na 3 karty, które jej nigdy nie dostały; 583 (0,21 → 2,66 s) i 292 (1,38 → 3,22 s) weszły | `state-2026-10-08-r060.md` |
| r061 | 2026-10-08 | kolejne 3 karty bez fill-take; weszła 5 (1,87 → 2,30 s) z przyciętym ogonem, 98 i 71 cofnięte | `state-2026-10-08-r061.md` |
| r062 | 2026-10-08 | fill-take na 4, 145 i 71; weszła tylko 71 (1,40 → 2,30 s, centroid 268 → 1157 Hz), 4 i 145 cofnięte | `state-2026-10-08-r062.md` |
| r063 | 2026-10-08 | łańcuch zdarzeń na 23, 469 i 247; weszły 469 (1,99 → 3,43 s) i 247 (2,06 → 4,00 s), 23 cofnięta | `state-2026-10-08-r063.md` |
| r064 | 2026-10-08 | łańcuch zdarzeń na kartach 2,0–2,6 s; weszła 491 (2,13 → 2,67 s), 52 za jasna i 260 za ciemna — cofnięte | `state-2026-10-08-r064.md` |
| r065 | 2026-10-08 | rzeczowniki zamiast przymiotników barwy; weszły 67 (2,12 → 3,96 s) i 553 (2,12 → 3,14 s), 524 cofnięta | `state-2026-10-08-r065.md` |
| r066 | 2026-10-08 | rzeczowniki na 52, 372 i 445; weszła 445 (2,27 → 3,74 s), 52 cofnięta na rytmie, 372 za parę z 97 | `state-2026-10-08-r066.md` |
| r067 | 2026-10-08 | 52 dostała równy odstęp i weszła za 5. razem (2,20 → 3,21 s); 355 weszła (2,01 → 3,08 s); 501 cofnięta na `low_all` | `state-2026-10-08-r067.md` |
| b074 | 2026-10-09 | 7 nowych kart z luk w numeracji; wszystkie weszły trafione i bez flag; 340 wymagała zmiany archetypu na `steam_hiss` | `state-2026-10-09-b074.md` |
| r068 | 2026-10-09 | 501 bez pary weszła (2,75 → 3,80 s), 565 weszła (2,67 → 3,24 s), 308 cofnięta na `attack_s` | `state-2026-10-09-r068.md` |
| r069 | 2026-10-09 | 74 weszła (2,76 → 3,20 s) i wyleczyła flagę `boomy`; 308 cofnięta, bo była krótsza; 177 bez głosu | `state-2026-10-09-r069.md` |
| r070 | 2026-10-09 | 308 weszła (2,06 → 3,31 s, +1,25) — wzorzec trafiony na 3 z 3; 224 trafiona, ale tylko +0,04 s; 452 cofnięta, krótsza | `state-2026-10-09-r070.md` |
| r071 | 2026-10-09 | **trzy z trzech**: 608 (+1,40), 435 (+1,17), 17 (+0,50) = +3,07 s; trzy karty z „prawdopodobnie" na „trafiony" | `state-2026-10-09-r071.md` |
| r072 | 2026-10-09 | 20 weszła (2,28 → 3,09 s); 224 i 524 cofnięte 0/3 — obie złamały `attack_s` po skróceniu czasownika w otwarciu | `state-2026-10-09-r072.md` |
| r073 | 2026-10-09 | 224 weszła (2,47 → 3,56 s, +1,09) na dokładnym tekście z 308; 250 trafiona, ale krótsza; 524 znów atak | `state-2026-10-09-r073.md` |
| r074 | 2026-10-09 | **zero z trzech**; 332 odrzucona mimo 4,00 s i zera flag za trzy nowe pary — długie niskie dudnienie to region zajęty | `state-2026-10-09-r074.md` |
| r075 | 2026-10-09 | 216 i 567 weszły (+0,95 każda); 524 trafiona po 7 próbach, ale para 0,9316 z 243; pierwszy dobór po sprawdzaniu zajętości regionu | `state-2026-10-09-r075.md` |
| r076 | 2026-10-09 | 156 weszła (2,09 → 2,47 s) i wyleczyła `boomy`; 534 i 548 cofnięte — 7 z 8 trafionych wariantów wyszło krótszych | `state-2026-10-09-r076.md` |
| r077 | 2026-10-09 | 491 weszła (2,67 → 3,45 s) — jedyna niestalowa w transzy; 140 i 548 nie urosły mimo „clashing"; hipoteza z r076 obalona | `state-2026-10-09-r077.md` |
| r078 | 2026-10-09 | **zero z trzech**; hipoteza o materiale obalona (brąz, kamień, bariera); wniosek: wariancja modelu większa niż zmienne w prompcie | `state-2026-10-09-r078.md` |
| r079 | 2026-10-09 | pierwsza transza 2 × 5 wariantów; 333 weszła (+0,21 s) i jest bardziej odrębna; 534 dostała 5 prób i wszystkie wyszły krótsze | `state-2026-10-09-r079.md` |
| r080 | 2026-10-09 | **pięć prób dało to, czego trzy nie dały** — 140 ten sam prompt co w r077, +0,76 s (2,70 → 3,46); 370 cofnięta: 5/5 dłuższych, 4/5 nie przeszło arrow_flight | `state-2026-10-09-r080.md` |
| r081 | 2026-10-10 | 56 weszła (3,00 → 4,00 s); 210 cofnięta na `low_all`; kostur o kamień skreślony | `state-2026-10-10-r081.md` |
| r082 | 2026-10-10 | **dwie z dwóch**: 71 (2,30 → 3,21 s) i 453 (2,97 → 3,36 s), obie trafione, 0 flag | `state-2026-10-10-r082.md` |
| r083 | 2026-10-10 | 250 weszła (2,70 → 3,11 s); 209 cofnięta (+0,01 s) | `state-2026-10-10-r083.md` |
| r084 | 2026-10-10 | **zero z dwóch**; 277 +0,15 s za mało; 576 dłuższe złamały flatness | `state-2026-10-10-r084.md` |
| r085 | 2026-10-10 | **dwie z dwóch**: 232 (0,98 → 3,36 s) i 280 (2,03 → 2,57 s) | `state-2026-10-10-r085.md` |
| r086 | 2026-10-10 | **zero z dwóch**; 269 i 583 dłuższe, gorszy werdykt | `state-2026-10-10-r086.md` |
| r087 | 2026-10-10 | **zero z dwóch**; 12 werdykt; 332 para 0,90 z 558 | `state-2026-10-10-r087.md` |
| r088 | 2026-10-10 | **dwie z dwóch**: 18 (2,10 → 2,70 s) i 571 (2,29 → 2,64 s) | `state-2026-10-10-r088.md` |
| r089 | 2026-10-10 | **zero z dwóch**; 5 para z 98; 163 werdykt | `state-2026-10-10-r089.md` |
| r090 | 2026-10-10 | **dwie z dwóch**: 329 (2,17 → 2,59 s) i 262 (2,44 → 3,27 s) | `state-2026-10-10-r090.md` |
| r091 | 2026-10-10 | **zero z dwóch**; 9 centroid; 96 krótsza po łańcuchu | `state-2026-10-10-r091.md` |
| r092 | 2026-10-10 | **zero z dwóch**; 164 centroid; 72 decay | `state-2026-10-10-r092.md` |
| r093 | 2026-10-10 | 468 weszła (2,85 → 3,16 s); 177 para 0,95 z 396 | `state-2026-10-10-r093.md` |
| r094 | 2026-10-10 | **quota 0**; 2/10 plików, oba krótsze, bez instalacji | `state-2026-10-10-r094.md` |
| r095 | 2026-10-10 | **zero z dwóch**; nowy budżet OK; 157/607 krótsze po łańcuchu | `state-2026-10-10-r095.md` |
| r096 | 2026-10-10 | **dwie z dwóch**: 4 (1,14 → 1,59 s) i 150 (2,37 → 3,69 s) | `state-2026-10-10-r096.md` |
| r097 | 2026-10-10 | **jedna z dwóch**: 2 (2,37 → 3,41 s); 263 cofnięta | `state-2026-10-10-r097.md` |
| r098 | 2026-10-10 | **341 weszła** (2,66 s); 348 para z 207; 350/351 bez audio | `state-2026-10-10-r098.md` |
| r099 | 2026-10-10 | **351 weszła** (3,84 s); 350 cofnięta (dzwon) | `state-2026-10-10-r099.md` |
| r100 | 2026-10-10 | **350 weszła** (3,67 s, fire_crackle); 348 para z 18 | `state-2026-10-10-r100.md` |
| r101 | 2026-10-10 | **382 +0,60 s**; 348 psychic_shriek cofnięta | `state-2026-10-10-r101.md` |
| r102 | 2026-10-10 | prompty: 348 steam_hiss + 145 heavy_impact, 2 × 5 | `state-2026-10-10-r102.md` |
| b059–b070 | 2026-10-01…04 | dostawy właściciela, 553 → 557 | `state-2026-10-01.md` |
| b054–b058, r001–r009 | 2026-09-28…30 | start flow v2 | `state-2026-09-28.md` |

**r034–r058eq łącznie: 380 generacji + 7 korekt EQ, 175 → 22 par
(−87 %), treść < 2 s 41 → 19, flagi 53 → 46.**

## Co robić dalej

1. **Następna transza: `r102` — 2 karty × 5.** `348` `steam_hiss`
   i `145` `heavy_impact`.

2. **Więcej prób próbkuje rozkład, nie przesuwa go — a to
   wystarcza, gdy rozkład obejmuje cel.** Pięć wariantów
   powiększa próbkę, ale nie zmienia środka. `140` to udowodniła
   z obu stron: trzy próby dały 2,22 / 2,42 / 2,37 s, pięć dało
   2,66 / **3,46** / 2,54 / 3,21 / 2,95. Rozkład był ten sam,
   próbka większa i trafiła w ogon. Nie pomaga, gdy cały rozkład
   leży po złej stronie — `534` dostała pięć prób i wszystkie
   wyszły krótsze, `370` dostała pięć i żadna nie przeszła
   kontraktu.

3. **Przestać szukać jednej dźwigni w prompcie.** Łańcuch zdarzeń
   został — jest konieczny, bo bez niego większość wariantów w
   ogóle nie przechodzi werdyktu. Ale dobór między „clashing" a
   „striking", między stalą a korą, nie dał się zamienić w regułę.
   Zmienną, której nie kontroluję, jest wariancja modelu; zmienną,
   którą kontroluję, jest liczba prób.

4. **Czasownik uderzenia jest konieczny, ale nie wystarczający.**
   `r076` słusznie uznała, że „turning" i „rolling" szkodzą; `r077`
   pokazała, że samo „clashing" nie wystarczy — `140` i `548`
   dostały je i żadna nie urosła. Reguła z `r074` (materiał to
   rzeczownik, czynność to czasownik) zostaje, ale trzeba do niej
   dopisać dobór materiału.

5. **Łańcuch zdarzeń nie gwarantuje długości, tylko szansę na nią.**
   W `r075` trafił dwa razy na dwie karty, w `r076` zero razy na
   dwie — ten sam szkielet, inny wynik. Zmienną pod kontrolą jest
   materiał w otwarcie: rzeczownik (*plates, armour, chest*) plus
   czasownik uderzenia (*clashing, striking*). Czasownik ruchu
   (*turning, rolling, shifting*) odbiera łańcuchowi tempo.
   **To reguła z `r074`, którą złamałam własnoręcznie w `r076`.**

6. **Zajętość liczyć też po wygenerowaniu, nie tylko przed wyborem.**
   `524` miała **zero** sąsiadów ≥ 0,80 przed rundą, a jej v1 i tak
   zrobiła parę 0,9316 z `243`. Region wokół *obecnego* sampla bywa
   pusty, a region, w który trafia *nowy*, już nie — obecny sample
   nie jest dobrym przewodnikiem po miejscu docelowym.

7. **Reguła 1 działa w obie strony.** Instaluję wariant tylko wtedy,
   gdy jest **co najmniej tak dobry w werdykcie** jak obecny **i**
   wyraźnie dłuższy. `prawdopodobnie` zamiast `trafiony` to
   pogorszenie, nawet przy +1 s treści — długość jest środkiem do
   ikoniczności, nie celem samym w sobie.

8. **Przed wyborem karty sprawdzać zajętość regionu.** Policzyć, ilu
   sąsiadów ma kosinus ≥ 0,85; więcej niż dwóch oznacza region
   zajęty. Wtedy nie wydłużać ogonem, tylko liczbą zdarzeń o różnej
   barwie — o ile kontrakt na to pozwala.

9. **Lekcja z r070, która zmienia sposób pracy:** `--apply` w
   `rewrite_archetype_prompts.py` przepisuje też pole `music_allowed`
   na podstawie trzeciego elementu w `OVERRIDES`. Wpis dla `452`
   dostał `False` („bez muzyki"), więc chór dostał zakaz muzyki
   wewnątrz promptu, który sam miał być chórem. Wygenerowane
   warianty były z góry skażone. Przy wycofywaniu karty trzeba
   przywracać **cztery** pola, nie trzy: `prompt`,
   `sample_scenario`, `batch`, `duration_seconds` — i sprawdzać
   `music_allowed`, bo `--apply` mógł je zmienić. Wyłapał to
   walidator na CI (lokalnie `tail -1` ukrył błędy), więc żadne
   kredyty nie poszły na zmarnowany run.

10. **Commit bez pusha nie istnieje.** Dokumentacja `r079` raz
   przepadła: była zacommitowana lokalnie, ale nie wypchnięta, a
   potem sandbox został prze-clone'owany od zera i wrócił do
   commitu bazowego. Uratowały ją tylko warianty MP3, które bot
   zdążył wcisnąć na GitHuba w commitach `[import-…]`. Po audycie
   i instalacji **wypychać natychmiast**, nie odkładać na później.
   To samo dotyczy kopii zapasowych: `/tmp` nie jest częścią
   workspace'u i znika między wywołaniami, więc kopia przed rundą
   idzie do `.arena-backup/` (katalog w `.gitignore`).
   Przy odtwarzaniu `r079` trzeba było też naprawić `534`:
   wycofanie wpisu z `OVERRIDES` bez wycofania pól w
   `scenarios.jsonl` zostawiło kartę z `duration_mismatch`.
   Karta niezainstalowana wraca na **cztery** pola naraz.
11. **Kopie zapasowe wyłącznie w repozytorium, nigdy w `/tmp`.**
   `/tmp` nie jest częścią workspace'u i znika między wywołaniami —
   w `r074` i `r075` próba cofnięcia plików z `/tmp/pre-r07X.jsonl`
   kończyła się na `cannot stat`, bo kopia już nie istniała. Kopia
   przed rundą idzie do `.arena-backup/` (katalog jest w
   `.gitignore`). Bez tego jedyna droga powrotna to ręczna
   rekonstrukcja z JSON-a — działa, ale kosztuje dwa razy tyle.
12. **Limit długości jest liczony od ładunku API, nie od promptu.**
   `validate_sample_scenarios.py` wywołuje `api_payload()` ze scouta,
   który po prompt dokleja jeszcze „ No multi-layer cinematic scene."
   (32 znaki). Dlatego prompt 446 znaków może być za długi. Numerek
   wypisywany przez `rewrite_archetype_prompts.py` (np. „507/450")
   liczy **sam prompt z rozwinięciem**, więc zawyża i bywa
   mylący — wiążący jest wynik walidatora, nie ten numer.

13. **Praca bezkosztowa** — żadna z nich nie wymaga generowania, więc
   można ją robić równolegle z rundami:
   - **Dobór archetypu po fakcie.** `340` nie przeszła `robot_servo`
     w pięciu podejściach i piętnastu wariantach, a okazało się, że
     te same pliki są **trafione** pod `steam_hiss`. Wniosek: zanim
     uznać kartę za przegraną, sprawdzić jej istniejące warianty
     przeciwko innym archetypom — to zero kredytów.
   - **`--fix-mono` na 25 parach i flagach stereo.** Flaga
     `mono_collapse` zniknęła na `334` po jednym przejściu
     (`lr_correlation` 0,195 → 0,589).
   - **Ręczne cięcie ciszy.** `329` miała 1,07 s ciszy na początku,
     której nie brał `--trim-lead-s`. Ucięcie z marginesem 0,20 s
     dało lead 0,04 s, zero flag i kosinus 0,8757 (bez pary).
     Uwaga: po cięciu trzeba skorygować `duration_seconds` w
     `scenarios.jsonl`, bo inaczej wchodzi `duration_mismatch`,
     a fingerprint przesuwa się na tyle, że może dobrać parę.
   - **Ponowny audyt** i porównanie z ostatnim raportem.
   `501` to ten sam archetyp, w którym rzeczowniki dały `67` +1,84 s
   w r065. Jej obecny prompt jest jeszcze przymiotnikowy („two heavy
   blasts with a low thump, over loud gritty metallic knocking...
   carried clearly in the middle of the range") — dostanie sam
   mechanizm: cylinder, zawór, pompa, korbowód.
   `52` wraca po raz trzeci i tym razem diagnoza jest wąska. W r064
   poległa na barwie (centroid 8309–9512), w r066 rzeczowniki barwę
   **naprawiły** (v1 5936, v3 5392 — oba w oknie 800–6000), ale
   wszystkie trzy złamały `ioi_cv` (1,33–2,23 przy progu 0,8):
   mechanizm stukał nierówno. Został jeden warunek — równy odstęp.
   Obecny sample ma `ioi_cv` 0,252, czyli wzorzec jest w korpusie.
   `355` leży w `plate_clank`, archetypie który odpowiedział na
   łańcuch zdarzeń trzy razy z rzędu (`491` +0,54 s, `445` +1,47 s,
   a w r066 wszystkie trzy warianty `445` przeszły kontrakt). Jej
   prompt ma już łańcuch („five separate steel plates"), ale kończy
   się przymiotnikiem „distinct and mid-pitched" bez domknięcia.
   `372` odpoczywa: jej najlepszy wariant dobrałby parę z `97`
   (0,9212), a drugi złamał `low_all` o 0,001 (0,249 przy progu 0,25).
   `524`, `4`, `145`, `23`, `98`, `12`, `232`, `260` — bez zmian.
   `553` i `524` to ten sam profil, który dał `247` (+1,94 s) i `491`
   (+0,54 s): **jedna próba, brak fill-take, prompt bez domknięcia.**
   `553` ma dodatkowo kontrakt już teraz **złamany** (score 1,0),
   bo jej prompt opisuje „steel sliding into a tarry basin... one slow
   drip" — czyli ciecz, nie klingę. Nowy prompt może naprawić i
   długość, i rozpoznawalność naraz.
   `67` wraca z największą luką w całym korpusie (1,52 s). Jej okno
   kontraktowe jest szerokie (centroid ≤ 2600, `mid_up` ≥ 0,1,
   `low_all` ≥ 0,35), więc ryzyko barwowe, które położyło `52` i `260`,
   jest tu mniejsze.
   **Wniosek z r064, ważniejszy od doboru:** `52` i `260` nie poległy
   na długości — oba łańcuchy zadziałały (3,10–3,61 s). Poległy na
   BARWIE, i to w przeciwnych kierunkach, mimo że oba prompty mówiły
   wprost „low dull wooden" i „huge roaring". Model ignoruje
   przymiotniki barwy, realizuje rzeczowniki. `491` dostał sam
   rzeczownik („six plates snapping into place with a firm woody
   clank") i wyszedł czysto. W r065 opisuję tylko zdarzenia i
   materiał, zero przymiotników barwy.
14. **Wątek bez kredytów — po `r058eq`:** `dull` zeszło z 16 na 11,
   `harsh` z 11 na 9. Tanich ruchów już nie ma: `harsh` wymaga
   −12…−15 dB przy 8 kHz na kartach z 0,94–0,98 energii w paśmie
   powietrznym (`226`, `6`, `522` nie mieszczą się nawet przy −15 dB),
   a `dull` przy +3 dB nie dobija do progu 0,005 energii > 2 kHz na
   `339`, `496`, `32`, `51`, `118`, `358`, `159`, `37`, `83`, `468`.
   Obie grupy domykają się tylko nowym materiałem (kredyty).
3. Pilnować `check_required_reading.py` przy każdym dopisywaniu do tego
   pliku (limit 50 000 tokenów).

## Archiwum

Narracje poszczególnych rund i dostaw — czyli wszystko, co nie jest
bieżącym stanem ani obowiązującą regułą — leżą w:

```text
docs/archive/state-2026-09-28.md   start flow v2, r001–r009, b054–b058
docs/archive/state-2026-10-01.md   b059–b070, r010–r015
docs/archive/state-2026-10-05.md   kontrakty archetypów, r016–r033
docs/archive/state-2026-10-06.md   r034–r056, dostawa b071
docs/archive/state-2026-10-07.md   dostawa b072 (324, 325)
docs/archive/state-2026-10-08.md   runda r057 i korekta EQ r058eq
docs/archive/state-2026-10-08-b073.md   dostawa b073 (327, 328)
docs/archive/state-2026-10-08-r058.md   runda r058 (113, 232, 434)
docs/archive/state-2026-10-08-r058b.md  krawędzie: 72, 278 (0 kredytów)
docs/archive/state-2026-10-08-r059.md   runda r059 (434 weszła, 232 cofnięta)
docs/archive/state-2026-10-08-r059b.md  nowa definicja cut_start_hard + 9 napraw
docs/archive/state-2026-10-08-r060.md   runda r060 (583, 292 weszły, 71 cofnięta)
docs/archive/state-2026-10-08-r061.md   runda r061 (5 weszła, 98 i 71 cofnięte)
docs/archive/state-2026-10-08-r062.md   runda r062 (71 weszła, 4 i 145 cofnięte)
docs/archive/state-2026-10-08-r063.md   runda r063 (469 i 247 weszły, 23 cofnięta)
docs/archive/state-2026-10-08-r064.md   runda r064 (491 weszła, 52 i 260 cofnięte)
docs/archive/state-2026-10-08-r065.md   runda r065 (67 i 553 weszły, 524 cofnięta)
docs/archive/state-2026-10-08-r066.md   runda r066 (445 weszła, 52 i 372 cofnięte)
docs/archive/state-2026-10-08-r067.md   runda r067 (52 i 355 weszły, 501 cofnięta)
docs/archive/state-2026-10-09-b074.md   paczka b074 (7 nowych kart, 5 paczek generacji)
docs/archive/state-2026-10-09-r068.md   runda r068 (501 i 565 weszły, 308 cofnięta)
docs/archive/state-2026-10-09-r069.md   runda r069 (74 weszła, 308 i 177 cofnięte)
docs/archive/state-2026-10-09-b074.md   paczka b074 (7 nowych kart, 5 paczek generacji)
docs/archive/state-2026-10-10-r081.md   runda r081 (56 weszła, 210 cofnięta)
docs/archive/state-2026-10-10-r082.md   runda r082 (71 i 453 weszły)
docs/archive/state-2026-10-10-r083.md   runda r083 (prompty 209, 250)
```

Archiwum powstało 2026-10-07 przez wycięcie historii z tego pliku:
`STATE.md` urósł do 3854 linii i sam ważył 51 485 tokenów, czyli więcej
niż cały limit `check_required_reading.py` (50 000). Zasada z
`docs/required-reading.md`: przy przekroczeniu przenieś szczegóły
historyczne do `docs/archive/` **bez utraty decyzji, reguł i procedur** —
dlatego reguły z r050–r056 zostały przepisane wyżej, a nie wycięte.
