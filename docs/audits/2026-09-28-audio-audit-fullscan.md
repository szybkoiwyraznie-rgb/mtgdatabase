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
| WYSOKIE — ucięty koniec | 0 | wysoka | odsłuch → regeneracja/fade |
| WYSOKIE — za cicho (LUFS/peak) | 30 | wysoka | normalizacja w postprodukcji |
| WYSOKIE — energia w infradźwiękach | 28 | wysoka | EQ+normalizacja albo regeneracja |
| WYSOKIE — brak treści powyżej 250 Hz | 31 | średnia | odsłuch → regeneracja |
| WYSOKIE — treść krótsza niż 0,8 s | 30 | wysoka | trym albo regeneracja |
| ŚREDNIE — przester (clipping) | 0 | średnia | tłumienie + limiter |
| ŚREDNIE — true peak > +1 dBTP | 58 | średnia | limiter w postprodukcji |
| ŚREDNIE — za głośno | 20 | średnia | wyrównanie głośności |
| ŚREDNIE — offset DC | 19 | wysoka | filtr górnoprzepustowy 20 Hz |
| DO ODSŁUCHU — tonalne/„muzyczne" | 6 | niska | weryfikacja uchem |
| DO ODSŁUCHU — podobne do mowy | 3 | niska | weryfikacja uchem |
| DO ODSŁUCHU — start na pełnym poziomie | 37 | niska | weryfikacja uchem / fade-in |
| BLIŹNIAKI — para sampli ≥ 0.95 kosinusa | 30 | niska | odsłuch pary, ewentualnie nowy prompt |
| KOSMETYCZNE — długa cisza wiodąca | 16 | wysoka | opcjonalny trym |
| KOSMETYCZNE — długa cisza końcowa | 38 | wysoka | opcjonalny trym |

Plików z co najmniej jedną flagą: **220** / 527.
Plików z flagą **merytoryczną** (bez kategorii kosmetycznych i „start na pełnym
poziomie"): **129**.


## Najważniejszy wniosek: korpus nie ma wyrównanej głośności

Rozkład głośności percepcyjnej: mediana **-15.5 LUFS**, p10 **-28.3**, p90 **-8.6**, σ **7.8 LU**, rozpiętość **43.9 LU** (od -46.6 do -2.7).

To nie jest kwestia pojedynczych odstających plików — **cały korpus jest nierówny**.
Przy odsłuchu biblioteki po kolei jedne sample są ledwie słyszalne, inne wyrywają
głośniki. Nic dziwnego: każdy plik przyszedł z generatora bez wspólnego odniesienia.

Gdyby wyrównać wszystko do **-20 LUFS** z sufitem **−1 dBTP**:

- plików wymagających wzmocnienia > +10 dB: **41** (z tego > +15 dB: 12 — tam wyjdzie szum tła, lepiej zregenerować),
- plików wymagających wyciszenia > 6 dB: **220**,
- plików w granicach ±3 dB od celu: **115**.

Operacja jest lokalna, odwracalna i **nie kosztuje kredytów**. Rekomendacja: zrobić ją
jednym przebiegiem na całym korpusie, dopiero potem oceniać pojedyncze sample uchem —
bo dziś ocena „ten jest za cichy" myli się z „ten jest zły".

## 1. KRYTYCZNE — plik (prawie) cichy

Materiał w praktyce niesłyszalny — regeneracja, nie postprodukcja.

_Brak plików w tej kategorii._

## 2. WYSOKIE — ucięty koniec (brak wybrzmienia)

Sortowane od najbrutalniejszego cięcia. Fade-out 0,2–0,35 s naprawia to bez kredytów.

_Brak plików w tej kategorii._

## 3. WYSOKIE — za cicho względem korpusu

Próg: LUFS < -32 albo peak < −18 dBFS. Większość naprawia normalizacja (bez kredytów); przy wzmocnieniu > +15 dB trzeba sprawdzić, czy nie wychodzi szum.

| ID | Tytuł | LUFS | Peak dBFS | Aktywny RMS | Inne flagi |
|---|---|---|---|---|---|
| 115 | Merfolk Mesmerist | -46.65 | -13.13 | -34.59 | sub_dominant, muffled |
| 608 | Skymarch Bloodletter | -46.47 | -17.79 | -40.38 | short_content, long_trail_silence |
| 294 | Tumbleweed Rising | -42.29 | -17.59 | -40.91 | — |
| 453 | Elgaud Inquisitor | -42.26 | -17.38 | -38.74 | short_content, long_trail_silence |
| 200 | Cloak of the Bat | -42.06 | -9.95 | -39.74 | — |
| 227 | Jwari Shapeshifter | -36.62 | -7.36 | -36.81 | — |
| 172 | Mournful Zombie | -36.47 | -12.26 | -38.1 | — |
| 270 | Roiling Regrowth | -36.4 | -16.31 | -43.01 | — |
| 85 | Phyrexian Rager | -35.98 | -8.16 | -39.74 | — |
| 559 | Gaelicat | -35.98 | -5.42 | -37.66 | — |
| 206 | High Stride | -35.17 | -15.92 | -35.63 | sub_dominant |
| 303 | Blanchwood Prowler | -35.02 | -10.89 | -35.61 | — |
| 584 | Merfolk Falconer | -34.52 | -11.26 | -33.57 | sub_dominant, long_lead_silence |
| 383 | Supernatural Stamina | -34.41 | -15.36 | -35.3 | muffled, short_content, long_trail_silence |
| 598 | Sheriff of Safe Passage | -33.72 | -8.17 | -37.67 | — |
| 55 | Etherwrought Page | -33.58 | -17.46 | -38.78 | — |
| 343 | Puppeteer Clique | -33.28 | -16.22 | -38.85 | — |
| 352 | Evangel of Synthesis | -33.2 | -14.78 | -38.03 | short_content, long_trail_silence |
| 311 | Guildsworn Prowler | -33.15 | -15.56 | -36.07 | — |
| 285 | Etherium Sculptor | -33.06 | -5.46 | -37.84 | — |
| 509 | Highland Game | -33.05 | -7.03 | -36.6 | — |
| 370 | Consume Spirit | -32.89 | -17.96 | -38.43 | — |
| 139 | Slithering Cryptid | -32.77 | -6.72 | -38.25 | — |
| 471 | Healer of the Glade | -32.68 | -8.08 | -39.27 | — |
| 600 | Rotting Legion | -32.48 | -11.19 | -37.67 | — |
| 313 | Faceless Butcher | -32.47 | -6.48 | -37.55 | — |
| 191 | Esper Stormblade | -32.26 | -12.79 | -39.26 | dc_offset |
| 93 | Dispeller's Capsule | -32.25 | -5.03 | -37.15 | — |
| 605 | Consign to Dream | -32.2 | -13.59 | -36.83 | — |
| 560 | Dead Ringers | -32.01 | -6.57 | -34.05 | long_lead_silence |

## 4. WYSOKIE — energia zepchnięta w infradźwięki

Ponad 80 % energii poniżej 60 Hz. Miernik peaku pokazuje „głośno", ale na laptopie, telefonie i większości słuchawek taki sample jest praktycznie niesłyszalny — dlatego LUFS (ważony percepcyjnie) bywa tu 20 dB niżej niż peak. Naprawa: EQ (odcięcie 40 Hz) + normalizacja, a jeśli po tym nie zostaje treść — regeneracja.

| ID | Tytuł | Udział < 60 Hz | Udział > 250 Hz | LUFS | Peak dBFS | Scenariusz |
|---|---|---|---|---|---|---|
| 223 | Angel's Feather | 1.00 | 0.000 | -28.17 | -1.52 | pojedyncze miękkie muśnięcie dużego pióra w n |
| 115 | Merfolk Mesmerist | 1.00 | 0.001 | -46.65 | -13.13 | hipnotyczne falowanie wody tkané trójoką syre |
| 444 | Colossodon Yearling | 0.99 | 0.002 | -20.51 | -0.33 | nalot smoka z lęgu Atarki na pancernego colos |
| 273 | Fertile Thicket | 0.99 | 0.000 | -20.46 | -0.43 | oddychająca ziemia pulsująca maną pod dłonią  |
| 70 | Capture Sphere | 0.96 | 0.027 | -14.73 | 0.14 | zamknięcie szarżującej bestii w fraktalnej sf |
| 439 | Hecteyes | 0.95 | 0.008 | -26.62 | -5.38 | wielookie spojrzenie koszmaru paraliżujące zw |
| 207 | Feed the Infection | 0.94 | 0.001 | -14.11 | -0.18 | czarne wici oleju przeszywające skórę wyznawc |
| 584 | Merfolk Falconer | 0.94 | 0.026 | -34.52 | -11.26 | sokół wracający na rękawicę sokolniczki nad c |
| 396 | Vow of Wildness | 0.93 | 0.057 | -14.03 | 0.32 | świetlista nić przysięgi między szamanką a ro |
| 206 | High Stride | 0.91 | 0.093 | -35.17 | -15.92 | krok królika na wysokich drewnianych szczudła |
| 143 | Kabira Vindicator | 0.88 | 0.071 | -20.79 | -0.11 | powiew białego proporca Kabiry nad rogatym wi |
| 428 | Curiosity | 0.88 | 0.002 | -22.38 | -4.8 | łomot ciężkich pazurów walących raz za razem  |
| 562 | Shock | 0.87 | 0.103 | -16.84 | -0.56 | błękitna błyskawica z rękawicy w napierśnik n |
| 526 | Canonized in Blood | 0.87 | 0.056 | -15.1 | -2.71 | fioletowa kanonizacja wampira przy ołtarzu bo |
| 112 | Flurry of Wings | 0.86 | 0.138 | -20.39 | 0.58 | nurkowanie formacji ptasich żołnierzy z grzec |
| 240 | Descendant of Storms | 0.86 | 0.133 | -11.7 | 1.18 | rodowe błogosławieństwo nad uniesionym piórem |
| 422 | Benevolent Blessing | 0.85 | 0.106 | -11.52 | 0.18 | kopuła światła gwiazd spopielająca mroczną pa |
| 550 | Frost Lynx | 0.85 | 0.087 | -24.39 | -0.11 | dotknięcie kryształowego rysia zamrażające ni |
| 71 | Security Rhox | 0.84 | 0.002 | -27.35 | -8.96 | głuche, gumowate uderzenie ciała o niewidzial |
| 33 | Fierce Empath | 0.84 | 0.041 | -20.54 | -3.46 | skrzypiąca fala biegnąca przez włókna pradawn |
| 101 | Grave Exchange | 0.84 | 0.154 | -24.84 | -2.63 | dotknięcie kościanych palców o żywe odbicie w |
| 151 | Revealing Wind | 0.84 | 0.162 | -9.43 | 1.89 | szał złotej burzy piaskowej zrywający iluzje  |
| 221 | Mark of the Vampire | 0.83 | 0.007 | -29.04 | -7.34 | dwa szybkie mokre ukłucia kłów i cichy puls p |
| 228 | Strandwalker | 0.83 | 0.003 | -15.51 | -0.44 | krok żywego ekwipunku na szczudlastych segmen |
| 345 | Porcelain Legionnaire | 0.82 | 0.143 | -15.47 | 0.68 | świst porcelanowego ostrza i lekki ceramiczny |
| 155 | Demolish | 0.81 | 0.033 | -13.04 | 0.31 | detonacja bramy i zawalenie wiaduktu w morze  |
| 420 | Cellar Door | 0.81 | 0.154 | -19.54 | -0.82 | skrzypienie okutych drzwi piwnicznych i wyjśc |
| 450 | Thornhide Wolves | 0.81 | 0.001 | -18.22 | -3.35 | wilk o skórze jak kora rozsuwający kolczasty  |

## 5. WYSOKIE — brak treści powyżej 250 Hz

Mniej niż 2 % energii powyżej 250 Hz — w paśmie, w którym ucho rozpoznaje materiał i detal, nie ma nic. Dla tąpnięcia olbrzyma to bywa poprawne, dla metalu, szkła, ptaków czy magii oznacza zgubioną treść.

| ID | Tytuł | Udział > 250 Hz | Centroid | LUFS | Inne flagi | Scenariusz |
|---|---|---|---|---|---|---|
| 223 | Angel's Feather | 0.0000 | 9 Hz | -28.17 | sub_dominant | pojedyncze miękkie muśnięcie dużego piór |
| 383 | Supernatural Stamina | 0.0001 | 51 Hz | -34.41 | too_quiet, short_content, long_trail_silence | dwa głębokie, powolne uderzenia serca z  |
| 273 | Fertile Thicket | 0.0002 | 15 Hz | -20.46 | sub_dominant, dc_offset | oddychająca ziemia pulsująca maną pod dł |
| 153 | Balamb Garden, Airborne | 0.0004 | 81 Hz | -19.25 | — | turkusowe silniki latającej akademii odg |
| 115 | Merfolk Mesmerist | 0.0005 | 8 Hz | -46.65 | too_quiet, sub_dominant | hipnotyczne falowanie wody tkané trójoką |
| 51 | Deepwood Denizen | 0.0007 | 62 Hz | -24.85 | — | głuchy drzewny puls jak stłumione serce  |
| 107 | Somberwald Spider | 0.0009 | 77 Hz | -12.01 | — | tąpnięcia i wibracje grubych nici pajęcz |
| 207 | Feed the Infection | 0.0010 | 20 Hz | -14.11 | sub_dominant | czarne wici oleju przeszywające skórę wy |
| 450 | Thornhide Wolves | 0.0010 | 28 Hz | -18.22 | sub_dominant | wilk o skórze jak kora rozsuwający kolcz |
| 330 | Invasion of the Giants | 0.0011 | 68 Hz | -18.49 | — | zbliżające się, coraz cięższe kroki olbr |
| 428 | Curiosity | 0.0022 | 37 Hz | -22.38 | cut_start_hard, sub_dominant | łomot ciężkich pazurów walących raz za r |
| 444 | Colossodon Yearling | 0.0023 | 14 Hz | -20.51 | sub_dominant | nalot smoka z lęgu Atarki na pancernego  |
| 71 | Security Rhox | 0.0024 | 43 Hz | -27.35 | sub_dominant | głuche, gumowate uderzenie ciała o niewi |
| 567 | Jwar Isle Avenger | 0.0026 | 57 Hz | -20.68 | — | zwrot sfinksy nad hedronami i cios w pan |
| 228 | Strandwalker | 0.0027 | 38 Hz | -15.51 | sub_dominant | krok żywego ekwipunku na szczudlastych s |
| 132 | Pilgrim's Eye | 0.0043 | 40 Hz | -14.72 | — | mechaniczne oko pielgrzyma kreślące kręg |
| 301 | Guildscorn Ward | 0.0050 | 103 Hz | -22.39 | — | podwójne tąpnięcie ciał o napiętą niewid |
| 118 | Dire-Strain Brawler | 0.0051 | 97 Hz | -10.34 | — | niski spokojny pomruk wilkołaka stojąceg |
| 221 | Mark of the Vampire | 0.0071 | 49 Hz | -29.04 | sub_dominant | dwa szybkie mokre ukłucia kłów i cichy p |
| 129 | Charismatic Vanguard | 0.0072 | 56 Hz | -11.19 | — | uniesienie święconego młota krasnoluda z |
| 125 | Ordinary Bear | 0.0074 | 121 Hz | -22.43 | — | rytmiczny pradawny taniec niedźwiedzi w  |
| 492 | Secluded Steppe | 0.0077 | 55 Hz | -29.66 | — | wiatr nad kurhanami Rohanu wśród simbelm |
| 439 | Hecteyes | 0.0083 | 40 Hz | -26.62 | sub_dominant | wielookie spojrzenie koszmaru paraliżują |
| 72 | Dragon Arch | 0.0089 | 62 Hz | -12.47 | — | wyłanianie się smoka z żarzącego portalu |
| 539 | Silvanus's Invoker | 0.0100 | 65 Hz | -12.13 | — | zew ziemi i wyłaniający się żywiołak ska |
| 289 | Rustvine Cultivator | 0.0101 | 57 Hz | -17.05 | — | kropla czarnego oleju karmiąca metaliczn |
| 588 | Cemetery Recruitment | 0.0107 | 75 Hz | -26.33 | — | fioletowy blask Liliany wskrzeszający wo |
| 235 | Trestle Troll | 0.0130 | 121 Hz | -10.2 | dc_offset | przestępowanie olbrzymiego trolla po fil |
| 281 | Moonlit Meditation | 0.0137 | 71 Hz | -13.91 | — | koncentryczne fale w idealnym rytmie od  |
| 181 | Spectral Prison | 0.0142 | 107 Hz | -13.13 | — | niski równy buczący ton pola więziennego |
| 182 | Stomping Slabs | 0.0174 | 157 Hz | -18.28 | — | oglącowe kamienne płyty przelatujące nis |

## 6. ŚREDNIE — przester i true peak

Przester = > 0.05 % próbek na pełnej skali (w tym korpusie: brak). True peak > +1 dBTP to ryzyko zniekształceń po transkodowaniu — naprawialne limiterem, bez kredytów.

| ID | Tytuł | Peak dBFS | True peak dBTP | % próbek na zakresie | Inne flagi |
|---|---|---|---|---|---|
| 585 | Jolrael, Mwonvuli Recluse | 3.02 | 3.47 | 0.047% | — |
| 151 | Revealing Wind | 1.89 | 2.88 | 0.033% | sub_dominant, dc_offset |
| 616 | Act of Treason | 2.52 | 2.75 | 0.043% | — |
| 61 | Stall Out | 2.42 | 2.42 | 0.019% | — |
| 288 | Wedgelight Rammer | 1.88 | 2.21 | 0.006% | — |
| 76 | Negate | 2.04 | 2.16 | 0.046% | — |
| 556 | Ruthless Invasion | 1.89 | 1.98 | 0.029% | — |
| 202 | Inferno Titan | 1.43 | 1.96 | 0.020% | — |
| 497 | Static Net | 1.62 | 1.96 | 0.012% | — |
| 449 | Greater Tanuki | 1.77 | 1.94 | 0.007% | — |
| 12 | Merchant's Dockhand | 1.7 | 1.75 | 0.015% | — |
| 103 | Sweet Oblivion | 1.74 | 1.74 | 0.009% | — |
| 459 | Prismari Campus | 1.26 | 1.74 | 0.009% | cut_start_hard |
| 141 | Sun-Collared Raptor | 1.57 | 1.69 | 0.033% | too_loud |
| 136 | Bone Splinters | 1.24 | 1.64 | 0.011% | — |
| 60 | Thornwood Falls | 1.45 | 1.57 | 0.013% | — |
| 113 | Welder Automaton | 1.37 | 1.54 | 0.027% | cut_start_hard |
| 540 | Chittering Rats | 1.49 | 1.53 | 0.027% | — |
| 16 | Brawler's Plate | 1.33 | 1.51 | 0.006% | — |
| 561 | Time to Feed | 1.51 | 1.51 | 0.006% | — |
| 242 | Knight of the Skyward Eye | 1.34 | 1.49 | 0.004% | — |
| 455 | Irontread Crusher | 1.43 | 1.49 | 0.012% | — |
| 472 | Kazuul's Toll Collector | 1.48 | 1.49 | 0.001% | short_content, long_trail_silence |
| 484 | Guidestone Compass | 1.45 | 1.47 | 0.024% | — |
| 46 | Selesnya Charm | 1.21 | 1.44 | 0.023% | long_trail_silence |
| 267 | Hunter's Blowgun | 1.28 | 1.42 | 0.004% | — |
| 111 | Final Parting | 1.35 | 1.4 | 0.012% | — |
| 54 | Cautious Survivor | 1.39 | 1.39 | 0.021% | too_loud, dc_offset |
| 451 | Downwind Ambusher | 1.1 | 1.37 | 0.020% | — |
| 15 | Tellah, Great Sage | 1.34 | 1.35 | 0.015% | — |
| 58 | Mobile Garrison | 1.34 | 1.34 | 0.040% | cut_start_hard |
| 366 | Assert Perfection | 1.1 | 1.33 | 0.046% | — |
| 88 | Baral and Kari Zev | 1.16 | 1.31 | 0.025% | dc_offset |
| 222 | Maritime Guard | 1.29 | 1.29 | 0.023% | — |
| 20 | Jeskai Devotee | 0.72 | 1.27 | 0.017% | dc_offset |
| 306 | Mysteries of the Deep | 0.95 | 1.27 | 0.008% | — |
| 463 | Knockout Maneuver | 1.17 | 1.27 | 0.012% | long_lead_silence |
| 84 | Garruk's Companion | 1.24 | 1.26 | 0.021% | — |
| 65 | Curate | 0.88 | 1.24 | 0.006% | short_content, long_lead_silence |
| 112 | Flurry of Wings | 0.58 | 1.24 | 0.007% | sub_dominant, dc_offset |
| 498 | Fathom Fleet Cutthroat | 1.22 | 1.23 | 0.006% | — |
| 42 | Murder of Crows | 1.2 | 1.21 | 0.036% | cut_start_hard |
| 232 | Goblin Piker | 1.05 | 1.21 | 0.027% | long_lead_silence |
| 326 | Bone Shredder | 1.21 | 1.21 | 0.006% | — |
| 18 | Lotusguard Disciple | 1.19 | 1.2 | 0.013% | — |
| 312 | Goblin Battle Jester | 1.01 | 1.2 | 0.009% | — |
| 130 | Scavenging Harpy | 1.15 | 1.19 | 0.019% | cut_start_hard |
| 168 | Steel Sabotage | 1.04 | 1.19 | 0.015% | — |
| 447 | Resurrected Cultist | 1.08 | 1.19 | 0.006% | — |
| 236 | Agate Assault | 1.07 | 1.18 | 0.044% | cut_start_hard |
| 240 | Descendant of Storms | 1.18 | 1.18 | 0.004% | sub_dominant, dc_offset |
| 161 | Dragonscale Boon | 1.05 | 1.16 | 0.006% | — |
| 597 | Ichorclaw Myr | 1.09 | 1.16 | 0.006% | — |
| 552 | Ettercap | 1.1 | 1.1 | 0.004% | — |
| 367 | Battle-Rattle Shaman | 0.76 | 1.09 | 0.003% | — |
| 595 | Óin the Brave | 0.49 | 1.07 | 0.006% | — |
| 452 | Omenspeaker | 1.03 | 1.03 | 0.002% | cut_start_hard |
| 27 | Erase | 0.87 | 1.02 | 0.031% | cut_start_hard |

## 7. WYSOKIE — realna treść krótsza niż 0,8 s

Po odjęciu ciszy zostaje bardzo mało dźwięku. Czasem to poprawne (jedno uderzenie), czasem generacja urwała temat.

| ID | Tytuł | Treść | Długość pliku | Cisza przód | Cisza tył | Scenariusz |
|---|---|---|---|---|---|---|
| 304 | Sagittars' Volley | 0.13 s | 2.48 s | 0.64 s | 1.71 s | salwa trzech elfich łuków zwolniona w jednym  |
| 608 | Skymarch Bloodletter | 0.16 s | 2.48 s | 0.0 s | 2.32 s | gwardzista spadający z całunu mroku na poster |
| 460 | Ivy Lane Denizen | 0.2 s | 2.48 s | 1.16 s | 1.12 s | dopasowanie rogowego napierśnika na tors młod |
| 283 | Magic Damper | 0.27 s | 2.48 s | 0.08 s | 2.13 s | tłumiąca kopuła heksagonów rozpryskująca poci |
| 576 | Akroan Sergeant | 0.3 s | 2.48 s | 0.26 s | 1.92 s | sygnał sierżanta mieczem i złota aura na tarc |
| 185 | Alaborn Trooper | 0.31 s | 2.48 s | 0.56 s | 1.61 s | donośne uderzenie włóczni w bruk przy żołnier |
| 251 | Stirring Bard | 0.31 s | 2.48 s | 0.0 s | 2.17 s | dwa ostre klaśnięcia dłoni odbite echem od ka |
| 403 | Dementia Bat | 0.36 s | 2.48 s | 0.79 s | 1.33 s | pęknięcie metalowego pancerza nietoperza i ch |
| 1 | Dunland Crebain | 0.37 s | 2.0 s | 0.0 s | 1.63 s | ostre pojedyncze krakanie kruka pikującego na |
| 453 | Elgaud Inquisitor | 0.4 s | 2.48 s | 0.0 s | 2.08 s | błogosławiona energia wzmacniająca inkwizytor |
| 610 | Gearsmith Prodigy | 0.41 s | 2.48 s | 0.0 s | 2.07 s | mechaniczny lis z mosiężnego filigranu w skok |
| 472 | Kazuul's Toll Collector | 0.45 s | 2.48 s | 0.0 s | 2.03 s | ogry poborca zawieszający zdobyczny oręż na s |
| 442 | Cenn's Tactician | 0.47 s | 2.48 s | 0.07 s | 1.94 s | jedno równoczesne tupnięcie szeregu obrońców  |
| 466 | Basilisk Gate | 0.5 s | 2.48 s | 0.0 s | 1.98 s | złoty rezonans bram miasta nasycający pancerz |
| 592 | Glorifier of Suffering | 0.53 s | 2.48 s | 0.03 s | 1.92 s | rozbity relikwiarz i karmazynowe wstęgi mocy  |
| 17 | Selhoff Occultist | 0.54 s | 2.48 s | 0.0 s | 1.94 s | ostry świst rytualnego sztyletu rozcinający z |
| 383 | Supernatural Stamina | 0.57 s | 2.48 s | 0.0 s | 1.91 s | dwa głębokie, powolne uderzenia serca z blisk |
| 563 | Koilos Roc | 0.57 s | 2.48 s | 0.53 s | 1.38 s | lądowanie roca na pękniętej półce piaskowca |
| 591 | Rust-Shield Rampager | 0.58 s | 2.48 s | 0.0 s | 1.9 s | szop z tarczą z garnka i szopię w hełmie w sz |
| 77 | Annie Flash, the Veteran | 0.6 s | 2.48 s | 0.32 s | 1.56 s | wystrzał elektrycznej wiązki z trójlufowej rę |
| 175 | Caves of Chaos Adventurer | 0.61 s | 2.48 s | 0.0 s | 1.87 s | pęknięcie ametystowej ściany z wypadającym zw |
| 352 | Evangel of Synthesis | 0.62 s | 2.48 s | 0.23 s | 1.63 s | krople oleju pieczętujące pakt syntezy z akol |
| 14 | Crew Captain | 0.63 s | 2.48 s | 0.0 s | 1.85 s | pojedyncze ciężkie uderzenie klucza-młota w s |
| 140 | Boros Challenger | 0.65 s | 2.48 s | 0.85 s | 0.98 s | przewrotka po ubitym placu z lekkim chrzęstem |
| 65 | Curate | 0.66 s | 2.48 s | 1.16 s | 0.66 s | gwałtowne otwarcie lewitującego tomu z błękit |
| 197 | Dismal Backwater | 0.71 s | 3.0 s | 0.28 s | 2.01 s | pojedyncza kropla zaburzająca lustrzaną toń p |
| 23 | Brightwood Tracker | 0.72 s | 2.48 s | 0.0 s | 1.76 s | krystaliczne dzwonkowe rozbłyski znaczące szm |
| 593 | Inspiring Captain | 0.78 s | 2.48 s | 0.07 s | 1.63 s | tupnięcie i donośne rżenie rumaka bojowego pr |
| 6 | Azorius Justiciar | 0.79 s | 2.0 s | 0.0 s | 1.21 s | kliknięcie runicznych kajdan zamykających się |
| 337 | Glaring Aegis | 0.79 s | 2.48 s | 0.0 s | 1.69 s | dźwięczne odbicie ciosu od brązowej tarczy z  |

## 8. ŚREDNIE — offset DC

Stała składowa w sygnale. Filtr górnoprzepustowy 20 Hz usuwa ją bezstratnie dla treści słyszalnej.

| ID | Tytuł | Offset DC | Peak dBFS | Uwaga |
|---|---|---|---|---|
| 151 | Revealing Wind | -0.110 | 1.89 | zabiera headroom, może trzaskać na starcie/końcu |
| 24 | Lunar Rejection | +0.071 | 0.15 | zabiera headroom, może trzaskać na starcie/końcu |
| 112 | Flurry of Wings | +0.055 | 0.58 | zabiera headroom, może trzaskać na starcie/końcu |
| 54 | Cautious Survivor | -0.033 | 1.39 | zabiera headroom, może trzaskać na starcie/końcu |
| 258 | Hill Giant | -0.031 | -1.15 | zabiera headroom, może trzaskać na starcie/końcu |
| 160 | Fiery Hellhound | -0.026 | 0.22 | zabiera headroom, może trzaskać na starcie/końcu |
| 235 | Trestle Troll | +0.023 | -0.21 | zabiera headroom, może trzaskać na starcie/końcu |
| 157 | Infectious Bloodlust | -0.022 | 0.38 | zabiera headroom, może trzaskać na starcie/końcu |
| 548 | Steelclaw Lance | -0.020 | 0.34 | zabiera headroom, może trzaskać na starcie/końcu |
| 529 | Turn the Tide | -0.018 | 0.2 | zabiera headroom, może trzaskać na starcie/końcu |
| 273 | Fertile Thicket | +0.016 | -0.43 | zabiera headroom, może trzaskać na starcie/końcu |
| 346 | Necrosquito | -0.015 | -4.16 | zabiera headroom, może trzaskać na starcie/końcu |
| 494 | Crested Herdcaller | -0.014 | -0.15 | zabiera headroom, może trzaskać na starcie/końcu |
| 20 | Jeskai Devotee | -0.013 | 0.72 | zabiera headroom, może trzaskać na starcie/końcu |
| 119 | Spin Out | -0.012 | 0.3 | zabiera headroom, może trzaskać na starcie/końcu |
| 88 | Baral and Kari Zev | -0.012 | 1.16 | zabiera headroom, może trzaskać na starcie/końcu |
| 240 | Descendant of Storms | -0.012 | 1.18 | zabiera headroom, może trzaskać na starcie/końcu |
| 577 | Thunderstaff | -0.012 | -1.79 | zabiera headroom, może trzaskać na starcie/końcu |
| 191 | Esper Stormblade | -0.010 | -12.79 | zabiera headroom, może trzaskać na starcie/końcu |

## 9. ŚREDNIE — za głośno względem korpusu

Próg: LUFS > -6.5. Sample wyrywa się z biblioteki przy odsłuchu seryjnym.

| ID | Tytuł | LUFS | Peak dBFS | Aktywny RMS |
|---|---|---|---|---|
| 385 | Midnight Guard | -2.72 | -0.07 | -8.31 |
| 8 | Goblin Deathraiders | -4.25 | 0.2 | -11.23 |
| 91 | Curse of the Pierced Heart | -4.54 | 0.21 | -10.05 |
| 11 | Sleep of the Dead | -4.59 | 0.09 | -20.05 |
| 24 | Lunar Rejection | -4.77 | 0.15 | -17.97 |
| 435 | Warrior's Sword | -4.91 | 0.72 | -19.31 |
| 292 | Rediscover the Way | -5.13 | -1.2 | -20.5 |
| 160 | Fiery Hellhound | -5.21 | 0.22 | -13.55 |
| 615 | Tah-Crop Skirmisher | -5.3 | 0.58 | -12.01 |
| 66 | Hooting Mandrills | -5.32 | 0.41 | -22.04 |
| 572 | Skinbrand Goblin | -5.55 | 0.15 | -15.21 |
| 593 | Inspiring Captain | -5.63 | 0.61 | -23.69 |
| 37 | Howl of the Night Pack | -5.67 | -0.35 | -12.09 |
| 578 | Savage Surge | -5.73 | -0.64 | -18.05 |
| 308 | Greatsword of Tyr | -5.77 | 0.48 | -16.5 |
| 461 | Negate | -5.94 | 0.33 | -20.88 |
| 252 | Captain's Call | -6.06 | 0.75 | -19.4 |
| 54 | Cautious Survivor | -6.12 | 1.39 | -14.04 |
| 141 | Sun-Collared Raptor | -6.42 | 1.57 | -17.66 |
| 468 | Cacophodon | -6.49 | -0.17 | -13.77 |

## 10. DO ODSŁUCHU — tonalne / potencjalnie muzyczne

Stabilna wysokość dźwięku przez większość pliku. Dla dzwonu/gongu/rezonansu to poprawne; flaga ma sens tylko jeśli scenariusz nie zakładał źródła tonalnego.

| ID | Tytuł | Ramki tonalne | f0 | σ f0 (półtony) | Flatness | Scenariusz |
|---|---|---|---|---|---|---|
| 91 | Curse of the Pierced Heart | 1.00 | 727 Hz | 0.0 | 0.0001 | wbicie ciernia w serce rytualnej figurki z szarpnięciem kląt |
| 146 | Palace Familiar | 1.00 | 615 Hz | 0.49 | 0.0002 | skrzek pałacowego ptaka z wirującą mechaniczną soczewką oka |
| 163 | Ghoulcaller's Bell | 1.00 | 727 Hz | 0.0 | 0.0002 | dźwięk patynowanego dzwonu nekromanty z sączącą się mgłą |
| 507 | Shatter | 1.00 | 1000 Hz | 0.0 | 0.0002 | rozsadzenie żelaznego golema w ognistą mandalę |
| 586 | Fourth Bridge Prowler | 1.00 | 1000 Hz | 0.0 | 0.0001 | miniaturowy ładunek eteru osłabiający strażnika z cienia |
| 347 | Pristine Talisman | 0.99 | 888 Hz | 0.0 | 0.0011 | pojedyncze czyste uderzenie małego wypolerowanego dzwonka z  |

## 11. DO ODSŁUCHU — podobne do mowy

Heurystyka mowy — niska pewność. Sprawdzić, czy nie ma zrozumiałych słów (prompty zabraniają mowy).

| ID | Tytuł | Modulacja 2–8 Hz | Udział dźwięcznych | Centroid | Scenariusz |
|---|---|---|---|---|---|
| 489 | Seer's Lantern | 0.85 | 1.00 | 648 Hz | zgrzyt przesłony latarni i narastający krystaliczny ton szkł |
| 163 | Ghoulcaller's Bell | 0.58 | 1.00 | 2396 Hz | dźwięk patynowanego dzwonu nekromanty z sączącą się mgłą |
| 580 | Loporrit Scout | 0.56 | 0.79 | 1475 Hz | pogodne, gulgoczące ćwierknięcie chocobo tuż przy uchu |

## 12. BLIŹNIAKI — sample brzmiące niemal identycznie

Kosinus odcisków log-mel ≥ 0.95. Identyczny PCM (md5): **0** grup.

| Kosinus | ID A | Tytuł A | ID B | Tytuł B | Scenariusz A | Scenariusz B |
|---|---|---|---|---|---|---|
| 0.978 | 321 | Ainok Artillerist | 507 | Shatter | wystrzał balisty z drewna świętych gajów | rozsadzenie żelaznego golema w ognistą mandal |
| 0.971 | 470 | Springbloom Druid | 527 | Shiva, Warden of Ice | ofiara z żyznej gleby i wybuch dwóch drzew w  | transformacja w Shivę zamrażająca całe pole b |
| 0.967 | 71 | Security Rhox | 428 | Curiosity | głuche, gumowate uderzenie ciała o niewidzial | łomot ciężkich pazurów walących raz za razem  |
| 0.967 | 142 | Savage Hunger | 535 | Lab Rats | taranowanie zamarzniętej palisady przez głodn | skaveńskie laboratoryjne cykle klatek i mecha |
| 0.967 | 510 | Angel of the Dawn | 568 | Nanoform Sentinel | anielska zjawa o brzasku złotym pyłem nad mur | rój nano-cząsteczek zasklepiający pęknięte pr |
| 0.964 | 39 | Brute Force | 142 | Savage Hunger | grząski tupnięcie orka z rozbryzgiem błota i  | taranowanie zamarzniętej palisady przez głodn |
| 0.962 | 137 | Withstand | 155 | Demolish | strumień ognia rozpraszający się na krawędzia | detonacja bramy i zawalenie wiaduktu w morze  |
| 0.962 | 39 | Brute Force | 70 | Capture Sphere | grząski tupnięcie orka z rozbryzgiem błota i  | zamknięcie szarżującej bestii w fraktalnej sf |
| 0.961 | 153 | Balamb Garden, Airborne | 330 | Invasion of the Giants | turkusowe silniki latającej akademii odginają | zbliżające się, coraz cięższe kroki olbrzymów |
| 0.960 | 15 | Tellah, Great Sage | 155 | Demolish | eksplozja ognia i błyskawic wyrywająca się z  | detonacja bramy i zawalenie wiaduktu w morze  |
| 0.960 | 128 | Undead Servant | 152 | Timely Interference | wydobycie się nieumarłego z rozkopanego grobu | ryw i cios kavu wyskakującego zza kolumny w b |
| 0.958 | 300 | Gila Courser | 595 | Óin the Brave | galop jaszczura-kuriera po czerwonej skale ka | dźwięczna kaskada złotych monet zsuwających s |
| 0.958 | 76 | Negate | 300 | Gila Courser | rozbicie strumienia zaklęcia o niewidzialną b | galop jaszczura-kuriera po czerwonej skale ka |
| 0.957 | 306 | Mysteries of the Deep | 470 | Springbloom Druid | długi syk morskiej wody cofającej się po mokr | ofiara z żyznej gleby i wybuch dwóch drzew w  |
| 0.957 | 122 | Blazing Torch | 376 | Doomed Dissenter | trzask smołowej pochodni płonącej w uchwycie  | powstanie napęczniałego nieżywego odszczepień |
| 0.957 | 40 | Expunge | 436 | Fireball | czarna mgła zamalowująca zbroję rycerza od do | trzy ogniste kule rozszczepione w drewniane c |
| 0.956 | 300 | Gila Courser | 459 | Prismari Campus | galop jaszczura-kuriera po czerwonej skale ka | zderzenie ognia i wody w taflę lodu i pary na |
| 0.956 | 236 | Agate Assault | 486 | Krallenhorde Wantons | kaskada głazów z pękającej krawędzi urwiska w | trzask wrót gospody pod uderzeniem przywódcy  |
| 0.956 | 39 | Brute Force | 535 | Lab Rats | grząski tupnięcie orka z rozbryzgiem błota i  | skaveńskie laboratoryjne cykle klatek i mecha |
| 0.956 | 18 | Lotusguard Disciple | 76 | Negate | iskry i odłamki odbijające się od pulsującej  | rozbicie strumienia zaklęcia o niewidzialną b |
| 0.954 | 15 | Tellah, Great Sage | 458 | Trained Arynx | eksplozja ognia i błyskawic wyrywająca się z  | skok wytresowanego arynxa nad kanionem Thunde |
| 0.954 | 459 | Prismari Campus | 585 | Jolrael, Mwonvuli Recluse | zderzenie ognia i wody w taflę lodu i pary na | niemy rozkaz druidki — pantery wyskakują nad  |
| 0.954 | 26 | Ember Beast | 321 | Ainok Artillerist | ciężki krok żarnej bestii z trzaskiem rozżarz | wystrzał balisty z drewna świętych gajów |
| 0.953 | 142 | Savage Hunger | 256 | Frightful Delusion | taranowanie zamarzniętej palisady przez głodn | koszmarne wizje sączące się do umysłu śpiącej |
| 0.953 | 58 | Mobile Garrison | 507 | Shatter | syk pneumatycznej rampy wozu bojowego i jej c | rozsadzenie żelaznego golema w ognistą mandal |
| 0.953 | 243 | Willbender | 486 | Krallenhorde Wantons | zaklęcie skręcające ze swojego toru nad wodam | trzask wrót gospody pod uderzeniem przywódcy  |
| 0.952 | 479 | Impact Tremors | 542 | Panic Spellbomb | sejsmiczny wstrząs szarży uderzający w żołnie | karmazynowa eksplozja spellbomba wywołująca p |
| 0.952 | 155 | Demolish | 458 | Trained Arynx | detonacja bramy i zawalenie wiaduktu w morze  | skok wytresowanego arynxa nad kanionem Thunde |
| 0.951 | 155 | Demolish | 542 | Panic Spellbomb | detonacja bramy i zawalenie wiaduktu w morze  | karmazynowa eksplozja spellbomba wywołująca p |
| 0.950 | 15 | Tellah, Great Sage | 601 | Exploding Borders | eksplozja ognia i błyskawic wyrywająca się z  | zderzenie Jundu z Nayą — lawa pochłania prast |

## 13. Kontrola tekstów scenariuszy

Wszystkie prompty i opisy scenariuszy są unikalne (527/527).

## 14. KOSMETYCZNE — cisza w pliku

- cisza wiodąca > 0.6 s: **16** plików (65, 460, 218, 140, 360, 403, 379, 232, 393, 500, 463, 560, 304, 382, 584, 578)
- cisza końcowa > 1.5 s: **38** plików (608, 251, 283, 453, 610, 472, 197, 466, 17, 442, 576, 592, 383, 591, 175, 14, 23, 304, 337, 142, 70, 482, 355, 543, 1 …)

To nie jest błąd generacji — sample po prostu nie wypełnia całej zadeklarowanej
długości. Trym/skrócenie pliku jest opcjonalne i bezkosztowe.

## 15. Różnice względem audytu po rundzie r005

- flagi merytoryczne w poprzednim skanie: **2**, teraz: **129**
- nowe (nie widział ich poprzedni zestaw metryk): 1, 6, 8, 11, 14, 17, 20, 23, 24, 33, 37, 51, 54, 55, 65, 66, 70, 71, 72, 77, 85, 88, 93, 101, 107, 112, 115, 118, 119, 125, 129, 132, 139, 140, 141, 143, 151, 153, 155, 157, 160, 172, 175, 181, 182, 185, 191, 197, 200, 206, 207, 221, 223, 227, 228, 235, 240, 251, 252, 258, 270, 273, 281, 283, 285, 289, 292, 294, 301, 303, 304, 308, 311, 313, 330, 337, 343, 345, 346, 352, 370, 383, 396, 403, 420, 422, 428, 435, 439, 442, 444, 450, 453, 460, 461, 466, 468, 471, 472, 492, 494, 509, 526, 529, 539, 548, 550, 559, 560, 562, 563, 567, 572, 576, 577, 578, 584, 588, 591, 592, 593, 598, 600, 605, 608, 610, 615
- zniknęły: —

Uwaga: poprzedni skan nie mierzył LUFS, pasma, tonalności ani duplikatów,
więc większość „nowych" pozycji to nie regresja plików, tylko nowe kryterium.

## 16. Rekomendowana kolejka decyzji

Kolejność jest celowa: najpierw tania, odwracalna obróbka całego korpusu, dopiero
potem odsłuch i dopiero na końcu wydawanie kredytów.

1. **Postprodukcja lokalna, 0 kredytów** — wyrównanie głośności całego korpusu, limiter −1 dBTP, filtr DC. Bezpośrednio dotyczy 137 plików z flagami głośnościowymi: 8, 11, 12, 15, 16, 18, 20, 24, 27, 33, 37, 42, 46, 54, 55, 58, 60, 61, 65, 66, 70, 71, 76, 84, 85, 88, 91, 93, 101, 103, 111, 112, 113, 115, 119, 130, 136, 139, 141, 143, 151, 155, 157, 160, 161, 168, 172, 191, 200, 202, 206, 207, 221, 222, 223, 227, 228, 232, 235, 236, 240, 242, 252, 258, 267, 270, 273, 285, 288, 292, 294, 303, 306, 308, 311, 312, 313, 326, 343, 345, 346, 352, 366, 367, 370, 383, 385, 396, 420, 422, 428, 435, 439, 444, 447, 449, 450, 451, 452, 453, 455, 459, 461, 463, 468, 471, 472, 484, 494, 497, 498, 509, 526, 529, 540, 548, 550, 552, 556, 559, 560, 561, 562, 572, 577, 578, 584, 585, 593, 595, 597, 598, 600, 605, 608, 615, 616

2. **Do odsłuchu przed decyzją** — 77 ID (tonalne, mowopodobne, bliźniaki, krótka treść): 1, 6, 14, 15, 17, 18, 23, 26, 39, 40, 58, 65, 70, 71, 76, 77, 91, 122, 128, 137, 140, 142, 146, 152, 153, 155, 163, 175, 185, 197, 236, 243, 251, 256, 283, 300, 304, 306, 321, 330, 337, 347, 352, 376, 383, 403, 428, 436, 442, 453, 458, 459, 460, 466, 470, 472, 479, 486, 489, 507, 510, 527, 535, 542, 563, 568, 576, 580, 585, 586, 591, 592, 593, 595, 601, 608, 610

3. **Kandydaci do regeneracji (kredyty, po potwierdzeniu uchem)** — 31 ID bez treści w paśmie słyszalnym: 51, 71, 72, 107, 115, 118, 125, 129, 132, 153, 181, 182, 207, 221, 223, 228, 235, 273, 281, 289, 301, 330, 383, 428, 439, 444, 450, 492, 539, 567, 588

   Uwaga: część z nich to scenariusze **celowo** niskie (kroki olbrzymów, tąpnięcia,
   bicie serca). Jeśli po EQ i normalizacji brzmią poprawnie, regeneracja jest zbędna.

Pełne metryki per plik: JSON obok tego raportu.

