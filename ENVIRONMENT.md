# Środowisko Agent Arena

Ten plik jest obowiązkową lekturą dla każdego agenta. Zawiera zasady specyficzne dla pracy w sandboxie Arena; decyzje dotyczące produktu pozostają w `AGENTS.md`, ADR-ach i `docs/LESSONS.md`.

## 1. Trwałość pracy

Nowa sesja może wystartować z czystego klona. Przetrwa tylko to, co zostało
zapisane w repozytorium, zacommitowane i wypchnięte na GitHub.

- Commituj i pushuj często — także materiał roboczy bramek (`data/gates/`).
  Snapshot workspace wyłącza z zapisu m.in. `.venv/`, `work/`, `build/`, `/tmp`
  (biblioteki źródeł klonujemy ponownie) i **może cofnąć lokalny stan gita**.
- Nie polegaj na historii rozmowy ani plikach w `/tmp`.
- Po restarcie sandboxa odtwórz środowisko: `python3 -m venv .venv &&
  .venv/bin/pip install numpy soundfile lameenc av scipy pytest`
  (**scipy** i **pytest** też są potrzebne: filtry w skryptach bramek
  i zestaw testów). Biblioteki źródeł klonuj ponownie do `/tmp` —
  patrz `docs/sources-and-licensing.md`.
- Otwieraj pull request na swój branch od razu po pierwszym pushu sesji —
  praca jest wtedy widoczna także poza sandboxem.
- Przed resetem, checkoutem lub zmianą branchu sprawdź `git status` i wykonaj kopię niezacommitowanych zmian.
- Pracuj wyłącznie na branchu roboczym bieżącej sesji Arena (format `arena/<id>-mtgdatabase`, wskazanym w konfiguracji sesji); nie twórz ani nie pushuj innych branchy. Jeśli nie masz pewności, który branch jest Twoim branchem sesji, sprawdź `git branch --show-current` i status sesji w Arena.
- Nie pushuj bezpośrednio do `main`.

## 2. Ochrona przed resetem workspace

Jeśli HEAD niespodziewanie wskazuje bazę albo zniknęły commity:

```bash
git status --porcelain
git diff > /tmp/arena-recovery.patch
git fetch origin <branch-sesji>   # np. arena/01a0c8f1-mtgdatabase
git reset --mixed FETCH_HEAD
```

`--mixed` zachowuje pliki i pozwala odzyskać niezacommitowane zmiany. `git reset --hard` wolno wykonać dopiero po sprawdzeniu, że drzewo robocze jest czyste albo po wykonaniu kopii.

## 3. GitHub i uwierzytelnienie

- Do operacji lokalnych używaj `git`, a do PR-ów, issue, workflowów i Releases używaj `gh`.
- Nigdy nie proś właściciela o hasła, tokeny ani kody 2FA w czacie.
- Jeśli `git push` lub `gh` zwróci błąd uwierzytelnienia, poproś o reconnect GitHub w Arena.
- **Token sesji to GitHub App bez `actions:write`.** `gh workflow run`,
  `gh api .../actions/workflows/*/dispatches` i `gh api user` zwracają
  `HTTP 403: Resource not accessible by integration`. To nie jest awaria
  połączenia i **nie proś właściciela o uprawnienia ani token** — użyj
  `repository_dispatch` (wymaga tylko `contents:write`), jak w workflow
  Sample scout. Odczyt (`gh run list`, `gh pr ...`) działa normalnie.
- `gh pr edit` może zgłaszać ostrzeżenie dotyczące Projects classic. Wtedy użyj GitHub API, np. `gh api --method PATCH repos/szybkoiwyraznie-rgb/mtgdatabase/pulls/1 -f body="$(cat /tmp/body.md)"`.
- Po każdym pushu sprawdź commit, status i checks PR-a.

## 4. Pliki i narzędzia

- Zapisuj tekst jako UTF-8.
- Przy polskich znakach preferuj `write_file` albo Python z `encoding="utf-8"`.
- Nie commituj sekretów, PIN-ów, tokenów, plików `.env` ani artefaktów tymczasowych.
- `artifacts/`, `build/` i `/tmp` nie są źródłem prawdy. Artefakty dystrybucyjne publikuj przez GitHub Releases.
- Po zmianach uruchom walidatory i `git diff --check`.

## 5. Podglądy dla właściciela (bramka i gablotka)

- Bramka: `python scripts/gate_preview.py data/gates/gNNN --port 8080`.
  Gablotka: `python scripts/serve_site.py --port 3000` (po `build_site.py`).
  Oba serwery słuchają na `0.0.0.0` — inaczej podgląd w przeglądarce
  właściciela nie zadziała.
- Jeden port = jedna bramka: przed postawieniem nowej **zatrzymaj
  poprzedni proces** na :8080, inaczej właściciel ogląda starą rundę.
- **Cache przeglądarki potrafi udawać błąd montażu.** `build_site.py`
  dokleja do adresów audio `?v=<md5>`, a `serve_site.py` wysyła
  `Cache-Control: no-store`. Nie zastępuj ich zwykłym
  `python -m http.server`: odpowiada `304` i właściciel słyszy poprzednią
  wersję pliku (zdarzyło się przy fabule 5). Reklamację „gra stara wersja”
  weryfikuj przez `md5sum` na dysku kontra `curl` z serwera.

## 5a. Testowanie i publikacja

- Build Pages na branchu roboczym może zakończyć się bez deploymentu; deployment Pages wykonuje się dopiero z `main` po konfiguracji GitHub Pages.
- Publiczny Pages nie jest prywatnym hostingiem. PIN po stronie JavaScript jest tylko wygodą interfejsu.
- ZIP najlepszych jingli ma być płaski i zawierać wyłącznie `id.mp3`.
- Przed końcem pracy sprawdź `git status`, historię i wynik GitHub Actions.
