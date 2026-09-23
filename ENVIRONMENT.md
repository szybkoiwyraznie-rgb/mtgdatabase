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
  .venv/bin/pip install numpy soundfile lameenc av`.
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
- `gh pr edit` może zgłaszać ostrzeżenie dotyczące Projects classic. Wtedy użyj GitHub API, np. `gh api --method PATCH repos/szybkoiwyraznie-rgb/mtgdatabase/pulls/1 -f body="$(cat /tmp/body.md)"`.
- Po każdym pushu sprawdź commit, status i checks PR-a.

## 4. Pliki i narzędzia

- Zapisuj tekst jako UTF-8.
- Przy polskich znakach preferuj `write_file` albo Python z `encoding="utf-8"`.
- Nie commituj sekretów, PIN-ów, tokenów, plików `.env` ani artefaktów tymczasowych.
- `artifacts/`, `build/` i `/tmp` nie są źródłem prawdy. Artefakty dystrybucyjne publikuj przez GitHub Releases.
- Po zmianach uruchom walidatory i `git diff --check`.

## 5. Testowanie i publikacja

- Build Pages na branchu roboczym może zakończyć się bez deploymentu; deployment Pages wykonuje się dopiero z `main` po konfiguracji GitHub Pages.
- Publiczny Pages nie jest prywatnym hostingiem. PIN po stronie JavaScript jest tylko wygodą interfejsu.
- ZIP najlepszych jingli ma być płaski i zawierać wyłącznie `id.mp3`.
- Przed końcem pracy sprawdź `git status`, historię i wynik GitHub Actions.
