# Protokół bramki odsłuchowej (model z ADR 0004)

Jedyny moment z ludzkim uchem. Jednak **nie jest to casting fabuły** —
właściciel dozoruje JAKOŚĆ wpisów przechodzących do bazy, a obsadę fabuł
i montaż bierze na siebie agent z twardymi bramkami QA. Odbywa się
**wewnątrz sesji agenta**, w sandboxie — nie na Pages (gablota, nie narzędzie
decyzji; fuzja PR zamyka sesję).

## Dwie fazy pracy agenta

### Faza A: bramka = przyjęcia do bazy (jeden kandydat na wpis)

1. Agent definiuje potrzebne **wpisy** do baz („jezioro", „nurek-wail",
   „groza-koda", „grandpiano") — każdy wpis ma rolę semantyczną i docelową
   bazę (d/c/a/b).
2. Dla KAŻDEGO wpisu: co najmniej **3 kandydaci dopasowani do tej roli**
   (3 jeziora, 3 nury, 3 pianina — NIE „kotły vs kieliszki vs harfa" jako
   konkurenci jednego wpisu); audycja `stem_probe.py` obowiązkowa; kody (a)
   renderuj na neutralnym instrumencie, instrumenty (b) na frazie
   demonstracyjnej W ICH REALNYM ZAKRESIE.
3. Bramka w `data/gates/gNNN/`: manifest (`entries` = wpisy z kandydatami)
   + kandydaci + opisy + licencje, **commitowana od razu** (ochrona przed
   resetami sandboksa).
4. Strona: `python scripts/gate_preview.py data/gates/gNNN --port 8080`,
   link w czacie.
5. Werdykt właściciela = **jeden kandydat na wpis** albo „żaden" z jednym
   słowem dlaczego. Zapisz jako `verdicts.json` i wykonaj:
   `python scripts/library_tool.py accept --gate gNNN` — do bazy trafia
   DOKŁADNIE wybrany; pozostali zostają wyłącznie w archiwum bramki
   (mogą wrócić jako kandydaci innej roli w innej bramce).

Format werdyktu (jeden na wpis):

```json
{"jezioro": "j.2", "nurek-wail": "n.1", "groza-koda": "g.żaden — za słaby", "grandpiano": "p.3"}
```

### Faza B: obsada fabuły + montaż (bez odsłuchu właściciela)

1. Agent czyta fabułę i definiuje **role** d / c / a / b (zakres: „tajemnicze
   jezioro", „krzyk dużego ptaka zwiadowczego", „koda groza", „grandpiano").
2. Jeśli rola jest obsadzona wpisem baz — używa go; jeśli nie, to faza A
   dla brakującej roli (rola przed plikiem).
3. Agent układa recepturę `data/recipes/<id>.json` i renderuje:
   `python scripts/render_signature.py data/recipes/<id>.json --audit`.
   Twardy render (patrz `docs/signature-system.md` § Render i QA) gwarantuje:
   - każda nuta kodu słyszalna: atak ≥ kontekst + **2,5 dB** (okno 0,3 s),
   - żadna nuta nie ginie przy adaptacji rejestru (zagrane == w gescie),
   - **autokalibracja**: maskowane nuty dobijane automatycznie (+0,5 dB
     zapasu, sufit 8 dB); nasycone boosty = geometria niewykonalna →
     agent zmienia układ hero/kody (jak fabuła 4: hero na 0,7 s, koda na 3,6 s),
   - długość pliku równa `length_sec` receptury (referencja: **6,0 s**).
4. Raport w czacie = liczby z audytu (wszystkie `!` z renderu), nie prośba
   o odsłuch.

## Zasady

- Bramkę podajemy **zbiorczo** (wszystkie role sesji na jednej stronie),
  minimalizując rundy.
- Zatwierdzony klocek jest zatwierdzony na zawsze; „usunięcie z bazy" tylko
  na wyraźne żądanie właściciela i z adnotacją w LESSONS.
- Zaakceptowane klocki można używać w dowolnej fabule — unikalność dotyczy
  kombinacji a·b·c·d całej receptury, nie pojedynczych klocków.
- Fabuł sygnaturowych właściciel nie pilotuje; szczegółowy werdykt odsłuchowy
  montażu jest NIE pożądany — błędy montażu łapią bramki maszynowe, a ewentualne
  uwagi estetyczne idą w reguły (nowe gesty/instrumenty przez bramkę), nie w
  remiksy na życzenie.
