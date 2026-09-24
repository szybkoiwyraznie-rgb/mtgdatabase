# CHANGELOG taksonomii semantycznej

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
