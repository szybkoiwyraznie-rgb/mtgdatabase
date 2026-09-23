# Architektura

```text
kolekcja.csv (fabuły)
  ↓ analiza semantyczna (agent)
role a·b·c·d ── braki ──> bramka odsłuchowa (sandbox preview + czat)
  ↓ wybór właściciela
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
- `work/gates/` — robocze pliki bramek (gitignore); manifesty po akceptacji
  archiwizowane w `data/gates/`.
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
wyłącznie gotowe, zatwierdzone sygnatury. Kandydaci bramkowi żyją tylko
w sesji sandboxa (`work/`), nigdy w historii gita.
