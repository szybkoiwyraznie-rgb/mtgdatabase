# Współpraca

Przeczytaj `AGENTS.md` przed każdą zmianą. Zmiany małe, weryfikowalne,
opisane w pull request.

## Przed rozpoczęciem

Audyt ostatniego PR/diffu + walidacje (poniżej). Nie zaczynaj produkcji na
niezweryfikowanym fundamencie.

## Przed zakończeniem

```
python -m compileall -q scripts
python scripts/test_signature_system.py
python scripts/library_tool.py check
python scripts/build_pack.py --output /tmp/pack.zip
```

Nie commituj: sekretów/PIN/tokenów, plików `.env`, kandydatów bramkowych
(`work/`), niezatwierdzonych sampli. Produkty idą na Release, nie do
historycznych artefaktów.
