# Roadmapa wdrożenia modelu semantycznego (ADR 0006)

Cel: cztery bazy **reużywalnych** komponentów; fabuła najpierw opisana
semantycznie w czterech warstwach, potem obsadzona klockami przez
deterministyczny resolver. Jedyna twarda reguła: zakaz identycznej
kombinacji czterech wpisów.

Etapy wykonuj po kolei; każdy ma jasne artefakty i warunek ukończenia
(DoD). Statusy aktualizuj w tym pliku i w `docs/STATE.md`.

---

## Etap 0 — Porządki po ADR 0005 ✅ (2026-09-24)

Cofnięcie ślepej uliczki, zanim powstanie cokolwiek nowego.

- [x] ADR 0006 przyjęty; ADR 0005 oznaczony jako superseded.
- [x] Usunięty enforcement trybu wzrostu z `library_tool.py check`
      (zostaje twardy zakaz powtórki kombinacji; statystyki użycia
      w `report` pozostają informacyjne).
- [x] `data/usage-policy.json` zastąpione minimalną polityką
      (schema 2: `unique_combo` jako jedyna twarda reguła).
- [x] Testy trybu wzrostu usunięte/zastąpione testem braku limitów.
- [x] Bramka g014 wycofana (archiwum w `data/gates/g014/` zostaje jako
      dokumentacja; żaden kandydat nie wchodzi do bazy).
- [x] `AGENTS.md`, `docs/gate-protocol.md`, `docs/signature-system.md`,
      `docs/STATE.md` zaktualizowane.

DoD: `library_tool.py check` i pełne testy zielone bez reguł ADR 0005.

## Etap 1 — Profile semantyczne 510 fabuł

Opisanie **całego katalogu** czterema parametrami, bez patrzenia do
bibliotek audio. To surowiec dla kafeterii — świadomie luźny słownik.

- Artefakt: `data/semantics/story-profiles.json`
  (na fabułę: `background`, `hero`, `mood`, `instrumentation`;
  każde pole = swobodny opis + robocze słowa kluczowe).
- Praca partiami (np. po 50 fabuł), commit po każdej partii.
- Zakaz zaglądania do `data/library/*.json` podczas opisywania —
  profil wynika z narracji, nie z inwentarza.
- Sześć fabuł legacy też dostaje profile (dokumentacyjnie, bez zmiany
  ich sygnatur).

DoD: 510/510 fabuł ma komplet czterech pól; walidator kompletności
w `scripts/` przechodzi.

## Etap 2 — Kafeteria v1 (kontrolowany słownik)

Normalizacja surowych opisów z Etapu 1 do zamkniętego zbioru klas
kanonicznych + kontrolowanych cech.

- Analiza częstości surowych określeń; sklejanie synonimów i różnic
  czysto fabularnych (test z ADR 0006: ukryj lore — czy ten sam dźwięk
  obsłużyłby obie fabuły?).
- Artefakty:
  - `data/semantics/taxonomy.json` — klasy kanoniczne per warstwa
    (a/b/c/d), każda z definicją „co słychać”, przykładami i listą
    dozwolonych cech; pole `version: 1`;
  - `data/semantics/CHANGELOG.md` — każda późniejsza zmiana taksonomii
    to wpis z uzasadnieniem (kontrolowane rozszerzanie).
- Rozmiary klas wynikają z korpusu, nie z góry (spodziewane rzędy:
  20–35 środowisk, 40–80 klas hero, 12–20 nastrojów, kilkanaście
  charakterów instrumentacji — ale liczy się analiza, nie prognoza).
- **Przegląd właściciela (bramka tekstowa, nie audio):** lista klas
  z licznikami wystąpień do akceptacji/korekty. Po akceptacji v1 jest
  zamrożona.
- Remapowanie profili z Etapu 1 na klasy v1 (`class` + `traits`);
  raport fabuł, których nie dało się zmapować → kandydaci na nowe klasy
  przed zamrożeniem.

DoD: 100% profili zmapowane na taksonomię v1; właściciel zaakceptował
listę klas; walidator odrzuca profil z klasą spoza taksonomii.

## Etap 3 — Migracja bibliotek i receptur

Istniejące wpisy i receptury dostają metadane semantyczne.

- Każdy wpis `data/library/*.json` deklaruje:
  `semantics: {classes: [...], traits: [...], bad_for: [...]}`
  (klasy wyłącznie z taksonomii v1).
- Sześć receptur legacy dostaje `profile` (z Etapu 1) — bez przerabiania
  ich audio; to zapis, nie remiks.
- Walidator: wpis bez `semantics` lub z klasą spoza taksonomii = błąd
  `library_tool.py check`.

DoD: 18/18 wpisów otagowane; 6/6 receptur ma profil; check zielony.

## Etap 4 — Resolver

Deterministyczna obsada fabuły z miękkim balansem użycia.

- Artefakt: `scripts/resolver.py` + testy w
  `scripts/test_signature_system.py`.
- Wejście: profil fabuły + biblioteki + historia receptur.
  Wyjście: obsada czterech ról **albo** lista braków do bramki.
- Ranking wg ADR 0006: klasa > cechy > kary miękkie (częstość w klasie,
  świeżość, powtarzalne pary) > tie-break z id fabuły. Twardy filtr:
  kombinacja a·b·c·d nie może powtórzyć istniejącej receptury.
- Ślad decyzji zapisywany w recepturze:
  `resolution: {candidates, scores, reason}`.
- Audyt ostrzeżeń (nie zakazów) w `library_tool.py report`:
  najczęstszy wpis wybrany mimo równie dobrego rzadszego; natychmiastowa
  powtórka klocka; stała para gest–instrument; wpisy nigdy niekandydujące.

DoD: testy resolvera zielone (determinizm, nadrzędność semantyki,
preferencja rzadszego przy remisie, blokada duplikatu kombinacji);
uruchomienie na 6 recepturach legacy daje raport zgodności bez błędów
twardych.

## Etap 5 — Wznowienie produkcji (od fabuły 18)

- Fabuła 18 (Lotusguard Disciple): profil z Etapu 1 → resolver →
  braki → **jedna kompletna bramka** (3 kandydatów na każdy brak,
  wszystkie braki naraz) → akceptacje → receptura → render `--audit`
  → QA → gablotka/pack → push.
- Dalej normalna pętla: kolejne fabuły wg tej samej ścieżki; bazy rosną
  tylko tam, gdzie resolver wykazał realny brak klasy.
- Materiał z wycofanej g014 wolno wykorzystać ponownie **jako
  kandydatów**, jeśli profil fabuły 18 na to wskaże — ale decyduje
  profil, nie fakt, że pliki już istnieją.

DoD: `audio/signatures/18.mp3` wyrenderowane po pełnej ścieżce
profil→resolver→bramka; ślad decyzji w recepturze.

---

## Ryzyka i zabezpieczenia

- **Dryf słownika w Etapie 1** (każda fabuła „unikalna”): dopuszczalny —
  normalizuje go Etap 2; nie poprawiaj słownika w trakcie opisywania.
- **Zaglądanie do bazy podczas profilowania**: złamanie kolejności
  z ADR 0006; profil robimy wyłącznie z narracji.
- **Pełzające klasy po zamrożeniu v1**: każda nowa klasa wymaga wpisu
  w `data/semantics/CHANGELOG.md` z testem „ukryj lore”.
- **Resolver-łatwizna**: łapią go ostrzeżenia audytu i ślad decyzji
  w recepturze — audyt czyta się w każdej sesji (pętla pracy, krok 1).
