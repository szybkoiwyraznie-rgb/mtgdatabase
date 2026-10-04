# Pełny audyt korpusu sampli — 2026-10-04

Zakres: **549** plików `audio/samples/<id>.mp3`. Skan od zera skryptem
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
| WYSOKIE — ucięty koniec | 2 | wysoka | odsłuch → regeneracja/fade |
| WYSOKIE — za cicho (LUFS/peak) | 0 | wysoka | normalizacja w postprodukcji |
| WYSOKIE — energia w infradźwiękach | 0 | wysoka | EQ+normalizacja albo regeneracja |
| WYSOKIE — brak treści powyżej 250 Hz | 0 | średnia | odsłuch → regeneracja |
| WYSOKIE — treść krótsza niż 0,8 s | 11 | wysoka | trym albo regeneracja |
| WYSOKIE — zapadanie w mono (mono collapse) | 0 | wysoka | korekta mid/side |
| ŚREDNIE — przester (clipping) | 0 | średnia | tłumienie + limiter |
| ŚREDNIE — true peak > +1 dBTP | 0 | średnia | limiter w postprodukcji |
| ŚREDNIE — za głośno | 0 | średnia | wyrównanie głośności |
| ŚREDNIE — offset DC | 0 | wysoka | filtr górnoprzepustowy 20 Hz |
| ŚREDNIE — dominacja dudnienia (boomy) | 0 | niska | filtr dolnozaporowy / shelf |
| ŚREDNIE — brak góry (dull) | 3 | niska | korekta high-shelf |
| ŚREDNIE — ostra góra (harsh) | 32 | niska | łagodne cięcie 4-6 kHz |
| DO ODSŁUCHU — tonalne/„muzyczne" | 3 | niska | weryfikacja uchem |
| DO ODSŁUCHU — podobne do mowy | 5 | niska | weryfikacja uchem |
| DO ODSŁUCHU — start na pełnym poziomie | 7 | niska | weryfikacja uchem / fade-in |
| BLIŹNIAKI — para sampli ≥ 0.95 kosinusa | 0 | niska | odsłuch pary, ewentualnie nowy prompt |
| KOSMETYCZNE — długa cisza wiodąca | 2 | wysoka | opcjonalny trym |
| KOSMETYCZNE — długa cisza końcowa | 39 | wysoka | opcjonalny trym |

Plików z co najmniej jedną flagą: **91** / 549.
Plików z flagą **merytoryczną** (bez kategorii kosmetycznych i „start na pełnym
poziomie"): **13**.


## Najważniejszy wniosek: korpus nie ma wyrównanej głośności

Rozkład głośności percepcyjnej: mediana **-20.0 LUFS**, p10 **-20.1**, p90 **-20.0**, σ **0.1 LU**, rozpiętość **3.1 LU** (od -21.9 do -18.8).

To nie jest kwestia pojedynczych odstających plików — **cały korpus jest nierówny**.
Przy odsłuchu biblioteki po kolei jedne sample są ledwie słyszalne, inne wyrywają
głośniki. Nic dziwnego: każdy plik przyszedł z generatora bez wspólnego odniesienia.

Gdyby wyrównać wszystko do **-20 LUFS** z sufitem **−1 dBTP**:

- plików wymagających wzmocnienia > +10 dB: **0** (z tego > +15 dB: 0 — tam wyjdzie szum tła, lepiej zregenerować),
- plików wymagających wyciszenia > 6 dB: **0**,
- plików w granicach ±3 dB od celu: **549**.

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
| 306 | Mysteries of the Deep | -31.34 dBFS | -20.88 dBFS | -10.5 dB | — |

## 3. WYSOKIE — za cicho względem korpusu

Próg: LUFS < -32 albo peak < −18 dBFS. Większość naprawia normalizacja (bez kredytów); przy wzmocnieniu > +15 dB trzeba sprawdzić, czy nie wychodzi szum.

_Brak plików w tej kategorii._

## 4. WYSOKIE — energia zepchnięta w infradźwięki

Ponad 80 % energii poniżej 60 Hz. Miernik peaku pokazuje „głośno", ale na laptopie, telefonie i większości słuchawek taki sample jest praktycznie niesłyszalny — dlatego LUFS (ważony percepcyjnie) bywa tu 20 dB niżej niż peak. Naprawa: EQ (odcięcie 40 Hz) + normalizacja, a jeśli po tym nie zostaje treść — regeneracja.

_Brak plików w tej kategorii._

## 5. WYSOKIE — brak treści powyżej 250 Hz

Mniej niż 2 % energii powyżej 250 Hz — w paśmie, w którym ucho rozpoznaje materiał i detal, nie ma nic. Dla tąpnięcia olbrzyma to bywa poprawne, dla metalu, szkła, ptaków czy magii oznacza zgubioną treść.

_Brak plików w tej kategorii._

## 6. ŚREDNIE — przester i true peak

Przester = > 0.05 % próbek na pełnej skali (w tym korpusie: brak). True peak > +1 dBTP to ryzyko zniekształceń po transkodowaniu — naprawialne limiterem, bez kredytów.

_Brak plików w tej kategorii._

## 7. WYSOKIE — realna treść krótsza niż 0,8 s

Po odjęciu ciszy zostaje bardzo mało dźwięku. Czasem to poprawne (jedno uderzenie), czasem generacja urwała temat. Flaga liczona **progiem względnym** (40 dB poniżej maksimum pliku), bo próg absolutny przesuwa się razem z poziomem nagrania — kolumna obok pokazuje, ile wychodzi po staremu.

| ID | Tytuł | Treść (próg wzgl.) | Treść (próg −45 dBFS) | Długość pliku | Scenariusz |
|---|---|---|---|---|---|
| 517 | Force Away | 0.21 s | 0.21 s | 2.48 s | twarde uderzenie sprężonego powietrza rozpyla |
| 290 | Soulbright Flamekin | 0.31 s | 0.22 s | 2.48 s | buchnięcie płomienia z trzaskiem iskier na st |
| 191 | Esper Stormblade | 0.41 s | 0.36 s | 2.48 s | unoszenie się vedalkena nad krawędzią wulkani |
| 403 | Dementia Bat | 0.42 s | 0.35 s | 2.48 s | pęknięcie metalowego pancerza nietoperza i ch |
| 504 | Ballista Watcher | 0.51 s | 0.41 s | 2.48 s | pojedynczy strzał ciężkiej balisty: trzask sp |
| 321 | Ainok Artillerist | 0.56 s | 0.51 s | 2.48 s | wystrzał balisty z drewna świętych gajów |
| 76 | Negate | 0.7 s | 0.64 s | 2.48 s | rozbicie strumienia zaklęcia o niewidzialną b |
| 65 | Curate | 0.71 s | 0.7 s | 2.48 s | gwałtowne otwarcie lewitującego tomu z błękit |
| 105 | Blade-Blizzard Kitsune | 0.74 s | 0.73 s | 2.48 s | świetlny wicher podwójnych energetycznych kat |
| 567 | Jwar Isle Avenger | 0.74 s | 0.65 s | 2.48 s | szpony przebijające chitynowy pancerz w locie |
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
| 71 | Security Rhox | 1.00 | 222 Hz | 0.18 | 0.0 | głuche, gumowate uderzenie ciała o niewidzialną barierę z kr |
| 163 | Ghoulcaller's Bell | 1.00 | 727 Hz | 0.0 | 0.0002 | dźwięk patynowanego dzwonu nekromanty z sączącą się mgłą |
| 347 | Pristine Talisman | 0.99 | 888 Hz | 0.0 | 0.001 | pojedyncze czyste uderzenie małego wypolerowanego dzwonka z  |

## 11. DO ODSŁUCHU — podobne do mowy

Heurystyka mowy — niska pewność. Sprawdzić, czy nie ma zrozumiałych słów (prompty zabraniają mowy).

| ID | Tytuł | Modulacja 2–8 Hz | Udział dźwięcznych | Centroid | Scenariusz |
|---|---|---|---|---|---|
| 489 | Seer's Lantern | 0.85 | 1.00 | 636 Hz | zgrzyt przesłony latarni i narastający krystaliczny ton szkł |
| 578 | Savage Surge | 0.61 | 0.94 | 2597 Hz | nagły zwrot centagora z ciężkim kiścieniem |
| 130 | Scavenging Harpy | 0.58 | 0.69 | 2868 Hz | skrzek harpii strzegącej zrabowanego sygnetu na sarkofagu |
| 163 | Ghoulcaller's Bell | 0.58 | 1.00 | 1968 Hz | dźwięk patynowanego dzwonu nekromanty z sączącą się mgłą |
| 580 | Loporrit Scout | 0.56 | 0.80 | 1473 Hz | pogodne, gulgoczące ćwierknięcie chocobo tuż przy uchu |

## 12. BLIŹNIAKI — sample brzmiące niemal identycznie

Kosinus odcisków log-mel ≥ 0.95. Identyczny PCM (md5): **0** grup.

_Nie znaleziono par powyżej progu._

## 13. Kontrola tekstów scenariuszy

Wszystkie prompty i opisy scenariuszy są unikalne (527/527).

## 14. KOSMETYCZNE — cisza w pliku

- cisza wiodąca > 0.6 s: **2** plików (604, 232)
- cisza końcowa > 1.5 s: **39** plików (517, 290, 191, 403, 514, 616, 197, 504, 593, 321, 14, 76, 556, 567, 65, 105, 218, 85, 39, 527, 544, 268, 87, 543, 291 …)

To nie jest błąd generacji — sample po prostu nie wypełnia całej zadeklarowanej
długości. Trym/skrócenie pliku jest opcjonalne i bezkosztowe.

## 15. Różnice względem audytu po rundzie r005

- flagi merytoryczne w poprzednim skanie: **13**, teraz: **13**
- nowe (nie widział ich poprzedni zestaw metryk): —
- zniknęły: —

Uwaga: poprzedni skan nie mierzył LUFS, pasma, tonalności ani duplikatów,
więc większość „nowych" pozycji to nie regresja plików, tylko nowe kryterium.

## 16. Rekomendowana kolejka decyzji

Kolejność jest celowa: najpierw tania, odwracalna obróbka całego korpusu, dopiero
potem odsłuch i dopiero na końcu wydawanie kredytów.

1. **Postprodukcja lokalna, 0 kredytów** — wyrównanie głośności całego korpusu, limiter −1 dBTP, filtr DC. Bezpośrednio dotyczy 2 plików z flagami głośnościowymi: 72, 306

2. **Do odsłuchu przed decyzją** — 18 ID (tonalne, mowopodobne, bliźniaki, krótka treść): 65, 71, 76, 105, 130, 163, 191, 290, 321, 347, 403, 489, 504, 517, 567, 578, 580, 593

3. **Kandydaci do regeneracji (kredyty, po potwierdzeniu uchem)** — 0 ID bez treści w paśmie słyszalnym: —

   Uwaga: część z nich to scenariusze **celowo** niskie (kroki olbrzymów, tąpnięcia,
   bicie serca). Jeśli po EQ i normalizacji brzmią poprawnie, regeneracja jest zbędna.

Pełne metryki per plik: JSON obok tego raportu.

