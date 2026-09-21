# Pętla pracy agenta

## Priorytet

Agent najpierw szuka otwartego feedbacku dotyczącego najniżej ocenionej wersji. Jeśli nie ma żadnego zadania do poprawy, losuje fabułę ze statusem `new` i tworzy pierwszą wersję.

## Każda pętla

### 1. Zadanie produkcyjne

- przeczytaj obowiązkową dokumentację;
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
