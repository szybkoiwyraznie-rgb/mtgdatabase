# Pętla pracy agenta

## Priorytet

Agent najpierw szuka otwartego feedbacku dotyczącego najniżej ocenionej wersji. Jeśli nie ma żadnego zadania do poprawy, losuje fabułę ze statusem `new` i tworzy pierwszą wersję.

## Każda pętla

### 0. Audyt poprzedniego PR i kodu

Po przeczytaniu obowiązkowej dokumentacji agent najpierw audytuje poprzednią pracę:

- sprawdź ostatni PR, commity i aktualny diff;
- przeczytaj zmienione pliki, a nie tylko opis zmian;
- uruchom testy, lint, walidatory i build;
- sprawdź zgodność z `AGENTS.md`, kontraktami danych i kryteriami bezpieczeństwa;
- poszukaj regresji, martwego kodu, placeholderów, błędnych ścieżek i brakujących konfiguracji;
- napraw znalezione problemy przed podjęciem nowego zadania;
- w raporcie zapisz, co zostało sprawdzone i co naprawiono.

Jeśli audyt wykryje ryzyko utraty danych, sekret w kodzie albo nieodwracalną publikację, zatrzymaj się i opisz problem zamiast go omijać.

### 1. Zadanie produkcyjne

- sprawdź status repozytorium i kolejki;
- zarezerwuj zadanie, aby dwóch agentów nie pracowało nad nim równocześnie;
- zaprojektuj recepturę audio na podstawie tytułu i fabuły;
- wyrenderuj MP3 i zapisz metadane;
- użyj kolejnego numeru wersji, bez kasowania poprzednich.

### 2. Rozwój warsztatu

W tej samej pętli wykonaj konkretną pracę rozwojową: dodaj zweryfikowane źródło sampli, popraw narzędzie DSP, test, prompt, dokumentację albo workflow. Sam link bez opisu licencji i zastosowania nie jest wystarczającym rezultatem.

### 3. Publikacja

- zwaliduj metadane, MP3 i strukturę wersji;
- zbuduj stronę Pages;
- utwórz raport gotowy do zapisania jako GitHub Issue;
- zbuduj płaski ZIP najlepszych ocenionych wersji;
- przygotuj asset GitHub Release.

## Reguła wyboru najlepszego pliku

Dla każdej fabuły wybierz tylko wersję z istniejącą oceną o najwyższej sumie trzech kryteriów. Wersja oczekująca na ocenę nie może trafić do ZIP-a, nawet jeśli jest najnowsza.
