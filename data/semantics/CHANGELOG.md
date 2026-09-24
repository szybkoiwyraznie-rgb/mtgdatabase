# CHANGELOG taksonomii semantycznej

Każda zmiana `taxonomy.json` po zamrożeniu v1 wymaga wpisu tutaj
(data, co się zmieniło, dlaczego). Kontrolowane rozszerzanie — bez wpisu
zmiana nie przechodzi przeglądu.

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
