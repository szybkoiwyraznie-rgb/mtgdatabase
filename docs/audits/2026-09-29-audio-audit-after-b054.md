# Pełny audyt korpusu sampli — 2026-09-29

Zakres: **530** plików `audio/samples/<id>.mp3`. Skan od zera skryptem
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
| WYSOKIE — za cicho (LUFS/peak) | 0 | wysoka | normalizacja w postprodukcji |
| WYSOKIE — energia w infradźwiękach | 0 | wysoka | EQ+normalizacja albo regeneracja |
| WYSOKIE — brak treści powyżej 250 Hz | 5 | średnia | odsłuch → regeneracja |
| WYSOKIE — treść krótsza niż 0,8 s | 22 | wysoka | trym albo regeneracja |
| ŚREDNIE — przester (clipping) | 0 | średnia | tłumienie + limiter |
| ŚREDNIE — true peak > +1 dBTP | 0 | średnia | limiter w postprodukcji |
| ŚREDNIE — za głośno | 0 | średnia | wyrównanie głośności |
| ŚREDNIE — offset DC | 0 | wysoka | filtr górnoprzepustowy 20 Hz |
| DO ODSŁUCHU — tonalne/„muzyczne" | 8 | niska | weryfikacja uchem |
| DO ODSŁUCHU — podobne do mowy | 3 | niska | weryfikacja uchem |
| DO ODSŁUCHU — start na pełnym poziomie | 11 | niska | weryfikacja uchem / fade-in |
| BLIŹNIAKI — para sampli ≥ 0.95 kosinusa | 23 | niska | odsłuch pary, ewentualnie nowy prompt |
| KOSMETYCZNE — długa cisza wiodąca | 17 | wysoka | opcjonalny trym |
| KOSMETYCZNE — długa cisza końcowa | 50 | wysoka | opcjonalny trym |

Plików z co najmniej jedną flagą: **91** / 530.
Plików z flagą **merytoryczną** (bez kategorii kosmetycznych i „start na pełnym
poziomie"): **28**.


## Najważniejszy wniosek: korpus nie ma wyrównanej głośności

Rozkład głośności percepcyjnej: mediana **-20.0 LUFS**, p10 **-20.5**, p90 **-20.0**, σ **0.6 LU**, rozpiętość **5.9 LU** (od -24.7 do -18.8).

To nie jest kwestia pojedynczych odstających plików — **cały korpus jest nierówny**.
Przy odsłuchu biblioteki po kolei jedne sample są ledwie słyszalne, inne wyrywają
głośniki. Nic dziwnego: każdy plik przyszedł z generatora bez wspólnego odniesienia.

Gdyby wyrównać wszystko do **-20 LUFS** z sufitem **−1 dBTP**:

- plików wymagających wzmocnienia > +10 dB: **0** (z tego > +15 dB: 0 — tam wyjdzie szum tła, lepiej zregenerować),
- plików wymagających wyciszenia > 6 dB: **0**,
- plików w granicach ±3 dB od celu: **526**.

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
| 445 | Locthwain Paladin | -27.13 dBFS | -10.72 dBFS | -16.4 dB | — |

## 3. WYSOKIE — za cicho względem korpusu

Próg: LUFS < -32 albo peak < −18 dBFS. Większość naprawia normalizacja (bez kredytów); przy wzmocnieniu > +15 dB trzeba sprawdzić, czy nie wychodzi szum.

_Brak plików w tej kategorii._

## 4. WYSOKIE — energia zepchnięta w infradźwięki

Ponad 80 % energii poniżej 60 Hz. Miernik peaku pokazuje „głośno", ale na laptopie, telefonie i większości słuchawek taki sample jest praktycznie niesłyszalny — dlatego LUFS (ważony percepcyjnie) bywa tu 20 dB niżej niż peak. Naprawa: EQ (odcięcie 40 Hz) + normalizacja, a jeśli po tym nie zostaje treść — regeneracja.

_Brak plików w tej kategorii._

## 5. WYSOKIE — brak treści powyżej 250 Hz

Mniej niż 2 % energii powyżej 250 Hz — w paśmie, w którym ucho rozpoznaje materiał i detal, nie ma nic. Dla tąpnięcia olbrzyma to bywa poprawne, dla metalu, szkła, ptaków czy magii oznacza zgubioną treść.

| ID | Tytuł | Udział > 250 Hz | Centroid | LUFS | Inne flagi | Scenariusz |
|---|---|---|---|---|---|---|
| 51 | Deepwood Denizen | 0.0008 | 65 Hz | -20.47 | — | głuchy drzewny puls jak stłumione serce  |
| 71 | Security Rhox | 0.0060 | 62 Hz | -20.09 | cut_start_hard | głuche, gumowate uderzenie ciała o niewi |
| 301 | Guildscorn Ward | 0.0061 | 114 Hz | -20.15 | — | podwójne tąpnięcie ciał o napiętą niewid |
| 273 | Fertile Thicket | 0.0138 | 153 Hz | -20.0 | — | oddychająca ziemia pulsująca maną pod dł |
| 181 | Spectral Prison | 0.0188 | 131 Hz | -20.0 | — | niski równy buczący ton pola więziennego |

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
| 129 | Charismatic Vanguard | 0.56 s | 0.33 s | 2.48 s | kuty młot uderzający o stalowy pancerz w geśc |
| 17 | Selhoff Occultist | 0.57 s | 0.49 s | 2.48 s | ostry świst rytualnego sztyletu rozcinający z |
| 442 | Cenn's Tactician | 0.58 s | 0.41 s | 2.48 s | jedno równoczesne tupnięcie szeregu obrońców  |
| 472 | Kazuul's Toll Collector | 0.58 s | 0.32 s | 2.48 s | ogry poborca zawieszający zdobyczny oręż na s |
| 592 | Glorifier of Suffering | 0.58 s | 0.52 s | 2.48 s | rozbity relikwiarz i karmazynowe wstęgi mocy  |
| 608 | Skymarch Bloodletter | 0.63 s | 0.4 s | 2.48 s | uderzenie rapiera o stalowy napierśnik |
| 223 | Angel's Feather | 0.65 s | 0.59 s | 2.48 s | mocne machnięcie wielkim skrzydłem tuż przy u |
| 77 | Annie Flash, the Veteran | 0.66 s | 0.49 s | 2.48 s | wystrzał elektrycznej wiązki z trójlufowej rę |
| 283 | Magic Damper | 0.67 s | 0.35 s | 2.48 s | tłumiąca kopuła heksagonów rozpryskująca poci |
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
| 0.964 | 70 | Capture Sphere | 567 | Jwar Isle Avenger | zamknięcie szarżującej bestii w fraktalnej sf | szpony przebijające chitynowy pancerz w locie |
| 0.964 | 39 | Brute Force | 70 | Capture Sphere | grząski tupnięcie orka z rozbryzgiem błota i  | zamknięcie szarżującej bestii w fraktalnej sf |
| 0.961 | 15 | Tellah, Great Sage | 155 | Demolish | eksplozja ognia i błyskawic wyrywająca się z  | detonacja bramy i zawalenie wiaduktu w morze  |
| 0.960 | 236 | Agate Assault | 486 | Krallenhorde Wantons | kaskada głazów z pękającej krawędzi urwiska w | trzask wrót gospody pod uderzeniem przywódcy  |
| 0.959 | 137 | Withstand | 155 | Demolish | strumień ognia rozpraszający się na krawędzia | detonacja bramy i zawalenie wiaduktu w morze  |
| 0.955 | 15 | Tellah, Great Sage | 601 | Exploding Borders | eksplozja ognia i błyskawic wyrywająca się z  | zderzenie Jundu z Nayą — lawa pochłania prast |
| 0.955 | 39 | Brute Force | 535 | Lab Rats | grząski tupnięcie orka z rozbryzgiem błota i  | skaveńskie laboratoryjne cykle klatek i mecha |
| 0.955 | 306 | Mysteries of the Deep | 470 | Springbloom Druid | długi syk morskiej wody cofającej się po mokr | ofiara z żyznej gleby i wybuch dwóch drzew w  |
| 0.954 | 155 | Demolish | 601 | Exploding Borders | detonacja bramy i zawalenie wiaduktu w morze  | zderzenie Jundu z Nayą — lawa pochłania prast |
| 0.954 | 300 | Gila Courser | 595 | Óin the Brave | galop jaszczura-kuriera po czerwonej skale ka | dźwięczna kaskada złotych monet zsuwających s |
| 0.953 | 128 | Undead Servant | 152 | Timely Interference | wydobycie się nieumarłego z rozkopanego grobu | ryw i cios kavu wyskakującego zza kolumny w b |
| 0.953 | 122 | Blazing Torch | 376 | Doomed Dissenter | trzask smołowej pochodni płonącej w uchwycie  | powstanie napęczniałego nieżywego odszczepień |
| 0.952 | 18 | Lotusguard Disciple | 76 | Negate | iskry i odłamki odbijające się od pulsującej  | rozbicie strumienia zaklęcia o niewidzialną b |
| 0.952 | 459 | Prismari Campus | 585 | Jolrael, Mwonvuli Recluse | zderzenie ognia i wody w taflę lodu i pary na | niemy rozkaz druidki — pantery wyskakują nad  |
| 0.952 | 15 | Tellah, Great Sage | 72 | Dragon Arch | eksplozja ognia i błyskawic wyrywająca się z  | łuskowate cielsko szorujące o kamienny łuk z  |
| 0.952 | 243 | Willbender | 486 | Krallenhorde Wantons | zaklęcie skręcające ze swojego toru nad wodam | trzask wrót gospody pod uderzeniem przywódcy  |
| 0.951 | 76 | Negate | 300 | Gila Courser | rozbicie strumienia zaklęcia o niewidzialną b | galop jaszczura-kuriera po czerwonej skale ka |
| 0.951 | 58 | Mobile Garrison | 507 | Shatter | syk pneumatycznej rampy wozu bojowego i jej c | rozsadzenie żelaznego golema w ognistą mandal |

## 13. Kontrola tekstów scenariuszy

Wszystkie prompty i opisy scenariuszy są unikalne (527/527).

## 14. KOSMETYCZNE — cisza w pliku

- cisza wiodąca > 0.6 s: **17** plików (604, 460, 65, 289, 218, 140, 360, 403, 463, 578, 232, 500, 304, 382, 560, 561, 292)
- cisza końcowa > 1.5 s: **50** plików (46, 175, 472, 129, 591, 251, 608, 514, 610, 466, 283, 197, 355, 520, 442, 17, 593, 616, 576, 592, 142, 14, 556, 567, 482 …)

To nie jest błąd generacji — sample po prostu nie wypełnia całej zadeklarowanej
długości. Trym/skrócenie pliku jest opcjonalne i bezkosztowe.

## 15. Różnice względem audytu po rundzie r005

- flagi merytoryczne w poprzednim skanie: **28**, teraz: **28**
- nowe (nie widział ich poprzedni zestaw metryk): —
- zniknęły: —

Uwaga: poprzedni skan nie mierzył LUFS, pasma, tonalności ani duplikatów,
więc większość „nowych" pozycji to nie regresja plików, tylko nowe kryterium.

## 16. Rekomendowana kolejka decyzji

Kolejność jest celowa: najpierw tania, odwracalna obróbka całego korpusu, dopiero
potem odsłuch i dopiero na końcu wydawanie kredytów.

1. **Postprodukcja lokalna, 0 kredytów** — wyrównanie głośności całego korpusu, limiter −1 dBTP, filtr DC. Bezpośrednio dotyczy 1 plików z flagami głośnościowymi: 445

2. **Do odsłuchu przed decyzją** — 61 ID (tonalne, mowopodobne, bliźniaki, krótka treść): 1, 15, 17, 18, 39, 46, 58, 70, 72, 76, 77, 91, 122, 128, 129, 137, 142, 152, 155, 163, 185, 223, 236, 243, 270, 283, 300, 304, 306, 321, 347, 376, 403, 442, 459, 460, 466, 470, 472, 486, 489, 507, 510, 520, 521, 527, 535, 551, 567, 568, 576, 580, 585, 586, 591, 592, 593, 595, 601, 608, 610

3. **Kandydaci do regeneracji (kredyty, po potwierdzeniu uchem)** — 5 ID bez treści w paśmie słyszalnym: 51, 71, 181, 273, 301

   Uwaga: część z nich to scenariusze **celowo** niskie (kroki olbrzymów, tąpnięcia,
   bicie serca). Jeśli po EQ i normalizacji brzmią poprawnie, regeneracja jest zbędna.

Pełne metryki per plik: JSON obok tego raportu.

