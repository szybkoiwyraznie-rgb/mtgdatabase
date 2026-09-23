# LESSONS — trwała wiedza projektu

Ten plik zawiera krótkie, praktyczne lekcje wynikające z pracy agentów. Każdy wpis powinien odpowiadać na pytanie: co się wydarzyło, czego się nauczyliśmy i jak zapobiec powtórce.

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
  wpisów do bazy (warianty jednej roli, wielowariantowo), agent obsadza fabułę
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
