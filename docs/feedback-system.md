# System ocen

Formularz przy najnowszej wersji jingla ma trzy pola liczbowe 1–5 i komentarz:

- feeling ogólny;
- zgodność z fabułą;
- jakość wykorzystanych sampli;
- komentarz tekstowy.

Wynik jest sumą trzech wartości, od 3 do 15.

## Zapis

Docelowy przycisk `Prześlij raport` wysyła dane do jednorazowo skonfigurowanego endpointu, który tworzy lub aktualizuje GitHub Issue. Token GitHub nie może znajdować się w kodzie Pages. Issue musi zawierać `story_id`, `version`, trzy oceny, sumę, komentarz i timestamp.

## Kolejka popraw

Otwarte raporty otrzymują etykietę `needs-review`. Agent sortuje je po sumie rosnąco, rezerwuje najgorsze zadanie, tworzy kolejną wersję i zamyka raport dopiero po udanej publikacji nowego renderu.
