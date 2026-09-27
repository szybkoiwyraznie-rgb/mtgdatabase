# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-27** (sesja `arena/01a0dd2c-mtgdatabase`).

## Liczby

- Katalog: **510 fabuł** (`data/catalog.json`), gotowych sygnatur: **64**
  (legacy 1–4 + model 1:1: 5, 8, 18, 23, 28, 55, 64, 72, 76, 84, 85, 95,
  110, 126, 133, 146, 166, 169, 175, 179, 188, 191, 193, 211, 215, 222,
  224, 225, 227, 249, 277, 282, 287, 290, 299, 337, 354, 382, 393, 401,
  422, 428, 433, 437, 451, 468, 474, 489, 496, 498, 499, 506, 511, 519,
  562, 575, 577, 578, 579, 585).
- Baza klocków: **56 wpisów** (`library_tool.py check`: 13 teł / 17 hero /
  15 gestów / 11 instrumentów — wszystkie z `semantics`, model 1:1,
  taksonomia v6 + pending typy dla braków).
- Bramki rozegrane z werdyktem i przyjęciem do biblioteki: **g001–g034**
  (g014 wycofana — archiwum). g034 zamknięta częściowo decyzjami właściciela:
  przyjęte tylko `hero-ogien=o.2` → `fire_roar_thruster_01`; odrzucone
  `tlo-step` (za głośne, `s.3` z muzyką), `tlo-kuznia` (brak miarowego kucia),
  `tlo-krypta` (nekropolia = cisza, nie target audio) i `hero-mechanizm`
  (nie ma uniwersalnego mechanizmu).
- `resolver.py --survey` po audycie/renderach po g034: **63** fabuły w pełni
  obsadzalne dziś (lista z survey nie zawiera części legacy), **445** z
  częściową obsadą. Bez receptury, mimo statusu `OBSADZONA`, zostają tylko
  **309** i **502** — technicznie nie przeszły QA renderu. Największe braki:
  `background:miasto-gwar`, `background:swiatynia-sanktuarium`,
  `background:noc-ksiezyc`, `background:miasto-nocne`,
  `background:laboratorium-technika`, `background:wioska-sielska`,
  `background:step-rownina`, `background:kuznia-warsztat`.
- **Wycofane po audycie semantycznym gotowych**: **90, 206, 268, 599**.
  Usunięto ich receptury i MP3; klasy skorygowano tak, żeby resolver zwracał
  BRAK zamiast ponownie obsadzić zły klocek. Pełny audyt:
  `docs/audits/2026-09-26-audyt-gotowych-sygnatur.md`.
- **Fałszywie pełne po g032, zablokowane przed renderem**: **79, 253, 309,
  428, 560, 607**. Pełny audyt i uzasadnienia:
  `docs/audits/2026-09-26-audyt-po-g032.md`.

## W toku

- PR: `https://github.com/szybkoiwyraznie-rgb/mtgdatabase/pull/38` na gałęzi
  `arena/01a0dd2c-mtgdatabase`. Zawiera audyt gotowych, przyjęcie g032, produkcję po g032, przyjęcie 4/5
  wpisów z g033, 15 renderów po g033, bramkę g034, werdykt g034, 5
  renderów po g034 oraz otwartą bramkę g035.
- Po g034 wyrenderowano 5 fabuł: `72`, `146`, `287`, `290`, `496`.
  Zablokowane pozostają: `104` i `528` semantycznie po g033 oraz `309` i `502`
  technicznie po QA. Pełne zapisy: `docs/audits/2026-09-27-audyt-po-g033.md`
  i `docs/audits/2026-09-27-audyt-po-g034.md`.
- Po korekcie właściciela **nie używać** `background:krypta-nekropolia` ani
  `hero:furkot-mechanizmu` jako targetów produkcyjnych. Oba mają 0 aktywnych
  przypisań; mechanizmy rozbijane są na konkretne typy pending.
- **Pivot po g035**: ręczne bramki nie są już główną ścieżką produkcji.
  Nowy kierunek v2: jedna fabuła → jeden prompt SFX → jeden MP3 z ElevenLabs
  → płaski ZIP. Szczegóły: `docs/ai-sfx-pipeline.md`.
- `g035` istnieje w repo jako ostatnia przygotowana bramka, ale po decyzji o
  pivocie nie jest blokującym etapem produkcji.
- `mood:wladza-kontrola` nadal bez klocka w starym modelu v1; w v2 nie blokuje
  produkcji, bo każda fabuła generuje własny efekt z promptu.
- Przed oddaniem/mergem utrzymać pełną walidację: `check_required_reading`,
  `compileall`, `test_signature_system`, `library_tool.py check`,
  `build_pack`, `build_site`, `git diff --check`, a po pushu sprawdzić CI PR.

## Sesja 2026-09-27 — pivot do AI SFX v2

1. Po decyzji właściciela zatrzymano manualny flow bramek jako główną ścieżkę.
2. Dodano pipeline v2: `scripts/generate_ai_sound_prompts.py`,
   `scripts/elevenlabs_soundgen.py` i workflow
   `.github/workflows/ai-sfx-elevenlabs.yml`.
3. Workflow jest manualny i wymaga repo secret `ELEVENLABS_API_KEY`; generuje
   artifact z `ai-signatures-latest.zip`, promptami i manifestem generacji.
4. `import_collection.py` i `validate_stories.py` przyjmują teraz obecny TSV
   z rozszerzeniem `.csv` oraz prawdziwy CSV.

## Sesja 2026-09-27 — g035 przygotowana przed pivotem

1. Przygotowano bramkę `g035` z pięcioma wpisami tła: cichy step, miarowa
   kuźnia, noc księżycowa, laboratorium techniczne i sanktuarium.
2. Po decyzji o przejściu na AI SFX v2 `g035` traktować jako ostatni artefakt
   starego flow, nie jako blokujący krok produkcji.

## Sesja 2026-09-27 — g034 i produkcja po audycie

1. Właściciel zamknął g034: zaakceptował tylko `hero-ogien=o.2`, odrzucił
   step, kuźnię, kryptę/nekropolię i uniwersalny mechanizm.
2. Do biblioteki wszedł `heroes/fire_roar_thruster_01` (`hero:huk-ognia`).
3. Po korekcie semantycznej usunięto wszystkie aktywne użycia
   `background:krypta-nekropolia` i `hero:furkot-mechanizmu`. Nekropolie
   zastąpiono konkretnymi słyszalnymi tłami; mechanizmy rozbito na typy per
   mechanizm.
4. Sanity audit nowo pełnych zablokował fałszywe ognie: `59`
   (`plomien-kontrolowany`), `209` (`plomien-pochodni`), `314`
   (`szelest-papieru` + podziemia) i `513` (`mroczna-fala`).
5. Wyrenderowano bez `--force` pięć sygnatur: `72`, `146`, `287`, `290`,
   `496`. `309` i `502` pozostają pełne semantycznie, ale bez receptur/MP3
   przez techniczne QA.

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

1. Najpierw wrócić do blokad tylko świadomie: `309` i `502` są pełne
   semantycznie, ale nie mają receptur/MP3, bo obecne kombinacje gest×instrument
   nie przechodzą QA; `104` i `528` wymagają nowych teł (`miasto-neonowe`,
   `dom-nawiedzony`).
2. Następna bramka po g034 powinna dalej brać typy z największych realnych
   braków: `background:miasto-gwar`, `background:swiatynia-sanktuarium`,
   `background:noc-ksiezyc`, `background:miasto-nocne`,
   `background:laboratorium-technika`, `background:wioska-sielska`,
   `background:step-rownina`, `background:kuznia-warsztat`.
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
