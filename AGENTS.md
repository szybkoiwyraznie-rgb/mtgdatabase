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
4. **Profil przed bazą (ADR 0006)**: fabułę najpierw rozbierz semantycznie
   na cztery warstwy — (a) tło/środowisko, (b) hero/zdarzenie, (c) nastrój
   kody, (d) przymiotnik instrumentacji — **zanim zajrzysz do bibliotek**.
   Profil wynika z narracji, nie z inwentarza. Dopiero potem dopasowanie:
   pasujące klocki → użyte, braki → jedna kompletna bramka. Opisuj to,
   co słychać, nie lore („śmiech goblina” i „śmiech orka” to ta sama klasa).
5. **Reuse bez limitów, różnorodność miękko**: klocki są reużywalne —
   żadnych trybów wzrostu ani progów procentowych (cofnięte ADR 0006).
   O wyborze spośród pasujących decyduje deterministyczny ranking resolvera
   (semantyka nadrzędna, potem preferencja rzadziej używanych); audyt
   generuje ostrzeżenia, nie zakazy. Plan wdrożenia: `docs/roadmap-semantyka.md`.
6. **Jedyna twarda reguła kombinacji**: zestaw (tło, hero, koda, instrument)
   musi być unikalny między fabułami. Weryfikuje `library_tool.py check`.
7. Hero i teła to **żywe nagrania** ze zweryfikowanych źródeł; instrumenty to
   prawdziwe nagrania instrumentów (VCSL/VSCO). Synteza proceduralna tylko dla
   fabuł z klimatem sci-fi i tylko jako uzupełnienie.
8. Natywna wysokość sampli (`pitch` 0,7–1,0 max w dół dla hero); opcjonalnie
   tylko `offset_sec`, `length_sec`, łagodny filtr, `target_db`, `pan`.
   **Audycja obowiązkowa** (`stem_probe.py`) — ustawiaj offset na głośny
   fragment, patrz LESSONS 2026-09-22 (ciche głowy nagrań).
9. Każdy wpis bazy ma proweniencję: źródło, autor, licencja, url, kanał
   pobrania (w polu `source`). **Licencja nieznana nie blokuje przyjęcia** —
   projekt jest prywatny i niekomercyjny (decyzja właściciela 2026-09-23);
   zapisz `"license": "brak informacji"` i pracuj dalej. Materiał jawnie
   wolny ma pierwszeństwo; jawne zastrzeżenia komercyjne oznacz, bo dotyczą
   publikacji na Pages/Release. Szczegóły: `docs/sources-and-licensing.md`.
10. Nie umieszczaj sekretów w kodzie/danych. Pages jest publiczny.
11. Decyzje jednoznaczne wykonuj bez pytań; pytaj przy ryzyku utraty danych
    lub nieodwracalnej publikacji.
12. Raport końcowy: obrobione fabuły, przebieg bramki, wyniki QA renderów,
    zmiany w bazach, ryzyka, następny krok.

## Pętla pracy

1. **Audyt**: przeczytaj ostatni PR/diff, uruchom `python -m compileall -q scripts`,
   `python scripts/test_signature_system.py`, `python scripts/library_tool.py check`.
   Napraw regresje przed nową pracą.
2. **Produkcja** (model ADR 0004 + 0006): najpierw zapisz profil semantyczny
   fabuły (cztery warstwy, bez zaglądania do baz), potem dopasuj klocki.
   Jedna bramka sesji ma od razu zawierać
   **wszystkie brakujące wpisy dla fabuły**, po 3 kandydatów na każdy wpis
   (np. 3 jeziora + 3 hero + 3 kody + 3 instrumenty), żeby właściciel nie
   dostawał potrzeb fabuły ratami. Właściciel wybiera dokładnie jednego na
   wpis → tylko wybrani trafiają do baz (`library_tool.py accept`). Agent
   układa recepturę i renderuje z `--audit`; twardy render
   autokalibruje słyszalność nut kody — pełne liczby w raporcie, odsłuch
   fabuły przez właściciela nie jest częścią pętli. **Agent sam decyduje,
   który wpis idzie do następnej bramki** i sam dobiera kandydatów — nie
   pytaj właściciela „co teraz?”, przedstaw gotową bramkę.
2a. **Rola wynika z narracji konkretnej fabuły**, nigdy z tego, co leży
   w bazie. Wpis o pasującej nazwie, ale nie pasujący do sceny, to BRAK →
   bramka. Powtórzenie hero między fabułami jest silnie karane w rankingu
   (ryzyko „fabuła 8 = fabuła 1 z innym tłem”), choć twardy jest tylko
   zakaz identycznej kombinacji czterech klocków.
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
