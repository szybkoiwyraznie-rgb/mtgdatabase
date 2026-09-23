# Instrukcje dla agentów

Repozytorium produkuje **sygnatury dźwiękowe** fabuł (okna ≤10 s). Przed
pracą przeczytaj `docs/required-reading.md`, `docs/signature-system.md`
i `docs/gate-protocol.md`.

## Zasady nadrzędne

1. **Jedna fabuła = jeden produkt**: `audio/signatures/<id>.mp3`. Nazwa to
   bezwzględnie numer fabuły; wersjonowanie wewnątrz gita, nie w nazwach.
2. Fabuła składa się z czterech klocków a (koda), b (instrument), c (hero),
   d (tło) — wyłącznie z baz `data/library/*.json`.
3. **Bramka odsłuchowa** (`docs/gate-protocol.md`): klocek wchodzi do bazy
   tylko wyborem właściciela. Minimum 3 kandydatów na brak, odrzuty nigdy
   nie są commitowane (`work/` jest poza gitem).
4. **Rola przed plikiem**: najpierw rola semantyczna, potem sprawdzenie bazy,
   dopiero potem pozyskiwanie. Nie dublować obsadzonych ról nowymi plikami.
5. **Zakaz powtórki kombinacji**: para (tło, hero, koda, instrument) musi być
   unikalna między fabułami. Weryfikuje `library_tool.py check`.
6. Hero i teła to **żywe nagrania** ze zweryfikowanych źródeł; instrumenty to
   prawdziwe nagrania instrumentów (VCSL/VSCO). Synteza proceduralna tylko dla
   fabuł z klimatem sci-fi i tylko jako uzupełnienie.
7. Natywna wysokość sampli (`pitch` 0,7–1,0 max w dół dla hero); opcjonalnie
   tylko `offset_sec`, `length_sec`, łagodny filtr, `target_db`, `pan`.
   **Audycja obowiązkowa** (`stem_probe.py`) — ustawiaj offset na głośny
   fragment, patrz LESSONS 2026-09-22 (ciche głowy nagrań).
8. Każdy wpis bazy ma proweniencję: źródło, autor, licencja, url, kanał
   pobrania (w polu `source`). **Licencja nieznana nie blokuje przyjęcia** —
   projekt jest prywatny i niekomercyjny (decyzja właściciela 2026-09-23);
   zapisz `"license": "brak informacji"` i pracuj dalej. Materiał jawnie
   wolny ma pierwszeństwo; jawne zastrzeżenia komercyjne oznacz, bo dotyczą
   publikacji na Pages/Release. Szczegóły: `docs/sources-and-licensing.md`.
9. Nie umieszczaj sekretów w kodzie/danych. Pages jest publiczny.
10. Decyzje jednoznaczne wykonuj bez pytań; pytaj przy ryzyku utraty danych
    lub nieodwracalnej publikacji.
11. Raport końcowy: obrobione fabuły, przebieg bramki, wyniki QA renderów,
    zmiany w bazach, ryzyka, następny krok.

## Pętla pracy

1. **Audyt**: przeczytaj ostatni PR/diff, uruchom `python -m compileall -q scripts`,
   `python scripts/test_signature_system.py`, `python scripts/library_tool.py check`.
   Napraw regresje przed nową pracą.
2. **Produkcja** (model ADR 0004): bramka = 3 kandydaci **na jeden wpis**
   (np. „3 jeziora"), właściciel wybiera dokładnie jednego → tylko wybrany
   trafia do bazy (`library_tool.py accept`). Agent sam obsadza fabułę z bazy
   (role d/c/a/b), układa recepturę i renderuje z `--audit`; twardy render
   autokalibruje słyszalność nut kody — pełne liczby w raporcie, odsłuch
   fabuły przez właściciela nie jest częścią pętli. **Agent sam decyduje,
   który wpis idzie do następnej bramki** i sam dobiera kandydatów — nie
   pytaj właściciela „co teraz?”, przedstaw gotową bramkę.
2a. **Rola wynika z narracji konkretnej fabuły**, nigdy z tego, co leży
   w bazie. Wpis o pasującej nazwie, ale nie pasujący do sceny, to BRAK →
   bramka. Hero jest tożsamością fabuły **1:1** — nie obsadzaj nim drugiej.
   Złamanie tych reguł kosztowało wycofanie dwóch gotowych fabuł.
3. **Warsztat**: co najmniej jedna poprawka narzędzi/dokumentacji/bazy w sesji.
4. **Publikacja**: `python scripts/build_pack.py` (test ZIP),
   `python scripts/build_site.py` (test gablotki), `git status`, commit, push.
   **Commituj wcześnie i często** (bramkę od razu po zbudowaniu); po pierwszym
   pushu sesji otwórz pull request. Sandbox potrafi resetować stan lokalny —
   patrz ENVIRONMENT.md §1-2.

## Stary system

`legacy/old-factory/` to archiwum (dawna fabryka jingli, oceny z issues,
workery). Nie rozwijać, nie importować. Aktualne prawo: cztery bazy
+ protokół bramki.
