# Pętla pracy agenta

## Priorytet

W każdej pętli agent wykonuje oba zadania produkcyjne: tworzy pierwszą wersję losowej nowej fabuły oraz wykonuje remake najgorzej ocenionego istniejącego jingla. Jeśli jedna z kolejek jest pusta, agent odnotowuje ten fakt i kontynuuje pozostałe zadania.

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

### 1. Nowa fabuła

- sprawdź status repozytorium i kolejki;
- zarezerwuj losową fabułę ze statusem `new`;
- zaprojektuj recepturę audio na podstawie tytułu i fabuły;
- wyrenderuj pierwsze MP3 i zapisz metadane jako `v1`;
- jeśli nie ma nowych fabuł, zapisz to w raporcie i przejdź dalej.

### 2. Remake najgorszego jingla

- znajdź najniżej oceniony, nierozwiązany raport;
- zarezerwuj zadanie, aby dwóch agentów nie pracowało nad nim równocześnie;
- przeanalizuj trzy oceny i komentarz;
- zaprojektuj poprawkę, zaktualizuj opis projektowy i nie kasuj poprzedniej wersji;
- wyrenderuj kolejną wersję `vN` i oznacz raport jako obsłużony dopiero po udanej publikacji;
- jeśli nie ma ocenionego jingla do poprawy, zapisz to w raporcie.

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
