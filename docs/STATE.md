# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-24** (sesja `arena/01a0d3b8-mtgdatabase`).

## Liczby

- Katalog: **510 fabuł** (`data/catalog.json`), gotowych sygnatur: **17**
  (6 legacy + 11 z modelu 1:1: 18, 23, 166, 169, 193, 225, 451, 468, 519, 575, 578).
- Baza klocków: **32 wpisy** (`library_tool.py check`: 8 tła / 12 hero /
  6 instrumentów / 6 gestów), wszystkie z `semantics` (1:1, taksonomia v6).
- Bramki rozegrane: **g001–g022** z werdyktami (g014 wycofana — archiwum).
- Bramka **otwarta: g023** (fabuła 222 Maritime Guard; tło `morze-wybrzeze`
  ×4 kandydatów + instrument `mroczna` ×3) — czeka na werdykt właściciela.

## Gotowe fabuły

| # | Tytuł | tło (d) | hero (c) | koda a × b | uwagi właściciela |
|---|---|---|---|---|---|
| 1 | Dunland Crebain | thunder_far_01 | raven_yell_long_01 | g1b_march_pulse × timpani | „super 15/15”, zamrożona |
| 4 | Mystic Sanctuary | frogs_night_01 | loon_wail_01 | g4b_mystery_tritone × wine_glasses | „super 15/15”, zamrożona |
| 5 | Academy Journeymage | energy_steam_roar_01 | spell_cast_bolt_01 | g5a_shimmer_up × piano_steinway | v2 po uwadze „czar brzmi jak koda”; przyjęta jako „akceptowalna jakość” |
| 8 | Goblin Deathraiders | fire_hearth_small_01 | warband_cry_03 | g1b_march_pulse × bassdrum | „fajna” |
| 2 | Coralhelm Guide | flooded_canyon_03 | beast_roar_long_01 | g4b_mystery_tritone × timpani→steinway | tło r.3 „najzajebistsza z zajebistych” |
| 3 | Nefarious Imp | fire_hearth_small_01 | demonic_laugh_02 | g4b_mystery_tritone × wine_glasses | g012 odrzucona jako kreskówkowa; g013 h.2 z prawdziwego wykonania |

## Gotowe fabuły (model 1:1, Etap 5)

| # | Tytuł | tło × hero × koda × instrument | bramka |
|---|---|---|---|
| 18 | Lotusguard Disciple | sky_rush_02 × barrier_ring_01 × g6c × steinway | g015 |
| 23 | Brightwood Tracker | forest_day_01 × light_bloom_01 × g5a × steinway | g017 |
| 166 | Talion's Messenger | forest_day_01 × stealth_move_03 × g6c × steinway | g017 |
| 519 | Lurking Green Dragon | forest_day_01 × stealth_move_03 × g6c × timpani | g017 |
| 468 | Cacophodon | forest_day_01 × beast_roar_01 × g6c × bassdrum | g016 |
| 578 | Savage Surge | forest_day_01 × beast_roar_01 × g6c × timpani | g016 |
| 575 | Dromoka Warrior | warcamp_01 × troop_march_05 × g7a × logdrum | g018/g019 |
| 193 | Floodhound | thunder_far_01 × sniff_track_01 × g8b × handchimes | g020/g021 |
| 169 | Greenwood Sentinel | forest_day_01 × stealth_move_03 × g6c × logdrum | pełny reuse |
| 225 | Furious Forebear | forest_day_01 × light_bloom_01 × g8b × steinway | pełny reuse |
| 451 | Downwind Ambusher | forest_day_01 × stealth_move_03 × g7a × handchimes | pełny reuse |

169/225/451 (2026-09-24, sesja 01a0d3b8): pierwsze fabuły obsadzone BEZ
bramki — resolver zgłosił pełną obsadę z istniejących klocków. QA renderów:
169 (hero +14,4 dB, RMS -21,5), 225 (hero +22,5 dB, RMS -19,9, HF 18,2%),
451 (hero +19,8 dB, RMS -22,1; po korekcie: hero przycięte do 2,6 s —
lekcja w LESSONS o ogonie hero maskującym nuty kody).

## W toku

**Bramka g023 czeka na werdykt** (7 kandydatów: `m.1–m.4` morze-wybrzeze,
`b.1–b.3` instr-mroczna). Po werdykcie: `library_tool.py accept --gate g023`,
receptura 222 (obsada resolvera: `morze-wybrzeze` + stealth_move_03 +
g6c_sentry_return + `<wybrany mroczna>`), render `--audit`, raport.
Ten sam duet braków (morze + mroczna) ma też fabuła 28 (Kraken's Eye) —
po g023 resolver obsadzi ją bez nowej bramki (hero fala-rozbryzg od g022
jest już w bazie: wave_crash_03).

Przebudowa semantyczna (ADR 0006) ZAMKNIĘĄ: Etapy 0–4 wykonane,
taksonomia v6 zamrożona, resolver produkcyjny. Bieżąca faza to **Etap 5 =
produkcja katalogu**: priorytety bramek daje `resolver.py --survey`.

## Co dalej (kolejność pracy, nie wymaga pytania właściciela)

Roadmapa semantyczna (`docs/roadmap-semantyka.md`) domknięta: Etapy 0–4
wykonane (profile 510/510, taksonomia zamrożona na **v6** — 32 tła / 75 hero
/ 20 nastrojów / 18 instrumentacji, 146 nadpisań, 510/510 kombinacji
unikalnych; klocki 32/32 otagowane 1:1; resolver + testy zielone).
Szczegółowa historia etapów: poprzednie wersje tego pliku w gicie
i `data/semantics/CHANGELOG.md`.

Bieżąca faza: **Etap 5 — produkcja katalogu**. Kolejka pracy:

1. **Werdykt g023** → accept → receptura i render fabuły 222 (a przy okazji
   resolver obsadzi 28 bez bramki) — opis w „W toku" wyżej.
2. **Dalej `resolver.py --survey`**: po g023 najczęstszymi brakami zostaną
   mood `groza-przerazenie` (59), mood `nadzieja-ukojenie` (47),
   mood `wspolnota-wiez` (34), instrumentacja `cieplo-serdeczna` (33)
   i `ostro-gwaltowna` (32). Bramkę kotwicz na fabule z małą liczbą
   braków, a kandydatów dobierz pod DEFINICJĘ TYPU (lekcja g015).
3. Kandydaci-zapas z `docs/sources-and-licensing.md` (miecze, zombie,
   metal/drewno, bagna, woda) pozostają w odwodzie; zwiad działa
   (patrz niżej), lecz czyści katalog partii — patrz LESSONS 2026-09-24.

## Sample scout — uruchomienie

Workflow **Sample scout** ściąga nagrania spoza sandboksa (runner ma internet).
Job działa tylko z `main` i z gałęzi `arena/**`; z innych jest „skipped”.
Agent uruchamia go sam po merge do `main`:

```bash
gh api repos/szybkoiwyraznie-rgb/mtgdatabase/dispatches \
  -f event_type=sample-scout \
  -F 'client_payload[source]=archive.org' \
  -F 'client_payload[query]=creek stream water' \
  -F 'client_payload[count]=5'
```

Pełna instrukcja pól i pułapki: `docs/sources-and-licensing.md`.

## Licencje — nie komplikuj

Projekt prywatny, niekomercyjny, pliki na dysk właściciela: **brak licencji
jest OK**, wolne ma pierwszeństwo, status zapisujemy w rejestrze. Ostrożność
dotyczy wyłącznie publicznej gablotki Pages i ZIP-a. Pełna polityka:
`docs/sources-and-licensing.md` (sekcja na górze).

## Rzeczy, które łatwo przeoczyć

- Bramka i gablotka to **dwa różne serwery** (:8080 i :3000);
  przed nową bramką zatrzymaj poprzedni proces na :8080.
- Gablotkę serwuj `scripts/serve_site.py`, nie `python -m http.server`
  (cache → właściciel słyszy stary montaż).
- `pip install ... scipy pytest` — bez tego skrypty bramek i testy padają.
- Źródła (`/tmp/ysl`, `/tmp/atomcut`, `/tmp/vcsl`) nie przeżywają resetu;
  klonuj sparse ponownie wg `docs/sources-and-licensing.md`.
- **Zwiad czyści `legacy/source/sample_scout/` przy każdym runie** —
  starsze partie znikają z HEAD; surowce trzymaj w `/tmp` albo odzyskaj
  `git show <baza>:<ścieżka>` (LESSONS 2026-09-24).
