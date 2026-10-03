# Środowisko Agent Arena

Ten plik zawiera zasady specyficzne dla pracy w sandboxie Arena. Decyzje
produktowe są w `AGENTS.md` i `docs/STATE.md`.

## 1. Trwałość pracy

Nowa sesja może wystartować z czystego klona. Przetrwa tylko to, co zostało
zapisane w repozytorium, zacommitowane i wypchnięte na GitHub.

- Commituj i pushuj często.
- Nie polegaj na historii rozmowy ani plikach w `/tmp`.
- Snapshot workspace wyłącza m.in. `.venv/`, `work/`, `build/`, `/tmp` i może
  cofnąć lokalny stan gita.
- Po restarcie sprawdź `git status` i `git log --oneline -5`; jeśli HEAD jest
  stary, zrób `git fetch origin <branch>` i dopiero potem resetuj do gałęzi
  sesji.
- Pracuj wyłącznie na branchu sesji Arena. Nie pushuj bezpośrednio do `main`.

## 2. Ochrona przed resetem workspace

Jeśli HEAD niespodziewanie wskazuje bazę albo zniknęły commity:

```bash
git status --porcelain
git diff > /tmp/arena-recovery.patch
git fetch origin <branch-sesji>
git reset --mixed FETCH_HEAD
```

`--hard` wykonuj dopiero po upewnieniu się, że nie ma lokalnych zmian do
uratowania.

## 3. GitHub, PR i uwierzytelnienie

- **Twarda zasada sesji: początek sesji = otwarcie PR; każde zadanie = commit + push.**
  Sprawdź `gh pr list --head <branch-sesji>` już na starcie pracy. Natychmiast
  po pierwszym commicie na gałęzi sesji (`arena/...`) utwórz PR do `main`
  (`gh pr create --base main --head <branch-sesji>`), a każde kolejne zadanie
  zamykaj commitem i pushem aktualizującym ten PR.
- Do operacji lokalnych używaj `git`, do PR/checków/workflowów `gh`.
- Nigdy nie proś właściciela o hasła, tokeny ani kody 2FA w czacie.
- Jeśli `git`/`gh` zwróci błąd uwierzytelnienia, poproś o reconnect GitHub w Arena.
- `gh workflow run` może nie działać z tokenem GitHub App (`actions:write`);
  jeśli tak, właściciel może uruchomić manualny workflow z UI GitHuba.
- Po każdym pushu sprawdź checks PR-a (`gh pr checks`).

## 4. Pliki i sekrety

- Tekst zapisuj jako UTF-8.
- Nie commituj sekretów, PIN-ów, tokenów ani plików `.env`.
- Sekret ElevenLabs ma nazwę `ELEVENLABS`.
- `artifacts/`, `build/`, `site/generated/` i `/tmp` nie są źródłem prawdy.
- Aktualne produkty audio, jeśli mają być wersjonowane, są w `audio/samples/`.

## 5. Podgląd biblioteki

Aktywna biblioteka HTML to sample v2:

```bash
python scripts/build_site.py --out site/generated
python scripts/serve_site.py --port 3000 --dir site/generated
```

Serwer musi słuchać na `0.0.0.0`; `serve_site.py` już to robi i wysyła
`Cache-Control: no-store`. Nie używaj do podglądu zwykłego `python -m http.server`,
jeśli właściciel ma odsłuchiwać świeże MP3.

## 6. Testowanie i publikacja

Przed końcem pracy:

```bash
python -m compileall -q scripts
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/validate_stories.py fabuły270926.csv
python scripts/import_collection.py fabuły270926.csv --output /tmp/catalog.json
python scripts/validate_sample_scenarios.py data/samples/scenarios.jsonl --catalog data/catalog.json
python scripts/build_pack.py --output /tmp/samples.zip
python scripts/build_site.py --out /tmp/site-out
git diff --check
```

ZIP jest płaski i zawiera wyłącznie `id.mp3` z `audio/samples`.
