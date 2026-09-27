# Jednorazowa konfiguracja GitHuba

Instrukcja dla właściciela repozytorium.

## Sekret ElevenLabs

`Settings → Secrets and variables → Actions → New repository secret`:

```text
ELEVENLABS
```

To jest API key do ElevenLabs Sound Generation. Klucz można wymieniać, gdy
wyczerpie się limit. Nie używamy nazwy `ELEVENLABS_API_KEY`.

## Generowanie paczki sampli

Workflow ręczny:

```text
Actions → Generate sample batch (ElevenLabs) → Run workflow
```

Najważniejsze pola:

- `batch` — np. `b001`,
- `limit` — zwykle `10`,
- `publish_pages` — deploy biblioteki na Pages; działa tylko z `main`.

Workflow generuje artifact z:

- `samples-latest.zip`,
- `generated-manifest.jsonl`,
- gotową biblioteką HTML.

## Pages

`Settings → Pages → Source: GitHub Actions`, potem:

```text
Actions → Publish sample library → Run workflow
```

Strona pokazuje scenariusze i gotowe `audio/samples/<id>.mp3`.

## Paczka ZIP

Po zmianach w `audio/samples/**` na `main` workflow `Build sample release`
publikuje płaski `samples-latest.zip` jako rolling release. Opcjonalne
szyfrowanie nadal używa sekretu `JINGLE_ZIP_PASSWORD`.

## Archiwum starego systemu

Stary flow bramek/Freesound/warstw jest w `archive/v1-curated-sound-design/` i
nie wymaga konfiguracji.
