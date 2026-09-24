# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-24** (PR #34, gałąź `arena/01a0d031-mtgdatabase`).

## Liczby

- Katalog: **510 fabuł** (`data/catalog.json`), gotowych sygnatur: **6**.
- Baza klocków: **18 wpisów** (`library_tool.py check`).
- Bramki rozegrane: **g001–g013**, wszystkie z werdyktami
  (`data/gates/*/verdicts.json`). Żadna nie czeka na właściciela.

## Gotowe fabuły

| # | Tytuł | tło (d) | hero (c) | koda a × b | uwagi właściciela |
|---|---|---|---|---|---|
| 1 | Dunland Crebain | thunder_far_01 | raven_yell_long_01 | g1b_march_pulse × timpani | „super 15/15”, zamrożona |
| 4 | Mystic Sanctuary | frogs_night_01 | loon_wail_01 | g4b_mystery_tritone × wine_glasses | „super 15/15”, zamrożona |
| 5 | Academy Journeymage | energy_steam_roar_01 | spell_cast_bolt_01 | g5a_shimmer_up × piano_steinway | v2 po uwadze „czar brzmi jak koda”; przyjęta jako „akceptowalna jakość” |
| 8 | Goblin Deathraiders | fire_hearth_small_01 | warband_cry_03 | g1b_march_pulse × bassdrum | „fajna” |
| 2 | Coralhelm Guide | flooded_canyon_03 | beast_roar_long_01 | g4b_mystery_tritone × timpani→steinway | tło r.3 „najzajebistsza z zajebistych” |
| 3 | Nefarious Imp | fire_hearth_small_01 | demonic_laugh_02 | g4b_mystery_tritone × wine_glasses | g012 odrzucona jako kreskówkowa; g013 h.2 z prawdziwego wykonania |

## W toku

**Przebudowa na model semantyczny (ADR 0006, 2026-09-24).** Właściciel
cofnął ADR 0005 (tryby wzrostowe, limity procentowe) w całości. Nowy
porządek: profil semantyczny fabuły (4 warstwy, bez zaglądania do baz) →
kafeteria kontrolowanych klas → resolver z miękkim balansem. Jedyna twarda
reguła: unikalna kombinacja a·b·c·d. Plan: `docs/roadmap-semantyka.md`
(Etap 0 ukończony w tej sesji).

Bramka **g014 (fabuła 18) jest wycofana** — żaden kandydat nie wszedł do
bazy; archiwum w `data/gates/g014/` zostaje. Fabuła 18 wróci w Etapie 5
roadmapy, obsadzona od profilu semantycznego.

## Co dalej (kolejność z roadmapy, nie wymaga pytania właściciela)

1. **Etap 1**: profile semantyczne wszystkich 510 fabuł
   (`data/semantics/story-profiles.json`), partiami, bez patrzenia
   do bibliotek.
2. **Etap 2**: kafeteria v1 (`data/semantics/taxonomy.json`) z analizy
   korpusu + bramka tekstowa właściciela (akceptacja listy klas).
3. Etapy 3–5: migracja bibliotek, resolver, wznowienie produkcji od
   fabuły 18. Kandydaci-zapas z `docs/sources-and-licensing.md`
   (miecze, zombie, metal/drewno, bagna, woda) pozostają w odwodzie.

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
- Źródła (`/tmp/ysl`, `/tmp/atomcut`) nie przeżywają resetu; klonuj sparse
  ponownie wg `docs/sources-and-licensing.md`.
