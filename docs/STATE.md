# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-26** (sesja `arena/01a0d8ef-mtgdatabase`).

## Liczby

- Katalog: **510 fabuł** (`data/catalog.json`), gotowych sygnatur: **38**
  (6 legacy + 32 z modelu 1:1: 18, 23, 28, 64, 90, 110, 126, 133, 166, 169,
  191, 193, 206, 222, 225, 249, 268, 422, 433, 437, 451, 468, 498, 506, 511,
  519, 562, 575, 577, 578, 585, 599).
- Baza klocków: **46 wpisów** (`library_tool.py check`: 11 tła / 13 hero /
  14 gestów / 9 instrumentów — wszystkie z `semantics`, model 1:1, taksonomia v6).
- Bramki rozegrane z werdyktem: **g001–g031** (g014 wycofana — archiwum).
  g030 (mood groza-przerazenie) → z.2 → `g_dread_descent`. **g031** (pakiet
  5 wpisów naraz, pierwsza runda wg nowej zasady właściciela) → werdykt
  w3/d2/b3/c3/m3 → `g_bond_echo`, `g_pride_ascent`, `g_ruthless_verdict`,
  `b_clarinet_warm`, `b_tubularbells_metal` — wszystkie 5 przyjęte do biblioteki.
- **Jedna fabuła zablokowana strukturalnie**: **253** (Inspiring Bard) —
  `g11c_home_arrival` × `b_clarinet_warm` nie przechodzi bramki ataku nut przy
  żadnej kombinacji parametrów (silnik `damp_db` konfliktuje z odstępem nut
  <0,4 s — pełna diagnoza w `docs/LESSONS.md` 2026-09-26). Nie wyrenderowana,
  `data/recipes/253.json` nie istnieje (świadomie usunięty, nie zapomniany).

## W toku

Brak otwartej bramki — g031 domknięta i w pełni wykorzystana (wszystkie 9
odblokowanych fabuł sprawdzone, 8 wyrenderowanych, 1 udokumentowana blokada).

**Następny krok**: zbudować kolejną PACZKĘ ≥5 wpisów (zasada właściciela,
patrz `AGENTS.md` pkt 2) z listy niżej. Serwer podglądu bramki (`:8080`) —
jeśli poprzedni proces wygasł (środowisko czyści procesy w tle między turami),
uruchom ponownie: `python3 scripts/gate_preview.py data/gates/gNNN --port 8080`.

## Sesja 2026-09-25 → 2026-09-26 — skrót przebiegu

1. Bramka g030 (mood `groza-przerazenie`) → werdykt właściciela **z.2**
   (`g_dread_descent`) → do bazy. Odblokowało fabuły 433 i 506 — obie
   wyrenderowane od razu (bez dodatkowej bramki).
2. Właściciel poprosił o **większe paczki bramek** (≥5 zestawów naraz) —
   zapisane trwale w `AGENTS.md` pkt 2.
3. Zbudowana i rozegrana bramka **g031** wg nowej zasady: 5 wpisów × 3
   kandydatów (15 klipów): 3 kody-nastroje (wspólnota-więź, duma-majestat,
   bezwzględność-drapieżność) + 2 zestawy instrumentów (ciepło-serdeczna:
   marimba/waltornia/klarnet z VCSL+VSCO-2-CE; metaliczno-mechaniczna:
   kowadło/tarcza hamulcowa/dzwony rurowe z VCSL). Werdykt właściciela:
   **w3, d2, b3, c3, m3** → `g_bond_echo`, `g_pride_ascent`,
   `g_ruthless_verdict`, `b_clarinet_warm`, `b_tubularbells_metal` — 5/5
   przyjęte (`library_tool.py accept --gate g031`).
4. `resolver.py --survey` po przyjęciu → **9 nowych fabuł w pełni
   obsadzalnych**: 64, 133, 191, 206, 253, 437, 498, 585, 599 (jednym
   zaakceptowanym klockiem, bez kolejnej bramki).
5. Zbudowano i wyrenderowano **8 z 9** (64, 133, 191, 206, 437, 498, 585,
   599) — wszystkie PASS `--audit`. Dwie wymagały dostrojenia poziomów
   (nie domyślnych): **206** `target_db=-12` (bez dampu — kaskada
   `g5a_shimmer_up` na wolno atakującym klarnecie wymagała więcej
   headroomu dla autokalibracji); **599** `target_db=-8` + `damp_db=1.0`
   (bardzo mały damp — większy łamał próg HF).
6. **253 pozostaje zablokowana** — `g11c_home_arrival` (akord E5+C3 + C4 w
   odstępie 0,35 s, <0,4 s okna dampu w silniku) na sustainowanym klarnecie
   nie przechodzi bramki ataku przy ŻADNEJ z >150 przeszukanych kombinacji
   `target_db`/`damp_db`/`at_sec`. Pełna diagnoza silnika w
   `docs/LESSONS.md` (sekcja „`damp_db` psuje się przy nutach <0,4 s”).
   Nie użyto `--force` (workshop-only, nie dla finalnych sygnatur).
7. Napotkano powtarzalną usterkę środowiska: **lokalny `.git` HEAD resetuje
   się do starszego commita między turami**, mimo że pliki na dysku
   pozostają aktualne i wypchnięte commity są na remote. Zweryfikowano
   trzykrotnie w tej sesji: `git diff FETCH_HEAD` na śledzonych plikach
   zawsze wychodził pusty (bezpieczne `git reset --hard FETCH_HEAD`).
   Procedura opisana w sekcji „Rzeczy, które łatwo przeoczyć” niżej.

Wszystkie 38 receptur przechodzą `library_tool.py check` (kombinacje
unikalne), `test_signature_system.py` (zielone), `build_pack.py` i
`build_site.py` (bez błędów; 46 wpisów baz, 38 sygnatur, 6 stron).

## Co dalej (kolejność pracy, nie wymaga pytania właściciela)

1. **Zbuduj następną paczkę ≥5 wpisów** (zasada właściciela). Kandydaci wg
   `resolver.py --survey` (po odjęciu tego, co zamknęła g031):
   `background:gory-wichry` (28), `background:podziemia-jaskinia` (28),
   `hero:rezonans-magiczny` (24), `mood:furia-dzikosc` (24),
   `hero:przemiana-materializacja` (23), `background:miasto-gwar` (23),
   `instrumentacja:zimno-szklista` (21), `hero:potezny-cios` (21),
   `background:swiatynia-sanktuarium` (21), `background:miasto-nocne` (21),
   `background:laboratorium-technika` (21), `background:wioska-sielska` (21),
   `background:step-rownina` (19), `background:kuznia-warsztat` (19),
   `mood:zuchwalosc-brawura` (18). Tła (`gory-wichry`, `podziemia-jaskinia`,
   `miasto-gwar`, `swiatynia-sanktuarium`, `miasto-nocne`,
   `laboratorium-technika`, `wioska-sielska`, `step-rownina`,
   `kuznia-warsztat`) prawdopodobnie wymagają prawdziwych nagrań terenowych
   (sample-scout / Freesound / archive.org), nie gestów autorskich — sprawdź
   `docs/sources-and-licensing.md` i rozważ dispatch sample-scout wcześniej
   (async, wymaga czasu), żeby materiał czekał gotowy na następną sesję.
2. **253 do rewizytacji**: jeśli w przyszłości pojawi się DRUGI kandydat na
   typ instrumentacji `cieplo-serdeczna` (obecnie tylko `b_clarinet_warm`),
   sprawdź czy nowy klocek (np. waltornia z tej samej bramki g031, c.2,
   niewybrana) przechodzi bramkę dla tej konkretnej fabuły — ale to wymaga
   zmiany modelu 1:1 (dwa klocki tego samego typu), nie rób tego bez zgody
   właściciela. Alternatywa: edycja `pre` w `coda_synth.py` (0,4 s →
   mniej) — dotyka WSZYSTKICH receptur z `damp_db`, wymaga pełnej regresji
   (`test_signature_system.py` + ręczny przegląd audytów istniejących
   receptur z dampem: 268, 433, 506, 511, 575, 599).
3. Filtr na anchor fabułę dla nowego typu (kopiuj-wklej do nowej sesji):
   ```python
   import sys, json
   sys.path.insert(0, "scripts")
   import resolver
   data = resolver.load_data()
   for sid in data["profiles"]:
       r = resolver.resolve_story(sid, data)
       if len(r["braki"]) == 1 and r["braki"][0]["layer"] == "TYP_WARSTWY" \
          and r["braki"][0]["typ"] == "TYP":
           print(sid, r["title"])
   ```
4. Ostrożnie z `scripts/build_gate_manifest.py` — jednorazowy legacy builder
   g001, nadpisuje ten katalog przy KAŻDYM uruchomieniu (LESSONS 2026-09-25).

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

**Nowość 2026-09-26**: `git clone`/`git ls-remote` na `github.com` działają
BEZPOŚREDNIO z bash tej sesji (sparse-checkout VCSL/VSCO-2-CE użyty w g031,
bez dispatcha) — sample-scout pozostaje potrzebny tylko dla hostów spoza
GitHuba (Freesound/archive.org/NPS). Zanim odpalisz dispatch, sprawdź czy
potrzebny dźwięk nie jest już dostępny w jakimś repo CC0 na GitHubie.

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
  `render_signature.py`/testy padają na `ModuleNotFoundError`. **Uwaga**:
  to trzeba robić PRZY KAŻDYM restarcie sandboksa w tej samej sesji też —
  pakiety pip nie zawsze przeżywają nawet między turami.
- **Lokalny git tej sesji bywa płytki/resetowany między turami, a
  procesy w tle (serwery podglądu) znikają między turami** — sprawdź
  `git log --oneline -5` i `get_process_output` na początku tury; jeśli HEAD
  wygląda staro mimo że poprzednia tura commitowała: `git fetch origin
  <branch>`, sprawdź `diff -q <(git show FETCH_HEAD:plik) plik` dla kilku
  śledzonych plików (jeśli SAME dla wszystkich — bezpiecznie
  `git reset --hard FETCH_HEAD`, potwierdzone 3× w sesji 2026-09-26 bez
  utraty danych). Serwery uruchom ponownie (`start_process`) — pliki
  podglądu (`index.html`) trzeba czasem przebudować (`gate_preview.py
  data/gates/gNNN --build-only`) jeśli też zniknęły z dysku.
- Źródła (`/tmp/ysl`, `/tmp/atomcut`, `/tmp/vcsl_probe`, `/tmp/vsco_probe`)
  nie przeżywają resetu; klonuj sparse ponownie wg
  `docs/sources-and-licensing.md`. `git clone`/`git ls-remote` na
  `github.com` działają z bash tego sandboksa; Freesound/NPS/
  raw.githubusercontent — nie (stąd sample-scout przez GitHub Actions).
- **Zwiad czyści `legacy/source/sample_scout/` przy każdym runie** —
  starsze partie znikają z HEAD; surowce trzymaj w `/tmp` albo odzyskaj
  `git show <baza>:<ścieżka>` (LESSONS 2026-09-24).
- **`build_gate_manifest.py` nie ma trybu podglądu** — każde uruchomienie
  nadpisuje `data/gates/g001/manifest.json` (LESSONS 2026-09-25).
- **`damp_db` na sustainowanych instrumentach (klarnet/waltornia/organy)
  psuje się, gdy nuty gestu są rozstawione <0,4 s** — sprawdź
  `notes[].on` w geście przed użyciem dampu (LESSONS 2026-09-26).
