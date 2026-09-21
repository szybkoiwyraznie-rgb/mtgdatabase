# Jednorazowa konfiguracja GitHuba

Ten dokument będzie uzupełniany wraz z kolejnymi elementami systemu.

## Pages

Po włączeniu workflow `Publish Pages preview`:

1. Wejdź w `Settings → Pages` repozytorium.
2. Jako źródło wybierz `GitHub Actions`.
3. Uruchom workflow ręcznie z zakładki `Actions` albo wypchnij zmianę na branch.
4. Adres strony pojawi się w jobie `deploy` oraz w `Settings → Pages`.

Na tym etapie strona jest wersją demonstracyjną z pięcioma plikami z materiałów prototypowych. Docelowy CSV zastąpi `data/catalog.example.json`.

## Następne sekrety

Nie ustawiaj jeszcze żadnych sekretów. W późniejszym kroku skonfigurujemy osobno:

- endpoint przyjmujący raporty ocen;
- `JINGLE_ZIP_PASSWORD` do szyfrowania paczki;
- publikację `best-jingles-latest.zip` jako GitHub Release.
