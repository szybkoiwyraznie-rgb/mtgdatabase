# Instrukcje dla agentów

To repozytorium jest prywatną, niekomercyjną linią produkcyjną krótkich form audio. Zanim rozpoczniesz pracę, przeczytaj ten plik oraz `README.md` i odpowiedni dokument z `docs/`.

## Zasady nadrzędne

1. Pracuj tylko na zadaniu, które wynika z aktualnego stanu kolejki.
2. Nie nadpisuj istniejących wersji jingla. Nowy render zapisuj jako kolejne `vN`.
3. Nie usuwaj ocen, komentarzy ani historii wersji.
4. Każdy jingle musi mieć identyfikator fabuły i wersję.
5. Wynikiem pracy musi być działający MP3, metadane oraz aktualizacja strony.
6. Przed zakończeniem uruchom walidację i opisz jej wynik.
7. Nie umieszczaj sekretów, PIN-u ani tokenów w kodzie, danych Pages ani commitach.
8. Przy nowych samplach zapisz źródło, licencję, autora i zakres dozwolonego użycia w rejestrze źródeł.
9. Nie traktuj ekranu PIN w JavaScripcie jako silnego zabezpieczenia. Pages może być dostępne publicznie.
10. Jeśli zadanie jest jednoznaczne, działaj bez dodatkowych pytań. Pytaj tylko przy ryzyku utraty danych, błędnym wyborze architektury lub nieodwracalnej publikacji.

## Pętla pracy

W każdej pętli wykonaj:

1. **Produkcję:** popraw najniżej oceniony nierozwiązany jingle albo, jeśli nie ma takiego zadania, wybierz losową nieopracowaną fabułę i utwórz `v1`.
2. **Rozwój warsztatu:** zbadaj lub ulepsz co najmniej jeden element narzędzi, dokumentacji, receptur albo biblioteki sampli. Zapisz konkretny rezultat.
3. **Publikację i kontrolę:** uruchom walidację, zbuduj Pages, przygotuj paczkę najlepszych MP3 i opisz zmiany.

## Oceny

Ocena jest sumą trzech parametrów od 1 do 5:

- feeling ogólny,
- zgodność z fabułą,
- jakość wykorzystanych sampli.

Maksymalny wynik to 15. Najlepsza wersja fabuły to najwyżej oceniona wersja, która ma już ocenę. Wersja bez oceny nie może zastąpić ocenionej wersji w paczce.

## Paczka offline

Paczka jest płaskim ZIP-em zawierającym wyłącznie pliki MP3 nazwane numerem fabuły, np. `1.mp3`, `67.mp3`, `389.mp3`. Nie dodawaj katalogów, JSON-ów ani receptur do środka.

## Raport końcowy

Podaj:

- co zostało zrobione,
- którą fabułę i wersję obsłużono,
- wynik ocen lub status oczekiwania na ocenę,
- przeprowadzone testy i ich wynik,
- zmiany w warsztacie,
- ryzyka i następny krok.
