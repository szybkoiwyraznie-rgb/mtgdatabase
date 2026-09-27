# Źródła i licencje — aktualny flow v2

Aktywny produkt powstaje przez ElevenLabs Sound Generation z promptów w
`data/samples/scenarios.jsonl`. Stare ręcznie dobierane źródła sampli, bramki i
biblioteki CC0 są zachowane w `archive/v1-curated-sound-design/` jako historia
v1, ale nie są używane w aktualnym ZIP-ie ani Pages.

## ElevenLabs

- Sekret/API key: `ELEVENLABS`.
- Klucza nie zapisujemy w repo ani w czacie.
- `scripts/elevenlabs_sample_scout.py` zapisuje wynik do `audio/samples/<id>.mp3`
  i manifest do `data/samples/generated-manifest.jsonl`.
- Token wystarcza mniej więcej na 40–50 generacji, więc pracujemy paczkami po
  ok. 10 scenariuszy.

## Publikacja

Aktualne publiczne/udostępniane artefakty:

- biblioteka HTML z `scripts/build_site.py`,
- ZIP z `scripts/build_pack.py`,
- opcjonalny artifact workflow `Generate sample batch (ElevenLabs)`.

Stare `audio/signatures` są w archiwum i nie są publikowane przez aktywne
skrypty.

## Scenariusze i proweniencja

Dla każdego samplem proweniencją jest:

- `story_id`,
- tytuł,
- `sample_scenario`,
- prompt wysłany do ElevenLabs,
- data/czas generacji w `generated-manifest.jsonl`,
- użyty model/endpoint, jeśli zostanie dodany do manifestu w przyszłości.

W razie potrzeby można rozszerzyć manifest o wersję modelu, ale nie blokuje to
obecnej produkcji.
