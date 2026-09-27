# Audyt taksonomii v4 (na zlecenie właściciela, 2026-09-24)

**Pytanie:** czy „śmiech" był wyjątkiem, czy wierzchołkiem góry lodowej?
**Odpowiedź:** górą lodową. Poniżej pełna inwentaryzacja.

**Kryterium audytu (model 1:1):** czy JEDEN konkretny klocek audio może
uczciwie zagrać daną warstwę każdej fabuły przypisanej do typu. Flagi
niejednorodności: tożsamość źródła (płeć/wiek głosu, gatunek, pojedynczy
vs tłum), materiał (drewno/kamień/metal/szkło), skala (drobne vs
kolosalne), charakter (nagłe vs ciągłe), pora (dzień vs noc).

**Rozróżnienie dwóch chorób:**
- **(A) typ źle zaprojektowany** — fabuły w typie mają niepogodzalne
  źródła dźwięku → trzeba ROZBIĆ (nowe typy);
- **(B) szum przypisań** — typ zdrowy, ale zachłanne wzorce wciągnęły
  cudze fabuły → trzeba POPRAWIĆ PRZYPISANIA (bez zmian taksonomii).

---

## HERO (59 typów) — 10 typów do rozbicia, 6 do obserwacji, reszta spójna

### A. DO ROZBICIA (propozycje nowych typów)

| Typ dziś | Problem | Propozycja |
|---|---|---|
| `ryk-bestii` (13) | ryk zwierzęcia vs gardłowy ryk człowieka/orka (22, 39, 177, 534); do tego 58 = **ryk silnika** (maszyna!) | + `ryk-humanoida`; 58 → `loskot-machiny` |
| `skrzek-wrzask` (11) | pojedynczy skrzek harpii/bruxy vs **masowy pisk tysięcy gryzoni** (535, 540); 8 (wrzask watahy goblinów) to gotowy przypadek `wrzask-bandy` | + `pisk-gryzoni`; 8 → `wrzask-bandy` |
| `jek-zawodzenie` (10) | ludzki szloch (355) vs **wycie wilka** (37; pokrewny skowyt 24 siedzi w skrzeku) | + `wycie-wilcze` |
| `lopot-skrzydel` (9) | trzepot skrzydełek wróżki/owada (86, 114, 35) vs łopot skrzydeł smoka/roka (547, 563) — skala nie do pogodzenia | + `trzepot-drobnych-skrzydel` |
| `strzal-pocisk` (11) | cięciwa łuku (304, 583, 267) vs **machina oblężnicza** (321, 504, 505) vs salwa głazów (265) | + `strzal-z-luku`, + `machina-miotajaca` |
| `piesn-chor` (9) | śpiew solowy kobiecy (510, 251) vs mówiona przemowa/pakt (520, 532, 335) vs chór wielu głosów (207, 231) vs samogrające struny (195 — instrument, nie głos!) | + `spiew-zenski`, + `przemowa-glos`, + `chor-glosow`; 195 → `rezonans-magiczny` |
| `okrzyk-bojowy` (12) | **płeć głosu** — jak przy śmiechu: kapłanka/taktyczka/weteranka/przewodniczka (94, 219, 442, 516) vs dowódca/kapitan/szeryf (129, 593, 598) | rozbić na `okrzyk-bojowy-meski` i `okrzyk-bojowy-zenski` |
| `chrobot-szelest` (28) | worek bez dna: grzechot kości (248, 447, 312) vs skrobanie pióra/rylca (360, 537, 306) vs brzęk kluczy/monet/wytrychów (229, 101, 284, 388) vs szuranie ziemi/przeszukiwanie (reszta) | + `grzechot-kosci`, + `skrobanie-pisma`, + `brzek-drobiazgow`; rdzeń zostaje |
| `rozblysk-swiatla` (38!) | największy zlepek: łagodna narastająca aura uzdrowienia (13, 29, 110, 240, 453…) vs gwałtowny oślepiający błysk (43, 282, 422, 524…) vs zatrzask świetlistych więzów (25, 45, 181) | + `aura-lagodna`, + `wiezy-swiatla`; `rozblysk-swiatla` zostaje = gwałtowny błysk |
| `pelzanie-sluz` (10) | mokre pełznięcie (40, 303, 506) vs **ciężki oddech cielska** (180, 234, 296) | + `oddech-cielska` |

Nowych typów hero: **14** (59 → 73; nadal w widełkach 40–80).

### B. SZUM PRZYPISAŃ (typ zdrowy, fabuły do przeniesienia ręcznie)

~45 fabuł, m.in.: 58 (ryk silnika→łoskot), 562 (błyskawica→trzask-blyskawicy),
163 (rezonans dzwonu→dzwon-gong), 34 (erupcja→wybuch), 32/121 (fale→fala-rozbryzg),
455 (czołg→loskot-machiny), 71/577 (bariera→bariera-odbicie), 262 (trąbka→rog-sygnal),
444 (świst lotu→swist-lotu), 445 (rumak→tetent-kopyt), 550 (zamarzanie→trzask-lodu),
527 (lodowiec→trzask-lodu), 592 (relikwiarz→rozbicie-szkla), 69 (rysiki→skrobanie-pisma),
403 (syk gazu→bulgot-syk), 386 (mlaskanie→chrzest-pozerania), 36 (zgrzyt→zgrzyt-metalu),
72/188 (pomruk energii→rezonans), 238 (walec→loskot-machiny), 97 (słup iskier→wybuch),
68 (kroki w śniegu), 117 (skrzyp sznurów), 522 (więzy światła), 173 (ryk szamana→ryk-humanoida),
24 (skowyt→wycie-wilcze), 8 (wataha→wrzask-bandy), 535/540 (→pisk-gryzoni) itd.
Pełna korekta = ręczny przegląd flagowanych fabuł przy wdrożeniu v5.

### C. OBSERWOWAĆ (rozbić dopiero, gdy pierwszy klocek ujawni konflikt)

`potezny-cios` (28 — po odsianiu szumu rdzeń „pojedyncze ciężkie uderzenie"
jest spójny), `kroki-kolosa` (kroki z metalu vs z mięsa: 189, 204),
`zwinny-skok`, `marsz-oddzialu` (374 kapela marszowa!), `brzeczenie-roju`
(rój owadów vs buczenie konstrukcji: 150, 213, 568), `skradanie-cisza`.

---

## TŁA (30 typów) — 2 rozbicia, duży szum w 4 typach

| Typ | Problem | Propozycja |
|---|---|---|
| `miasto-gwar` (30) | średniowieczny targ vs **neonowa metropolia z elektrycznym buczeniem** (58, 71, 105, 14) — inna epoka = inne spektrum | + `miasto-neonowe` |
| `oboz-wojenny` (32) | wzorzec „dziedzin-" wciągnął **ciche dziedzińce** katedr/klasztorów/kampusów (40, 46, 70, 231, 274) — zero wojska w tle | + `dziedziniec-spokojny` |
| `las-dzienny` (67) | głównie szum: mroczne/mgliste/skażone lasy (31, 54, 62, 73, 83) → `las-mroczny`; nocna dolina (125) → `noc-ksiezyc` | korekta przypisań |
| `gory-wichry` (34) | przestworza (64, 132) → `niebo-przestworza`; śnieżne (68, 173) → `kraina-lodu`; skarbiec (284) → `dwor-komnaty` | korekta przypisań |

Nowych typów tła: **2** (30 → 32).

## NASTRÓJ (20) i INSTRUMENTACJA (18) — SPÓJNE

Te warstwy opisują emocję kody i charakter palety — abstrakcje bez
tożsamości źródła (nie mają płci, gatunku ani materiału). Jeden gest
„czujności" i jedna paleta „mroczna" mogą uczciwie obsłużyć wszystkie
swoje fabuły — dokładnie na tym polega modularność. Bez zmian.

---

## Wnioski

1. Wzorzec „śmiechu" (tożsamość źródła) powtarza się w ~1/6 typów hero
   i 2 typach tła. Po rozbiciach: hero 73, tła 32 — nadal w widełkach.
2. Druga, osobna choroba to szum przypisań (~50–60 fabuł) — wynik
   zachłannych wzorców regex; taksonomii nie psuje, ale zafałszowuje
   liczniki i przyszłe obsady. Wymaga ręcznej korekty przy wdrożeniu.
3. Warstwy nastroju i instrumentacji nie mają tej klasy problemu.
4. Sześć typów na liście obserwacyjnej — decyzja odroczona świadomie,
   do pierwszego klocka.

**Status:** czeka na akceptację właściciela (bramka tekstowa).
Po akceptacji: taksonomia v5 + ręczna korekta przypisań + retag klocków
(np. `warband_cry_03` ma już typ `wrzask-bandy` — bez zmian).
