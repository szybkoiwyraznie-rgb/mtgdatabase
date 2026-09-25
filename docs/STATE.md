# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-25** (sesja `arena/01a0d8ef-mtgdatabase`).

## Liczby

- Katalog: **510 fabuł** (`data/catalog.json`), gotowych sygnatur: **28**
  (6 legacy + 22 z modelu 1:1: 18, 23, 28, 90, 110, 126, 166, 169, 193, 222,
  225, 249, 268, 422, 451, 468, 511, 519, 562, 575, 577, 578).
- Baza klocków: **40 wpisów** (`library_tool.py check`: 11 tła / 13 hero /
  8 gestów / 8 instrumentów), wszystkie z `semantics` (1:1, taksonomia v6).
- Bramki rozegrane z werdyktem: **g001–g029** (g014 wycofana — archiwum).
  g023–g029: seria rund o tło-bitwa-zgielk / hero-lopot / koda-nadzieja /
  tlo-dwor-komnaty / koda-spokoj / instr-ostro — wszystkie zamknięte,
  wpisy w bazie: `battle_clamor_01`, `wingburst_takeoff_01`,
  `g11c_home_arrival`, `chamber_hearth_01`, `g10c_humble_pulse`,
  `b_soloviol_spic`.
- **Bramka g030 OTWARTA** (patrz „W toku” niżej) — czeka na werdykt
  właściciela, serwer podglądu działa na `:8080`.

## W toku

**Bramka g030 czeka na werdykt** (`data/gates/g030/index.html`, serwer
uruchomiony na porcie 8080 tego sandboksa — proces w tle „Bramka g030
(podgląd)”). Priorytet z `resolver.py --survey`: mood `groza-przerazenie`
blokuje **59 fabuł** — najczęstszy pojedynczy brak w całym katalogu.
Zakotwiczone na fabule **433 „Inspire Awe”** (jedyny brak fabuły: koda;
tło `forest_day_01`, hero `light_bloom_01`, instrumentacja `b_bassdrum`
już obsadzone przez resolver). Trzej kandydaci — gesty autorskie pod
definicję typu („Groza, strach, makabra — koda mrozi”), podgląd neutralny
na `b_piano_steinway`:

- **z.1** `g_dread_freeze` — niski klaster (C3/D3) narasta i urywa się bez
  wybrzmienia („mrozi”, nie gaśnie).
- **z.2** `g_dread_descent` — trzy stąpnięcia w dół, potem nagły spadek
  w dysonansowe dno z podszytą wielką sekundą.
- **z.3** `g_dread_pulse` — ostry szturchaniec wysoko, cisza, niski powidok,
  z którego budzi się późny dysonansowy podszept.

Po werdykcie właściciela (np. „z.2”): `library_tool.py accept --gate g030`,
receptura fabuły 433 (background/hero/instrumentation już znane z resolvera),
render `--audit`, potem `resolver.py --survey` ponownie — mood
`groza-przerazenie` odblokuje od razu wszystkie fabuły, które mają go jako
JEDYNY brak (sprawdzić przez `resolve_story` po zamknięciu bramki, podobnie
jak zrobiono to w tej sesji dla `dwor-komnaty`/`spokoj-kontemplacja`/
`ostro-gwaltowna` — 8 fabuł obsadzonych bez dodatkowej bramki po zamknięciu
g026+g028).

**Sesja 2026-09-25 (arena/01a0d8ef)**: po zamknięciu g025–g029 (odziedziczone
z poprzedniej sesji z otwartymi werdyktami) `resolver.py --survey` pokazał
**22 fabuły w pełni obsadzalne bez nowej bramki**. Zbudowano recepturę i
render dla wszystkich 8 brakujących (249, 90, 126, 268, 422, 511, 562, 577);
14 pozostałych było już gotowych z poprzednich sesji. Szczegóły poziomów
i lekcje w `docs/LESSONS.md`:
- **249 (Feedback)**: hero `light_bloom_01` (86% energii >6 kHz w izolacji)
  + cichy `chamber_hearth_01` + krótka, w większości cicha koda
  `g10c_humble_pulse` na `b_soloviol_spic` = pierwsza porażka bramki HF
  (73,4%) mimo poziomów sprawdzonych w innych fabułach z tym samym hero.
  Naprawione siatką `render_signature.py --force --audit` po poziomach
  hero×coda (hero -20 dB, coda -3 dB → HF 16,9%, RMS -25,2 dB, margines
  hero 9,9 dB) — praktyczny sufit RMS tej obsady to ok. -25,1 dB.
- **511**: `stealth_move_03` (sustainowana czynela) + `b_handchimes`
  (sustainowane próbki) na gest `g10c_humble_pulse` = samomaskowanie nut —
  naprawione `damp_db: 12` (jak w fabule 451) + przycięcie hero do 2,6 s.
- **268 / 577**: wąski bank `b_bassdrum` (3 próbki) na `g11c_home_arrival`
  (5 nut, dwie nałożone) maskował ostatnią, pojedynczą nutę — naprawione
  `damp_db: 4`.
- **90, 126, 422, 562**: bez niespodzianek, poziomy z analogicznych fabuł
  (222, 23/110, 5) przeniesione wprost.

Wszystkie 28 receptur przechodzą `library_tool.py check` (kombinacje
unikalne), `test_signature_system.py` (zielone), `build_pack.py` i
`build_site.py` (bez błędów).

## Co dalej (kolejność pracy, nie wymaga pytania właściciela)

1. **Werdykt g030** → `library_tool.py accept --gate g030` → receptura i
   render fabuły 433 → `resolver.py --survey` ponownie, obsadzić od razu
   każdą fabułę, dla której `groza-przerazenie` był JEDYNYM brakiem.
2. Po g030 kolejne najczęstsze braki (z `resolver.py --survey` sprzed tej
   sesji, do przeliczenia po g030): mood `wspolnota-wiez` (34),
   instrumentacja `cieplo-serdeczna` (33), mood `duma-majestat` (31), mood
   `bezwzglednosc-drapieznosc` (31), instrumentacja `metaliczno-mechaniczna`
   (30), tło `gory-wichry` (28), tło `podziemia-jaskinia` (28), hero
   `rezonans-magiczny` (24), mood `furia-dzikosc` (24). Bramkę kotwicz na
   fabule z małą liczbą braków (użyj tego samego filtra co dla g030:
   `resolve_story` z `braki` długości 1 na docelowy typ), kandydatów dobierz
   pod DEFINICJĘ TYPU z `data/semantics/taxonomy.json` (`co_slychac`), nie
   pod jedną narrację.
3. Tła/hero (audio z zewnątrz) wymagają sample-scout (workflow GitHub,
   internet) — patrz sekcja niżej. Gesty (koda) i przy okazji część
   instrumentów już w bazie (VCSL/VSCO) nie wymagają nowego sourcingu —
   dobieraj to, co tańsze/szybsze, chyba że definicja typu wymaga realnego
   nagrania terenowego.
4. Ostrożnie z `scripts/build_gate_manifest.py` — jednorazowy legacy builder
   g001, nadpisuje ten katalog przy KAŻDYM uruchomieniu (patrz LESSONS
   2026-09-25). Nie uruchamiać „na sprawdzenie”.

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
- `pip install --break-system-packages numpy scipy pytest soundfile av
  lameenc` — świeży sandbox nie ma żadnej z tych zależności; bez nich
  `render_signature.py`/testy padają na `ModuleNotFoundError`.
- Źródła (`/tmp/ysl`, `/tmp/atomcut`, `/tmp/vcsl`, `/tmp/vsco2ce`) nie
  przeżywają resetu; klonuj sparse ponownie wg `docs/sources-and-licensing.md`.
- **Zwiad czyści `legacy/source/sample_scout/` przy każdym runie** —
  starsze partie znikają z HEAD; surowce trzymaj w `/tmp` albo odzyskaj
  `git show <baza>:<ścieżka>` (LESSONS 2026-09-24).
- **`build_gate_manifest.py` nie ma trybu podglądu** — każde uruchomienie
  nadpisuje `data/gates/g001/manifest.json` (LESSONS 2026-09-25).
