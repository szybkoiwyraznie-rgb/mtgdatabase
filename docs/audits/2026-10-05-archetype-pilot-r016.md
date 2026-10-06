# Pilot archetypowy r016 — 5 kart × 3 warianty, wybór kontraktem

Data: 2026-10-05 · batch `r016` · 15 generacji · długość 4,0 s

Cel: sprawdzić, czy **prompt archetypowy** (ryk, chór, jęk, grzmot, erupcja)
zamiast opisu tekstury naprawia rozpoznawalność, i czy **wybór wariantu
kontraktem** zdejmuje wariancję generacji, na którą skarżył się właściciel.

## Wynik

| ID | Karta | Archetyp | Przed | Najlepszy wariant | Po | Wybrany | Punktacja wariantów |
|---:|---|---|---:|---:|---:|---|---|
| 387 | Molten Nursery | wybuch wulkanu / lawy | 2.5 | 1.0 | **1.0** | v1 | 1.0 / 1.0 / 2.0 |
| 396 | Vow of Wildness | ryk / porykiwanie dużego zwierzęcia | 3.5 | 0 | **0** | v3 | 0 / 2.5 / 3.5 |
| 452 | Omenspeaker | chór / zaświatowy śpiew bez słów | 6.0 | 0 | **0** | v3 | 0 / 0 / 0 |
| 464 | Polluted Dead | jęk / pomruk nieumarłego | 4.0 | 2.5 | **2.5** | v1 | 2.5 / 2.5 / 2.5 |
| 539 | Silvanus's Invoker | grzmot ziemi / osuwisko skalne | 3.5 | 0 | **1.0** | v2 | 0 / 0 / 0 |

`Przed` i `Po` = punktacja kontraktu archetypu na pliku produkcyjnym
(`data/samples/archetype-match-2026-10-05-{baseline,after-r016}.json`); 0 pkt =
kontrakt spełniony, <2 = prawdopodobnie, ≥2 = nie trafiony.

**Rozrzut między wariantami jest realny**: `396` ryk — 0 pkt vs 2,5 pkt vs 3,5 pkt
z tego samego promptu. Bez selekcji trafiamy w dobry wariant z
prawdopodobieństwem 1/3.

## Co pilot pokazał

- **Prompt archetypowy działa, kiedy archetyp jest jednoznaczny.** `452`
  (chór proroctwa) i `396` (ryk) weszły na 0 pkt; wszystkie trzy warianty
  chóru spełniły kontrakt — to nie przypadek, to powtarzalność archetypu.
  Dla porównania przed pilotem `452` miał 6,0 pkt (toaleta zamiast chóru).
- **Erupcja zjechała w generyczny boom.** `387` v1 ma `spectral_flatness`
  0,0003 i kosinus **0,9762** z `501` (salwa plazmowa Egzekutora) — audyt
  złapał dokładnie to, na co skarży się właściciel: dwa różne karty, ten sam
  bezimienny huk. Kontrakt odrzucił to poprawnie (`erupcja jest szumowa,
  nie tonalna`); runda `r016b` zamawia lawę i parę zamiast „explosive blast”.
- **Grzmot ziemi jest poprawny archetypowo, ale niesłyszalny.** `539`:
  `low_all` 0,937, `mid_up` 0,063, centroid 101 Hz, flagi `boomy`+`dull`.
  Na telefonie i laptopie to prawie cisza. Dlatego kontrakt `earth_rumble`
  dostał dodatkowy warunek `mid_up >= 0,10` (słyszalność na małych
  głośnikach) — `539` spada z 0 na 1,0 pkt, co jest uczciwsze.
- **Jęk nieumarłego: model kontra kontrakt.** Wszystkie trzy warianty `464`
  mają centroid 1,1–1,25 kHz przy kontrakcie 120–1000 Hz. Możliwe dwie
  przyczyny: model nie schodzi niżej albo próg jest zły (jęki zombie w grach
  bywają chrapliwe i wyższe). `r016b` zamawia wprost „low register” — jeśli
  znów wyjdzie ~1 kHz, kalibrujemy kontrakt, nie prompt.

## Higiena po imporcie

- Postprodukcja: `postprocess_samples.py --ids 387,396,452,464,539 --fix-mono
  --trim-trail-s 0.4` → LUFS −20,00/−20,02/−19,99 (cel −20), 0 plików ponad
  sufit, SNR transkodowania ≥ 29,8 dB.
- Nowa opcja `--trim-trail-s` w `postprocess_samples.py`: odcina martwy ogon
  (audyt flaguje `long_trail_silence` > 1,5 s). `452` stracił 0,67 s ciszy
  (4,00 → 3,33 s, zadeklarowana długość zaktualizowana), `396` 0,14 s.
  `--fix-mono` ściągnął nadmiar stereo `452` z 2,69 do 0,99 LU.
- Flagi korpusu: 82 (bez zmian liczbowo: zniknęły dwie flagi `452`, `539`
  dalej `boomy`+`dull`). Pary bliźniacze: 1 (`387`↔`501`) — do zdjęcia
  w `r016b`.

## Stan audytu archetypów (13 kart)

- przed pilotem: {'nie trafiony': 6, 'prawdopodobnie': 6, 'trafiony': 1}
- po pilocie: {'nie trafiony': 2, 'prawdopodobnie': 8, 'trafiony': 3}

## Zastrzeżenie

Audyt archetypów jest **proxy** dla ucha. Progi ustawiono ręcznie i jeszcze
nie skalibrowano na odsłuchu właściciela — `463` przegrywa kontrakt o 0,0001
(`low_all=0.250` przy ≥0,25). Raport służy do sortowania i do kierowania
kolejnych generacji, nie do zastępowania odsłuchu.

