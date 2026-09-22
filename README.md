# Fabryka jingli fabularnych

Prywatny, niekomercyjny pipeline do projektowania, renderowania, oceniania i iteracyjnego poprawiania krótkich form dźwiękowych na podstawie fabuł z CSV.

## Cel

Agent najpierw audytuje poprzedni PR i stan kodu, naprawia znalezione problemy, następnie w każdej pętli tworzy jingle dla nowych fabuł oraz wykonuje remake najgorzej ocenionego istniejącego jingla. Wyniki publikuje w panelu odsłuchowym GitHub Pages, przyjmuje trzy oceny liczbowe i komentarz, a równolegle rozwija dokumentację, narzędzia i bibliotekę sampli.

## Stan projektu

Repozytorium zawiera fundament procesu, aktualną kolekcję `kolekcja.csv` oraz pięć produkcyjnych jingli `v1` (fabuły 1–5; audio w `legacy/source/jingle_output/`, stan ocen w `data/versions.json`). Kolekcja ma format TSV `Ilustracja`, `Nazwa Karty`, `Narracja`; z artID, np. `123DOM`, importer wyciąga numer `123`, który jest ID jingla i nazwą pliku `123.mp3`. Sufiks setu jest zachowany w metadanych, ale nie bierze udziału w produkcji.

## Zasady produktu

- każda fabuła może mieć wiele wersji `v1`, `v2`, `v3`;
- każda wersja ma opis projektowy z użytymi samplami i timestampami efektów;
- nowe wersje nie usuwają starszych;
- ocena to suma: feeling + zgodność z fabułą + jakość sampli, każda 1–5;
- ocena pokazuje się od razu na urządzeniu oceniającego, a po automatycznej synchronizacji z issues trafia do `data/versions.json` i na wszystkie urządzenia;
- ZIP zawiera jedną najwyżej ocenioną, już ocenioną wersję każdej fabuły;
- ZIP jest płaski i zawiera wyłącznie `id.mp3`;
- paczka jest publikowana jako asset GitHub Release i pojawia się automatycznie po pierwszych ocenach; bez sekretu `JINGLE_ZIP_PASSWORD` ZIP jest nieszyfrowany;
- Pages służy do odsłuchu i wysyłania raportów.

## Dokumentacja

- [`AGENTS.md`](AGENTS.md) — obowiązkowy kontrakt dla agentów;
- [`docs/agent-workflow.md`](docs/agent-workflow.md) — pętla produkcyjna;
- [`docs/architecture.md`](docs/architecture.md) — architektura repozytorium i publikacji;
- [`docs/feedback-system.md`](docs/feedback-system.md) — model ocen i komunikacja z GitHubem;
- [`docs/sources-and-licensing.md`](docs/sources-and-licensing.md) — rejestr źródeł sampli;
- [`ENVIRONMENT.md`](ENVIRONMENT.md) — ograniczenia i pułapki Agent Arena;
- [`docs/LESSONS.md`](docs/LESSONS.md) oraz [`docs/decisions/`](docs/decisions/) — trwała wiedza i decyzje.

## Narzędzia

Wstępny skrypt paczki najlepszych jingli:

```bash
python scripts/build_best_zip.py \
  --versions data/versions.json \
  --output build/best-jingles-latest.zip
```

Render nowej wersji z receptury (`pip install numpy soundfile lameenc` w venv; narzędzie autorskie poza CI):

```bash
python scripts/render_jingle.py data/recipes/<id>_<vN>.json \
  --out legacy/source/jingle_output/<id>[_<vN>].mp3 --print-description
```

Przed uruchomieniem produkcji należy skonfigurować publikację Pages, endpoint raportów oraz sekret szyfrowania ZIP-a. Instrukcja konfiguracji zostanie uzupełniona w kolejnym etapie wraz z pierwszym działającym panelem.
