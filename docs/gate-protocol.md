# Protokół bramki odsłuchowej

Jedyny moment, w którym potrzebne jest ludzkie ucho. Odbywa się **wewnątrz
sesji agenta**, w sandboxie — nie na Pages (Pages to gablotka, nie narzędzie
decyzji; fuzja PR zamyka sesję, więc bramka musi mieć się przed nią).

## Przebieg dla agenta

1. Wybierz fabułę (losowo albo zleconą). Przeczytaj ją i zdefiniuj **role
   semantyczne** każdego klocka: miejsce (d), jedno główne zdarzenie (c),
   emocję muzycznej odpowiedzi (a) i charakter brzmienia (b).
2. **Sprawdź bazy** (`data/library/*.json`): jeśli rola jest obsadzona —
   użyj wpisu. Bramka dotyczy tylko braków.
3. Dla każdego braku zgromadź **co najmniej 3 kandydatów** (audycja
   `stem_probe.py` obowiązkowa; kody (a) renderuj na neutralnym instrumencie
   referencyjnym, instrumenty (b) pokaż na krótkiej frazie demonstracyjnej).
4. Zbuduj manifest bramki w `work/gates/gNNN/` (numeracja rosnąca): kandydaci,
   opisy, licencje, propozycje wpisów `entry` do baz.
5. Wygeneruj stronę: `python scripts/gate_preview.py work/gates/gNNN --port 8080`
   (preview sandboxa) i podaj użytkownikowi link w czacie.
6. Odpowiedź właściciela zapisz jako `work/gates/gNNN/verdicts.json` i wykonaj
   `python scripts/library_tool.py accept --gate gNNN` — skrypt przenosi
   zaakceptowane pliki do `audio/library/`, dopisuje wpisy z pieczątką
   `approved` i archiwizuje manifest w `data/gates/gNNN.json`.
7. Ułóż recepturę `data/recipes/<id>.json` z zatwierdzonych klocków,
   wyrenderuj `python scripts/render_signature.py data/recipes/<id>.json --audit`,
   dołóż wynik QA do raportu i commituj.

## Format odpowiedzi właściciela (w czacie)

```text
fabuła 1: d.1 c.2 a.1 b.2  ·  fabuła 4: d.1 c.1 a.2 b.3
```

`d.żaden` odrzuca wszystkich kandydatów slotu; po „żaden" warto dopisać jedno
słowo dlaczego (`za cichy`, `zły klimat`) — druga runda kandydatów będzie trafniejsza.
Werdykt `verdicts.json`:

```json
{"1": {"d": "d.1", "c": "c.2", "a": "a.1", "b": "b.2"}, "4": {"d": "d.żaden"}}
```

## Zasady

- Bramkę zawsze podajemy **zbiorczo** (wszystkie fabuły sesji na jednej stronie),
  minimalizując rundy odsłuchu.
- Kandydaci odrzuceni nie wchodzą do git (pozostają w `work/gates/`).
- Nie dopisujemy nowej roli do bazy, jeśli istniejąca rola pokrywa potrzebę
  (rola przed plikiem — patrz `docs/signature-system.md`).
- Zatwierdzony klocek jest zatwierdzony na zawsze; „usunięcie z bazy" tylko
  na wyraźne żądanie właściciela i z adnotacją w LESSONS.
- Zaakceptowane gesty i instrumenty można używać w dowolnej fabule —
  unikalność dotyczy kombinacji a·b·c·d całej receptury, nie pojedynczych klocków.
