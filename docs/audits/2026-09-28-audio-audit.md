# Audyt sygnałowy sampli — 2026-09-28

Zakres: wszystkie **527** plików `audio/samples/<id>.mp3` (paczki b001–b053).
Metoda: dekodowanie PCM (libsndfile) + analiza obwiedni w ramkach 10 ms —
skrypt `scripts/audit_samples_audio.py`. Audyt **tylko typuje podejrzanych**;
nic nie było regenerowane ani zmieniane.

## Metodologia i uczciwe zastrzeżenia

- **Ucięty koniec**: energia w ostatnich 10/30 ms pliku. Zdrowy sample wybrzmiewa
  (mediana korpusu: −71 dBFS w ostatnich 10 ms). Plik kończący się na poziomie
  > −30 dBFS albo w granicach 15 dB od swojego maksimum urywa się w pół dźwięku.
  To najbardziej wiarygodna flaga w tym audycie.
- **Ucięty start**: energia w pierwszych 15 ms. Zastrzeżenie: sample SFX z natury
  atakują szybko (mediana korpusu w pierwszych 15 ms to już −32 dBFS), więc flaga
  łapie tylko starty od razu na pełnym poziomie pliku (> −12 dBFS i w granicach
  4 dB od maksimum). Dla dźwięków ciągłych (bitwa, deszcz, tłum) taki start bywa
  naturalny — ta kategoria wymaga potwierdzenia uchem, dlatego ma niższą pewność.
- **Za cicho**: peak < −18 dBFS lub aktywny RMS odstający > 2,5σ od średniej
  korpusu (średnia −26,4 dBFS, σ ≈ 5,6 dB). Część scenariuszy jest celowo cicha —
  zaznaczono w tabeli.
- **Przester**: > 0,05% sampli przy pełnej skali; szczyty do +2,6 dBFS po dekodowaniu.
- **Cisza wiodąca/końcowa**: > 0,6 s / > 1,5 s ciszy (< −45 dBFS) w plikach 2–3 s —
  wada kosmetyczna, nie błąd generacji.
- Czas trwania: **bez zastrzeżeń** — wszystkie 527 plików zgadza się z `duration_seconds`
  scenariusza (±0,02 s).

## Podsumowanie

| Kategoria | Plików | Pewność | Rekomendacja |
|---|---|---|---|
| KRYTYCZNE — (prawie) cisza | 3 | wysoka | regeneracja praktycznie pewna |
| WYSOKIE — ucięty koniec | 21 | wysoka | odsłuch, większość do regeneracji |
| WYSOKIE — za cicho | 13 | średnia | odsłuch; część może być celowo cicha |
| ŚREDNIE — przester | 21 | średnia | odsłuch pod kątem zniekształceń |
| DO ODSŁUCHU — start na pełnym poziomie | 39 | niska | weryfikacja uchem |
| KOSMETYCZNE — długa cisza w pliku | 43 | wysoka | opcjonalny trym, nie regeneracja |
| **Razem plików z ≥1 flagą** | **140** | | |

Pozostałe **387** plików przeszło audyt bez zastrzeżeń.

## 1. KRYTYCZNE — plik (prawie) całkiem cichy

| ID | Tytuł | Peak dBFS | Aktywny RMS | Uwagi |
|---|---|---|---|---|
| 115 | Merfolk Mesmerist | -28.66 | -43.3 | maks. ramka −41 dBFS, do tego urwany koniec |
| 303 | Blanchwood Prowler | -32.11 | -44.36 | 1,77 s ciszy na starcie, treść ledwo słyszalna |
| 377 | Scroll of Avacyn | -39.71 | -120.0 | plik w praktyce PUSTY (cała długość poniżej progu ciszy) — nieudana generacja |

## 2. WYSOKIE — dźwięk ucięty na końcu (brak wybrzmienia)

Posortowane od najbrutalniejszego cięcia (poziom w ostatnich 10 ms pliku).

| ID | Tytuł | Koniec (ost. 10 ms) | Maks. ramka | Różnica | Inne flagi |
|---|---|---|---|---|---|
| 281 | Moonlit Meditation | -6.15 dBFS | -2.33 dBFS | -3.8 dB | — |
| 576 | Akroan Sergeant | -7.31 dBFS | -3.4 dBFS | -3.9 dB | cut_start_hard, clipping |
| 264 | Ghost Warden | -10.54 dBFS | -6.93 dBFS | -3.6 dB | cut_start_hard |
| 388 | Goblin Picker | -12.2 dBFS | -10.69 dBFS | -1.5 dB | — |
| 306 | Mysteries of the Deep | -19.64 dBFS | -15.18 dBFS | -4.5 dB | — |
| 159 | Predator's Gambit | -19.7 dBFS | -11.33 dBFS | -8.4 dB | — |
| 496 | Shiv's Embrace | -20.24 dBFS | -15.53 dBFS | -4.7 dB | — |
| 347 | Pristine Talisman | -20.28 dBFS | -15.73 dBFS | -4.6 dB | — |
| 542 | Panic Spellbomb | -20.7 dBFS | -2.1 dBFS | -18.6 dB | cut_start_hard, clipping |
| 204 | Skilled Animator | -24.22 dBFS | -11.5 dBFS | -12.7 dB | cut_start_hard |
| 517 | Force Away | -26.84 dBFS | -12.54 dBFS | -14.3 dB | — |
| 560 | Dead Ringers | -28.07 dBFS | -5.92 dBFS | -22.1 dB | cut_start_hard |
| 186 | Cogwork Assembler | -28.95 dBFS | -15.19 dBFS | -13.8 dB | — |
| 150 | Balamb Garden, SeeD Academy | -29.12 dBFS | -18.53 dBFS | -10.6 dB | — |
| 346 | Necrosquito | -29.13 dBFS | -16.58 dBFS | -12.6 dB | — |
| 149 | Blossoming Sands | -29.53 dBFS | -15.53 dBFS | -14.0 dB | — |
| 191 | Esper Stormblade | -30.45 dBFS | -25.53 dBFS | -4.9 dB | — |
| 454 | Setessan Skirmisher | -31.1 dBFS | -13.35 dBFS | -17.8 dB | — |
| 349 | Enduring Sliver | -34.43 dBFS | -11.08 dBFS | -23.4 dB | — |
| 124 | Courage in Crisis | -35.06 dBFS | -12.7 dBFS | -22.4 dB | — |
| 511 | Emerald Oryx | -41.82 dBFS | -28.9 dBFS | -12.9 dB | too_quiet |

## 3. WYSOKIE — za cicho względem korpusu

Średni aktywny RMS korpusu: −26,4 dBFS. Poniżej −38 dBFS sample ginie przy odsłuchu
obok pozostałych. Część scenariuszy jest z natury cicha — ocena w kolumnie „scenariusz”.

| ID | Tytuł | Peak | Aktywny RMS | Scenariusz (skrót) |
|---|---|---|---|---|
| 309 | Civilized Scholar | -27.44 | -42.66 | cień bestii w lustrze uczonego i rozlany atrament |
| 302 | Curate | -25.44 | -42.59 | obracanie błękitnej sfery i odkładanie zwojów na dębowym stole |
| 169 | Greenwood Sentinel | -19.92 | -42.53 | szelest żywych liści w zbroi elfickiej zwiadowczyni na mszarze |
| 200 | Cloak of the Bat | -26.57 | -41.69 | świsz lotu złodzieja w płaszczu-nietoperzu między kominami |
| 352 | Evangel of Synthesis | -19.65 | -41.06 | krople oleju pieczętujące pakt syntezy z akolitą |
| 582 | Vaan, Street Thief | -28.69 | -40.75 | dachowy skok złodzieja nad baldachimami targu |
| 93 | Dispeller's Capsule | -22.2 | -40.55 | rozchylenie się płatków kapsuły ze spiralą oczyszczającej energii |
| 172 | Mournful Zombie | -19.72 | -40.41 | cierpliwe przewijanie bandaży smutnego zombie przy świecach |
| 181 | Spectral Prison | -22.29 | -40.09 | utkana ze bladego światła klatka nici więżąca postać w magicznym śnie |
| 301 | Guildscorn Ward | -21.33 | -39.79 | bezbarwna bariera odpychająca patrol gildii w zaułku |
| 213 | Reclusive Artificer | -21.0 | -39.5 | jednoczesna aktywacja całego gabinetu wynalazków rzemieślniczki |
| 331 | Trostani Discordant | -18.09 | -38.73 | liście opadające między trzema siostrami w milczeniu oczekiwania |
| 492 | Secluded Steppe | -26.48 | -38.19 | wiatr nad kurhanami Rohanu wśród simbelmynë |

## 4. ŚREDNIE — przester / szczyty ponad pełną skalę

| ID | Tytuł | Peak dBFS | % sampli w klipie | Inne flagi |
|---|---|---|---|---|
| 461 | Negate | 2.48 | 0.556% | — |
| 434 | Epic Experiment | 1.12 | 0.547% | — |
| 288 | Wedgelight Rammer | 2.62 | 0.42% | — |
| 615 | Tah-Crop Skirmisher | 1.31 | 0.391% | cut_start_hard |
| 88 | Baral and Kari Zev | 1.48 | 0.293% | cut_start_hard |
| 401 | Rage of Purphoros | 1.7 | 0.29% | cut_start_hard |
| 287 | Sarkhan's Rage | 1.88 | 0.241% | cut_start_hard |
| 243 | Willbender | 2.12 | 0.161% | — |
| 493 | Skyclave Geopede | 1.56 | 0.161% | cut_start_hard |
| 108 | Forced Landing | 1.45 | 0.154% | — |
| 501 | Exterminator Magmarch | 1.11 | 0.137% | cut_start_hard |
| 585 | Jolrael, Mwonvuli Recluse | 1.95 | 0.135% | — |
| 504 | Ballista Watcher | 2.31 | 0.125% | — |
| 76 | Negate | 1.8 | 0.095% | — |
| 373 | Fear of Abduction | 1.33 | 0.094% | — |
| 435 | Warrior's Sword | 2.2 | 0.084% | cut_start_hard |
| 202 | Inferno Titan | 1.79 | 0.076% | — |
| 494 | Crested Herdcaller | 0.68 | 0.066% | — |
| 606 | Treefolk Umbra | 1.0 | 0.057% | — |
| 448 | Rupture Spire | 1.47 | 0.055% | cut_start_hard |
| 77 | Annie Flash, the Veteran | 1.41 | 0.053% | — |

## 5. DO ODSŁUCHU — start od razu na pełnym poziomie (niska pewność)

Możliwe wejście „w środek dźwięku”, ale dla ciągłych faktur to bywa naturalne.

| ID | Tytuł | Start (15 ms) | Maks. ramka | Scenariusz (skrót) |
|---|---|---|---|---|
| 156 | Summary Judgment | -3.53 dBFS | -3.8 dBFS | opadająca z nieba złota pieczęć przygważdżająca buntownika do bruku |
| 613 | Duskmantle Seer | -8.86 dBFS | -8.93 dBFS | psioniczna sieć wydzierająca wspomnienia w archiwum |
| 452 | Omenspeaker | -10.57 dBFS | -10.49 dBFS | ożywione astrolabium rzucające nieznane konstelacje na sufit |
| 440 | Your Temple Is Under Attack | -2.95 dBFS | -2.84 dBFS | srebrna bariera kapłana zatrzymująca szarżę biesa |
| 487 | Stoic Rebuttal | -2.93 dBFS | -2.81 dBFS | geometryczna tarcza rezonansu rozbijająca ognisty pocisk |
| 252 | Captain's Call | -6.49 dBFS | -6.34 dBFS | ryt w branego rogu i zwieranie tarcz obrońców w ruinach |
| 311 | Guildsworn Prowler | -5.09 dBFS | -4.93 dBFS | bójka w tawernie za plecami zabójcy i rozkaz w rynnie |
| 113 | Welder Automaton | -6.65 dBFS | -6.48 dBFS | spawanie palnikiem miedziano-mosiężnego automatu z iskrami metalu |
| 459 | Prismari Campus | -9.42 dBFS | -9.23 dBFS | zderzenie ognia i wody w taflę lodu i pary na scenie |
| 91 | Curse of the Pierced Heart | -5.31 dBFS | -5.11 dBFS | wbicie ciernia w serce rytualnej figurki z szarpnięciem klątwy |
| 330 | Invasion of the Giants | -9.51 dBFS | -9.3 dBFS | przejście olbrzymów przez Omenpath i zryw tarcz klanu |
| 607 | Containment Membrane | -4.99 dBFS | -4.75 dBFS | bestia zamknięta w lewitującej sferze stazy |
| 337 | Glaring Aegis | -2.12 dBFS | -1.85 dBFS | odbicie promienia słońca od tarczy hoplity oślepiające wroga |
| 430 | Nightshade Harvester | -3.5 dBFS | -3.15 dBFS | zbieranie wilczych jagód w księżycowym lesie |
| 137 | Withstand | -6.99 dBFS | -6.64 dBFS | strumień ognia rozpraszający się na krawędziach wieżowej tarczy z p… |
| 456 | Crawling Chorus | -10.64 dBFS | -10.01 dBFS | porcelanowe monstrum rozsypujące się w rój metalowych roztoczy |
| 130 | Scavenging Harpy | -10.12 dBFS | -9.12 dBFS | skrzek harpii strzegącej zrabowanego sygnetu na sarkofagu |
| 389 | Bring Low | -10.91 dBFS | -9.88 dBFS | uklęknięcie lodowego żywiołaka pod dotykiem chana |
| 386 | Insatiable Appetite | -6.59 dBFS | -5.49 dBFS | żarłoczna uczta olbrzyma w zagrodzie chłopów |
| 175 | Caves of Chaos Adventurer | -4.45 dBFS | -3.31 dBFS | pęknięcie ametystowej ściany z wypadającym zwójem i sakwą monet |
| 256 | Frightful Delusion | -9.79 dBFS | -8.52 dBFS | koszmarne wizje sączące się do umysłu śpiącej kobiety |
| 528 | Enter the Enigma | -10.61 dBFS | -9.33 dBFS | przecięcie bariery rzeczywistości błękitnymi iskrami |
| 160 | Fiery Hellhound | -4.87 dBFS | -3.33 dBFS | ogień ogar żywiołów wymyka się spod kontroli i zrywa do skoku |
| 480 | Zoraline, Cosmos Caller | -4.16 dBFS | -2.48 dBFS | astralny strumień gwiazd budzący nieprzytomnego zwiadowcę |
| 209 | Burning-Yard Trainer | -8.47 dBFS | -6.74 dBFS | machnięcie płonącym treningowym mieczem i spokojenie konia |
| 466 | Basilisk Gate | -11.4 dBFS | -9.11 dBFS | złoty rezonans bram miasta nasycający pancerz strażnika |
| 569 | Manifest Dread | -10.84 dBFS | -8.29 dBFS | pulsujący kokon lęku kontra miotacz ognia |
| 321 | Ainok Artillerist | -4.65 dBFS | -2.01 dBFS | wystrzał balisty z drewna świętych gajów |
| 27 | Erase | -8.06 dBFS | -5.29 dBFS | pęknięcie złowrogiej klątwy na tysiące nieszkodliwych okruchów |
| 262 | Angel's Herald | -10.64 dBFS | -7.84 dBFS | trąbka herolda wzywająca anioła słupem światła |
| 24 | Lunar Rejection | -6.26 dBFS | -3.36 dBFS | lodowaty puls księżycowego światła odpychający wyjącego wilkołaka |
| 34 | Volcanic Submersion | -6.03 dBFS | -3.12 dBFS | smoczy kolos nurkujący w krater z erupcją wrzącej magmy |
| 11 | Sleep of the Dead | -6.74 dBFS | -3.65 dBFS | ciężkie ziewnięcie śpiącego cerbera przechodzące w cichnący senny p… |
| 236 | Agate Assault | -6.05 dBFS | -2.88 dBFS | kaskada głazów z pękającej krawędzi urwiska wywołana magią salamandry |
| 515 | Warmaker Gunship | -11.45 dBFS | -8.07 dBFS | gunship opuszczający rampę i wysypujący bojowe drony |
| 534 | Terminal Agony | -7.79 dBFS | -4.22 dBFS | pancerz czempiona zmieniający się w żużel i ryk ofiary |
| 21 | Pyxis of Pandemonium | -8.05 dBFS | -4.47 dBFS | stukot podskakującego wieka ceramicznej pyksy z wybuchem światła i … |
| 305 | Illusory Demon | -8.44 dBFS | -4.53 dBFS | rozsypujący się na świetliste drobiny iluzoryczny demon |
| 601 | Exploding Borders | -8.73 dBFS | -4.8 dBFS | zderzenie Jundu z Nayą — lawa pochłania prastary las |

## 6. KOSMETYCZNE — nietypowo długa cisza w pliku

| ID | Tytuł | Cisza na starcie | Cisza na końcu |
|---|---|---|---|
| 1 | Dunland Crebain | 0.0 s | 1.63 s |
| 14 | Crew Captain | 0.0 s | 1.85 s |
| 17 | Selhoff Occultist | 0.0 s | 1.94 s |
| 45 | Piercing Rays | 0.07 s | 1.55 s |
| 50 | Dream Twist | 0.03 s | 1.51 s |
| 65 | Curate | 1.16 s | 0.66 s |
| 70 | Capture Sphere | 0.0 s | 1.67 s |
| 82 | Messenger Falcons | 0.09 s | 1.56 s |
| 109 | Relic Robber | 0.0 s | 1.55 s |
| 142 | Savage Hunger | 0.0 s | 1.68 s |
| 185 | Alaborn Trooper | 0.56 s | 1.61 s |
| 197 | Dismal Backwater | 0.28 s | 2.01 s |
| 218 | Trigon of Corruption | 0.87 s | 0.92 s |
| 232 | Goblin Piker | 0.71 s | 0.77 s |
| 275 | Aerith Rescue Mission | 0.0 s | 1.74 s |
| 283 | Magic Damper | 0.08 s | 2.13 s |
| 304 | Sagittars' Volley | 0.64 s | 1.71 s |
| 345 | Porcelain Legionnaire | 0.07 s | 2.17 s |
| 355 | Cathartic Reunion | 0.0 s | 1.65 s |
| 360 | Inspiration | 0.8 s | 0.81 s |
| 379 | Swooping Protector | 0.72 s | 0.88 s |
| 382 | Geological Appraiser | 0.64 s | 1.03 s |
| 393 | Forge Devil | 0.67 s | 0.43 s |
| 403 | Dementia Bat | 0.79 s | 1.33 s |
| 442 | Cenn's Tactician | 0.0 s | 2.11 s |
| 453 | Elgaud Inquisitor | 0.0 s | 2.08 s |
| 460 | Ivy Lane Denizen | 1.16 s | 1.12 s |
| 463 | Knockout Maneuver | 0.66 s | 0.56 s |
| 472 | Kazuul's Toll Collector | 0.0 s | 2.03 s |
| 482 | True Conviction | 0.02 s | 1.66 s |
| 484 | Guidestone Compass | 0.0 s | 1.51 s |
| 499 | Vandalize | 0.0 s | 1.56 s |
| 500 | Instant Ramen | 0.67 s | 0.76 s |
| 518 | Woolly Loxodon | 0.0 s | 1.62 s |
| 535 | Lab Rats | 0.0 s | 1.55 s |
| 543 | Wooden Stake | 0.0 s | 1.65 s |
| 578 | Savage Surge | 0.61 s | 0.84 s |
| 580 | Loporrit Scout | 0.65 s | 0.73 s |
| 584 | Merfolk Falconer | 0.62 s | 0.75 s |
| 591 | Rust-Shield Rampager | 0.0 s | 1.9 s |
| 592 | Glorifier of Suffering | 0.03 s | 1.92 s |
| 608 | Skymarch Bloodletter | 0.0 s | 2.32 s |
| 610 | Gearsmith Prodigy | 0.0 s | 2.07 s |

## Pełne metryki

Surowe metryki wszystkich 527 plików: `data/samples/audio-audit-2026-09-28.json`
(wyjście `scripts/audit_samples_audio.py`).

---

## Aktualizacja po regeneracji (2026-09-28, ta sama sesja)

Właściciel zatwierdził regenerację kategorii: krytyczne (3) + ucięty koniec (21)
+ za cicho (13) + przester (21) = **58 plików**. Kategoria „start na pełnym
poziomie" czeka na odsłuch właściciela; kosmetyczne pominięte.

### Runda r001 — 58 plików (run 36411204847)

Prompty podejrzanych dostały celowane dopiski (bez zmiany idei dźwięku):
za ciche → `Recorded close-up, clearly audible, strong presence.`,
ucięte → `The sound finishes with a quick natural decay, fully faded out
before the clip ends.`, przester → `Clean recording at moderate level,
no distortion.` Wszystkie 58 wygenerowane ze statusem `generated`.
Ponowny audyt: **41/58 naprawione**, 17 nadal z flagą główną
(w tym 1 regresja: `191` z uciętego końca na prawie niemy).

### Runda r002 — 17 plików (run 36411895113)

Mocniejsze dopiski (`loud, prominent, close foreground` / `generous
headroom` / `decays completely to silence`). Ponowny audyt po imporcie:
**łącznie 49/58 naprawione**. Zostało **9 opornych**:

| ID | Było | Jest | Uwagi po r002 |
|---|---|---|---|
| 150 | ucięty koniec | za cicho | koniec naprawiony, poziom spadł (aktywny RMS −39,7) |
| 181 | za cicho | za cicho | −41,3 dBFS mimo dwóch rund |
| 302 | za cicho | za cicho | −39,6 dBFS |
| 303 | prawie niemy | za cicho | duża poprawa (z −44,4 na −42,6; peak z −32 na −25) |
| 347 | ucięty koniec | ucięty koniec | poprawa końcówki (−5 → −23 dBFS), wciąż za mało wybrzmienia |
| 377 | PUSTY | za cicho | plik już nie jest pusty; nadal cichy (−42,2) |
| 493 | przester | przester | peak +2,2 dBFS |
| 504 | przester | przester | peak +1,35 dBFS |
| 511 | ucięty koniec + cicho | za cicho | koniec naprawiony |

### Wniosek

Dla tych 9 plików możliwości promptu się wyczerpały — model uparcie generuje
delikatne sceny cicho, a mastering ElevenLabs sam wbija szczyty ponad pełną
skalę. Rzetelna rekomendacja: **deterministyczna postprodukcja** zamiast
kolejnych losowań — normalizacja szczytowa do ok. −1,5 dBFS dla za cichych,
tłumienie −3 dB dla przesterów, krótki fade-out 150 ms dla `347`. Decyzja
właściciela.

Metryki po regeneracji: `data/samples/audio-audit-2026-09-28-after-regen.json`.
Zużycie quota: 75 generacji ≈ 3 750 kredytów (zostało ~5 150 na trzecim kluczu).

### Runda r003 — 9 opornych z całkiem nowymi promptami (run 36413153819)

Właściciel zlecił przepisanie promptów od zera na jednoźródłowe, fizycznie
zakotwiczone dźwięki. Wynik: **6/9 czystych** (303, 347, 377, 493, 504, 511 —
w tym 377 z pustego pliku do zdrowego sampla, peak −1,85 dBFS). Zostały:
`150` (ciągła fontanna — głośna i zdrowa, ale ciągłe źródło z natury urywa się
na końcu klipu; wystarczy fade-out), `181` i `302` (model generuje je cicho
mimo wymuszeń; wystarczy normalizacja). Łącznie po trzech rundach:
**55/58 naprawione**, 3 do ewentualnej postprodukcji.

---

## Postprodukcja opornych + regeneracja semantyczna r004 (2026-09-28)

**Postprodukcja (zatwierdzona przez właściciela):** deterministyczne poprawki
zamiast kolejnych losowań — `150` i `74` (ciągłe źródła: fade-out 0,4–0,45 s),
`181`, `302`, `195`, `223`, `279`, `322` (normalizacja szczytowa do −1,5 dBFS),
`528` (tłumienie −3,5 dB). Narzędzie: dekodowanie/enkodowanie libsndfile.

**Audyt semantyczny (wyniki w czacie, decyzja właściciela):** 78 fabuł miało
prompty opisujące obraz/abstrakt zamiast dźwięku (18), muzykę (6) albo wiele
rozłącznych zdarzeń naraz (54). Wszystkie 78 przepisano od zera na
jednoźródłowe, fizycznie zakotwiczone dźwięki i zregenerowano w rundzie r004
(run 36415052620, 78/78 `generated`). Audyt sygnałowy po r004: 72/78 czyste,
6 poprawione postprodukcją jak wyżej.

**Stan końcowy: 527/527 plików bez żadnej głównej flagi sygnałowej**
(near_silent / too_quiet / clipping / cut_end). Pozostają wyłącznie flagi
kosmetyczne (dłuższe cisze, szybkie starty ciągłych faktur) — zaakceptowane
przez właściciela po odsłuchu.

Zużycie quota: 162 generacje ≈ 8 100 kredytów; na trzecim kluczu zostało
~800 — kolejna paczka będzie wymagała nowego klucza (konta bezpłatne,
decyzja właściciela: bez ograniczeń).
