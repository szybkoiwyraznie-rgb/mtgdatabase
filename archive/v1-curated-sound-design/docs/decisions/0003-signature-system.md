# ADR 0003: System sygnatur z bramką klockową zamiast fabryki jingli

- Status: accepted (punkty 2 i 5 zmienione przez <a href="0004-wlasciciel-dozoruja-baze-agent-montuje.md">ADR 0004</a>: bramka = dozór przyjęć do bazy, agent obsadza i montuje, kandydaci bramek commitowani)
- Data: 2026-09-23

## Decyzja

1. Dwanaście dotychczasowych jingli i dawna pętla produkcyjna zostają
   skasowane/archiwizowane (`legacy/old-factory/`). Produkcja przechodzi na
   **system sygnatur**: fabuła = tło (d) + hero (c) + koda muzyczna (a)
   grana na instrumencie (b), wyłącznie z zatwierdzonych klocków czterech baz.
2. Bazy startują puste i rosną organicznie; klocek wchodzi do bazy tylko
   przez **bramkę odsłuchową w sandboxie** (minimum 3 kandydatów, wybór
   właściciela w czacie). Pages nie jest bramką.
3. Produkt końcowy ma bezwzględnie nazwę `<id>.mp3` (płasko, także w ZIP).
4. Zakaz powtórki kombinacji a·b·c·d między fabułami; zasada „rola przed
   plikiem" przy pozyskiwaniu.
5. Odrzuceni kandydaci nigdy nie są commitowani.

## Uzasadnienie

Właściciel: produkcja ok. 10 jingli pochłonęła wiele rund ocen per utwór,
a efekt nie był nastrojowy; koszt liniowy od liczby fabuł czynił cel
nieosiągalnym. Analiza (udokumentowana w czacie sesji 2026-09-23): wąskim
gardłem była ewaluacja audio zepchnięta na właściciela przy każdym utworze;
kolaż foley to najtrudniejsze medium do automatycznej kontroli jakości;
unikalna kompozycja per fabuła walczyła z naturą game audio. Nowy system
kompresuje pracę uszna do obsadzenia klocków, a jakość wynika z konstrukcji
(zatwierdzone składniki i gesty), nie z iterowanej oceny miksu.

## Konsekwencje

Znikają: wersjonowanie vN, oceny z issues, kolejka remaków, feedback worker,
stary ZIP „best jingles". Pojawia się: protokół bramki (`docs/gate-protocol.md`),
cztery rejestry (`data/library/`), `render_signature.py` z bramkami montażu,
gablotka Pages (bez formularza ocen). Właściciel angażuje się synchronicznie
w sesiach z bramką — ograniczenie świadomie przyjęte („droga ważniejsza niż
cel").
