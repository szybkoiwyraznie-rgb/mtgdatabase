# 0006. Model semantyczny: profil fabuły → kafeteria → resolver

- Status: accepted (decyzja właściciela 2026-09-24)
- Zastępuje: ADR 0005 (tryb wzrostu i limit 10% — **cofnięte w całości**)

## Kontekst

ADR 0005 (tryb wzrostu, limity procentowe) prowadził w ślepą uliczkę:
każda fabuła stawała się ręcznie kurowanym tworem z czterema nowymi
klockami, zamiast korzystać z reużywalnych baz. Właściciel cofnął
wszystkie limitowania i tryby wzrostowe oraz zdefiniował ideę od nowa.

## Decyzja

### Jedyna twarda reguła

Kombinacja czterech wpisów (tło, hero, koda, instrument) musi być
**unikalna między fabułami**. Nic więcej nie jest twardo zakazane.
Poszczególne klocki są reużywalne bez limitów ilościowych.

### Kolejność pracy nad fabułą

1. **Profil semantyczny** — fabuła jest rozbierana na cztery warstwy
   **zanim agent zajrzy do bibliotek**. Opis wynika wprost z narracji:
   - (a) tło/środowisko (las, jaskinia, rzeka, wietrzne góry, bagno…),
   - (b) hero — główny podmiot/wydarzenie (ryk bestii, wybuch, rzucenie
     czaru, diaboliczny śmiech, krakanie wron, płacz dziecka…),
   - (c) koda — nastrój (smutek, radość, zwycięstwo, klęska, nadzieja,
     zdrada…),
   - (d) instrumentacja — przymiotnik (delikatny, mocny, jasny, ciemny,
     głośny, cichy, twardy, miękki…).
2. **Dopasowanie** — dopiero po zapisaniu profilu agent sprawdza, czy
   bazy zawierają klocki obsługujące te opisy. Pasujące → użyte.
   Brakujące → kandydaci wg procedury bramki, **wszystkie braki fabuły
   w jednej bramce jednocześnie**.
3. **Montaż** — z kompletu klocków agent renderuje docelowe mp3.

### Kafeteria semantyczna (odpowiedź na p1)

Model hybrydowy: **kafeteria kontrolowana, baza audio otwarta**.

- Kafeteria v1 powstaje z analizy semantycznej **całego katalogu
  510 fabuł** (nie z arbitralnych liczb i nie przyrostowo per fabuła).
- Po zbudowaniu v1 główne klasy są zamrożone; nową klasę wolno dodać
  tylko, gdy żadna istniejąca nie opisuje zjawiska dźwiękowego
  (kontrolowane rozszerzenie, z wpisem w changelogu taksonomii).
- Baza audio rośnie organicznie: wpis wchodzi bramką, deklaruje które
  klasy kafeterii obsługuje.

### Klasa kanoniczna + cechy (odpowiedź na p2)

Taksonomia opisuje **to, co słychać**, nie lore. „Śmiech goblina”
i „śmiech orka” to ta sama klasa `zlosliwy_chichot` / `zlowrogi_smiech`,
jeśli po ukryciu ilustracji ten sam dźwięk byłby wiarygodny dla obu.

Każdy parametr profilu ma dwa poziomy:

1. **klasa kanoniczna** — decyduje o reużywalności (dopasowanie wpisu),
2. **cechy pomocnicze** (kontrolowany słownik) — wpływają na ranking,
   ale nie wymuszają nowego wpisu.

Test nowej klasy: *czy po ukryciu nazwy karty, gatunku i lore ten sam
dźwięk nadal mógłby obsłużyć istniejącą klasę?* Jeśli tak — to nie jest
nowa klasa. Nowa klasa wymaga różnicy **akustycznej i funkcjonalnej**
(płacz dziecka ≠ płacz dorosłego; eksplozja ≠ implozja).

### Resolver z miękkim balansem (odpowiedź na p3)

Żadnych globalnych limitów procentowych — rozkład fabuł bywa naturalnie
nierówny. Różnorodność kontroluje **deterministyczny ranking wewnątrz
zbioru semantycznie pasujących wpisów**:

```text
wynik = zgodność klasy
      + zgodność cech
      - kara za częste użycie w tej klasie
      - kara za użycie w ostatnich produkcjach
      - kara za często powtarzaną parę z pozostałymi klockami
      + deterministyczny tie-break (id fabuły)
```

Zgodność semantyczna jest nadrzędna: rzadki, ale źle pasujący klocek
nigdy nie wygrywa z właściwym. Receptura zapisuje ślad decyzji (profil,
kandydaci, ranking, powód wyboru). Audyt generuje **ostrzeżenia** (nie
zakazy), m.in.: wybrano najczęstszy wpis mimo równie dobrego rzadszego;
ten sam klocek wraca natychmiast; stała para gest–instrument; martwa
część bazy nigdy nie kandyduje.

### Klasa konieczna, nie wystarczająca (uzupełnienie 2026-09-24)

Pytanie właściciela: czy istnienie wpisu z pasującą klasą nie zamrozi
klasy na jednym wpisie, skoro traity są tylko rankingiem? Odpowiedź:
traity działają na **trzech poziomach**, z których dwa są twarde:

1. **weto `bad_for`** — jeśli profil wymaga cechy z listy `bad_for`
   wpisu, wpis odpada mimo zgodnej klasy;
2. **cechy wymagane** — profil może oznaczyć 1–2 cechy jako `required`;
   wpis, który ich nie obsługuje, nie jest kandydatem;
3. **cechy miękkie** — reszta traitów wpływa tylko na ranking.

**Brak → bramka** zachodzi więc, gdy klasa jest pusta ALBO gdy wszystkie
wpisy klasy odpadły przez weto/cechy wymagane. Tak klasy rosną wewnętrznie
pod ciśnieniem profili (chichot demona ≠ chichot wróżki przy tej samej
klasie), bez powrotu do limitów ilościowych. Dodatkowe ostrzeżenie audytu:
klasa często wołana, obsługiwana stale jednym wpisem → sygnał do
opcjonalnej bramki poszerzającej (decyzja świadoma, nie automat).

## Skutki

- `data/usage-policy.json` traci moc w wersji z ADR 0005; zostaje
  wyłącznie twardy zakaz powtórki kombinacji.
- Sześć zamrożonych fabuł (1, 2, 3, 4, 5, 8) pozostaje bez zmian;
  dostaną profile semantyczne retrospektywnie (dokumentacyjnie).
- Bramka g014 (fabuła 18) jest **wycofana** — obsada fabuły 18 zostanie
  wyprowadzona od nowa z profilu semantycznego po zbudowaniu kafeterii.
- Plan wdrożenia: `docs/roadmap-semantyka.md`.

### Jeden typ = jeden klocek (rozstrzygnięcie właściciela, 2026-09-24)

Właściciel skorygował interpretację modelu: **każdy typ (klasa)
taksonomii ma w bazie dokładnie jeden klocek audio — zawsze.** Klocek
jest fizyczną realizacją typu; relacja jest 1:1 w obu kierunkach.
To jest główna zasada modularności i ma pierwszeństwo przed wcześniejszymi
zapisami tego ADR.

Konsekwencje (zastępują mechanikę „klasy rosną wewnętrznie"
z uzupełnienia powyżej):

1. **Zakaz drugiego klocka w typie.** Baza rośnie WYŁĄCZNIE przez
   dodanie nowego typu wraz z jego jedynym klockiem. Dodanie typu to
   kontrolowane rozszerzenie taksonomii: wpis w
   `data/semantics/CHANGELOG.md` + akceptacja właściciela (bramka
   tekstowa), potem bramka audio na jedyny klocek tego typu.
2. **Reguła unikalności działa na poziomie typów.** Przy relacji 1:1
   kombinacja czterech typów = kombinacja czterech klocków. Dwie fabuły
   z identyczną czwórką typów łamią regułę.
3. **Kolizja = sygnał, że taksonomia jest za gruba.** Rozwiązaniem jest
   doprecyzowanie słownika: nowy typ dla jednej z fabuł, wyprowadzony
   z cech JUŻ zapisanych w jej profilu (profil pochodzi z narracji
   i nie wolno go naciągać). Nie zmienia się fabuły — precyzuje się
   słownik.
4. **Cechy `wymagane`, których typ nie realizuje**, prowadzą tą samą
   drogą do nowego typu (nie do drugiego klocka). Weto `bad_for`
   i cechy wymagane pozostają twardymi filtrami — rozstrzygają, czy
   istniejący typ w ogóle obsługuje profil.
5. **Ranking kandydatów** (deterministyczny, z uzasadnieniem w logu)
   stosuje się przy bramce audio — do wyboru JEDYNEGO klocka typu
   spośród zgromadzonych kandydatów — a nie do wyboru klocka per
   fabuła. Kary różnorodności per produkcja tracą przedmiot: powtarzanie
   klocka między fabułami to istota modularności, nie problem.
6. **Migracja (Etap 3)**: 18 istniejących klocków musi dostać 18
   RÓŻNYCH typów (przypisanie wzajemnie jednoznaczne). Audyt pilnuje
   niezmiennika 1:1 w obie strony.
