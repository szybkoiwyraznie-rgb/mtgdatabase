# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-26** (sesja `arena/01a0dd2c-mtgdatabase`).

## Liczby

- Katalog: **510 fabuł** (`data/catalog.json`), gotowych sygnatur: **44**
  (legacy 1–4 + model 1:1: 5, 8, 18, 23, 28, 55, 64, 76, 84, 95, 110,
  126, 133, 166, 169, 179, 188, 191, 193, 222, 224, 225, 249, 277, 282,
  299, 422, 433, 437, 451, 468, 498, 506, 511, 519, 562, 575, 577, 578,
  585).
- Baza klocków: **51 wpisów** (`library_tool.py check`: 11 teł / 15 hero /
  14 gestów / 11 instrumentów — wszystkie z `semantics`, model 1:1,
  taksonomia v6 + pending typy dla braków).
- Bramki rozegrane z werdyktem i przyjęciem do biblioteki: **g001–g032**
  (g014 wycofana — archiwum). g032 zamknięta decyzjami właściciela:
  `koda-furia=f.3`, `koda-zuchwalosc=z.2`, `hero-rezonans=r.1`,
  `hero-potezny=p.2`, `instr-zimno=i.1` → do bazy weszły:
  `g_feral_stampede`, `g_brave_swagger`, `resonance_bowed_01`,
  `heavyblow_gong_01`, `b_vibraphone_cold`. **g033 jest otwarta**:
  5 wpisów × 3 kandydatów (`tlo-podziemia`, `tlo-gory`,
  `hero-przemiana`, `koda-intryga`, `koda-wladza`), czeka na werdykty.
- `resolver.py --survey` po sanity audycie po g032: **40** fabuł w pełni
  obsadzalnych dziś (lista z survey nie zawiera legacy 1–4), **467** z
  częściową obsadą. Największe braki: `background:podziemia-jaskinia`,
  `background:gory-wichry`, `hero:przemiana-materializacja`,
  `background:miasto-gwar`, `background:swiatynia-sanktuarium`,
  `background:miasto-nocne`, `background:laboratorium-technika`,
  `background:wioska-sielska`.
- **Wycofane po audycie semantycznym gotowych**: **90, 206, 268, 599**.
  Usunięto ich receptury i MP3; klasy skorygowano tak, żeby resolver zwracał
  BRAK zamiast ponownie obsadzić zły klocek. Pełny audyt:
  `docs/audits/2026-09-26-audyt-gotowych-sygnatur.md`.
- **Fałszywie pełne po g032, zablokowane przed renderem**: **79, 253, 309,
  428, 560, 607**. Pełny audyt i uzasadnienia:
  `docs/audits/2026-09-26-audyt-po-g032.md`.

## W toku

- PR: `https://github.com/szybkoiwyraznie-rgb/mtgdatabase/pull/38` na gałęzi
  `arena/01a0dd2c-mtgdatabase`. Zawiera audyt gotowych, przyjęcie g032,
  produkcję po g032 oraz otwartą bramkę g033.
- **g033 do werdyktu właściciela**: `tlo-podziemia: p.1/p.2/p.3`,
  `tlo-gory: g.1/g.2/g.3`, `hero-przemiana: m.1/m.2/m.3`,
  `koda-intryga: i.1/i.2/i.3`, `koda-wladza: w.1/w.2/w.3` albo
  `żaden` z powodem dla danego wpisu.
- Przed oddaniem/mergem utrzymać pełną walidację: `check_required_reading`,
  `compileall`, `test_signature_system`, `library_tool.py check`,
  `build_pack`, `build_site`, `git diff --check`, a po pushu sprawdzić CI PR.

## Sesja 2026-09-26 — skrót przebiegu

1. Po reklamacji właściciela dotyczącej fabuły 206 wykonano audyt wszystkich
   gotowych sygnatur. Wycofano cztery twarde pomyłki semantyczne: 90, 206,
   268, 599. Gotowe spadły z 38 do 34.
2. Właściciel uzupełnił brakujący werdykt g032 (`r1`). Przyjęto 5 klocków do
   biblioteki: 2 gesty, 2 hero i 1 instrument.
3. Po g032 resolver wskazał 16 nowych fabuł jako pełne. Zgodnie z lekcją z
   206 wykonano sanity audit przed renderem:
   - wyrenderowano 10: 55, 76, 84, 95, 179, 188, 224, 277, 282, 299;
   - zablokowano 6 fałszywych trafień: 79, 253, 309, 428, 560, 607.
4. Najważniejsze korekty klas po g032: 76→`niebo-przestworza`,
   79→`pustkowie-cisza`, 179→`radosc-beztroska`, 224→`nieuchronnosc-fatum`,
   253→`aura-lagodna`, 309→`przemiana-materializacja`,
   428→`podziemia-jaskinia`, 560→pending `twierdza-posepna`,
   607→`wladza-kontrola`.
5. Aktualnie **44** receptury/sygnatury przechodzą `library_tool.py check`;
   żadnego nowego renderu nie zapisano z `--force`.

## Co dalej (kolejność pracy, nie wymaga pytania właściciela)

1. Najpierw zamknąć **g033** po werdykcie właściciela: wpisać wybory do
   `data/gates/g033/verdicts.json`, uruchomić
   `python3 scripts/library_tool.py accept --gate g033`, potem `resolver.py --survey`
   i sanity audit nowo odblokowanych fabuł przed renderem.
2. Następna bramka po g033 powinna dalej brać typy z największych realnych
   braków, zwłaszcza te nieobjęte g033: `background:miasto-gwar`,
   `background:swiatynia-sanktuarium`, `background:miasto-nocne`,
   `background:laboratorium-technika`, `background:wioska-sielska`.
3. W tej samej kolejce uwzględniać braki ujawnione audytami właściciela:
   `background:zatoka-spokojna` (90), `hero:stukot-szczudel` (206),
   `hero:aura-lagodna` (253/268), `background:las-mroczny` (599),
   `background:twierdza-posepna` (560), `mood:wladza-kontrola` (607).
4. Po każdej nowej bramce NIE batch-renderować samej listy `OBSADZONA`.
   Najpierw wypisz nowo pełne bez receptury i wykonaj sanity audit narracja →
   klasa → konkretny klocek. Dopiero potem renderuj.
5. Filtr na anchor fabułę dla nowego typu (kopiuj-wklej do nowej sesji):
   ```python
   import sys
   sys.path.insert(0, "scripts")
   import resolver
   data = resolver.load_data()
   for sid in data["profiles"]:
       r = resolver.resolve_story(sid, data)
       if (len(r["braki"]) == 1
               and r["braki"][0]["layer"] == "TYP_WARSTWY"
               and r["braki"][0]["typ"] == "TYP"):
           print(sid, r["title"])
   ```
6. Ostrożnie z `scripts/build_gate_manifest.py` — jednorazowy legacy builder
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
