# AI SFX pipeline v2 — jeden prompt, jeden MP3 na fabułę

Cel: uprościć produkcję 500+ unikalnych efektów dźwiękowych. Zamiast ręcznych
bramek, bibliotek klocków i miksów warstwowych, każda fabuła dostaje dokładnie
jeden scenariusz dźwięku i dokładnie jeden wygenerowany plik `<id>.mp3`.

## Zasada produktu

Dla każdej fabuły:

1. czytamy narrację z katalogu (`data/catalog.json`, generowane z `kolekcja.csv`),
2. jeśli istnieje profil semantyczny, używamy go jako jednej analizy sceny,
3. budujemy jeden prompt SFX:
   - miejsce / tło,
   - jedno główne zdarzenie,
   - nastrój,
   - tekstura brzmienia,
   - zakaz muzyki, melodii, narracji i mowy,
4. wysyłamy prompt do ElevenLabs Sound Generation,
5. zapisujemy odpowiedź jako `audio/ai-signatures/<id>.mp3`,
6. budujemy płaski ZIP z plikami `<id>.mp3`.

To jest ścieżka v2. Stary system bramek i ręcznych klocków zostaje w repo jako
historia/prace v1, ale nie jest już konieczny do produkcji pełnej paczki.

## Sekret API

Nie wpisuj klucza w kodzie ani w czacie. W repozytorium GitHub dodaj secret:

- `ELEVENLABS_API_KEY` — wymagany,
- opcjonalnie `ELEVENLABS_SOUNDGEN_ENDPOINT` — tylko jeśli endpoint API się
  zmieni; domyślnie skrypt używa `https://api.elevenlabs.io/v1/sound-generation`.

## Ręczny run w GitHub Actions

Workflow: **Generate AI sound effects (ElevenLabs)**

Parametry:

- `collection_csv` — domyślnie `kolekcja.csv`; po dosłaniu nowego zestawu CSV/TSV
  można wskazać jego ścieżkę w repo,
- `ids` — puste = wszystkie fabuły; można podać np. `1,2,3` do testu,
- `limit` — pierwsze N wybranych fabuł; zalecane do pierwszego testu, np. `5`,
- `force` — regeneruj istniejące pliki w workspace joba,
- `prompt_influence` — przekazywane do ElevenLabs; domyślnie `0.35`.

Workflow publikuje artifact `ai-signatures-elevenlabs` zawierający:

- `build/ai-signatures-latest.zip`,
- `data/ai-sfx/prompts.jsonl`,
- `data/ai-sfx/generated-manifest.jsonl`.

## Lokalne przygotowanie promptów bez API

```bash
python scripts/import_collection.py kolekcja.csv --output data/catalog.json
python scripts/generate_ai_sound_prompts.py \
  --catalog data/catalog.json \
  --profiles data/semantics/story-profiles.json \
  --out data/ai-sfx/prompts.jsonl \
  --limit 10
python scripts/elevenlabs_soundgen.py --prompts data/ai-sfx/prompts.jsonl --dry-run
```

## Lokalny run z API

Tylko jeśli lokalne środowisko ma dostęp do internetu i ustawiony sekret:

```bash
ELEVENLABS_API_KEY=... python scripts/elevenlabs_soundgen.py \
  --prompts data/ai-sfx/prompts.jsonl \
  --out audio/ai-signatures \
  --manifest data/ai-sfx/generated-manifest.jsonl \
  --limit 5
python scripts/build_pack.py --src audio/ai-signatures --output build/ai-signatures-latest.zip
```

## Uwaga o kosztach i QA

Workflow jest manualny, bo każde uruchomienie zużywa zewnętrzny limit/koszt API.
Najpierw robić krótki smoke test (`limit=5` albo kilka `ids`), potem pełną paczkę.

QA w v2 jest uproszczone: sprawdzamy kompletność plików, nazwy `<id>.mp3`,
manifest promptów i ewentualnie odsłuch próbkowy. Nie ma już ręcznej bramki
akceptacji dla każdego typu dźwięku.
