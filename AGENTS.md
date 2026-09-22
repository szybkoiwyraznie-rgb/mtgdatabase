# Instrukcje dla agentów

To repozytorium jest prywatną, niekomercyjną linią produkcyjną krótkich form audio. Zanim rozpoczniesz pracę, przeczytaj ten plik oraz `README.md` i odpowiedni dokument z `docs/`.

## Zasady nadrzędne

1. Przeczytaj całą obowiązkową lekturę z `docs/required-reading.md`, w tym `ENVIRONMENT.md`, aktywne ADR-y, `docs/LESSONS.md` oraz zaktualizowaną kolekcję fabuł.
2. Pracuj tylko na zadaniu, które wynika z aktualnego stanu kolejki.
3. Nie nadpisuj istniejących wersji jingla. Nowy render zapisuj jako kolejne `vN`.
3. Nie usuwaj ocen, komentarzy ani historii wersji.
4. Każdy jingle musi mieć identyfikator fabuły, wersję i opis projektowy. Opis zapisuje użyte sample, timestampy, warstwy oraz najważniejsze decyzje miksu.
5. Wynikiem pracy musi być działający MP3, metadane oraz aktualizacja strony.
6. Przed zakończeniem uruchom walidację i opisz jej wynik.
7. Nie umieszczaj sekretów, PIN-u ani tokenów w kodzie, danych Pages ani commitach.
8. Przy nowych samplach zapisz źródło, licencję, autora i zakres dozwolonego użycia w rejestrze źródeł.
9. Nie traktuj ekranu PIN w JavaScripcie jako silnego zabezpieczenia. Pages może być dostępne publicznie.
10. Jeśli zadanie jest jednoznaczne, działaj bez dodatkowych pytań. Pytaj tylko przy ryzyku utraty danych, błędnym wyborze architektury lub nieodwracalnej publikacji.
11. Pięć jingli z `legacy/source/jingle_output/` (fabuły 1–5) to produkcyjne wersje `v1`, nie demo. Nigdy ich nie usuwaj ani nie oznaczaj jako prototyp; lepszą wersję tworzysz jako kolejne `vN`.
12. W każdej pętli zsynchronizuj oceny: uruchom `python scripts/sync_ratings.py --versions data/versions.json` i dopilnuj, by każda ocena z issues z etykietą `feedback` trafiła do `data/versions.json` przed publikacją. Workflow `Sync ratings from issues` robi to automatycznie, ale agent weryfikuje wynik i domyka braki.
13. Render publikujesz dopiero po audycie QA ≥85/100: bramki techniczne (DC offset, headroom, ciągłość tła, kontrast kulminacji — `scripts/qa_score.py`) oraz próg `--min-score 85` w `scripts/render_jingle.py`. Poniżej progu poprawiasz recepturę i renderujesz ponownie, zanim wersję zapiszesz w metadanych; to pętla samokontroli z `legacy/source/INSTRUKCJA_PRODUKCJI_JINGLI.md`.
14. Żywe sample przed syntetykami (zasada twarda): syntetyczne brzmienia — generowane drony, pady, dzwonki, sweep-y, stingery — nadają się **prawie wyłącznie do scen science fiction**. W każdej innej scenie (fantasy, przyroda, dramat historyczny) jingle musi opierać się na żywych nagraniach ze zweryfikowanego rejestru (`data/sources.json`): co najmniej dwa wyraźnie słyszalne zdarzenia na samplach oraz punkt kulminacyjny zbudowany na samplu, nie na syntetyku. Nawet w scenie SF przynajmniej jedno zdarzenie ma być żywym nagraniem. Neutralne proceduralne tło szumowe (wiatr, woda) i delikatne detale szumowe są dozwolone w każdej scenie; wyjątek od zakazu dronu syntetycznego w scenie nie-SF wymaga wcześniejszej pozytywnej oceny tego elementu przez właściciela. `scripts/render_jingle.py` odrzuci, a `scripts/validate_versions.py` zweryfikują recepturę/metadane łamiące tę zasadę (pole `genre`: `sci-fi` zwalnia minimum do jednego żywego zdarzenia).

## Pętla pracy

W każdej pętli wykonaj:

1. **Audyt poprzedniej pracy:** sprawdź ostatni PR, commit lub wynik pracy poprzedniego agenta. Przeczytaj diff, uruchom dostępne testy i walidatory, zweryfikuj zgodność z dokumentacją oraz poszukaj regresji, niedokończonych fragmentów i błędów bezpieczeństwa. Jeśli znajdziesz problem, napraw go przed rozpoczęciem nowego zadania i opisz naprawę.
2. **Nowa produkcja:** wybierz losową nieopracowaną fabułę i utwórz jej pierwszą wersję `v1`. Jeśli nie ma już nowych fabuł, jawnie odnotuj ten fakt.
3. **Remake:** wyszukaj najgorzej oceniony nierozwiązany jingle spośród istniejących, zaplanuj poprawkę na podstawie ocen i komentarzy, a następnie utwórz kolejną wersję `vN`. Jeśli nie ma jeszcze ocenionego jingla wymagającego poprawy, odnotuj brak zadania.
4. **Rozwój warsztatu:** zbadaj lub ulepsz co najmniej jeden element narzędzi, dokumentacji, receptur albo biblioteki sampli. Zapisz konkretny rezultat.
5. **Publikację i kontrolę:** uruchom walidację, zbuduj Pages, przygotuj paczkę najlepszych MP3 i opisz zmiany.

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
