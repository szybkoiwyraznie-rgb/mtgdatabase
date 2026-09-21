# Współpraca

Przeczytaj `AGENTS.md` przed każdą zmianą. Zmiany powinny być małe, możliwe do zweryfikowania i opisane w pull request.

## Przed zakończeniem

```bash
python -m compileall -q scripts
python scripts/build_best_zip.py --help
```

Nie commituj sekretów, PIN-u, tokenów ani nieprzetworzonych plików tymczasowych. Duże artefakty produkcyjne publikujemy przez GitHub Releases, nie jako zwykłe pliki w historii Git.
