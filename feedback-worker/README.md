# Feedback Worker

To jest bezpieczny pośrednik między publicznym JavaScriptem Pages a GitHub Issues. Token GitHub nie trafia do strony.

## Jednorazowa konfiguracja

1. Utwórz konto Cloudflare i zainstaluj Wrangler.
2. W tym katalogu uruchom `wrangler login`.
3. Utwórz token GitHub Fine-grained z dostępem tylko do tego repozytorium i uprawnieniem `Issues: Read and write`.
4. Ustaw sekret:

```bash
wrangler secret put GITHUB_TOKEN
```

5. Wdróż worker:

```bash
wrangler deploy
```

6. Skopiuj adres workera do `site/data/config.json` jako `feedbackEndpoint`.

Token nigdy nie może być wpisany do JavaScriptu Pages ani commitowany do repozytorium.
