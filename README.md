# Fabryka jingli fabularnych

Prywatny, niekomercyjny pipeline do projektowania, renderowania, oceniania i iteracyjnego poprawiania krótkich form dźwiękowych na podstawie fabuł z CSV.

## Cel

Agent najpierw audytuje poprzedni PR i stan kodu, naprawia znalezione problemy, następnie w każdej pętli tworzy jingle dla nowych fabuł oraz wykonuje remake najgorzej ocenionego istniejącego jingla. Wyniki publikuje w panelu odsłuchowym GitHub Pages, przyjmuje trzy oceny liczbowe i komentarz, a równolegle rozwija dokumentację, narzędzia i bibliotekę sampli.

## Stan projektu

Repozytorium zawiera fundament procesu oraz materiały prototypowe przeniesione do `legacy/source/` z dostarczonego archiwum. Docelowy CSV z kolumnami `id,title,story` zostanie podmieniony przed uruchomieniem produkcyjnej kolejki.

## Zasady produktu

- każda fabuła może mieć wiele wersji `v1`, `v2`, `v3`;
- nowe wersje nie usuwają starszych;
- ocena to suma: feeling + zgodność z fabułą + jakość sampli, każda 1–5;
- ZIP zawiera jedną najwyżej ocenioną, już ocenioną wersję każdej fabuły;
- ZIP jest płaski i zawiera wyłącznie `id.mp3`;
- paczka będzie publikowana jako asset GitHub Release, opcjonalnie jako szyfrowany ZIP;
- Pages służy do odsłuchu i wysyłania raportów.

## Dokumentacja

- [`AGENTS.md`](AGENTS.md) — obowiązkowy kontrakt dla agentów;
- [`docs/agent-workflow.md`](docs/agent-workflow.md) — pętla produkcyjna;
- [`docs/architecture.md`](docs/architecture.md) — architektura repozytorium i publikacji;
- [`docs/feedback-system.md`](docs/feedback-system.md) — model ocen i komunikacja z GitHubem;
- [`docs/sources-and-licensing.md`](docs/sources-and-licensing.md) — rejestr źródeł sampli.

## Narzędzia

Wstępny skrypt paczki najlepszych jingli:

```bash
python scripts/build_best_zip.py \
  --versions data/versions.json \
  --output build/best-jingles-latest.zip
```

Przed uruchomieniem produkcji należy skonfigurować publikację Pages, endpoint raportów oraz sekret szyfrowania ZIP-a. Instrukcja konfiguracji zostanie uzupełniona w kolejnym etapie wraz z pierwszym działającym panelem.
