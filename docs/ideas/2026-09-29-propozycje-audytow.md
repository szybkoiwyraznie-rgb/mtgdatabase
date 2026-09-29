# Propozycje kolejnych audytów i poprawek (2026-09-29)

Rekonesans na korpusie 533 sampli. Każdy punkt ma dowód liczbowy, szacunek
pracy i koszt w kredytach ElevenLabs. Kolejność = moja rekomendacja.

Stan wyjściowy: baza jest strukturalnie czysta — 533 fabuły = 533 scenariusze
= 533 pliki MP3, zero sierot, zero rozjazdów deklarowanej długości, zero
duplikatów PCM, mediana −20,02 LUFS, σ 0,54 LU, max true peak −1,07 dBTP.

---

## P1. Zgodność mono — sample, które znikają na telefonie ✅ ZREALIZOWANE 2026-09-29

**Dowód:** po zsumowaniu kanałów do mono
- **181 traci 11,0 LU** (−20,0 → −31,0 LUFS) — na głośniku telefonu praktycznie znika,
- 52 pliki tracą ponad 2 LU, 96 plików ponad 1 LU,
- 10 plików ma **ujemną korelację L/R** (do −0,87), czyli kanały wzajemnie się znoszą.

Obecny audyt mierzy głośność wyłącznie w stereo, więc tego nie widać. Tymczasem
sample odsłuchuje się na laptopie, telefonie i w podglądzie — wszędzie tam
sumowanie do mono jest realne.

**Propozycja:** nowa metryka `mono_delta_lu` + flaga `mono_collapse` (> 2 LU
straty) w `audit_samples_full.py`, a do tego korekta mid/side w postprodukcji:
przyciszenie składowej bocznej tylko w plikach dotkniętych problemem, z
ponownym wyrównaniem do −20 LUFS. Praca: ~1 sesja. Koszt: **0 kredytów**.

---

## P2. Rozwiązanie 20 par bliźniaków brzmieniowych

**Dowód:** audyt od dawna raportuje 20 par o podobieństwie ≥ 0,95, np.
`321 balista` ~ `507 rozsadzenie golema` (0,973), `39 tupnięcie orka` ~
`142 taranowanie palisady` (0,969). Niektóre ID wracają w kilku parach
(`15`, `155`, `70`) — to znaczy, że mamy kilka „worków" bardzo podobnych
eksplozji i uderzeń. Reguła projektu mówi: każda fabuła ma własny, unikalny
sample.

**Propozycja dwuetapowa:**
1. **Za darmo** — różnicowanie postprodukcyjne (inny varispeed, tilt barwy,
   inna obwiednia, ewentualnie multiplikacja tam, gdzie fabuła pozwala).
   Sprawdzone: przy ostatniej multiplikacji liczba par spadła 23 → 20 sama z siebie.
2. **Za kredyty** — regeneracja słabszego z pary z bardziej konkretnym
   promptem (materiał + kontakt), ~29 kredytów za sztukę.

Sugeruję najpierw etap 1 na wszystkich 20 parach i dopiero potem decyzję,
które (jeśli w ogóle) regenerować.

---

## P3. Głośność odczuwalna dla transjentów, nie tylko LUFS zintegrowany

**Dowód:** rozrzut crest factor to 11,6–23,1 dB (mediana 17,3). Przy tym samym
−20 LUFS sample „szpilkowy" (jedno trzaśnięcie, 56 plików > 22 dB) brzmi
wyraźnie ciszej niż sample gęsty. LUFS zintegrowany z bramkowaniem na pliku
2,5-sekundowym premiuje materiał ciągły.

**Propozycja:** dołożyć do audytu **maksimum LUFS-S (3 s) / momentary** i
zestawić z wartością zintegrowaną. Tam, gdzie rozjazd jest duży, wyrównywać
do celu liczonego z krótkiego okna, a nie z całego pliku. Efekt: biblioteka
przestanie „skakać" przy odsłuchu jeden po drugim. Koszt: **0 kredytów**.

---

## P4. Balans pasma względem mediany korpusu

**Dowód (skan orientacyjny, liczony na początku pliku — do powtórzenia na całości):**
- **133 pliki** mają praktycznie zerową energię powyżej 10 kHz (głuche, bez „powietrza"),
- **71 plików** ma ponad 60 % energii poniżej 200 Hz (dominacja dudnienia —
  dokładnie klasa błędu opisana w `LESSONS.md`),
- **27 plików** wyróżnia się energią w paśmie 2–5 kHz (kandydaci na ostre/męczące).

Obecny audyt ma flagę `muffled`, ale łapie tylko 5 plików — próg jest zbyt
konserwatywny.

**Propozycja:** policzyć medianowy profil widmowy całego korpusu i flagować
odchylenia (`dull`, `boomy`, `harsh`), a następnie zastosować **delikatną
korektę** (półkowa góra / filtr dolnozaporowy / wąskie cięcie w 3 kHz) tylko
do wyraźnych odstających. Koszt: **0 kredytów**.

---

## P5. Audyt semantyczny „czy sample brzmi jak opis" ✅ ZREALIZOWANE

Największa dziura w kontroli jakości: wszystkie dotychczasowe metryki są
sygnałowe. Nikt nie weryfikuje maszynowo, czy `krakanie kruka` to naprawdę
krakanie, a nie szum.

**Propozycja (bez modeli zewnętrznych):** tablica oczekiwań słowo → podpis
akustyczny, np. `dzwon/gong` → wysoka tonalność i długie wybrzmienie,
`uderzenie/trzask` → ostry transjent i krótki ogon, `skrzydła` → modulacja
obwiedni 3–10 Hz, `syk/para` → szerokopasmowy szum bez wyraźnego f0,
`woda/plusk` → szum z szybkim zanikiem i rozproszonymi transjentami.
Niezgodność = pozycja na liście do odsłuchu. To zawęzi ręczny odsłuch z 533
plików do kilkunastu podejrzanych. Koszt: **0 kredytów**.

---

## P6. Dokończenie higieny czasu (kontynuacja multiplikacji)

**Dowód:** zostało 37 plików z długim ogonem ciszy, 14 z długim wstępem,
14 ze zbyt krótką treścią, 11 z twardym cięciem na starcie. Z pierwotnych
96 kandydatów obsłużyłem 21.

**Propozycja:** druga tura — multiplikacja tam, gdzie fabuła uzasadnia
powtórzenie, a zwykły trym/fade tam, gdzie nie. Koszt: **0 kredytów**.

---

## P7. Zabezpieczenie regresji w CI

**Dowód:** w tej sesji dwukrotnie zdarzyło się, że wskaźnik gałęzi cofał się
do commita bazowego, a pliki zostawały nowe — łatwo o niezauważone nadpisanie
(np. podwójna multiplikacja tego samego pliku).

**Propozycja:** snapshot metryk (ID → LUFS, true peak, długość, md5) w repo
plus krok w `validate.yml`, który porównuje bieżące pliki ze snapshotem i
wymaga świadomej aktualizacji przy każdej zmianie audio. Dodatkowo zapis
**commita bazowego** w manifeście każdej paczki, żeby remastering od
oryginałów był zawsze możliwy (dziś oryginały żyją w artefaktach, które
wygasają po 30 dniach — w gicie są, ale nigdzie nie opisane wprost).

---

## P8. Użyteczność biblioteki dla odbiorcy

Korpus jest zrównoważony gatunkowo (metal 11,8 %, woda 11,3 %, magia 9,2 %,
kamień 9,2 %, zwierzęta 7,5 %, kroki 6,8 %, ogień 6,8 %, drewno 5,1 %,
mechanizmy 3,8 %, elektryczność 1,1 %), więc nie ma przesytu jednej rodziny.

**Propozycja:** automatyczne tagi (materiał / czynność / otoczenie) wyliczone
ze scenariuszy i wystawione na stronie jako filtry, plus sortowanie po
długości i głośności. Dziś wyszukiwarka opiera się wyłącznie na tytule
i tekście scenariusza.
