# Audyt odsłuchowy — instrukcja

Ten katalog jest **samodzielną aplikacją**: działa lokalnie, bez internetu.

## Jak odsłuchiwać

1. Ściągnij repozytorium na tej gałęzi (klon gita albo „Download ZIP”
   z GitHuba) i rozpakuj na pulpicie.
2. Otwórz podwójnym kliknięciem plik **`odsluch/index.html`**
   (Chrome/Edge/Firefox — cokolwiek nowszego).
3. Przy każdej fabule masz **wszystkie wersje jej sampla** z całej historii
   projektu: produkcyjne (to, co było w `audio/samples/` w danej epoce)
   i kandydatów z paczek wariantów. „OBECNY” = plik, który jest teraz
   w korpusie. Rozwiń „scenariusz / prompt tej generacji”, żeby zobaczyć,
   co dokładnie zamówiono.
4. **Zaptaszkuj** wersję, która podoba Ci się najbardziej — albo „ŻADNA”
   i wpisz w polu uwag, co jest nie tak / czego byś chciał.
5. Wybory zapisują się **same** w pamięci przeglądarki (localStorage).
   Przeładowanie strony czy restart komputera nie tracą postępu.
   Mimo to rób co jakiś czas **„💾 Kopia postępu”** — to plik JSON, który
   można potem wczytać przyciskiem „📂 Wczytaj kopię” (np. po przeniesieniu
   na inny komputer).

## Miniaturki kart

Strona szuka pliku `<numer>FOT.png` najpierw w `odsluch/img/`
(skopiuj tam swój folder `img` — wtedy działa wszędzie), a potem pod
ścieżką z ustawień (⚙ Folder miniatur), domyślnie:
`C:\Users\Jacek PC\Desktop\MtG Fusion\img\`.
Ścieżkę możesz zmienić w nagłówku strony.

## Koniec audytu

Na samym dole (i w nagłówku) jest przycisk **„Stwórz raport (JSON)”**.
Pobiera plik `raport-audytu-odsluchowego-<data>.json` ze wszystkimi
wyborami i komentarzami. **Wyślij ten plik agentowi** — na jego podstawie:

- zostanie złożony **dream team** (najlepsza wersja każdej fabuli wraca
  do `audio/samples/`),
- fabuły oznaczone „ŻADNA” dostaną nowy prompt zgodnie z Twoimi uwagami,
- przeprowadzę analizę preferencji (co się sprawdza, jakie parametry
  brzmią dobrze) na potrzeby przyszłych generacji.

## Uwagi techniczne

- Wersje z różnych epok mają różną głośność (normalizacja −20 LUFS
  weszła do produkcji dopiero 2026-09-28/29). Oceń brzmienie, nie poziom.
- Nazwy plików audio to skróty blobów gita (`<vid>.mp3`) — identyfikator
  wersji w raporcie mapuje się 1:1 na dokładną zawartość pliku z historii.
- Stronę przebudowuje `python scripts/build_listening_audit.py`
  (wymaga pełnej historii gita: `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`).

Wygenerowano: 2026-10-13 · commit `b60eaef102` · fabuł: 583 · wersji audio: 4803.
