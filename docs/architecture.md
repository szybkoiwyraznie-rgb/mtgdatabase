# Architektura

```text
kolekcja.csv (fabuły)
  ↓ analiza semantyczna (agent)
role a·b·c·d z NARRACJI ── braki ──> bramka odsłuchowa (preview :8080 + czat)
  ↓ wybór właściciela (tylko jakość wpisu; „żaden” = runda naprawcza)
data/library/*.json + audio/library/…      (bazy klocków, rosną organicznie)
  ↓ receptura data/recipes/<id>.json
render_signature.py ── QA ──> audio/signatures/<id>.mp3
  ↓
gablotka Pages (build_site.py)   +   płaski ZIP <id>.mp3 (build_pack.py → Release)
```

## Repozytorium

- `kolekcja.csv` → `scripts/import_collection.py` → `data/catalog.json`
  (ID fabuły = liczbowy prefiks artID, np. `123DOM` → `123`).
- `audio/signatures/<id>.mp3` — gotowe produkty (nazwa = numer, bezwzględnie).
- `audio/library/` — przyjęte klocki; `data/library/` — ich rejestry.
- `data/gates/gNNN/` — bramki **commitowane od razu** (manifest, kandydaci,
  `verdicts.json`): sandbox bywa resetowany, a odrzuceni kandydaci wraz
  z notatką właściciela to zapis powodów decyzji dla następnych sesji.
  Buduje je `scripts/build_gate_gNNN.py` — kandydat ma powstawać z kodu,
  nie z ręcznej obróbki pliku.
- `legacy/old-factory/` — zamrożone archiwum dawnego systemu (nie rozwijać,
  nie importować).

## Publikacja

- Deployment Pages: tylko z `main` (workflow `pages.yml`); branch roboczy
  ma build-check (`pages-build.yml`).
- Release ZIP: `release-signatures.yml` z `main` przy zmianach w
  `audio/signatures/`; szyfrowanie opcjonalne przez sekret
  `JINGLE_ZIP_PASSWORD` (nigdy w kodzie).

## Prywatność

Pages (Free) nie jest hostingiem prywatnym. W ZIP i na Pages trafiają
wyłącznie gotowe, zatwierdzone sygnatury; Pages jest **gablotką bez bramek**
(decyzje zapadają w sesji agenta, nie na publicznej stronie). Materiał
bramkowy jest w repozytorium, ale poza buildem Pages.
