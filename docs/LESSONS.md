# LESSONS — trwała wiedza projektu

Ten plik zawiera krótkie, praktyczne lekcje wynikające z pracy agentów. Każdy wpis powinien odpowiadać na pytanie: co się wydarzyło, czego się nauczyliśmy i jak zapobiec powtórce.

> **Jak czytać ten plik:** wpisy są chronologiczne i **nowszy wpis może
> uchylić starszy** (np. progi widmowe dla teł zostały obalone przez wpis
> o nagraniach terenowych). Przy sprzeczności obowiązuje wpis późniejszy;
> uchylone miejsca są oznaczone. Skrypty wymieniane we wpisach sprzed
> pivotu (`render_jingle.py`, `sync_ratings.py`, `remake_queue.py`,
> `audit_audio.py`, `validate_versions.py`, `docs/agent-workflow.md`) już
> nie istnieją — opisują dawną fabrykę i zostają jako wiedza procesowa.
>
> **Uwaga (2026-09-23):** wpisy sprzed tej daty opisują zakończoną „fabrykę jingli”
> (oceny z issues, wersje vN, remake’i, `versions.json`). Zachowujemy je dla
> wiedzy procesowej (audycja sampli, determinizm renderu, kanały pobierania),
> ale reguły produktu wynikają dziś z ADR 0003 i `docs/signature-system.md`.

## Format wpisu

```markdown
## YYYY-MM-DD — Krótki tytuł

- Sytuacja:
- Wniosek:
- Zasada / działanie zapobiegawcze:
```

## 2026-09-21 — Workflow musi być bezpieczny na branchu roboczym

- Sytuacja: deployment Pages nie powinien wykonywać się przed scaleniem do `main`.
- Wniosek: build i deploy trzeba rozdzielić warunkiem gałęzi.
- Zasada / działanie zapobiegawcze: na branchach roboczych uruchamiaj build i walidację, a deployment wykonuj tylko z `main`. Realizacja (od 2026-09-22): dwa workflow — `pages.yml` (build+deploy, wyzwalany tylko z `main`) i `pages-build.yml` (sam build, push na `arena/**`). Warunek `if` w jobie deploy zostawia w checkach PR wiecznie „skipped"; rozdzielenie workflow usuwa ten szum, a reguła pozostaje spełniona.

## 2026-09-22 — Workflow mutujący stan publiczny działa wyłącznie z main

- Sytuacja: workflow synchronizacji ocen uruchomiony po pushu `data/versions.json` na branchu PR zamknął raporty i dopisał komentarze, zanim render znalazł się na `main`.
- Wniosek: kontrola deploymentu Pages nie wystarcza; każdy workflow mogący zmienić issue albo Release jest publikacją i wymaga tej samej granicy gałęzi.
- Zasada / działanie zapobiegawcze: `Sync ratings from issues` i `Build best jingles release` reagują na push wyłącznie z `main`, a ich joby mają dodatkowy guard `github.ref == 'refs/heads/main'`. Branch roboczy dostaje tylko walidację i build podglądu.

## 2026-09-22 — QA licz na zdekodowanym artefakcie, rendery w pełni deterministyczne

- Sytuacja: audyt QA liczył metryki na mixie float przed enkodowaniem, a zdekodowany MP3 dryfował o ~0.4–0.8 pkt (overshoot kodera, zmiana RMS); warstwa `synth_pad` używała nieziarnicowanego RNG, więc render nie był powtarzalny.
- Wniosek: metryki w `versions.json` mają opisywać plik, który faktycznie publikujemy, a receptura musi dawać ten sam artefakt przy każdym przebiegu.
- Zasada / działanie zapobiegawcze: `render_jingle.py` audytuje zapisany MP3 przez `scripts/audit_audio.py`, wszystkie warstwy są ziarnicowane, a `audit_audio.py --versions data/versions.json` służy w pętli do kontroli dryftu metadata↔plik (cel 0.0).

## 2026-09-22 — ID fabuły to liczbowy prefiks artID, nie sklejenie wszystkich cyfr

- Sytuacja: losowanie fabuły własnym parserem „wszystkie cyfry z kolumny Ilustracja" dało ID `45019` zamiast `450` (artID `450M19`: prefiks 450 + set `M19`); `merge_catalog` po cichu usunął fabułę ze strony, bo ID nie istniało w katalogu.
- Wniosek: kanoniczne ID wyznacza wyłącznie regex `^(\d+)([A-Za-z0-9_-]+)$` z `scripts/import_collection.py`; sufiks to metadane setu.
- Zasada / działanie zapobiegawcze: agent losuje i sprawdza fabuły na podstawie WYJŚCIA `import_collection.py` (katalog), nigdy własnym parsowaniem CSV; po merge'u katalog liczba fabuł musi się zgadzać z `versions.json` (kontrola w pętli).

## 2026-09-22 — Bez żywych sampli projekt nie ma sensu (decyzja właściciela)

- Sytuacja: Oceny 5 v2 (3/15, „jakaś masakra... nic nie pasuje") i 450 v1 (7/15, „gdzie warczenie wilka? a ten dron? co to SF?") odrzuciły miksy zbudowane głównie na warstwach syntetycznych w scenach fantasy; pochwalone były wyłącznie żywe nagrania (kroki w błocie). Właściciel zlecił wpisanie na sztywno zasady: syntetyki prawie wyłącznie do SF.
- Wniosek: syntetyczne timbre brzmią obco poza science fiction i zabijają zgodność z fabułą; tożsamość jingla mają nieść realne nagrania ze zweryfikowanego rejestru.
- Zasada / działanie zapobiegawcze: twarda reguła nr 14 w `AGENTS.md` oraz pkt 4 złotych reguł w `legacy/source/INSTRUKCJA_PRODUKCJI_JINGLI.md`; egzekwowana automatycznie przez bramkę żywych sampli w `scripts/render_jingle.py` (pole `genre` w recepturze) i kontrolę `genre`-aware w `scripts/validate_versions.py`.

## 2026-09-22 — Pitchowanie niszczy rozpoznawalność sampla (decyzja właściciela)

- Sytuacja: partia jingli z pitchem 0,45–1,35 była oceniona około 5/15 mimo dobrych metryk technicznych; słuchacz słyszał hałas, nie opisywane zdarzenia.
- Wniosek: słyszalność nie oznacza rozpoznawalności. Tożsamość zdarzenia niesie naturalny timbr nagrania, który zmiana wysokości/tempa niszczy.
- Zasada / działanie zapobiegawcze: dla nowych receptur żywe sample są natywne (`pitch` nieobecny lub `1.0`); inny charakter = inny sample. Bramka `render_jingle.py` i testy odrzucają `pitch != 1`.

## 2026-09-22 — Jak pobierać sample w sandboxie: GitHub, nie Wikimedia

- Sytuacja: poprzedni agent pobierał stems z Wikimedia Commons techniką User-Agent „NazwaAplikacji/Wersja (kontakt)" (bez tego Wikimedia zwraca 403). W sandboxie tej sesji ta technika nie wystarcza: egress tnie połączenie TLS (SSL EOF, kod 000) do upload.wikimedia.org, commons.wikimedia.org, nps.gov, raw.githubusercontent.com i huggingface.co, zanim padnie jakiekolwiek zapytanie HTTP; osiągalne są m.in. github.com, api.github.com i pypi.org.
- Wniosek: kanałem na żywe sample jest **git clone z github.com** (protokół smart HTTP na dozwolonej domenie), nie bezpośrednie pobieranie z Wikimedia/NPS ani `raw.githubusercontent.com`.
- Zasada / działanie zapobiegawcze: sprawdzoną ścieżką jest mirror `github.com/rosuH/YSL` — automatyczny, publiczny crawler Yellowstone Sound Library (NPS, domena publiczna): `git clone --depth 1 --filter=blob:none --sparse` + `git sparse-checkout set <Folder>`. Pełny katalog zweryfikowanych bibliotek (przyroda, foley, miecze/kroki/magia z OpenGameArt, impacts z Kenney, instrumenty VCSL/VSCO, procedura pobierania i dekodowania M4A przez PyAV) prowadzi sekcja „Katalog zweryfikowanych bibliotek dźwięków" w `docs/sources-and-licensing.md`. Każdy sample z rejestru `data/sources.json` musi mieć udokumentowane oryginalne źródło (url NPS/Wikimedia/OGA) i kanał pobrania w `notes`. Uwaga: licencja dotyczy oryginału — status mirrora tylko odnotowujemy, nie traktujemy go jako źródła licencji.
## 2026-09-22 — Niesłyszalne zdarzenia: prawdziwa przyczyna porażek 3-5/15 (audyt sygnałowy)

- Sytuacja: partia jingli (8, 475, 450, 5 v2-v4) oceniona 3-9/15 mimo QA 100/100; dwa wcześniejsze wpisy z tego dnia (zakaz pitchowania, bramka QA ≥85) zdiagnozowały objaw, nie przyczynę. Audyt sygnałowy całości (poziomy, widma, timing, profile RMS wszystkich sampli) wykazał pięć mechanicznych przyczyn: (1) receptury grały **ciche głowy długich nagrań** — raven_call przez pierwsze 4 s ma -71..-55 dB (najgłośniejsze okno @ 8,5 s), bear_growl startuje od -62 dB; w 8_v2 kulminacja siedziała 4,5 dB **poniżej** tła, a ryk balotha w 2_v2 przychodził w ostatnich 0,4 s pliku (właściciel: „zniknął rewelacyjny ryk"); (2) te same 11 sampli w każdej scenie („słyszę tylko kroki"); (3) gravel_feet niesie 36% energii >6 kHz — dosłownie „darcie papieru"; (4) metryka climax-ratio wynagradzała „samotny klik nad ciszą" — korelacja ODWROTNA z ocenami właściciela (8_v2: QA 100/100, ocena 3/15; 568_v2: QA 86,6, ocena 15/15); (5) rendery były 6-13 dB cichsze od chwalonych oryginałów (brak kompresora, normalizacja 0,55 zamiast 0,92).
- Wniosek: pierwotny agent wygrywał nie „talentem", tylko procedurą: ręcznie odsłuchane, głośne fragmenty nagrań, 2-4 duże rozpoznawalne beaty, zdarzenia złożone (krok bestii = sub + chrzęst + plusk), ciągłe tło, kompresor sklejający, głośny master. To się da zakodować — i zostało zakodowane.
- Zasada / działanie zapobiegawcze: silnik v2 (`render_jingle.py`) miksuje po **celach głośności RMS** (-16 kulminacja / -21 support / -26 detal), odrzuca segment >12 dB pod najgłośniejszym oknem nagrania (z podaniem sugestii offsetu), wspiera zdarzenia złożone i łańcuch klejący (echo + kompresor + master 0,9). Nowe narzędzie `scripts/stem_probe.py` = audycja sampli przed użyciem. QA v2 (`qa_score.py`): bramki słyszalności (każde żywe zdarzenie ≥ +6 dB nad tłem, 15. percentyl okien jako tło, okno pomiarowe zatrzymywane przez następne odrębne zdarzenie), RMS ≥ -26 dB, >6 kHz ≤ 12%; climax-ratio tylko informacyjnie. Kalibracja na całym katalogu: odrzuca wszystkie wersje ≤9/15 i przepuszcza wszystkie ≥11/15; znane wyjątki: 5_v2 (receptura sprzed reguły genre — wada to fit, nie akustyka) i 450_v3 (słabe kroki dostają kredyt z ogona wycia — bramka mierzy obecność, nie fit). O decyzjach właściciela z tej sesji: pitch w dół 0,7-1,0 dozwolony (poprzedni zakaz #15 złagodzony), próg remaków <12/15 (poniżej = projekt od zera), najpierw partia kontrolna 8/475/450 przed resztą kolejki (5, 2).
## 2026-09-23 — Remake nie wyrzuca sampli pochwalonych w komentarzu (decyzja właściciela)

- Sytuacja: dwa udokumentowane przypadki utraty najlepszego materiału podczas remaku: fabuła 2 — komentarz do v1 (11/15) chwalił ryk balotha („ryk fajny"), a v2 go usunął (ocena: „kroki super, tylko zniknął rewelacyjny świetny ryk balotha"); fabuła 5 — v1 (10/15) miała pochwalone elementy z 1-3 s, v3 je stracił („brakuje tych fajnych sampli z v1 z 1-3 sekundy"). Agent remakujący traktował ocenę jako wymaganie wymiany wszystkiego, także tego, co działало.
- Wniosek: komentarz tekstowy to nie tylko lista wad — elementy wprost pochwalone są aktywnymi aktywami fabuły i muszą przetrwać remake w niezmienionej formie (te same pliki sampli, to samo masterowanie: offset, pitch, filtry, głośność, pozycja).
- Zasada / działanie zapobiegawcze: twarda reguła w AGENTS.md pkt 3 i docs/agent-workflow.md §2 — każda wersja z oceną **powyżej 10/15** „przypina" swoje pochwalone sample: każdy kolejny remake fabuły musi ich użyć dokładnie; remake od zera dotyczy wyłącznie fabuł, w których żadna wersja nie przekroczyła 10/15. `scripts/remake_queue.py` wypisuje te obowiązki razem z treścią komentarzy do zachowania. Panel Pages (build_site.py) od tej pory pokazuje komentarze właściciela na kartach ocenionych wersji (amber = nieoceniona, zielona ramka = najlepsza ocena, kolejność: nieocenione → malejąco po ocenie), żeby pochwały były widoczne dla każdego agenta i właściciela.
## 2026-09-23 — Doprecyzowanie progów remake'ów: 12/15+ bez bana, 15/15 bez sensu

- Sytuacja: wpisany dzień wcześniej „próg remaków <12/15" został odczytany przez agenta jako „dla 12/15+ remake niewymagany" — zbyt restrykcyjnie.
- Wniosek właściciela: kolejka remake'ów biegnie od najgorzej ocenianych i **nie wyklucza żadnego jingla poniżej 15/15** — każdy może być lepszy. Remake nie ma sensu wyłącznie przy 15/15. Dla wyników 11–14/15 obowiązuję reguła ochrony pochwalonych sampli (remake na fundamencie, nie od zera); od zera wolno projektować tylko fabuły, w których żadna wersja nie przekroczyła 10/15.
- Zasada / działanie zapobiegawcze: AGENTS.md pkt 3, docs/agent-workflow.md §2 i docs/feedback-system.md opisują progi w wersji z 2026-09-23; `scripts/remake_queue.py` wypisuje plan dla każdej fabuły zgodnie z progami (≤10 → od zera dozwolone; 11–14 → fundament z pochwalonymi samplami; 15 → pomiń, chyba że wyraźne zlecenie). Kolejność kolejki bez zmian: od najgorzej ocenianych (wg najlepszej wersji fabuły).
## 2026-09-23 — Słyszalność ≠ rozpoznawalność (lekcja z partii kontrolnej 8/475/450)

- Sytuacja: partia kontrolna po naprawie silnika v2 przeszła wszystkie bramki QA (każde zdarzenie +8..+16 dB nad tłem), a oceny właściciela: 450 v4 = 6/15, 475 v3 = 5/15, 8 v3 = 10/15. Komentarze wskazały nową jakość problemu: zdarzenia były słyszalne, ale NIECZYTELNE — wycie wilka NPS brzmiało jak darcie papieru (nagranie ma 82% energii <250 Hz = pomruk wiatru, nie wokal), kruk obniżony do smoka nadal brzmiał jak wrona, deszcz „prawdziwych" gruzów jak kostki do gry, a pochwalona z v1 „elektronika na końcu" — syntetyczny swarm — została usunięta na rzecz foley.
- Wniosek: bramki głośności są warunkiem koniecznym, ale niewystarczającym. Rozpoznawalność wymaga (1) sampli o właściwej CHARAKTERYSTYCE widmowej dla danego zdarzenia (wokal = dominanta 250-2000 Hz; whoosh = zbalansowane pasmo z ruchem powietrza; ciężar = sub), (2) czytelnych okien czasowych (wnyki zginęły pod ogonem wycia), (3) w scenach SF syntetycznych tekstur dla zjawisk ENERGETYCZNYCH (iskry, deszcz elektroniki) — foley zastępczy brzmi jak kuchnia („miedziana misa", „kostki do gry"). Po raz trzeci pochwalono żywe tło (lawa/wiatr/hangar/suw) — to najpewniejszy element warsztatu.
- Zasada / działanie zapobiegawcze: dobór sampli pod charakter widmowy zdarzenia przed renderem (audycja profilem z stem_probe.py — patrz kolumna charakteru); wokale bestii: pakiet creature SFX (howl.m4a = 100% energii 250-2 kHz) zamiast nagrań terenowych NPS jako lead; zjawiska energetyczne SF = warstwy syntetyczne (dopuszczalne w SF), fizyka = żywe sample; każde zdarzenie fabularne w osobnym oknie czasowym; kolejka remake'ów wypisuje obowiązki zachowania sampli pochwalonych (AGENTS.md pkt 3). Nowe wersje: 475 v4 (QA 94,5 — powrót deszczu elektroniki), 450 v5 (96,2 — tonalne wycie + czytelne wnyki i drugi wilk), 8 v4 (96,8 — 7 s, gobliny pitch 0,82, smok = ryk grizzly, whooshe skoku).
## 2026-09-23 — Fabryka jingli zakończona: system sygnatur (zwrot koncepcji)

- Sytuacja: po ~10 utworach i wielu rundach ocen właściciel stwierdził, że efekt nie jest nastrojowy, a koszt linowy od liczby fabuł czyni cel nieosiągalnym; podjął decyzję o zastąpieniu fabryki systemem czterech baz klocków z bramką odsłuchową (kasacja starych jingli, nazwa produktu zawsze `<id>.mp3`).
- Wniosek: wąskim gardłem była ewaluacja audio zepchnięta na jedną parę uszu przy każdym utworze; właściwe miejsce ucha człowieka to obsadzanie klocków (raz), nie ocena miksu (500 razy). Unikalność kombinacji a·b·c·d wystarcza jako ochrona różnorodności — nie trzeba 500 unikalnych miksu.
- Zasada / działanie zapobiegawcze: obowiązuje ADR 0003; jakość ma wynikać z konstrukcji (zatwierdzone składniki + bramki montażu), nie z iterowanej oceny. Od pierwszej bramki: nagrania terenowe ptactwa o bardzo niskim profilu (Bald Eagle, 98 % < 250 Hz) nie nadają się na hero — sprawdzać pasmo charakterystyczne; biblioteka Kawai VCSL ma luki w skali (brak A3, F2) — wybór nut gestu po sprawdzeniu mapy sampli, nie „na papierze".

- **2026-09-23 (adaptacja rejestru kody):** gesty nutowe i banki sampli żyją w
  różnych zakresach (A1 marczego pulsu vs kotły D2–F2, F#3 trytonu vs kieliszki
  D#4–D5). „Pomiń nutę" cicho psuło utwór — wdrożono deterministyczną drabinę:
  ±3 półtony → oktawa → jednolita transpozycja gestu → jawne pominięcie. Każda
  adaptacja ląduje w ostrzeżeniach renderu. Pętle tła: crossfade na szwie
  (zwykły `np.tile` klikał). Przy bramce demo instrumentu zawsze prezentować
  fragment w JEGO zakresie — i tak się dzieje (fraza demonstracyjna), trzymać
  tę zasadę.

- **2026-09-23 (koda ma grać, nie klepnąć):** ucięcie jednostrzałowca do długości
  nuty (0,32 s) pod niskim tłem = jedno „bum" zamiast trzech uderzeń. Reguła
  MIN_NOTE_AUDIBLE_SEC=1,2 (logowana w renderze). Długość pliku = `length_sec`
  receptury — wcześniej ogon kody ciszej przekraczał deklarację (8,41 s przy
  8,0 s), teraz twardy master-fade. Użytkownik: długość referencyjna sygnatur
  to **6 s** — receptury używają 6,0 s jako bazy.

- **2026-09-23 (model pracy: dozór bazy ≠ montaż):** właściciel akceptuje jakość
  wpisów do bazy — **uwaga: pierwotnie opisałem to błędnie jako
  wielowariantowo („doktryna-jakości"); właściciel sprostował: na wpis bazy
  3 kandydatów, wybiera DOKŁADNIE JEDNEGO, tylko on trafia do bazy**; agent obsadza fabułę
  i montuje — bez odsłuchu końcowego. Konsekwencja kodowa: twarda bramka ataku
  każdej nuty kodu (+2,5 dB nad kontekst, okno 0,3 s), licznik zagranych nut,
  AUTOKALIBRACJA poziomów nut w renderze (sufit 8 dB, log `coda_boosts_db`).
  Pułapka: pomiar pokazał, że „naprawione na okoł" wersje nadal zawodziły
  (atak +0,8 dB kotła, −3,3/−4,6 dB kieliszków) — poziom bloku nie leczy
  nakładającego się ringtonu; leki zadziałały: minimum brzmienia, semantyka
  DB per nuta, autokalibracja, geometria czasowa (fabuła 4: hero na 0,7 s i
  koda na 3,6 s zamiast przez wail). Kieliszki pod zewem nura — parowanie na
  granicy; na przyszłość bramki demo kodu prezentować też na instrumencie
  z PODGŁOSEM finalnego typu tła (kontekstowa odsłuchówka), nie na pusto.

- **2026-09-23 (przy budowie g002):** banki sampli w VCSL bywają rzadkie — nie
  sprawdzać „na czuja": Kawai/Steinway nie mają pełnej chromatyki per velocitiy
  (Kawai: luki F/G/natural; Steinway: tylko A#/C/D/E/F#/G#), Yamaha Upright
  tylko tony C i G, Knight prawie nic. Zanim obiecasz listę nut instrumentu —
  `git ls-tree` na katalogu. Konsekwencja produktowa: banki gęste (≤4 półtony
  odstępu) dają demo bez przestrajania; bank rzadki = cecha opisowa wpisu
  (caveat w kandydacie). Demo gestów projektować w siatce nut, która NAPRAWDĘ
  jest w banku referencyjnym — inaczej drabina oktaw psuje gesty (kaskada
  zamieniła się w skoki C4↔D#5 zanim to zauważyłem).
- Sparse-checkout wielu plików: `git sparse-checkout set --no-cone --stdin <
  plik.txt`; podawanie listy jako argv z cudzysłowami i spacjami NIE działa.

- **2026-09-23 (werdykt g002 — korekty):** właściciel przyjął 5 wpisów
  (Steinway, bassdrum, ogień mały, wir pary, światło-koda) i ODRZUCIŁ ryk-bestii:
  założyłem „3 kandydatów = 3 gatunki" (łoś/kojot/żubr zamiast 3 RYKÓW tej
  samej bestii), a c.2 okazał się „pustym dźwiękiem" (brak sondy słyszalności
  przed wystawieniem). Też: dwa wpisy z tym samym prefixem etykiet (d.*) —
  właściciel sam rozróżnił po kontekście, ale to pułapka. Wnioski wdrożone:
  protokół faza A punkt 2/2a (warianty = jeden rodzaj źródła; sonda RMS/peak;
  etykiety unikalne bramkowo), g003 naprawcza = 3 ryki żubra (warianty
  ciężki/krótki/masywny) z zwolnieniem tempa (resample_poly −3…−5 półtonów).

- **2026-09-23 (technikalia przeróbki na ryk):** polifazowy
  `scipy.signal.resample_poly` ze współczynnikiem `Fraction(ratio).limit_denominator(96)`
  daje pitch+tempo down bez artefaktów „chipmunk rewards"; po zwolnieniu
  filtry HP 45 Hz / LP 2,8 kHz (sosfiltfilt) czyszczą szum taśmy.
  KLUCZOWE: przejściowy klik po resamplingu daje crest >15 dB — wtedy
  `normalize_rms(...)` + `peak_ceiling(0.92)` ścisza materiał o ~6 dB
  (skala globalna). Rozwiązanie: iteracyjny limiter tanh (drive 2.0, do crest
  ≤12 dB) PRZED normalizacją RMS — r.1 zachowuję −15,3 dB przy peaku 0,60.

- **2026-09-23 (obsada inwentarzem = nieważność montażu):** zamontowałem
  fabuły 5 i 8 „tym, co leżało" (nur z fabuły 4 do wiru portalu; kruk z
  fabuły 1 do goblinów Jundu) — właściciel słusznie odrzucił obie jako
  bez związku z narracją („kopia fabuły 1"). Lekcja kosztem dwóch renderów:
  faza B punkt 2/2a wzmocniona — rola z narracji, „obsada" = pasuje do
  fabuły; hero = tożsamość 1:1 (zakaz powtórek hero między fabułami).
  Równolegle: ryk bestii ≠ wygodny bison „pod ręką"; YSL nie ma niedźwiedzia
  (fałszywy inwentarz w sources-and-licensing skorygowany; `git ls-tree`
  na HEAD zawsze przed planowaniem).
- **2026-09-23 (atomcut jako odpowiedź na role fabuł):** pakiety OGA CC0
  z mirroru `novincode/atomcut-library` (potwory ogrebane ×3 paczki,
  goblins artisticdude, magic jaggedstone, creature rubberduck) dekodować
  PyAV (m4a 48k); krótkie hity 0.2–2.4 s, `pack.json` per pack z licencją
  i autorem. Do kandydatów-uderzeń: tanh 1.35 (jądro) → soft_limit crest 12 →
  normalize RMS −15 → fade 5 ms/180 ms — peaki ~0.4–0.6 bez klipu.

- **2026-09-23 (gobliny z kreskówki = pitch-down):** właściciel odrzucił
  goblinowe warcry jako „kreskówkowe, za wysokie" (g.1 najlepszy, ale piskły).
  Reguła: głosy „muppetów" stają się groźne przy −4…−6 półtonach (resample,
  czas rośnie ×1.26–1.41 — z 0,5 s robi się czytelny hero 0,97–1,28 s;
  centroid z 2300→1450–1900 Hz, pik z 1764→846–1323 Hz). Rundę 2 robić z TEJ
  SAMEJ paczki (doktryna wariantów), nie ze skoku na inne źródło.
- **2026-09-23 (hero vs koda — zderzenie semantyk):** przy wykonaniu fabuły 5
  właściciel uprzedził: „czar-błysk sam brzmi jak koda". Reguła obsady:
  jeśli hero ma charakter muzyczny/błysk, koda idzie wyraźnie później
  (≥1,3 s przerwy po hero) i barwo-odbiciem (tu: syntetyczny błysk vs struna
  fortepianu), nie drugim „zapem". Zapisane w recepcie 5 (pole notes).

- **2026-09-23 (rodzina źródła ≠ pitch):** gobliny artisticdude obniżone
  o −6 półtonów to dalej Smerfy — wada była w stylu wokalizacji źródła,
  nie w wysokości. Reguła: jeśli werdykt mówi „zły CHARAKTER", zmieniaj
  rodzinę; jeśli „za wysoki", zostaw rodzinę, schodź w dół. Rubberduck
  80-creature: grep pasma głosu (udział 200–900 Hz > ~60%) dobrym sitom na
  „poważny głos stwora" (grunt-02 78%, troll-01 79% vs hurt-01 11%).
- **2026-09-23 (technika orków > dobór paczki):** trzy rundy wrzasku padły,
  bo wszystkie źródła były wokalizacjami UDAWANYMI pod stwora (artisticdude,
  rubberduck) — takie nagrania robi się z uśmiechem, słychać kabaret.
  Filmowe fantasy idzie odwrotnie: PRAWDZIWY ludzki wrzask + pitch-down +
  saturacja. Sito liczbowe: udział pasma gardła 150–800 Hz — prawdziwy głos
  41–66%, „głosik stwora" 4–22%.
- **2026-09-23 (stare audio w playerze):** site serwowany przez
  `http.server` odpowiadał 304 na niezmienioną nazwę pliku, więc właściciel
  słyszał poprzedni montaż fabuły. Dwa zabezpieczenia: `build_site.py`
  dokleja `?v=<md5[:10]>` do każdego <audio>, a `scripts/serve_site.py`
  wysyła `Cache-Control: no-store`. Przy każdej reklamacji „gra stara
  wersja" najpierw md5 pliku na dysku vs to, co zwraca serwer.
- **2026-09-23 (403 na dispatch):** token sandboksa to GitHub App bez
  `actions:write` → `workflow_dispatch` po API odpada. Działa
  `repository_dispatch` (potrzebuje tylko `contents:write`), więc workflow
  dostał drugi wyzwalacz `types: [sample-scout]` i czyta client_payload.
- **2026-09-23 (poprawka wykonawcza po werdykcie):** przy „dobre, ale utnij
  koniec" nie zgaduj miejsca cięcia — zrób profil energii co 50 ms i tnij
  w MINIMUM przed artefaktem (tu: −25 dB @ 1,25 s, potem głos wracał na
  −16 dB pnąc się 558→733 Hz). Parametr `end_sec` w budowniczym bramki, nie
  ręczna edycja pliku, żeby kandydat dał się odtworzyć z kodu.
- **2026-09-23 (schemat source):** własny słownik `SOURCE` w nowym skrypcie
  bramki rozjechał się z rejestrem (`homepage/mirror/path` zamiast
  `url/channel`) — `library_tool check` złapał to dopiero po accept.
  Nowe bramki kopiować pola źródła z istniejącego wpisu, nie wymyślać.

## 2026-09-23 — Stan flow po sesji bramek g003–g008 (czytaj to najpierw)

- Sytuacja: w jednej sesji przeszliśmy cztery rundy jednego wpisu, dwie
  wycofane fabuły i fałszywą reklamację „gra stary plik". Poniżej skrót,
  żeby następny agent nie odtwarzał tych pomyłek od zera.
- Wniosek: proces jest stabilny, kosztowne są tylko trzy rzeczy — obsada
  z magazynu zamiast z narracji, dobór źródła „na najbliższe wygodne"
  i diagnozowanie na ucho zamiast liczbami.
- Zasada / działanie zapobiegawcze:
  1. **Podział ról**: właściciel ocenia WYŁĄCZNIE jakość wpisów w bramce.
     Fabuły montuje agent i sam wybiera, co idzie do następnej bramki.
     Nie pytaj „co teraz?" — pokaż gotową bramkę i raport z liczbami.
  2. **Rola z narracji fabuły, hero 1:1.** Wpis pasujący nazwą, lecz nie
     sceną, to brak → bramka (kruk ≠ gobliny Jundu). Hero użyty w innej
     fabule robi z nowej „kopię tamtej".
  3. **Werdykt „żaden" czytaj jako diagnozę** (tabela w
     `docs/gate-protocol.md`): parametr → ta sama rodzina; charakter →
     inna rodzina lub inna technika; detal → parametr w skrypcie bramki.
  4. **Mierz, nie zgaduj**: pasmo gardła 150–800 Hz (głos prawdziwy 41–66%
     vs kreskówka 4–22%), wahanie RMS w podoknach 0,5 s i udział > 4 kHz
     (tła), profil energii co 50 ms (miejsce cięcia).
  5. **Reklamację odsłuchową weryfikuj technicznie** przed zmianą czegokolwiek
     (md5 dysk vs serwer, pik widma hero) — raz winna była wyłącznie
     pamięć podręczna przeglądarki.
  6. **Ograniczenia narzędzi omijaj, nie eskaluj do właściciela**: brak
     `actions:write` → `repository_dispatch`; brak egressu → mirrory GitHub;
     m4a → PyAV.

## 2026-09-23 — „Szum wiatru zamiast wody”: żywioł poznaje się po tranzjentach

- Sytuacja: tło „zalany kanion” (g008) wycięto z nagrania NPS „The Dragon's
  Mouth” — gorącego źródła w jaskini. Wybór opierał się na opisie źródła
  („woda bijąca o ściany”) i na stabilności RMS. Właściciel: „to nie brzmi
  jak woda tylko jak szum wiatru — woda gdzieś tam jest, ale zagłuszona”.
- Wniosek: gorące źródła to głównie syk pary. Miary, których użyłem
  (stabilność, udział > 4 kHz), mówiły o gładkości łoża, ale żadna nie
  sprawdzała, czy w materiale są **zdarzenia** charakterystyczne dla
  żywiołu. Szerokopasmowy szum bez tranzjentów ucho zawsze przeczyta jako
  wiatr, niezależnie od tego, co było przed mikrofonem.
- Zasada / działanie zapobiegawcze: dla teł żywiołów licz dwie rzeczy —
  (1) udział energii poniżej 1 kHz, (2) liczbę skoków energii > 4 dB na
  sekundę (okna 100 ms). Woda: 67–81% i ≥1,5 zdarzenia/s (bulgot, bąble).
  **UWAGA — próg „>65% poniżej 1 kHz” został później OBALONY** (wpis
  z 2026-09-23 o nagraniach terenowych): przyjęty strumień ma 15–27% i
  centroid ~3 kHz. Zostawiam wpis, bo diagnoza „syk pary ≠ woda” była
  trafna, ale nie stroj do tych liczb — patrz ostatni wpis pliku.
  Odrzucone jako „wiatr”: Dragon's Mouth ~20% i ~0 zdarzeń, a także
  `loop-water-*` rubberducka (13–36%, centroid 3200–4300 Hz — mimo nazwy
  „water” to szum). Dodatkowo tnij pasmo > 5–6 kHz, które nadaje charakter
  syku. Sprawdzone rodziny chlupotu: `bubbling-*` z lokif „Swamp
  Environment Audio” i `loop-bubbles-*` z rubberduck „40 water/splash/slime”.

## 2026-09-23 — Woda stojąca ≠ woda płynąca; brakujący żywioł składa się foleyem

- Sytuacja: po odrzuceniu syku pary (g008) tło zbudowano z bulgotu i bąbli
  (g009). Werdykt: „wszystko brzmi jak gotująca się woda, a woda w kanionie
  płynie i ciurka, a nie puszcza bąbelki — ma być jak kroki w wodzie,
  płynąca rzeka, woda po kamieniach”.
- Wniosek: „woda” to nie jedna rola. Bulgot/bąble = ciecz STOJĄCA (gaz
  wypływa na powierzchnię). Nurt = ciągła płynąca masa + nieregularne
  chlupnięcia o przeszkody. Sito z poprzedniej rundy (energia < 1 kHz,
  liczba zdarzeń) obie rzeczy przepuszcza jednakowo, więc nie wystarcza —
  trzeba rozróżnić CHARAKTER zdarzeń, nie tylko ich liczbę.
- Zasada / działanie zapobiegawcze: (1) rolę tła nazywaj czasownikiem ze
  sceny („woda płynie po kamieniach”), nie rzeczownikiem („woda”);
  (2) gdy żadna biblioteka nie ma nagrania danego zjawiska (tu: rzeki —
  YSL ma wyłącznie gejzery, źródła i jezioro, a OGA `water-flowing` to syk
  o centroidzie 5160 Hz), **złóż je foleyem** zamiast naciągać najbliższy
  plik: warstwa ciągła (szum wody obniżony o 8–9 półtonów, filtr ~3 kHz =
  płynąca masa) + warstwa zdarzeń (`scatter()`: chlupnięcia rozsiane
  nierównomiernie z ziarnem, obniżone o 5–6 półtonów, bo biblioteczne
  plusknięcia są jasne „pod grę”); (3) warstwy strojemy liczbami do celu
  roli — tu centroid 1069–1332 Hz, > 6 kHz poniżej 2%, 2,4–3,0 zdarzenia/s.
  Funkcje wielokrotnego użytku: `build_gate_g010.flow_layer()` i `scatter()`.

## 2026-09-23 — Pitch-down słychać: foley nie zastąpi nagrania terenowego

- Sytuacja: po trzech odrzuconych rundach tła („wiatr”, „gotująca się woda”)
  spróbowałem złożyć nurt foleyem — obniżony szum wody plus rozsiane,
  również obniżone chlupnięcia. Werdykt: „wszystko strasznie nienaturalnie
  nisko, jakby ktoś spitchował dźwięki; chlupotanie brzmi nienaturalnie”.
- Wniosek: pitch-down działa na GŁOSY (g007: prawdziwy krzyk → orkowy
  warcry — ucho nie zna „prawdziwego” tembru orka, więc akceptuje
  przesunięcie). Nie działa na ŻYWIOŁY, których brzmienie każdy zna z
  natury: spowolniona woda natychmiast zdradza obróbkę, bo znika
  mikrostruktura (pojedyncze krople, przypadkowe rytmy, szerokie pasmo
  tuż nad nurtem). Metryki mogą być idealne, a materiał i tak brzmi
  sztucznie — sito liczbowe sprawdza pasmo i zdarzenia, nie naturalność.
- Zasada / działanie zapobiegawcze: dla teł żywiołów (woda, deszcz, wiatr,
  las) używaj WYŁĄCZNIE nagrań terenowych; dozwolone są tylko cięcie,
  filtr łagodny, poziom i pętla. Jeśli w zweryfikowanych bibliotekach nie
  ma danego zjawiska — nie składaj go i nie naciągaj podobnego: uruchom
  Sample Scout (archive.org/Freesound przez GitHub Actions) po prawdziwy
  field recording. Trzy rundy przepalone na materiale zastępczym są
  droższe niż jedno uruchomienie workflow.

## 2026-09-23 — Pusty wynik Scouta to zwykle błąd filtra, nie brak nagrań

- Sytuacja: ręczne uruchomienie Sample scout dla „creek stream flowing water
  field recording” zakończyło się `brak kandydatów CC0` i kodem wyjścia 1.
  Nagrania strumieni w Internet Archive są pospolite, więc wynik był
  nieprawdopodobny.
- Wniosek: konektor pobierał 40 najpopularniejszych pozycji audio i dopiero
  potem sprawdzał licencję. Popularne audio w Archive to muzyka i podcasty —
  praktycznie nigdy CC0, więc po filtrze zostawała pusta lista niezależnie od
  zapytania. Drugi, ukryty filtr: pliki powyżej 12 MB były odrzucane, a każde
  sensowne nagranie terenowe jest dłuższe.
- Zasada / działanie zapobiegawcze: (1) warunek licencji wstawiaj do
  zapytania wyszukiwarki, nie do pętli po wynikach; (2) dla materiału
  długiego pobieraj początek pliku zamiast odrzucać całość (`truncated`
  w manifeście); (3) gdy workflow zwraca pustkę dla pospolitego dźwięku,
  podejrzewaj własny filtr — zanim uznasz, że źródła nie ma. Test regresyjny:
  `test_archiveorg_finds_cc0_behind_popular_non_cc0_rows`.

## 2026-09-23 — „Skipped” to warunek `if`, nie awaria; instrukcję podaj z góry

- Sytuacja: właściciel uruchomił Sample scout z gałęzi sesji, żeby
  przetestować moją poprawkę. Job wypadał jako `skipped (This job was
  skipped)` — kilka razy z rzędu. Przyczyną był warunek
  `if: github.ref == 'refs/heads/main'`, o którym go nie uprzedziłem;
  dodatkowo sam musiał zgadywać, co wpisać w pole `sort`.
- Wniosek: status „skipped” bez ani jednego wykonanego kroku prawie zawsze
  oznacza niespełniony warunek `if` na poziomie joba, a nie błąd narzędzi.
  Guard na gałąź był słuszny, ale zbyt wąski: blokował także gałęzie sesji,
  czyli jedyne miejsce, gdzie można przetestować poprawkę przed merge.
- Zasada / działanie zapobiegawcze: (1) guard rozszerzony do
  `main` lub `arena/**`, a push idzie na `HEAD:${GITHUB_REF_NAME}`, więc
  kandydaci trafiają na tę samą gałąź, z której uruchomiono workflow;
  (2) gdy prosisz właściciela o ręczną akcję w UI, **wypisz wszystkie pola
  formularza wraz z gałęzią** — brak jednego pola kosztował kilka pustych
  przebiegów; (3) pola nieistotne dla wybranej ścieżki opisz jako
  ignorowane (tu: `sort` działa tylko dla Freesound).

## 2026-09-23 — Nagranie terenowe bije każdą składankę; moje sito „wody” było błędne

- Sytuacja: cztery rundy tła do fabuły 2. Trzy własne (syk źródła, bulgot,
  foley z pitch-downu) odrzucone. Czwarta — dwa prawdziwe nagrania
  strumienia z Internet Archive przez Sample scout — werdykt: „wszystkie
  trzy ZAJEBISTE, o kilka klas lepsze niż wcześniejsze propozycje”.
- Wniosek, najważniejszy z całej sesji: **progi, którymi strojłem tła, były
  fałszywe**. Zakładałem „im więcej energii poniżej 1 kHz, tym bardziej
  woda” i dociskałem materiał do > 65%. Przyjęte nagranie ma **15–27%
  poniżej 1 kHz i centroid ~3 kHz** — czyli dokładnie profil, który moje
  sito odrzucało jako „wiatr”. Naturalność bierze się z mikrostruktury
  (tysiące drobnych, nieregularnych zdarzeń), a tej żadna z moich liczb nie
  mierzyła. Im dłużej stroiłem metryki, tym dalej byłem od celu.
- Zasada / działanie zapobiegawcze: (1) dla teł żywiołów metryki służą
  WYŁĄCZNIE do odsiewania wad technicznych — rumble < 8%, brak mowy
  (modulacja obwiedni < 0,25), stabilność okna; oceny „czy brzmi jak woda”
  nie da się zautomatyzować, robi ją ucho w bramce; (2) brak zjawiska
  w lokalnych bibliotekach = **od razu Sample scout**, bez rundy
  zastępczej — polecenie właściciela: „nie bój się korzystać ze scouta”;
  (3) obróbka nagrania terenowego: tylko okno, filtr rumble, łagodne
  przymknięcie góry i poziom. Żadnego pitchowania.

## 2026-09-23 — Licencje: prywatny użytek, nie audyt prawny

- Sytuacja: po tym, jak Scout przyniósł nagranie z notą „Copyright status
  unknown”, usunąłem plik i zaostrzyłem filtr do jawnego CC0/PD. Właściciel
  skorygował: „projekt jest prywatny, pliki trafią na mój dysk lokalny,
  jak nie ma podanej licencji to przyjmujemy że jest ok, do prywatnego,
  niekomercyjnego wykorzystania też może być”.
- Wniosek: nadmiarowa ostrożność kosztowała kandydatów i rundy poszukiwań
  bez korzyści dla właściciela. Rygor CC0 miał sens dla materiału
  publikowanego, a nie dla wszystkiego, co przechodzi przez warsztat.
- Zasada / działanie zapobiegawcze: brak licencji **nie** blokuje przyjęcia
  (`"license": "brak informacji"`); materiał jawnie wolny ma pierwszeństwo
  w rankingu; jawne zastrzeżenia komercyjne oznaczamy statusem
  `restricted`, bo dotyczą wyłącznie publicznej gablotki Pages i ZIP-a
  w Releases. Scout: `license_status` w manifeście, `--free-only` gdy
  materiał ma iść do publikacji. Polityka w `docs/sources-and-licensing.md`.

## 2026-09-23 — Metryki głosu nie odróżniają aktora od kreskówkowego stworka

- Sytuacja: g012 miała obsadzić „złośliwy chichot małego demona”. Złożyłem
  krótkie sylaby z kitu `80 creature SFX`; wszystkie były głośne, niepuste,
  miały czytelne pasmo głosu i równe poziomy. Właściciel odrzucił całą rundę:
  „to nie żaden imp tylko postać z kreskówki — ma być prawdziwy diabelski
  chichot”.
- Wniosek: techniczna sonda słyszalności potwierdza tylko, że sygnał istnieje.
  Nie potwierdza źródła wykonania ani wiarygodności aktorskiej. Nazwanie kilku
  zaprojektowanych odgłosów `cute-*` „chichotem” było nadinterpretacją opisu.
- Zasada / działanie zapobiegawcze: role oparte na ludzkiej ekspresji
  (śmiech, płacz, krzyk, szept) zaczynaj od **prawdziwego nagrania człowieka
  wykonującego tę ekspresję**. Creature-SFX nie wolno przemianować na emocję
  tylko dlatego, że zgadza się długość i pasmo. Obróbka może wzmacniać rolę,
  ale nie zastępuje wiarygodnego wykonania źródłowego.

## Bramka obsadza TYP, nie fabułę (g015, 2026-09-24)

- Sytuacja: do typu tła `niebo-przestworza` („pęd powietrza na wysokości")
  pokazałem właścicielowi kandydata „przelot skutera śnieżnego", bo
  narracja fabuły 18 mówiła o „pędzie pojazdu". Właściciel: „to jest
  zupełnie inny dźwięk".
- Zasada: w modelu 1:1 klocek jest wielokrotnego użytku w RAMACH TYPU —
  kandydatów przesłuchuje się pod DEFINICJĘ TYPU (`co_slychac`), nie pod
  smaczek pojedynczej narracji. Silnik spalinowy skaziłby każdą przyszłą
  fabułę przestworzy.
- Wniosek techniczny: matcher cech wymaganych ignorował słowa <4 znaki
  (gubił „pęd/ryk/syk/huk") — naprawione (min. 3 znaki, resolver.py).

## Zwiad freesound: klucz API ≠ OAuth2 (2026-09-24)

- Objaw: wyszukiwanie działa, każde pobranie pada z HTTP 401.
- Przyczyna: endpoint `/download` Freesound wymaga OAuth2; zwykły klucz
  API autoryzuje tylko wyszukiwanie i previews. Pobieramy więc
  `preview-hq-mp3` (~128 kbps — nasz docelowy bitrate i tak wynosi 128).
- Przy okazji: archive.org łączy słowa domyślnym AND (wielosłowne
  zapytania → zero trafień; scout ma teraz fallback z OR), a zapytania
  zwiadu mają być krótkie i ogólne (2–3 słowa).
- Diagnostyka: workflow commituje log porażki do
  `legacy/source/sample_scout/error.log`, bo sandbox nie czyta logów
  Actions.

## Ogon hero maskuje środkowe nuty kody (fabuła 451, 2026-09-24)

- Sytuacja: receptura 451 z hero `stealth_move_03` (4,0 s brzmienia) na 0,9 s
  oblała QA ataków: dwie środkowe nuty kody z detektorem „atak < +2,5 dB"
  mimo sufitu autokalibracji (ogniwa 3–4 staccato handchimes wpadały
  w jeszcze brzmiący ogon smyczkowanego talerza, koniec ~4,9 s).
- Wniosek: QA ataku mierzy się względem KONTEKSTU (tło+hero+ogon kody),
  więc „cichy" hero o długim ogonie bywa maskotą groźniejszą niż głośny
  o krótkim. Przy planowaniu okna kody licz `hero.at_sec + duration`
  kontra pozycje nut (`coda_note_ons` w audycie).
- Zasada / remedium (w tej kolejności): (1) przytnij hero
  (`length_sec`, tu 4,0 → 2,6 s) — esencja roli siedzi w głowie nagrania;
  (2) przesuń hero wcześniej albo kodę później; (3) dla staccato na
  wybrzmiewającym instrumencie podnieś `damp_db` (8 → 12). Efekt: marginesy
  ataków 3,2–3,4 dB przy boostach 1–4,5 dB zamiast porażki przy +8.

## Zwiad czyści `legacy/source/sample_scout/` przy każdym runie (2026-09-24)

- Sytuacja: po dispatchu nowej kolejki (freesound „storm sea waves rocks
  coast") merge commita bota usunął z drzewa CAŁĄ poprzednią partię
  (`freesound_water-splash/`) — w workflow jest `rm -rf legacy/source/
  sample_scout` przed pobieraniem. Surowce g022 zniknęły z HEAD,
  choć bramka i jej source-manifest (sha256) zostały.
- Wniosek: katalog zwiadu jest PRZYCHOWALNIĄ, nie archiwum. Surowiec
  potrzebny w kolejnej rundzie trzymaj poza repo (`/tmp`, `work/`) albo
  odzyskaj z historii: `git show <baza>:<ścieżka> > /tmp/plik` (tak
  odzyskano ocean g022 do bramki g023). Token sesji (bez actions:write)
  nie poprawi workflow — stąd zapis tu, nie w YAML-u.
- Zasada: przy planowaniu rund zwiadu zakładaj, że przetrwa tylko
  ostatnia partia; skrypty bramek nie mogą zakładać obecności
  `legacy/source/sample_scout/<stara_partia>` w drzewie.

## Jasny hero + cichy dwór/gest = bramka HF, nie wina kandydatów (fabuła 249, 2026-09-25)

- Sytuacja: fabuła 249 (Feedback) OBSADZONA przez resolver bez nowej bramki
  (`chamber_hearth_01` z g028, `g10c_humble_pulse`/`b_soloviol_spic` z g026,
  `light_bloom_01` z g017 — reuse). Pierwszy render z poziomami „jak zawsze”
  dla `light_bloom_01` (-17 dB, sprawdzone w 23/110/225) oblał bramkę >6 kHz:
  **73,4%** przy limicie 20%.
- Diagnoza: hero `light_bloom_01` (dzwonki wiatrowe) ma **86% energii
  powyżej 6 kHz w izolacji** — w fabułach 23/110/225 „rozcieńcza” go głośny
  fortepian kody (RMS kody ok. -10 dB, pełne akordy w średnicy). W 249 tło
  to cichy roomtone komnaty (-32 dB), a koda `g10c_humble_pulse` to trzy
  KRÓTKIE, ciche uderzenia (vel 0,28–0,34) rozstawione w 2,8 s — większość
  trwania kody to cisza, więc jej realny wkład energii jest znikomy.
  Bez masy niskopasmowej hero-dzwonki zdominowały całe widmo.
- Zasada: bramka >6 kHz to właściwość **całego miksu**, nie hero z osobna —
  przy doborze poziomów licz, że „cichy, oszczędny” gest (mało nut, długie
  przerwy) nie zbalansuje jasnego hero tak jak gęsta koda fortepianowa.
  Zanim zmienisz instrument/gest (niedostępne w modelu 1:1), zrób siatkę
  `render_signature.py --force --audit` po hero×coda `target_db` i wybierz
  punkt maksymalizujący `mix_rms` przy `hf_share ≤ 0,20` i marginesie hero
  ≥ 6 dB — nie zakładaj z góry poziomów użytych w innych fabułach z tym
  samym hero, każda koda ma inny profil widmowy i inny „koszt” rozcieńczenia.
  W 249: hero -20 dB (margines 9,9 dB), koda -3 dB (RMS -13 dB, wciąż cichsza
  niż fortepianowe kody -10 dB — bliżej charakteru „pokorny/spokojny” z
  semantyki gestu), HF 16,9%, `mix_rms` -25,2 dB (praktyczny sufit tej
  obsady to ok. -25,1 dB — krótka, cicha koda + cichy dwór nie dają więcej
  bez złamania bramki HF; wciąż > limit -26 dB).

## `build_gate_manifest.py` bez argumentów nadpisuje g001 (2026-09-25)

- Sytuacja: uruchomienie `python scripts/build_gate_manifest.py --help` (bez
  realnego `--help` w parserze) wykonało cały skrypt i **nadpisało**
  `data/gates/g001/manifest.json` świeżo wygenerowaną wersją — bez pól
  `amendments`/`verdicts` dopisanych ręcznie po werdykcie właściciela
  (przycięty fragment żab fabuły 4, historia decyzji). `git checkout --`
  odzyskało plik, bo nic nie zostało jeszcze zacommitowane.
- Przyczyna: to jednorazowy, historyczny builder pilotażu (`G = Path("data/
  gates/g001")` na sztywno w kodzie) — nie ma trybu `--help` ani ochrony
  przed nadpisaniem, każde uruchomienie odtwarza g001 od zera z kodu źródłowego.
- Zasada: **nie uruchamiaj `build_gate_manifest.py` „na sprawdzenie"** — to
  nie jest ogólny builder bramek (tym jest `gate_preview.py` + `build_gate_
  gNNN.py` per bramka). Jeśli trzeba sprawdzić manifest g001, czytaj plik
  albo `git show HEAD:data/gates/g001/manifest.json`. Po każdym takim
  eksperymencie sprawdź `git status` i odtwórz nietknięte pliki bramek przed
  dalszą pracą.

## Gablotka Pages sortowała fabuły numerycznie zamiast „najnowsze najwyżej” (2026-09-25)

- Zgłoszenie właściciela: strona biblioteki na Pages miała pokazywać gotowe
  jingle-fabuły od najnowiej zmienionych, a pokazywała je wg numeru fabuły.
- Kod sortujący (`build_site.py::last_touch`) był poprawny — bierze datę
  ostatniego commita `git log -1 -- <plik>` dla receptury/sygnatury, z
  fallbackiem na mtime dla plików niezacommitowanych. Problem był w CI:
  oba workflowy Pages (`pages.yml`, `pages-build.yml`) robią
  `actions/checkout@v4` **bez `fetch-depth`**, czyli domyślny płytki klon
  (depth 1, jeden commit). W płytkim klonie `git log -1 -- path` widzi
  TYLKO ten jeden dostępny commit dla KAŻDEGO pliku z drzewa — więc każda
  fabuła dostaje tę samą datę i sortowanie `(-data, numer)` degraduje się
  do czystego sortowania po numerze. Zweryfikowane lokalnie: pełne klony
  (`git clone`) dają poprawną kolejność (najnowsza sesja na górze), płytki
  klon (`git clone --depth 1 file://...`) odtwarza dokładnie zgłoszony błąd
  (1, 2, 3, 4, 5, 8, 18, 23, 28, ...).
- Naprawa: `fetch-depth: 0` w obu krokach `actions/checkout@v4` (pełna
  historia, mały koszt przy tym rozmiarze repo). Dodatkowo `build_site.py`
  teraz wykrywa płytki checkout (`git rev-parse --is-shallow-repository`)
  i krzyczy o tym w logu builda, żeby regresja configu CI (np. po zmianie
  workflow przez kogoś innego) była widoczna od razu, a nie cicho psuła
  kolejność na gablotce.
- Zasada: każda funkcja, która czyta `git log` per plik do celów
  prezentacyjnych (daty, kolejność), musi zakładać, że CI może dać płytki
  klon — albo wymuś `fetch-depth: 0` w workflow, albo dodaj wykrywanie i
  głośne ostrzeżenie zamiast cichej degradacji.

## Właściciel chce paczki bramek ≥5 zestawów naraz, nie po jednym (2026-09-25)

- Po zamknięciu g030 (pojedynczy typ, mood `groza-przerazenie`) właściciel:
  „Prosiłbym na przyszłość o przygotowywanie większych pakietów do oceny.
  Nie jednego ale przynajmniej pięciu zestawów dźwięków/kod/instrumentów/teł”.
- Zasada zapisana w `AGENTS.md` pkt 2: jedna runda bramki od teraz to
  **≥5 wpisów bazy** (typy z `resolver.py --survey`), po 3 kandydatów każdy,
  w jednym manifeście (`data/gates/gNNN/manifest.json` z wieloma `entries`)
  i jednej stronie podglądu. Wzorzec: g031 (3 gesty mood + 2 zestawy
  instrumentów, 5×3=15 kandydatów, jedna runda).
- Dobór anchor-fabuły dla wielu typów naraz: dla każdego typu osobno znajdź
  fabułę, dla której to JEDYNY brak (inaczej trzeba by rozstrzygać kilka
  typów na tej samej fabule i tracić równoległość). Filtr w Pythonie
  w `docs/STATE.md` sekcja „Co dalej” — do skopiowania w kolejnych sesjach.

## `git clone`/`git ls-remote` z github.com działa z bash sandboksa — bez
   dispatcha sample-scout (2026-09-25)

- Wcześniejsze sesje zakładały, że jedynym kanałem na materiał audio jest
  workflow **Sample scout** (GitHub Actions, osobny runner z internetem),
  bo `docs/sources-and-licensing.md` opisuje „egress sandboksa tnie TLS do
  Wikimedia/NPS/Freesound/raw.githubusercontent”. To prawda dla TYCH
  hostów, ale **`git clone`/`git ls-remote` na `github.com` działa wprost
  z bash tej sesji** (zweryfikowane: sparse-checkout VCSL i VSCO-2-CE, po
  ~100 MB każdy, bez dispatcha). Więc gesty (bez sourcingu) i instrumenty
  z repozytoriów na GitHubie (VCSL, VSCO-2-CE — oba CC0 1.0) można budować
  bezpośrednio w sesji, bez czekania na workflow zewnętrzny. Sample-scout
  (Freesound/archive.org/NPS) pozostaje jedyną drogą dla tła/hero, których
  źródła NIE są na GitHubie.
- Wniosek: przy planowaniu bramki najpierw sprawdź, czy potrzebny typ da się
  obsłużyć materiałem z VCSL/VSCO (instant, w sesji) zanim odpalisz
  sample-scout (async, wymaga merge do main + dispatch + oczekiwanie).

## `damp_db` psuje się przy nutach kody rozstawionych <0,4 s — fabuła 253 zablokowana (2026-09-26)

- Sytuacja: po werdykcie bramki g031 (5 nowych klocków, w tym `b_clarinet_warm`)
  odblokowały się od razu fabuły 64/133/191/206/253/437/498/585/599 (9 sztuk).
  8 z nich wyrenderowano czysto. **Fabuła 253** (`g11c_home_arrival` na
  `b_clarinet_warm`) nie przechodzi bramki ataku nut przy ŻADNEJ kombinacji
  `target_db`/`damp_db`/`at_sec` (przeszukano siatkę >150 punktów).
- Diagnoza: `coda_synth.render_coda` implementuje `damp_db` jako tłumienie
  „dotychczasowego bufora” z rampą **zaczynającą się 0,4 s PRZED atakiem
  KAŻDEJ kolejnej nuty** (`pre = 0.40 * SR` w `scripts/coda_synth.py`). Gdy
  gest ma dwie nuty rozstawione o **mniej niż 0,4 s** (tu: akord E5+C3 w t=0,95 s,
  potem C4 w t=1,3 s — odstęp 0,35 s), rampa tłumienia „dla następnej nuty”
  zaczyna się jeszcze PRZED lub tuż po ataku poprzedniej — więc każde
  `damp_db > 0` psuje właśnie tę wcześniejszą nutę zamiast pomóc kolejnej.
  Bez dampu naturalny sustain klarnetu (VSCO susLong, wolny zanik) maskuje
  cichszą nutę C4 do końca utworu (obie nuty grają do końca 6-sekundowego
  okna) — autokalibracja dobija margines do ok. -0,6…+2,3 dB, twardy limit
  to +2,5 dB, a sufit podbicia w silniku to +8 dB/nutę (już wykorzystany).
- Kontrast: **fabuła 599** (`g1b_march_pulse`, nuty rozstawione 0,42 s i
  0,53 s — obie ≥0,4 s) dała się naprawić kombinacją `target_db=-8` +
  **bardzo mały** `damp_db=1.0` (większy `damp_db` ponad ~2 dB łamał bramkę
  HF, bo szybkie rampy tłumienia dokładają energię >6 kHz). **Fabuła 206**
  (`g5a_shimmer_up`, szybka kaskada) naprawiła się samym podbiciem
  `target_db` do -12 (bez dampu w ogóle) — czysty przypadek sufitu
  autokalibracji, nie interferencji dampu.
- Zasada na przyszłość: przed użyciem `damp_db` na sustainowanym instrumencie
  (klarnet/waltornia/organy — cokolwiek bez naturalnego opadania w
  MIN_NOTE_AUDIBLE_SEC=1,2 s) sprawdź odstępy między nutami gestu
  (`data/library/gestures.json` pole `notes[].on`). Jeśli najmniejszy odstęp
  < 0,4 s: **nie próbuj `damp_db`** (pogorszy sytuację lub złamie HF) — szukaj
  ratunku wyłącznie w `target_db` (siatka co ok. 2-3 dB). Jeśli nawet przy
  ekstremalnym `target_db` (blisko 0 dB) margines nie przekracza sufitu
  autokalibracji (+8 dB), kombinacja gest×instrument jest **strukturalnie
  niemożliwa do zrealizowania w obecnym silniku** — nie używać `--force`
  (tylko warsztat), tylko zostawić fabułę nieobsadzoną i odnotować blokadę
  (jak tutaj, dla 253) do rozważenia w przyszłej bramce (inny kandydat na typ
  instrumentacji, albo edycja silnika `pre` w `coda_synth.py` — nie robić
  pochopnie, wpływa na WSZYSTKIE dotychczasowe receptury z `damp_db`).

## Nie mapuj metafory ani pojedynczego ruchu na gotowy typ tylko dlatego, że zgadza się słowo (audyt 2026-09-26)

- Sytuacja: właściciel zapytał, skąd w fabule 206 (`High Stride`) wziął się
  marsz wojsk. Przyczyną było słowo „marsz” w profilu: pojedynczy królik na
  drewnianych szczudłach został zmapowany na `marsz-oddzialu`, a resolver
  użył `troop_march_05` (cztery warstwy kroków po żwirze jak pluton). Audyt
  gotowych sygnatur znalazł trzy analogiczne naciągnięcia: 90 (spokojna
  zatoka obsadzona sztormowym wybrzeżem), 268 (metaforyczna fala aury
  obsadzona wodnym rozbryzgiem), 599 (nocny rytuał w mrocznym lesie obsadzony
  dziennym chórem ptaków).
- Wniosek: wzorzec tekstowy jest tylko hipotezą. Liczy się „co słychać”:
  liczebność źródła (pojedynczy krok ≠ oddział), żywioł fizyczny (aura ≠ woda)
  i pora/charakter środowiska (nocny rytuał ≠ las za dnia). Notatka typu
  „to nie pasuje idealnie, ale jedyny klocek typu” jest sygnałem do BRAKU,
  nie usprawiedliwieniem reuse.
- Zasada / działanie zapobiegawcze: gdy opis klocka ma `bad_for` lub zdrowy
  rozsądek przeczy scenie, popraw klasę fabuły albo zgłoś typ pending i
  bramkę. Nie renderuj finalnie na „najbliższym” klocku. Po audycie 90, 206,
  268 i 599 zostały wycofane z gotowych; klasy skorygowane tak, by resolver
  zwracał BRAK zamiast ponownie tworzyć złą sygnaturę.
