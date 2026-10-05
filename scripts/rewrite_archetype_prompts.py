#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Przepisywanie promptów na archetypowe — paliwo dla serii naprawczych.

Diagnoza z `docs/STATE.md` (wpis 2026-10-05): dotychczasowe prompty opisywały
**kadry** („green light pouring from a palm, muscles swelling") albo materiały
(„chitin bodies hissing"), więc model improwizował generyczną teksturę. Pilot
r016/r016b pokazał, że prompt zamówiony jako **archetyp** (ryk, chór, jęk,
grzmot, erupcja) wchodzi powtarzalnie i mierzalnie: pięć kart pilota zjechało
z 6,0 / 4,0 / 3,5 / 3,5 / 2,5 pkt na 0.

Ten skrypt zamienia prompt karty na szablon archetypu zadeklarowanego w polu
`archetype`. Szablon jest napisany pod kontrakt z `audit_archetype_match.py`
(dzwon ma dzwonić i wybrzmiewać, skrzypienie ma falować, osuwisko musi mieć
masę w dole), a nie pod opis fabuły — fabuła zostaje w `title` i w karcie,
a sample ma być rozpoznawalnym dźwiękiem.

Kilka archetypów jest z natury muzycznych (dzwon, chór, róg, muzyka ludowa) —
dostają `music_allowed: true` i nazwany instrument, bo walidator wymaga, żeby
wyjątek muzyczny miał źródło w kadrze.

Użycie:
    python scripts/rewrite_archetype_prompts.py --ids 515,7,312            # podgląd
    python scripts/rewrite_archetype_prompts.py --ids 515,7,312 --apply
    python scripts/rewrite_archetype_prompts.py --worst-per-family 2 \
        --families door_creak,temple_bell --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from audit_archetype_match import CONTRACTS  # noqa: E402
from elevenlabs_sample_scout import api_payload  # noqa: E402

DURATION = 4.0
NO_M = "No music, no speech, no ambience bed."   # dla archetypów niemuzykalnych
NO_S = "No speech, no ambience bed."             # dla archetypów muzycznych

# archetyp: (prompt EN, opis PL, muzyka?)
TEMPLATES: dict[str, tuple[str, str, bool]] = {
    "temple_bell": ("A single bronze temple bell struck once and left to ring: a deep "
                    "struck tone with warm shimmering partials, ringing on and slowly fading. "
                    + NO_S,
                    "uderzenie dzwonu: jeden głęboki ton brązu z ciepłymi alikwotami, dzwoni i powoli gaśnie", True),
    "door_creak": ("A heavy old wooden door pushed slowly open: a long wavering creak of dry "
                   "wood and iron hinge, held and groaning, ending in a soft wooden clunk. " + NO_M,
                   "skrzypienie ciężkich drzwi: długie falujące skrzypienie suchego drewna i zawiasu", False),
    "stone_slide": ("A rockslide tearing loose: heavy boulders grinding and tumbling down, stone "
                    "cracking, rubble cascading with a deep rumble underneath, ending in one "
                    "heavy slam. " + NO_M,
                    "osuwisko: głazy mielą się i staczają, kamień pęka, gruz sypie się z głębokim pomrukiem", False),
    "magic_shimmer": ("An arcane spell igniting: a rising crystalline shimmer, a bright tonal hum "
                      "with sparkling high overtones, swelling and holding steady. " + NO_M,
                      "magia: narastające krystaliczne migotanie z jasnym tonem i iskrzącymi alikwotami", False),
    "creature_roar": ("A large beast roaring: one long throaty harmonic roar, low and swelling, "
                      "held full and ending in a forceful snort. " + NO_M,
                      "ryk bestii: jeden długi gardłowy harmoniczny ryk, narastający i trzymany", False),
    "creature_cackle": ("A goblin cackling: a series of sharp mocking cackles, four or five rapid "
                        "bursts, high and jeering. " + NO_M,
                        "chichot: seria ostrych kpiących chichotów, cztery-pięć szybkich wybuchów", False),
    "undead_groan": ("A plague zombie moaning deep in its chest: a slow guttural groan in a low "
                     "register, wet rattle in the throat, held long and sagging at the end. " + NO_M,
                     "jęk nieumarłego: powolny niski gardłowy pomruk z mokrym rzężeniem, trzymany długo", False),
    "beast_screech": ("A monster shrieking: one piercing high screech with a hard immediate "
                      "attack, tearing and wavering. " + NO_M,
                      "wrzask potwora: jeden przenikliwy wysoki krzyk z twardym natychmiastowym atakiem", False),
    "psychic_shriek": ("A psychic scream: an instant piercing tonal shriek inside the skull, a "
                       "high sustained tone with a hard immediate attack. " + NO_M,
                       "uderzenie psychiczne: natychmiastowy przenikliwy tonalny krzyk w czaszce", False),
    "war_machine": ("A war machine's engine: a deep diesel-like rumble spooling up with heavy "
                    "rhythmic pounding and grinding gears. " + NO_M,
                    "machina wojenna: głęboki pomruk silnika z ciężkim rytmicznym biciem i zgrzytem przekładni", False),
    "robot_servo": ("A robot's servos engaging: a smooth continuous mechanical whirr with a "
                    "steady hum and a precise click at the end. " + NO_M,
                    "serwo robota: ciągłe gładkie warczenie mechanizmu z równym brzęczeniem i kliknięciem", False),
    "forest_birdsong": ("Forest birds calling: several distinct whistled bird songs and chirps, "
                        "one after another, clear and tonal. " + NO_M,
                        "ptaki w lesie: kilka wyraźnych gwizdanych zawołań i treli, jedno po drugim", False),
    "folk_music": ("Village folk music: a fiddle playing a lively dance tune over a hand drum, "
                   "warm and rustic. " + NO_S,
                   "muzyka ludowa: skrzypce grają żywą taneczną melodię nad bębenkiem", True),
    "arcane_choir": ("A prophecy from the heavens: a wordless mystical choir chant swelling in "
                     "sustained harmonious voices, with a soft bell shimmer over it. " + NO_S,
                     "chór proroctwa: bezsłowny mistyczny śpiew narastający w zgodnych głosach", True),
    "horn_call": ("A war horn sounding: one long brazen call rising and holding, with a breathy "
                  "edge at the start. " + NO_S,
                  "róg bojowy: jeden długi mosiężny sygnał, narastający i trzymany", True),
    "earth_rumble": ("An earth elemental rising: heavy boulders grinding against each other and "
                     "cracking, rubble tumbling down in a rolling cascade, a deep rumble "
                     "underneath, ending in one heavy stone slam. " + NO_M,
                     "grzmot ziemi: głazy mielą się i pękają, gruz stacza się kaskadą, głęboki pomruk", False),
    "volcanic_eruption": ("A volcano erupting close by: molten lava tearing out of the ground in "
                          "a sustained roar, rocks cracking and bursting apart, dense steam "
                          "hissing over the cooling flow. " + NO_M,
                          "erupcja: lawa wyrywa się z ziemi w jednostajnym huku, skały pękają, para syczy", False),
    "thunder_clap": ("A thunderclap overhead: one sharp crack followed by a deep rolling rumble "
                     "that fades slowly. " + NO_M,
                     "grzmot: jedno ostre trzaśnięcie i głęboki toczący się pomruk", False),
    "wind_gust": ("A strong gust of wind rushing past: a swelling roar of air that builds and "
                  "fades, with a low whistle through it. " + NO_M,
                  "podmuch wiatru: narastający huk powietrza z niskim gwizdem", False),
    "wing_flutter": ("A great winged creature taking off: three powerful wingbeats with a deep "
                     "leathery flap and a rush of air. " + NO_M,
                    "trzepot skrzydeł: trzy mocne uderzenia szerokich skrzydeł z podmuchem powietrza", False),
    "insect_swarm": ("A swarm of insects hovering close: a dense sustained buzzing of beating "
                     "wings, rising and holding. " + NO_M,
                     "rój owadów: gęste ciągłe bzyczenie bijących skrzydeł", False),
    "fire_crackle": ("A bonfire burning: dense crackling and popping of dry wood with a low roar "
                     "of flame underneath. " + NO_M,
                     "ognisko: gęste trzaski i strzały suchego drewna z niskim hukiem płomienia", False),
    "steam_hiss": ("A jet of steam venting: a strong sustained hiss of high-pressure gas escaping, "
                   "swelling then easing off. " + NO_M,
                   "syk pary: mocny ciągły syk uchodzącego gazu pod ciśnieniem", False),
    "water_splash": ("A heavy object hitting deep water: one big splash with a spray of droplets "
                     "and a low submerged boom. " + NO_M,
                     "plusk: ciężki przedmiot uderza w głęboką wodę, chlapie i dudni pod powierzchnią", False),
    "liquid_pour": ("Thick liquid pouring from a flask: a steady glugging pour with bubbling and "
                    "splashing into a pool. " + NO_M,
                    "lanie cieczy: równy bulgoczący strumień z pluskiem w zbiorniku", False),
    "arrow_flight": ("An arrow shot past the listener: a sharp bowstring twang followed by a fast "
                     "fletched whoosh cutting through the air. " + NO_M,
                     "strzała: ostre szarpnięcie cięciwy i szybki świst przelatującego pocisku", False),
    "heavy_footsteps": ("Heavy armored footsteps: three weighty boot steps on stone, each with a "
                        "metallic clank of plate armor. " + NO_M,
                        "ciężkie kroki: trzy ważkie kroki w zbroi po kamieniu z brzękiem płyt", False),
    "sword_clash": ("Swords clashing: two sharp steel strikes ringing out with a bright metallic "
                    "shimmer. " + NO_M,
                    "starcie mieczy: dwa ostre uderzenia stali z jasnym metalicznym pobrzmieniem", False),
    "plate_clank": ("Plate armor shifting: heavy steel plates clanking and scraping against each "
                    "other with a dull weight. " + NO_M,
                    "pancerz: ciężkie stalowe płyty dzwonią i szorują o siebie", False),
    "chain_rattle": ("Chains rattling: a bright cascade of metal links shaking and clinking "
                     "together. " + NO_M,
                    "łańcuchy: jasna kaskada ogniw dzwoniących o siebie", False),
    "glass_shatter": ("Glass shattering: one sharp breaking crash with many tinkling shards "
                      "falling and scattering. " + NO_M,
                      "tłuczenie szkła: ostry trzask pękania i dzwoniące spadające odłamki", False),
    "mechanism_click": ("A clockwork mechanism turning: a series of crisp ratcheting clicks in a "
                        "steady rhythm. " + NO_M,
                        "mechanizm zegarowy: seria suchych zapadkowych kliknięć w równym rytmie", False),
    "bone_snap": ("A bone breaking: one dry hard snap of a thick bone splitting, with a wet "
                  "tearing tail. " + NO_M,
                  "trzask kości: jedno suche twarde pęknięcie grubej kości", False),
    "whip_crack": ("A whip cracking: one explosive crack of a lash breaking the air, sharp and "
                   "instant. " + NO_M,
                   "trzask bicza: jeden eksplozywny strzał bicza łamiącego powietrze", False),
    "electric_zap": ("An electric discharge: a sharp crackling zap with snapping sparks and a "
                     "short buzzing tail. " + NO_M,
                     "wyładowanie: ostry trzaskający błysk z przeskokiem iskier", False),
    "heavy_impact": ("A heavy blow landing: one deep weighted impact with a dull thud and a low "
                     "tail. " + NO_M,
                     "ciężkie uderzenie: jeden głęboki ważki cios z głuchym łomotem", False),
    "anvil_strike": ("A smith's hammer on an anvil: two hard ringing strikes of steel on steel "
                     "with a bright metallic ring. " + NO_M,
                     "kowadło: dwa twarde dzwoniące uderzenia młota w stal", False),
}


# ---------------------------------------------------------------------------
# Profile akustyczne wewnątrz archetypu.
#
# Powód: runda r017a pokazała, że dwa karty z tym samym szablonem (`168` i `382`,
# oba `stone_slide`) wyszły z kosinusem 0,9676 i żadna kombinacja wariantów nie
# zeszła poniżej 0,95. Sama klauzula z tytułem nie różnicuje dźwięku — model
# i tak gra ten sam archetyp. Dlatego duże rodziny mają 2-3 profile: inny
# materiał, inna skala, inne tempo. Karta dostaje profil po `int(id) % N`,
# czyli rodzina rozkłada się na kilka różnych dźwięków zamiast jednego.
# ---------------------------------------------------------------------------
PROFILES: dict[str, list[tuple[str, str]]] = {
    # r025: cztery rodziny miały tylko TEMPLATE, więc wszystkie ich karty
    # dostawały ten sam prompt i psuły się grupowo (4x forest_birdsongs za niskie,
    # 4x mechanism_click za jasne, 3x robot_servo bez tonu, 3x plate_clank bez
    # kilku płyt). Profile różnicują zdarzenie i celują w zmierzoną wadę.
    "forest_birdsong": [
        ("Small songbirds chattering in a hedge: many quick high-pitched chirps and thin "
         "whistles, bright and piercing, one after another. " + NO_M,
         "drobne ptaki w żywopłocie: wiele szybkich wysokich świergotów i cienkich gwizdów"),
        ("A dawn chorus of tiny birds: rapid tinkling high chirps, sharp and silvery, "
         "overlapping in a fast flurry. " + NO_M,
         "poranny chór drobnych ptaków: szybkie wysokie dzwoniące świergoty"),
        ("A flock of finches taking off: a burst of high squeaking chirps and short sharp "
         "calls, light and bright. " + NO_M,
         "stado zięb zrywa się: seria wysokich piszczących świergotów i ostrych zawołań"),
    ],
    "mechanism_click": [
        ("A clockwork mechanism turning: a series of crisp mid-pitched ratchet clicks in a "
         "steady rhythm, dry and woody rather than hissy. " + NO_M,
         "mechanizm zegarowy: seria ostrych klików ze środka pasma, suchych, nie syczących"),
        ("A small gear train stepping: firm mid-range clicks of steel on brass, evenly spaced, "
         "each with a soft body. " + NO_M,
         "mała przekładnia: równe kliki stali na mosiądzu ze środka pasma"),
        ("A winding ratchet handle turning: repeated low-medium clicks with a dull mechanical "
         "body, in a regular rhythm. " + NO_M,
         "korba zapadkowa: powtarzalne kliki z niskiego środka pasma, głuche i rytmiczne"),
    ],
    "robot_servo": [
        ("A robot servo holding one pure tone: a smooth sustained harmonic hum at a single "
         "unwavering pitch, like a struck tuning fork, with two short precise clicks. " + NO_M,
         "serwo robota trzyma jeden czysty ton jak kamerton, z dwoma klikami"),
        ("A robot arm rotating under power: a steady harmonic motor whine at one constant "
         "pitch, clean and tonal, with three crisp clicks as it moves. " + NO_M,
         "ramię robota obraca się: równy harmoniczny pisk silnika o stałej wysokości, trzy kliki"),
        ("A drone's servo locking into place: a clear sustained electronic tone at a fixed "
         "pitch, even and tonal, punctuated by two precise clicks. " + NO_M,
         "serwo drona blokuje się: czysty ciągły ton o stałej wysokości, dwa kliki"),
    ],
    "plate_clank": [
        ("Plate armor shifting: three separate heavy steel plates clanking one after another, "
         "each hit distinct and sharply struck. " + NO_M,
         "zbroja płytowa się przesuwa: trzy osobne ciężkie płyty dzwonią jedna po drugiej"),
        ("A knight's harness rattling: several steel plates knocking together in quick "
         "succession, bright but weighty, with a scrape between. " + NO_M,
         "opierzenie rycerza grzechocze: kilka płyt stalowych uderza kolejno, z przesunięciem"),
        ("Armored shoulders turning: two or three dull steel clanks with body, spaced apart, "
         "ending in a short scrape of plates. " + NO_M,
         "pancerne ramiona się obracają: dwa-trzy głuche stalowe brzęki i krótki zgrzyt"),
    ],
    "stone_slide": [
        ("A rockslide tearing loose: heavy boulders grinding and tumbling down, stone cracking, "
         "rubble cascading with a deep rumble underneath, ending in one heavy slam. " + NO_M,
         "osuwisko: głazy mielą się i staczają, gruz sypie się z głębokim pomrukiem"),
        ("One huge boulder splitting apart and rolling down a gravel slope: a deep crack, then a "
         "slow grinding roll of stone over loose rock, heavier and heavier. " + NO_M,
         "głaz pęka i toczy się po żwirze, coraz ciężej"),
        ("A cliff face collapsing: a long scrape of rock sliding off stone, shards snapping, then "
         "a spreading crash of debris settling. " + NO_M,
         "ściana skalna osuwa się: długi zgrzyt, trzaski i opadający gruz"),
    ],
    # r025: trzy karty miały mod_peak 1,0-1,4 Hz (próg 2-12) i decay 0,06-0,08 s
    # (próg >= 0,3) — skrzypienie było jednostajne i urywało się. Profile mówią
    # wprost o wielokrotnym falowaniu i o tym, że dźwięk ma trwać sekundami.
    "door_creak": [
        ("A heavy old wooden door pushed slowly open: a long creak that rises and falls several "
         "times over seconds, groaning and wavering, ending in a soft wooden clunk. " + NO_M,
         "ciężkie drzwi: długie skrzypienie falujące w górę i w dół przez kilka sekund"),
        ("A rusted iron gate swinging on dry hinges: a thin metallic squeal whose pitch wobbles "
         "up and down repeatedly as the gate moves, drawn out, ending with a clank. " + NO_M,
         "zardzewiała brama: pisk zawiasów wielokrotnie chwiejący się w wysokości"),
        ("A stiff wooden lid forced open slowly: a groaning creak that pulses and wavers, "
         "stretching out for seconds before it settles. " + NO_M,
         "sztywne wieko: pulsujące falujące skrzypienie ciągnące się sekundami"),
    ],
    # r025: skrajne profile dawały centroid 243 Hz („deep bronze") i 7538 Hz
    # („small silver handbell") przy oknie 400-3000. Wszystkie trzy profile
    # celują teraz w środek pasma — dzwon średniej wielkości.
    "temple_bell": [
        ("A medium bronze temple bell struck once and left to ring: a mid-range struck tone with "
         "warm shimmering partials, ringing on steadily. " + NO_S,
         "średni dzwon brązowy: ton ze środka pasma z ciepłymi alikwotami"),
        ("A chapel bell tolled once: a clear mid-pitched ring with a slow shimmering decay, "
         "holding its level. " + NO_S,
         "dzwon kaplicy: czysty dźwięk ze środka pasma z powolnym wybrzmieniem"),
        ("An iron monastery bell hit with a hammer: a mid struck note with a dark hum, sustained "
         "and even, ringing for seconds. " + NO_S,
         "żelazny dzwon klasztorny: uderzony ton ze środka pasma, równy i długi"),
    ],
    "magic_shimmer": [
        ("An arcane spell igniting: a rising crystalline shimmer, a bright tonal hum with "
         "sparkling high overtones, swelling and holding steady. " + NO_M,
         "magia: narastające krystaliczne migotanie z jasnym tonem"),
        ("A protective ward unfolding: a soft glassy chime cluster rising in pitch, thin and "
         "delicate, hovering at the end. " + NO_M,
         "bariera: delikatny szklany klaster dzwonków wznoszący się w górę"),
        ("Dark magic pooling: a low throbbing hum with a gritty warped overtone, swelling slowly "
         "and staying. " + NO_M,
         "mroczna magia: niski pulsujący pomruk z chropawym przydźwiękiem"),
    ],
    # r025: low_all 0,000 / 0,000 / 0,044 przy progu >= 0,45 (p85 korpusu) —
    # ryki nie miały w sobie dołu. Profile mówią o piersiowym pomruku i
    # basowym dudnieniu pod spodem, nie tylko o „głębokim" ryku.
    "creature_roar": [
        ("A huge beast roaring from deep in its chest: a low roaring growl with heavy bass body "
         "underneath, swelling and held full. " + NO_M,
         "ryk z piersi: niski gardłowy ryk z ciężkim basowym ciałem"),
        ("A monster's close-up roar: a guttural bellow with a thick low-frequency rumble beneath "
         "it, sustained and swelling. " + NO_M,
         "ryk potwora z bliska: gardłowy ryk z gęstym niskim dudnieniem"),
        ("A giant predator roaring: a very deep roaring call with a strong low end and a raspy "
         "harmonic edge, held long. " + NO_M,
         "ryk drapieżnika: bardzo niski zew z mocnym dołem i chropawą krawędzią"),
    ],
    # r025: obie karty-wzorce mówiły o „gwiździe", więc model oddał czysty ton
    # (tonal 1,0, flatness 0,000-0,002 przy progu >= 0,05). Wiatr ma być
    # turbulentnym szumem — profile mówią o hissing/turbulent/breath, nie o gwizdaniu.
    "wind_gust": [
        ("A strong gust of wind rushing past: a broad hissing rush of turbulent air, noisy and "
         "airy, swelling up and fading away. " + NO_M,
         "podmuch wiatru: szeroki szumiący pęd turbulentnego powietrza"),
        ("Wind tearing through bare branches: a gusting wash of air with a ragged hiss, rising "
         "and falling in waves. " + NO_M,
         "wiatr w gałęziach: podmuchy szumiącego powietrza falujące w górę i w dół"),
        ("A cold squall hitting a stone wall: a wide band of breathy wind noise, turbulent and "
         "even, surging then easing off. " + NO_M,
         "zimna nawałnica: szerokie pasmo oddechowego szumu wiatru"),
    ],
    "wing_flutter": [
        ("A great winged creature taking off: three powerful wingbeats with a deep leathery flap "
         "and a rush of air. " + NO_M,
         "trzepot skrzydeł: trzy mocne uderzenia szerokich skrzydeł"),
        ("A flock of small birds taking off at once: a rapid burst of many small wingbeats, "
         "fluttering and thinning out. " + NO_M,
         "stado ptaków zrywa się: szybka seria drobnych uderzeń skrzydeł"),
    ],
    # r025: low_all 0,016 / 0,017 / 0,139 przy progu >= 0,15 — „metallic clank"
    # w profilu ciągnął energię w górę pasma. Profile mówią o głębokim łupnięciu
    # i drżeniu ziemi, a rytm ma być równy (ioi_cv <= 0,6, onset >= 3).
    "heavy_footsteps": [
        ("Heavy armored footsteps on stone: three weighty steps, each a deep thud with a low "
         "ground shake, evenly spaced. " + NO_M,
         "ciężkie kroki po kamieniu: trzy głębokie łupnięcia z drżeniem ziemi, równo"),
        ("A huge creature walking: three slow massive thuds on packed earth, deep and heavy, "
         "each shaking the ground. " + NO_M,
         "kroki olbrzyma: trzy powolne masywne łomoty w ubitą ziemię"),
        ("A giant marching: four heavy stomps with a booming low end, evenly timed, each landing "
         "with full weight. " + NO_M,
         "marsz olbrzyma: cztery ciężkie stąpnięcia z dudniącym dołem, równym rytmem"),
    ],
    "undead_groan": [
        ("A plague zombie moaning deep in its chest: a slow guttural groan in a low register, wet "
         "rattle in the throat, held long and sagging at the end. " + NO_M,
         "jęk nieumarłego: powolny niski gardłowy pomruk z mokrym rzężeniem"),
        ("A wight hissing and moaning: a dry rasping moan with a breathy rattle, rising once and "
         "dropping away. " + NO_M,
         "upiór: suchy chrapliwy jęk z oddechowym rzężeniem"),
    ],
    "earth_rumble": [
        ("An earth elemental rising: heavy boulders grinding against each other and cracking, "
         "rubble tumbling down in a rolling cascade, a deep rumble underneath, ending in one "
         "heavy stone slam. " + NO_M,
         "grzmot ziemi: głazy mielą się i pękają, gruz stacza się kaskadą, głęboki pomruk"),
        ("The ground splitting open: one deep cracking split through soil and rock, debris "
         "falling into the gap, then a long low grind settling. " + NO_M,
         "ziemia pęka: głębokie rozdarcie gruntu, gruz wpada w szczelinę, niski zgrzyt"),
        ("A great stone slab shifting: a slow heavy grind of rock on rock, gathering weight, "
         "then one deep settling thud. " + NO_M,
         "kamienna płyta się przesuwa: powolny ciężki zgrzyt i głębokie osadzenie"),
    ],
    "volcanic_eruption": [
        ("A volcano erupting close by: molten lava tearing out of the ground in a sustained roar, "
         "rocks cracking and bursting apart, dense steam hissing over the cooling flow. " + NO_M,
         "erupcja: lawa wyrywa się z ziemi, skały pękają, para syczy"),
        ("A lava flow collapsing into the sea: a violent burst of steam with a deep roar and "
         "sharp crackling of cooling rock. " + NO_M,
         "lawa wpada do morza: gwałtowny wybuch pary z hukiem i trzaskiem"),
    ],
}

# Rotacja długości: różne czasy trwania dodatkowo rozróżniają odciski kart
# z tej samej rodziny. Zamawiamy 3,5-4,5 s, choć okno akceptacji to 2-5 s
# (decyzja właściciela z 2026-10-05: „dobre 2 sekundy są lepsze niż złe 4"):
# model i tak często oddaje mniej, a zapas daje selektorowi z czego wybierać.
DURATIONS = (4.0, 4.5, 3.5)

# Karty, których prompt musi zostać ręczny (fabuła narzuca konkretne źródło).
OVERRIDES: dict[str, tuple[str, str, bool]] = {
    "312": ("A goblin jester cackling: a series of sharp mocking cackles, five rapid jeering "
            "bursts, high and cruel. " + NO_M,
            "chichot błazna: seria ostrych kpiących chichotów, pięć szybkich wybuchów", False),
    "557": ("Village folk music: a fiddle playing a lively dance tune over a hand drum, warm and "
            "rustic, feet stamping the beat. " + NO_S,
            "wiejska muzyka: skrzypce grają żywą taneczną melodię nad bębenkiem, stopy wybijają rytm", True),

    # --- poprawki po rundzie r017a (audyt pokazał, co model zrobił nie tak) ---
    # 515: wyszedł centroid 90 Hz i flagi muffled/boomy/dull — sam infrabas.
    "515": ("A war gunship hovering low: heavy rotor blades chopping the air with a sharp slap, "
            "a high turbine whine over it and a bright metallic rattle of the hull. " + NO_M,
            "gunship: ciężkie łopaty wirnika tną powietrze, nad nimi świst turbiny i jasny grzechot kadłuba", False),
    # 35: tylko 2,53 s i 2,0 pkt.
    "35": ("A winged creature hovering close: five steady deep wingbeats with a leathery flap "
           "and a rush of air, filling the whole take. " + NO_M,
           "skrzydła z bliska: pięć równych głębokich uderzeń skrzydeł z podmuchem powietrza", False),
    # 62: boomy/dull, centroid 118 Hz.
    "62": ("A wounded bird struggling to fly: four uneven wingbeats with a dry papery flap and a "
           "soft thump as it lands. " + NO_M,
           "ranny ptak: cztery nierówne uderzenia suchych skrzydeł i miękki łomot przy lądowaniu", False),
    # 112: boomy/dull — podmuch zjechał w dół pasma.
    "112": ("A flurry of wings in a narrow street: a fast rush of many small wingbeats with a "
            "bright rustle of feathers and a swirl of air. " + NO_M,
            "furkot skrzydeł w zaułku: szybki pęd wielu drobnych skrzydeł z jasnym szelestem piór", False),
    # 6: profil 0 dał 2,5 pkt — twardszy atak i puls w dole.
    "6": ("A lawmage's ward snapping into place: a crisp glassy chime cluster with a firm low "
          "pulse underneath, bright and holding. " + NO_M,
          "bariera prawodawcy: szklisty klaster dzwonków z twardym niskim pulsem", False),
    # --- poprawki po rundach r018/r019: prompt pod konkretną wadę z audytu ---
    # 49: low_all 0,449 przy progu 0,50 — więcej masy w dole.
    "49": ("The ground splitting between two worlds: one deep cracking split through soil and "
           "rock in the deep bass, debris falling into the gap, then a long low grinding "
           "settle. " + NO_M,
           "ziemia pęka między światami: głębokie rozdarcie gruntu w niskim paśmie i długi zgrzyt", False),
    # 168: centroid 1378 Hz przy progu 900 — niżej.
    "168": ("A deep rockslide low in the mountains: huge boulders grinding and rolling in the "
            "bass, rubble cascading down, a heavy low rumble underneath. " + NO_M,
            "głębokie osuwisko w górach: głazy mielą się i toczą w niskim paśmie, ciężki pomruk", False),
    # 493: centroid 2223 Hz przy progu 2000 — niżej.
    "493": ("A stone wall cracking apart: one deep crack, then heavy chunks of rock tumbling "
            "down onto a stone floor, low and weighty. " + NO_M,
            "kamienny mur pęka: głęboki trzask i ciężkie bryły spadają na kamienną posadzkę", False),
    # 298: tonal_frame_fraction 0,32 przy progu 0,50 — czystszy ton.
    "298": ("A heavy iron alarm bell tolled by rope: one clear struck tone that rings steadily "
            "and purely with a warm hum, no rattling, no clatter. " + NO_S,
            "żelazny dzwon alarmowy: jeden czysty ton dzwoniący równo i ciepło, bez grzechotania", True),
    # 521: mod_peak 1,82 Hz przy progu 3,0 — szybsze trele.
    "521": ("Forest birds at dawn: quick rapid chirps and short whistled trills, several birds "
            "answering fast, bright and light. " + NO_M,
            "ptaki o świcie: szybkie ćwierknięcia i krótkie trele, kilka ptaków odpowiada prędko", False),
    "343": ("A bronze temple bell struck once and left to ring: a deep struck tone with warm "
            "shimmering partials ringing on and on, filling the whole take. " + NO_S,
            "dzwon z brązu uderzony raz: głęboki ton z ciepłymi alikwotami dzwoni bez końca", True),

    # --- druga poprawka po r020: audyt pokazał, że model nie dowozi ---
    # 7: atak 0,90 s przy progu 0,10 — wymuszamy brak narastania.
    "7": ("A mind stab: a sudden piercing shriek at full volume from the very first "
          "millisecond, no fade-in at all, a high tonal scream cut off short. " + NO_M,
          "pchnięcie psychiczne: nagły przenikliwy krzyk od pierwszej milisekundy, bez narastania", False),
    # 31 i 456: kontrakt chce harmonicznego bzyczenia, a „suchy szelest" dał szum 8,5-9,3 kHz.
    "31": ("A dense swarm of flies hovering close: a low thick buzzing drone, the steady "
           "harmonic hum of thousands of wings, sustained and even. " + NO_M,
           "gęsty rój much: niski gruby bzyk, równe harmoniczne brzęczenie tysięcy skrzydeł", False),
    "456": ("A swarm rising from shattered porcelain: one bright crack of ceramic, then a "
            "thick low buzzing drone of many wings lifting off, harmonic and sustained. " + NO_M,
            "rój wzbija się z potłuczonej porcelany: trzask i gruby niski bzyk wielu skrzydeł", False),
    # 568: tonal_frame_fraction 0,000 — serwo wyszło szumowe, ma być ton o stałej wysokości.
    # r023 (kliki przecinające ton) dał najwyżej onset 1 i stonizowany ton
    # (0,767 / f0_std 3,3) — model rozstrzyga konflikt ton-vs-klik kosztem tonu.
    # Próg klików jest dobrze skalibrowany: mediana korpusu 4, a pozostałe karty
    # robot_servo mają 2-29, więc to realna wada, nie zły próg.
    # r024 odwraca hierarchię: rytm jest zdarzeniem głównym, ton — tłem.
    "568": ("A robot servo working in a steady rhythm: a precise mechanical ticking, "
            "two clicks per second, each click crisp and separate, over a continuous "
            "harmonic whine held at one unwavering pitch. " + NO_M,
            "serwo robota pracuje równym rytmem: precyzyjne mechaniczne tikanie, dwa kliki "
            "na sekundę, każdy osobny, nad ciągłym harmonicznym brzęczeniem o stałej wysokości",
            False),
    # 317: 2,23 s — cztery uderzenia mają wypełnić cały czas.
    "317": ("A large iron church bell tolled in alarm: four heavy strikes in a steady rhythm, "
            "each one ringing out fully, filling the whole take from start to finish. " + NO_S,
            "kościelny dzwon na alarm: cztery ciężkie uderzenia równym rytmem, każde w pełni wybrzmiewa", True),

    # 459: profil 0 dał 1,5 pkt i dull — jaśniejszy ryk z echem.
    "459": ("A great beast roaring across a campus courtyard: a huge bright roaring call with a "
            "raspy harmonic edge and a short stone echo. " + NO_M,
            "ryk przez dziedziniec: potężny jasny ryk z chrapliwą harmoniczną krawędzią i krótkim echem", False),
}


TAILS = (NO_M, NO_S)


def card_clause(row: dict) -> str:
    """Klauzula rozróżniająca kartę, doklejona do szablonu archetypu.

    Bez niej wszystkie karty jednej rodziny dostałyby identyczny prompt, a wtedy
    zamiast rozpoznawalnych dźwięków powstałaby nowa fala bliźniaków (audyt
    flaguje kosinus >= 0,95). Archetyp zostaje na początku promptu — model
    najmocniej waży początek — a karta dokłada własne źródło z dotychczasowego
    opisu i tytuł.
    """
    old = (row.get("prompt") or "").strip()
    for tail in TAILS:
        old = old.replace(tail, "")
    phrase = old.split(":")[0].strip().rstrip(".")
    if len(phrase) > 70:
        phrase = phrase[:70].rsplit(" ", 1)[0]
    title = (row.get("title") or "").strip()
    if not phrase:
        return f" Signature sound of the card {title}."
    return f" Signature sound of the card {title} — {phrase}."


PROFILE_SHIFT = 0


FILL_TAKE = False


def build(row: dict) -> dict | None:
    sid = str(row["story_id"])
    archetype = row.get("archetype")
    if sid in OVERRIDES:
        prompt, pl, music = OVERRIDES[sid]
    elif archetype in PROFILES:
        choices = PROFILES[archetype]
        prompt, pl = choices[(int(sid) + PROFILE_SHIFT) % len(choices)]
        music = TEMPLATES[archetype][2] if archetype in TEMPLATES else False
    elif archetype in TEMPLATES:
        prompt, pl, music = TEMPLATES[archetype]
    else:
        return None
    tail = NO_S if music else NO_M
    clause = card_clause(row)
    body = prompt
    for t_ in TAILS:
        body = body.replace(t_, "")
    if FILL_TAKE:
        prompt = (f"{body.rstrip()} {clause.strip()} The sound fills the whole take, "
                  f"start to finish, with no silence at the beginning or the end. {tail}")
    else:
        prompt = f"{body.rstrip()} {clause.strip()} {tail}"
    return {"prompt": prompt, "sample_scenario": pl, "music_allowed": music,
            "duration_seconds": DURATION if sid in OVERRIDES else DURATIONS[int(sid) % len(DURATIONS)]}


def latest_archetype_audit() -> Path:
    """Najnowszy zrzut `archetype-match-*.json` w data/samples/.

    Powód: --worst czyta punktacje kontraktu z tego pliku. Gdy domyślnie
    wskazywał stary zrzut, transza naprawcza trafiała w karty już naprawione
    (r021: 8 z 20 wybranych kart miało wtedy werdykt „trafiony"), a nowe
    generacje potrafiły je zepsuć (`383`: 0 -> 3,0 pkt).
    """
    cands = sorted((ROOT / "data/samples").glob("archetype-match-*.json"),
                   key=lambda f: (f.stat().st_mtime, f.name))
    return cands[-1] if cands else ROOT / "data/samples/archetype-match-2026-10-05-strong.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", type=Path, default=ROOT / "data/samples/scenarios.jsonl")
    ap.add_argument("--audit", type=Path, default=latest_archetype_audit(),
                    help="JSON audytu archetypów; domyślnie NAJNOWSZY w data/samples/. "
                         "Twardo zaszyta ścieżka do starego zrzutu kosztowała w r021 "
                         "24 generacje: --worst wybrał 8 kart już wtedy trafionych.")
    ap.add_argument("--ids", default="", help="lista ID po przecinku")
    ap.add_argument("--families", default="", help="archetypy do wyboru, po przecinku")
    ap.add_argument("--worst", type=int, default=0,
                    help="ile najgorszych kart z całego katalogu (wg punktacji kontraktu)")
    ap.add_argument("--worst-per-family", type=int, default=0,
                    help="ile najgorszych kart z każdego archetypu (wg punktacji kontraktu)")
    ap.add_argument("--batch", default="r017a")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--profile-shift", type=int, default=0,
                    help="przesuń wybór profilu akustycznego (do ponowień kart, "
                         "które zlały się z inną kartą)")
    ap.add_argument("--fill-take", action="store_true",
                    help="dopisz wymaganie wypełnienia całego czasu (dla kart za krótkich)")
    args = ap.parse_args()

    global PROFILE_SHIFT, FILL_TAKE
    PROFILE_SHIFT, FILL_TAKE = args.profile_shift, args.fill_take
    rows = [json.loads(l) for l in args.scenarios.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_id = {str(r["story_id"]): r for r in rows}
    wanted: list[str] = [s.strip() for s in args.ids.split(",") if s.strip()]

    if args.worst:
        scores = json.loads(args.audit.read_text(encoding="utf-8"))["results"]
        fams = {f.strip() for f in args.families.split(",") if f.strip()}
        cand = [r for r in scores
                if r["verdict"] != "trafiony" and r["id"] not in wanted
                and (r["archetype"] in TEMPLATES or r["archetype"] in PROFILES)
                and (not fams or r["archetype"] in fams)]
        cand.sort(key=lambda r: (-r["score"], int(r["id"])))
        wanted += [r["id"] for r in cand[:args.worst]]

    if args.worst_per_family:
        scores = json.loads(args.audit.read_text(encoding="utf-8"))["results"]
        fams = {f.strip() for f in args.families.split(",") if f.strip()}
        per: dict[str, list] = {}
        for r in scores:
            if r["verdict"] == "trafiony" or r["id"] in wanted:
                continue
            if fams and r["archetype"] not in fams:
                continue
            if r["archetype"] not in TEMPLATES:
                continue
            per.setdefault(r["archetype"], []).append(r)
        for arch, items in sorted(per.items()):
            items.sort(key=lambda r: (-r["score"], int(r["id"])))
            wanted += [r["id"] for r in items[:args.worst_per_family]]

    if args.limit:
        wanted = wanted[:args.limit]

    changed, missing = 0, []
    for sid in wanted:
        row = by_id.get(sid)
        if row is None:
            missing.append(f"{sid}: nie ma w scenariuszach")
            continue
        patch = build(row)
        if patch is None:
            missing.append(f"{sid}: brak szablonu dla archetypu {row.get('archetype')!r}")
            continue
        text = api_payload({**row, **patch}, 0.35)["text"]
        print(f"{sid:>4} {row.get('title','')[:24]:<24} {(row.get('archetype') or '-'):<18} "
              f"{len(text)}/450 znaków{'  [muzyka]' if patch['music_allowed'] else ''}")
        print(f"     {patch['prompt'][:150]}")
        if args.apply:
            row.update(patch)
            row["batch"] = args.batch
            row["status"] = "ready"
            changed += 1
    for m in missing:
        print("  pomijam:", m)

    if args.apply:
        args.scenarios.write_text(
            "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
            encoding="utf-8")
        print(f"zapisano {changed} promptów (batch {args.batch}) do {args.scenarios}")
    else:
        print(f"podgląd: {len(wanted)} kart, użyj --apply żeby zapisać")
    print(f"generacje: {2 * len(wanted)} wariantów = {2 * len(wanted) * 40} kredytów (2 warianty na kartę)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
