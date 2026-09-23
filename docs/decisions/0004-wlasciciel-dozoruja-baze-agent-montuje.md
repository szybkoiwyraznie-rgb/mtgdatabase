# ADR 0004: Właściciel dozoruje bazę, agent obsadza role i montuje

- Status: accepted (wersja uzupełniona 2026-09-23, korekta zgłoszona przez
  właściciela tego samego dnia po pierwotnej publikacji; nadpisuje punkty
  2 i 5 ADR 0003)
- Data: 2026-09-23

## Kontekst

Po pierwszej bramce (g001) i dwóch sygnaturach właściciel skorygował proces:

1. „Ja mogę akceptować jakość propozycji klocków, ale nie będę oceniać
   fabuł — one muszą być budowane samodzielnie bez mojego sprawdzania."
2. „Kody muszą być zawsze słyszalne i nie ja to będę oceniał."
3. „Nie ja mam dobierać klocki do karty tylko. Ja mam akceptować wpisy do
   bazy, a wybór tego czy tamtego robisz ty."
4. „Bramka podaje 3 kandydatów do konkretnego wpisu do bazy, np. 3 jeziora,
   3 nury, 3 grandpiano. I ja wybieram jednego i jeden trafia do bazy."

## Decyzja

1. **Bramka = dozór przyjęć do bazy, jeden kandydat na wpis.** Bramka
   prezentuje dla każdego potrzebnego WPISU bazy co najmniej 3 kandydatów
   dopasowanych do JEDNEJ roli („3 jeziora" do wpisu „jezioro", „3 nury" do
   wpisu „nurek", „3 grandpiana"). Właściciel wybiera **dokładnie jednego**
   (albo „żaden" z jednym słowem dlaczego). Tylko wybrany kandydat trafia
   do bazy; pozostali zostają w archiwum bramki. NIGDY „wszystkie dobre
   trafiają" — to był błąd pierwotnej wersji ADR („doktryna-jakości"),
   wycofany natychmiast po korekcie; baza wróciła do 8 wpisów werdyktowych
   z g001.
2. **Agent obsadza fabułę samodzielnie.** Agent definiuje cztery role fabuły
   (np. „tajemnicze jezioro + krzyk nurka + koda groza + grandpiano"), dobiera
   konkretne wpisy z bazy i podpisuje decyzję w recepturze/commit.
3. **Montaż ma twarde gwarancje maszynowe — bez odsłuchu właściciela.**
   Render odrzuca mix, w którym cokolwiek zniknęło:
   - każda nuta kodu musi dać mierzalny atak w finalnym mixie
     (`note_attack_margin_db = 2,5 dB` w oknie ataku 0,3 s wobec kontekstu);
   - żadna nuta z gestu nie może być pominięta przez adaptację rejestru
     (licznik nut: zagrane == w gescie);
   - **autokalibracja**: render sam dobija maskowane nuty o brakujący
     margin (+0,5 dB zapasu, sufit 8 dB, ≤6 iteracji); gdy sufit nie
     wystarcza, geometria hero/koda zgłasza się jako niewykonalna i trzeba
     zmienić układ czasowy — wszystko logowane w audycie.
4. **Odrzuci kandydaci z bramek zostają w archiwum bramki** (trwałość po
   resetach sandboksa), ale do baz i gry nigdy.
5. **Długość referencyjna sygnatury: 6,0 s** (werdykt właściciela przy
   pierwszych dwóch fabułach).

## Nauka techniczna (nie zgadywać — mierzyć)

- Moje „naprawione" wersje bez bramki nadal zawodziły: pomiar pokazał ataki
  kotłów +0,8 dB i kieliszków −3,3/−4,6 dB vs próg 2,5 dB.
- Poziom całego bloku nie leczy nakładających się wybrzmień (skala wspólna
  kontekstu i ataku) — leki: minimum brzmienia 1,2 s, semantyka „poziom
  per nuta", autokalibracja per nuta i geometria montażu (fabuła 4: hero na
  0,7 s, koda na 3,6 s).
- Demo gestu na fortepianie nie pokazuje ryzyka parowania z instrumentem o
  wolnym ataku (kieliszki) — potwierdzono produkcyjnie.
