# CHANGELOG taksonomii semantycznej

## 2026-09-24 — v4: rozbicie szerokiego typu `smiech` (korekta właściciela)

Właściciel: demonic_laugh_02 to nie szeroki „śmiech" — to śmiech
maniakalny/demoniczny, w dodatku męski (nie obsłuży ról żeńskich).
Typ `smiech` rozbity wg realnych odcieni w korpusie (4 fabuły → 4 typy):

- `smiech-maniakalny` — złośliwy, diaboliczny chichot (fabuła 3;
  klocek `demonic_laugh_02`, traits + „męski", bad_for + „kobiecy głos");
- `smiech-widmowy` — bezcielesne echa śmiechu (fabuła 48; bez klocka);
- `smiech-biesiadny` — gromadny śmiech zabawy z klaskaniem (fabuła 138;
  bez klocka);
- `smiech-dzieciecy` — jasny śmiech dzieci (fabuła 187; bez klocka).

Hero: 56 → 59 typów. Po remapie: 510/510 kombinacji unikalnych, zero
kolizji. Płeć/wiek głosu zapisujemy w traits/bad_for klocka — przyszły
kobiecy śmiech dostanie własny typ, gdy zawoła go profil.

## 2026-09-24 — v3: decyzje właściciela (ognisko + krakanie + wrzask bandy)

1. **Zaakceptowany** typ tła `ognisko-palenisko` (30 typów tła);
   `pending-types.json` opróżnione; fabuły 190 i 500 przechodzą do
   nowego typu.
2. **Korekta właściciela:** krakanie to nie krzyk ptaka drapieżnego.
   Nowy typ hero `krakanie` (chrapliwe kraknięcia krukowatych);
   `krzyk-ptaka` zawężony do drapieżnych pisków (sokół/orzeł/gryf).
   Klocek `raven_yell_long_01` przetagowany na `krakanie`; fabuły 1 i 42
   przechodzą do `krakanie`.
3. **Korekta właściciela:** wielogłosowy wrzask bandy to nie szeroki
   okrzyk bojowy. Nowy typ hero `wrzask-bandy` (kilka rozstrojonych
   głosów podchwytuje krzyk); klocek `warband_cry_03` przetagowany.
   Typ `okrzyk-bojowy` zostaje bez klocka (dozwolone — klocek przyjdzie
   bramką, gdy zawoła go produkcja).

Hero: 54 → 56 typów. Po remapie: 510/510 kombinacji unikalnych, zero
kolizji.

## 2026-09-24 — Etap 3: migracja bibliotek + propozycja typu `ognisko-palenisko` (CZEKA NA AKCEPTACJĘ)

- 18/18 klocków otagowane `semantics: {type, traits, bad_for}`; typy
  wzajemnie różne w każdej bazie (niezmiennik 1:1 pilnowany przez
  `library_tool.py check`).
- 6/6 receptur legacy dostało pole `profile` (typy wg taksonomii v2,
  zapis dokumentacyjny — audio bez zmian).
- **Propozycja nowego typu tła** `ognisko-palenisko` („Małe ognisko /
  palenisko z bliska: oszczędne trzaski żaru, kameralne ciepło ognia")
  dla klocka `fire_hearth_small_01` — nie mieści się uczciwie w żadnym
  z 29 typów tła. Do akceptacji: `data/semantics/pending-types.json`;
  walidator zgłasza go jako OSTRZEŻENIE do czasu decyzji.

## 2026-09-24 — korekta modelu: jeden typ = jeden klocek + 4 nowe typy hero (ZAAKCEPTOWANE → v2)

Właściciel zaakceptował propozycję („kontynuuj" po bramce tekstowej).
Taksonomia podniesiona do `version: 2`: hero 50 → 54 typy
(`slup-wody`, `szelest-papieru`, `budzenie-gleby`, `ciche-wrota`).
Po remapie: **510/510 kombinacji unikalnych, zero kolizji.**

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
