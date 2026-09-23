# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-23** (PR #33, gałąź `arena/01a0ce26-mtgdatabase`).

## Liczby

- Katalog: **510 fabuł** (`data/catalog.json`), gotowych sygnatur: **4**.
- Baza klocków: **16 wpisów** (`library_tool.py check`).
- Bramki rozegrane: **g001–g009** (werdykty w `data/gates/*/verdicts.json`),
  **g010 czeka na werdykt**.

## Gotowe fabuły

| # | Tytuł | tło (d) | hero (c) | koda a × b | uwagi właściciela |
|---|---|---|---|---|---|
| 1 | Dunland Crebain | thunder_far_01 | raven_yell_long_01 | g1b_march_pulse × timpani | „super 15/15”, zamrożona |
| 4 | Mystic Sanctuary | frogs_night_01 | loon_wail_01 | g4b_mystery_tritone × wine_glasses | „super 15/15”, zamrożona |
| 5 | Academy Journeymage | energy_steam_roar_01 | spell_cast_bolt_01 | g5a_shimmer_up × piano_steinway | v2 po uwadze „czar brzmi jak koda”; przyjęta jako „akceptowalna jakość” |
| 8 | Goblin Deathraiders | fire_hearth_small_01 | warband_cry_03 | g1b_march_pulse × bassdrum | „fajna” |

## W toku

- **Fabuła 2 (Coralhelm Guide)** — hero gotowy (`beast_roar_long_01`,
  jedyny wolny hero w bazie), koda do wyboru przy montażu, **tło czeka na
  werdykt bramki g008** (trzy okna nagrania NPS „The Dragon’s Mouth”:
  k.1 spokojny chlupot / k.2 woda pod naporem / k.3 echo w głębi).
  Po werdykcie: `verdicts.json` → `library_tool.py accept --gate g008` →
  receptura `data/recipes/2.json` → render `--audit` → `build_pack` +
  `build_site` → commit.

## Co dalej (propozycja agenta, nie wymaga pytania właściciela)

1. Domknąć fabułę 2.
2. Wybrać kolejne fabuły z katalogu i dla każdej wyprowadzić role
   z narracji; brakujące role → bramki. Hero nie może się powtórzyć,
   więc **każda nowa fabuła to zwykle nowa bramka hero**.
3. Kandydaci-zapas rozpoznani, ale niewykorzystani (patrz
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

## Rzeczy, które łatwo przeoczyć

- Bramka i gablotka to **dwa różne serwery** (:8080 i :3000);
  przed nową bramką zatrzymaj poprzedni proces na :8080.
- Gablotkę serwuj `scripts/serve_site.py`, nie `python -m http.server`
  (cache → właściciel słyszy stary montaż).
- `pip install ... scipy pytest` — bez tego skrypty bramek i testy padają.
- Źródła (`/tmp/ysl`, `/tmp/atomcut`) nie przeżywają resetu; klonuj sparse
  ponownie wg `docs/sources-and-licensing.md`.
