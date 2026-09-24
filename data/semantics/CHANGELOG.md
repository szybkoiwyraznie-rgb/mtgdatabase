# CHANGELOG taksonomii semantycznej

## 2026-09-24 — korekta modelu: jeden typ = jeden klocek + propozycja 4 nowych typów hero (CZEKA NA AKCEPTACJĘ)

**Korekta rozstrzygnięciem właściciela** (unieważnia pkt 3 wpisu
o akceptacji v1 poniżej): każdy typ ma dokładnie jeden klocek audio (1:1),
więc `unique_combo` działa już na poziomie typów. Powtórzona kombinacja
czterech typów między fabułami JEST naruszeniem. Rozwiązaniem kolizji jest
doprecyzowanie taksonomii (nowy typ wyprowadzony z cech profilu), nigdy
drugi klocek w typie i nigdy naciąganie fabuły. Szczegóły: ADR 0006,
aneks „Jeden typ = jeden klocek".

**Propozycja rozszerzenia v1 → v2** (rozbija wszystkie 4 kolizje,
zweryfikowano: 510/510 kombinacji unikalnych, zero nowych kolizji) —
4 nowe typy hero:

1. `slup-wody` — „Wzbierający słup wody": pionowa, narastająca kolumna
   wody (nie uderzenie fali). Dla fabuły 508; `fala-rozbryzg` traci
   wzorzec „słup wody". Kolizja 133↔508 rozbita.
2. `szelest-papieru` — papier w ruchu: mapa, kartkowanie, zwój.
   Przejmuje fabuły 65, 322, 377, 381, 580 z `chrobot-szelest`.
   Kolizja 232↔580 rozbita.
3. `budzenie-gleby` — praca gleby: ściółka, rozkład, kiełkujące
   nasiona (bez strzelających pędów). Przejmuje 289, 438, 473, 491;
   `wzrost-roslin` oddaje wzorce „nasion/kiełk/żyzn". Kolizja
   438↔471 rozbita.
4. `ciche-wrota` — bezgłośny mechanizm: uniesienie kraty, sunięcie
   łodzi w ciszy. Dla fabuły 570. Kolizja 570↔586 rozbita.

Hero: 50 → 54 typy. Status: propozycja — taksonomia pozostaje na
`version: 1` do bramki tekstowej właściciela.

Każda zmiana `taxonomy.json` po zamrożeniu v1 wymaga wpisu tutaj
(data, co się zmieniło, dlaczego). Kontrolowane rozszerzanie — bez wpisu
zmiana nie przechodzi przeglądu.

## 2026-09-24 — akceptacja i zamrożenie v1 (`version: 1`)

Bramka tekstowa Etapu 2 — decyzje właściciela:

1. Klasa `mroczno-ciezka` (140 fabuł) **rozbita** na `mroczna` (barwa; 90)
   i `ciezka` (masa/niski rejestr; 50). Instrumentacja: 17 → 18 klas.
2. Klasy o 1–3 fabułach **pozostają** (akustycznie odrębne; urosną wraz
   z nowymi fabułami).
3. Potwierdzone rozumienie reguły twardej: `unique_combo` dotyczy
   **bloków audio w recepturach**, nie klas taksonomii. Powtórzona
   kombinacja klas między fabułami jest dozwolona — resolver ma
   obowiązek dobrać różniący się zestaw bloków (cechy `wymagane`/`bad_for`
   + kary różnorodności), a gdy w bazie brakuje drugiego bloku danej
   klasy, powstaje bramka na **nowego kandydata-blok** (organiczny wzrost
   baz), nigdy nowa klasa.

Stan po zamrożeniu: 29 środowisk / 50 hero / 20 nastrojów /
18 instrumentacji; mapowanie 510/510.

## 2026-09-24 — szkic v1 (`version: 1-draft`)


- Pierwsza wersja taksonomii wyprowadzona z analizy korpusu 510 profili
  (Etap 1): 29 klas środowisk (a), 50 klas hero (b), 20 nastrojów kody (c),
  17 charakterów instrumentacji (d).
- Klasy opisują akustykę („co słychać"), nie lore — zgodnie z ADR 0006.
- Rozmiary klas wynikają z korpusu; mieszczą się w rzędach spodziewanych
  w roadmapie (20–35 / 40–80 / 12–20 / kilkanaście).
- Wstępne mapowanie regułowe (wzorce w `taxonomy.json`, skrypt
  `scripts/map_profiles.py`) pokrywa 510/510 fabuł we wszystkich
  czterech warstwach.
- Status: **szkic** — czeka na bramkę tekstową właściciela (akceptacja
  listy klas). Po akceptacji `version` zmienia się na `1` i taksonomia
  zostaje zamrożona.
