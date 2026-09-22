# Jednorazowa konfiguracja GitHuba

Ten dokument jest instrukcją dla właściciela repozytorium. Workflow i pliki przygotowujemy na branchu roboczym; nie scalaj pull requesta, dopóki nie zakończymy konfiguracji.

## Pages

Po scaleniu PR `Settings → Pages → Source: GitHub Actions`, a następnie `Actions → Publish Pages preview → Run workflow`.

Workflow Pages waliduje i importuje aktualny `kolekcja.csv`. Lokalny katalog demonstracyjny może nadal używać `data/catalog.example.json` i pięciu plików z materiałów prototypowych.

## Raporty ocen

Raporty wymagają wdrożenia workera z katalogu `feedback-worker/`. Instrukcja znajduje się w jego README. Po wdrożeniu adres workera trzeba wpisać do pliku konfiguracyjnego Pages. Token GitHub zapisuje się wyłącznie jako sekret workera.

## Paczka ZIP

Po pojawieniu się `data/versions.json` workflow `Build best jingles release` zbuduje `best-jingles-latest.zip` i opublikuje go jako GitHub Release. Opcjonalne szyfrowanie:

1. Wejdź w `Settings → Secrets and variables → Actions`.
2. Utwórz sekret `JINGLE_ZIP_PASSWORD`.
3. Wartość sekretu ustaw jako PIN do ZIP-a.

Bez tego sekretu workflow opublikuje zwykły ZIP. Hasło nigdy nie jest zapisywane w repozytorium.
