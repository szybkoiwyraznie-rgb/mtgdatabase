# Audyt rozpoznawalności — czy sample brzmi jak archetyp

Sprawdzono **180** sampli z zadeklarowanym polem `archetype`.

| Wynik | ID | Karta | Archetyp | Co nie gra |
|---|---|---|---|---|
| 1.5 | 31 | Carrion Call | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest harmoniczne (tonal_frame_fraction=0.023, oczekiwane >= 0.3) |
| 1.0 | 3 | Nefarious Imp | `fire_crackle` (trzask ognia / żaru) | trzaski są jasne (spectral_centroid_hz=7264.400, oczekiwane 1000.0–6000.0) |
| 1.0 | 17 | Selhoff Occultist | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.140, oczekiwane <= 0.1) |
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
| 1.0 | 292 | Rediscover the Way | `wind_gust` (podmuch wiatru) | podmuch płynie (sustain_ratio=0.258, oczekiwane >= 0.3) |
| 1.0 | 303 | Blanchwood Prowler | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=17.390, oczekiwane 2.0–12.0) |
| 1.0 | 381 | Caravan Vigil | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.100, oczekiwane 2.0–12.0) |
| 1.0 | 382 | Geological Appraiser | `earth_rumble` (grzmot ziemi / osuwisko skalne) | grzmot się toczy (decay_s=0.310, oczekiwane >= 0.8) |
| 1.0 | 456 | Crawling Chorus | `insect_swarm` (rój owadów / bzykanie) | bzykanie jest wysokie (spectral_centroid_hz=9314.700, oczekiwane 1000.0–6000.0) |
| 1.0 | 492 | Secluded Steppe | `wind_gust` (podmuch wiatru) | wiatr siedzi w środku pasma (spectral_centroid_hz=6780.700, oczekiwane 300.0–3000.0) |
| 1.0 | 493 | Skyclave Geopede | `stone_slide` (osuwisko / tarcie skał) | osuwisko się toczy (decay_s=0.130, oczekiwane >= 0.5) |
| 1.0 | 496 | Shiv's Embrace | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja jest szumowa, nie tonalna (spectral_flatness=0.000, oczekiwane >= 0.04) |
| 1.0 | 513 | Spreading Insurrection | `wind_gust` (podmuch wiatru) | wiatr siedzi w środku pasma (spectral_centroid_hz=3616.300, oczekiwane 300.0–3000.0) |
| 1.0 | 531 | Disa the Restless | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie się ciągnie (decay_s=0.070, oczekiwane >= 0.3) |
| 1.0 | 537 | Kor Cartographer | `door_creak` (skrzypienie drewna / zawiasów) | skrzypienie faluje (mod_peak_hz=1.640, oczekiwane 2.0–12.0) |
| 1.0 | 553 | Coat with Venom | `sword_clash` (starcie stali / cios miecza) | stal uderza natychmiast (attack_s=0.600, oczekiwane <= 0.1) |
| 1.0 | 568 | Nanoform Sentinel | `robot_servo` (serwo i mechanizm robota) | ton serwa jest stabilny (f0_semitone_std=4.380, oczekiwane <= 4.0) |
| 1.0 | 610 | Gearsmith Prodigy | `mechanism_click` (zegarowy mechanizm / zamek / zapadka) | klik jest suchy i jasny (spectral_centroid_hz=9641.500, oczekiwane 800.0–6000.0) |
| 1.0 | 611 | Lifecrafter's Gift | `robot_servo` (serwo i mechanizm robota) | robot klika i pracuje (onset_count=1, oczekiwane >= 2) |
| 0.5 | 345 | Porcelain Legionnaire | `sword_clash` (starcie stali / cios miecza) | uderzenie ma szumowy transient (spectral_flatness=0.042, oczekiwane >= 0.05) |
| 0.5 | 435 | Warrior's Sword | `sword_clash` (starcie stali / cios miecza) | uderzenie ma szumowy transient (spectral_flatness=0.028, oczekiwane >= 0.05) |
| 0.5 | 608 | Skymarch Bloodletter | `sword_clash` (starcie stali / cios miecza) | uderzenie ma szumowy transient (spectral_flatness=0.007, oczekiwane >= 0.05) |
| 0 | 1 | Dunland Crebain | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 2 | Coralhelm Guide | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 4 | Mystic Sanctuary | `water_splash` (plusk / uderzenie w wodę) | — |
| 0 | 5 | Academy Journeymage | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 6 | Azorius Justiciar | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 7 | Mindstab | `psychic_shriek` (przenikliwy jęk / uderzenie psychiczne) | — |
| 0 | 9 | Toll of the Invasion | `wind_gust` (podmuch wiatru) | — |
| 0 | 12 | Merchant's Dockhand | `robot_servo` (serwo i mechanizm robota) | — |
| 0 | 15 | Tellah, Great Sage | `whip_crack` (trzask bicza) | — |
| 0 | 16 | Brawler's Plate | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 18 | Lotusguard Disciple | `magic_shimmer` (magiczne migotanie / aureola) | — |
| 0 | 20 | Jeskai Devotee | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 23 | Brightwood Tracker | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 26 | Ember Beast | `stone_slide` (osuwisko / tarcie skał) | — |
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
| 0 | 145 | Clone Shell | `beast_screech` (wrzask / pisk potwora) | — |
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
| 0 | 317 | Village Bell-Ringer | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 323 | Quandrix Campus | `liquid_pour` (lanie cieczy / bulgot mikstury) | — |
| 0 | 335 | Gather the Townsfolk | `heavy_footsteps` (ciężkie kroki / kopyta) | — |
| 0 | 343 | Puppeteer Clique | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 344 | Pain for All | `sword_clash` (starcie stali / cios miecza) | — |
| 0 | 347 | Pristine Talisman | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 352 | Evangel of Synthesis | `forest_birdsong` (śpiew ptaków) | — |
| 0 | 355 | Cathartic Reunion | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 358 | Frontline War-Rager | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 370 | Consume Spirit | `arrow_flight` (strzała / świst pocisku) | — |
| 0 | 372 | Dragonbroods' Relic | `stone_slide` (osuwisko / tarcie skał) | — |
| 0 | 383 | Supernatural Stamina | `door_creak` (skrzypienie drewna / zawiasów) | — |
| 0 | 387 | Molten Nursery | `volcanic_eruption` (wybuch wulkanu / lawy) | — |
| 0 | 396 | Vow of Wildness | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 431 | Delta Bloodflies | `insect_swarm` (rój owadów / bzykanie) | — |
| 0 | 434 | Epic Experiment | `war_machine` (silnik i mechanizm wojennej machiny) | — |
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
| 0 | 548 | Steelclaw Lance | `plate_clank` (pancerz / płyty stalowe) | — |
| 0 | 557 | Kishla Village | `folk_music` (muzyka ludowa / taneczna) | — |
| 0 | 558 | White Mage's Staff | `temple_bell` (dzwon / dzwonek / gong) | — |
| 0 | 559 | Gaelicat | `beast_screech` (wrzask / pisk potwora) | — |
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
| 0 | 616 | Act of Treason | `sword_clash` (starcie stali / cios miecza) | — |

Werdykty: {'prawdopodobnie': 33, 'trafiony': 147}

0 pkt = kontrakt archetypu spełniony w całości. ≥ 2 pkt = sample nie jest tym,
co deklaruje scenariusz, i nie da się go rozpoznać z zamkniętymi oczami.
