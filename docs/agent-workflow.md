# Pętla pracy agenta

## Priorytet

W każdej pętli agent wykonuje oba zadania produkcyjne: tworzy pierwszą wersję losowej nowej fabuły oraz wykonuje remake najsłabszej fabuli w kolejce (szeregowanie wg najlepszej ocenionej wersji fabuły — patrz krok 2). Jeśli jedna z kolejek jest pusta, agent odnotowuje ten fakt i kontynuuje pozostałe zadania.

## Każda pętla

### 0. Audyt poprzedniego PR i kodu

Po przeczytaniu obowiązkowej dokumentacji, w tym `ENVIRONMENT.md` i aktualnej kolekcji, agent najpierw audytuje poprzednią pracę:

- sprawdź ostatni PR, commity i aktualny diff;
- przeczytaj zmienione pliki, a nie tylko opis zmian;
- uruchom testy, lint, walidatory i build;
- sprawdź zgodność z `AGENTS.md`, kontraktami danych i kryteriami bezpieczeństwa;
- poszukaj regresji, martwego kodu, placeholderów, błędnych ścieżek i brakujących konfiguracji;
- napraw znalezione problemy przed podjęciem nowego zadania;
- w raporcie zapisz, co zostało sprawdzone i co naprawiono.

Jeśli audyt wykryje ryzyko utraty danych, sekret w kodzie albo nieodwracalną publikację, zatrzymaj się i opisz problem zamiast go omijać.

### 0.5 Synchronizacja ocen

Przed nową produkcją zsynchronizuj oceny z issues z etykietą `feedback`:

```bash
python scripts/sync_ratings.py --versions data/versions.json
```

Najnowszy raport dla pary (fabuła, wersja) ustawia aktualną ocenę, a każdy raport trafia do historii `reports` wersji. Pominięte wpisy (np. ocena bez wyrenderowanej wersji) wypisz w raporcie. Workflow `Sync ratings from issues` wykonuje to samo automatycznie po każdym nowym issue i przebudowuje Pages oraz paczkę ZIP, ale agent nie zwaliduje pętli bez sprawdzenia, że wszystkie oceny są w `data/versions.json`.

### 1. Nowa fabuła

- sprawdź status repozytorium i kolejki;
- zarezerwuj losową fabułę ze statusem `new`;
- zaprojektuj recepturę audio na podstawie tytułu i fabuły;
- wyrenderuj pierwsze MP3 i zapisz metadane jako `v1`; render musi przejść audyt QA ≥85/100 — poniżej progu poprawiasz recepturę i liczysz ponownie, zanim zapiszesz metadane;
- jeśli nie ma nowych fabuł, zapisz to w raporcie i przejdź dalej.

### 2. Remake najsłabszej fabuły (ranking wg najlepszej wersji)

- uszereguj fabuły po **najlepiej ocenionej wersji** rosnąco: `python scripts/remake_queue.py --versions data/versions.json`; nisko oceniony remake (np. v2 = 3/15 przy v1 = 10/15) nie podnosi priorytetu fabuły ponad jej najlepszą wersję;
- **próg właściciela (2026-09-22): fabuła z najlepszą wersją poniżej 12/15 wymaga remake'u; poniżej progu nowa wersja powstaje OD ZERA** (nowa dramaturgia, nowe sample, audytowane offsety) — iterowanie na odrzuconej recepturze dało 475 v2 „niczym się nie różni od poprzedniej";
- pomiń fabuły, których najnowsza wersja czeka jeszcze na ocenę (nie stackuj wersji), oraz fabuły bez otwartych raportów;
- zarezerwuj zadanie, aby dwóch agentów nie pracowało nad nim równocześnie;
- przeanalizuj trzy oceny i komentarz; przy najlepszej wersji ≥12/15 nowa wersja `vN` buduje na jej mocnych stronach — raporty wskazują, co poprawić, nie wymuszają kontynuacji po porażce;
- zaprojektuj poprawkę, zaktualizuj opis projektowy i nie kasuj poprzedniej wersji;
- wyrenderuj kolejną wersję `vN` (audyt QA v2 ≥85/100: słyszalność żywych zdarzeń +6 dB nad tłem, RMS ≥ -26 dB, >6 kHz ≤ 12%) i oznacz raport jako obsłużony dopiero po udanej publikacji; po merge'u `data/versions.json` z nowszą wersją workflow `Sync ratings from issues` zamyka raport automatycznie, ale agent weryfikuje to na wypadek awarii automatu;
- jeśli nie ma ocenionej fabuły do poprawy, zapisz to w raporcie.

### 3. Rozwój warsztatu

W tej samej pętli wykonaj konkretną pracę rozwojową: dodaj zweryfikowane źródło sampli, popraw narzędzie DSP, test, prompt, dokumentację albo workflow. Sam link bez opisu licencji i zastosowania nie jest wystarczającym rezultatem.

### 4. Publikacja

- zwaliduj metadane, MP3 i strukturę wersji;
- zbuduj stronę Pages;
- utwórz raport gotowy do zapisania jako GitHub Issue;
- zbuduj płaski ZIP najlepszych ocenionych wersji;
- przygotuj asset GitHub Release.

## Reguła wyboru najlepszego pliku

Dla każdej fabuły wybierz tylko wersję z istniejącą oceną o najwyższej sumie trzech kryteriów. Wersja oczekująca na ocenę nie może trafić do ZIP-a, nawet jeśli jest najnowsza.
