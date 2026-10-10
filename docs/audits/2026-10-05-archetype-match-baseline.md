# Audyt rozpoznawalności — czy sample brzmi jak archetyp

Sprawdzono **13** sampli z zadeklarowanym polem `archetype`.

| Wynik | ID | Karta | Archetyp | Co nie gra |
|---|---|---|---|---|
| 6.0 | 452 | Omenspeaker | `arcane_choir` (chór / zaświatowy śpiew bez słów) | chór jest harmoniczny (tonal_frame_fraction=0.440, oczekiwane >= 0.45); chór ma wyraźną wysokość (voiced_fraction=0.056, oczekiwane >= 0.25); chór płynie, nie pulsuje (sustain_ratio=0.040, oczekiwane >= 0.35); chór wybrzmiewa (decay_s=0.090, oczekiwane >= 0.8); chór siedzi w środku pasma (spectral_centroid_hz=8621.100, oczekiwane 250.0–2800.0) |
| 4.0 | 464 | Polluted Dead | `undead_groan` (jęk / pomruk nieumarłego) | jęk jest niski (spectral_centroid_hz=3553.800, oczekiwane 120.0–1000.0); jęk się ciągnie (decay_s=0.150, oczekiwane >= 0.6); jęk ma ciało w dole (low_all=0.013, oczekiwane >= 0.55) |
| 3.5 | 396 | Vow of Wildness | `creature_roar` (ryk / porykiwanie dużego zwierzęcia) | ryk musi być harmoniczny (voiced) (voiced_fraction=0.253, oczekiwane >= 0.3); ryk ma ciało w dole pasma (low_all=0.001, oczekiwane >= 0.45); ryk musi trwać, nie kliknąć (decay_s=0.220, oczekiwane >= 0.4) |
| 3.5 | 539 | Silvanus's Invoker | `earth_rumble` (grzmot ziemi / osuwisko skalne) | grzmot ziemi jest w dole pasma (low_all=0.099, oczekiwane >= 0.5); grzmot ziemi jest niski (spectral_centroid_hz=4284.000, oczekiwane <= 900.0); grzmot się toczy (decay_s=0.040, oczekiwane >= 0.8) |
| 2.5 | 387 | Molten Nursery | `volcanic_eruption` (wybuch wulkanu / lawy) | erupcja ma masę w dole (low_all=0.003, oczekiwane >= 0.35); erupcja się toczy (decay_s=0.300, oczekiwane >= 0.8) |
| 2.5 | 515 | Warmaker Gunship | `war_machine` (silnik i mechanizm wojennej machiny) | machina dudni dołem (low_all=0.241, oczekiwane >= 0.35); machina nie jest cienka (spectral_centroid_hz=2641.200, oczekiwane <= 2600.0) |
| 1.5 | 7 | Mindstab | `psychic_shriek` (przenikliwy jęk / uderzenie psychiczne) | to ton, nie szum (tonal_frame_fraction=0.012, oczekiwane >= 0.3) |
| 1.0 | 312 | Goblin Battle Jester | `creature_cackle` (chichot / pokrzykiwanie stworzenia) | chichot jest ostry i wysoki (spectral_centroid_hz=6099.500, oczekiwane 700.0–4500.0) |
| 1.0 | 521 | Leafcrown Dryad | `forest_birdsong` (śpiew ptaków) | zawołania ptaków są tonalne (tonal_frame_fraction=0.000, oczekiwane >= 0.25) |
| 1.0 | 557 | Kishla Village | `folk_music` (muzyka ludowa / taneczna) | muzyka musi potrwać (content_rel_s=1.980, oczekiwane >= 2.0) |
| 0.5 | 463 | Knockout Maneuver | `heavy_impact` (potężne uderzenie / upadek ciała) | uderzenie ma masę (low_all=0.250, oczekiwane >= 0.25) |
| 0.5 | 568 | Nanoform Sentinel | `robot_servo` (serwo i mechanizm robota) | serwo pracuje ciągiem (sustain_ratio=0.133, oczekiwane >= 0.2) |
| 0 | 145 | Clone Shell | `beast_screech` (wrzask / pisk potwora) | — |

Werdykty: {'nie trafiony': 6, 'prawdopodobnie': 6, 'trafiony': 1}

0 pkt = kontrakt archetypu spełniony w całości. ≥ 2 pkt = sample nie jest tym,
co deklaruje scenariusz, i nie da się go rozpoznać z zamkniętymi oczami.
