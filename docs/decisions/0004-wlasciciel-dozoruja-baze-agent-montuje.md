# ADR 0004: Właściciel dozoruje bazę, agent obsadza role i montuje

- Status: accepted (nadpisuje punkty 2 i 5 ADR 0003)
- Data: 2026-09-23

## Kontekst

Po pierwszej bramce (g001) i dwóch sygnaturach właściciel skorygował proces:

1. „Ja mogę akceptować jakość propozycji klocków, ale nie będę oceniać fabuł —
   one muszą być budowane samodzielnie bez mojego sprawdzania."
2. „Kody muszą być zawsze słyszalne i nie ja to będę oceniał."
3. „Nie ja mam dobierać klocki do karty. Ja mam akceptować wpisy do bazy,
   a wybór tego czy tamtego robisz ty."
4. „Nie dawaj 3 zupełnie różnych instrumentów [jako konkurentów] — każdy
   jest ok i wszystkie powinny trafić do bazy."

## Decyzja

1. **Bramka = dozór przyjęć do bazy, nie casting fabuły.** Kandydaci
   prezentowani jako **warianty jednej, wąskiej roli semantycznej**
   („3 jeziora", „3 krzyki nurka", „koda groza × 3", „3 grandpiana").
   Akceptacja jest wielowariantowa; odrzuca się tylko wadliwą jakość
   (z krótkim powodem). Nic z „wybierz 1 z 3".
2. **Agent obsadza fabułę samodzielnie.** Agent definiuje cztery role
   fabuły (np. „tajemnicze jezioro + krzyk nurka + koda groza + grandpiano"),
   dobiera konkretne wpisy z bazy i podpisuje decyzję w recepturze/commit.
3. **Montaż ma twarde gwarancje maszynowe — bez odsłuchu właściciela.**
   Render odrzuca mix, w którym cokolwiek zniknęło:
   - każda nuta kodu musi dać mierzalny atak w finalnym mixie
     (`note_attack_margin_db = 2,5 dB` w oknie ataku 0,3 s wobec kontekstu);
   - żadna nuta z gestu nie może być pominięta przez adaptację rejestru
     (licznik nut: zagrane == w gescie);
   - **autokalibracja**: render sam dobija maskowane nuty o brakujący
     margin (+0,5 dB zapasu, sufit 8 dB, ≤6 iteracji); gdy sufit nie
     wystarcza, para gest×instrument w tym układzie czasowym zgłasza
     się jako niewykonalna i trzeba zmienić geometrię montażu (moment
     hero/kody) — wszystko logowane w audycie.
4. **Odrzuci kandydaci z bramek zostają w archiwum bramki** (już
   od chęci trwałości z sesji reset-sandbox), ale do baz i gry nigdy.
5. **Długość referencyjna sygnatury: 6,0 s** (werdykt właściciela
   przy pierwszych dwóch fabułach).

## Konsekwencje dla g001 (retroakcja)

Werdykty z g001 określały wybory slotów dwóch fabuł, ale żaden kandydat
nie został odrzucony za jakość — właściciel jednoznacznie wskazał, że
dobre warianty mają trafiać do bazy. W związku z tym do baz dowożone są
również pozostałe, usłyszane i zaakceptowane jakościowo klocki g001
(pieczątka `choice: "doktryna-jakości"`), zachowując werdykty fabuł 1 i 4
jako obowiązujące receptury.

## Nauka techniczna (nie zgadywać — mierzyć)

- Moje „naprawione" wersje bez bramki nadal zawodziły: pomiar pokazał
  ataki kotłów +0,8 dB i kieliszków −3,3/−4,6 dB vs próg 2,5 dB.
- Poziom całego bloku nie leczy nakładających się ringtonów (skala
  wspólna kontekstu i ataku) — leki były: minimum brzmienia 1,2 s już
  wcześniej, sięgnięcie po semantykę „poziom per nuta", autokalibracja
  per nuta i geometria (hero wcześniej, koda po jego fade-out).
- Demo gestu na fortepianie nie pokazuje ryzyka parowania z instrumentem
  o wolnym ataku (kieliszki) — wpisy baz b niosą od teraz charakter
  ataku w metadanych, a gate codowy jest ostatecznym strażnikiem.
