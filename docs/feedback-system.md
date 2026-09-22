# System ocen

Formularz przy najnowszej wersji jingla ma trzy pola liczbowe 1–5 i komentarz:

- feeling ogólny;
- zgodność z fabułą;
- jakość wykorzystanych sampli;
- komentarz tekstowy.

Wynik jest sumą trzech wartości, od 3 do 15.

## Zapis

Docelowy przycisk `Prześlij raport` wysyła dane do jednorazowo skonfigurowanego endpointu, który tworzy lub aktualizuje GitHub Issue. Token GitHub nie może znajdować się w kodzie Pages. Issue musi zawierać `story_id`, `version`, trzy oceny, sumę, komentarz i timestamp.

## Natychmiastowe wyświetlanie

Po udanym wysłaniu strona od razu zapisuje ocenę w `localStorage` przeglądarki i pokazuje ją jako „X/15 · na tym urządzeniu" — na karcie wersji oraz na liście katalogu. To warstwa tymczasowa na danym urządzeniu, nie substytut zapisu.

## Automatyczny zapis ocen

Workflow `Sync ratings from issues` reaguje na każde nowe lub edytowane issue z etykietą `feedback`: uruchamia `scripts/sync_ratings.py`, zapisuje oceny w `data/versions.json` w commicie bota i odpala przebudowę Pages oraz paczki ZIP. Efekt: ocena jest trwale widoczna na wszystkich urządzeniach w ciągu kilku minut, a `best-jingles-latest.zip` w Releases aktualizuje się sam. Agent w każdej pętli weryfikuje synchroniczność ręcznie (patrz `docs/agent-workflow.md`).

## Kolejka popraw

Otwarte raporty otrzymują etykietę `needs-review`. Agent sortuje je po sumie rosnąco, rezerwuje najgorsze zadanie, tworzy kolejną wersję i zamyka raport dopiero po udanej publikacji nowego renderu. Ten ostatni krok automatyzuje `scripts/close_served_reports.py` w workflow `Sync ratings from issues` (odpala się też na push `data/versions.json`): raport dotyczący `vN` zamyka się z komentarzem, gdy w metadanych istnieje nowsza wersja `vM`. Raport o najnowszej wersji nigdy nie zamyka się automatycznie — czeka na własną ocenę.
