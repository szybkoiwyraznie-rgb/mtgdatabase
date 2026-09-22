# LESSONS — trwała wiedza projektu

Ten plik zawiera krótkie, praktyczne lekcje wynikające z pracy agentów. Każdy wpis powinien odpowiadać na pytanie: co się wydarzyło, czego się nauczyliśmy i jak zapobiec powtórce.

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
