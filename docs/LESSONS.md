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
- Zasada / działanie zapobiegawcze: na branchach roboczych uruchamiaj build i walidację, a deployment wykonuj tylko z `main`.

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

## 2026-09-22 — Jak pobierać sample w sandboxie: GitHub, nie Wikimedia

- Sytuacja: poprzedni agent pobierał stems z Wikimedia Commons techniką User-Agent „NazwaAplikacji/Wersja (kontakt)" (bez tego Wikimedia zwraca 403). W sandboxie tej sesji ta technika nie wystarcza: egress tnie połączenie TLS (SSL EOF, kod 000) do upload.wikimedia.org, commons.wikimedia.org, nps.gov, raw.githubusercontent.com i huggingface.co, zanim padnie jakiekolwiek zapytanie HTTP; osiągalne są m.in. github.com, api.github.com i pypi.org.
- Wniosek: kanałem na żywe sample jest **git clone z github.com** (protokół smart HTTP na dozwolonej domenie), nie bezpośrednie pobieranie z Wikimedia/NPS ani `raw.githubusercontent.com`.
- Zasada / działanie zapobiegawcze: sprawdzoną ścieżką jest mirror `github.com/rosuH/YSL` — automatyczny, publiczny crawler Yellowstone Sound Library (NPS, domena publiczna): `git clone --depth 1 --filter=blob:none --sparse` + `git sparse-checkout set <Folder>`. Każdy sample z rejestru `data/sources.json` musi mieć udokumentowane oryginalne źródło (url NPS/Wikimedia) i kanał pobrania w `notes`. Uwaga: licencja dotyczy oryginału — status mirrora tylko odnotowujemy, nie traktujemy go jako źródła licencji.
