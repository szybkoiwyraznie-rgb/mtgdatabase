# Stan produkcji (aktualizuj na końcu każdej sesji)

Ten plik odpowiada na pytanie „gdzie jesteśmy i co robić dalej”, żeby nowa
sesja nie musiała rekonstruować kontekstu z historii gita. Reguły są
w `AGENTS.md` i `docs/gate-protocol.md` — tutaj wyłącznie bieżący stan.

Ostatnia aktualizacja: **2026-09-25** (sesja `arena/01a0d8ef-mtgdatabase`).

## Liczby

- Katalog: **510 fabuł** (`data/catalog.json`), gotowych sygnatur: **30**
  (6 legacy + 24 z modelu 1:1: 18, 23, 28, 90, 110, 126, 166, 169, 193, 222,
  225, 249, 268, 422, **433, 451, 468, 506**, 511, 519, 562, 575, 577, 578).
- Baza klocków: **41 wpisów** (`library_tool.py check`: 11 tła / 13 hero /
  9 gestów / 8 instrumentów), wszystkie z `semantics` (1:1, taksonomia v6).
- Bramki rozegrane z werdyktem: **g001–g030** (g014 wycofana — archiwum).
  g030: mood `groza-przerazenie` → werdykt z.2 → `g_dread_descent` w bazie;
  odblokowało fabuły 433 i 506 bez dodatkowej bramki.
- **Bramka g031 OTWARTA** (patrz „W toku” niżej) — PAKIET 5 zestawów naraz
  (na życzenie właściciela, patrz `AGENTS.md` pkt 2 „Rozmiar paczki”), serwer
  podglądu na `:8080`.

## W toku

**Bramka g031 czeka na werdykt** (`data/gates/g031/index.html`, serwer na
porcie 8080 — proces w tle „Bramka g031 (podgląd)”). Pierwsza bramka po
zmianie zasady na **pakiety ≥5 zestawów naraz** (właściciel, 2026-09-25):
5 wpisów, po 3 kandydatów każdy = 15 klipów do odsłuchu w jednej rundzie.

1. **koda-wspolnota** (mood `wspolnota-wiez`, 34 fabuły, anchor: 585
   „Jolrael, Mwonvuli Recluse”) — w.1 `g_bond_converge` (dystans→jedność),
   w.2 `g_bond_embrace` (równoległe tercje), w.3 `g_bond_echo` (wezwanie
   i odpowiedź).
2. **koda-duma** (mood `duma-majestat`, 31 fabuł, anchor: 64 „Lightwalker”)
   — d.1 `g_pride_broadening`, d.2 `g_pride_ascent`, d.3 `g_pride_spread`
   (wszystkie: „koda rośnie szeroko”).
3. **koda-bezwzglednosc** (mood `bezwzglednosc-drapieznosc`, 31 fabuł,
   anchor: 437 „Giant Spider”) — b.1 `g_ruthless_strike` (jeden zimny cios),
   b.2 `g_ruthless_press` (narastający nacisk + cios), b.3
   `g_ruthless_verdict` (dwa identyczne wyroki).
4. **instr-cieplo** (instrumentacja `cieplo-serdeczna`, 33 fabuły, anchor:
   206 „High Stride”) — c.1 marimba (VCSL, drewniana, ciepła), c.2 waltornia
   sus (VSCO-2-CE), c.3 klarnet susLong (VSCO-2-CE). Prawdziwe nagrania,
   sparse-checkout z github.com/sgossner/{VCSL,VSCO-2-CE} (CC0 1.0).
5. **instr-metal** (instrumentacja `metaliczno-mechaniczna`, 30 fabuł,
   anchor: 191 „Esper Stormblade”) — m.1 kowadło/Anvil (VCSL, bez realnej
   wysokości), m.2 tarcza hamulcowa/Brake Drum Hammer (VCSL, bez realnej
   wysokości), m.3 dzwony rurowe/Tubular Bells 1 (VCSL, tonalne — jedyny
   kandydat z melodią, skala całotonowa D3–E4).

Po werdykcie: `library_tool.py accept --gate g031` → dla KAŻDEGO
zaakceptowanego wpisu sprawdzić `resolver.py --survey`, czy odblokował
fabuły z jedynym takim brakiem (jak zrobiono to dla 433/506 po g030) →
receptura + render `--audit` dla wszystkich nowo obsadzonych.

**Uwaga na przyszłość**: `/tmp/vcsl_probe` i `/tmp/vsco_probe` (sparse
klony VCSL/VSCO-2-CE użyte do zbudowania kandydatów instrumentów g031) NIE
przeżyją resetu sandboksa — jeśli werdykt wybierze m.1/m.2/m.3 lub c.1/c.2/c.3,
`library_tool.py accept` kopiuje pliki z `data/gates/g031/instr_notes/`
(już w gicie po commicie tej sesji), więc nie trzeba klonować ponownie.

## Sesja 2026-09-25 — skrót przebiegu

1. Odziedziczone po poprzedniej sesji zamknięte bramki g025–g029 →
   `resolver.py --survey` pokazał 22 fabuły w pełni obsadzalne → zbudowano
   8 brakujących receptur (249, 90, 126, 268, 422, 511, 562, 577).
2. Naprawiono sortowanie gablotki Pages: oba workflowy `actions/checkout@v4`
   robiły domyślny płytki klon (depth=1), przez co `git log` per plik widział
   jeden commit dla wszystkich plików i sortowanie „najnowsze najwyżej”
   degradowało się do kolejności numerycznej. Naprawa: `fetch-depth: 0`
   w `pages.yml` i `pages-build.yml` + wykrywanie płytkiego repo w
   `build_site.py` (głośne ostrzeżenie w logu builda).
3. Bramka g030 (mood `groza-przerazenie`, 59 fabuł, anchor 433) — werdykt
   właściciela **z.2** (`g_dread_descent`) → do bazy. Odblokowało od razu
   fabuły **433** i **506** (obie miały ten mood jako jedyny brak) —
   wyrenderowane bez dodatkowej bramki.
4. Właściciel poprosił o **większe paczki bramek** (≥5 zestawów naraz,
   nie jeden na raz) — zapisane w `AGENTS.md` pkt 2. Zbudowano bramkę
   **g031** wg nowej zasady: 5 wpisów (3 mood + 2 instrumentacja) × 3
   kandydatów, zakotwiczone na fabułach z dokładnie jednym brakiem
   (585, 64, 437, 206, 191). Pierwszy raz w tej sesji instrumenty
   sourcowane bezpośrednio (sparse-checkout VCSL/VSCO-2-CE z github.com —
   bash MA dostęp do github.com, ale nie do Freesound/NPS/raw.githubusercontent,
   patrz `docs/sources-and-licensing.md`).

Wszystkie 30 receptur przechodzą `library_tool.py check` (kombinacje
unikalne), `test_signature_system.py` (zielone), `build_pack.py` i
`build_site.py` (bez błędów).

## Co dalej (kolejność pracy, nie wymaga pytania właściciela)

1. **Werdykt g031** (5 wpisów naraz) → `library_tool.py accept --gate g031`
   → dla każdego zaakceptowanego typu sprawdzić `resolver.py --survey` pod
   kątem fabuł z jedynym takim brakiem → receptury + render.
2. Kolejni kandydaci na następną PACZKĘ ≥5 (po odjęciu tego, co zamknie
   g031): `hero:rezonans-magiczny` (24), `mood:furia-dzikosc` (24),
   `hero:przemiana-materializacja` (23), `background:miasto-gwar` (23),
   `instrumentacja:zimno-szklista` (21), `hero:potezny-cios` (21),
   `background:swiatynia-sanktuarium` (21), `background:miasto-nocne` (21),
   `background:gory-wichry` (28), `background:podziemia-jaskinia` (28) —
   te dwa ostatnie zostały w kolejce z poprzedniej sesji, prawdopodobnie
   wymagają prawdziwych nagrań terenowych (sample-scout / Freesound) zamiast
   gestów/instrumentów z VCSL — sprawdź `docs/sources-and-licensing.md`.
3. Filtr na anchor fabułę dla nowego typu (kopiuj-wklej do nowej sesji):
   ```python
   import sys, json
   sys.path.insert(0, "scripts")
   import resolver
   data = resolver.load_data()
   matches = [sid for sid in data["profiles"]
              if len(resolver.resolve_story(sid, data)["braki"]) == 1
              and resolver.resolve_story(sid, data)["braki"][0]["layer"] == "mood"  # lub inna warstwa
              and resolver.resolve_story(sid, data)["braki"][0]["typ"] == "TYP"]
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
- **Lokalny git tej sesji bywa płytki/resetowany między turami** — sprawdź
  `git log --oneline -5` na początku tury; jeśli HEAD wygląda staro mimo że
  poprzednia tura commitowała, zrób `git fetch origin <branch>` i porównaj
  z `FETCH_HEAD` (zwykle wystarczy `git reset --hard FETCH_HEAD`, bezpieczne
  gdy `git diff FETCH_HEAD` na working tree wychodzi pusty).
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
