# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-26** (sesja `arena/01a0dd2c-mtgdatabase`).

## Liczby

- Katalog: **510 fabuł** (`data/catalog.json`), gotowych sygnatur: **34**
  (6 legacy + 28 z modelu 1:1: 18, 23, 28, 64, 110, 126, 133, 166, 169,
  191, 193, 222, 225, 249, 422, 433, 437, 451, 468, 498, 506, 511, 519,
  562, 575, 577, 578, 585).
- Baza klocków: **46 wpisów** (`library_tool.py check`: 11 tła / 13 hero /
  14 gestów / 9 instrumentów — wszystkie z `semantics`, model 1:1, taksonomia v6).
- Bramki rozegrane z werdyktem i przyjęciem do biblioteki: **g001–g031**
  (g014 wycofana — archiwum). **g032 jest otwarta**: właściciel podał
  werdykt częściowy `f3, z2, p2, i1`; kandydaci `r.1–r.3` dla
  `hero-rezonans` nie grały w odsłuchu, więc zostały przebudowane z
  głośniejszych/aktywnych okien VCSL i czekają na ponowny wybór `r.*`.
- **Wycofane po audycie semantycznym gotowych**: **90, 206, 268, 599**.
  Usunięto ich receptury i MP3 z `audio/signatures/`; klasy skorygowano tak,
  żeby resolver zwracał BRAK zamiast ponownie obsadzić zły klocek:
  90→`background:zatoka-spokojna` (pending), 206→`hero:stukot-szczudel`
  (pending), 268→`hero:aura-lagodna` (typ istniejący bez klocka),
  599→`background:las-mroczny` (typ istniejący bez klocka). Pełny audyt:
  `docs/audits/2026-09-26-audyt-gotowych-sygnatur.md`.
- **Jedna fabuła zablokowana strukturalnie**: **253** (Inspiring Bard) —
  `g11c_home_arrival` × `b_clarinet_warm` nie przechodzi bramki ataku nut przy
  żadnej kombinacji parametrów (silnik `damp_db` konfliktuje z odstępem nut
  <0,4 s — pełna diagnoza w `docs/LESSONS.md` 2026-09-26). Nie wyrenderowana,
  `data/recipes/253.json` nie istnieje (świadomie usunięty, nie zapomniany).

## W toku

1. **Dokończyć g032** — podgląd działa na `:8080` po uruchomieniu:
   `python3 scripts/gate_preview.py data/gates/g032 --port 8080`.
   Brakuje tylko werdyktu dla `hero-rezonans` (`r.1`, `r.2`, `r.3` albo
   „żaden — powód”). Po kompletnym werdykcie uruchomić
   `python3 scripts/library_tool.py accept --gate g032`, potem `resolver.py --survey`
   i renderować odblokowane fabuły.
2. Po audycie gotowych nie wracać automatycznie do 90/206/268/599 na starych
   typach. Ich naprawa wymaga brakujących klocków/typów wskazanych wyżej.

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
4. `resolver.py --survey` po przyjęciu → 9 nowych fabuł w pełni
   obsadzalnych: 64, 133, 191, 206, 253, 437, 498, 585, 599. Wyrenderowano
   8 z 9 (253 zablokowana technicznie).
5. **Korekta po pytaniu właściciela 2026-09-26:** 206 była błędną obsadą
   (`marsz-oddzialu`/`troop_march_05` dla pojedynczego królika na szczudłach).
   Audyt wszystkich gotowych wykrył i wycofał analogiczne naciągnięcia:
   90 (spokojna zatoka ≠ sztormowe wybrzeże), 268 (aura ≠ wodny rozbryzg),
   599 (nocny rytuał ≠ las za dnia). Gotowe spadły z 38 do 34.
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

Aktualnie 34 receptury przechodzą `library_tool.py check` (kombinacje
unikalne). Po wycofaniu 90/206/268/599 trzeba ponownie budować pack/site
przed publikacją końcową.

## Co dalej (kolejność pracy, nie wymaga pytania właściciela)

1. **Najpierw domknij g032** — brakuje tylko wyboru `r.*` dla
   `hero-rezonans`. Po `accept` od razu uruchom `resolver.py --survey` i
   renderuj fabuły odblokowane przez `furia-dzikosc`, `zuchwalosc-brawura`,
   `rezonans-magiczny`, `potezny-cios`, `zimno-szklista`.
2. Następna paczka po g032 powinna uwzględniać również braki ujawnione
   audytem: `background:zatoka-spokojna` (90), `hero:stukot-szczudel` (206),
   `hero:aura-lagodna` (268; typ jest w taksonomii, brak klocka),
   `background:las-mroczny` (599; typ jest w taksonomii, brak klocka).
3. **253 do rewizytacji**: jeśli w przyszłości pojawi się DRUGI kandydat na
   typ instrumentacji `cieplo-serdeczna` (obecnie tylko `b_clarinet_warm`),
   sprawdź czy nowy klocek przechodzi bramkę dla tej konkretnej fabuły — ale
   to wymaga zmiany modelu 1:1 (dwa klocki tego samego typu), nie rób tego
   bez zgody właściciela. Alternatywa: edycja `pre` w `coda_synth.py` (0,4 s
   → mniej) — dotyka WSZYSTKICH receptur z `damp_db`, wymaga pełnej regresji
   (`test_signature_system.py` + ręczny przegląd audytów istniejących
   receptur z dampem: 433, 506, 511, 575).
4. Filtr na anchor fabułę dla nowego typu (kopiuj-wklej do nowej sesji):
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
5. Ostrożnie z `scripts/build_gate_manifest.py` — jednorazowy legacy builder
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
