# Pełny audyt korpusu sampli — 2026-09-28

Zakres: **527** plików `audio/samples/<id>.mp3`. Skan od zera skryptem
`scripts/audit_samples_full.py` (dekodowanie PCM → metryki sygnałowe,
głośnościowe, widmowe i odciski brzmieniowe). Audyt **niczego nie zmienia**.

## Co nowego względem audytu porannego

Poprzedni audyt (`2026-09-28-audio-audit.md`) mierzył obwiednię, peak i ciszę.
Ten skan dokłada cztery wymiary, których wcześniej nie sprawdzaliśmy:

1. **Głośność percepcyjna (LUFS, BS.1770-4)** + **true peak** (4x nadpróbkowanie) —
   peak próbkowy nie mówi, czy sample będzie słyszalny w bibliotece obok innych.
2. **Rozkład energii w pasmach** — wyłapuje sample zepchnięte w infradźwięki
   (peak pokazuje „głośno", a na telefonie nie słychać nic) i takie bez treści
   powyżej 250 Hz.
3. **Tonalność i mowa** — spectral flatness, śledzenie f0 i modulacja obwiedni
   2–8 Hz; prompty zabraniają muzyki i mowy, więc to kontrola zgodności z regułą.
4. **Duplikaty i bliźniaki** — md5 zdekodowanego PCM oraz kosinus odcisków
   log-mel; reguła projektu wymaga unikalnego sampla dla każdej fabuły.

## Uczciwe zastrzeżenia

- **LUFS na 2–3 s materiale** jest przybliżeniem (standard zakłada dłuższy program).
  Używam go porównawczo wewnątrz korpusu, nie jako certyfikowanego pomiaru.
- **Tonalność ≠ muzyka.** Dzwon, gong, rezonans metalu czy gwizd wiatru też są tonalne.
  Flaga `tonal_sustained` to kandydat do odsłuchu, nie wyrok.
- **Mowa** wykrywana heurystycznie (modulacja sylabiczna + pasmo mowy). Krzyki
  stworów i skrzypienie drewna potrafią ją udawać — pewność niska.
- **Bliźniaki brzmieniowe**: wysoki kosinus log-mel oznacza „podobna barwa i przebieg
  w czasie", a nie „ten sam plik". Dwa różne uderzenia miecza *mają prawo* być podobne.
- **`cut_start_hard`** dla dźwięków ciągłych (deszcz, tłum, bitwa) bywa naturalne —
  kategoria utrzymana z poprzedniego audytu dla porównywalności.
- **True peak i peak** liczone są na **zdekodowanym** MP3, więc zależą od dekodera;
  wartości > 0 dBFS to normalny overshoot kodera, nie błąd generacji.
- **Infradźwięki vs „ciemny dźwięk"**: LUFS jest ważony percepcyjnie (filtr K tłumi
  dół pasma), dlatego plik z peakiem −0,3 dBFS potrafi mieć −20 LUFS. To nie jest
  błąd pomiaru, tylko dokładnie to, co usłyszy właściciel.
- Kategorie `sub_dominant` i `muffled` **częściowo się pokrywają** — pierwsza mówi
  „energia poszła w dół pasma", druga „nie ma nic w paśmie detalu".

## Podsumowanie

| Kategoria | Plików | Pewność | Rekomendacja |
|---|---|---|---|
| KRYTYCZNE — (prawie) cisza | 0 | wysoka | regeneracja |
| WYSOKIE — ucięty koniec | 1 | wysoka | odsłuch → regeneracja/fade |
| WYSOKIE — za cicho (LUFS/peak) | 1 | wysoka | normalizacja w postprodukcji |
| WYSOKIE — energia w infradźwiękach | 0 | wysoka | EQ+normalizacja albo regeneracja |
| WYSOKIE — brak treści powyżej 250 Hz | 25 | średnia | odsłuch → regeneracja |
| WYSOKIE — treść krótsza niż 0,8 s | 19 | wysoka | trym albo regeneracja |
| ŚREDNIE — przester (clipping) | 0 | średnia | tłumienie + limiter |
| ŚREDNIE — true peak > +1 dBTP | 0 | średnia | limiter w postprodukcji |
| ŚREDNIE — za głośno | 0 | średnia | wyrównanie głośności |
| ŚREDNIE — offset DC | 0 | wysoka | filtr górnoprzepustowy 20 Hz |
| DO ODSŁUCHU — tonalne/„muzyczne" | 8 | niska | weryfikacja uchem |
| DO ODSŁUCHU — podobne do mowy | 3 | niska | weryfikacja uchem |
| DO ODSŁUCHU — start na pełnym poziomie | 12 | niska | weryfikacja uchem / fade-in |
| BLIŹNIAKI — para sampli ≥ 0.95 kosinusa | 25 | niska | odsłuch pary, ewentualnie nowy prompt |
| KOSMETYCZNE — długa cisza wiodąca | 16 | wysoka | opcjonalny trym |
| KOSMETYCZNE — długa cisza końcowa | 47 | wysoka | opcjonalny trym |

Plików z co najmniej jedną flagą: **107** / 527.
Plików z flagą **merytoryczną** (bez kategorii kosmetycznych i „start na pełnym
poziomie"): **46**.


## Najważniejszy wniosek: korpus nie ma wyrównanej głośności

Rozkład głośności percepcyjnej: mediana **-20.0 LUFS**, p10 **-21.3**, p90 **-20.0**, σ **1.5 LU**, rozpiętość **19.8 LU** (od -38.6 do -18.8).

To nie jest kwestia pojedynczych odstających plików — **cały korpus jest nierówny**.
Przy odsłuchu biblioteki po kolei jedne sample są ledwie słyszalne, inne wyrywają
głośniki. Nic dziwnego: każdy plik przyszedł z generatora bez wspólnego odniesienia.

Gdyby wyrównać wszystko do **-20 LUFS** z sufitem **−1 dBTP**:

- plików wymagających wzmocnienia > +10 dB: **3** (z tego > +15 dB: 1 — tam wyjdzie szum tła, lepiej zregenerować),
- plików wymagających wyciszenia > 6 dB: **0**,
- plików w granicach ±3 dB od celu: **504**.

Operacja jest lokalna, odwracalna i **nie kosztuje kredytów**. Rekomendacja: zrobić ją
jednym przebiegiem na całym korpusie, dopiero potem oceniać pojedyncze sample uchem —
bo dziś ocena „ten jest za cichy" myli się z „ten jest zły".

## 1. KRYTYCZNE — plik (prawie) cichy

Materiał w praktyce niesłyszalny — regeneracja, nie postprodukcja.

_Brak plików w tej kategorii._

## 2. WYSOKIE — ucięty koniec (brak wybrzmienia)

Sortowane od najbrutalniejszego cięcia. Fade-out 0,2–0,35 s naprawia to bez kredytów.

| ID | Tytuł | Koniec 10 ms | Maks. ramka | Różnica | Inne flagi |
|---|---|---|---|---|---|
| 445 | Locthwain Paladin | -29.3 dBFS | -10.57 dBFS | -18.7 dB | — |

## 3. WYSOKIE — za cicho względem korpusu

Próg: LUFS < -32 albo peak < −18 dBFS. Większość naprawia normalizacja (bez kredytów); przy wzmocnieniu > +15 dB trzeba sprawdzić, czy nie wychodzi szum.

| ID | Tytuł | LUFS | Peak dBFS | Aktywny RMS | Inne flagi |
|---|---|---|---|---|---|
| 115 | Merfolk Mesmerist | -38.57 | -11.61 | -40.13 | — |

## 4. WYSOKIE — energia zepchnięta w infradźwięki

Ponad 80 % energii poniżej 60 Hz. Miernik peaku pokazuje „głośno", ale na laptopie, telefonie i większości słuchawek taki sample jest praktycznie niesłyszalny — dlatego LUFS (ważony percepcyjnie) bywa tu 20 dB niżej niż peak. Naprawa: EQ (odcięcie 40 Hz) + normalizacja, a jeśli po tym nie zostaje treść — regeneracja.

_Brak plików w tej kategorii._

## 5. WYSOKIE — brak treści powyżej 250 Hz

Mniej niż 2 % energii powyżej 250 Hz — w paśmie, w którym ucho rozpoznaje materiał i detal, nie ma nic. Dla tąpnięcia olbrzyma to bywa poprawne, dla metalu, szkła, ptaków czy magii oznacza zgubioną treść.

| ID | Tytuł | Udział > 250 Hz | Centroid | LUFS | Inne flagi | Scenariusz |
|---|---|---|---|---|---|---|
| 383 | Supernatural Stamina | 0.0002 | 63 Hz | -20.62 | — | dwa głębokie, powolne uderzenia serca z  |
| 107 | Somberwald Spider | 0.0005 | 78 Hz | -20.0 | — | tąpnięcia i wibracje grubych nici pajęcz |
| 153 | Balamb Garden, Airborne | 0.0005 | 84 Hz | -20.0 | — | turkusowe silniki latającej akademii odg |
| 51 | Deepwood Denizen | 0.0008 | 65 Hz | -20.47 | — | głuchy drzewny puls jak stłumione serce  |
| 330 | Invasion of the Giants | 0.0013 | 75 Hz | -20.0 | — | zbliżające się, coraz cięższe kroki olbr |
| 567 | Jwar Isle Avenger | 0.0035 | 66 Hz | -20.01 | — | zwrot sfinksy nad hedronami i cios w pan |
| 118 | Dire-Strain Brawler | 0.0056 | 104 Hz | -20.0 | — | niski spokojny pomruk wilkołaka stojąceg |
| 71 | Security Rhox | 0.0060 | 62 Hz | -20.09 | cut_start_hard | głuche, gumowate uderzenie ciała o niewi |
| 301 | Guildscorn Ward | 0.0061 | 114 Hz | -20.15 | — | podwójne tąpnięcie ciał o napiętą niewid |
| 450 | Thornhide Wolves | 0.0061 | 64 Hz | -20.0 | — | wilk o skórze jak kora rozsuwający kolcz |
| 428 | Curiosity | 0.0076 | 62 Hz | -20.0 | cut_start_hard | łomot ciężkich pazurów walących raz za r |
| 125 | Ordinary Bear | 0.0077 | 124 Hz | -20.0 | — | rytmiczny pradawny taniec niedźwiedzi w  |
| 132 | Pilgrim's Eye | 0.0095 | 61 Hz | -20.0 | — | mechaniczne oko pielgrzyma kreślące kręg |
| 129 | Charismatic Vanguard | 0.0101 | 67 Hz | -20.0 | — | uniesienie święconego młota krasnoluda z |
| 72 | Dragon Arch | 0.0116 | 72 Hz | -20.0 | long_trail_silence | wyłanianie się smoka z żarzącego portalu |
| 588 | Cemetery Recruitment | 0.0126 | 81 Hz | -20.0 | — | fioletowy blask Liliany wskrzeszający wo |
| 273 | Fertile Thicket | 0.0138 | 153 Hz | -20.0 | — | oddychająca ziemia pulsująca maną pod dł |
| 235 | Trestle Troll | 0.0141 | 128 Hz | -20.0 | — | przestępowanie olbrzymiego trolla po fil |
| 539 | Silvanus's Invoker | 0.0146 | 84 Hz | -20.0 | — | zew ziemi i wyłaniający się żywiołak ska |
| 228 | Strandwalker | 0.0164 | 71 Hz | -20.0 | — | krok żywego ekwipunku na szczudlastych s |
| 182 | Stomping Slabs | 0.0175 | 157 Hz | -20.0 | — | oglącowe kamienne płyty przelatujące nis |
| 281 | Moonlit Meditation | 0.0175 | 81 Hz | -20.0 | — | koncentryczne fale w idealnym rytmie od  |
| 181 | Spectral Prison | 0.0188 | 131 Hz | -20.0 | — | niski równy buczący ton pola więziennego |
| 289 | Rustvine Cultivator | 0.0188 | 94 Hz | -20.0 | — | kropla czarnego oleju karmiąca metaliczn |
| 207 | Feed the Infection | 0.0193 | 95 Hz | -20.0 | — | czarne wici oleju przeszywające skórę wy |

## 6. ŚREDNIE — przester i true peak

Przester = > 0.05 % próbek na pełnej skali (w tym korpusie: brak). True peak > +1 dBTP to ryzyko zniekształceń po transkodowaniu — naprawialne limiterem, bez kredytów.

_Brak plików w tej kategorii._

## 7. WYSOKIE — realna treść krótsza niż 0,8 s

Po odjęciu ciszy zostaje bardzo mało dźwięku. Czasem to poprawne (jedno uderzenie), czasem generacja urwała temat. Flaga liczona **progiem względnym** (40 dB poniżej maksimum pliku), bo próg absolutny przesuwa się razem z poziomem nagrania — kolumna obok pokazuje, ile wychodzi po staremu.

| ID | Tytuł | Treść (próg wzgl.) | Treść (próg −45 dBFS) | Długość pliku | Scenariusz |
|---|---|---|---|---|---|
| 304 | Sagittars' Volley | 0.13 s | 0.09 s | 2.48 s | salwa trzech elfich łuków zwolniona w jednym  |
| 46 | Selesnya Charm | 0.21 s | 0.14 s | 2.48 s | miękki wystrzał świeżych pędów i liści rozwij |
| 460 | Ivy Lane Denizen | 0.21 s | 0.14 s | 2.48 s | dopasowanie rogowego napierśnika na tors młod |
| 185 | Alaborn Trooper | 0.31 s | 0.3 s | 2.48 s | donośne uderzenie włóczni w bruk przy żołnier |
| 576 | Akroan Sergeant | 0.34 s | 0.28 s | 2.48 s | sygnał sierżanta mieczem i złota aura na tarc |
| 1 | Dunland Crebain | 0.38 s | 0.27 s | 2.0 s | ostre pojedyncze krakanie kruka pikującego na |
| 403 | Dementia Bat | 0.43 s | 0.36 s | 2.48 s | pęknięcie metalowego pancerza nietoperza i ch |
| 610 | Gearsmith Prodigy | 0.46 s | 0.41 s | 2.48 s | mechaniczny lis z mosiężnego filigranu w skok |
| 591 | Rust-Shield Rampager | 0.47 s | 0.34 s | 2.48 s | szop z tarczą z garnka i szopię w hełmie w sz |
| 270 | Roiling Regrowth | 0.48 s | 0.48 s | 2.48 s | hedry pękają, a z czarnego bazaltu wyrastają  |
| 520 | Rakshasa Vizier | 0.52 s | 0.37 s | 2.48 s | turkusowa mgła nekromancji wzmacniająca raksh |
| 466 | Basilisk Gate | 0.55 s | 0.42 s | 2.48 s | złoty rezonans bram miasta nasycający pancerz |
| 17 | Selhoff Occultist | 0.57 s | 0.49 s | 2.48 s | ostry świst rytualnego sztyletu rozcinający z |
| 442 | Cenn's Tactician | 0.58 s | 0.41 s | 2.48 s | jedno równoczesne tupnięcie szeregu obrońców  |
| 472 | Kazuul's Toll Collector | 0.58 s | 0.32 s | 2.48 s | ogry poborca zawieszający zdobyczny oręż na s |
| 592 | Glorifier of Suffering | 0.58 s | 0.52 s | 2.48 s | rozbity relikwiarz i karmazynowe wstęgi mocy  |
| 77 | Annie Flash, the Veteran | 0.66 s | 0.49 s | 2.48 s | wystrzał elektrycznej wiązki z trójlufowej rę |
| 283 | Magic Damper | 0.67 s | 0.33 s | 2.48 s | tłumiąca kopuła heksagonów rozpryskująca poci |
| 593 | Inspiring Captain | 0.78 s | 0.42 s | 2.48 s | tupnięcie i donośne rżenie rumaka bojowego pr |

## 8. ŚREDNIE — offset DC

Stała składowa w sygnale. Filtr górnoprzepustowy 20 Hz usuwa ją bezstratnie dla treści słyszalnej.

_Brak plików w tej kategorii._

## 9. ŚREDNIE — za głośno względem korpusu

Próg: LUFS > -6.5. Sample wyrywa się z biblioteki przy odsłuchu seryjnym.

_Brak plików w tej kategorii._

## 10. DO ODSŁUCHU — tonalne / potencjalnie muzyczne

Stabilna wysokość dźwięku przez większość pliku. Dla dzwonu/gongu/rezonansu to poprawne; flaga ma sens tylko jeśli scenariusz nie zakładał źródła tonalnego.

| ID | Tytuł | Ramki tonalne | f0 | σ f0 (półtony) | Flatness | Scenariusz |
|---|---|---|---|---|---|---|
| 91 | Curse of the Pierced Heart | 1.00 | 727 Hz | 0.0 | 0.0001 | wbicie ciernia w serce rytualnej figurki z szarpnięciem kląt |
| 163 | Ghoulcaller's Bell | 1.00 | 727 Hz | 0.0 | 0.0003 | dźwięk patynowanego dzwonu nekromanty z sączącą się mgłą |
| 507 | Shatter | 1.00 | 1000 Hz | 0.0 | 0.0002 | rozsadzenie żelaznego golema w ognistą mandalę |
| 586 | Fourth Bridge Prowler | 1.00 | 1000 Hz | 0.0 | 0.0001 | miniaturowy ładunek eteru osłabiający strażnika z cienia |
| 551 | Contested Game Ball | 0.99 | 1000 Hz | 0.0 | 0.0005 | ciężka kamienna kula obijająca się ostro o kamienną obręcz b |
| 347 | Pristine Talisman | 0.98 | 888 Hz | 0.0 | 0.0007 | pojedyncze czyste uderzenie małego wypolerowanego dzwonka z  |
| 521 | Leafcrown Dryad | 0.93 | 333 Hz | 0.43 | 0.0026 | jeżyny tkające sieć pułapki pod koronami drzew |
| 155 | Demolish | 0.80 | 1000 Hz | 0.0 | 0.0152 | detonacja bramy i zawalenie wiaduktu w morze ognia |

## 11. DO ODSŁUCHU — podobne do mowy

Heurystyka mowy — niska pewność. Sprawdzić, czy nie ma zrozumiałych słów (prompty zabraniają mowy).

| ID | Tytuł | Modulacja 2–8 Hz | Udział dźwięcznych | Centroid | Scenariusz |
|---|---|---|---|---|---|
| 489 | Seer's Lantern | 0.85 | 1.00 | 642 Hz | zgrzyt przesłony latarni i narastający krystaliczny ton szkł |
| 163 | Ghoulcaller's Bell | 0.58 | 1.00 | 2391 Hz | dźwięk patynowanego dzwonu nekromanty z sączącą się mgłą |
| 580 | Loporrit Scout | 0.56 | 0.80 | 1474 Hz | pogodne, gulgoczące ćwierknięcie chocobo tuż przy uchu |

## 12. BLIŹNIAKI — sample brzmiące niemal identycznie

Kosinus odcisków log-mel ≥ 0.95. Identyczny PCM (md5): **0** grup.

| Kosinus | ID A | Tytuł A | ID B | Tytuł B | Scenariusz A | Scenariusz B |
|---|---|---|---|---|---|---|
| 0.973 | 321 | Ainok Artillerist | 507 | Shatter | wystrzał balisty z drewna świętych gajów | rozsadzenie żelaznego golema w ognistą mandal |
| 0.969 | 39 | Brute Force | 142 | Savage Hunger | grząski tupnięcie orka z rozbryzgiem błota i  | taranowanie zamarzniętej palisady przez głodn |
| 0.969 | 470 | Springbloom Druid | 527 | Shiva, Warden of Ice | ofiara z żyznej gleby i wybuch dwóch drzew w  | transformacja w Shivę zamrażająca całe pole b |
| 0.967 | 142 | Savage Hunger | 535 | Lab Rats | taranowanie zamarzniętej palisady przez głodn | skaveńskie laboratoryjne cykle klatek i mecha |
| 0.965 | 510 | Angel of the Dawn | 568 | Nanoform Sentinel | anielska zjawa o brzasku złotym pyłem nad mur | rój nano-cząsteczek zasklepiający pęknięte pr |
| 0.964 | 39 | Brute Force | 70 | Capture Sphere | grząski tupnięcie orka z rozbryzgiem błota i  | zamknięcie szarżującej bestii w fraktalnej sf |
| 0.963 | 153 | Balamb Garden, Airborne | 330 | Invasion of the Giants | turkusowe silniki latającej akademii odginają | zbliżające się, coraz cięższe kroki olbrzymów |
| 0.961 | 15 | Tellah, Great Sage | 155 | Demolish | eksplozja ognia i błyskawic wyrywająca się z  | detonacja bramy i zawalenie wiaduktu w morze  |
| 0.961 | 71 | Security Rhox | 428 | Curiosity | głuche, gumowate uderzenie ciała o niewidzial | łomot ciężkich pazurów walących raz za razem  |
| 0.960 | 236 | Agate Assault | 486 | Krallenhorde Wantons | kaskada głazów z pękającej krawędzi urwiska w | trzask wrót gospody pod uderzeniem przywódcy  |
| 0.959 | 107 | Somberwald Spider | 153 | Balamb Garden, Airborne | tąpnięcia i wibracje grubych nici pajęczej si | turkusowe silniki latającej akademii odginają |
| 0.959 | 137 | Withstand | 155 | Demolish | strumień ognia rozpraszający się na krawędzia | detonacja bramy i zawalenie wiaduktu w morze  |
| 0.955 | 15 | Tellah, Great Sage | 601 | Exploding Borders | eksplozja ognia i błyskawic wyrywająca się z  | zderzenie Jundu z Nayą — lawa pochłania prast |
| 0.955 | 39 | Brute Force | 535 | Lab Rats | grząski tupnięcie orka z rozbryzgiem błota i  | skaveńskie laboratoryjne cykle klatek i mecha |
| 0.955 | 306 | Mysteries of the Deep | 470 | Springbloom Druid | długi syk morskiej wody cofającej się po mokr | ofiara z żyznej gleby i wybuch dwóch drzew w  |
| 0.954 | 155 | Demolish | 601 | Exploding Borders | detonacja bramy i zawalenie wiaduktu w morze  | zderzenie Jundu z Nayą — lawa pochłania prast |
| 0.954 | 99 | Steelfin Whale | 450 | Thornhide Wolves | magnetyczne fiszbiny stalowego wieloryba zbie | wilk o skórze jak kora rozsuwający kolczasty  |
| 0.954 | 300 | Gila Courser | 595 | Óin the Brave | galop jaszczura-kuriera po czerwonej skale ka | dźwięczna kaskada złotych monet zsuwających s |
| 0.953 | 128 | Undead Servant | 152 | Timely Interference | wydobycie się nieumarłego z rozkopanego grobu | ryw i cios kavu wyskakującego zza kolumny w b |
| 0.953 | 122 | Blazing Torch | 376 | Doomed Dissenter | trzask smołowej pochodni płonącej w uchwycie  | powstanie napęczniałego nieżywego odszczepień |
| 0.952 | 18 | Lotusguard Disciple | 76 | Negate | iskry i odłamki odbijające się od pulsującej  | rozbicie strumienia zaklęcia o niewidzialną b |
| 0.952 | 459 | Prismari Campus | 585 | Jolrael, Mwonvuli Recluse | zderzenie ognia i wody w taflę lodu i pary na | niemy rozkaz druidki — pantery wyskakują nad  |
| 0.952 | 243 | Willbender | 486 | Krallenhorde Wantons | zaklęcie skręcające ze swojego toru nad wodam | trzask wrót gospody pod uderzeniem przywódcy  |
| 0.951 | 76 | Negate | 300 | Gila Courser | rozbicie strumienia zaklęcia o niewidzialną b | galop jaszczura-kuriera po czerwonej skale ka |
| 0.951 | 58 | Mobile Garrison | 507 | Shatter | syk pneumatycznej rampy wozu bojowego i jej c | rozsadzenie żelaznego golema w ognistą mandal |

## 13. Kontrola tekstów scenariuszy

Wszystkie prompty i opisy scenariuszy są unikalne (527/527).

## 14. KOSMETYCZNE — cisza w pliku

- cisza wiodąca > 0.6 s: **16** plików (604, 460, 65, 218, 140, 360, 403, 463, 578, 232, 500, 304, 382, 560, 561, 292)
- cisza końcowa > 1.5 s: **47** plików (46, 175, 472, 591, 251, 283, 514, 610, 466, 197, 355, 520, 442, 17, 593, 616, 576, 592, 142, 14, 556, 482, 453, 270, 304 …)

To nie jest błąd generacji — sample po prostu nie wypełnia całej zadeklarowanej
długości. Trym/skrócenie pliku jest opcjonalne i bezkosztowe.

## 15. Różnice względem audytu po rundzie r005

- flagi merytoryczne w poprzednim skanie: **121**, teraz: **46**
- nowe (nie widział ich poprzedni zestaw metryk): 46, 442, 445, 466, 520
- zniknęły: 8, 11, 20, 24, 33, 37, 54, 55, 65, 66, 70, 85, 88, 91, 93, 101, 112, 119, 139, 141, 143, 151, 155, 157, 160, 172, 175, 191, 197, 200, 206, 221, 223, 227, 240, 251, 252, 258, 285, 292, 294, 303, 308, 311, 313, 343, 345, 346, 352, 370, 385, 396, 420, 422, 435, 439, 444, 453, 461, 468, 471, 492, 494, 509, 526, 529, 548, 550, 559, 560, 562, 572, 577, 578, 584, 598, 600, 605, 608, 615

Uwaga: poprzedni skan nie mierzył LUFS, pasma, tonalności ani duplikatów,
więc większość „nowych" pozycji to nie regresja plików, tylko nowe kryterium.

## 16. Rekomendowana kolejka decyzji

Kolejność jest celowa: najpierw tania, odwracalna obróbka całego korpusu, dopiero
potem odsłuch i dopiero na końcu wydawanie kredytów.

1. **Postprodukcja lokalna, 0 kredytów** — wyrównanie głośności całego korpusu, limiter −1 dBTP, filtr DC. Bezpośrednio dotyczy 2 plików z flagami głośnościowymi: 115, 445

2. **Do odsłuchu przed decyzją** — 63 ID (tonalne, mowopodobne, bliźniaki, krótka treść): 1, 15, 17, 18, 39, 46, 58, 70, 71, 76, 77, 91, 99, 107, 122, 128, 137, 142, 152, 153, 155, 163, 185, 236, 243, 270, 283, 300, 304, 306, 321, 330, 347, 376, 403, 428, 442, 450, 459, 460, 466, 470, 472, 486, 489, 507, 510, 520, 521, 527, 535, 551, 568, 576, 580, 585, 586, 591, 592, 593, 595, 601, 610

3. **Kandydaci do regeneracji (kredyty, po potwierdzeniu uchem)** — 25 ID bez treści w paśmie słyszalnym: 51, 71, 72, 107, 118, 125, 129, 132, 153, 181, 182, 207, 228, 235, 273, 281, 289, 301, 330, 383, 428, 450, 539, 567, 588

   Uwaga: część z nich to scenariusze **celowo** niskie (kroki olbrzymów, tąpnięcia,
   bicie serca). Jeśli po EQ i normalizacji brzmią poprawnie, regeneracja jest zbędna.

Pełne metryki per plik: JSON obok tego raportu.

