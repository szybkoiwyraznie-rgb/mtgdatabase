# System ocen

Formularz oceny pokazuje się wyłącznie przy wersjach bez oceny i ma trzy pola liczbowe 1–5 oraz komentarz:

- feeling ogólny;
- zgodność z fabułą;
- jakość wykorzystanych sampli;
- komentarz tekstowy.

Wynik jest sumą trzech wartości, od 3 do 15. Wersja, która ma już ocenę, pokazuje na swojej karcie wynik z rozbiciem na trzy kryteria oraz **komentarze tekstowe właściciela** (najnowszy na górze, z datą i linkiem do issue) zamiast formularza — poprawy wprowadza się jako nową wersję `vN`, a nie przez ponowne ocenienie. Na liście fabuł karta, która ma ocenę i nowszą nieocenioną wersję, dostaje badge „nieoceniona nowa wersja" obok znacznika „najlepiej x/15".

Karty wersji na stronach fabuł (decyzje właściciela 2026-09-23):

- **kolejność:** najpierw wersje oczekujące na ocenę (najnowsza na górze), potem ocenione od najwyższej do najniższej oceny;
- **kolorowe ramki:** wersje bez oceny mają ramkę amber (oczekiwanie na ocenę), wersja z najwyższą oceną fabuły — ramkę zieloną, pozostałe wersje są bez wyróżnienia.

## Zapis

Docelowy przycisk `Prześlij raport` wysyła dane do jednorazowo skonfigurowanego endpointu, który tworzy lub aktualizuje GitHub Issue. Token GitHub nie może znajdować się w kodzie Pages. Issue musi zawierać `story_id`, `version`, trzy oceny, sumę, komentarz i timestamp.

## Natychmiastowe wyświetlanie

Po udanym wysłaniu strona od razu zapisuje ocenę w `localStorage` przeglądarki i pokazuje ją jako „X/15 · na tym urządzeniu" — na karcie wersji oraz na liście katalogu. To warstwa tymczasowa na danym urządzeniu, nie substytut zapisu.

## Automatyczny zapis ocen

Workflow `Sync ratings from issues` reaguje na każde nowe lub edytowane issue z etykietą `feedback`: uruchamia `scripts/sync_ratings.py`, zapisuje oceny w `data/versions.json` w commicie bota i odpala przebudowę Pages oraz paczki ZIP. Efekt: ocena jest trwale widoczna na wszystkich urządzeniach w ciągu kilku minut, a `best-jingles-latest.zip` w Releases aktualizuje się sam. Agent w każdej pętli weryfikuje synchroniczność ręcznie (patrz `docs/agent-workflow.md`).

## Kolejka popraw

Otwarte raporty otrzymują etykietę `needs-review`. Kolejkę remaków określa **najlepsza oceniona wersja fabuły** (rosnąco), nie najniższa pojedyncza ocena: nisko oceniony remake przy lepszym oryginale nie podbija fabuły w kolejce, a fabuła, której najnowsza wersja czeka na ocenę, czeka na swoją kolej (`scripts/remake_queue.py`). Zasady progów (doprecyzowanie właściciela 2026-09-23): kolejka biegnie od najgorzej ocenianych i **nie wyklucza jingli 12–14/15** — każdy wynik poniżej 15/15 może być lepszy; dla 15/15 remake nie ma sensu (pomijaj, chyba że wyraźne zlecenie właściciela); przy najlepszej wersji powyżej 10/15 remake obowiązkowo zachowuje sample wprost pochwalone w komentarzach (te same pliki i masterowanie). Agent rezerwuje zadanie, tworzy kolejną wersję na fundamencie najlepiej ocenionej wersji fabuły i zamyka raport dopiero po udanej publikacji nowego renderu. Ten ostatni krok automatyzuje `scripts/close_served_reports.py` w workflow `Sync ratings from issues` (odpala się też na push `data/versions.json`): raport dotyczący `vN` zamyka się z komentarzem, gdy w metadanych istnieje nowsza wersja `vM`. Raport o najnowszej wersji nigdy nie zamyka się automatycznie — czeka na własną ocenę.
