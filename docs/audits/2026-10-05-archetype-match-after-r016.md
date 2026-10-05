# Audyt rozpoznawalności — czy sample brzmi jak archetyp

Sprawdzono **13** sampli z zadeklarowanym polem `archetype`.

| Wynik | ID | Karta | Archetyp | Co nie gra |
|---|---|---|---|---|
| 2.5 | 464 | Polluted Dead | `undead_groan` (jęk / pomruk nieumarłego) | jęk jest niski (spectral_centroid_hz=1096.200, oczekiwane 120.0–1000.0); jęk ma ciało w dole (low_all=0.160, oczekiwane >= 0.55) |
| 2.5 | 515 | Warmaker Gunship | `war_machine` (silnik i mechanizm wojennej machiny) | machina dudni dołem (low_all=0.241, oczekiwane >= 0.35); machina nie jest cienka (spectral_centroid_hz=2641.200, oczekiwane <= 2600.0) |
| 1.5 | 7 | Mindstab | `psychic_shriek` (przenikliwy jęk / uderzenie psychiczne) | to ton, nie szum (tonal_frame_fraction=0.012, oczekiwane >= 0.3) |
| 1.0 | 312 | Goblin Battle Jester | `creature_cackle` (chichot / pokrzykiwanie stworzenia) | chichot jest ostry i wysoki (spectral_centroid_hz=6099.500, oczekiwane 700.0–4500.0) |
| 1.0 | 387 | Molten Nursery | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja jest szumowa, nie tonalna (spectral_flatness=0.000, oczekiwane >= 0.04) |
| 1.0 | 521 | Leafcrown Dryad | `forest_birdsong` (śpiew ptaków) | zawołania ptaków są tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.25) |
| 1.0 | 539 | Silvanus's Invoker | `earth_rumble` (grzmot ziemi / osuwisko skalne) | grzmot musi być słyszalny też na małych głośnikach, nie sam infrabas (mid_up=0.063, oczekiwane >= 0.1) |
| 1.0 | 557 | Kishla Village | `folk_music` (muzyka ludowa / taneczna) | muzyka musi potrwać (content_rel_s=1.980, oczekiwane >= 2.0) |
| 0.5 | 463 | Knockout Maneuver | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie ma masę (low_all=0.250, oczekiwane >= 0.25) |
| 0.5 | 568 | Nanoform Sentinel | `robot_servo` (serwo i mechanizm robota) | serwo pracuje ciągiem (sustain_ratio=0.133, oczekiwane >= 0.2) |
| 0 | 145 | Clone Shell | `beast_screech` (wrzask / pisk potwora) | — |
| 0 | 396 | Vow of Wildness | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | — |
| 0 | 452 | Omenspeaker | `arcane_choir` (chór / zaświatowy śpiew bez słów) | — |

Werdykty: {'nie trafiony': 2, 'prawdopodobnie': 8, 'trafiony': 3}

0 pkt = kontrakt archetypu spełniony w całości. ≥ 2 pkt = sample nie jest tym,
co deklaruje scenariusz, i nie da się go rozpoznać z zamkniętymi oczami.
