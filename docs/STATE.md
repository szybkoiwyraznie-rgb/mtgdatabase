# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-23** (PR #33, gałąź `arena/01a0ce26-mtgdatabase`).

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

Nic nie czeka na werdykt właściciela. Fabuła 3 (Nefarious Imp) domknięta:
trzy istniejące wpisy pasowały semantycznie (ogień dopalającej się mapy,
tajemnica widmowego artefaktu, eteryczne szkło dla kryształu); brakował
wyłącznie hero 1:1. G012 z creature-SFX odrzucona jako kreskówkowa, g013
z prawdziwym ludzkim śmiechem przyjęta w wariancie h.2.

## Co dalej (propozycja agenta, nie wymaga pytania właściciela)

1. Wybrać kolejne fabuły z katalogu i dla każdej wyprowadzić role
   z narracji; brakujące role → bramki. Hero nie może się powtórzyć,
   więc **każda nowa fabuła to zwykle nowa bramka hero**.
2. Kandydaci-zapas rozpoznani, ale niewykorzystani (patrz
   `docs/sources-and-licensing.md`): miecze, zombie, głosy wysiłku,
   metal/drewno, bagna, woda/plusk.

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
