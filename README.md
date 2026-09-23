# Sygnatury fabularne

Prywatny, niekomercyjny system warstwy dźwiękowej do gry fabularnej: każda
fabuła z `kolekcja.csv` dostaje jedno „okno dźwiękowe" (do 10 s) złożone
z czterech zatwierdzonych klocków — **tło + hero + koda muzyczna + instrument**.

## Jak to działa

1. Agent analizuje fabułę semantycznie i dobiera klocki z czterech baz
   (`data/library/*.json`). Bazy **rosną organicznie** — zaczęły się puste.
2. Brakujące klocki idą przez **bramkę odsłuchową**: minimum 3 kandydatów
   na slot, właściciel wybiera jednego (albo odrzuca wszystkich) w czacie,
   wybrany trafia do bazy na stałe.
3. Z zatwierdzonych klocków agent składa recepturę i renderuje
   `audio/signatures/<id>.mp3` — deterministycznie, z bramkami QA (montaż,
   nie „ocena gustu").
4. Pages to gablotka gotowych sygnatur; ZIP w Releases to płaski pakiet
   `<id>.mp3` budowany z `audio/signatures/`.

Dokumenty: [`docs/signature-system.md`](docs/signature-system.md) —
architektura, [`docs/gate-protocol.md`](docs/gate-protocol.md) — protokół
bramki, [`AGENTS.md`](AGENTS.md) — kontrakt pracy. Dawna „fabryka jingli"
(zamieniona 2026-09-23) leży w `legacy/old-factory/`.

## Narzędzia

```bash
pip install numpy soundfile lameenc av   # venv pod audio

python scripts/render_signature.py data/recipes/<id>.json --audit   # render sygnatury
python scripts/gate_preview.py work/gates/gNNN --port 8080          # bramka odsłuchowa
python scripts/library_tool.py check                                # walidacja baz + unikalność
python scripts/library_tool.py accept --gate gNNN                   # po werdykcie właściciela
python scripts/build_pack.py                                        # ZIP <id>.mp3
python scripts/build_site.py                                        # gablotka Pages
python scripts/stem_probe.py <nagranie>                             # audycja przed cięciem
python scripts/make_stem.py <nagranie> --start S --end E --out ...  # stem kandydata
```

Źródła sampli i licencje: `docs/sources-and-licensing.md`. Zweryfikowane
pobieranie: `git clone` (sparse) z github.com; fallback: workflow Sample scout.
