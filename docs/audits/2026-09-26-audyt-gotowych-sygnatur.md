# Audyt semantyczny gotowych sygnatur — 2026-09-26

Powód: właściciel zapytał „skąd w fabule 206 marsz wojsk?” po wykryciu,
że `High Stride` dostało hero `troop_march_05` (`marsz-oddzialu`), mimo że
narracja opisuje **jednego królika na drewnianych szczudłach**.

## Metoda

Dla każdej gotowej sygnatury sprawdzono:

1. narrację z `data/catalog.json`,
2. profil surowy z `data/semantics/story-profiles.json`,
3. klasy z `data/semantics/story-classes.json`,
4. faktyczne klocki z `data/recipes/*.json` i opisy `data/library/*.json`,
5. czy obsada jest „co słychać”, czy tylko wynika z wygodnego słowa-klucza
   albo najbliższego istniejącego klocka.

## Wynik: wycofane z gotowych

Te sygnatury zostały usunięte z `data/recipes/` i `audio/signatures/`, bo
naruszały tę samą regułę co 206: istniejący klocek był naciągnięty na scenę,
zamiast oznaczyć brak i zrobić bramkę.

| ID | Tytuł | Problem | Korekta klasy / brak |
|---:|---|---|---|
| 90 | Tranquil Cove | `sea_storm_02` to ciężkie, sztormowe wybrzeże pod nocnym klifem, a fabuła mówi o osłoniętej, spokojnej zatoce i delikatnych falach. Stara notatka w recepcie przyznawała: „tu bez sztormu narracyjnie, ale jedyny klocek typu” — to dokładnie niedozwolone podstawienie inwentarza. | `background: zatoka-spokojna` jako typ pending, brak klocka → przyszła bramka tła. |
| 206 | High Stride | `troop_march_05` to cztery warstwy kroków po żwirze „jak w plutonie”; narracja to pojedynczy królik na drewnianych szczudłach. Słowo „marsz” w profilu błędnie wygrało z akustyką i liczebnością. | `hero: stukot-szczudel` jako typ pending, brak klocka → przyszła bramka hero. |
| 268 | Might of the Masses | `wave_crash_03` jest wodnym rozbryzgiem; fabuła mówi o napływie szmaragdowej aury i rośnięciu trolla od wspólnej energii. Słowo „fale” zostało potraktowane dosłownie wodnie. | `hero: aura-lagodna` (istniejący typ bez klocka), brak klocka → przyszła bramka hero. |
| 599 | Candlegrove Witch | `forest_day_01` ma poranny/dzienny chór ptaków i `bad_for: noc`; fabuła to zamglony prastary las w noc równonocy, świece, mrok i upiory. | `background: las-mroczny` (istniejący typ bez klocka), brak klocka → przyszła bramka tła. |

## Zostają gotowe — sprawdzone bez blokera

| ID | Werdykt audytu |
|---:|---|
| 1 | Legacy; kruk jako hero pasuje, grzmot/timpani budują groźne urwisko i armię. Nie jest przypadkiem „marszu wojsk znikąd”. |
| 2 | Legacy; Baloth w narracji uzasadnia bestialny hero, tło wody pasuje. Profil klas jest dokumentacyjny i nie odtwarza w pełni starej obsady. |
| 3 | Chochlik/śmiech i dopalająca się mapa/ogień pasują. Legacy, ale bez analogicznego naciągnięcia. |
| 4 | Jezioro nocą + zew ptaka wodnego / tajemnica; legacy, ale spójne akustycznie. |
| 5 | Portal/zaklęcie brzmi dziś jako `spell_cast_bolt_01`; g032 ma osobny typ `rezonans-magiczny`, ale obecna legacy-obsada nie jest takim samym błędem liczebności/żywiołu. Do naturalnej rewizji po domknięciu g032. |
| 8 | Goblinia szarża / wrzask bandy / ogień Jundu — spójne. |
| 18 | Pęd powietrza + odbicia od bariery + jasna czujność — spójne. |
| 23 | Leśny trop + magiczny rozbłysk śladu — spójne. |
| 28 | Sztormowe morze i wodny crash mieszczą się w scenie krakenowego trofeum na rozkołysanym statku. |
| 64 | Świetliste stopnie i duma wznoszenia — spójne. |
| 110 | Pole bitwy + anielski rozbłysk / łaska — spójne. |
| 126 | Leśna polana + trzepot ptaków karmionych z dłoni — spójne. |
| 133 | Hippokamp wynurzający się z wody — `fala-rozbryzg` pasuje dosłownie. |
| 166 | Wróżka-posłanniczka / bezszelestna obecność — `skradanie-cisza` mieści się w definicji cichej obecności, bez blokera. |
| 169 | Jawna warta na granicy lasu — `skradanie-cisza` jest tu użyte jako cisza/czuwanie, zgodnie z definicją typu. |
| 191 | Para/iskry miecza, wulkaniczny klif, metaliczne dzwony — spójne. |
| 193 | Węszenie ogara jest po korekcie v6 spójne. Tło grzmotu dla deszczowego brzegu jest słabsze niż dedykowany deszcz/rzeka-brzeg, ale nie tak jawnie sprzeczne jak 90/599; oznaczone do obserwacji przy przyszłym typie deszczowym. |
| 222 | Sztormowe wybrzeże + samotna czujna warta — spójne. |
| 225 | Leśna scena po walce + świetlista aureola ducha przodkini — spójne. |
| 249 | Komnata maga + niestabilny rozbłysk zaklęcia — spójne; problem tej receptury był techniczny HF, nie semantyczny. |
| 422 | Leśna zasadzka + kopuła światła gwiazd — spójne. |
| 433 | Nylea wyłaniająca się w boskim blasku + groza/majestat — spójne. |
| 437 | Pająk i napięcie sieci — `skradanie-cisza` jako ciche opuszczanie/zasadzka, bez blokera. |
| 451 | Ciche użycie wiatru i paraliżującej mgły przez skunksa; `skradanie-cisza` jest uproszczeniem, ale mieści się w cichej zasadzce. Do rozważenia przy przyszłym typie gaz/spray, bez natychmiastowego wycofania. |
| 468 | Ogłuszający ryk bestii — spójne. |
| 498 | Plusk zrzucanych tarcz i ciał za burtę — `fala-rozbryzg` pasuje dosłownie. |
| 506 | Bezgłośna pełzająca asymilacja czarnego oleju — `skradanie-cisza` jako cichy, napięty ruch; spójne. |
| 511 | Niewidzialny oryks przemyka przez zarośla — `skradanie-cisza` pasuje. |
| 519 | Smok w bezruchu / czatowanie / smużka gazu — `skradanie-cisza` jest napięciem i czatowaniem, nie ruchem oddziału; do ewentualnego doprecyzowania, ale bez blokera. |
| 562 | Błyskawica w bitwie — spójne. |
| 575 | `marsz-oddzialu` zostaje: narracja jest o oddanych wojownikach Dromoki, murze obronnym i kroku natarcia oddziału, więc to nie przypadek 206. |
| 577 | Bitwa + bariera Laski Gromu + monumentalna otucha — spójne. |
| 578 | Bestia w lesie kontratakuje z rykiem — spójne. |
| 585 | Pantery z rykiem skaczą ponad rzekę; więź z Jolrael — spójne. |

## Reguły po audycie

- Nie wolno mapować **pojedynczego kroku / szczudeł / chodu jednej postaci**
  na `marsz-oddzialu`, nawet jeśli profil zawiera słowo „marsz”.
- `fala-rozbryzg` oznacza wodę/plusk, nie metaforyczną falę magii lub aury.
- `las-dzienny` nie obsługuje nocy, mroku rytuału ani scen z `bad_for: noc`.
- `morze-wybrzeze` w obecnej bibliotece ma klocek sztormowy; spokojna zatoka
  wymaga osobnego typu/klocka, bo w modelu 1:1 typ nie może znaczyć naraz
  „sztormowy klif” i „osłonięta zatoka”.
