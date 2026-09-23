# ADR 0005: Najpierw wzrost baz, potem kontrolowany reuse

- Status: accepted (próg wzrostu skorygowany przez właściciela z 50 do 10
  wpisów na kategorię tego samego dnia)
- Data: 2026-09-23

## Kontekst

Po sześciu sygnaturach małe bazy zaczęły wymuszać pozornie wygodny reuse:
`g4b_mystery_tritone` wystąpił w 3/6 produkcji, a `b_wine_glasses`,
`b_piano_steinway` i `fire_hearth_small_01` po 2/6. Właściciel wskazał, że
na etapie czterech wpisów w kategorii taki proces utrwala kilka brzmień
zamiast rozwijać język całej kolekcji.

Drugi problem procesowy: agent wystawił jedną brakującą rolę fabuły 18,
chociaż już z analizy wynikało, że potrzebne będą następne wpisy. Właściciel
nie powinien przechodzić przez przewidywalne potrzeby tej samej fabuły ratami.

## Decyzja

1. **Tryb wzrostu:** dopóki każda z czterech baz nie ma co najmniej 10
   wpisów, każda nowa fabuła dostaje nowe tło, hero, kodę i instrument.
   Nawet semantycznie pasujący istniejący klocek nie jest wtedy automatycznym
   wyborem — priorytetem jest poszerzanie bazy.
2. **Tryb dojrzały:** po osiągnięciu 10 wpisów w każdej kategorii reuse jest
   dozwolony, ale żaden klocek nie może występować w ponad 10% produkcji.
   Limit dyskretny to `max(1, floor(0.10 × liczba_receptur))`.
3. Zamrożonych sygnatur 1, 2, 3, 4, 5 i 8 nie przebudowujemy retroaktywnie.
   Ich użycia liczą się jednak do przyszłego limitu.
4. Polityka jest maszynowa: `data/usage-policy.json`, walidacja w
   `library_tool.py check`, pełny rozkład w `library_tool.py report`.
5. Agent wyprowadza komplet czterech ról przed pozyskiwaniem. Jedna bramka
   zawiera jednocześnie wszystkie wpisy potrzebne danej fabule, po minimum
   trzy warianty każdego wpisu.

## Konsekwencje

- Najbliższe produkcje — do osiągnięcia 10 wpisów w każdej kategorii — będą
  zwykle wymagać czterech werdyktów w jednej bramce i będą droższe źródłowo,
  ale baza będzie rosła równomiernie.
- Matematyczna różnorodność staje się twardym QA, nie deklaracją w raporcie.
- Dopiero dojrzała baza zacznie realizować korzyść kombinatoryczną a×b×c×d;
  wcześniej ważniejsza jest szerokość słownika brzmień.
