# Pełny audyt korpusu sampli — 2026-10-08

Zakres: **561** plików `audio/samples/<id>.mp3`. Skan od zera skryptem
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
| WYSOKIE — brak treści powyżej 250 Hz | 2 | średnia | odsłuch → regeneracja |
| WYSOKIE — treść krótsza niż 0,8 s | 0 | wysoka | trym albo regeneracja |
| WYSOKIE — zapadanie w mono (mono collapse) | 1 | wysoka | korekta mid/side |
| ŚREDNIE — przester (clipping) | 0 | średnia | tłumienie + limiter |
| ŚREDNIE — true peak > +1 dBTP | 0 | średnia | limiter w postprodukcji |
| ŚREDNIE — za głośno | 0 | średnia | wyrównanie głośności |
| ŚREDNIE — offset DC | 0 | wysoka | filtr górnoprzepustowy 20 Hz |
| ŚREDNIE — dominacja dudnienia (boomy) | 8 | niska | filtr dolnozaporowy / shelf |
| ŚREDNIE — brak góry (dull) | 11 | niska | korekta high-shelf |
| ŚREDNIE — ostra góra (harsh) | 9 | niska | łagodne cięcie 4-6 kHz |
| DO ODSŁUCHU — tonalne/„muzyczne" | 6 | niska | weryfikacja uchem |
| DO ODSŁUCHU — podobne do mowy | 6 | niska | weryfikacja uchem |
| DO ODSŁUCHU — start na pełnym poziomie | 3 | niska | weryfikacja uchem / fade-in |
| BLIŹNIAKI — para sampli ≥ 0.95 kosinusa | 22 | niska | odsłuch pary, ewentualnie nowy prompt |
| KOSMETYCZNE — długa cisza wiodąca | 3 | wysoka | opcjonalny trym |
| KOSMETYCZNE — długa cisza końcowa | 3 | wysoka | opcjonalny trym |

Plików z co najmniej jedną flagą: **46** / 561.
Plików z flagą **merytoryczną** (bez kategorii kosmetycznych i „start na pełnym
poziomie"): **4**.


## Najważniejszy wniosek: korpus nie ma wyrównanej głośności

Rozkład głośności percepcyjnej: mediana **-20.0 LUFS**, p10 **-20.2**, p90 **-19.9**, σ **0.5 LU**, rozpiętość **6.3 LU** (od -25.4 do -19.0).

To nie jest kwestia pojedynczych odstających plików — **cały korpus jest nierówny**.
Przy odsłuchu biblioteki po kolei jedne sample są ledwie słyszalne, inne wyrywają
głośniki. Nic dziwnego: każdy plik przyszedł z generatora bez wspólnego odniesienia.

Gdyby wyrównać wszystko do **-20 LUFS** z sufitem **−1 dBTP**:

- plików wymagających wzmocnienia > +10 dB: **0** (z tego > +15 dB: 0 — tam wyjdzie szum tła, lepiej zregenerować),
- plików wymagających wyciszenia > 6 dB: **0**,
- plików w granicach ±3 dB od celu: **557**.

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
| 72 | Dragon Arch | -20.26 dBFS | -8.11 dBFS | -12.2 dB | — |

## 3. WYSOKIE — za cicho względem korpusu

Próg: LUFS < -32 albo peak < −18 dBFS. Większość naprawia normalizacja (bez kredytów); przy wzmocnieniu > +15 dB trzeba sprawdzić, czy nie wychodzi szum.

| ID | Tytuł | LUFS | Peak dBFS | Aktywny RMS | Inne flagi |
|---|---|---|---|---|---|
| 611 | Lifecrafter's Gift | -20.0 | -18.63 | -26.87 | — |

## 4. WYSOKIE — energia zepchnięta w infradźwięki

Ponad 80 % energii poniżej 60 Hz. Miernik peaku pokazuje „głośno", ale na laptopie, telefonie i większości słuchawek taki sample jest praktycznie niesłyszalny — dlatego LUFS (ważony percepcyjnie) bywa tu 20 dB niżej niż peak. Naprawa: EQ (odcięcie 40 Hz) + normalizacja, a jeśli po tym nie zostaje treść — regeneracja.

_Brak plików w tej kategorii._

## 5. WYSOKIE — brak treści powyżej 250 Hz

Mniej niż 2 % energii powyżej 250 Hz — w paśmie, w którym ucho rozpoznaje materiał i detal, nie ma nic. Dla tąpnięcia olbrzyma to bywa poprawne, dla metalu, szkła, ptaków czy magii oznacza zgubioną treść.

| ID | Tytuł | Udział > 250 Hz | Centroid | LUFS | Inne flagi | Scenariusz |
|---|---|---|---|---|---|---|
| 49 | Unstable Frontier | 0.0087 | 110 Hz | -20.0 | boomy | ziemia pęka między światami: głębokie ro |
| 339 | Patron of the Arts | 0.0134 | 105 Hz | -20.03 | boomy, dull | krok smoczej arystokratki po galerii z c |

## 6. ŚREDNIE — przester i true peak

Przester = > 0.05 % próbek na pełnej skali (w tym korpusie: brak). True peak > +1 dBTP to ryzyko zniekształceń po transkodowaniu — naprawialne limiterem, bez kredytów.

_Brak plików w tej kategorii._

## 7. WYSOKIE — realna treść krótsza niż 0,8 s

Po odjęciu ciszy zostaje bardzo mało dźwięku. Czasem to poprawne (jedno uderzenie), czasem generacja urwała temat. Flaga liczona **progiem względnym** (40 dB poniżej maksimum pliku), bo próg absolutny przesuwa się razem z poziomem nagrania — kolumna obok pokazuje, ile wychodzi po staremu.

_Brak plików w tej kategorii._

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
| 71 | Security Rhox | 1.00 | 222 Hz | 0.18 | 0.0 | głuche, gumowate uderzenie ciała o niewidzialną barierę z kr |
| 146 | Palace Familiar | 1.00 | 615 Hz | 0.4 | 0.0005 | skrzek pałacowego ptaka z wirującą mechaniczną soczewką oka |
| 163 | Ghoulcaller's Bell | 1.00 | 727 Hz | 0.0 | 0.0002 | dźwięk patynowanego dzwonu nekromanty z sączącą się mgłą |
| 204 | Skilled Animator | 1.00 | 444 Hz | 0.0 | 0.0 | serwo robota: jeden ciągły czysty ton o stałej wysokości, do |
| 231 | Anthem of Champions | 1.00 | 258 Hz | 0.25 | 0.0001 | cztery bezsłowne głosy nucą jeden trzymany dźwięk hymnu, otw |
| 301 | Guildscorn Ward | 0.99 | 1000 Hz | 0.0 | 0.0003 | podwójne tąpnięcie ciał o napiętą membranę bariery, jedno po |

## 11. DO ODSŁUCHU — podobne do mowy

Heurystyka mowy — niska pewność. Sprawdzić, czy nie ma zrozumiałych słów (prompty zabraniają mowy).

| ID | Tytuł | Modulacja 2–8 Hz | Udział dźwięcznych | Centroid | Scenariusz |
|---|---|---|---|---|---|
| 489 | Seer's Lantern | 0.85 | 1.00 | 636 Hz | zgrzyt przesłony latarni i narastający krystaliczny ton szkł |
| 187 | Idyllic Grange | 0.64 | 0.85 | 1962 Hz | ptaki w lesie: kilka wyraźnych gwizdanych zawołań i treli, j |
| 578 | Savage Surge | 0.60 | 0.40 | 2546 Hz | nagły zwrot centagora z ciężkim kiścieniem |
| 124 | Courage in Crisis | 0.58 | 0.92 | 2105 Hz | ptaki w lesie: kilka wyraźnych gwizdanych zawołań i treli, j |
| 163 | Ghoulcaller's Bell | 0.58 | 1.00 | 1968 Hz | dźwięk patynowanego dzwonu nekromanty z sączącą się mgłą |
| 521 | Leafcrown Dryad | 0.57 | 0.79 | 2568 Hz | ptaki o świcie: szybkie ćwierknięcia i krótkie trele, kilka  |

## 12. BLIŹNIAKI — sample brzmiące niemal identycznie

Kosinus odcisków log-mel ≥ 0.95. Identyczny PCM (md5): **0** grup.

| Kosinus | ID A | Tytuł A | ID B | Tytuł B | Scenariusz A | Scenariusz B |
|---|---|---|---|---|---|---|
| 0.942 | 26 | Ember Beast | 539 | Silvanus's Invoker | ciężki krok żarnej bestii: głęboki niski zgrz | kamienny żywiołak wstaje: ciężkie głazy mielą |
| 0.935 | 103 | Sweet Oblivion | 261 | Universal Solvent | wiatr w gałęziach: szeroki pęd szumiącego tur | jedna kropla rozpuszczalnika na masywny zamek |
| 0.928 | 98 | Fleeting Distraction | 266 | Druid of the Cowl | wir świetlistych motyli wstrzymujący skok wam | magia zielonego eteru z kostura budzi uśpione |
| 0.927 | 496 | Shiv's Embrace | 562 | Shock | wulkan wybucha blisko: szeroki huczący wybuch | grzmot nad głową: jeden bardzo ostry nagły tr |
| 0.925 | 241 | News Helicopter | 562 | Shock | silnik machiny oblężniczej: bardzo niski puls | grzmot nad głową: jeden bardzo ostry nagły tr |
| 0.924 | 118 | Dire-Strain Brawler | 496 | Shiv's Embrace | bliski ryk potwora: gardłowy wrzask wyraźnie  | wulkan wybucha blisko: szeroki huczący wybuch |
| 0.923 | 325 | Narset's Rebuke | 493 | Skyclave Geopede | fala magii: potężny niski huk z trzaskiem pęk | kamienny mur pęka: jedno głębokie pęknięcie,  |
| 0.923 | 26 | Ember Beast | 260 | Etched Host Doombringer | ciężki krok żarnej bestii: głęboki niski zgrz | ryk drapieżnika z jaskini: potężny zew z dług |
| 0.923 | 37 | Howl of the Night Pack | 358 | Frontline War-Rager | ryk potwora z bliska: gardłowy ryk z gęstym n | ryk potwora z bliska: gardłowy ryk z gęstym n |
| 0.912 | 118 | Dire-Strain Brawler | 358 | Frontline War-Rager | bliski ryk potwora: gardłowy wrzask wyraźnie  | ryk potwora z bliska: gardłowy ryk z gęstym n |
| 0.911 | 260 | Etched Host Doombringer | 562 | Shock | ryk drapieżnika z jaskini: potężny zew z dług | grzmot nad głową: jeden bardzo ostry nagły tr |
| 0.911 | 343 | Puppeteer Clique | 347 | Pristine Talisman | dzwon z brązu uderzony raz: głęboki ton z cie | żelazny dzwon klasztorny: uderzony ton ze śro |
| 0.908 | 6 | Azorius Justiciar | 261 | Universal Solvent | bariera prawodawcy: szklisty klaster dzwonków | jedna kropla rozpuszczalnika na masywny zamek |
| 0.908 | 347 | Pristine Talisman | 558 | White Mage's Staff | żelazny dzwon klasztorny: uderzony ton ze śro | brązowy dzwon uderzony raz: niski ciężki dzwo |
| 0.908 | 298 | Raise the Alarm | 343 | Puppeteer Clique | żelazny dzwon alarmowy: jeden czysty ton dzwo | dzwon z brązu uderzony raz: głęboki ton z cie |
| 0.908 | 396 | Vow of Wildness | 468 | Cacophodon | ryk dzikiej bestii: jeden długi gardłowy harm | ryk bestii: jeden długi gardłowy harmoniczny  |
| 0.908 | 23 | Brightwood Tracker | 317 | Village Bell-Ringer | żelazny dzwon klasztorny: uderzony ton ze śro | kościelny dzwon na alarm: cztery ciężkie uder |
| 0.904 | 558 | White Mage's Staff | 562 | Shock | brązowy dzwon uderzony raz: niski ciężki dzwo | grzmot nad głową: jeden bardzo ostry nagły tr |
| 0.903 | 23 | Brightwood Tracker | 347 | Pristine Talisman | żelazny dzwon klasztorny: uderzony ton ze śro | żelazny dzwon klasztorny: uderzony ton ze śro |
| 0.901 | 5 | Academy Journeymage | 164 | Gryffwing Cavalry | zaklęcie zapala się: jasne krystaliczne migot | wielka skrzydlata istota startuje: kilka sprę |
| 0.901 | 298 | Raise the Alarm | 347 | Pristine Talisman | żelazny dzwon alarmowy: jeden czysty ton dzwo | żelazny dzwon klasztorny: uderzony ton ze śro |
| 0.900 | 23 | Brightwood Tracker | 562 | Shock | żelazny dzwon klasztorny: uderzony ton ze śro | grzmot nad głową: jeden bardzo ostry nagły tr |

## 13. Kontrola tekstów scenariuszy

Identyczne opisy `sample_scenario`:

| ID | Scenariusz |
|---|---|
| 1, 42, 124, 187 | ptaki w lesie: kilka wyraźnych gwizdanych zawołań i treli, jedno po drugim |
| 23, 347 | żelazny dzwon klasztorny: uderzony ton ze środka pasma, równy i długi |
| 37, 358 | ryk potwora z bliska: gardłowy ryk z gęstym niskim dudnieniem |
| 58, 444, 534 | pancerz: ciężkie stalowe płyty dzwonią i szorują o siebie |
| 74, 335 | marsz olbrzyma: cztery ciężkie stąpnięcia z dudniącym dołem, równym rytmem |
| 92, 120, 128, 172 | jęk nieumarłego: powolny niski gardłowy pomruk z mokrym rzężeniem |
| 166, 574 | chmara much nad padliną: głęboki bzyk z ciepłym harmonicznym środkiem, bez przerwy |
| 177, 214 | ryk rogatego bydlęcia: dwa krótkie głębokie porykiwania z chrypką |
| 202, 495 | lawa wpada do morza: gwałtowny wybuch pary z hukiem i trzaskiem |
| 223, 571 | stado ptaków zrywa się: szybka seria drobnych uderzeń skrzydeł |
| 277, 532, 616 | miecz zbity w pół ciosu: natychmiastowe twarde uderzenie stali z chmurą metalicznego szumu |
| 352, 580 | poranny chór drobnych ptaków: szybkie wysokie dzwoniące świergoty |

## 14. KOSMETYCZNE — cisza w pliku

- cisza wiodąca > 0.6 s: **3** plików (583, 542, 232)
- cisza końcowa > 1.5 s: **3** plików (113, 12, 156)

To nie jest błąd generacji — sample po prostu nie wypełnia całej zadeklarowanej
długości. Trym/skrócenie pliku jest opcjonalne i bezkosztowe.

## 15. Rekomendowana kolejka decyzji

Kolejność jest celowa: najpierw tania, odwracalna obróbka całego korpusu, dopiero
potem odsłuch i dopiero na końcu wydawanie kredytów.

1. **Postprodukcja lokalna, 0 kredytów** — wyrównanie głośności całego korpusu, limiter −1 dBTP, filtr DC. Bezpośrednio dotyczy 2 plików z flagami głośnościowymi: 72, 611

2. **Do odsłuchu przed decyzją** — 37 ID (tonalne, mowopodobne, bliźniaki, krótka treść): 5, 6, 23, 26, 37, 71, 98, 103, 118, 124, 146, 163, 164, 187, 204, 231, 241, 260, 261, 266, 298, 301, 317, 325, 343, 347, 358, 396, 468, 489, 493, 496, 521, 539, 558, 562, 578

3. **Kandydaci do regeneracji (kredyty, po potwierdzeniu uchem)** — 2 ID bez treści w paśmie słyszalnym: 49, 339

   Uwaga: część z nich to scenariusze **celowo** niskie (kroki olbrzymów, tąpnięcia,
   bicie serca). Jeśli po EQ i normalizacji brzmią poprawnie, regeneracja jest zbędna.

Pełne metryki per plik: JSON obok tego raportu.

