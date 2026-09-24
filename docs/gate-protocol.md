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
   bazę (d/c/a/b). Najpierw zapisuje profil semantyczny fabuły (ADR 0006:
   cztery warstwy z narracji, bez zaglądania do baz), potem dopasowuje bazy;
   brak klasy = wpis do bramki. **Wszystkie braki jednej fabuły trafiają do
   jednej bramki jednocześnie**; nie wolno wystawić hero, a dopiero po jego
   wyborze ujawnić kolejnej potrzeby tła, kody lub instrumentu.
2. Dla KAŻDEGO wpisu: co najmniej **3 kandydaci dopasowani do tej roli**
   (3 jeziora, 3 nury, 3 pianina — NIE „kotły vs kieliszki vs harfa" jako
   konkurenci jednego wpisu; dla głosów: 3 RYKI tej samej bestii = rekordy/
   przeróbki jednego rodzaju źródła, NIE 3 różne gatunki — korekta g002);
   audycja `stem_probe.py` obowiązkowa i **sonda słyszalności każdego
   kandydata** (RMS/peak w oknie — żadnego „pustego dźwięku"); kody (a)
   renderuj na neutralnym instrumencie, instrumenty (b) na frazie
   demonstracyjnej W ICH REALNYM ZAKRESIE.
2a. **Etykiety kandydatów unikalne w skali CAŁEJ bramki** (np. p.*, b.*,
   r.*, o.*, w.*, a.* — nie „d.* dla dwóch różnych wpisów"; kolizja w g002
   zmusiła właściciela do zgadywania kontekstu).
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

Pole `notes` w `verdicts.json` jest obowiązkowe przy „żaden” i przy wyborze
z zastrzeżeniem — przechowuje słowa właściciela, bo to jedyny zapis kierunku
naprawy dla następnej rundy (i dla następnej sesji).

### Runda naprawcza: czytaj, CO właściciel skrytykował

Werdykt „żaden” niesie diagnozę; dobierz remedium do jej rodzaju, zamiast
powtarzać tę samą robotę z innym plikiem:

| Słowa właściciela | Co jest zepsute | Remedium |
|---|---|---|
| „za wysoki”, „za cichy”, „za krótki” | parametr | **ta sama rodzina**, zmiana parametru (pitch-down, inne okno, dłuższy wycinek) |
| „brzmi jak kreskówka”, „to nie jest ryk”, „za czysty” | charakter źródła | **inna rodzina albo inna TECHNIKA** — patrz niżej |
| „dobre, ale utnij koniec/początek” | detal wykonania | popraw parametrem w skrypcie bramki (np. `end_sec`), nigdy ręczną edycją pliku |

**Technika bywa ważniejsza niż paczka.** Wrzask goblinów padł trzy razy
(g004 surowe gobliny, g005 te same o −6 półtonów, g006 inny kit stworów),
bo wszystkie źródła były wokalizacjami UDAWANYMI pod stwora — takie nagrania
robi się z uśmiechem i to słychać. Zadziałało dopiero odwrócenie metody, tak
jak robi to filmowe fantasy: **prawdziwy ludzki wrzask + pitch-down +
saturacja** (g007, przyjęty). Zanim otworzysz czwartą rundę z kolejną paczką,
zapytaj: czy zepsuty jest plik, czy sposób jego wytworzenia?

**Sito liczbowe zamiast zgadywania.** Metryki drukuj w skrypcie bramki —
trafiają wtedy do raportu w czacie i ułatwiają właścicielowi werdykt.

| Rola | Miara | Wartość „to brzmi jak…” |
|---|---|---|
| głos (hero) | udział pasma gardła 150–800 Hz | prawdziwy głos 41–66%, „głosik stwora” 4–22% (g007) |
| **woda** | ~~udział poniżej 1 kHz~~ — **miara obalona**, patrz niżej | prawdziwy strumień ma centroid 2836–3102 Hz i tylko 15–27% energii < 1 kHz (g011, przyjęty) |
| tło ogólnie | wahanie RMS w podoknach 0,5 s | stabilne łoże < ~2,5 dB |
| tło ogólnie | udział > 6 kHz | powyżej ~15% ucho słyszy syk/wiatr, nie materiał |

**Uwaga: sito „im niżej, tym bardziej woda” było błędne.** Trzy rundy
(g008–g010) strojono do progu > 65% energii poniżej 1 kHz. Przyjęte
w g011 nagranie terenowe ma **15–27%** i centroid ~3 kHz — czyli wartości,
które moje sito odrzucało jako „wiatr”. Prawdziwy strumień jest jasny;
o naturalności decyduje mikrostruktura (tysiące drobnych, nieregularnych
zdarzeń), której żadna z tych liczb nie mierzy. Wniosek: **dla teł żywiołów
metryki służą wyłącznie do odsiewania wad technicznych** (rumble < 8%,
brak mowy: modulacja obwiedni < 0,25, stabilność okna), a nie do oceny
„czy to brzmi jak woda”. Tę ocenę robi ucho właściciela w bramce.

**Żywioł rozpoznajemy po zdarzeniach, nie po nazwie pliku.** Nagranie
podpisane „hot spring” było w istocie sykiem pary: szerokie pasmo, centroid
2100–2700 Hz, zero tranzjentów — właściciel usłyszał wiatr. Woda brzmi jak
woda, gdy ma masę poniżej 1 kHz (rezonans pęcherzyków i wnęki) i policzalne
chlupnięcia. Analogicznie ogień potrzebuje trzasków, a deszcz gęstych
mikrouderzeń. Zanim wytniesz okno, policz zdarzenia.

### Poprawka wykonawcza po akceptacji

Właściciel może przyjąć kandydata z uwagą („dobry, ale utnij koniec”).
Wtedy: (1) znajdź miejsce liczbowo — profil energii co 50 ms, tnij w
MINIMUM przed artefaktem (g007: −25 dB przy 1,25 s, po czym głos wracał na
−16 dB pnąc się 558→733 Hz); (2) wprowadź cięcie jako **parametr skryptu
bramki**, żeby kandydat dawał się odtworzyć z kodu; (3) przebuduj bramkę,
zapisz uwagę w `verdicts.json::notes` i dopiero wtedy `accept`.

### Faza B: obsada fabuły + montaż (bez odsłuchu właściciela)

1. Agent czyta fabułę i definiuje **role** d / c / a / b (zakres: „tajemnicze
   jezioro", „krzyk dużego ptaka zwiadowczego", „koda groza", „grandpiano").
   Rola wynika z **narracji tej konkretnej fabuły** — nigdy „co jest wolne
   w bazie".
2. Jeśli rola jest obsadzona wpisem baz — używa go; jeśli nie, to faza A
   dla brakującej roli (rola przed plikiem). „Obsadzona" znaczy **pasująca
   do narracji**: wpis o ogólnej roli („ptak"), który nie pasuje do
   fabuły („gobliny Jundu" ≠ „kruk"), NIE jest obsadą — to brak → bramka
   (korekta po fabułach 5/8: nur z fabuły 4 do fabuły o portalu i kruk
   z fabuły 1 do goblinów = podstawianie inwentarza, wycofane).
2a. **Hero = tożsamość fabuły**: powtórzenie hero między fabułami grozi
   kopią („fabuła 8 = fabuła 1 z innym tłem"), więc resolver karze je
   najmocniej ze wszystkich powtórek — ale twardy (ADR 0006) jest tylko
   zakaz identycznej kombinacji czterech klocków. Tło/gest/instrument
   mogą się powtarzać swobodnie (ekonomia wariacji).
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
- Fabuł sygnaturowych właściciel nie pilotuje: nie prosimy o odsłuch ani
  o casting, błędy montażu łapią bramki maszynowe. Właściciel **może** rzucić
  krótką uwagę po fakcie („fabuła 8 fajna”, „czar brzmi jak koda”) — wtedy
  zamień ją w REGUŁĘ (zapis w `recipes/<id>.json::notes` + LESSONS), a nie
  w rundę remiksów na życzenie. Uwaga o brakującym charakterze roli
  („co mają kruki do Jundu”) oznacza nową bramkę, nie podmianę pliku.
- **Weryfikuj reklamację, zanim coś zmienisz.** Przy „gra stara wersja”
  najpierw `md5sum` pliku na dysku kontra to, co zwraca serwer, i analiza
  treści (np. pik widma hero) — raz przyczyną był wyłącznie cache
  przeglądarki, a montaż był poprawny. Patrz LESSONS 2026-09-23.
