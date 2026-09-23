# Protokół bramki odsłuchowej (model z ADR 0004)

Jedyny moment z ludzkim uchem. Jednak **nie jest to casting fabuły** —
właściciel dozoruje JAKOŚĆ wpisów przechodzących do bazy, a obsadę fabuł
i montaż bierze na siebie agent z twardymi bramkami QA. Odbywa się
**wewnątrz sesji agenta**, w sandboxie — nie na Pages (gablota, nie narzędzie
decyzji; fuzja PR zamyka sesję).

## Dwie fazy pracy agenta

### Faza A: bramka = przyjęcia do bazy (raz na kandydaturę roli)

1. Właściciel lub agent definiuje brak semantyczny („brakuje nam jeziora"),
   ale kandydaci to **warianty JEDNEJ roli**, nigdy „kotły vs kieliszki vs
   harfa" jako konkurenci jednego slotu.
2. Co najmniej 3 warianty na rolę; audycja `stem_probe.py` obowiązkowa;
   kody (a) renderuj na neutralnym instrumencie, instrumenty (b) na frazie
   demonstracyjnej W ICH REALNYM ZAKRESIE.
3. Bramka w `data/gates/gNNN/`: manifest + kandydaci + opisy + licencje,
   **commitowana od razu** (ochrona przed resetami sandboksa).
4. Strona: `python scripts/gate_preview.py data/gates/gNNN --port 8080`,
   link w czacie.
5. Werdykt właściciela = **lista akceptacji**, może być „wszystkie dobre";
   po odrzucie jedno słowo („za cichy", „zły klimat"). Zapisz jako
   `verdicts.json`, wykonaj:
   `python scripts/library_tool.py accept --gate gNNN` — skrypt przenosi
   pliki do `audio/library/` i dopisuje wpisy z pieczątką `approved`.
   Niezaakceptowane warianty zostają tylko w archiwum bramki.

Format werdyktu (listowy):

```json
{"jezioro": ["j.1", "j.3"], "krzyki-nurka": "wszystkie", "groza-koda": ["g.1"], "grandpiano": "żaden — za sztuczny"}
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
