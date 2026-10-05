# Audyt rozpoznawalności — czy sample brzmi jak archetyp

Sprawdzono **421** sampli z zadeklarowanym polem `archetype`.

| Wynik | ID | Karta | Archetyp | Co nie gra |
|---|---|---|---|---|
| 6.0 | 255 | Urborg Uprising | `arcane_choir` (chór / zaświatowy śpiew bez słów) | chór jest harmoniczny (tonal_frame_fraction=0.198, oczekiwane >= 0.45); chór ma wyraźną wysokość (voiced_fraction=0.000, oczekiwane >= 0.25); chór płynie, nie pulsuje (sustain_ratio=0.240, oczekiwane >= 0.35); chór wybrzmiewa (decay_s=0.410, oczekiwane >= 0.8); chór siedzi w środku pasma (spectral_centroid_hz=2866.600, oczekiwane 250.0–2800.0) |
| 5.0 | 234 | Gray Slaad | `undead_groan` (jęk / pomruk nieumarłego) | jęk jest niski (spectral_centroid_hz=1164.100, oczekiwane 120.0–1000.0); jęk się ciągnie (decay_s=0.060, oczekiwane >= 0.6); jęk trzyma poziom, nie gaśnie od razu (sustain_ratio=0.202, oczekiwane >= 0.25); jęk ma ciało w dole (low_all=0.013, oczekiwane >= 0.44) |
| 5.0 | 314 | Revolutionist | `undead_groan` (jęk / pomruk nieumarłego) | jęk jest niski (spectral_centroid_hz=3262.800, oczekiwane 120.0–1000.0); jęk się ciągnie (decay_s=0.180, oczekiwane >= 0.6); jęk trzyma poziom, nie gaśnie od razu (sustain_ratio=0.073, oczekiwane >= 0.25); jęk ma ciało w dole (low_all=0.114, oczekiwane >= 0.44) |
| 5.0 | 321 | Ainok Artillerist | `undead_groan` (jęk / pomruk nieumarłego) | jęk jest niski (spectral_centroid_hz=8987.400, oczekiwane 120.0–1000.0); jęk się ciągnie (decay_s=0.020, oczekiwane >= 0.6); jęk trzyma poziom, nie gaśnie od razu (sustain_ratio=0.242, oczekiwane >= 0.25); jęk ma ciało w dole (low_all=0.007, oczekiwane >= 0.44) |
| 5.0 | 585 | Jolrael, Mwonvuli Recluse | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.000, oczekiwane >= 0.3); ryk nie może być szumem (spectral_flatness=0.280, oczekiwane <= 0.15); ryk siedzi w niskim środku pasma (spectral_centroid_hz=3314.400, oczekiwane 150.0–1600.0); ryk ma ciało w dole pasma (low_all=0.014, oczekiwane >= 0.45) |
| 4.5 | 142 | Savage Hunger | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.007, oczekiwane >= 0.3); ryk siedzi w niskim środku pasma (spectral_centroid_hz=2019.200, oczekiwane 150.0–1600.0); ryk ma ciało w dole pasma (low_all=0.043, oczekiwane >= 0.45); ryk musi trwać, nie kliknąć (decay_s=0.110, oczekiwane >= 0.4) |
| 4.5 | 240 | Descendant of Storms | `heavy_footsteps` (ciężkie kroki / kopyta) | kroki to seria uderzeń (onset_count=0, oczekiwane >= 3); brak metryki ioi_cv; ciężki krok ma masę w dole (low_all=0.062, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=10803.600, oczekiwane <= 2000.0) |
| 4.5 | 260 | Etched Host Doombringer | `sword_clash` (starcie stali / cios miecza) | cios stali jest ostry (crest_db=11.630, oczekiwane >= 18.0); stal uderza natychmiast (attack_s=0.300, oczekiwane <= 0.05); stal błyszczy górą pasma (spectral_centroid_hz=453.800, oczekiwane >= 2500.0); cios ma energię w górze (high_all=0.006, oczekiwane >= 0.3); uderzenie ma szumowy transient (spectral_flatness=0.002, oczekiwane >= 0.05) |
| 4.5 | 282 | Hysterical Blindness | `heavy_footsteps` (ciężkie kroki / kopyta) | kroki to seria uderzeń (onset_count=0, oczekiwane >= 3); brak metryki ioi_cv; ciężki krok ma masę w dole (low_all=0.001, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=4316.100, oczekiwane <= 2000.0) |
| 4.5 | 300 | Gila Courser | `heavy_footsteps` (ciężkie kroki / kopyta) | kroki to seria uderzeń (onset_count=1, oczekiwane >= 3); brak metryki ioi_cv; ciężki krok ma masę w dole (low_all=0.006, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=6766.800, oczekiwane <= 2000.0) |
| 4.5 | 337 | Glaring Aegis | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.340, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=3215.800, oczekiwane 400.0–3000.0); dzwon trzyma poziom (sustain_ratio=0.077, oczekiwane >= 0.2); dzwon musi potrwać (content_rel_s=1.390, oczekiwane >= 1.5) |
| 4.5 | 437 | Giant Spider | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.220, oczekiwane >= 0.3); skrzypienie faluje (mod_peak_hz=16.370, oczekiwane 2.0–12.0); skrzypienie siedzi w środku (spectral_centroid_hz=11511.400, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.020, oczekiwane >= 0.3) |
| 4.5 | 447 | Resurrected Cultist | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.058, oczekiwane >= 0.3); skrzypienie faluje (mod_peak_hz=1.720, oczekiwane 2.0–12.0); skrzypienie siedzi w środku (spectral_centroid_hz=4373.900, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.220, oczekiwane >= 0.3) |
| 4.5 | 577 | Thunderstaff | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.188, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=2568.500, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.120, oczekiwane >= 0.5); osuwisko trwa (content_rel_s=1.330, oczekiwane >= 1.5) |
| 4.0 | 1 | Dunland Crebain | `forest_birdsong` (śpiew ptaków) | ptaki to wiele zawołań (onset_count=3, oczekiwane >= 4); śpiew ptaków jest wysoki (spectral_centroid_hz=1334.900, oczekiwane 1500.0–6500.0); trele są szybkie (mod_peak_hz=2.860, oczekiwane 3.0–22.0) |
| 4.0 | 160 | Fiery Hellhound | `fire_crackle` (trzask ognia / żaru) | ogień jest szumowy (spectral_flatness=0.002, oczekiwane >= 0.1); ogień strzela wieloma trzaskami (onset_count=3, oczekiwane >= 8); trzaski są jasne (spectral_centroid_hz=339.100, oczekiwane 1000.0–6000.0) |
| 4.0 | 166 | Talion's Messenger | `temple_bell` (dzwon / dzwonek / gong) | dzwon jest tonalny, nie szumowy (tonal_frame_fraction=0.459, oczekiwane >= 0.5); dzwon wybrzmiewa (decay_s=0.420, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=12408.000, oczekiwane 400.0–3000.0) |
| 4.0 | 187 | Idyllic Grange | `forest_birdsong` (śpiew ptaków) | ptaki to wiele zawołań (onset_count=3, oczekiwane >= 4); śpiew ptaków jest wysoki (spectral_centroid_hz=1480.300, oczekiwane 1500.0–6500.0); trele są szybkie (mod_peak_hz=2.830, oczekiwane 3.0–22.0) |
| 4.0 | 192 | Crumbling Vestige | `temple_bell` (dzwon / dzwonek / gong) | dzwon jest tonalny, nie szumowy (tonal_frame_fraction=0.027, oczekiwane >= 0.5); dzwon wybrzmiewa (decay_s=0.350, oczekiwane >= 0.8); dzwon musi potrwać (content_rel_s=0.840, oczekiwane >= 1.5) |
| 4.0 | 298 | Raise the Alarm | `temple_bell` (dzwon / dzwonek / gong) | dzwon jest tonalny, nie szumowy (tonal_frame_fraction=0.000, oczekiwane >= 0.5); dzwon wybrzmiewa (decay_s=0.230, oczekiwane >= 0.8); dzwon trzyma poziom (sustain_ratio=0.143, oczekiwane >= 0.2) |
| 4.0 | 558 | White Mage's Staff | `temple_bell` (dzwon / dzwonek / gong) | dzwon jest tonalny, nie szumowy (tonal_frame_fraction=0.344, oczekiwane >= 0.5); dzwon wybrzmiewa (decay_s=0.340, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=7907.700, oczekiwane 400.0–3000.0) |
| 3.5 | 8 | Goblin Deathraiders | `beast_screech` (wrzask / pisk potwora) | wrzask ma gwałtowny atak (crest_db=10.530, oczekiwane >= 12.0); wrzask uderza od razu (attack_s=0.640, oczekiwane <= 0.15); wrzask ma energię w górze (high_all=0.136, oczekiwane >= 0.2) |
| 3.5 | 23 | Brightwood Tracker | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.560, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=11931.000, oczekiwane 400.0–3000.0); dzwon trzyma poziom (sustain_ratio=0.198, oczekiwane >= 0.2) |
| 3.5 | 31 | Carrion Call | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest harmoniczne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); rój brzmi ciągiem (sustain_ratio=0.125, oczekiwane >= 0.4); bzykanie jest wysokie (spectral_centroid_hz=7938.400, oczekiwane 1000.0–6000.0) |
| 3.5 | 38 | Liliana's Triumph | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.000, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=7187.200, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.150, oczekiwane >= 0.5) |
| 3.5 | 50 | Dream Twist | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.012, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.044, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.050, oczekiwane >= 0.1) |
| 3.5 | 64 | Lightwalker | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.140, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=7960.700, oczekiwane 400.0–3000.0); dzwon trzyma poziom (sustain_ratio=0.121, oczekiwane >= 0.2) |
| 3.5 | 67 | Scorpion Sentinel | `electric_zap` (wyładowanie / iskra) | wyładowanie jest natychmiastowe (attack_s=0.420, oczekiwane <= 0.03); wyładowanie jest szumowe (spectral_flatness=0.074, oczekiwane >= 0.1); iskra gaśnie szybko (decay_s=0.930, oczekiwane <= 0.8) |
| 3.5 | 74 | Rush of Battle | `thunder_clap` (grzmot / uderzenie pioruna) | grzmot jest w dole pasma (low_all=0.139, oczekiwane >= 0.5); grzmot jest niski (spectral_centroid_hz=1142.700, oczekiwane <= 800.0); grzmot uderza (crest_db=16.450, oczekiwane >= 18.0) |
| 3.5 | 81 | Krotiq Nestguard | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest harmoniczne (tonal_frame_fraction=0.167, oczekiwane >= 0.3); rój brzmi ciągiem (sustain_ratio=0.032, oczekiwane >= 0.4); rój trwa (content_rel_s=1.080, oczekiwane >= 1.5) |
| 3.5 | 87 | Angelic Benediction | `wing_flutter` (trzepot skrzydeł) | skrzydła biją wielokrotnie (onset_count=3, oczekiwane >= 6); trzepot pulsuje w tempie machania (mod_peak_hz=1.100, oczekiwane 4.0–20.0); trzepot jest szelestem w środku pasma (spectral_centroid_hz=633.400, oczekiwane 800.0–6000.0) |
| 3.5 | 89 | Release the Ants | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest harmoniczne (tonal_frame_fraction=0.089, oczekiwane >= 0.3); rój brzmi ciągiem (sustain_ratio=0.157, oczekiwane >= 0.4); bzykanie jest wysokie (spectral_centroid_hz=7620.300, oczekiwane 1000.0–6000.0) |
| 3.5 | 90 | Tranquil Cove | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.351, oczekiwane >= 0.4); migotanie jest tonalne (tonal_frame_fraction=0.025, oczekiwane >= 0.3); magia płynie, nie klika (sustain_ratio=0.258, oczekiwane >= 0.3) |
| 3.5 | 98 | Fleeting Distraction | `wing_flutter` (trzepot skrzydeł) | skrzydła biją wielokrotnie (onset_count=0, oczekiwane >= 6); trzepot pulsuje w tempie machania (mod_peak_hz=1.430, oczekiwane 4.0–20.0); trzepot jest szelestem w środku pasma (spectral_centroid_hz=8860.500, oczekiwane 800.0–6000.0) |
| 3.5 | 103 | Sweet Oblivion | `forest_birdsong` (śpiew ptaków) | ptaki to wiele zawołań (onset_count=0, oczekiwane >= 4); zawołania ptaków są tonalne (tonal_frame_fraction=0.228, oczekiwane >= 0.25); trele są szybkie (mod_peak_hz=1.020, oczekiwane 3.0–22.0) |
| 3.5 | 107 | Somberwald Spider | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); skrzypienie siedzi w środku (spectral_centroid_hz=6409.500, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.030, oczekiwane >= 0.3) |
| 3.5 | 114 | Fledgling Imp | `water_splash` (plusk / uderzenie w wodę) | plusk jest szumowy (spectral_flatness=0.002, oczekiwane >= 0.08); plusk chlapie górą (high_all=0.021, oczekiwane >= 0.25); plusk zaczyna się od razu (attack_s=0.250, oczekiwane <= 0.1) |
| 3.5 | 117 | Tireless Hauler | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.010, oczekiwane >= 0.3); skrzypienie faluje (mod_peak_hz=1.320, oczekiwane 2.0–12.0); skrzypienie siedzi w środku (spectral_centroid_hz=10492.000, oczekiwane 700.0–4000.0) |
| 3.5 | 130 | Scavenging Harpy | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.065, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=2868.900, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.220, oczekiwane >= 0.5) |
| 3.5 | 152 | Timely Interference | `thunder_clap` (grzmot / uderzenie pioruna) | grzmot jest w dole pasma (low_all=0.312, oczekiwane >= 0.5); grzmot jest niski (spectral_centroid_hz=3559.600, oczekiwane <= 800.0); grzmot się toczy (decay_s=0.110, oczekiwane >= 0.5) |
| 3.5 | 156 | Summary Judgment | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.170, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=5840.400, oczekiwane 400.0–3000.0); dzwon trzyma poziom (sustain_ratio=0.161, oczekiwane >= 0.2) |
| 3.5 | 157 | Infectious Bloodlust | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.178, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.028, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.020, oczekiwane >= 0.1) |
| 3.5 | 164 | Gryffwing Cavalry | `wing_flutter` (trzepot skrzydeł) | skrzydła biją wielokrotnie (onset_count=2, oczekiwane >= 6); trzepot pulsuje w tempie machania (mod_peak_hz=1.490, oczekiwane 4.0–20.0); trzepot jest szelestem w środku pasma (spectral_centroid_hz=538.100, oczekiwane 800.0–6000.0) |
| 3.5 | 170 | Riftburst Hellion | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.020, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=2982.200, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.040, oczekiwane >= 0.5) |
| 3.5 | 172 | Mournful Zombie | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.019, oczekiwane >= 0.3); skrzypienie siedzi w środku (spectral_centroid_hz=4930.600, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.040, oczekiwane >= 0.3) |
| 3.5 | 178 | Oreplate Pangolin | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.018, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=5794.700, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.300, oczekiwane >= 0.5) |
| 3.5 | 205 | Vulturous Aven | `arcane_choir` (chór / zaświatowy śpiew bez słów) | chór jest harmoniczny (tonal_frame_fraction=0.278, oczekiwane >= 0.45); chór wybrzmiewa (decay_s=0.690, oczekiwane >= 0.8); chór siedzi w środku pasma (spectral_centroid_hz=7260.100, oczekiwane 250.0–2800.0) |
| 3.5 | 209 | Burning-Yard Trainer | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.110, oczekiwane <= 0.05); stal błyszczy górą pasma (spectral_centroid_hz=269.500, oczekiwane >= 2500.0); cios ma energię w górze (high_all=0.005, oczekiwane >= 0.3); uderzenie ma szumowy transient (spectral_flatness=0.004, oczekiwane >= 0.05) |
| 3.5 | 223 | Angel's Feather | `wing_flutter` (trzepot skrzydeł) | skrzydła biją wielokrotnie (onset_count=3, oczekiwane >= 6); trzepot pulsuje w tempie machania (mod_peak_hz=2.410, oczekiwane 4.0–20.0); trzepot jest szelestem w środku pasma (spectral_centroid_hz=474.100, oczekiwane 800.0–6000.0) |
| 3.5 | 228 | Strandwalker | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.001, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=7180.400, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.060, oczekiwane >= 0.5) |
| 3.5 | 242 | Knight of the Skyward Eye | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.003, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=2000.900, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.150, oczekiwane >= 0.5) |
| 3.5 | 265 | Boulder Salvo | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.019, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.238, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.020, oczekiwane >= 0.1) |
| 3.5 | 286 | Weftblade Enhancer | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.230, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=7183.000, oczekiwane 400.0–3000.0); dzwon trzyma poziom (sustain_ratio=0.044, oczekiwane >= 0.2) |
| 3.5 | 289 | Rustvine Cultivator | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.011, oczekiwane >= 0.3); skrzypienie siedzi w środku (spectral_centroid_hz=4687.200, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.090, oczekiwane >= 0.3) |
| 3.5 | 290 | Soulbright Flamekin | `steam_hiss` (syk pary / gazu) | syk jest szumem (spectral_flatness=0.021, oczekiwane >= 0.15); syk siedzi w górze pasma (high_all=0.026, oczekiwane >= 0.3); syk jest ciągły (sustain_ratio=0.194, oczekiwane >= 0.3) |
| 3.5 | 303 | Blanchwood Prowler | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); skrzypienie siedzi w środku (spectral_centroid_hz=8097.000, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.060, oczekiwane >= 0.3) |
| 3.5 | 331 | Trostani Discordant | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | mechanizm klika serią (onset_count=1, oczekiwane >= 3); klik jest suchy i jasny (spectral_centroid_hz=8249.700, oczekiwane 800.0–6000.0); brak metryki ioi_cv |
| 3.5 | 347 | Pristine Talisman | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.370, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=7651.100, oczekiwane 400.0–3000.0); dzwon trzyma poziom (sustain_ratio=0.077, oczekiwane >= 0.2) |
| 3.5 | 383 | Supernatural Stamina | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.064, oczekiwane >= 0.3); skrzypienie faluje (mod_peak_hz=15.350, oczekiwane 2.0–12.0); skrzypienie się ciągnie (decay_s=0.030, oczekiwane >= 0.3) |
| 3.5 | 384 | Sequestered Stash | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.008, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=10686.600, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.180, oczekiwane >= 0.5) |
| 3.5 | 393 | Forge Devil | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.002, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=10509.900, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.090, oczekiwane >= 0.5) |
| 3.5 | 432 | Wishful Merfolk | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.002, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=6486.400, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.030, oczekiwane >= 0.5) |
| 3.5 | 448 | Rupture Spire | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.109, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=6877.000, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.390, oczekiwane >= 0.5) |
| 3.5 | 456 | Crawling Chorus | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest harmoniczne (tonal_frame_fraction=0.139, oczekiwane >= 0.3); rój brzmi ciągiem (sustain_ratio=0.097, oczekiwane >= 0.4); bzykanie jest wysokie (spectral_centroid_hz=6575.300, oczekiwane 1000.0–6000.0) |
| 3.5 | 478 | Spare from Evil | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.000, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=4445.000, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.190, oczekiwane >= 0.5) |
| 3.5 | 486 | Krallenhorde Wantons | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.111, oczekiwane >= 0.3); skrzypienie faluje (mod_peak_hz=1.800, oczekiwane 2.0–12.0); skrzypienie się ciągnie (decay_s=0.280, oczekiwane >= 0.3) |
| 3.5 | 493 | Skyclave Geopede | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.054, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=2038.200, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.120, oczekiwane >= 0.5) |
| 3.5 | 505 | Ballista Wielder | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.074, oczekiwane >= 0.3); skrzypienie faluje (mod_peak_hz=1.380, oczekiwane 2.0–12.0); skrzypienie się ciągnie (decay_s=0.100, oczekiwane >= 0.3) |
| 3.5 | 508 | Wavecrash Triton | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.380, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.052, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.040, oczekiwane >= 0.1) |
| 3.5 | 520 | Rakshasa Vizier | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.011, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=2520.200, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.030, oczekiwane >= 0.5) |
| 3.5 | 537 | Kor Cartographer | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.133, oczekiwane >= 0.3); skrzypienie faluje (mod_peak_hz=17.650, oczekiwane 2.0–12.0); skrzypienie się ciągnie (decay_s=0.050, oczekiwane >= 0.3) |
| 3.5 | 549 | Stampeding Elk Herd | `earth_rumble` (grzmot ziemi / osuwisko skalne) | grzmot ziemi jest w dole pasma (low_all=0.027, oczekiwane >= 0.5); grzmot ziemi jest niski (spectral_centroid_hz=1268.900, oczekiwane <= 900.0); grzmot się toczy (decay_s=0.070, oczekiwane >= 0.8) |
| 3.5 | 550 | Frost Lynx | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.000, oczekiwane >= 0.3); ryk ma ciało w dole pasma (low_all=0.436, oczekiwane >= 0.45); ryk musi trwać, nie kliknąć (decay_s=0.340, oczekiwane >= 0.4) |
| 3.5 | 556 | Ruthless Invasion | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.000, oczekiwane >= 0.3); ryk siedzi w niskim środku pasma (spectral_centroid_hz=1753.900, oczekiwane 150.0–1600.0); ryk ma ciało w dole pasma (low_all=0.045, oczekiwane >= 0.45) |
| 3.5 | 563 | Koilos Roc | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.042, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=7246.000, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.020, oczekiwane >= 0.5) |
| 3.5 | 582 | Vaan, Street Thief | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.250, oczekiwane >= 0.3); ryk ma ciało w dole pasma (low_all=0.021, oczekiwane >= 0.45); ryk musi trwać, nie kliknąć (decay_s=0.160, oczekiwane >= 0.4) |
| 3.5 | 588 | Cemetery Recruitment | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.002, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=5533.500, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.070, oczekiwane >= 0.5) |
| 3.5 | 607 | Containment Membrane | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.062, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.298, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.000, oczekiwane >= 0.1) |
| 3.5 | 609 | Jungleborn Pioneer | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.005, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=2303.100, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.160, oczekiwane >= 0.5) |
| 3.5 | 611 | Lifecrafter's Gift | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); skrzypienie faluje (mod_peak_hz=1.550, oczekiwane 2.0–12.0); skrzypienie się ciągnie (decay_s=0.090, oczekiwane >= 0.3) |
| 3.0 | 9 | Toll of the Invasion | `arrow_flight` (strzała / świst pocisku) | strzała startuje od razu (attack_s=0.290, oczekiwane <= 0.1); świst jest szumowy (spectral_flatness=0.008, oczekiwane >= 0.1); świst siedzi w środku i górze (spectral_centroid_hz=611.100, oczekiwane 800.0–6000.0) |
| 3.0 | 95 | Krumar Initiate | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.760, oczekiwane 2.0–12.0); skrzypienie siedzi w środku (spectral_centroid_hz=262.800, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.170, oczekiwane >= 0.3) |
| 3.0 | 101 | Grave Exchange | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.138, oczekiwane >= 0.3); magia płynie, nie klika (sustain_ratio=0.048, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.040, oczekiwane >= 0.1) |
| 3.0 | 113 | Welder Automaton | `robot_servo` (serwo i mechanizm robota) | serwo trzyma ton (tonal_frame_fraction=0.000, oczekiwane >= 0.35); robot klika i pracuje (onset_count=1, oczekiwane >= 2); serwo pracuje ciągiem (sustain_ratio=0.056, oczekiwane >= 0.2) |
| 3.0 | 124 | Courage in Crisis | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=19.410, oczekiwane 2.0–12.0); skrzypienie siedzi w środku (spectral_centroid_hz=651.500, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.140, oczekiwane >= 0.3) |
| 3.0 | 136 | Bone Splinters | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); magia płynie, nie klika (sustain_ratio=0.048, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.020, oczekiwane >= 0.1) |
| 3.0 | 143 | Kabira Vindicator | `wind_gust` (podmuch wiatru) | podmuch płynie (sustain_ratio=0.048, oczekiwane >= 0.3); wiatr jest szumowy (spectral_flatness=0.042, oczekiwane >= 0.05); podmach narasta (attack_s=0.030, oczekiwane >= 0.3) |
| 3.0 | 184 | Altar of the Goyf | `wind_gust` (podmuch wiatru) | podmuch płynie (sustain_ratio=0.294, oczekiwane >= 0.3); wiatr jest szumowy (spectral_flatness=0.015, oczekiwane >= 0.05); podmach narasta (attack_s=0.130, oczekiwane >= 0.3) |
| 3.0 | 185 | Alaborn Trooper | `wind_gust` (podmuch wiatru) | podmuch płynie (sustain_ratio=0.016, oczekiwane >= 0.3); wiatr jest szumowy (spectral_flatness=0.001, oczekiwane >= 0.05); podmach narasta (attack_s=0.010, oczekiwane >= 0.3) |
| 3.0 | 189 | Glint-Sleeve Artisan | `robot_servo` (serwo i mechanizm robota) | serwo trzyma ton (tonal_frame_fraction=0.000, oczekiwane >= 0.35); ton serwa jest stabilny (f0_semitone_std=4.440, oczekiwane <= 4.0); serwo pracuje ciągiem (sustain_ratio=0.190, oczekiwane >= 0.2) |
| 3.0 | 204 | Skilled Animator | `heavy_footsteps` (ciężkie kroki / kopyta) | kroki mają równy rytm (ioi_cv=0.645, oczekiwane <= 0.6); ciężki krok ma masę w dole (low_all=0.010, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=9507.000, oczekiwane <= 2000.0) |
| 3.0 | 211 | Seismic Monstrosaur | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); magia płynie, nie klika (sustain_ratio=0.050, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.020, oczekiwane >= 0.1) |
| 3.0 | 218 | Trigon of Corruption | `liquid_pour` (lanie cieczy / bulgot mikstury) | lanie jest ciągłe (sustain_ratio=0.117, oczekiwane >= 0.3); ciecz szumi (spectral_flatness=0.000, oczekiwane >= 0.05); lanie trwa (content_rel_s=1.220, oczekiwane >= 1.5) |
| 3.0 | 256 | Frightful Delusion | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.168, oczekiwane >= 0.3); magia płynie, nie klika (sustain_ratio=0.137, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.000, oczekiwane >= 0.1) |
| 3.0 | 274 | Akrasan Squire | `folk_music` (muzyka ludowa / taneczna) | taniec ma rytm (onset_count=3, oczekiwane >= 4); rytm taneczny 1–6 Hz (mod_peak_hz=8.890, oczekiwane 1.2–6.0); muzyka musi potrwać (content_rel_s=1.740, oczekiwane >= 2.0) |
| 3.0 | 295 | Fake Your Own Death | `forest_birdsong` (śpiew ptaków) | ptaki to wiele zawołań (onset_count=2, oczekiwane >= 4); śpiew ptaków jest wysoki (spectral_centroid_hz=1046.800, oczekiwane 1500.0–6500.0) |
| 3.0 | 342 | Gorger Wurm | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.021, oczekiwane >= 0.3); magia płynie, nie klika (sustain_ratio=0.121, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.090, oczekiwane >= 0.1) |
| 3.0 | 389 | Bring Low | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); magia płynie, nie klika (sustain_ratio=0.198, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.030, oczekiwane >= 0.1) |
| 3.0 | 462 | Marut | `heavy_footsteps` (ciężkie kroki / kopyta) | kroki mają równy rytm (ioi_cv=0.749, oczekiwane <= 0.6); ciężki krok ma masę w dole (low_all=0.001, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=8771.100, oczekiwane <= 2000.0) |
| 3.0 | 492 | Secluded Steppe | `arrow_flight` (strzała / świst pocisku) | strzała startuje od razu (attack_s=0.760, oczekiwane <= 0.1); przelot jest krótki (decay_s=1.210, oczekiwane <= 0.8); świst siedzi w środku i górze (spectral_centroid_hz=11263.300, oczekiwane 800.0–6000.0) |
| 3.0 | 506 | Spread the Sickness | `liquid_pour` (lanie cieczy / bulgot mikstury) | lanie jest ciągłe (sustain_ratio=0.117, oczekiwane >= 0.3); ciecz szumi (spectral_flatness=0.001, oczekiwane >= 0.05); ciecz siedzi w środku pasma (spectral_centroid_hz=407.300, oczekiwane 500.0–4000.0) |
| 3.0 | 531 | Disa the Restless | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.030, oczekiwane 2.0–12.0); skrzypienie siedzi w środku (spectral_centroid_hz=408.900, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.160, oczekiwane >= 0.3) |
| 3.0 | 546 | Clawing Torment | `plate_clank` (pancerz / płyty stalowe) | płyty pancerza uderzają ostro (crest_db=15.730, oczekiwane >= 17.0); stal pancerza jest jasna (spectral_centroid_hz=631.800, oczekiwane 1000.0–6000.0); brzęk stali ma szum (spectral_flatness=0.004, oczekiwane >= 0.03) |
| 2.5 | 4 | Mystic Sanctuary | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.129, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.085, oczekiwane >= 0.3) |
| 2.5 | 5 | Academy Journeymage | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.032, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.153, oczekiwane >= 0.3) |
| 2.5 | 6 | Azorius Justiciar | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.219, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.222, oczekiwane >= 0.3) |
| 2.5 | 24 | Lunar Rejection | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.051, oczekiwane >= 0.3); ryk ma ciało w dole pasma (low_all=0.378, oczekiwane >= 0.45) |
| 2.5 | 34 | Volcanic Submersion | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja ma masę w dole (low_all=0.181, oczekiwane >= 0.35); erupcja się toczy, nie wybucha raz (sustain_ratio=0.107, oczekiwane >= 0.2) |
| 2.5 | 42 | Murder of Crows | `arcane_choir` (chór / zaświatowy śpiew bez słów) | chór ma wyraźną wysokość (voiced_fraction=0.136, oczekiwane >= 0.25); chór wybrzmiewa (decay_s=0.270, oczekiwane >= 0.8) |
| 2.5 | 44 | Underdark Explorer | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.019, oczekiwane >= 0.25); osuwisko się toczy (decay_s=0.080, oczekiwane >= 0.5) |
| 2.5 | 45 | Piercing Rays | `electric_zap` (wyładowanie / iskra) | wyładowanie jest natychmiastowe (attack_s=0.120, oczekiwane <= 0.03); wyładowanie ma ostry szczyt (crest_db=17.190, oczekiwane >= 18.0) |
| 2.5 | 53 | Illvoi Operative | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.190, oczekiwane >= 0.8); dzwon trzyma poziom (sustain_ratio=0.089, oczekiwane >= 0.2) |
| 2.5 | 63 | Dragon Fodder | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.061, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=3275.500, oczekiwane <= 2000.0) |
| 2.5 | 75 | Phyrexian Rager | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.017, oczekiwane >= 0.25); osuwisko się toczy (decay_s=0.100, oczekiwane >= 0.5) |
| 2.5 | 78 | Nightsnare | `temple_bell` (dzwon / dzwonek / gong) | dzwon jest tonalny, nie szumowy (tonal_frame_fraction=0.000, oczekiwane >= 0.5); dzwon siedzi w środku pasma (spectral_centroid_hz=7127.600, oczekiwane 400.0–3000.0) |
| 2.5 | 86 | Cloudbound Moogle | `temple_bell` (dzwon / dzwonek / gong) | dzwon jest tonalny, nie szumowy (tonal_frame_fraction=0.460, oczekiwane >= 0.5); dzwon siedzi w środku pasma (spectral_centroid_hz=11124.800, oczekiwane 400.0–3000.0) |
| 2.5 | 120 | Returned Centaur | `plate_clank` (pancerz / płyty stalowe) | płyty pancerza uderzają ostro (crest_db=15.430, oczekiwane >= 17.0); pancerz dzwoni kilkoma płytami (onset_count=1, oczekiwane >= 2); płyty gasną szybciej niż dzwon (decay_s=1.290, oczekiwane <= 1.2) |
| 2.5 | 127 | Wing Shredder | `temple_bell` (dzwon / dzwonek / gong) | dzwon jest tonalny, nie szumowy (tonal_frame_fraction=0.478, oczekiwane >= 0.5); dzwon siedzi w środku pasma (spectral_centroid_hz=9522.500, oczekiwane 400.0–3000.0) |
| 2.5 | 128 | Undead Servant | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.007, oczekiwane >= 0.25); osuwisko się toczy (decay_s=0.080, oczekiwane >= 0.5) |
| 2.5 | 141 | Sun-Collared Raptor | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.003, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=2973.100, oczekiwane <= 2000.0) |
| 2.5 | 146 | Palace Familiar | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.002, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.173, oczekiwane >= 0.3) |
| 2.5 | 150 | Balamb Garden, SeeD Academy | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.020, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=5642.200, oczekiwane <= 2000.0) |
| 2.5 | 167 | Lost in the Mist | `water_splash` (plusk / uderzenie w wodę) | plusk jest szumowy (spectral_flatness=0.000, oczekiwane >= 0.08); plusk chlapie górą (high_all=0.080, oczekiwane >= 0.25) |
| 2.5 | 174 | Izzet Charm | `electric_zap` (wyładowanie / iskra) | wyładowanie jest natychmiastowe (attack_s=0.060, oczekiwane <= 0.03); iskra gaśnie szybko (decay_s=1.530, oczekiwane <= 0.8) |
| 2.5 | 183 | Sifter Wurm | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.001, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=8905.100, oczekiwane <= 2000.0) |
| 2.5 | 188 | Apprentice Wizard | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.049, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=6691.300, oczekiwane <= 2000.0) |
| 2.5 | 191 | Esper Stormblade | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja ma masę w dole (low_all=0.031, oczekiwane >= 0.35); erupcja trwa (content_rel_s=1.340, oczekiwane >= 1.5) |
| 2.5 | 202 | Inferno Titan | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja ma masę w dole (low_all=0.069, oczekiwane >= 0.35); erupcja się toczy, nie wybucha raz (sustain_ratio=0.193, oczekiwane >= 0.2) |
| 2.5 | 217 | Manor Gate | `chain_rattle` (grzechot łańcuchów / kolczugi) | łańcuch dzwoni wieloma ogniwami (onset_count=4, oczekiwane >= 6); łańcuch jest jasny (spectral_centroid_hz=1990.700, oczekiwane >= 2000.0) |
| 2.5 | 219 | Prishe's Wanderings | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.700, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=6137.300, oczekiwane 400.0–3000.0) |
| 2.5 | 220 | Urza's Mine | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); skrzypienie siedzi w środku (spectral_centroid_hz=4927.200, oczekiwane 700.0–4000.0) |
| 2.5 | 238 | Ramroller | `steam_hiss` (syk pary / gazu) | syk jest szumem (spectral_flatness=0.092, oczekiwane >= 0.15); syk jest ciągły (sustain_ratio=0.266, oczekiwane >= 0.3) |
| 2.5 | 241 | News Helicopter | `horn_call` (róg bojowy / sygnał dęty) | róg jest harmoniczny (voiced_fraction=0.254, oczekiwane >= 0.3); sygnał rogu wybrzmiewa (decay_s=0.470, oczekiwane >= 0.6) |
| 2.5 | 244 | Natural Connection | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.003, oczekiwane >= 0.25); osuwisko się toczy (decay_s=0.400, oczekiwane >= 0.5) |
| 2.5 | 296 | Minotaur Abomination | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.172, oczekiwane >= 0.3); skrzypienie się ciągnie (decay_s=0.090, oczekiwane >= 0.3) |
| 2.5 | 307 | Jyoti, Moag Ancient | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.026, oczekiwane >= 0.25); osuwisko się toczy (decay_s=0.100, oczekiwane >= 0.5) |
| 2.5 | 317 | Village Bell-Ringer | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.730, oczekiwane >= 0.8); dzwon trzyma poziom (sustain_ratio=0.188, oczekiwane >= 0.2) |
| 2.5 | 358 | Frontline War-Rager | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.150, oczekiwane >= 0.3); ryk ma ciało w dole pasma (low_all=0.007, oczekiwane >= 0.45) |
| 2.5 | 367 | Battle-Rattle Shaman | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.680, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=8841.700, oczekiwane 400.0–3000.0) |
| 2.5 | 401 | Rage of Purphoros | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.001, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=7428.100, oczekiwane <= 2000.0) |
| 2.5 | 441 | Survivor of Korlis | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.054, oczekiwane >= 0.25); osuwisko się toczy (decay_s=0.040, oczekiwane >= 0.5) |
| 2.5 | 468 | Cacophodon | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.024, oczekiwane >= 0.3); ryk ma ciało w dole pasma (low_all=0.018, oczekiwane >= 0.45) |
| 2.5 | 475 | Ruinous Rampage | `undead_groan` (jęk / pomruk nieumarłego) | jęk jest niski (spectral_centroid_hz=2989.900, oczekiwane 120.0–1000.0); jęk ma ciało w dole (low_all=0.431, oczekiwane >= 0.44) |
| 2.5 | 477 | Jeskai Windscout | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.001, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.270, oczekiwane >= 0.3) |
| 2.5 | 494 | Crested Herdcaller | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.064, oczekiwane >= 0.3); ryk ma ciało w dole pasma (low_all=0.372, oczekiwane >= 0.45) |
| 2.5 | 495 | Scorch Spitter | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja ma masę w dole (low_all=0.014, oczekiwane >= 0.35); erupcja trwa (content_rel_s=1.400, oczekiwane >= 1.5) |
| 2.5 | 509 | Highland Game | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.189, oczekiwane >= 0.3); skrzypienie się ciągnie (decay_s=0.080, oczekiwane >= 0.3) |
| 2.5 | 519 | Lurking Green Dragon | `steam_hiss` (syk pary / gazu) | syk jest szumem (spectral_flatness=0.031, oczekiwane >= 0.15); syk siedzi w górze pasma (high_all=0.249, oczekiwane >= 0.3) |
| 2.5 | 532 | You're Confronted by Robbers | `sword_clash` (starcie stali / cios miecza) | stal błyszczy górą pasma (spectral_centroid_hz=1146.400, oczekiwane >= 2500.0); cios ma energię w górze (high_all=0.260, oczekiwane >= 0.3); uderzenie ma szumowy transient (spectral_flatness=0.017, oczekiwane >= 0.05) |
| 2.5 | 538 | Ojutai's Breath | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | mechanizm klika serią (onset_count=0, oczekiwane >= 3); brak metryki ioi_cv |
| 2.5 | 545 | Fuel for the Cause | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.133, oczekiwane >= 0.4); magia płynie, nie klika (sustain_ratio=0.214, oczekiwane >= 0.3) |
| 2.5 | 562 | Shock | `thunder_clap` (grzmot / uderzenie pioruna) | grzmot jest w dole pasma (low_all=0.160, oczekiwane >= 0.5); grzmot jest niski (spectral_centroid_hz=2125.100, oczekiwane <= 800.0) |
| 2.5 | 571 | Vow of Flight | `sword_clash` (starcie stali / cios miecza) | stal błyszczy górą pasma (spectral_centroid_hz=206.200, oczekiwane >= 2500.0); cios ma energię w górze (high_all=0.008, oczekiwane >= 0.3); uderzenie ma szumowy transient (spectral_flatness=0.044, oczekiwane >= 0.05) |
| 2.5 | 574 | Invasive Species | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); skrzypienie się ciągnie (decay_s=0.070, oczekiwane >= 0.3) |
| 2.5 | 579 | Kulrath Mystic | `fire_crackle` (trzask ognia / żaru) | ogień jest szumowy (spectral_flatness=0.001, oczekiwane >= 0.1); trzaski są jasne (spectral_centroid_hz=456.000, oczekiwane 1000.0–6000.0) |
| 2.5 | 590 | Keep Out | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.440, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=9845.800, oczekiwane 400.0–3000.0) |
| 2.5 | 592 | Glorifier of Suffering | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.130, oczekiwane >= 0.25); skały są niskie (spectral_centroid_hz=2189.200, oczekiwane <= 2000.0) |
| 2.5 | 595 | Óin the Brave | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.300, oczekiwane >= 0.8); dzwon siedzi w środku pasma (spectral_centroid_hz=9918.100, oczekiwane 400.0–3000.0) |
| 2.5 | 610 | Gearsmith Prodigy | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | mechanizm klika serią (onset_count=2, oczekiwane >= 3); brak metryki ioi_cv |
| 2.5 | 617 | Douse in Gloom | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.129, oczekiwane >= 0.4); migotanie jest tonalne (tonal_frame_fraction=0.207, oczekiwane >= 0.3) |
| 2.0 | 2 | Coralhelm Guide | `water_splash` (plusk / uderzenie w wodę) | plusk chlapie górą (high_all=0.121, oczekiwane >= 0.25); plusk zaczyna się od razu (attack_s=0.370, oczekiwane <= 0.1) |
| 2.0 | 33 | Fierce Empath | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie siedzi w środku (spectral_centroid_hz=637.700, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.070, oczekiwane >= 0.3) |
| 2.0 | 35 | Halo Forager | `wing_flutter` (trzepot skrzydeł) | trzepot pulsuje w tempie machania (mod_peak_hz=1.160, oczekiwane 4.0–20.0); trzepot jest szelestem w środku pasma (spectral_centroid_hz=298.100, oczekiwane 800.0–6000.0) |
| 2.0 | 48 | Raucous Carnival | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=16.000, oczekiwane 2.0–12.0); skrzypienie się ciągnie (decay_s=0.040, oczekiwane >= 0.3) |
| 2.0 | 51 | Deepwood Denizen | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie siedzi w środku (spectral_centroid_hz=187.300, oczekiwane 700.0–4000.0); skrzypienie się ciągnie (decay_s=0.170, oczekiwane >= 0.3) |
| 2.0 | 58 | Mobile Garrison | `plate_clank` (pancerz / płyty stalowe) | pancerz dzwoni kilkoma płytami (onset_count=0, oczekiwane >= 2); brzęk stali ma szum (spectral_flatness=0.011, oczekiwane >= 0.03) |
| 2.0 | 62 | Grounded | `wing_flutter` (trzepot skrzydeł) | trzepot pulsuje w tempie machania (mod_peak_hz=1.860, oczekiwane 4.0–20.0); trzepot jest szelestem w środku pasma (spectral_centroid_hz=151.900, oczekiwane 800.0–6000.0) |
| 2.0 | 68 | Ainok Tracker | `heavy_footsteps` (ciężkie kroki / kopyta) | ciężki krok ma masę w dole (low_all=0.010, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=5383.200, oczekiwane <= 2000.0) |
| 2.0 | 79 | Holdout Settlement | `wind_gust` (podmuch wiatru) | wiatr jest szumowy (spectral_flatness=0.000, oczekiwane >= 0.05); wiatr siedzi w środku pasma (spectral_centroid_hz=261.800, oczekiwane 300.0–3000.0) |
| 2.0 | 88 | Baral and Kari Zev | `sword_clash` (starcie stali / cios miecza) | cios stali jest ostry (crest_db=16.630, oczekiwane >= 18.0); stal błyszczy górą pasma (spectral_centroid_hz=1945.100, oczekiwane >= 2500.0) |
| 2.0 | 102 | Fiery Fall | `wind_gust` (podmuch wiatru) | podmuch płynie (sustain_ratio=0.190, oczekiwane >= 0.3); wiatr jest szumowy (spectral_flatness=0.004, oczekiwane >= 0.05) |
| 2.0 | 105 | Blade-Blizzard Kitsune | `wind_gust` (podmuch wiatru) | podmuch płynie (sustain_ratio=0.282, oczekiwane >= 0.3); wiatr siedzi w środku pasma (spectral_centroid_hz=3894.700, oczekiwane 300.0–3000.0) |
| 2.0 | 111 | Final Parting | `forest_birdsong` (śpiew ptaków) | zawołania ptaków są tonalne (tonal_frame_fraction=0.013, oczekiwane >= 0.25); trele są szybkie (mod_peak_hz=1.120, oczekiwane 3.0–22.0) |
| 2.0 | 112 | Flurry of Wings | `wind_gust` (podmuch wiatru) | wiatr jest szumowy (spectral_flatness=0.000, oczekiwane >= 0.05); wiatr siedzi w środku pasma (spectral_centroid_hz=164.200, oczekiwane 300.0–3000.0) |
| 2.0 | 147 | Renegade Tactics | `heavy_footsteps` (ciężkie kroki / kopyta) | ciężki krok ma masę w dole (low_all=0.057, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=6207.500, oczekiwane <= 2000.0) |
| 2.0 | 158 | Kozilek's Shrieker | `beast_screech` (wrzask / pisk potwora) | wrzask uderza od razu (attack_s=1.260, oczekiwane <= 0.15); wrzask ma energię w górze (high_all=0.074, oczekiwane >= 0.2) |
| 2.0 | 159 | Predator's Gambit | `insect_swarm` (rój owadów / bzykanie) | rój brzmi ciągiem (sustain_ratio=0.323, oczekiwane >= 0.4); bzykanie jest wysokie (spectral_centroid_hz=200.500, oczekiwane 1000.0–6000.0) |
| 2.0 | 161 | Dragonscale Boon | `magic_shimmer` (magiczne migotanie / aureola) | magia płynie, nie klika (sustain_ratio=0.024, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.030, oczekiwane >= 0.1) |
| 2.0 | 175 | Caves of Chaos Adventurer | `sword_clash` (starcie stali / cios miecza) | stal błyszczy górą pasma (spectral_centroid_hz=1474.700, oczekiwane >= 2500.0); cios ma energię w górze (high_all=0.256, oczekiwane >= 0.3) |
| 2.0 | 180 | Homicidal Brute | `heavy_footsteps` (ciężkie kroki / kopyta) | kroki mają równy rytm (ioi_cv=0.842, oczekiwane <= 0.6); ciężki krok ma masę w dole (low_all=0.141, oczekiwane >= 0.15) |
| 2.0 | 210 | Fiery Justice | `stone_slide` (osuwisko / tarcie skał) | skały są niskie (spectral_centroid_hz=2538.400, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.130, oczekiwane >= 0.5) |
| 2.0 | 213 | Reclusive Artificer | `heavy_footsteps` (ciężkie kroki / kopyta) | ciężki krok ma masę w dole (low_all=0.001, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=11444.400, oczekiwane <= 2000.0) |
| 2.0 | 214 | Snarling Wolf | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk ma ciało w dole pasma (low_all=0.332, oczekiwane >= 0.45); ryk musi trwać, nie kliknąć (decay_s=0.110, oczekiwane >= 0.4) |
| 2.0 | 225 | Furious Forebear | `arrow_flight` (strzała / świst pocisku) | strzała startuje od razu (attack_s=0.680, oczekiwane <= 0.1); świst siedzi w środku i górze (spectral_centroid_hz=6708.600, oczekiwane 800.0–6000.0) |
| 2.0 | 230 | Horizon Spellbomb | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=8349.600, oczekiwane 800.0–6000.0); mechanizm ma rytm (ioi_cv=1.218, oczekiwane <= 0.8) |
| 2.0 | 233 | Barkform Harvester | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.430, oczekiwane 2.0–12.0); skrzypienie się ciągnie (decay_s=0.140, oczekiwane >= 0.3) |
| 2.0 | 246 | Cuombajj Witches | `bone_snap` (trzask kości / łamanie) | pęknięcie jest natychmiastowe (attack_s=0.060, oczekiwane <= 0.05); trzask kości jest suchy i średni (spectral_centroid_hz=7171.200, oczekiwane 500.0–4000.0) |
| 2.0 | 247 | Subterranean Scout | `arrow_flight` (strzała / świst pocisku) | świst jest szumowy (spectral_flatness=0.038, oczekiwane >= 0.1); świst siedzi w środku i górze (spectral_centroid_hz=301.000, oczekiwane 800.0–6000.0) |
| 2.0 | 251 | Stirring Bard | `folk_music` (muzyka ludowa / taneczna) | taniec ma rytm (onset_count=1, oczekiwane >= 4); rytm taneczny 1–6 Hz (mod_peak_hz=1.090, oczekiwane 1.2–6.0) |
| 2.0 | 254 | Snarespinner | `heavy_footsteps` (ciężkie kroki / kopyta) | ciężki krok ma masę w dole (low_all=0.010, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=8871.400, oczekiwane <= 2000.0) |
| 2.0 | 259 | Kozilek's Predator | `stone_slide` (osuwisko / tarcie skał) | skały są niskie (spectral_centroid_hz=3571.500, oczekiwane <= 2000.0); osuwisko się toczy (decay_s=0.280, oczekiwane >= 0.5) |
| 2.0 | 262 | Angel's Herald | `horn_call` (róg bojowy / sygnał dęty) | róg siedzi nisko w środku (spectral_centroid_hz=1782.500, oczekiwane 200.0–1500.0); sygnał rogu wybrzmiewa (decay_s=0.590, oczekiwane >= 0.6) |
| 2.0 | 279 | Village Rites | `magic_shimmer` (magiczne migotanie / aureola) | magia płynie, nie klika (sustain_ratio=0.060, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.030, oczekiwane >= 0.1) |
| 2.0 | 287 | Sarkhan's Rage | `wing_flutter` (trzepot skrzydeł) | trzepot pulsuje w tempie machania (mod_peak_hz=1.140, oczekiwane 4.0–20.0); trzepot jest szelestem w środku pasma (spectral_centroid_hz=384.400, oczekiwane 800.0–6000.0) |
| 2.0 | 291 | Plague Reaver | `plate_clank` (pancerz / płyty stalowe) | stal pancerza jest jasna (spectral_centroid_hz=402.800, oczekiwane 1000.0–6000.0); brzęk stali ma szum (spectral_flatness=0.017, oczekiwane >= 0.03) |
| 2.0 | 293 | Forever Young | `liquid_pour` (lanie cieczy / bulgot mikstury) | lanie jest ciągłe (sustain_ratio=0.238, oczekiwane >= 0.3); ciecz szumi (spectral_flatness=0.003, oczekiwane >= 0.05) |
| 2.0 | 308 | Greatsword of Tyr | `sword_clash` (starcie stali / cios miecza) | cios stali jest ostry (crest_db=15.820, oczekiwane >= 18.0); stal uderza natychmiast (attack_s=1.470, oczekiwane <= 0.05) |
| 2.0 | 320 | Infectious Horror | `arrow_flight` (strzała / świst pocisku) | strzała startuje od razu (attack_s=0.340, oczekiwane <= 0.1); świst siedzi w środku i górze (spectral_centroid_hz=8599.200, oczekiwane 800.0–6000.0) |
| 2.0 | 322 | Satyr Wayfinder | `heavy_footsteps` (ciężkie kroki / kopyta) | ciężki krok ma masę w dole (low_all=0.032, oczekiwane >= 0.15); krok nie jest cienki (spectral_centroid_hz=4014.400, oczekiwane <= 2000.0) |
| 2.0 | 330 | Invasion of the Giants | `stone_slide` (osuwisko / tarcie skał) | osuwisko się toczy (decay_s=0.080, oczekiwane >= 0.5); osuwisko trwa (content_rel_s=1.220, oczekiwane >= 1.5) |
| 2.0 | 343 | Puppeteer Clique | `temple_bell` (dzwon / dzwonek / gong) | dzwon siedzi w środku pasma (spectral_centroid_hz=5006.500, oczekiwane 400.0–3000.0); dzwon trzyma poziom (sustain_ratio=0.098, oczekiwane >= 0.2) |
| 2.0 | 360 | Inspiration | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3); magia płynie, nie klika (sustain_ratio=0.298, oczekiwane >= 0.3) |
| 2.0 | 385 | Midnight Guard | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.060, oczekiwane 2.0–12.0); skrzypienie siedzi w środku (spectral_centroid_hz=310.500, oczekiwane 700.0–4000.0) |
| 2.0 | 403 | Dementia Bat | `plate_clank` (pancerz / płyty stalowe) | stal pancerza jest jasna (spectral_centroid_hz=9255.500, oczekiwane 1000.0–6000.0); pancerz dzwoni kilkoma płytami (onset_count=1, oczekiwane >= 2) |
| 2.0 | 431 | Delta Bloodflies | `insect_swarm` (rój owadów / bzykanie) | rój brzmi ciągiem (sustain_ratio=0.177, oczekiwane >= 0.4); bzykanie jest wysokie (spectral_centroid_hz=701.400, oczekiwane 1000.0–6000.0) |
| 2.0 | 444 | Colossodon Yearling | `plate_clank` (pancerz / płyty stalowe) | stal pancerza jest jasna (spectral_centroid_hz=349.800, oczekiwane 1000.0–6000.0); brzęk stali ma szum (spectral_flatness=0.029, oczekiwane >= 0.03) |
| 2.0 | 454 | Setessan Skirmisher | `sword_clash` (starcie stali / cios miecza) | cios stali jest ostry (crest_db=17.130, oczekiwane >= 18.0); stal uderza natychmiast (attack_s=0.700, oczekiwane <= 0.05) |
| 2.0 | 457 | Silken Strength | `magic_shimmer` (magiczne migotanie / aureola) | magia płynie, nie klika (sustain_ratio=0.097, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.080, oczekiwane >= 0.1) |
| 2.0 | 465 | Gurmag Drowner | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.126, oczekiwane >= 0.3); magia płynie, nie klika (sustain_ratio=0.246, oczekiwane >= 0.3) |
| 2.0 | 467 | Monastery Flock | `wind_gust` (podmuch wiatru) | podmach narasta (attack_s=0.200, oczekiwane >= 0.3); wiatr siedzi w środku pasma (spectral_centroid_hz=3381.900, oczekiwane 300.0–3000.0) |
| 2.0 | 482 | True Conviction | `sword_clash` (starcie stali / cios miecza) | cios stali jest ostry (crest_db=17.570, oczekiwane >= 18.0); stal uderza natychmiast (attack_s=1.790, oczekiwane <= 0.05) |
| 2.0 | 496 | Shiv's Embrace | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja jest szumowa, nie tonalna (spectral_flatness=0.007, oczekiwane >= 0.04); erupcja się toczy, nie wybucha raz (sustain_ratio=0.198, oczekiwane >= 0.2) |
| 2.0 | 502 | Kin-Tree Nurturer | `liquid_pour` (lanie cieczy / bulgot mikstury) | lanie jest ciągłe (sustain_ratio=0.093, oczekiwane >= 0.3); ciecz siedzi w środku pasma (spectral_centroid_hz=7374.800, oczekiwane 500.0–4000.0) |
| 2.0 | 512 | Vanish from Sight | `plate_clank` (pancerz / płyty stalowe) | stal pancerza jest jasna (spectral_centroid_hz=348.000, oczekiwane 1000.0–6000.0); brzęk stali ma szum (spectral_flatness=0.001, oczekiwane >= 0.03) |
| 2.0 | 513 | Spreading Insurrection | `wing_flutter` (trzepot skrzydeł) | trzepot pulsuje w tempie machania (mod_peak_hz=1.330, oczekiwane 4.0–20.0); trzepot jest szelestem w środku pasma (spectral_centroid_hz=271.000, oczekiwane 800.0–6000.0) |
| 2.0 | 514 | Wolfkin Bond | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk ma ciało w dole pasma (low_all=0.105, oczekiwane >= 0.45); ryk musi trwać, nie kliknąć (decay_s=0.320, oczekiwane >= 0.4) |
| 2.0 | 516 | Tenth District Veteran | `sword_clash` (starcie stali / cios miecza) | stal błyszczy górą pasma (spectral_centroid_hz=582.800, oczekiwane >= 2500.0); cios ma energię w górze (high_all=0.045, oczekiwane >= 0.3) |
| 2.0 | 523 | Segmented Krotiq | `forest_birdsong` (śpiew ptaków) | zawołania ptaków są tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.25); trele są szybkie (mod_peak_hz=1.460, oczekiwane 3.0–22.0) |
| 2.0 | 541 | Bomat Bazaar Barge | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.140, oczekiwane 2.0–12.0); skrzypienie się ciągnie (decay_s=0.250, oczekiwane >= 0.3) |
| 2.0 | 565 | Mana Cylix | `magic_shimmer` (magiczne migotanie / aureola) | magia płynie, nie klika (sustain_ratio=0.040, oczekiwane >= 0.3); magia narasta, nie uderza (attack_s=0.020, oczekiwane >= 0.1) |
| 2.0 | 569 | Manifest Dread | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk siedzi w niskim środku pasma (spectral_centroid_hz=1726.000, oczekiwane 150.0–1600.0); ryk ma ciało w dole pasma (low_all=0.397, oczekiwane >= 0.45) |
| 2.0 | 583 | Kill Shot | `arrow_flight` (strzała / świst pocisku) | strzała startuje od razu (attack_s=0.780, oczekiwane <= 0.1); świst jest szumowy (spectral_flatness=0.000, oczekiwane >= 0.1) |
| 2.0 | 586 | Fourth Bridge Prowler | `plate_clank` (pancerz / płyty stalowe) | stal pancerza jest jasna (spectral_centroid_hz=449.000, oczekiwane 1000.0–6000.0); brzęk stali ma szum (spectral_flatness=0.000, oczekiwane >= 0.03) |
| 2.0 | 587 | Leonin Surveyor | `arrow_flight` (strzała / świst pocisku) | strzała startuje od razu (attack_s=0.550, oczekiwane <= 0.1); świst siedzi w środku i górze (spectral_centroid_hz=10814.200, oczekiwane 800.0–6000.0) |
| 2.0 | 589 | Acidic Slime | `plate_clank` (pancerz / płyty stalowe) | stal pancerza jest jasna (spectral_centroid_hz=8162.300, oczekiwane 1000.0–6000.0); pancerz dzwoni kilkoma płytami (onset_count=1, oczekiwane >= 2) |
| 1.5 | 3 | Nefarious Imp | `fire_crackle` (trzask ognia / żaru) | ogień jest szumowy (spectral_flatness=0.023, oczekiwane >= 0.1) |
| 1.5 | 7 | Mindstab | `psychic_shriek` (przenikliwy jęk / uderzenie psychiczne) | uderzenie psychiczne jest natychmiastowe (attack_s=1.570, oczekiwane <= 0.1) |
| 1.5 | 22 | Titan's Strength | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.002, oczekiwane >= 0.25) |
| 1.5 | 26 | Ember Beast | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.231, oczekiwane >= 0.25) |
| 1.5 | 37 | Howl of the Night Pack | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.000, oczekiwane >= 0.4) |
| 1.5 | 66 | Hooting Mandrills | `stone_slide` (osuwisko / tarcie skał) | skały mają masę w dole (low_all=0.000, oczekiwane >= 0.25) |
| 1.5 | 80 | Merciless Repurposing | `war_machine` (silnik i mechanizm wojennej machiny) | machina dudni dołem (low_all=0.159, oczekiwane >= 0.35) |
| 1.5 | 97 | Great Furnace | `fire_crackle` (trzask ognia / żaru) | ogień strzela wieloma trzaskami (onset_count=2, oczekiwane >= 8) |
| 1.5 | 173 | Awaken the Bear | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.250, oczekiwane >= 0.3) |
| 1.5 | 177 | Dire Fleet Ravager | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.011, oczekiwane >= 0.4) |
| 1.5 | 203 | Golem-Skin Gauntlets | `temple_bell` (dzwon / dzwonek / gong) | dzwon wybrzmiewa (decay_s=0.580, oczekiwane >= 0.8) |
| 1.5 | 243 | Willbender | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.066, oczekiwane >= 0.4) |
| 1.5 | 249 | Feedback | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.058, oczekiwane >= 0.4) |
| 1.5 | 276 | Heap Gate | `forest_birdsong` (śpiew ptaków) | śpiew ptaków jest wysoki (spectral_centroid_hz=594.900, oczekiwane 1500.0–6500.0) |
| 1.5 | 297 | Grizzled Leotau | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.043, oczekiwane >= 0.4) |
| 1.5 | 349 | Enduring Sliver | `plate_clank` (pancerz / płyty stalowe) | stal pancerza jest jasna (spectral_centroid_hz=7004.800, oczekiwane 1000.0–6000.0); płyty gasną szybciej niż dzwon (decay_s=1.350, oczekiwane <= 1.2) |
| 1.5 | 362 | Simian Simulacrum | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.087, oczekiwane >= 0.4) |
| 1.5 | 459 | Prismari Campus | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.222, oczekiwane >= 0.3) |
| 1.5 | 461 | Negate | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.000, oczekiwane >= 0.3) |
| 1.5 | 485 | Moonscarred Werewolf | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie jest tonalne (tonal_frame_fraction=0.162, oczekiwane >= 0.3) |
| 1.5 | 501 | Exterminator Magmarch | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.000, oczekiwane >= 0.3) |
| 1.5 | 517 | Force Away | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie jest natychmiastowe (attack_s=0.350, oczekiwane <= 0.15); uderzenie ma masę (low_all=0.014, oczekiwane >= 0.2) |
| 1.5 | 526 | Canonized in Blood | `plate_clank` (pancerz / płyty stalowe) | pancerz dzwoni kilkoma płytami (onset_count=1, oczekiwane >= 2); płyty gasną szybciej niż dzwon (decay_s=1.530, oczekiwane <= 1.2) |
| 1.5 | 540 | Chittering Rats | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest harmoniczne (tonal_frame_fraction=0.000, oczekiwane >= 0.3) |
| 1.5 | 554 | Cherished Hatchling | `magic_shimmer` (magiczne migotanie / aureola) | magia świeci górą pasma (high_all=0.161, oczekiwane >= 0.4) |
| 1.5 | 561 | Time to Feed | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie jest natychmiastowe (attack_s=0.460, oczekiwane <= 0.15); uderzenie ma masę (low_all=0.035, oczekiwane >= 0.2) |
| 1.5 | 580 | Loporrit Scout | `forest_birdsong` (śpiew ptaków) | śpiew ptaków jest wysoki (spectral_centroid_hz=1473.700, oczekiwane 1500.0–6500.0) |
| 1.5 | 597 | Ichorclaw Myr | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest harmoniczne (tonal_frame_fraction=0.262, oczekiwane >= 0.3) |
| 1.0 | 11 | Sleep of the Dead | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk ma ciało w dole pasma (low_all=0.001, oczekiwane >= 0.45) |
| 1.0 | 12 | Merchant's Dockhand | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | mechanizm ma rytm (ioi_cv=0.817, oczekiwane <= 0.8) |
| 1.0 | 15 | Tellah, Great Sage | `whip_crack` (trzask bicza) | bicz pęka natychmiast (attack_s=0.340, oczekiwane <= 0.03) |
| 1.0 | 17 | Selhoff Occultist | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.270, oczekiwane <= 0.05) |
| 1.0 | 18 | Lotusguard Disciple | `magic_shimmer` (magiczne migotanie / aureola) | magia płynie, nie klika (sustain_ratio=0.287, oczekiwane >= 0.3) |
| 1.0 | 19 | Twiddle | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3) |
| 1.0 | 20 | Jeskai Devotee | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.140, oczekiwane <= 0.05) |
| 1.0 | 40 | Expunge | `plate_clank` (pancerz / płyty stalowe) | stal pancerza jest jasna (spectral_centroid_hz=8052.200, oczekiwane 1000.0–6000.0) |
| 1.0 | 43 | Kor Sanctifiers | `wind_gust` (podmuch wiatru) | wiatr jest szumowy (spectral_flatness=0.000, oczekiwane >= 0.05) |
| 1.0 | 49 | Unstable Frontier | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja się toczy, nie wybucha raz (sustain_ratio=0.023, oczekiwane >= 0.2) |
| 1.0 | 52 | Divest | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=11827.700, oczekiwane 800.0–6000.0) |
| 1.0 | 60 | Thornwood Falls | `water_splash` (plusk / uderzenie w wodę) | plusk zaczyna się od razu (attack_s=0.280, oczekiwane <= 0.1) |
| 1.0 | 82 | Messenger Falcons | `plate_clank` (pancerz / płyty stalowe) | pancerz dzwoni kilkoma płytami (onset_count=1, oczekiwane >= 2) |
| 1.0 | 84 | Garruk's Companion | `fire_crackle` (trzask ognia / żaru) | ogień trwa (content_rel_s=1.490, oczekiwane >= 1.5) |
| 1.0 | 92 | Silumgar Butcher | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=1.770, oczekiwane <= 0.05) |
| 1.0 | 93 | Dispeller's Capsule | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=11582.700, oczekiwane 800.0–6000.0) |
| 1.0 | 96 | Voice of the Vermin | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.010, oczekiwane >= 0.3) |
| 1.0 | 99 | Steelfin Whale | `undead_groan` (jęk / pomruk nieumarłego) | jęk ma ciało w dole (low_all=0.363, oczekiwane >= 0.44) |
| 1.0 | 106 | Mosquito Guard | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest wysokie (spectral_centroid_hz=8116.900, oczekiwane 1000.0–6000.0) |
| 1.0 | 108 | Forced Landing | `whip_crack` (trzask bicza) | trzask bicza jest jasny (spectral_centroid_hz=1779.000, oczekiwane >= 2000.0) |
| 1.0 | 115 | Merfolk Mesmerist | `water_splash` (plusk / uderzenie w wodę) | plusk chlapie górą (high_all=0.200, oczekiwane >= 0.25) |
| 1.0 | 118 | Dire-Strain Brawler | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk ma ciało w dole pasma (low_all=0.000, oczekiwane >= 0.45) |
| 1.0 | 132 | Pilgrim's Eye | `wing_flutter` (trzepot skrzydeł) | trzepot jest szelestem w środku pasma (spectral_centroid_hz=10995.900, oczekiwane 800.0–6000.0) |
| 1.0 | 138 | Join the Dance | `folk_music` (muzyka ludowa / taneczna) | rytm taneczny 1–6 Hz (mod_peak_hz=7.720, oczekiwane 1.2–6.0) |
| 1.0 | 144 | Stensia Innkeeper | `forest_birdsong` (śpiew ptaków) | trele są szybkie (mod_peak_hz=2.360, oczekiwane 3.0–22.0) |
| 1.0 | 151 | Revealing Wind | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.006, oczekiwane >= 0.3) |
| 1.0 | 153 | Balamb Garden, Airborne | `wind_gust` (podmuch wiatru) | wiatr siedzi w środku pasma (spectral_centroid_hz=4895.400, oczekiwane 300.0–3000.0) |
| 1.0 | 162 | Griffin Guide | `horn_call` (róg bojowy / sygnał dęty) | róg siedzi nisko w środku (spectral_centroid_hz=2469.900, oczekiwane 200.0–1500.0) |
| 1.0 | 168 | Steel Sabotage | `stone_slide` (osuwisko / tarcie skał) | osuwisko się toczy (decay_s=0.310, oczekiwane >= 0.5) |
| 1.0 | 169 | Greenwood Sentinel | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.190, oczekiwane <= 0.05) |
| 1.0 | 171 | Grizzled Outcasts | `heavy_footsteps` (ciężkie kroki / kopyta) | ciężki krok ma masę w dole (low_all=0.006, oczekiwane >= 0.15) |
| 1.0 | 176 | Chocobo Kick | `stone_slide` (osuwisko / tarcie skał) | osuwisko się toczy (decay_s=0.130, oczekiwane >= 0.5) |
| 1.0 | 186 | Cogwork Assembler | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=9688.000, oczekiwane 800.0–6000.0) |
| 1.0 | 190 | Goldmeadow Nomad | `wind_gust` (podmuch wiatru) | wiatr jest szumowy (spectral_flatness=0.033, oczekiwane >= 0.05) |
| 1.0 | 198 | Tackle Artist | `heavy_footsteps` (ciężkie kroki / kopyta) | krok nie jest cienki (spectral_centroid_hz=5889.600, oczekiwane <= 2000.0) |
| 1.0 | 207 | Feed the Infection | `arrow_flight` (strzała / świst pocisku) | świst siedzi w środku i górze (spectral_centroid_hz=6473.900, oczekiwane 800.0–6000.0) |
| 1.0 | 216 | Armored Skaab | `plate_clank` (pancerz / płyty stalowe) | płyty pancerza uderzają ostro (crest_db=16.470, oczekiwane >= 17.0) |
| 1.0 | 224 | Immersturm Skullcairn | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.070, oczekiwane <= 0.05) |
| 1.0 | 231 | Anthem of Champions | `arcane_choir` (chór / zaświatowy śpiew bez słów) | chór wybrzmiewa (decay_s=0.620, oczekiwane >= 0.8) |
| 1.0 | 250 | Loxodon Mender | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.080, oczekiwane <= 0.05) |
| 1.0 | 253 | Inspiring Bard | `folk_music` (muzyka ludowa / taneczna) | taniec ma rytm (onset_count=0, oczekiwane >= 4) |
| 1.0 | 257 | Lash of the Balrog | `whip_crack` (trzask bicza) | bicz pęka natychmiast (attack_s=0.040, oczekiwane <= 0.03) |
| 1.0 | 270 | Roiling Regrowth | `stone_slide` (osuwisko / tarcie skał) | osuwisko się toczy (decay_s=0.050, oczekiwane >= 0.5) |
| 1.0 | 272 | Feral Invocation | `arrow_flight` (strzała / świst pocisku) | strzała startuje od razu (attack_s=0.820, oczekiwane <= 0.1) |
| 1.0 | 277 | Spinewoods Paladin | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.190, oczekiwane <= 0.05) |
| 1.0 | 281 | Moonlit Meditation | `water_splash` (plusk / uderzenie w wodę) | plusk chlapie górą (high_all=0.190, oczekiwane >= 0.25) |
| 1.0 | 292 | Rediscover the Way | `wing_flutter` (trzepot skrzydeł) | trzepot pulsuje w tempie machania (mod_peak_hz=1.140, oczekiwane 4.0–20.0) |
| 1.0 | 313 | Faceless Butcher | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=6093.600, oczekiwane 800.0–6000.0) |
| 1.0 | 319 | Call the Mountain Chocobo | `forest_birdsong` (śpiew ptaków) | zawołania ptaków są tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.25) |
| 1.0 | 335 | Gather the Townsfolk | `heavy_footsteps` (ciężkie kroki / kopyta) | ciężki krok ma masę w dole (low_all=0.016, oczekiwane >= 0.15) |
| 1.0 | 345 | Porcelain Legionnaire | `sword_clash` (starcie stali / cios miecza) | stal błyszczy górą pasma (spectral_centroid_hz=2292.600, oczekiwane >= 2500.0) |
| 1.0 | 346 | Necrosquito | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest wysokie (spectral_centroid_hz=10878.700, oczekiwane 1000.0–6000.0) |
| 1.0 | 352 | Evangel of Synthesis | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie się ciągnie (decay_s=0.080, oczekiwane >= 0.3) |
| 1.0 | 370 | Consume Spirit | `arrow_flight` (strzała / świst pocisku) | świst siedzi w środku i górze (spectral_centroid_hz=6308.900, oczekiwane 800.0–6000.0) |
| 1.0 | 375 | Deadly Recluse | `wing_flutter` (trzepot skrzydeł) | trzepot jest szelestem w środku pasma (spectral_centroid_hz=10177.500, oczekiwane 800.0–6000.0) |
| 1.0 | 379 | Swooping Protector | `stone_slide` (osuwisko / tarcie skał) | osuwisko się toczy (decay_s=0.090, oczekiwane >= 0.5) |
| 1.0 | 381 | Caravan Vigil | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie się ciągnie (decay_s=0.060, oczekiwane >= 0.3) |
| 1.0 | 420 | Cellar Door | `heavy_footsteps` (ciężkie kroki / kopyta) | kroki mają równy rytm (ioi_cv=0.724, oczekiwane <= 0.6) |
| 1.0 | 434 | Epic Experiment | `thunder_clap` (grzmot / uderzenie pioruna) | grzmot się toczy (decay_s=0.340, oczekiwane >= 0.5) |
| 1.0 | 435 | Warrior's Sword | `sword_clash` (starcie stali / cios miecza) | cios stali jest ostry (crest_db=16.480, oczekiwane >= 18.0) |
| 1.0 | 453 | Elgaud Inquisitor | `plate_clank` (pancerz / płyty stalowe) | pancerz dzwoni kilkoma płytami (onset_count=1, oczekiwane >= 2) |
| 1.0 | 458 | Trained Arynx | `thunder_clap` (grzmot / uderzenie pioruna) | grzmot jest niski (spectral_centroid_hz=1695.200, oczekiwane <= 800.0) |
| 1.0 | 466 | Basilisk Gate | `plate_clank` (pancerz / płyty stalowe) | pancerz dzwoni kilkoma płytami (onset_count=1, oczekiwane >= 2) |
| 1.0 | 472 | Kazuul's Toll Collector | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.160, oczekiwane <= 0.05) |
| 1.0 | 479 | Impact Tremors | `thunder_clap` (grzmot / uderzenie pioruna) | grzmot uderza (crest_db=15.500, oczekiwane >= 18.0) |
| 1.0 | 497 | Static Net | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=7221.700, oczekiwane 800.0–6000.0) |
| 1.0 | 498 | Fathom Fleet Cutthroat | `water_splash` (plusk / uderzenie w wodę) | plusk zaczyna się od razu (attack_s=0.860, oczekiwane <= 0.1) |
| 1.0 | 503 | Rustwing Falcon | `wind_gust` (podmuch wiatru) | wiatr jest szumowy (spectral_flatness=0.000, oczekiwane >= 0.05) |
| 1.0 | 515 | Warmaker Gunship | `war_machine` (silnik i mechanizm wojennej machiny) | machina musi być słyszalna też na małych głośnikach (mid_up=0.000, oczekiwane >= 0.1) |
| 1.0 | 534 | Terminal Agony | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja jest szumowa, nie tonalna (spectral_flatness=0.000, oczekiwane >= 0.04) |
| 1.0 | 544 | Thraben Valiant | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.400, oczekiwane <= 0.05) |
| 1.0 | 548 | Steelclaw Lance | `plate_clank` (pancerz / płyty stalowe) | pancerz dzwoni kilkoma płytami (onset_count=0, oczekiwane >= 2) |
| 1.0 | 553 | Coat with Venom | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.600, oczekiwane <= 0.05) |
| 1.0 | 566 | Creakwood Safewright | `plate_clank` (pancerz / płyty stalowe) | pancerz dzwoni kilkoma płytami (onset_count=0, oczekiwane >= 2) |
| 1.0 | 568 | Nanoform Sentinel | `robot_servo` (serwo i mechanizm robota) | ton serwa jest stabilny (f0_semitone_std=14.220, oczekiwane <= 4.0) |
| 1.0 | 570 | Dimir Guildgate | `chain_rattle` (grzechot łańcuchów / kolczugi) | łańcuch jest jasny (spectral_centroid_hz=1991.100, oczekiwane >= 2000.0) |
| 1.0 | 572 | Skinbrand Goblin | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk ma ciało w dole pasma (low_all=0.005, oczekiwane >= 0.45) |
| 1.0 | 576 | Akroan Sergeant | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.200, oczekiwane <= 0.05) |
| 1.0 | 594 | Ironclad Slayer | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=1.770, oczekiwane <= 0.05) |
| 1.0 | 596 | Ghirapur Gearcrafter | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=10579.400, oczekiwane 800.0–6000.0) |
| 1.0 | 601 | Exploding Borders | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja jest szumowa, nie tonalna (spectral_flatness=0.002, oczekiwane >= 0.04) |
| 1.0 | 602 | Abstruse Interference | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.3) |
| 1.0 | 603 | Kheru Dreadmaw | `water_splash` (plusk / uderzenie w wodę) | plusk chlapie górą (high_all=0.117, oczekiwane >= 0.25) |
| 1.0 | 612 | Crumb and Get It | `magic_shimmer` (magiczne migotanie / aureola) | migotanie jest tonalne (tonal_frame_fraction=0.006, oczekiwane >= 0.3) |
| 1.0 | 615 | Tah-Crop Skirmisher | `sword_clash` (starcie stali / cios miecza) | cios stali jest ostry (crest_db=16.780, oczekiwane >= 18.0) |
| 0.5 | 14 | Crew Captain | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie ma masę (low_all=0.034, oczekiwane >= 0.2) |
| 0.5 | 70 | Capture Sphere | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie ma masę (low_all=0.114, oczekiwane >= 0.2) |
| 0.5 | 226 | Makeshift Mauler | `robot_servo` (serwo i mechanizm robota) | serwo pracuje ciągiem (sustain_ratio=0.121, oczekiwane >= 0.2) |
| 0.5 | 440 | Your Temple Is Under Attack | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie ma masę (low_all=0.132, oczekiwane >= 0.2) |
| 0.5 | 499 | Vandalize | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie ma masę (low_all=0.118, oczekiwane >= 0.2) |
| 0.5 | 608 | Skymarch Bloodletter | `sword_clash` (starcie stali / cios miecza) | uderzenie ma szumowy transient (spectral_flatness=0.037, oczekiwane >= 0.05) |
| 0.5 | 616 | Act of Treason | `sword_clash` (starcie stali / cios miecza) | uderzenie ma szumowy transient (spectral_flatness=0.042, oczekiwane >= 0.05) |
| 0 | 10 | Servant of the Scale | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 13 | Soulmender | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 16 | Brawler's Plate | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 21 | Pyxis of Pandemonium | `steam_hiss` (syk pary / gazu) | — |
| 0 | 25 | Bonds of Faith | `chain_rattle` (grzechot łańcuchów / kolczugi) | — |
| 0 | 29 | You're Not Alone | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 30 | Containment Protocol | `steam_hiss` (syk pary / gazu) | — |
| 0 | 39 | Brute Force | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 41 | Severed Strands | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 46 | Selesnya Charm | `arrow_flight` (strzała / świst pocisku) | — |
| 0 | 56 | Diplomatic Relations | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 59 | Mysidian Elder | `steam_hiss` (syk pary / gazu) | — |
| 0 | 61 | Stall Out | `glass_shatter` (tłuczenie szkła / kryształu) | — |
| 0 | 71 | Security Rhox | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 72 | Dragon Arch | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 73 | Bladed Sentinel | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 76 | Negate | `glass_shatter` (tłuczenie szkła / kryształu) | — |
| 0 | 77 | Annie Flash, the Veteran | `electric_zap` (wyładowanie / iskra) | — |
| 0 | 94 | Fortify | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 123 | Trade Route Envoy | `door_creak` (skrzypienie drewna / zawiasów) | — |
| 0 | 126 | Bird Admirer | `wing_flutter` (trzepot skrzydeł) | — |
| 0 | 129 | Charismatic Vanguard | `anvil_strike` (uderzenie młota w kowadło) | — |
| 0 | 134 | Waveskimmer Aven | `wind_gust` (podmuch wiatru) | — |
| 0 | 140 | Boros Challenger | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 145 | Clone Shell | `beast_screech` (wrzask / pisk potwora) | — |
| 0 | 155 | Demolish | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 163 | Ghoulcaller's Bell | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 193 | Floodhound | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 194 | Lionheart Maverick | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 196 | Mnemonic Wall | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 206 | High Stride | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 212 | Bloodtithe Harvester | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 229 | Sterling Keykeeper | `chain_rattle` (grzechot łańcuchów / kolczugi) | — |
| 0 | 232 | Goblin Piker | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 236 | Agate Assault | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 239 | Dig Site Inventory | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | — |
| 0 | 278 | Kappa Tech-Wrecker | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 304 | Sagittars' Volley | `arrow_flight` (strzała / świst pocisku) | — |
| 0 | 312 | Goblin Battle Jester | `creature_cackle` (chichot / pokrzykiwanie stworzenia) | — |
| 0 | 315 | Chronic Flooding | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 318 | Gond Gate | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 344 | Pain for All | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 355 | Cathartic Reunion | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 366 | Assert Perfection | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 372 | Dragonbroods' Relic | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 374 | Thistledown Players | `folk_music` (muzyka ludowa / taneczna) | — |
| 0 | 382 | Geological Appraiser | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 387 | Molten Nursery | `volcanic_eruption` (wybuch wulkanu / lawy) | — |
| 0 | 388 | Goblin Picker | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 395 | Unearth | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 396 | Vow of Wildness | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 442 | Cenn's Tactician | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 445 | Locthwain Paladin | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 452 | Omenspeaker | `arcane_choir` (chór / zaświatowy śpiew bez słów) | — |
| 0 | 460 | Ivy Lane Denizen | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 463 | Knockout Maneuver | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 464 | Polluted Dead | `undead_groan` (jęk / pomruk nieumarłego) | — |
| 0 | 469 | Chained Throatseeker | `chain_rattle` (grzechot łańcuchów / kolczugi) | — |
| 0 | 473 | Scion Summoner | `undead_groan` (jęk / pomruk nieumarłego) | — |
| 0 | 483 | Lodestone Needle | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 488 | Carapace Forger | `anvil_strike` (uderzenie młota w kowadło) | — |
| 0 | 491 | Nature's Embrace | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 510 | Angel of the Dawn | `arcane_choir` (chór / zaświatowy śpiew bez słów) | — |
| 0 | 518 | Woolly Loxodon | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 521 | Leafcrown Dryad | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 522 | Hobble | `chain_rattle` (grzechot łańcuchów / kolczugi) | — |
| 0 | 524 | Squire's Lightblade | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 525 | Jill, Shiva's Dominant | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 530 | Grazing Gladehart | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 535 | Lab Rats | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | — |
| 0 | 539 | Silvanus's Invoker | `earth_rumble` (grzmot ziemi / osuwisko skalne) | — |
| 0 | 557 | Kishla Village | `folk_music` (muzyka ludowa / taneczna) | — |
| 0 | 559 | Gaelicat | `beast_screech` (wrzask / pisk potwora) | — |
| 0 | 567 | Jwar Isle Avenger | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 606 | Treefolk Umbra | `heavy_impact` (potężne uderzenie / upadek ciała) | — |
| 0 | 614 | Hunt the Weak | `heavy_impact` (potężne uderzenie / upadek ciała) | — |

Werdykty: {'nie trafiony': 225, 'prawdopodobnie': 120, 'trafiony': 76}

0 pkt = kontrakt archetypu spełniony w całości. ≥ 2 pkt = sample nie jest tym,
co deklaruje scenariusz, i nie da się go rozpoznać z zamkniętymi oczami.
