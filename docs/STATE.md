# Stan produkcji — AI SFX v2

Ostatnia aktualizacja: **2026-10-07** (sesja `arena/01a108e2-mtgdatabase`).

> Ten plik jest **obowiązkową lekturą agenta** i musi się mieścić w limicie
> 50 000 tokenów razem z resztą plików z `docs/required-reading.md`
> (walidator `scripts/check_required_reading.py`). Dlatego trzyma tylko
> stan bieżący, reguły i indeks rund. Opisy poszczególnych rund i dostaw
> są w `docs/archive/state-*.md` i czyta się je na żądanie, nie zawsze.

## Aktualna decyzja produktu

Dla każdej fabuły powstaje **jeden krótki, jednorodny sample**: „krakanie
wron”, „uderzenie dzwonu”, „szczęk bitwy”, „odgłos upadku”. Nie robimy
wielowarstwowej sceny z tłem i kodą. Stary ręczny sound design v1 leży
w `archive/v1-curated-sound-design/` i nie trafia do ZIP-a ani Pages.

Najważniejszy wymóg właściciela: **dźwięk ma się kojarzyć z kartą.**
Czyste skrobanie, syczenie, stuknięcie czy szelest bez rozpoznawalnego
źródła to porażka, nawet jeśli metryki się zgadzają.

## Aktualny stan produkcji

- Katalog: `fabuły270926.csv` — **563 fabuł** (walidacja: 563 rekordów).
  ID fabuły to numeryczna część `Ilustracja` (`280KTK` → fabuła `280`).
- Sample: **563 MP3** w `audio/samples/<id>.mp3`, **563 scenariuszy**
  w `data/samples/scenarios.jsonl` — 100 % katalogu.
- Ostatnia dostawa: `b073` — `327BLB` *Brave-Kin Duo* (`water_splash`)
  i `328LRW` *Bog Hoodlums* (`heavy_impact`), obie **trafione, 0 flag**.
  `328` weszła z pierwszej tury; `327` dopiero po zmianie archetypu
  z `liquid_pour` na `water_splash` — patrz reguła 25.
- Poprzednia dostawa: `b072` — `324DSK` *Spineseeker Centipede*
  (`mechanism_click`) i `325TDM` *Narset's Rebuke* (`thunder_clap`),
  obie **trafione, 0 flag**; `325` wymagała 5 prób i montażu.
- Ostatnia runda: `r059` — z 2 kart weszła **jedna**: `434`
  *Epic Experiment* urosła z **1,20 → 3,91 s** treści, kontrakt
  `war_machine` spełniony. Cena: nowy bliźniak `325-434` (0,9422).
  `232` znów cofnięta — crest 12,9–14,9 przy progu 17.
- Poprzednia runda: `r058` — z 3 kart weszła jedna, najgorsza w swojej
  klasie: `113` *Welder Automaton* urosła z **1,24 → 3,96 s** treści
  (fade 150 ms domknął kontrakt). `232` i `434` cofnięte.
- Jeszcze wcześniej: `r057` — 3 z 8 kart urosły (`558` +1,91 s,
  `4` +0,69 s, `26` +0,54 s), treść < 2 s **21 → 19**, flagi 53 → 52.
- Ostatnia korekta EQ: `r058eq` — **zero kredytów**, półka widmowa na
  7 kartach: `dull` 16 → 11 (`74`, `102`, `120`, `173`, `214`; +3 dB przy
  2 kHz), `harsh` 11 → 9 (`86`, `267`; −3 dB przy 8 kHz). Flagi 52 → 46,
  pary ≥ 0,90 **23 → 22**, nowych flag 0, werdykty bez zmiany.
- Ostatnia runda korekt: `r056` — zero przyjętych (diagnoza poniżej).

Metryki korpusu (audyt `2026-10-08-after-eq`):

| metryka | wartość |
|---|---|
| pliki z flagą | **41** |
| bliźniaki ≥ 0,95 | **0** |
| identyczny PCM | **0** |
| pary ≥ 0,90 (graf kosinusowy) | **23** |
| treść < 2 s | **17** |
| poza oknem 2–5 s | **0** |
| LUFS średnio | **-20.09** (odch. 0.48) |
| archetypy nie trafiony / prawdopodobnie / trafiony | **0 / 33 / 151** |

Budżet: klucz 10 000 kredytów, **wydane 2080, zostaje 7920**.
Realny koszt to **40 kredytów za generację**; pełna runda 8 kart po
2 warianty = 16 generacji = **640 kredytów**, dostawa 2 kart = 160.

Mechanizm generacji: token bota Arena **nie może** użyć
`workflow_dispatch` (HTTP 403), więc generacje idą przez tymczasowy
workflow `.github/workflows/temp-variants-r016.yml`, odpalany markerem
w treści commita (`[generate-rNNN]` / `[generate-bNNN]`). Workflow
commituje warianty z powrotem na branch (`[import-rNNN]`), agent je
pobiera `git pull`, wybiera wariant i sprząta katalog `variants/`.

**Po resecie sandboxa** (zdarzyło się trzy razy w jednej sesji):
`.venv/` i `.cache/` są w `.gitignore` i giną, a repo wraca do commitu
bazowego. Kolejność odtwarzania:

```bash
git fetch origin <branch-sesji> && git reset --hard origin/<branch-sesji>
python3 -m venv .venv && .venv/bin/pip install numpy scipy soundfile pyyaml pyloudnorm resampy
# .cache/wezly.py trzeba napisać od nowa — graf par kosinusowych,
# ładuje scripts/audit_samples_full.py przez importlib Z wpisem w sys.modules
```

## Aktywne ścieżki

- `fabuły270926.csv` — bieżąca kolekcja właściciela.
- `data/catalog.json` — katalog generowany z CSV/TSV przez `scripts/import_collection.py`.
  ID fabuły = numeryczna część `Ilustracja` (sufiks setu wycinany przy
  imporcie: `158OGW` → fabuła `158`); scenariusze, MP3 i manifest używają
  wyłącznie numeru.
- `data/samples/scenarios.jsonl` — ręcznie pisane małe paczki scenariuszy sampli.
- `data/samples/generated-manifest.jsonl` — manifest generacji scouta ElevenLabs.
- `audio/samples/<id>.mp3` — aktualne wygenerowane sample produkcyjne.
- `site/generated/` — biblioteka HTML do sandboxa i Pages, generowana lokalnie.
- `build/samples-latest.zip` — płaski ZIP z `<id>.mp3`, generowany lokalnie.
- `docs/archive/state-*.md` — historia rund i dostaw (nie jest obowiązkową lekturą).

## Aktywne narzędzia

```bash
python scripts/validate_stories.py fabuły270926.csv
python scripts/import_collection.py fabuły270926.csv --output data/catalog.json
python scripts/validate_sample_scenarios.py data/samples/scenarios.jsonl --catalog data/catalog.json
python scripts/audit_samples_full.py --json data/samples/audio-audit-YYYY-MM-DD-after-rNNN.json
python scripts/audit_archetype_match.py --audit <audyt.json> --json data/samples/archetype-match-...json
python scripts/audit_scenario_quality.py --json data/samples/scenario-quality.json
python scripts/rewrite_archetype_prompts.py --ids 1,2,3 --batch rNNN --fill-take --apply
python scripts/postprocess_samples.py --ids 1,2,3 --max-gain-db 26 --report data/samples/postprocess-rNNN.json
python scripts/build_site.py --out site/generated
python scripts/build_pack.py --output build/samples-latest.zip
python scripts/check_required_reading.py
```

Sekret GitHub/API nazywa się **`ELEVENLABS`**. Nie używać dawnej nazwy
`ELEVENLABS_API_KEY`.

## Workflow

**Dostawa nowych fabuł (batch `b0NN`)** — właściciel podaje teksty:

1. Dopisać wiersze do `fabuły270926.csv` (TSV, `\r\n`, kolumny
   `Ilustracja` / `Nazwa Karty` / `Narracja`).
2. `validate_stories.py` → `import_collection.py` (katalog rośnie).
3. Napisać `sample_scenario` (PL) i `prompt` (EN) do `scenarios.jsonl`.
4. `validate_sample_scenarios.py` — **musi wyjść z kodem 0**.
5. Przestawić `temp-variants-r016.yml` na `b0NN` (`--batch`, `IDS`,
   `variants/b0NN`, markery), commit z `[generate-b0NN]`, push.
6. Czekać na `[import-b0NN]` (`git ls-remote` co 20 s, zwykle 40–140 s).
7. Wybrać wariant po metrykach, `postprocess_samples.py`, audyty,
   `build_site.py` + `build_pack.py`, wpis do `STATE.md`, sprzątanie
   `variants/`.

**Runda korekty istniejących kart (batch `r0NN`)** — 8 kart × 2 warianty:
jak wyżej, ale prompty idą przez `rewrite_archetype_prompts.py`
(`OVERRIDES` w tym skrypcie to źródło prawdy dla regeneracji).

## Stan liczbowy

- Katalog: **563 fabuł**, scenariusze **563** (100 %), sample **563**.
- Flagi **41**, pary ≥ 0,90 **26**, treść < 2 s **17**.
- Archetypy: **0** nie trafionych, **33** prawdopodobnie, **151** trafionych.
- Budżet: **5760 / 10 000** kredytów (b072: 560, r057: 640, b073: 360,
  r058: 360, r059: 240).

## Reguły i procedury

Obowiązujące dziś — wyciągnięte z rund r050–r056 i dostawy b071.

**1. Zasada ochronna.** Spadek werdyktu archetypu = powrót do starego
sample. Werdykt jest ważniejszy niż długość. Wyjątek: `292` w r055 nie
zmieniła werdyktu (1,0 pkt przed i po), a i tak została cofnięta, bo
nowy dźwięk był czystym dronem zamiast wiatru — **zamiana jednego
naruszenia na drugie przy tym samym werdykcie to nie jest postęp.**

**2. Przyrost poniżej ~0,3 s nie jest wart nowej flagi.** `469` w r056
przeszła kontrakt i zyskała 0,07 s, ale wzięłaby flagę `harsh` i skok
centroidu 5096 → 12 972 Hz. Odrzucona.

**3. Cofnięcie pliku to cofnięcie tekstu.** Gdy karta wraca do starego
sample, wracają razem: `(a)` MP3, `(b)` `duration_seconds` **i**
`(c)` `sample_scenario` + `prompt`. Punkt `(c)` był pomijany od r051 i
przez sześć rund uzbierał **36 kart**, których opis na stronie nie
odpowiadał plikowi (naprawione 2026-10-07, 0 kredytów).

**4. Dwa limity długości, dwa różne narzędzia.** Przed każdym wysłaniem:
`prompt` po doklejce `--fill-take` **≤ 450** znaków (limit API; realny
ładunek liczy `api_text_length()`, bo scout dokłada zakazy w locie) oraz
`sample_scenario` **≤ 220** znaków (`validate_sample_scenarios.py`).
**Walidator wychodzi z kodem 1 na ostrzeżeniach, nie tylko na błędach** —
lokalny `| tail` to ukrywa i CI wywala się dopiero na GitHubie.

**5. Walidator zabrania słowa „layer”.** `BANNED_LAYER_WORDS` sprawdza
oba pola, więc zapisany prompt kończy się na
`No music, no speech, no ambience bed.`, a zakaz
`No multi-layer cinematic scene.` dokłada scout w locie.

**6. Take 4,0 s, nie krócej.** r056 zmierzyła: przy take'u 2,5 s model
wypełnił 8–83 % pliku, przy 4,0 s — 31–85 %, i najdłuższe treści
powstały właśnie przy 4,0 s. `duration_seconds` to ramka, nie cel.

**7. Wzorzec promptu.** NAKAZ, nie zakaz · jawna liczba powtórzeń ·
pierwsze zdarzenie najgłośniejsze (obniża `attack_s`) · unikać słów
`deep` / `under` / `subterranean` (model robi z nich czysty sub-bas) ·
pilnować centroidu w zakresie kontraktu · dopisek `--fill-take`
(„The sound fills the whole take…”).

**8. `decay_s` = szczyt → pierwsza ramka poniżej szczyt−20 dB**
(`audit_semantic_match.py`). Zdarzenia **rozdzielone przerwami** dają
jednocześnie krótki `decay_s` (przerwa spada pod próg) i wysoki
`onset_count` — sprawdzone na `469` (decay 0,120 / onset 15) i `71`
(0,100 / 5). Ten sam wzorzec nie zadziała dla kontraktów z **dolnym**
progiem `decay_s` (np. `stone_slide` wymaga ≥ 0,5 — tam potrzeba dźwięku
ciągłego).

**9. `onset_count = 0` to dziś dominantny tryb porażki** — `113` i `434`
w r055, `232` w r056. Model robi jedną ciągłą teksturę zamiast N zdarzeń,
mimo że prompt mówi „eight clanks”. Pisz o przerwach wprost.

**10. `attack_s` rośnie, choć prompt mówi „at the very first instant”.**
`4` → 0,670 s, `269` → 0,820 s, `558` → 0,200 s w r056. Samo
sformułowanie nie wystarcza.

**11. `--apply` w `rewrite_archetype_prompts.py` nadpisuje
`duration_seconds` stałą `DURATION` (4,0).** Po każdym `--apply` trzeba
przeliczyć wartość z `sf.info()`, inaczej wychodzi `duration_mismatch`.

**12. Montaż zamiast generacji, gdy się da.** Nadmiar ciszy na krańcach
ucina `postprocess_samples.py --trim-lead-s / --trim-trail-s` (0
kredytów) — tak powstało `280.mp3` (4,00 s → 2,40 s).
`cut_internal_silence.py` wycina dziury w **środku**, nie na krańcach.

**13. Nowa karta ma większą szansę niż poprawka do poprawki.** Karty po
trzecim i czwartym podejściu (`292` — cztery, `87` — cztery) nie
wchodzą; świeże (`244`, `280`, `323`) wchodzą od razu.

**14. Check-lista zamknięcia rundy:** audyt `audit_samples_full.py` →
`audit_archetype_match.py` → graf par (`wezly.py 0.90`, musi zostać 23) →
kopie `-latest.json` → `compileall` + unittest → walidator **z kodem
wyjścia** → `build_site.py` + `build_pack.py` → wpis w `STATE.md` →
commit + push + `gh pr checks` → `git rm -r --cached variants`.

**15. Regeneracja: `--batch` musi zgadzać się z polem `batch` w
`scenarios.jsonl`.** `elevenlabs_sample_scout.py: select_rows()` filtruje
po `row["batch"]`, więc po zmianie batchu w workflow trzeba przepisać
pole w scenariuszu. Inaczej run idzie **na sucho**: `selected 0` →
`No selected ready scenario` → zero kredytów, zero plików, a log
wygląda jak udany (b072b spalił tak dwa odpalenia).

**16. Manifest nie blokuje generacji — pomijanie idzie po pliku.**
`elevenlabs_sample_scout.py` sprawdza `out_file.exists()` w katalogu
`--out`, a nie `generated-manifest.jsonl`. Czyszczenie manifestu przed
regeneracją jest więc **niepotrzebne i szkodliwe** (kasuje historię).

**17. Dopisek „The sound fills the whole take…" blokuje `crest_db`.**
`crest_db = 20log10(peak/rms)`, więc równo wypełniony take ma niski
 crest. Wzorzec `562` *Shock* (jedyne trafione `thunder_clap`): crest
18,83 przy **`audible_share` 0,478** — połowa take'u to cisza. Dla
archetypów z progiem crestu pisz wprost „…dying away into silence
before the end". Dopisek **nie jest** wymagany przez walidator.

**18. Reverb podnosi `decay_s`, ale obniża `crest_db` — konflikt,
którego kontrakt nie widzi.** `add_reverb_tail.py` na `325` dał decay
0,34 → 0,85 s, ale crest 18,61 → 15,72. Używać tylko na take'ach
z zapasem crestu ≥ 6 dB (`325` ostatecznie: 24,5 → 20,9).

**19. Kolejność montażu: reverb → postprodukcja → `tame_spectrum` →
postprodukcja.** Filtr górnoprzepustowy 25 Hz w `postprocess_samples.py`
wycina sub-bas, którym `tame_spectrum` wyrobił centroid (`325`: centroid
734 → 1017, `low_all` 0,504 → 0,302). Po korekcji trzeba puścić
postprodukcję raz jeszcze. I **`--shelf-hz` ma być tam, gdzie jest
energia**: domyślne 3500 Hz mija pasmo 250–2000 Hz, przez co korekcja
rosła z −3 dB do −15 dB i i tak nie trafiała w okno.

**20. Dobór kart do rundy po DIAGNOZIE, nie po długości.** r056 wzięła
osiem „świeżych" kart wybranych z tabeli najkrótszych — nie weszła
żadna. r057 wzięła osiem wybranych po tym, **która konkretna metryka
nie dowiozła**, i weszły trzy. Liczy się nie to, jak bardzo karta
odstaje, tylko czy wiadomo, w co uderzyć.

**21. Dwie miary treści — nie mylić ich.** `content_s` = czas pliku
minus cisza na krawędziach przy progu **bezwzględnym −45 dBFS**; to
jest „treść < 2 s" z tego pliku i z okna akceptacji 2–5 s.
`content_rel_s` = to samo przy progu **względnym** i to od niej zależy
flaga `short_content` (< 0,8 s). Po b072: **21** kart wg `content_s`,
ale tylko **7** wg `content_rel_s`. Normalizacja do −20 LUFS potrafi
`content_s` skurczyć o połowę, więc decyzję o przyjęciu wariantu
podejmujemy dopiero po `postprocess_samples.py`.

**22. Wpisy `OVERRIDES` mają dwa style zapisu** i wycinanie ich
regexem kończy się katastrofą. Część wpisów jest zwarta
(`"...", "...", False),`), część wieloliniowa (`    ),`) — regex na
`^    ),$` przeskakuje do następnego wieloliniowego i kasuje po drodze
cudze wpisy (raz wycięło 4961 znaków zamiast 355). Zakresy liczyć
przez `ast`: węzeł to **`AnnAssign`**, nie `Assign`, bo `OVERRIDES` ma
adnotację typu. Przed każdą edycją: `cp` pliku do `/tmp`.

**23. Po `git reset --hard` branch traci upstream.** `git pull`
wychodzi wtedy bez błędu, ale **nic nie pobiera** — wygenerowane
warianty czekają na serwerze, a lokalnie wygląda jakby run się nie
udał. Po każdym resecie: `git rev-parse --abbrev-ref @{u}` i w razie
`fatal: no upstream` — `git branch --set-upstream-to=origin/<branch>`.

**25. Sprawdzić, czy kontrakt archetypu jest osiągalny, zanim się w
niego wyceluje.** `liquid_pour` żąda `sustain_ratio` ≥ 0,3, a trzy
karty już do niego przypisane mają 0,085 / 0,238 / 0,379 — próg
spełnia jedna. Sześć generacji dla `327` (b073 + b073b = 360 kr)
nie doszło ani razu (najlepsze 0,120). Ten sam plik z pierwszej
tury spełniał `water_splash` w całości. Zasada: przed wyborem
archetypu zmierzyć sporną metrykę na istniejących kartach tej
klasy; jeśli większość jej nie domyka, wziąć inny archetyp dla
tego samego dźwięku.

**24. Korekcję EQ aplikować tylko tam, gdzie zdejmuje flagę.** Próba na
27 kartach (`16 dull` + `11 harsh`) dała ten sam zysk flag (52 → 46),
ale 19 kart bez zysku dorzuciło **2 nowe pary** i podbiło maksimum
kosinusa 0,9415 → 0,9461 (próg bliźniaków 0,95). Po zawężeniu do 7 kart,
które faktycznie straciły flagę: pary 23 → **22**, maksimum bez zmiany.
Zasada: korekta bez efektu to czyste ryzyko — wycinać ją z `--ids`.

## Indeks rund i dostaw

Pełne opisy w `docs/archive/`. Skrót: `pary` = liczba par ≥ 0,90,
`krótkie` = kart z treścią < 2 s.

| batch | data | wynik | archiwum |
|---|---|---|---|
| r016–r033 | 2026-10-05 | kontrakty archetypów, 69 → 0 nie trafionych | `state-2026-10-05.md` |
| r034–r037 | 2026-10-06 | różnicowanie węzłów: 175 → 81 par | `state-2026-10-06.md` |
| r038–r045 | 2026-10-06 | kolejne piętra + trym ogonów: 81 → 21 par | `state-2026-10-06.md` |
| r046–r050 | 2026-10-06 | cleanup krótkiej treści: 69 → 26 krótkich | `state-2026-10-06.md` |
| r051 | 2026-10-06 | 6 krótkich nad progiem, 2 cofnięte | `state-2026-10-06.md` |
| r052 | 2026-10-06 | 6 nad progiem, 2 cofnięte | `state-2026-10-06.md` |
| r053 | 2026-10-07 | 3 nad progiem, 5 cofniętych | `state-2026-10-06.md` |
| r054 | 2026-10-07 | 3 trafione wydłużone bez utraty werdyktu (+2,07 s śr.) | `state-2026-10-06.md` |
| r055 | 2026-10-07 | 2 przyjęte (+2,23 s i +1,86 s), 5 cofniętych | `state-2026-10-06.md` |
| r056 | 2026-10-07 | **0 przyjętych** — diagnoza: krótki take się nie wypełnia | `state-2026-10-06.md` |
| b071 | 2026-10-07 | 2 nowe karty (280, 323), obie trafione z 0 flag | `state-2026-10-06.md` |
| b072 | 2026-10-07 | 2 nowe karty (324, 325), obie trafione; 325 po 5 próbach | `state-2026-10-07.md` |
| r057 | 2026-10-08 | 3 z 8 krótkich weszły, treść < 2 s 21 → 19 | `state-2026-10-08.md` |
| r058eq | 2026-10-08 | EQ za 0 kr: 7 kart, `dull` 16 → 11, `harsh` 11 → 9, flagi 52 → 46, pary 23 → 22 | `state-2026-10-08.md` |
| b073 | 2026-10-08 | 2 nowe karty (327, 328), obie trafione z 0 flag; 327 po zmianie archetypu | `state-2026-10-08-b073.md` |
| r058 | 2026-10-08 | 3 najgorsze karty swoich klas; weszła 113 (1,24 → 3,96 s), 232 i 434 cofnięte | `state-2026-10-08-r058.md` |
| r058b | 2026-10-08 | darmowe domknięcia krawędzi: 72 i 278 bez flag, 0 kredytów | `state-2026-10-08-r058b.md` |
| r059b | 2026-10-08 | `cut_start_hard` przeliczone na skok z ciszy; 2 fałszywe alarmy zdjęte, 9 prawdziwych trzasków naprawionych | `state-2026-10-08-r059b.md` |
| b059–b070 | 2026-10-01…04 | dostawy właściciela, 553 → 557 | `state-2026-10-01.md` |
| b054–b058, r001–r009 | 2026-09-28…30 | start flow v2 | `state-2026-09-28.md` |

**r034–r058eq łącznie: 380 generacji + 7 korekt EQ, 175 → 22 par
(−87 %), treść < 2 s 41 → 19, flagi 53 → 46.**

## Co robić dalej

1. **Kolejna runda `r060`** — `232` pudłuje drugi raz z rzędu
   (r058: crest 13,5–15,6; r059: 12,9–14,9 przy progu 17). Próba
   z promptem na wzór kart przechodzących ruszyła go tylko o 1,5 dB.
   Korpus `plate_clank` ma crest od 19,9 w górę, czyli brakuje ~5 dB,
   a trzy rundy dały łącznie +1,6 dB — **przestać go ruszać**, to nie
   jest karta do naprawy promptem. Zostaje `269` (+0,16 s do progu)
   i `23` (+0,28 s), obie poniżej reguły 2.
   Odkrycie do wykorzystania: kontrakty `thunder_clap` i `war_machine`
   są **zagnieżdżone** — każdy grzmot spełnia war_machine (centroid
   ≤ 800 mieści się w ≤ 2600, low_all ≥ 0,5 w ≥ 0,35). Dlatego
   `325` spełnia oba, a `434` v3 zrobiła się z nim bliźniakiem.
   Celować w centroid **800–2400**: machina spełni kontrakt,
   a nie wejdzie w pasmo grzmotu.
2. **Wątek bez kredytów — po `r058eq`:** `dull` zeszło z 16 na 11,
   `harsh` z 11 na 9. Tanich ruchów już nie ma: `harsh` wymaga
   −12…−15 dB przy 8 kHz na kartach z 0,94–0,98 energii w paśmie
   powietrznym (`226`, `6`, `522` nie mieszczą się nawet przy −15 dB),
   a `dull` przy +3 dB nie dobija do progu 0,005 energii > 2 kHz na
   `339`, `496`, `32`, `51`, `118`, `358`, `159`, `37`, `83`, `468`.
   Obie grupy domykają się tylko nowym materiałem (kredyty).
3. Pilnować `check_required_reading.py` przy każdym dopisywaniu do tego
   pliku (limit 50 000 tokenów).

## Archiwum

Narracje poszczególnych rund i dostaw — czyli wszystko, co nie jest
bieżącym stanem ani obowiązującą regułą — leżą w:

```text
docs/archive/state-2026-09-28.md   start flow v2, r001–r009, b054–b058
docs/archive/state-2026-10-01.md   b059–b070, r010–r015
docs/archive/state-2026-10-05.md   kontrakty archetypów, r016–r033
docs/archive/state-2026-10-06.md   r034–r056, dostawa b071
docs/archive/state-2026-10-07.md   dostawa b072 (324, 325)
docs/archive/state-2026-10-08.md   runda r057 i korekta EQ r058eq
docs/archive/state-2026-10-08-b073.md   dostawa b073 (327, 328)
docs/archive/state-2026-10-08-r058.md   runda r058 (113, 232, 434)
docs/archive/state-2026-10-08-r058b.md  krawędzie: 72, 278 (0 kredytów)
docs/archive/state-2026-10-08-r059.md   runda r059 (434 weszła, 232 cofnięta)
docs/archive/state-2026-10-08-r059b.md  nowa definicja cut_start_hard + 9 napraw
```

Archiwum powstało 2026-10-07 przez wycięcie historii z tego pliku:
`STATE.md` urósł do 3854 linii i sam ważył 51 485 tokenów, czyli więcej
niż cały limit `check_required_reading.py` (50 000). Zasada z
`docs/required-reading.md`: przy przekroczeniu przenieś szczegóły
historyczne do `docs/archive/` **bez utraty decyzji, reguł i procedur** —
dlatego reguły z r050–r056 zostały przepisane wyżej, a nie wycięte.
