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
13. Render publikujesz dopiero po audycie QA ≥85/100 (QA v2, `scripts/qa_score.py`): bramki techniczne (DC offset, headroom, ciągłość tła), głośność (RMS ≥ −26 dB), balans widma (udział >6 kHz ≤ 12% — „papierowy" charakter odrzuconej partii) oraz **słyszalność każdego opisanego żywego zdarzenia ≥ +6 dB nad tłem**; kontrast kulminacji jest tylko informacyjny (stara metryka climax-ratio oceniała rendery 3/15 na 100/100). Próg `--min-score 85` w `scripts/render_jingle.py`; poniżej progu poprawiasz recepturę i renderujesz ponownie, zanim wersję zapiszesz w metadanych. Bramka mierzy obecność dźwięku, nie fit do fabuły — ostatecznym sędzią zgodności z fabułą pozostaje ocena właściciela.
14. Żywe sample przed syntetykami (zasada twarda): syntetyczne brzmienia — generowane drony, pady, dzwonki, sweep-y, stingery — nadają się **prawie wyłącznie do scen science fiction**. W każdej innej scenie (fantasy, przyroda, dramat historyczny) jingle musi opierać się na żywych nagraniach ze zweryfikowanego rejestru (`data/sources.json`): co najmniej dwa wyraźnie słyszalne zdarzenia na samplach oraz punkt kulminacyjny zbudowany na samplu, nie na syntetyku. Nawet w scenie SF przynajmniej jedno zdarzenie ma być żywym nagraniem. Neutralne proceduralne tło szumowe (wiatr, woda) i delikatne detale szumowe są dozwolone w każdej scenie; wyjątek od zakazu dronu syntetycznego w scenie nie-SF wymaga wcześniejszej pozytywnej oceny tego elementu przez właściciela. Dopuszczalny wyjątek: krótki sub-impakt syntetyczny wzmacniający żywe zdarzenie (precedens: pochwalone kroki Balotha z subem w 2 v2) — nie może zastępować żywego sampla ani grać samodzielnie. `scripts/render_jingle.py` odrzuci, a `scripts/validate_versions.py` zweryfikują recepturę/metadane łamiące tę zasadę (pole `genre`: `sci-fi` zwalnia minimum do jednego żywego zdarzenia).
15. Wysokość sampli (decyzja właściciela 2026-09-22, skorygowana po audycie porażek): domyślnie natywna wysokość; **dozwolone jest umiarkowane obniżanie `pitch` 0,7–1,0** (kruk −12% i grizzly −25% w chwalonych jinglach v1; impact 0,72 w ocenionym 15/15 568 v2). Zakazane jest podbicie w górę (`pitch > 1`) — to ono niszczyło rozpoznawalność w odrzuconej partii. Inny charakter bestii czy materiału = najpierw inny sample z biblioteki, pitch w dół tylko jako doprawienie. Dozwolone przy samplu: `offset_sec` (wybór fragmentu), `length_sec` (długość odtwarzania), łagodny `hp_hz`, `target_db`, `pan`. **Audycja obowiązkowa**: przed użyciem sampla sprawdź jego profil (`scripts/stem_probe.py`) i ustaw `offset_sec` na głośny fragment — silnik odrzuca segmenty cichsze o ponad 12 dB od najgłośniejszego okna nagrania (to ciche głowy nagrań zniszczyły partię 3–5/15). Historycznych artefaktów i ich receptur nie przepisuj.

## Pętla pracy

W każdej pętli wykonaj:

1. **Audyt poprzedniej pracy:** sprawdź ostatni PR, commit lub wynik pracy poprzedniego agenta. Przeczytaj diff, uruchom dostępne testy i walidatory, zweryfikuj zgodność z dokumentacją oraz poszukaj regresji, niedokończonych fragmentów i błędów bezpieczeństwa. Jeśli znajdziesz problem, napraw go przed rozpoczęciem nowego zadania i opisz naprawę.
2. **Nowa produkcja:** wybierz losową nieopracowaną fabułę i utwórz jej pierwszą wersję `v1`. Jeśli nie ma już nowych fabuł, jawnie odnotuj ten fakt.
3. **Remake:** kolejką steruje **najlepsza oceniona wersja fabuły**, nie najgorsza pojedyncza wersja. Szereguj fabuły rosnąco po ich najlepiej ocenionej wersji i remakuj fabułę o najniższym wyniku najlepszej wersji; nisko oceniony remake (np. v2 przy znacznie lepszym v1) nie podbija fabuły w kolejce ponad jej najlepszą wersję. **Zasady progów remake'ów (doprecyzowanie właściciela 2026-09-23):** kolejka obejmuje wszystkie fabuły z otwartymi raportami, uszeregowane od najgorzej ocenianych — **nie ma bana na remaki jingli 12/15 i wyżej**; każdy wynik poniżej 15/15 może zostać poprawiony, a dla 15/15 remake nie ma sensu (pomijaj, chyba że właściciel wyraźnie zleci). **Ochrona pochwalonych sampli (decyzja właściciela 2026-09-23, zasada twarda):** jeśli jakakolwiek wersja fabuły ma ocenę **powyżej 10/15**, każdy kolejny remake tej fabuły **obowiązkowo** wykorzystuje **dokładnie te same efekty dźwiękowe, które właściciel wprost pochwalił w komentarzu tekstowym** do tej wersji — te same pliki sampli (nie „podobne"), z tym samym masterowaniem (offset, pitch, filtry, głośność, pozycja). Remake „od zera" (nowa koncepcja, nowe sample) dotyczy **wyłącznie** fabuł, w których żadna wersja nie przekroczyła 10/15; iterowanie na odrzuconej recepturze dało 475 v2 („niczym się nie różni"), a wyrzucenie pochwalonych sampli zepsuło 2 v2 („zniknął rewelacyjny świetny ryk balotha") i 5 v3 („brakuje tych fajnych sampli z v1"). Fabuła, której najnowsza wersja czeka jeszcze na ocenę, nie wchodzi do kolejki (nie stackuj wersji). Kolejkę z wypisanymi obowiązkami wypisze `python scripts/remake_queue.py --versions data/versions.json`. Jeśli nie ma ocenionej fabuły wymagającej poprawy, odnotuj brak zadania.
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
