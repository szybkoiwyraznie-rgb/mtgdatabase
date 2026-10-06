# r017a — seria naprawcza: 20 kart × 2 warianty (40 generacji, 1600 kredytów)

Prompty archetypowe z `scripts/rewrite_archetype_prompts.py`, wybór wariantu
`pick_archetype_variant.py --postprocess --avoid-twins`, postprodukcja z trymowaniem
ogona i zrównaniem zadeklarowanej długości z plikiem.

| ID | Karta | Archetyp | Przed | Po | Werdykt | Dł. | Flagi |
|---:|---|---|---:|---:|---|---:|---|
| 518 | Woolly Loxodon | creature_roar | 6.0 | **0** | trafiony | 3.39 | — |
| 196 | Mnemonic Wall | temple_bell | 5.0 | **0** | trafiony | 3.57 | — |
| 382 | Geological Appraiser | stone_slide | 4.5 | **0** | trafiony | 3.84 | — |
| 459 | Prismari Campus | creature_roar | 5.0 | **1.5** | prawdopodobnie | 3.56 | dull |
| 352 | Evangel of Synthesis | door_creak | 4.5 | **1.0** | prawdopodobnie | 4.00 | — |
| 168 | Steel Sabotage | stone_slide | 4.5 | **1.0** | prawdopodobnie | 3.72 | — |
| 343 | Puppeteer Clique | temple_bell | 5.0 | **2.0** | nie trafiony | 4.00 | long_trail_silence |
| 18 | Lotusguard Disciple | magic_shimmer | 3.5 | **1.0** | prawdopodobnie | 3.60 | — |
| 43 | Kor Sanctifiers | wind_gust | 3.0 | **1.0** | prawdopodobnie | 3.51 | — |
| 124 | Courage in Crisis | door_creak | 4.5 | **3.0** | nie trafiony | 3.74 | — |
| 35 | Halo Forager | wing_flutter | 3.5 | **2.0** | nie trafiony | 2.53 | — |
| 62 | Grounded | wing_flutter | 3.5 | **2.0** | nie trafiony | 3.75 | boomy, dull |
| 515 | Warmaker Gunship | war_machine | 2.5 | **1.0** | prawdopodobnie | 4.00 | muffled, boomy, dull |
| 6 | Azorius Justiciar | magic_shimmer | 3.5 | **2.5** | nie trafiony | 3.43 | — |
| 112 | Flurry of Wings | wind_gust | 3.0 | **2.0** | nie trafiony | 3.54 | boomy, dull |
| 312 | Goblin Battle Jester | creature_cackle | 1.0 | **0** | trafiony | 4.00 | — |
| 521 | Leafcrown Dryad | forest_birdsong | 1.0 | **0** | trafiony | 3.40 | speech_like |
| 557 | Kishla Village | folk_music | 1.0 | **0** | trafiony | 4.00 | — |
| 7 | Mindstab | psychic_shriek | 1.5 | **1.5** | prawdopodobnie | 3.31 | — |
| 568 | Nanoform Sentinel | robot_servo | 0.5 | **1.0** | prawdopodobnie | 4.00 | — |

**18 kart poprawionych, 1 pogorszona, 1 bez zmian.**

Katalog (421 kart z archetypem): **225 nie trafionych / 120 prawdopodobnie / 76 trafionych**
(przed rundą: 234 / 117 / 70).

## Co wyszło, a co nie

- **Działa**: `518` ryk 6,0 → 0, `459` 5,0 → 1,5, `196` dzwon 5,0 → 0, `382` osuwisko
  4,5 → 0, `312` chichot 1,0 → 0, `521` ptaki 1,0 → 0, `557` muzyka ludowa 1,0 → 0,
  `515` machina 2,5 → 1,0.
- **Bliźniak wewnątrz partii**: `168` i `382` (oba `stone_slide`) mają kosinus 0,9676
  i żaden z czterech wariantów nie schodzi poniżej 0,95 (168 v1 vs 382 v2 = 0,9806,
  168 v2 vs 382 v2 = 0,9408 przed postprodukcją). Dwa prawie identyczne prompty
  archetypowe dają prawie identyczny dźwięk — selektor to widzi i karze (+2 pkt), ale
  czystej pary nie ma z czego wybrać: potrzebny osobny prompt (runda r017b).
- **`515` Warmaker Gunship** dalej `muffled/boomy/dull` (centroid 90 Hz): prompt
  o głębokim turbinowym pomruku zjechał w infrabas. Kontrakt `war_machine` dostał
  `mid_up >= 0,10` (jak `earth_rumble` i `thunder_clap`), więc audyt to łapie, ale
  naprawić musi prompt z wyraźnym środkiem pasma.
- **`521` Leafcrown Dryad** ma flagę `speech_like` — ptasi śpiew wyszedł głosowo.
- **`35` Halo Forager** ma 2,53 s (cel 3–5 s) i 2,0 pkt — do ponowienia.
- **`343` Puppeteer Clique** (dzwon 2,0 pkt) ma `long_trail_silence`.

## Poprawki narzędzi wymuszone przez tę rundę

1. `pick_archetype_variant.py --avoid-twins` — kara +2 pkt dla wariantu, który byłby
   bliźniakiem karty z korpusu albo innej karty z tej samej partii.
2. Bug: plik tymczasowy postprodukcji był wspólny dla wszystkich wariantów karty, więc
   do puli wybranych trafiał odcisk ostatniego wariantu, nie wybranego — przez to `382`
   nie dostał kary za bliźniaka z `168`. Odcisk jest trzymany przy wariancie.
3. Kontrakty `war_machine` i `thunder_clap` dostały `mid_up` (słyszalność na małych
   głośnikach) — ten sam wniosek co przy `earth_rumble`.
4. Zadeklarowana `duration_seconds` jest zrównywana z długością pliku po trymowaniu
   (inaczej 12 kart miało `duration_mismatch`).

