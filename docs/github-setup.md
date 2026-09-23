# Jednorazowa konfiguracja GitHuba

Instrukcja dla właściciela repozytorium.

## Pages (gablotka)

`Settings → Pages → Source: GitHub Actions`, potem
`Actions → Publish signature gallery → Run workflow` (albo merge do `main`).
Strona pokazuje katalog fabuł i gotowe sygnatury do odsłuchu.
Nie jest to narzędzie decyzji — bramki odbywają się w sesji agenta
(`docs/gate-protocol.md`).

## Paczka ZIP

Przy każdej zmianie w `audio/signatures/` na `main` workflow
`Build signatures release` publikuje płaski `signatures-latest.zip`
(nazwy `<id>.mp3`) jako asset rolling release. Opcjonalne szyfrowanie:
sekret `JINGLE_ZIP_PASSWORD` w `Settings → Secrets and variables → Actions`;
bez niego ZIP jest nieszyfrowany. Hasło nigdy nie trafia do repozytorium.

## Sample scout

Workflow `Sample scout` (uruchamiany ręcznie z `main`) pobiera kandydatów
CC0 z Freesound (sekret `FREESOUND_TOKEN` opcjonalny) i Internet Archive do
`legacy/source/sample_scout/`. Kandydaci trafiają potem na bramki
odsłuchowe — nie do produkcji automatycznie.

## Usunięte elementy starego systemu

Feedback worker, workflow synchronizacji ocen i paczka „best jingles"
nie istnieją (ADR 0003). Ich konfiguracja nie jest już potrzebna.
