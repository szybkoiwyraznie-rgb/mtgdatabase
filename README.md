# Krótkie sample fabularne

Nowy flow projektu: każda fabuła z `fabuły270926.csv` dostaje **jeden krótki,
jednorodny efekt dźwiękowy** wygenerowany przez ElevenLabs i zapisany jako
`audio/samples/<id>.mp3`.

To nie jest już czterowarstwowy sound design z tłem, hero, kodą i instrumentem.
Efekt ma być prostym samplem typu: „krakanie wron”, „uderzenie dzwonu”,
„szczęk bitwy”, „odgłos upadku” — opisanym konkretnie dla danej fabuły, ale
bez skomplikowanej sceny audio.

Stary system v1 jest zachowany tylko jako archiwum w
`archive/v1-curated-sound-design/` i nie trafia do aktualnego ZIP-a ani Pages.

## Aktualny workflow

1. Właściciel wrzuca nowy `fabuły270926.csv` jako commit.
2. Agent przygotowuje małą paczkę scenariuszy, zwykle około 10 sztuk, w
   `data/samples/scenarios.jsonl`.
3. Po paczce agent uruchamia scouta ElevenLabs:

   ```bash
   python scripts/validate_sample_scenarios.py
   ELEVENLABS=... python scripts/elevenlabs_sample_scout.py --batch b001 --limit 10
   ```

4. Wygenerowane pliki lądują w `audio/samples/<id>.mp3`.
5. Biblioteka HTML i ZIP:

   ```bash
   python scripts/build_site.py
   python scripts/build_pack.py
   python scripts/serve_site.py --port 3000 --dir site/generated
   ```

## Sekret API

GitHub secret ma nazwę:

```text
ELEVENLABS
```

Klucz nie jest zapisywany w repo ani w czacie. Ponieważ limit wystarcza mniej
więcej na 40–50 generacji, workflow jest manualny i działa małymi paczkami.

## Najważniejsze ścieżki

- `data/catalog.json` — katalog importowany z `fabuły270926.csv`,
- `data/samples/scenarios.jsonl` — ręcznie pisane scenariusze sampli,
- `data/samples/generated-manifest.jsonl` — manifest generacji scouta,
- `audio/samples/<id>.mp3` — aktualne produkty,
- `site/generated/` — lokalna/Pages biblioteka HTML,
- `build/samples-latest.zip` — płaski ZIP z `<id>.mp3`.

Pełny opis: [`docs/ai-sfx-pipeline.md`](docs/ai-sfx-pipeline.md).
