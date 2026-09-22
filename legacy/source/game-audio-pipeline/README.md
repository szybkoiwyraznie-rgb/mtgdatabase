# Game Audio Pipeline (Hurtowe Tworzenie 500 Jingli Fabularnych)

System do automatycznego, bezpłatnego (0 zł) generowania 3–6 sekundowych fabularnych efektów dźwiękowych (audio vignettes / stingers) dla gier karcianych, RPG i narracyjnych.

---

## 1. Dlaczego ten podział jest kluczowy? (Architektura)

Próba wygenerowania 500 plików dźwiękowych w jednej sesji agenta AI skończyłaby się błędem pamięci (workspace budget), przekroczeniem limitu tokenów lub timeoutem. 

Dlatego podzieliliśmy proces na dwa niezależne etapy:

```
[Arkusz 500 Wydarzeń (events.csv)]
                  │
                  ▼  (Krok 1: Tani i szybki proces tekstu)
       [Agent LLM / Orchestrator] 
                  │  Zamienia opisy literackie na parametryczne scenariusze akustyczne
                  ▼  
         [recipes.json / batch_XX.json]
                  │
                  ▼  (Krok 2: Błyskawiczny, deterministyczny DSP w Pythonie)
          [audio_engine.py] + [stems/ CC0 Library]
                  │
                  ▼  (Renderuje ~100 plików na minutę!)
         [/output/event_001.mp3 ... event_500.mp3]
```

* **Etap 1 (Kreatywny):** LLM działa wyłącznie jako reżyser dźwięku – generuje czysty tekst (JSON) z timingiem, panningiem i wyborem próbek. 50 wydarzeń w formacie JSON to zaledwie kilka tysięcy tokenów.
* **Etap 2 (Renderujący):** Skrypt Python `audio_engine.py` pobiera bazę próbek CC0 (2 MB) i miksuje audio z precyzyjnym pogłosem, duckingiem i kompresją w ułamku sekundy na plik.

---

## 2. Struktura Repozytorium

```
game-audio-pipeline/
├── events_sample.csv          # Przykładowy arkusz z opisami fabularnymi (id, title, genre, lore)
├── llm_orchestrator_prompt.txt # Prompt systemowy dla agenta do konwersji CSV -> JSON
├── recipes_sample.json        # Wygenerowane receptury dźwiękowe dla próbek
├── fetch_stems.py             # Skrypt pobierający próbki CC0 (Yellowstone, Gravity Sound)
├── audio_engine.py            # Silnik audio renderujący pliki MP3 z JSON
├── stems/                     # Katalog bazowych próbek (zajmuje łącznie tylko ~2 MB)
│   ├── sword_draw.mp3
│   ├── raven_call.mp3
│   ├── bear_growl.mp3
│   ├── alligator_bellow.mp3
│   ├── water_splash.mp3
│   ├── gravel_feet.mp3
│   └── whoosh_flap.mp3
└── output/                    # Gotowe wyrenderowane pliki MP3 (ok. 80-90 KB / sztuka)
```

---

## 3. Jak przeprowadzić hurtową produkcję 500 dźwięków?

### Wariant A: Praca w sesjach Agent Arena (Partiami po 25-50 sztuk)
1. Podziel swój arkusz 500 wydarzeń na 10-15 partii po 30-40 wierszy.
2. W nowej sesji Agenta wklejasz treść z `llm_orchestrator_prompt.txt` oraz paczkę wierszy z CSV.
3. Agent natychmiast generuje plik `recipes_batch_01.json`.
4. Agent (lub Ty lokalnie) uruchamia `python audio_engine.py` i otrzymujesz paczkę 40 gotowych plików `.mp3`.
5. Cała paczka 500 plików zajmie łącznie zaledwie **~45 MB**, co z łatwością zmieści się w repozytorium GitHub lub archiwum ZIP.

### Wariant B: Pełna automatyzacja (Lokalny skrypt Python lub GitHub Actions)
Jeśli masz klucz do OpenAI, Anthropic lub lokalny model (np. Ollama / Llama 3):
1. Skrypt odczytuje kolejne wiersze z `events.csv`.
2. Wysyła zapytanie z `llm_orchestrator_prompt.txt` do modelu (np. 50 wierszy na zapytanie).
3. Wyniki dokleja do pliku `recipes.json`.
4. Uruchamia `python audio_engine.py`.
5. W 10-15 minut masz wyrenderowany komplet 500 plików `.mp3` bez żadnych kosztów licencji dźwiękowych!

---

## 4. Szybki start (uruchomienie testowe)

```bash
# 1. Pobierz próbki bazowe (jeśli nie ma ich w katalogu)
python fetch_stems.py

# 2. Wyrenderuj próbki z recipes_sample.json
python audio_engine.py

# Gotowe pliki MP3 znajdziesz w folderze output/
```
