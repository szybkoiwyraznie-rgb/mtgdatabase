# Audyt rozpoznawalności — czy sample brzmi jak archetyp

Sprawdzono **272** sampli z zadeklarowanym polem `archetype`.

| Wynik | ID | Karta | Archetyp | Co nie gra |
|---|---|---|---|---|
| 4.0 | 415 | Kavu Primarch | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.034, oczekiwane >= 0.3); ryk nie może być szumem (spectral_flatness=0.160, oczekiwane <= 0.15); ryk siedzi w niskim środku pasma (spectral_centroid_hz=1795.700, oczekiwane 150.0–1600.0) |
| 4.0 | 417 | Heron-Blessed Geist | `forest_birdsong` (śpiew ptaków) | ptaki to wiele zawołań (onset_count=1, oczekiwane >= 4); śpiew ptaków jest wysoki (spectral_centroid_hz=1089.600, oczekiwane 1500.0–6500.0); trele są szybkie (mod_peak_hz=1.290, oczekiwane 3.0–22.0) |
| 3.0 | 416 | Fleeting Flight | `wind_gust` (podmuch wiatru) | podmuch płynie (sustain_ratio=0.030, oczekiwane >= 0.3); podmach narasta (attack_s=0.050, oczekiwane >= 0.3); wiatr siedzi w środku pasma (spectral_centroid_hz=9028.500, oczekiwane 300.0–3000.0) |
| 2.5 | 405 | Raze to the Ground | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.093, oczekiwane >= 0.25); osuwisko się toczy (decay_s=0.090, oczekiwane >= 0.5) |
| 2.5 | 412 | Makindi Aeronaut | `wing_flutter` (trzepot skrzydeł) | skrzydła biją wielokrotnie (onset_count=1, oczekiwane >= 6); trzepot pulsuje w tempie machania (mod_peak_hz=1.050, oczekiwane 4.0–20.0) |
| 2.5 | 413 | Bloodfire Infusion | `fire_crackle` (trzask ognia / żaru) | ogień jest szumowy (spectral_flatness=0.008, oczekiwane >= 0.1); trzaski są jasne (spectral_centroid_hz=553.000, oczekiwane 1000.0–6000.0) |
| 2.5 | 429 | Vault of Whispers | `war_machine` (silnik i mechanizm wojennej machiny) | machina dudni dołem (low_all=0.003, oczekiwane >= 0.35); machina nie jest cienka (spectral_centroid_hz=7193.800, oczekiwane <= 2600.0) |
| 2.0 | 402 | Bloodfire Expert | `arrow_flight` (strzała / świst pocisku) | strzała startuje od razu (attack_s=0.110, oczekiwane <= 0.1); świst jest szumowy (spectral_flatness=0.054, oczekiwane >= 0.1) |
| 2.0 | 404 | Meteorite | `earth_rumble` (grzmot ziemi / osuwisko skalne) | grzmot się toczy (decay_s=0.040, oczekiwane >= 0.8); grzmot musi być słyszalny też na małych głośnikach, nie sam infrabas (mid_up=0.004, oczekiwane >= 0.1) |
| 2.0 | 425 | Myr Scrapling | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=8899.100, oczekiwane 800.0–6000.0); mechanizm ma rytm (ioi_cv=0.802, oczekiwane <= 0.8) |
| 2.0 | 623 | Trigon of Rage | `thunder_clap` (grzmot / uderzenie pioruna) | grzmot uderza (crest_db=14.790, oczekiwane >= 18.0); grzmot musi być słyszalny też na małych głośnikach (mid_up=0.049, oczekiwane >= 0.08) |
| 1.5 | 31 | Carrion Call | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest harmoniczne (tonal_frame_fraction=0.023, oczekiwane >= 0.3) |
| 1.5 | 390 | Battlefield Butcher | `forest_birdsong` (śpiew ptaków) | śpiew ptaków jest wysoki (spectral_centroid_hz=1339.100, oczekiwane 1500.0–6500.0) |
| 1.5 | 394 | Cancel | `psychic_shriek` (przenikliwy jęk / uderzenie psychiczne) | uderzenie psychiczne jest natychmiastowe (attack_s=0.110, oczekiwane <= 0.1) |
| 1.5 | 418 | Ior Ruin Expedition | `water_splash` (plusk / uderzenie w wodę) | plusk jest szumowy (spectral_flatness=0.002, oczekiwane >= 0.08) |
| 1.5 | 426 | Paranormal Analyst | `electric_zap` (wyładowanie / iskra) | wyładowanie jest natychmiastowe (attack_s=0.780, oczekiwane <= 0.03) |
| 1.5 | 618 | Kaleidoscorch | `fire_crackle` (trzask ognia / żaru) | ogień strzela wieloma trzaskami (onset_count=0, oczekiwane >= 8) |
| 1.5 | 624 | Arlinn's Wolf | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.215, oczekiwane >= 0.3) |
| 1.5 | 632 | Anticipate | `electric_zap` (wyładowanie / iskra) | wyładowanie jest natychmiastowe (attack_s=2.360, oczekiwane <= 0.03) |
| 1.5 | 643 | Shining Aerosaur | `wing_flutter` (trzepot skrzydeł) | skrzydła biją wielokrotnie (onset_count=2, oczekiwane >= 6) |
| 1.5 | 644 | Lich's Caress | `psychic_shriek` (przenikliwy jęk / uderzenie psychiczne) | uderzenie psychiczne jest natychmiastowe (attack_s=0.770, oczekiwane <= 0.1) |
| 1.0 | 3 | Nefarious Imp | `fire_crackle` (trzask ognia / żaru) | trzaski są jasne (spectral_centroid_hz=7264.400, oczekiwane 1000.0–6000.0) |
| 1.0 | 49 | Unstable Frontier | `earth_rumble` (grzmot ziemi / osuwisko skalne) | grzmot musi być słyszalny też na małych głośnikach, nie sam infrabas (mid_up=0.009, oczekiwane >= 0.1) |
| 1.0 | 81 | Krotiq Nestguard | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest wysokie (spectral_centroid_hz=932.100, oczekiwane 1000.0–6000.0) |
| 1.0 | 95 | Krumar Initiate | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.360, oczekiwane 2.0–12.0) |
| 1.0 | 98 | Fleeting Distraction | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest wysokie (spectral_centroid_hz=8860.500, oczekiwane 1000.0–6000.0) |
| 1.0 | 103 | Sweet Oblivion | `wind_gust` (podmuch wiatru) | wiatr siedzi w środku pasma (spectral_centroid_hz=8601.600, oczekiwane 300.0–3000.0) |
| 1.0 | 106 | Mosquito Guard | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest wysokie (spectral_centroid_hz=6176.800, oczekiwane 1000.0–6000.0) |
| 1.0 | 144 | Stensia Innkeeper | `forest_birdsong` (śpiew ptaków) | trele są szybkie (mod_peak_hz=2.760, oczekiwane 3.0–22.0) |
| 1.0 | 168 | Steel Sabotage | `earth_rumble` (grzmot ziemi / osuwisko skalne) | grzmot ziemi jest niski (spectral_centroid_hz=1446.800, oczekiwane <= 900.0) |
| 1.0 | 204 | Skilled Animator | `robot_servo` (serwo i mechanizm robota) | robot klika i pracuje (onset_count=1, oczekiwane >= 2) |
| 1.0 | 228 | Strandwalker | `heavy_footsteps` (ciężkie kroki / kopyta) | kroki mają równy rytm (ioi_cv=0.640, oczekiwane <= 0.6) |
| 1.0 | 253 | Inspiring Bard | `folk_music` (muzyka ludowa / taneczna) | rytm taneczny 1–6 Hz (mod_peak_hz=1.130, oczekiwane 1.2–6.0) |
| 1.0 | 257 | Lash of the Balrog | `whip_crack` (trzask bicza) | bicz pęka natychmiast (attack_s=0.140, oczekiwane <= 0.03) |
| 1.0 | 292 | Rediscover the Way | `wind_gust` (podmuch wiatru) | wiatr jest szumowy (spectral_flatness=0.015, oczekiwane >= 0.05) |
| 1.0 | 303 | Blanchwood Prowler | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=17.390, oczekiwane 2.0–12.0) |
| 1.0 | 378 | Sentry Bot | `horn_call` (róg bojowy / sygnał dęty) | sygnał rogu wybrzmiewa (decay_s=0.390, oczekiwane >= 0.6) |
| 1.0 | 381 | Caravan Vigil | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.100, oczekiwane 2.0–12.0) |
| 1.0 | 382 | Geological Appraiser | `earth_rumble` (grzmot ziemi / osuwisko skalne) | grzmot musi być słyszalny też na małych głośnikach, nie sam infrabas (mid_up=0.000, oczekiwane >= 0.1) |
| 1.0 | 400 | Kulrath Zealot | `fire_crackle` (trzask ognia / żaru) | trzaski są jasne (spectral_centroid_hz=7977.500, oczekiwane 1000.0–6000.0) |
| 1.0 | 406 | Stymied Hopes | `glass_shatter` (tłuczenie szkła / kryształu) | odłamki dzwonią serią (onset_count=3, oczekiwane >= 5) |
| 1.0 | 408 | Halo Scarab | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=10323.600, oczekiwane 800.0–6000.0) |
| 1.0 | 409 | Child of Night | `liquid_pour` (lanie cieczy / bulgot mikstury) | lanie jest ciągłe (sustain_ratio=0.265, oczekiwane >= 0.3) |
| 1.0 | 414 | Tuskguard Captain | `heavy_footsteps` (ciężkie kroki / kopyta) | kroki mają równy rytm (ioi_cv=0.634, oczekiwane <= 0.6) |
| 1.0 | 424 | Gruul Beastmaster | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie jest natychmiastowe (attack_s=0.910, oczekiwane <= 0.15) |
| 1.0 | 456 | Crawling Chorus | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest wysokie (spectral_centroid_hz=9314.700, oczekiwane 1000.0–6000.0) |
| 1.0 | 492 | Secluded Steppe | `wind_gust` (podmuch wiatru) | wiatr siedzi w środku pasma (spectral_centroid_hz=6780.700, oczekiwane 300.0–3000.0) |
| 1.0 | 493 | Skyclave Geopede | `stone_slide` (osuwisko / tarcie skał) | osuwisko się toczy (decay_s=0.130, oczekiwane >= 0.5) |
| 1.0 | 496 | Shiv's Embrace | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja jest szumowa, nie tonalna (spectral_flatness=0.000, oczekiwane >= 0.04) |
| 1.0 | 513 | Spreading Insurrection | `wind_gust` (podmuch wiatru) | wiatr siedzi w środku pasma (spectral_centroid_hz=3616.300, oczekiwane 300.0–3000.0) |
| 1.0 | 531 | Disa the Restless | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie się ciągnie (decay_s=0.070, oczekiwane >= 0.3) |
| 1.0 | 537 | Kor Cartographer | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.640, oczekiwane 2.0–12.0) |
| 1.0 | 553 | Coat with Venom | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.410, oczekiwane <= 0.1) |
| 1.0 | 568 | Nanoform Sentinel | `robot_servo` (serwo i mechanizm robota) | ton serwa jest stabilny (f0_semitone_std=4.380, oczekiwane <= 4.0) |
| 1.0 | 610 | Gearsmith Prodigy | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=9641.500, oczekiwane 800.0–6000.0) |
| 1.0 | 611 | Lifecrafter's Gift | `robot_servo` (serwo i mechanizm robota) | robot klika i pracuje (onset_count=1, oczekiwane >= 2) |
| 1.0 | 620 | Fen Hauler | `water_splash` (plusk / uderzenie w wodę) | plusk zaczyna się od razu (attack_s=0.250, oczekiwane <= 0.1) |
| 1.0 | 621 | Moldgraf Millipede | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie jest natychmiastowe (attack_s=0.290, oczekiwane <= 0.15) |
| 1.0 | 622 | Magma Pummeler | `earth_rumble` (grzmot ziemi / osuwisko skalne) | grzmot musi być słyszalny też na małych głośnikach, nie sam infrabas (mid_up=0.014, oczekiwane >= 0.1) |
| 1.0 | 625 | Vampire Hounds | `undead_groan` (jęk / pomruk nieumarłego) | jęk ma ciało w dole (low_all=0.002, oczekiwane >= 0.44) |
| 1.0 | 626 | Curse of the Bloody Tome | `liquid_pour` (lanie cieczy / bulgot mikstury) | lanie jest ciągłe (sustain_ratio=0.173, oczekiwane >= 0.3) |
| 1.0 | 627 | Rumbling Rockslide | `stone_slide` (osuwisko / tarcie skał) | osuwisko się toczy (decay_s=0.180, oczekiwane >= 0.5) |
| 1.0 | 628 | Ambassador Oak | `heavy_footsteps` (ciężkie kroki / kopyta) | krok nie jest cienki (spectral_centroid_hz=6399.500, oczekiwane <= 2000.0) |
| 1.0 | 635 | Feral Ridgewolf | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk ma ciało w dole pasma (low_all=0.107, oczekiwane >= 0.45) |
| 1.0 | 636 | Creeping Peeper | `creature_cackle` (chichot / pokrzykiwanie stworzenia) | chichot pulsuje w tempie śmiechu (mod_peak_hz=1.280, oczekiwane 2.5–14.0) |
| 1.0 | 637 | Vortex Runner | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.033, oczekiwane >= 0.3) |
| 1.0 | 639 | Open the Gates | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.780, oczekiwane 2.0–12.0) |
| 1.0 | 641 | Banishing Light | `temple_bell` (dzwon / dzwonek / gong) | dzwon siedzi w środku pasma (spectral_centroid_hz=137.700, oczekiwane 400.0–3000.0) |
| 0.5 | 345 | Porcelain Legionnaire | `sword_clash` (starcie stali / cios miecza) | uderzenie ma szumowy transient (spectral_flatness=0.042, oczekiwane >= 0.05) |
| 0.5 | 368 | Scythe Tiger | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie ma masę (low_all=0.080, oczekiwane >= 0.2) |
| 0.5 | 380 | Artful Maneuver | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie ma masę (low_all=0.094, oczekiwane >= 0.2) |
| 0.5 | 516 | Tenth District Veteran | `sword_clash` (starcie stali / cios miecza) | uderzenie ma szumowy transient (spectral_flatness=0.014, oczekiwane >= 0.05) |
| 0.5 | 629 | Tail Slash | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie ma masę (low_all=0.072, oczekiwane >= 0.2) |
| 0 | 1 | Dunland Crebain | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 2 | Coralhelm Guide | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 4 | Mystic Sanctuary | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 5 | Academy Journeymage | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 6 | Azorius Justiciar | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 7 | Mindstab | `psychic_shriek` (przenikliwy jęk / uderzenie psychiczne) | — |
| 0 | 9 | Toll of the Invasion | `wind_gust` (podmuch wiatru) | — |
| 0 | 12 | Merchant's Dockhand | `robot_servo` (serwo i mechanizm robota) | — |
| 0 | 13 | Soulmender | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 14 | Crew Captain | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 15 | Tellah, Great Sage | `whip_crack` (trzask bicza) | — |
| 0 | 16 | Brawler's Plate | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 17 | Selhoff Occultist | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 18 | Lotusguard Disciple | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 20 | Jeskai Devotee | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 23 | Brightwood Tracker | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 26 | Ember Beast | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 29 | You're Not Alone | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 37 | Howl of the Night Pack | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 39 | Brute Force | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 40 | Expunge | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 42 | Murder of Crows | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 43 | Kor Sanctifiers | `wind_gust` (podmuch wiatru) | — |
| 0 | 45 | Piercing Rays | `electric_zap` (wyładowanie / iskra) | — |
| 0 | 52 | Divest | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | — |
| 0 | 56 | Diplomatic Relations | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 58 | Mobile Garrison | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 67 | Scorpion Sentinel | `war_machine` (silnik i mechanizm wojennej machiny) | — |
| 0 | 71 | Security Rhox | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 72 | Dragon Arch | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 73 | Bladed Sentinel | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 74 | Rush of Battle | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 75 | Phyrexian Rager | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 80 | Merciless Repurposing | `war_machine` (silnik i mechanizm wojennej machiny) | — |
| 0 | 82 | Messenger Falcons | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 87 | Angelic Benediction | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 92 | Silumgar Butcher | `undead_groan` (jęk / pomruk nieumarłego) | — |
| 0 | 96 | Voice of the Vermin | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 112 | Flurry of Wings | `wing_flutter` (trzepot skrzydeł) | — |
| 0 | 113 | Welder Automaton | `robot_servo` (serwo i mechanizm robota) | — |
| 0 | 118 | Dire-Strain Brawler | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 120 | Returned Centaur | `undead_groan` (jęk / pomruk nieumarłego) | — |
| 0 | 124 | Courage in Crisis | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 126 | Bird Admirer | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 128 | Undead Servant | `undead_groan` (jęk / pomruk nieumarłego) | — |
| 0 | 129 | Charismatic Vanguard | `anvil_strike` (uderzenie młota w kowadło) | — |
| 0 | 132 | Pilgrim's Eye | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | — |
| 0 | 140 | Boros Challenger | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 145 | Clone Shell | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 150 | Balamb Garden, SeeD Academy | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 156 | Summary Judgment | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 157 | Infectious Bloodlust | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 163 | Ghoulcaller's Bell | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 164 | Gryffwing Cavalry | `wing_flutter` (trzepot skrzydeł) | — |
| 0 | 166 | Talion's Messenger | `insect_swarm` (rój owadów / bzykanie) | — |
| 0 | 172 | Mournful Zombie | `undead_groan` (jęk / pomruk nieumarłego) | — |
| 0 | 173 | Awaken the Bear | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 176 | Chocobo Kick | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 177 | Dire Fleet Ravager | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 187 | Idyllic Grange | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 192 | Crumbling Vestige | `glass_shatter` (tłuczenie szkła / kryształu) | — |
| 0 | 194 | Lionheart Maverick | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 196 | Mnemonic Wall | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 202 | Inferno Titan | `volcanic_eruption` (wybuch wulkanu / lawy) | — |
| 0 | 207 | Feed the Infection | `arrow_flight` (strzała / świst pocisku) | — |
| 0 | 209 | Burning-Yard Trainer | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 210 | Fiery Justice | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 213 | Reclusive Artificer | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | — |
| 0 | 214 | Snarling Wolf | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 216 | Armored Skaab | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 223 | Angel's Feather | `wing_flutter` (trzepot skrzydeł) | — |
| 0 | 224 | Immersturm Skullcairn | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 226 | Makeshift Mauler | `robot_servo` (serwo i mechanizm robota) | — |
| 0 | 231 | Anthem of Champions | `arcane_choir` (chór / zaświatowy śpiew bez słów) | — |
| 0 | 232 | Goblin Piker | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 241 | News Helicopter | `war_machine` (silnik i mechanizm wojennej machiny) | — |
| 0 | 244 | Natural Connection | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 247 | Subterranean Scout | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 250 | Loxodon Mender | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 251 | Stirring Bard | `folk_music` (muzyka ludowa / taneczna) | — |
| 0 | 260 | Etched Host Doombringer | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 261 | Universal Solvent | `steam_hiss` (syk pary / gazu) | — |
| 0 | 262 | Angel's Herald | `horn_call` (róg bojowy / sygnał dęty) | — |
| 0 | 263 | Man-o'-War | `electric_zap` (wyładowanie / iskra) | — |
| 0 | 265 | Boulder Salvo | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 266 | Druid of the Cowl | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 269 | Scouting Hawk | `beast_screech` (wrzask / pisk potwora) | — |
| 0 | 276 | Heap Gate | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 277 | Spinewoods Paladin | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 280 | Sultai Scavenger | `creature_cackle` (chichot / pokrzykiwanie stworzenia) | — |
| 0 | 298 | Raise the Alarm | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 308 | Greatsword of Tyr | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 312 | Goblin Battle Jester | `creature_cackle` (chichot / pokrzykiwanie stworzenia) | — |
| 0 | 316 | Wormfang Newt | `steam_hiss` (syk pary / gazu) | — |
| 0 | 317 | Village Bell-Ringer | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 323 | Quandrix Campus | `liquid_pour` (lanie cieczy / bulgot mikstury) | — |
| 0 | 324 | Spineseeker Centipede | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | — |
| 0 | 325 | Narset's Rebuke | `thunder_clap` (grzmot / uderzenie pioruna) | — |
| 0 | 327 | Brave-Kin Duo | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 328 | Bog Hoodlums | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 329 | Blinding Drone | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 332 | Blitz of the Thunder-Raptor | `thunder_clap` (grzmot / uderzenie pioruna) | — |
| 0 | 333 | Bring to Trial | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 334 | Skyscythe Engulfer | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 335 | Gather the Townsfolk | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 336 | Zombie Boa | `steam_hiss` (syk pary / gazu) | — |
| 0 | 338 | Brine Giant | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 340 | Ambulatory Edifice | `steam_hiss` (syk pary / gazu) | — |
| 0 | 341 | Pacifism | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 343 | Puppeteer Clique | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 344 | Pain for All | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 347 | Pristine Talisman | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 348 | Impulse | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | — |
| 0 | 350 | Temple of Abandon | `fire_crackle` (trzask ognia / żaru) | — |
| 0 | 351 | Sporecap Spider | `steam_hiss` (syk pary / gazu) | — |
| 0 | 352 | Evangel of Synthesis | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 353 | Warden of Geometries | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 355 | Cathartic Reunion | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 356 | Cazur, Ruthless Stalker | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | — |
| 0 | 357 | Lorescale Coatl | `steam_hiss` (syk pary / gazu) | — |
| 0 | 358 | Frontline War-Rager | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 359 | Foul Orchard | `insect_swarm` (rój owadów / bzykanie) | — |
| 0 | 361 | Noble Vestige | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 363 | Wild Celebrants | `glass_shatter` (tłuczenie szkła / kryształu) | — |
| 0 | 364 | Naturalize | `bone_snap` (trzask kości / łamanie) | — |
| 0 | 365 | Rakish Revelers | `folk_music` (muzyka ludowa / taneczna) | — |
| 0 | 369 | Improbable Alliance | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 370 | Consume Spirit | `arrow_flight` (strzała / świst pocisku) | — |
| 0 | 371 | Spellkeeper Weird | `electric_zap` (wyładowanie / iskra) | — |
| 0 | 372 | Dragonbroods' Relic | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 383 | Supernatural Stamina | `door_creak` (skrzypienie drewna / zawiasów) | — |
| 0 | 387 | Molten Nursery | `volcanic_eruption` (wybuch wulkanu / lawy) | — |
| 0 | 391 | Wolf's Quarry | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 392 | Kuldotha Ringleader | `horn_call` (róg bojowy / sygnał dęty) | — |
| 0 | 396 | Vow of Wildness | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 397 | Render Speechless | `whip_crack` (trzask bicza) | — |
| 0 | 398 | Intrepid Tenderfoot | `chain_rattle` (grzechot łańcuchów / kolczugi) | — |
| 0 | 407 | Secure the Scene | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 410 | Austere Command | `thunder_clap` (grzmot / uderzenie pioruna) | — |
| 0 | 411 | Neurok Invisimancer | `war_machine` (silnik i mechanizm wojennej machiny) | — |
| 0 | 423 | Gnoll War Band | `creature_cackle` (chichot / pokrzykiwanie stworzenia) | — |
| 0 | 427 | Jilt | `glass_shatter` (tłuczenie szkła / kryształu) | — |
| 0 | 431 | Delta Bloodflies | `insect_swarm` (rój owadów / bzykanie) | — |
| 0 | 434 | Epic Experiment | `war_machine` (silnik i mechanizm wojennej machiny) | — |
| 0 | 435 | Warrior's Sword | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 442 | Cenn's Tactician | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 444 | Colossodon Yearling | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 445 | Locthwain Paladin | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 452 | Omenspeaker | `arcane_choir` (chór / zaświatowy śpiew bez słów) | — |
| 0 | 453 | Elgaud Inquisitor | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 459 | Prismari Campus | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 460 | Ivy Lane Denizen | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 463 | Knockout Maneuver | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 464 | Polluted Dead | `undead_groan` (jęk / pomruk nieumarłego) | — |
| 0 | 468 | Cacophodon | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 469 | Chained Throatseeker | `chain_rattle` (grzechot łańcuchów / kolczugi) | — |
| 0 | 478 | Spare from Evil | `glass_shatter` (tłuczenie szkła / kryształu) | — |
| 0 | 482 | True Conviction | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 491 | Nature's Embrace | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 495 | Scorch Spitter | `volcanic_eruption` (wybuch wulkanu / lawy) | — |
| 0 | 501 | Exterminator Magmarch | `war_machine` (silnik i mechanizm wojennej machiny) | — |
| 0 | 506 | Spread the Sickness | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 510 | Angel of the Dawn | `arcane_choir` (chór / zaświatowy śpiew bez słów) | — |
| 0 | 515 | Warmaker Gunship | `war_machine` (silnik i mechanizm wojennej machiny) | — |
| 0 | 518 | Woolly Loxodon | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 521 | Leafcrown Dryad | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 522 | Hobble | `chain_rattle` (grzechot łańcuchów / kolczugi) | — |
| 0 | 524 | Squire's Lightblade | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 525 | Jill, Shiva's Dominant | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 532 | You're Confronted by Robbers | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 534 | Terminal Agony | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 539 | Silvanus's Invoker | `earth_rumble` (grzmot ziemi / osuwisko skalne) | — |
| 0 | 540 | Chittering Rats | `insect_swarm` (rój owadów / bzykanie) | — |
| 0 | 542 | Panic Spellbomb | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 548 | Steelclaw Lance | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 557 | Kishla Village | `folk_music` (muzyka ludowa / taneczna) | — |
| 0 | 558 | White Mage's Staff | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 559 | Gaelicat | `beast_screech` (wrzask / pisk potwora) | — |
| 0 | 561 | Time to Feed | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 562 | Shock | `thunder_clap` (grzmot / uderzenie pioruna) | — |
| 0 | 565 | Mana Cylix | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 567 | Jwar Isle Avenger | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 571 | Vow of Flight | `wing_flutter` (trzepot skrzydeł) | — |
| 0 | 574 | Invasive Species | `insect_swarm` (rój owadów / bzykanie) | — |
| 0 | 576 | Akroan Sergeant | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 580 | Loporrit Scout | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 583 | Kill Shot | `arrow_flight` (strzała / świst pocisku) | — |
| 0 | 594 | Ironclad Slayer | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 607 | Containment Membrane | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 608 | Skymarch Bloodletter | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 616 | Act of Treason | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 619 | Orazca Puzzle-Door | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | — |
| 0 | 630 | Changeling Berserker | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 631 | Sphinx's Herald | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 633 | Trumpet Blast | `horn_call` (róg bojowy / sygnał dęty) | — |
| 0 | 634 | Violent Urge | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 638 | Kraken Hatchling | `anvil_strike` (uderzenie młota w kowadło) | — |
| 0 | 640 | Living History | `undead_groan` (jęk / pomruk nieumarłego) | — |
| 0 | 642 | Pheres-Band Centaurs | `plate_clank` (pancerz / płyty stalowe) | — |

Werdykty: {'nie trafiony': 11, 'prawdopodobnie': 62, 'trafiony': 199}

0 pkt = kontrakt archetypu spełniony w całości. ≥ 2 pkt = sample nie jest tym,
co deklaruje scenariusz, i nie da się go rozpoznać z zamkniętymi oczami.
