# Jednorazowa konfiguracja GitHuba

Ten dokument jest instrukcją dla właściciela repozytorium. Workflow i pliki przygotowujemy na branchu roboczym; nie scalaj pull requesta, dopóki nie zakończymy konfiguracji.

## Pages

Po scaleniu PR `Settings → Pages → Source: GitHub Actions`, a następnie `Actions → Publish Pages preview → Run workflow`.

Workflow Pages waliduje i importuje aktualny `kolekcja.csv`. Lokalny katalog demonstracyjny może nadal używać `data/catalog.example.json` i pięciu plików z materiałów prototypowych.

## Raporty ocen

Raporty wymagają wdrożenia workera z katalogu `feedback-worker/`. Deployment odbywa się zdalnie przez `Actions → Deploy feedback worker → Run workflow`; nie trzeba instalować niczego na desktopie. Przed uruchomieniem dodaj sekrety `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` i `WORKER_GITHUB_TOKEN`. Po wdrożeniu adres workera trzeba wpisać do pliku konfiguracyjnego Pages. Token GitHub jest przekazywany wyłącznie jako sekret Cloudflare.

## Synchronizacja ocen

Workflow `Sync ratings from issues` nie wymaga żadnych sekretów — działa na wbudowanym tokenie Actions. Odpala się przy każdym nowym/edytowanym issue z etykietą `feedback`, dopisuje oceny do `data/versions.json`, a potem automatycznie przebudowuje Pages i paczkę ZIP.

## Paczka ZIP

Po pojawieniu się `data/versions.json` z ocenionymi wersjami workflow `Build best jingles release` zbuduje `best-jingles-latest.zip` i opublikuje go jako GitHub Release (link w kolumnie Releases na stronie repo). Bez sekretu szyfrowania ZIP jest nieszyfrowany. Opcjonalne szyfrowanie:

1. Wejdź w `Settings → Secrets and variables → Actions`.
2. Utwórz sekret `JINGLE_ZIP_PASSWORD`.
3. Wartość sekretu ustaw jako PIN do ZIP-a.

Bez tego sekretu workflow opublikuje zwykły ZIP. Hasło nigdy nie jest zapisywane w repozytorium.
