# Feedback Worker

To jest bezpieczny, zdalny pośrednik między publicznym JavaScriptem Pages a GitHub Issues. Token GitHub nie trafia do strony.

## Deployment zdalny — bez instalacji na komputerze

Worker jest wdrażany przez GitHub Actions. Twój desktop, iPad, laptop ani telefon nie muszą być włączone. Wystarczy jednorazowo utworzyć konto Cloudflare, token Cloudflare i sekrety repozytorium.

1. Utwórz konto Cloudflare Workers.
2. W Cloudflare utwórz API Token z uprawnieniem do edycji Workers dla właściwego konta.
3. W GitHubie dodaj sekrety Actions:
   - `CLOUDFLARE_API_TOKEN` — token Cloudflare;
   - `CLOUDFLARE_ACCOUNT_ID` — Account ID z panelu Cloudflare;
   - `WORKER_GITHUB_TOKEN` — Fine-grained token GitHub z dostępem tylko do tego repozytorium i `Issues: Read and write`.
4. Wejdź w `Actions → Deploy feedback worker → Run workflow`.
5. Workflow wdroży workera i zapisze token GitHub jako sekret Cloudflare.
6. Adres workera skopiuj do `site/data/config.example.json` jako `feedbackEndpoint`.

Nie uruchamiaj `wrangler login` na desktopie — lokalna instalacja jest opcjonalna i nie jest potrzebna w tym projekcie.

Tokeny nigdy nie mogą być wpisane do JavaScriptu Pages ani commitowane do repozytorium.
