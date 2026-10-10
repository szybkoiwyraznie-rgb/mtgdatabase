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
    # r026: kolejne rodziny z jednym TEMPLATE, w których karty psuja sie grupowo.
    # sword_clash: zdajace karty maja attack 0,00-0,08 s, gubiace 0,14-1,77 s -
    #   wiec natychmiastowy cios jest osiagalny, trzeba go nazwac wprost.
    # insect_swarm: centroid 8,1-12,4 kHz przy oknie 1000-6000 i tonal 0,0 -
    #   "buzzing of beating wings" daje szum; kotwiczymy w niskim harmonicznym bzyku.
    "sword_clash": [
        ("Swords clashing: two steel blades struck together with no build-up, full force at the "
         "very first instant, a bright ringing shimmer over a gritty scrape of metal. " + NO_M,
         "miecze się zderzają: dwa stalowe ciosy bez zamachu, pełną siłą w pierwszej chwili"),
        ("A sword parried mid-swing: an instant hard steel impact, sharp and immediate, with a "
         "spray of metallic noise and a bright ring. " + NO_M,
         "miecz zbity w pół ciosu: natychmiastowe twarde uderzenie stali z chmurą metalicznego szumu"),
        ("Two blades meeting edge to edge: a sudden violent steel strike landing at once, with a "
         "harsh gritty ring and a short scrape. " + NO_M,
         "dwa ostrza schodzą się krawędziami: nagły gwałtowny cios z chropawym brzękiem"),
    ],
    "insect_swarm": [
        ("A dense swarm of bees hovering close: a low thick buzzing drone, a steady harmonic hum "
         "of many wings, sustained and even. " + NO_M,
         "gęsty rój pszczół z bliska: niski gruby bzyk, równe harmoniczne brzęczenie"),
        ("A cloud of flies over a carcass: a deep droning buzz with a warm harmonic core, "
         "holding steadily without a break. " + NO_M,
         "chmara much nad padliną: głęboki bzyk z ciepłym harmonicznym środkiem, bez przerwy"),
        ("A swarm settling on wood: a low continuous buzzing hum, mid-pitched and harmonic, "
         "thick and unbroken. " + NO_M,
         "rój osiada na drewnie: niski ciągły harmoniczny bzyk, gęsty i nieprzerwany"),
    ],
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
    # r026: water_splash mial high_all 0,044-0,095 przy progu 0,25 (plusk byl
    # niski, bez rozbryzgu), a war_machine low_all 0,001-0,010 przy progu 0,35
    # (silnik bez dołu). Kontrakt war_machine chce tez mid_up >= 0,1, wiec
    # profile trzymaja mechaniczny srodek nad basem.
    "water_splash": [
        ("A heavy object hitting deep water: one big splash with a bright hiss of spray and "
         "droplets scattering, then a low submerged boom. " + NO_M,
         "ciężki przedmiot wpada do wody: duży plusk z jasnym sykiem rozbryzgu i głuchym echem"),
        ("A body slamming into a pool: a sharp crack of water with a wide hissing spray flying "
         "up, followed by a deep gurgle. " + NO_M,
         "ciało wpada do basenu: ostry trzask wody z szerokim syczącym rozbryzgiem i bulgotem"),
        ("A stone thrown into deep water: a bright splashing burst with a fine spray hissing "
         "down, then a low thump underneath. " + NO_M,
         "kamień rzucony w głęboką wodę: jasny wybuch plusku z drobnym syczącym rozbryzgiem"),
    ],
    "war_machine": [
        ("A war machine's engine: a deep diesel rumble with heavy bass, spooling up over slow "
         "rhythmic pounding and a gritty mechanical mid-range. " + NO_M,
         "silnik machiny wojennej: głęboki basowy pomruk diesla z rytmicznym łomotem"),
        ("A siege engine's motor: a very low throbbing engine note with thick bass underneath "
         "and heavy metal clanking beats on top. " + NO_M,
         "silnik machiny oblężniczej: bardzo niski pulsujący ton z grubym basem i łomotem"),
        ("An armored vehicle idling: a deep guttural engine rumble dominated by low "
         "frequencies, with a gritty metallic knocking over it. " + NO_M,
         "opancerzony pojazd na biegu: głęboki gardłowy pomruk z niskim basem i stukotem"),
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
    "224": (
        "A blade striking plate in the first instant: one hard crack of the blade, "
        "then two long rasping cuts of steel drawn along steel, then a third crack, "
        "the shearing to the end. " + NO_M,
        "ostrze uderza w płytowy pancerz w pierwszej chwili: jeden twardy trzask klingi, potem dwa długie zgrzyty stali o stal, potem trzeci trzask, cięcie do końca",
        False,
    ),
    "312": ("A goblin jester cackling: a series of sharp mocking cackles, five rapid jeering "
            "bursts, high and cruel. " + NO_M,
            "chichot błazna: seria ostrych kpiących chichotów, pięć szybkich wybuchów", False),
    "333": (
        "Bronze gates clashing shut in the first instant: one hard crack of the gates, then a second crack, then a third crack, then a fourth crack, the striking to the end. " + NO_M,
        "brązowe wrota zamykają się w pierwszej chwili: jeden twardy trzask wrót, potem drugi, potem trzeci, potem czwarty, uderzanie do końca",
        False,
    ),
    "340": ("An edifice coming alive: a smooth continuous servo whirr with a steady hum, held unbroken across the whole take, and two precise clicks of steel legs locking out.",
            "stalowy mechanizm się rozkłada: jeden ciągły jęk serva na jednej stałej wysokości, potem cztery nogi z kliknięciem, jęk do końca", False),
    "338": ("A colossal giant rising from the sea: one crash of water thrown up, then a stone pier struck apart, then spray and rubble raining down into the water, the crashing to the end.",
            "olbrzym wynurza się i druzgocze kamienny port: wyrzut wody, głazy pirsu rozbijane, gruz wpadający do wody, do końca", False),
    "334": ("A scythe striking a metal tree in the first instant: one hard crack of the blade, then two long rasping cuts of steel through copper, shearing to the end.",
            "podniebna kosa uderza w metalowy pień w pierwszej chwili: twarde uderzenie, dwa długie zgrzyty stali przez miedź, trzecie cięcie, do końca", False),
    "332": ("A raptor folding its wings: one short whistle of air, then a crack of lightning, then a roll of thunder that stays loud for over a second before dying away into silence before the end.",
            "gromoraptor składa skrzydła: krótki świat powietrza, trzask błyskawicy, potem grzmot trwający ponad sekundę i cichnący przed końcem", False),
    "329": ("Obsidian plates lifting: a whine of stone sounding from the very first moment and swelling, then a beam released with a glassy shimmer, then two more whines, the shimmer to the end.",
            "płyty obsydianu unoszą się: narastający jęk kamienia, potem snop energii ze szklistym połyskiem, jeszcze dwa jęki, połysk do końca", False),
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
    # --- poprawki po rundach r018/r019: prompt pod konkretną wadę z audytu ---
    # 49: low_all 0,449 przy progu 0,50 — więcej masy w dole.
    # 168: centroid 1378 Hz przy progu 900 — niżej.
    # 493: centroid 2223 Hz przy progu 2000 — niżej.
    "493": ("A stone wall cracking: one deep crack, then heavy rock chunks tumbling and grinding to a stop with a long slow rumble that fades over more than a second.",
            "kamienny mur pęka: jedno głębokie pęknięcie, potem ciężkie bryły staczają się z długim powolnym pomrukiem gasnącym ponad sekundę", False),
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
    "7": (
        "Three mind stabs in a row, the first at full volume with no fade-in: a "
        "piercing tonal scream held and wavering each time, pitched in the upper "
        "middle of the range. " + NO_M,
        "trzy pchnięcia psychiczne jedno po drugim, pierwsze na pełnym poziomie bez narastania: za każdym razem przenikliwy tonalny krzyk trzymany i falujący, umiejscowiony w górnej połowie środka pasma",
        False,
    ),
    # 31 i 456: kontrakt chce harmonicznego bzyczenia, a „suchy szelest" dał szum 8,5-9,3 kHz.
    # 568: tonal_frame_fraction 0,000 — serwo wyszło szumowe, ma być ton o stałej wysokości.
    # r023 (kliki przecinające ton) dał najwyżej onset 1 i stonizowany ton
    # (0,767 / f0_std 3,3) — model rozstrzyga konflikt ton-vs-klik kosztem tonu.
    # Próg klików jest dobrze skalibrowany: mediana korpusu 4, a pozostałe karty
    # robot_servo mają 2-29, więc to realna wada, nie zły próg.
    # r024 odwraca hierarchię: rytm jest zdarzeniem głównym, ton — tłem.
    "567": (
        "Claws striking chitin armour in the first instant: one hard crack of the "
        "plates, then a second crack, then a third crack, then a fourth crack, the "
        "striking to the end. " + NO_M,
        "szpony uderzają w chitynowy pancerz w pierwszej chwili: jeden twardy trzask płyt, potem drugi trzask, potem trzeci, potem czwarty, uderzanie do końca",
        False,
    ),
    "568": ("A robot servo working: one precise mechanical tone at an absolutely fixed pitch that never bends or wavers, with two crisp clicks per second over it.",
            "serwo robota pracuje: jeden precyzyjny mechaniczny ton o absolutnie stałej wysokości, bez żadnego odchylania, z dwoma klikami na sekundę", False),
    # 317: 2,23 s — cztery uderzenia mają wypełnić cały czas.
    "317": ("A large iron church bell tolled in alarm: four heavy strikes in a steady rhythm, "
            "each one ringing out fully, filling the whole take from start to finish. " + NO_S,
            "kościelny dzwon na alarm: cztery ciężkie uderzenia równym rytmem, każde w pełni wybrzmiewa", True),

    # 459: profil 0 dał 1,5 pkt i dull — jaśniejszy ryk z echem.
    "459": ("A great beast roaring across a campus courtyard: a huge bright roaring call with a "
            "raspy harmonic edge and a short stone echo. " + NO_M,
            "ryk przez dziedziniec: potężny jasny ryk z chrapliwą harmoniczną krawędzią i krótkim echem", False),

    # --- r026: dwie rodziny, w których profil rodzinny nie wystarczył ---
    # mechanism_click: profile r025 mówiły „mid-pitched, dry and woody rather
    # than hissy", a centroid i tak wyszedł 7,7-10,6 kHz przy oknie 800-6000.
    # Model czyta „click" jako jasny trzask, więc nazywamy wprost czego NIE ma być.
    "52": ("A clockwork mechanism turning: a brass cog releasing a wooden peg, then a lever dropping, then a ratchet catching, eight wooden and brass knocks at an even spacing, "
           "the mechanism working on to the end. " + NO_M,
           "mechanizm zegarowy: mosiężne koło zwalnia drewniany kołek, potem dźwignia i zapadka, osiem stuków w równym odstępie do końca", False),
    "132": ("A small gear train stepping: firm low knocks of wood on brass, dark and round, "
            "evenly spaced, without any high-pitched snap. " + NO_M,
            "przekładnia: niskie głuche stuki drewna o mosiądz, ciemne i bez wysokiego trzasku", False),
    "213": ("A winding ratchet turning slowly: repeated dull low clicks with a soft body, "
            "mid-low pitched, no hiss and no bright edge. " + NO_M,
            "zapadka kręcona powoli: powtarzalne głuche niskie kliki bez syku i jasnej krawędzi", False),
    # magic_shimmer: `5` i `607` trafiły na profil „mroczna magia" (niski pulsujący
    # pomruk) i wyszły z centroidem 93-104 Hz przy wymaganym high_all >= 0,4.
    "607": ("A protective ward unfolding: a thin glassy chime cluster high in pitch, delicate "
            "and sparkling, hovering bright at the end. " + NO_M,
            "bariera się rozwija: cienki szklisty klaster dzwonków wysoko, delikatny i błyszczący", False),
    # --- r027: 45 kart, w których karta obiecuje powtarzalne zdarzenie,
    # a sample miał jedno (treść 0,41-2,04 s). Prompt nazywa liczbę
    # powtórzeń wprost, bo model inaczej gra jedno zdarzenie i resztę ciszy.
    # Dla 7 kart z archetypem dopisane wymogi kontraktu (atak w pierwszej
    # chwili, chropawy brzęk, niska podstawa).
    "10": ("A column of warriors marching past: eight to ten heavy boot strikes on hard ground in a steady even cadence filling the whole take, with one crisp banner cloth snap above them.",
            "kolumna wojowników maszeruje: osiem-dziesięć ciężkich kroków równym rytmem przez cały sample, z trzaskiem proporca", False),
    "111": ("A band of silk slowly ripped in two: a long fibrous tearing that runs across the whole take, with four or five successive fibre snaps as the tear advances.",
            "pasmo jedwabiu powoli rozdarte na dwoje: długi włóknisty dźwięk przez cały sample z kolejnymi pęknięciami włókien", False),
    "114": ("A rolled parchment dropping into thick mud: one soft plop, then a row of five fat bubbles rising and bursting one after another.",
            "zwinięty pergamin wpada w bagno: miękki plusk, a potem szereg pięciu grubych bąbli kolejno pękających", False),
    "131": ("Three separate water drops falling from a still surface, evenly spaced about half a second apart, each with a clean glassy plink and its own small ripple.",
            "trzy osobne krople spadają z tafli wody w równych odstępach, każda z czystym szklistym dźwiękiem i własnym kręgiem", False),
    "212": ("Thick blood sloshing in a glass carafe: four slow heavy glugs one after another, with the small glass flasks chiming softly between them.",
            "gęsta krew chlupoce w szklanej karafce: cztery powolne ciężkie bulgoty kolejno, z miękkim brzękiem szkła między nimi", False),
    "218": (
        "Three sludge tanks burble in turn: thick uneven glugs, separate wet "
        "bubble pops and a glass vessel rattling after each; one viscous drop "
        "plops onto stone at the end. " + NO_M,
        "trzy zbiorniki szlamu bulgoczą po kolei: gęste nierówne gulgoty, osobne mokre pęknięcia pęcherzy i brzęk szkła po każdym; na koniec lepka kropla kapie na kamień",
        False,
    ),
    "227": ("A row of wet joint cracks as a body rearranges itself: six distinct cracking pops in an uneven rhythm, each one sharp and separate.",
            "szereg mokrych trzasków stawów układających nowe ciało: sześć wyraźnych trzasków w nierównym rytmie", False),
    "252": ("Two short commanding brass horn calls over ruins, the second a little higher than the first, each one ringing out fully before the next.",
            "dwa krótkie władcze sygnały mosiężnego rogu nad ruinami, drugi nieco wyżej, każdy w pełni wybrzmiewa", False),
    "256": ("Nightmare visions seeping into a sleeping mind: three rising dissonant whispers of air, each swelling and falling away, layered one after another.",
            "koszmarne wizje sączą się do umysłu śpiącej kobiety: trzy narastające dysonansowe szmery powietrza kolejno", False),
    "264": ("An iron grate exploding outward and hitting an invisible spirit shield: one hard burst, then three successive metallic rebounds as the bars strike the barrier.",
            "krata eksploduje i zatrzymuje się na tarczy ducha: jeden wybuch, potem trzy kolejne metaliczne odbicia od bariery", False),
    "268": ("A building rhythm of open hands slapping bark and tree trunks: six to eight slaps getting faster and louder around the clearing.",
            "narastający rytm dłoni uderzających o korę i pnie: sześć do ośmiu klaśnięć coraz szybciej i głośniej", False),
    "282": ("Blinding moonlight reflected in potion mist: four thin glassy tinkle clusters rising one after another, each a little brighter than the last.",
            "oślepiający blask księżyca we mgle eliksiru: cztery cienkie szkliste brzęczenia kolejno, każde jaśniejsze", False),
    "300": ("A messenger lizard galloping over red canyon rock: eight quick clawed footfalls in an even running rhythm, each with a small stone tick.",
            "galop jaszczura-kuriera po czerwonej skale kanionu: osiem szybkich kroków pazurów równym biegiem, każdy z drobnym stukotem", False),
    "301": ("Two heavy bodies slamming into a taut invisible barrier membrane, one after the other, each a deep weighted thump with a stretched shudder.",
            "podwójne tąpnięcie ciał o napiętą membranę bariery, jedno po drugim, każde z głębokim łomotem i drżeniem", False),
    "304": ("A volley of three elven bows released in one breath: three bowstring twangs in fast succession, then three arrows thudding into wood one after another.",
            "salwa trzech elfich łuków w jednym oddechu: trzy brzęki cięciw szybko po sobie, potem trzy strzały wbijają się w drewno", False),
    "320": ("Green horror vapour draining strength from a battlefield: four successive hollow sucking pulses, each drawing inward and fading away.",
            "zielonkawa para horroru drenuje siły z pola bitwy: cztery kolejne głuche ssące pulsacje, każda wciąga i gaśnie", False),
    "330": ("A giant walking in: four enormous footsteps on frozen ground, evenly spaced and heavy, each with a crunch of cracked ice.",
            "kroki olbrzyma: cztery ogromne kroki na zamarzniętej ziemi, równo i ciężko, każdy z chrzęstem pękającego lodu", False),
    "331": ("Leaves ticking against stone, then three slow hollow knocks of a wooden fist, each spaced apart and resonant.",
            "liście tykają o kamień, potem trzy powolne głuche uderzenia drewnianej pięści drzewca, każde w odstępie", False),
    "339": ("A dragon aristocrat walking a gallery carrying a heavy gilded frame: six measured footsteps on stone, each with a soft chink of gilded metal.",
            "krok smoczej arystokratki po galerii z ciężką złoconą ramą: sześć mierzonych kroków na kamieniu, każdy z brzękiem złocenia", False),
    # `35` Halo Forager ma już wpis wyżej (pięć uderzeń skrzydeł + „filling the
    # whole take") — celowo nie duplikujemy, bo dict cicho przesłania.
    "360": ("A quill writing by itself over glowing parchment: a continuous scratchy nib running across the whole take, with four short pauses and resumptions.",
            "samo piszące pióro nad świecącym pergaminem: ciągły skrobiący dźwięk stalówki przez cały sample z czterema krótkimi pauzami", False),
    "362": ("A mechanical monkey climbing out of a vending automaton: five successive clanking ratchet steps, then a small brass plaque dropping with a chink.",
            "mechaniczna małpa wydostaje się z automatu: pięć kolejnych brzęczących kroków zapadki, potem mosiężna plakietka spada z brzękiem", False),
    "432": ("A merfolk tail splitting apart and first steps on rock: one wet tearing split, then four unsteady barefoot steps on stone, each small and hesitant.",
            "ogon syreny pęka i pierwsze kroki po skałach: mokre rozdarcie, potem cztery niepewne bose kroki na kamieniu", False),
    "436": ("Three fireballs splitting apart into wooden training targets: three successive roaring whooshes, each ending in a heavy wooden crack of the target breaking.",
            "trzy ogniste kule rozszczepione w drewniane cele ćwiczebne: trzy kolejne ryczące świsty, każdy kończy się trzaskiem pękanego drewna", False),
    "441": ("Searching through smoking rubble for route maps: four successive shifts of broken stone and ash, each a gritty scraping handful.",
            "odnajdywanie planów marszruty w dymiących zgliszczach: cztery kolejne przesunięcia gruzu i popiołu, każde chropawym chwytem", False),
    "453": ("Plate armour shifting as the inquisitor turns: five separate heavy steel plates clanking one after another across the whole take, each hit distinct and sharply struck.",
            "zbroja płytowa się przesuwa: pięć osobnych ciężkich płyt dzwoni kolejno przez cały sample, każda wyraźnie i ostro uderzona", False),
    "462": ("Iron footsteps of a Marut crushing gold on the floor: four immense metallic steps, evenly spaced, each grinding coins beneath it.",
            "żelazne kroki Maruta miażdżące złoto na posadzce: cztery ogromne metaliczne kroki w równych odstępach, każdy miele monety", False),
    "463": ("A body slamming down hard onto ice: one instant deep weighted impact with no build-up, then two shorter cracking snaps of the ice sheet within the next second.",
            "ciało pada ciężko na lód: jedno natychmiastowe głębokie uderzenie, potem dwa krótsze trzaski pękającej tafli w ciągu sekundy", False),
    "469": (
        "A chained predator lunging again and again: heavy links snapping "
        "taut and grinding, the cage rattling under each lunge, at least "
        "ten separate metallic clanks, a wet growl to a frenzy." + NO_M,
        "skuty łańcuchem drapieżnik rzuca się raz za razem: ciężkie ogniwa napinają się i zgrzytają, klatka grzechocze przy każdym skoku, co najmniej dziesięć osobnych metalicznych stuków, mokry warkot do szału",
        False,
    ),
    "470": ("A sacrifice of fertile soil, then two trees bursting apart in ash: two deep woody explosions, the second louder, each followed by a long shower of crackling embers.",
            "ofiara z gleby i wybuch dwóch drzew w popiele: dwie drewniane eksplozje, druga głośniejsza, z długim deszczem iskier", False),
    "482": ("Two blades meeting edge to edge and pressing on: three violent steel strikes in "
           "quick succession, the first at the very first instant, each with a harsh gritty ring.",
            "dwa ostrza schodzą się krawędziami i napierają: trzy gwałtowne ciosy stali kolejno, pierwszy w pierwszej chwili, każdy z chropawym brzękiem", False),
    "487": (
        "A resonance shield shattering a fire projectile: four hard "
        "crystalline impacts, each a bright glassy ping over a solid low "
        "thud.  " + NO_M,
        "tarcza rezonansu rozbija pocisk ognia: cztery twarde krystaliczne uderzenia, każde z jasnym szklistym dzwonkiem nad solidnym niskim łupnięciem",
        False,
    ),
    "488": ("Three artefacts being fused into a copper carapace: three successive resonant metallic lock-in clicks, each one deeper than the last.",
            "integracja trzech artefaktów z miedzianą skorupą zbrojmistrza: trzy kolejne rezonansowe metaliczne zatrzaśnięcia, każde głębsze", False),
    "494": ("A herd call answered by two giant reptiles charging in sync: one long rising bellow, then eight heavy footfalls in a fast even thunder.",
            "zew stada i zsynchronizowana szarża dwóch gigantycznych gadów: jeden długi narastający ryk, potem osiem ciężkich kroków w szybkim grzmocie", False),
    "507": ("An iron shell torn apart with a hail of shards falling on stone: one hard shattering burst, then a scattering row of many small metallic shards ticking down over two seconds.",
            "rozerwanie żelaznej skorupy z gradem odłamków na posadzce: jedno twarde pęknięcie, potem szereg wielu drobnych odłamków dzwoniących przez dwie sekundy", False),
    "514": ("A hunter and a wolf attacking in sync: two matching low snarls together, then four paired footfalls and one hard strike, all in tight unison.",
            "synchroniczny atak myśliwego i wilka: dwa zgodne niskie warczenia razem, potem cztery sparowane kroki i jedno twarde uderzenie w równym rytmie", False),
    "551": ("A heavy stone ball bouncing sharply off a stone ring: five successive hard bounces, each a little softer and a little closer together than the last.",
            "ciężka kamienna kula obija się ostro o kamienną obręcz boiska: pięć kolejnych twardych odbić, każde nieco słabsze i bliżej", False),
    "555": ("A bed-legged beastie charging militia in a doorway: four thumping bedpost steps, then a wooden splintering crash as it hits the frame.",
            "bebok z łóżkiem na rogach contra milicjanci w progu chaty: cztery dudniące kroki słupków łóżka, potem drewniany trzask uderzenia w futrynę", False),
    "591": ("Two raccoons charging, one with a pot lid for a shield: six quick scuttling footfalls, then three successive clangs of the pot lid being struck.",
            "szop z tarczą z garnka i szopię w hełmie w szarży: sześć szybkich kroków, potem trzy kolejne brzęki uderzanego garnka", False),
    "596": ("A golden thopter on its first solo flight: a quick whirring rotor spooling up, then six even beats of small metal wings as it climbs away.",
            "pierwszy samodzielny lot złotego thoptera: szybki świst rozkręcanego wirnika, potem sześć równych uderzeń małych metalowych skrzydeł", False),
    "603": ("A mummified crocodile devouring a servant in a flooded crypt: three successive wet tearing bites, each with a heavy gulp and a slosh of water.",
            "mumifikowany krokodyl pożera sługę w zalanej krypcie: trzy kolejne mokre szarpnięcia zębami, każde z ciężkim przełknięciem i pluskiem", False),
    "64": ("Running up crystalline steps of light: eight quick ascending chime-steps in an even run, each a bright glassy tone a little higher than the last.",
            "bieg po krystalicznych stopniach światła ze złotym błyskiem: osiem szybkich dzwoniących stopni w równym biegu, każdy wyższy", False),
    # --- r028: 35 kart z archetypem i trescia < 2 s. Prompt pod kontrakt
    # konkretnej rodziny + jawna liczba powtorzen. Tam, gdzie kontrakt
    # ogranicza czas (arrow_flight decay <= 0,8 s, whip_crack <= 0,5 s,
    # heavy_impact <= 1,4 s), kart NIE ruszamy - wydłużanie by je złamalo.
    "247": (
        "A boggart scout running down an earth tunnel: quick light "
        "bare-foot steps pattering over damp clay, keeping on without a "
        "break to the end. No boots, no marching." + NO_M,
        "boggart biegnie tunelem: szybkie lekkie kroki bosych stóp tupoczą po wilgotnej glinie, tupot trwa bez przerwy do końca",
        False,
    ),
    "250": ("A steel blade snapping back together: one bright hard clash at the very first instant, then four short sharp metallic clicks as the crack seals, each with a gritty shimmer.",
            "ostrze scala się po pęknięciu: jeden jasny twardy szczęk w pierwszej chwili, potem cztery ostre metaliczne kliki", False),
    "71": (
        "A rhino soldier slams into a force wall: one instant deep impact, "
        "then his armour plates clattering and the barrier cracking with "
        "sharp splintering snaps, mid-range." + NO_M,
        "nosoroż uderza w barierę siły: jeden natychmiastowy głęboki impet, potem płyty pancerza łomoczą i bariera pęka z ostrymi trzaskami, środek pasma",
        False,
    ),
    "73": ("A golden construct's blade snapping out and striking: an instant bright steel hit at the very first moment, then three more crisp clashes with a harsh metallic ring.",
            "ostrze konstrukta wysuwa się i uderza: natychmiastowy jasny cios stali, potem trzy kolejne szczęki z ostrym brzękiem", False),
    "344": (
        "Crossed kavu blades: five harsh gritty steel clashes in a row, and the very "
        "first one is by far the loudest moment of the whole take, landing at full "
        "force with no build-up. " + NO_M,
        "skrzyżowane ostrza kavu: pięć ostrych ziarnistych starć stali jedno po drugim, z których pierwsze jest zdecydowanie najgłośniejszym momentem całego take, uderzające z pełną siłą bez narastania",
        False,
    ),
    "525": ("A rapier thrust throwing a wave of glacial spikes: one instant bright steel impact, then four sharp cracking strikes as the ice splinters, each with a glassy metallic ring.",
            "fala lodowcowych kolców od ciosu rapiera: natychmiastowy jasny cios, potem cztery ostre trzaski pękanego lodu", False),
    "594": ("A sword wrenched out of mud and struck: an instant hard bright steel clash at the very first moment, then three more gritty ringing strikes.",
            "miecz wyrwany z błota i cios: natychmiastowy twardy szczęk stali, potem trzy chrapliwe dzwoniące uderzenia", False),
    "140": (
        "Steel plates clashing on a chest in the first instant: one hard crack of "
        "the plates, then a second crack, then a third crack, then a fourth "
        "crack, the striking to the end. " + NO_M,
        "stalowe płyty stukają na piersi w pierwszej chwili: jeden twardy trzask płyt, potem drugi, potem trzeci, potem czwarty, uderzanie do końca",
        False,
    ),
    "232": ('A goblin shifting in plate armour: six separate hard steel plate knocks, each a sharp hit with a gritty unpitched scrape of steel on steel, clear silence between them, no ringing tone.',
            'goblin przestępuje w za dużej zbroi: sześć oddzielnych twardych stuknięć płyt, każde z chrzęstem stali o stal, wyraźne przerwy między nimi', False),
    "16": ("A heavy breastplate lifted off a stone table: four separate steel plates clanking one after another, each distinct and sharply struck, mid-pitched with body.",
            "podniesienie ciężkiego napierśnika ze stołu: cztery osobne płyty dzwonią kolejno, każda wyraźna i z ciałem", False),
    "460": ("A horned breastplate buckled onto a young centaur: five firm knocks of plate against plate, each separate and mid-pitched, with a short leather creak between.",
            "dopasowanie rogowego napierśnika: pięć mocnych stuków płyty o płytę, każdy osobny, ze środka pasma", False),
    "176": ("Two clawed kicks landing on plate armour: one heavy blow then a lighter one, followed by four separate steel plates clanking loose, each distinct and mid-pitched.",
            "podwójne kopnięcie szponów w płytową zbroję: jedno ciężkie, jedno lżejsze, potem cztery osobne płyty dzwonią", False),
    "194": ("A warhorse's steel caparison rattling: seven quick separate plate chinks in an uneven cluster, each mid-pitched and sharply struck, ending in a short scrape.",
            "grzechot stalowego kropierza rumaka: siedem szybkich osobnych brzęków w nierównej grupie, ze środka pasma", False),
    "210": (
        "A rune staff clashing on stone in the first instant: one hard crack of "
        "the staff, then a second crack, then a third crack, then a fourth "
        "crack, the striking to the end. " + NO_M,
        "runowy kostur uderza o kamienną posadzkę w pierwszej chwili: jeden twardy trzask kostura o kamień, potem drugi, potem trzeci, potem czwarty, uderzanie do końca",
        False,
    ),
    "56": (
        "Chitin plates clashing shut in the first instant: one hard crack of "
        "the plates, then a second crack, then a third crack, then a fourth "
        "crack, the striking to the end. " + NO_M,
        "chitynowe płyty zatrzaskują się w pierwszej chwili: jeden twardy trzask płyt, potem drugi, potem trzeci, potem czwarty, uderzanie do końca",
        False,
    ),
    "355": ("Armour set down on a workbench: a steel breastplate dropped, a helmet and a buckler clanking after it, then three more plates dropped one after another, the last plate clanging to the end.",
            "odkładanie zbroi na stół: napierśnik, hełm i puklerz dzwonią kolejno, potem trzy następne płyty, ostatnia do końca", False),
    "39": ("An orc stamping into soft mud: five heavy sodden footsteps in a steady even rhythm, each deep and low with a wet mud splash, filling the whole take.",
            "grząskie tupnięcie orka w błocie: pięć ciężkich mokrych kroków równym rytmem, każdy niski z rozbryzgiem", False),
    "442": ("A rank of defenders stamping in unison: four heavy boot stamps in a strict even rhythm, each one deep and low with a grounded thud.",
            "równoczesne tupnięcie szeregu obrońców: cztery ciężkie kroki w ścisłym równym rytmie, każdy głęboki i niski", False),
    "565": (
        "Songbirds answering one another in a forest clearing: eight piping chirps, a trill between them, then six more chirps, the last trill running "
        "to the end. " + NO_M,
        "ptaki w leśnej polanie odpowiadają sobie: osiem treli, gwizd między nimi, potem sześć następnych, ostatnia trel do końca",
        False,
    ),
    "434": ('A mizzium reactor overloading: a deep low engine rumble underneath, with loud gritty metallic knocking and clanking forward in the mid range, and heavy pressure vents blasting open one after another.',
            'przeciążenie reaktora mizzium: niski pomruk silnika, nad nim głośne metalowe stukanie, kolejne zawory wyrywające się jeden po drugim', False),
    "2": ("A stone thrown into deep water: one bright hard splash at the very first instant, then a hissing spray of droplets and three smaller plops spreading outward.",
            "kamień rzucony w głęboką wodę: jeden jasny twardy plusk w pierwszej chwili, potem syk drobnego rozbryzgu i trzy mniejsze pluski", False),
    "559": (
        "A gaelicat screaming: four sharp rasping screeches in a row, the first at "
        "full force with no build-up, each with a leathery wing snap underneath. " + NO_M,
        "gaelicat wrzeszczy: cztery ostre chrapliwe wrzaski jeden po drugim, pierwszy z pełną siłą bez narastania, każdy z trzaskiem skórzastego skrzydła pod spodem",
        False,
    ),
    "292": (
        "A strong gust of wind rushing past: broadband hissing white noise of "
        "turbulent air, swelling and easing in waves, with no whistle, no pitched "
        "note, no tonal hum. " + NO_M,
        "silny podmuch wiatru pedzacy obok: szerokopasmowy szum bialego halasu turbulentnego "
        "powietrza, wzbierajacy i slabnacy falami, bez gwizdu i bez dzwiezczacego tonu",
        False,
    ),
    "583": (
        "An arrow loosed at a target: a sharp bowstring twang, then the fletched shaft "
        "hissing through the air, the whoosh swelling and fading as it flies off, "
        "ending in a soft distant thud as it strikes home. " + NO_M,
        "strzala wypuszczona do celu: ostre szarpniecie cieciwy, potem syk lotki przecinajacej "
        "powietrze, swist wzbierajacy i powoli cichnacy w oddali, na koniec miekki gluchy stuk "
        "trafienia",
        False,
    ),
    "173": ("A warrior's roar taking bear form: a long deep chest roar with enormous low-frequency body underneath, dark and massive, sustained across the whole take.",
            "ryk wojownika przybierającego postać niedźwiedzia: długi głęboki piersiowy ryk z olbrzymim niskim ciałem pod spodem, masywny", False),
    "478": ("Claws raking a hard glassy barrier: a bright scraping screech then a shattering burst of many small glass shards ticking down, at least eight separate tinkling impacts.",
            "zgrzyt pazurów po szklistej barierze: jasny pisk zgrzytu, potem pęknięcie z gradem odłamków, co najmniej osiem osobnych dzwięków", False),
    "26": ("A molten beast's heavy step: a deep low grinding slide of cracked rock that holds the same loud rumbling level all the way across the take instead of spiking and fading, with crackling fissures beneath.",
            "ciężki krok żarnej bestii: głęboki niski zgrzyt pękniętych skał trzymający równy głośny poziom przez cały sample, bez piku i zaniku", False),
    "129": ("A forging hammer striking steel armour in a raised salute: four hard bright hammer blows in a steady rhythm, each with a sharp metallic ring that dies quickly.",
            "kuty młot uderza o stalowy pancerz: cztery twarde jasne uderzenia równym rytmem, każde z ostrym brzękiem, który szybko gaśnie", False),
    "23": ("An iron monastery bell struck once: a hard iron clapper hitting a heavy bell, one struck tone in the middle of the range that holds its level evenly while it rings, sustained across the take.",
            "żelazny dzwon uderzony raz: głęboki dzwon żelaza i brązu wybrzmiewa równo", False),
    "522": ("Luminous chains snapping taut around a running beast: a long bright rattling cascade of many small links, at least ten separate metallic ticks across the whole take.",
            "świetliste łańcuchy napinają się na biegnącej bestii: długa jasna kaskada grzechotu wielu ogniw, co najmniej dziesięć osobnych stuków", False),
    "244": (
        "Songbirds replying to one another in a forest: ten short clear piping chirps "
        "in an uneven rhythm, each a bright tonal whistle, stone grinding beneath. " + NO_M,
        "ptaki śpiewające odpowiadają sobie w lesie: dziesięć krótkich wyraźnych szczebiotliwych treli w nierównym rytmie, każda jasnym tonalnym gwizdem, pod spodem zgrzyt kamienia",
        False,
    ),
    "12": (
        "A dock robot's servo running: one smooth continuous tonal hum at a steady "
        "pitch held unbroken, with an even buzzing undertone and eight soft mechanical "
        "clicks over it. " + NO_M,
        "serwo portowego robota w ruchu: jeden gładki ciągły tonalny pomruk o stałej wysokości trzymany bez przerwy, z jednostajnym bzyczącym podkładem i ośmioma miękkimi mechanicznymi kliknięciami",
        False,
    ),
    "5": (
        "An arcane spell igniting: a bright crystalline shimmer swelling and holding "
        "steadily, with sparkling glassy overtones ringing high above it for the whole "
        "take. " + NO_M,
        "arcydzieło magii się zapala: jasne krystaliczne migotanie narastające i trzymane jednostajnie, z iskrzącymi szklanymi alikwotami dzwoniącymi wysoko nad nim przez cały take",
        False,
    ),
    "253": ("An elven bard's lute at dawn: a short plucked phrase of five or six separate clear string notes played with even rhythm, warm and bright.",
            "lutnia elfiego barda o świcie: krótka fraza z pięciu-sześciu osobnych wyraźnych dźwięków strun w równym rytmie", False),
    # --- r029: 33 karty, kazda z DOKLADNIE jednym zlamanym progiem kontraktu.
    # Prompt celuje w ta jedna ceche. Uwaga: insect_swarm potrzebuje raz
    # nizszego centroidu (98, 106, 456, 81), a raz wiecej tonalnosci (31, 540) -
    # dlatego tylko wpisy per karta, profil rodzinny by je pogodzic nie mogl.
    "308": ("A greatsword striking in the first instant: one hard crack of the blade, then two long rasping cuts of steel drawn along steel, then a third crack, the shearing to the end.",
            "wielki miecz uderza w pierwszej chwili: twardy trzask ostrza, dwa długie zgrzyty stali o stal, trzeci trzask, cięcie do końca", False),
    "9": ("A gust of wind: broadband hissing white noise of turbulent air, swelling and easing, with no whistle, no pitched note and no tonal hum anywhere in it.",
            "podmuch wiatru: szerokopasmowy szumiący szum białego turbulentnego powietrza, bez gwizdu i bez tonu", False),
    "67": (
        "A war machine's engine: a piston knocking, a second piston "
        "joining in, gears grinding and a chain running over a sprocket, "
        "the clanking keeping on without a break to the end." + NO_M,
        "silnik machiny: stuka tłok, dołącza drugi, zgrzytają koła zębate i biegnie łańcuch po kole napędowym, stukot trwa bez przerwy do końca",
        False,
    ),
    "80": ("An armored vehicle idling: a moderate low engine rumble under loud gritty mechanical clatter and metal knocking that sits forward in the mid range.",
            "opancerzony pojazd na biegu: umiarkowany pomruk pod głośnym chrapliwym metalicznym terkotem w środku", False),
    "501": ("A war machine reactor working: a piston knocking, a crankshaft turning over, gears grinding and a flywheel spinning down, the clanking keeping on without a break to the end.",
            "reaktor machiny wojennej: tłok stuka, korbowód się obraca, koła zębate mielą i koło zamachowe zwalnia, stukot bez przerwy do końca", False),
    "49": ("The ground tearing between worlds: a deep split with loud grinding and snapping rock carried clearly in the middle of the range, not only sub-bass.",
            "ziemia rozdziera się między światami: głębokie pęknięcie z głośnym mielącym i trzaskającym kamieniem wyraźnie w środku pasma", False),
    "168": ("A deep mountain landslide: boulders grinding with very low heavy weight, deep and dark, the rumble sitting well below the middle of the range.",
            "głębokie osuwisko w górach: głazy mielą się z bardzo niskim ciężarem, głęboko i ciemno, pomruk dobrze poniżej środka pasma", False),
    "31": ("A dense swarm of flies: a steady pitched drone with one clear fundamental note held throughout, smooth and harmonic, buzzing on a single sustained pitch.",
            "gęsty rój much: równy bzyk z jednym wyraźnym tonem podstawowym trzymanym przez cały czas", False),
    "540": ("A dense swarm close up: a smooth pitched buzzing drone on one steady note, clearly harmonic and even, held without breaking.",
            "gęsty rój z bliska: gładki bzyk na jednym równym tonie, wyraźnie harmoniczny i ciągły", False),
    "6": ("A lawmage's barrier: a glassy chime cluster with a hard low strike, then a long sustained shimmering tail that holds steadily to the very end of the take.",
            "bariera prawodawcy: szklisty klaster dzwonków z twardym uderzeniem, potem długi trzymany ogon migotania", False),
    "18": ("Magic kindling: a rising crystalline shimmer with a bright tone and sparkles, holding its sustained glow right through to the end without dropping away.",
            "magia się zapala: narastające krystaliczne migotanie trwające równo do samego końca", False),
    "15": ("Old parchment cards swirling, then a fire crack: the crack lands with zero build-up at the very first sample, an instantaneous snap with nothing before it.",
            "szelest wirujących kart i trzask ognia: trzask w pierwszej próbce, bez żadnego zamachu", False),
    "257": ("A fire whip coiling and dragging: one very sharp bright high crack with zero wind-up at the first instant, then a brief bright sputtering of flame.",
            "ognisty bicz się owija i ciągnie: jeden bardzo ostry jasny wysoki trzask bez zamachu w pierwszej chwili, potem krótkie prychanie płomienia", False),
    "144": ("A heavy iron key turning slowly in an old lock, with rapid bird trills around it: several quick chirps per second, fast and fluttering, not slow calls.",
            "obrót żelaznego klucza w starym zamku z szybkimi trelem ptaków: kilka świergotów na sekundę", False),
    "506": ("A flock of finches taking flight: a rapid burst of high squeaking chirps, many quick notes per second in a fast fluttering trill, with wingbeats under them.",
            "stado zięb zrywa się do lotu: szybka seria wysokich świergotów, wiele nut na sekundę w trzepoczącym trelem", False),
    # 610: poprzedni prompt z r026 mowil 'no bright ticking and no hiss',
    # przez co centroid spadl do 163 Hz przy wymaganym oknie 800-6000 Hz.
    "610": ("A toy automaton taking a few steps: three or four light crisp mechanical clicks and gear ticks pitched in the middle of the range, warm rather than bright.",
            "automaton robi kilka kroków: trzy-cztery lekkie sprężyste kliknięcia i zębatki w środku pasma, ciepłe raczej niż jasne", False),
    # --- r030: zasada po r029. Prompt pod jedna ceche naprawial ja, ale model
    # rozstrzygal konflikt kosztem innej cechy w tej samej rodzinie (sword_clash
    # dostal szum i stracil attack_s; robot_servo dostal cztery kliky i stracil
    # tonal_frame_fraction do 0,04 przy wymaganym >= 0,35). Dlatego cecha CHRONIONA
    # idzie pierwsza i jako element dominujacy, a poprawka dopiero po niej.
    "17": (
        "A dagger striking stone in the first instant: one hard crack of the blade, "
        "then a rasp of steel drawn over stone, then a second crack, then a second "
        "rasp, the scraping held to the end. " + NO_M,
        "sztylet uderza w kamień w pierwszej chwili: twardy trzask klingi, potem zgrzyt stali po kamieniu, potem drugi trzask, potem drugi zgrzyt po kamieniu, skrobanie wytrzymane do końca",
        False,
    ),
    "20": (
        "A sword hitting a sword in the first instant: one hard crack of the "
        "blade, then two long rasping cuts of steel drawn along steel, then a "
        "third crack, the shearing held to the end. " + NO_M,
        "miecz uderza o miecz w pierwszej chwili: jeden twardy trzask klingi, potem dwa długie zgrzyty stali o stal, potem trzeci trzask, cięcie wytrzymane do końca",
        False,
    ),
    "345": ("A porcelain blade striking: one hard impact with zero wind-up at the very start, built from harsh broadband gritty ceramic-and-steel noise, bright and rough-edged.",
            "porcelanowe ostrze uderza: twarde uderzenie bez zamachu, z chrapliwego szerokopasmowego szumu", False),
    "435": (
        "A blade striking a shield boss in the first instant: one hard crack, then a long rasp of steel over iron, a second crack, a second rasp, then a third crack, shearing to the end."
        + NO_M,
        "ostrze uderza w guz tarczy w pierwszej chwili: twardy trzask klingi, potem długi zgrzyt stali po żelazie, potem drugi trzask, potem drugi długi zgrzyt, potem trzeci trzask, cięcie wytrzymane do końca",
        False,
    ),
    "608": (
        "Two blades meeting edge to edge in the first instant: one hard crack, then two long rasping cuts of steel drawn along steel, then a third crack, the shearing held to the end."
        + NO_M,
        "dwa ostrza krawędziami w pierwszej chwili: jeden twardy trzask klingi, potem dwa długie zgrzyty stali o stal, potem trzeci trzask, cięcie wytrzymane do końca",
        False,
    ),
    "98": (
        "A swarm settling on wood: one steady pitched drone buzzing in the middle of "
        "the range, warm and rounded, held unbroken for the whole take. " + NO_M,
        "rój osiada na drewnie: jeden jednostajny ton bzyczenia trzymany bez przerwy i brzęczący w środku pasma, ciepły i zaokrąglony, wytrzymany przez cały take bez przerwy",
        False,
    ),
    "106": ("A single sustained buzzing drone on one clear pitch, unbroken and smooth from the first moment to the last, sitting in the middle of the range with nothing shrill on top.",
            "chmara much: jeden ciągły bzyk na jednym wyraźnym tonie, nieprzerwany, w środku pasma, bez pisku", False),
    "456": ("One sharp crack, then a single sustained buzzing drone held unbroken on a clear pitch, thick and rounded, sitting in the middle of the range with no bright hiss.",
            "rój wzbija się z porcelany: trzask, potem jeden ciągły bzyk na wyraźnym tonie, w środku pasma", False),
    "81": ("One steady pitched drone held unbroken with a clear fundamental note, buzzing slightly forward and bright in the upper middle of the range, even and continuous.",
            "gęsty rój pszczół z bliska: jeden równy bzyk trzymany bez przerwy, nieco jasny w górnym środku pasma", False),
    "95": ("Heavy wooden doors: a long tonal creak that rings on and fades slowly over more than a second, its pitch wavering gently about three or four times a second, not faster.",
            "ciężkie drzwi: długie tonalne skrzypienie wybrzmiewające ponad sekundę, wysokość faluje łagodnie trzy-cztery razy na sekundę", False),
    "303": ("Heavy doors: a long tonal creak that rings on past a second, its pitch wobbling at a steady medium rate of about five or six times a second - faster than a slow slide.",
            "ciężkie drzwi: długie tonalne skrzypienie ponad sekundę, wysokość chwieje się w średnim tempie pięć-sześć razy na sekundę", False),
    "531": (
        "Heavy doors pushed slowly open: a long drawn-out tonal creak that rises and "
        "falls five or six times, groaning and wavering, held for the whole take, "
        "ending in a soft wooden clunk. " + NO_M,
        "ciężkie drzwi uchylają się powoli: długie przeciągłe tonalne skrzypienie, które wznosi się i opada pięć lub sześć razy, jęcząc i falując, trzymane przez cały take, kończące się miękkim drewnianym stuknięciem",
        False,
    ),
    "103": ("A broad gust that builds slowly over a third of a second and holds, broadband hissing air noise whose weight sits low - deep rumbling air, no bright hiss on top.",
            "wiatr w gałęziach: szeroki podmuch narastający powoli i trzymany, o ciężarze nisko, bez jasnego syku", False),
    "491": (
        "Bark plates snapping onto an arm in the first instant: one hard crack of the plates, then a second crack, "
        "then a third crack, then a fourth crack, the striking to the end. "
        + NO_M,
        "kora twardnieje w płyty na ramieniu: jeden twardy trzask płyt, potem drugi trzask, potem trzeci, potem czwarty, uderzanie do końca",
        False,
    ),
    "492": ("Tall grass laid down by a gust over a barrow: a broad swell of wind that builds slowly and holds, deep and low in the range, broadband air noise with no bright hiss above it.",
            "wysoka trawa kładziona podmuchem nad kurhanem: szeroki narastający wiatr, głęboki i niski, bez syku", False),
    "513": ("A wide gust sweeping open ground: air that builds slowly over a third of a second and holds, deep low broadband rumbling wind, with no bright hiss or whistle on top.",
            "szeroki podmuch nad otwartym terenem: powietrze narasta powoli i trwa, głęboki niski szum bez syku", False),
    "381": ("A settled caravan wagon creaking in the night wind: one long tonal slow creak that keeps ringing on and fades gradually for well over a second, timber settling under it.",
            "skrzypienie wozu karawany w nocnym wietrze: jedno długie tonalne skrzypienie wybrzmiewające ponad sekundę", False),
    "537": ("Heavy doors: a long drawn-out tonal creak that holds and fades slowly across more than a second, its pitch wavering gently, ringing on long after the push ends.",
            "ciężkie drzwi: długie przeciągłe tonalne skrzypienie, które trwa i gaśnie powoli ponad sekundę", False),
    "204": ("One continuous clean tone at a constant pitch, dominant and unbroken like a tuning fork, with just two very soft clicks barely audible over it.",
            "serwo robota: jeden ciągły czysty ton o stałej wysokości, dominujący od początku do końca, z dwoma bardzo cichymi klikami", False),
    "611": ("One steady clean tone at a constant pitch dominating the whole take, continuous and unbroken, with only two very soft faint mechanical clicks sitting lightly on top of it.",
            "serwo drona: jeden równy czysty ton dominujący w całym nagraniu, ciągły, z dwoma bardzo cichymi klikami", False),
    # --- pkt 1 (2026-10-06): 25 kart, ktorych zlamana metryka jest sterowalna
    # promptem i ktore NIE dostaly jeszcze celowanego promptu pod te ceche.
    # Pomijam attack_s i mod_peak_hz (r030: model nie realizuje liczb) oraz karty
    # probowane 2-3 razy bez efektu.
    "3": ("A bonfire of dry wood: a dense shower of crackles and pops pitched in the middle of the range, warm and woody rather than bright or hissy.",
            "ognisko z suchego drewna: gęsty deszcz trzasków w środku pasma, ciepły i drewniany raczej niż jasny czy syczący", False),
    "4": (
        "Five bodies slam into a pool one after another, the first impact "
        "the loudest: each a bright hissing spray of water droplets, "
        "churning and dripping to the end." + NO_M,
        "pięć ciał wpada do sadzawki jedno po drugim, pierwsze uderzenie najgłośniejsze: za każdym razem jasny syczący rozbryzg kropel, woda kłębi się i kapie do końca",
        False,
    ),
    "40": ("Thick armour plates knocked together: two or three mid-pitched metal clanks, weighty and dull rather than bright, each plate struck separately.",
            "grube płyty pancerza zderzają się: dwa-trzy klanki w środku pasma, ciężkie i matowe raczej niż jasne", False),
    "96": ("A stream of emerald magic: one continuous flowing shimmering tone with a clear sustained pitch and bright sparkling overtones, smooth and even throughout.",
            "strumień szmaragdowej magii: jeden ciągły płynący migotliwy ton o wyraźnej wysokości i jasnych iskrzących alikwotach", False),
    "113": ("A welder drone's servo locking up: one smooth steady hum at a single unwavering mid-low pitch, held at one even volume across the whole take, with two light clicks underneath far quieter than the hum.",
            'serwo drona się blokuje: jeden równy ciągły metaliczny brzęk o stałej niskiej wysokości, trzymany na tym samym poziomie przez cały czas bez zanikania, pod nim dwa lekkie trzaski dużo ciszej niż brzęk', False),
    "118": ("A monster's close roar: a guttural bellow sitting clearly in the low middle of the range, rough and raspy, well above a pure sub-bass rumble.",
            "bliski ryk potwora: gardłowy wrzask wyraźnie w niskim środku pasma, chropawy, dobrze ponad czystym infrabasem", False),
    "126": ("Wild birds feeding from a hand: several clear melodic chirps on distinct notes, each one tonal and bright, with soft wing flutters between them.",
            "dzikie ptaki karmione z ręki: kilka wyraźnych melodyjnych świergotów na różnych nutach, każdy tonalny i jasny", False),
    "156": (
        "A stone slab slamming onto marble in the first instant: one crushing "
        "impact, then a second impact, then a third impact, then a fourth "
        "impact, the striking to the end. " + NO_M,
        "kamienna płyta wali w marmur w pierwszej chwili: jedno miażdżące uderzenie, potem drugie, potem trzecie, potem czwarte, uderzanie do końca",
        False,
    ),
    "164": ("A great winged creature taking off: several crisp wingbeats with a bright leathery snap and a high rushing hiss of air, each beat clearly in the middle of the range.",
            "wielka skrzydlata istota startuje: kilka sprężystych uderzeń skrzydeł z jasnym skórzanym trzaskiem i wysokim pędem powietrza", False),
    "216": (
        "Armour plates clashing on a stitched body in the first instant: one hard "
        "crack of the plates, then a second crack, then a third crack, then a "
        "fourth crack, the striking to the end. " + NO_M,
        "płyty pancerza stukają na zszytym ciele w pierwszej chwili: jeden twardy trzask płyt, potem drugi trzask, potem trzeci, potem czwarty, uderzanie do końca",
        False,
    ),
    "226": ("A makeshift construct stirring: one continuous low electronic servo tone held unbroken beneath the shifting limbs, sustaining steadily through the whole take.",
            "prowizoryczny konstrukt budzi się: jeden ciągły niski elektroniczny ton serwa trzymany bez przerwy pod poruszanymi kończynami", False),
    "228": ("Heavy armoured footsteps: exactly four boot steps on stone at strict metronome-even spacing, each step identical in weight and timing, with the same plate clank.",
            "ciężkie kroki w pancerzu: dokładnie cztery kroki na kamieniu w idealnie metronomicznych odstępach, każdy identyczny", False),
    "231": ("Four wordless voices humming one sustained hymn note in unison, opening into a chord that rings on and fades very slowly, well over a second after the breath stops.",
            "cztery bezsłowne głosy nucą jeden trzymany dźwięk hymnu, otwierając się w akord, który brzmi i gaśnie bardzo powoli", False),
    "265": ("A cliff face collapsing: a long low grind of rock sliding off stone, deep and heavy, shards snapping, then a spreading low crash of debris settling.",
            "ściana klifu się wali: długi niski zgrzyt skały sunącej po kamieniu, głęboki i ciężki, potem niski rozlegający się łoskot gruzu", False),
    "382": ("The ground splitting: one deep crack, then a low rolling rumble that keeps going and fades extremely slowly, still audible right to the end of the take.",
            "ziemia pęka: jedno głębokie pęknięcie, potem niski toczący się grzmot gasnący niezwykle powoli, słyszalny do samego końca", False),
    "496": ("A volcano erupting close by: a broad roaring eruption of grinding rocky noise with enormous deep bass weight, gritty and broadband rather than a smooth tone.",
            "wulkan wybucha blisko: szeroki huczący wybuch mielącego skalnego szumu z olbrzymim basem, chropawy i szerokopasmowy", False),
    "558": ("A bronze temple bell struck once: a low, dark bronze tone well below the middle of the range, holding a steady even level while it rings rather than fading quickly, sustained to the end.",
            "brązowy dzwon uderzony raz: niski ciężki dzwon mosiądzu wybrzmiewa długo", False),
    "562": ("A thunderclap overhead: one very sharp sudden crack that peaks hard and abruptly, then a deep rolling rumble fading slowly.",
            "grzmot nad głową: jeden bardzo ostry nagły trzask osiągający szczyt twardo i nagle, potem głęboki toczący się pomruk", False),
    # --- r032: 14 kart wybranych pomiarem, nie zgadywaniem. 269 - kontrakt
    # attack_s przy dzwieku wieloudarzeniowym wymaga, zeby najglosniejszy byl
    # PIERWSZY cios (attack_s liczy sie wstecz od globalnego szczytu). Reszta to
    # karty, ktore w r031 drgnely ku celowi albo dostaly nowa metryke po
    # naprawieniu poprzedniej.
    "269": ("One piercing hawk screech, and its very first instant is by far the loudest moment of the whole take, bright and high, with two quieter wingbeats after it.",
            "jastrząb: jeden przenikliwy krzyk, pierwsza chwila zdecydowanie najgłośniejsza, potem dwa cichsze uderzenia skrzydeł", False),
    # --- r033: dwie karty bez archetypu z flaga speech_like. Próg flagi to
    # mod_2_8hz_ratio > 0,55 (tempo sylab) + voiced > 0,35 + centroid 300-3000 Hz,
    # czyli NIE wykrywa mowy, tylko modulację w tempie sylab. Pięć pozostałych
    # kart z tą flagą ma tonalność wymaganą kontraktem (forest_birdsong >= 0,25,
    # temple_bell >= 0,5) albo wprost w scenariuszu, więc ich nie ruszam.
    # Tu przyczyna jest w prompcie: 578 prosił o 'morning star WHISTLING',
    # a gwizd to czysty ton.
    "130": ("A harpy guarding her hoard: one harsh ragged broadband screech, rough grating and noisy rather than sung or tonal, curved talons clattering on cracked stone, loose bone trinkets rattling.",
            "skrzek harpii strzegącej skarbu: jeden chrapliwy szerokopasmowy wrzask, szorstki i szumowy raczej niż śpiewny, szpony na pękniętym kamieniu", False),
    "578": ("A beast's sudden reversal: hooves wrenching around in the mud, a heavy morning star sweeping full-circle with a broad low whoosh of displaced air, no whistle and no pitched tone, hunters scattering.",
            "nagły zwrot bestii: kopyta w błocie, ciężki kiścień zatacza krąg z szerokim niskim świstem powietrza, bez gwizdu i bez tonu", False),
    # --- r034: 7 najwiekszych wezlow podobienstwa. Pomiar: 175 par w pasmie
    # 0,90-0,95 (129 kart w >=1 parze, 45 w >=3). Te karty maja rozne fabuly,
    # ale model renderuje je identycznie - jako niski szerokopasmowy huk.
    # Regeneracja jednego wezla zdjmuje najwiecej par naraz.
    # Wzor: NAKAZ nie zakaz (z 578/r033: zakaz bez zamiennika zdjal cale pasmo,
    # centroid 2546 -> 35 Hz). Kazdy prompt foregrounduje element charakterystyczny
    # i daje mu hierarchie glosnosci - jedyny wzorzec dzialajacy niezawodnie (269).
    "529": ("A colossal mercury wave: liquid metal sloshing with a bright glassy ring, thousands of tiny metal droplets tinkling as the crest falls over armour.",
            "kolosalna fala rtęci przelewająca się z jasnym metalicznym brzękiem i tysiącem drobnych kropel", False),
    "479": ("Heavy armour slamming onto rock: one sharp metallic plate crack as the loudest moment, then stone shards skittering and grit raining down on metal.",
            "pancerz uderzający w skałę: ostry trzask płyty, potem odpryski kamienia i grad żwiru na metalu", False),
    "290": ("A flame bursting to life: a dense bright crackle of sparks snapping as the loudest moment, then a turbulent roaring fire with popping embers.",
            "buchnięcie płomienia: gęsty jasny trzask iskier, potem turbulentny ogień z pękającymi węglami", False),
    "160": ("An elemental hound breaking loose: one wet snarling canine roar as the loudest moment, iron-hot claws raking basalt, fire crackling underneath.",
            "ogar żywiołów zrywa się: mokry warczący ryk, żelazne pazury na bazalcie, trzaskający ogień", False),
    "614": ("An old wyvern striking: one leathery wing snap for balance, then a heavy paw hammering a body onto rock with a dull crunch and sliding gravel.",
            "wiwerna uderza: skórzasty trzask skrzydła, potem ciężka łapa wbija ciało w skałę ze żwirem", False),
    "123": ("An ox caravan on a packed road: dry wooden axles creaking in a steady rhythm, harness ropes straining, one ox lowing, iron tyres on hard dirt.",
            "karawana wołów na trakcie: suche skrzypienie osi, naprężone postronki, jedno muczenie", False),
    "287": ("Dragon fury erupting: one deep reptilian roar as the loudest moment, then fire roaring upward into vast wings with sparks spiralling high.",
            "smocza furia: głęboki gadzi ryk, potem ogień wzbijający się w skrzydła z iskrami w górze", False),
    # --- r035: drugie pietro wezlow podobienstwa (po r034: 120 par, bylo 175).
    # 7 kart BEZ archetypu - nie ma kontraktu do złamania. Pominięte celowo:
    # 562 Shock (thunder_clap, TRAFIONY), 343 Puppeteer Clique (temple_bell,
    # TRAFIONY) - regeneracja ryzykowalaby utrate trafienia.
    # Wzor ten sam co w r034, ktory zadzialal: NAKAZ nie zakaz + hierarchia
    # glosnosci dla elementu charakterystycznego. 470, 477, 57 maja centroid
    # 237-341 Hz, czyli siedza w niskim huku, z ktorego r034 wyprowadzila
    # poprzednia siodemke.
    "477": (
        "An aven banks through icy air with three strong wingbeats, folds its "
        "wings, then sweeps past with a sharp spearhead chime and rushing "
        "cold current. " + NO_M,
        "aven skręca w lodowym powietrzu trzema mocnymi uderzeniami skrzydeł, składa je, po czym przelatuje z ostrym dźwiękiem grotu i pędem zimnego prądu",
        False,
    ),
    "445": (
        "A warhorse crossing frozen ground: four hoof crunches breaking the "
        "crust, steel tack clinking between them, then three more crunches, "
        "the last clink to the end." + NO_M,
        "koń bojowy idzie po zamarzniętym gruncie: cztery chrupnięcia kopyt w skorupie, między nimi brzęk stalowej uprzęży, potem trzy kolejne chrupnięcia, ostatni brzęk do końca",
        False,
    ),
    "448": (
        "A chaos spire erupting from a street: cobblestones bursting upward "
        "with sharp stone cracks, a crystal spike grinding gritty and low.  " + NO_M,
        "iglica chaosu wybucha z ulicy: bruk trzaska ostro w górę, kryształowy kolec zgrzyta chropowato i nisko",
        False,
    ),
    "57": (
        "Silk robes billowing open: a long bright rustle of heavy fabric "
        "unfolding and climbing upward, a shimmering thread above it. " + NO_M,
        "jedwabne szaty rozkładają się: długi jasny szelest ciężkiej tkaniny pnącej się w górę, nad nią lśniąca nić",
        False,
    ),
    "550": ("A frost lynx freezing its prey: one leap, a touch, then ice snapping shut in a spreading series of sharp crystalline cracks, a bear's roar cut short mid-breath.",
            "mroźny ryś zamraża ofiarę: skok, dotyk, lód zatrzaskuje się serią ostrych kryształowych pęknięć, ryk urywa się", False),
    "438": ("Old ruins rotting into new soil: dead leaves crumbling with a dry papery rustle as the loudest moment, buried artifacts flaking apart, green pulses quickening beneath.",
            "stare ruiny próchnieją w glebę: suche liście kruszą się z szelestem, artefakty łuszczą, zielone pulsy przyspieszają", False),
    # --- r036: trzecie pietro wezlow podobienstwa (po r035: 99 par, bylo 175).
    # 5 kart BEZ archetypu. Z listy wezlow odrzucone, bo sa TRAFIONE z kontraktami:
    # 562 Shock (thunder_clap), 343 Puppeteer Clique (temple_bell), 261 Universal
    # Solvent (steam_hiss), 23 Brightwood Tracker (temple_bell), 26 Ember Beast
    # (stone_slide), 358 Frontline War-Rager (creature_roar).
    # 487 bylo probowane w r035 i cofniete (warianty krotkie: v1 1,09 s, v2 1,30 s)
    # - tym razem prompt jawnie rozklada cztery uderzenia na caly take.
    # 22 i 32 maja centroid 440-493 Hz, czyli siedza w niskim huku; 32 ma
    # 'burst of bubbles' w scenariuszu, wiec dostaje hierarchie glosnosci.
    "592": (
        "A stone reliquary crashes onto an altar: one deep crack, iron "
        "fittings break loose in several quick snaps, grit rattles across the "
        "slab, then the final clasp falls with a bright clink. " + NO_M,
        "kamienny relikwiarz spada na ołtarz: głębokie pęknięcie, żelazne okucia puszczają serią szybkich trzasków, żwir grzechocze po płycie, a ostatnia sprzączka brzęczy jasno",
        False,
    ),
    "238": ("A dwarf war roller grinding forward: iron drums crushing a wrecked chariot, wood splintering in sharp cracks and metal buckling, gravel spraying off the tread.",
            "krasnoludzki walec wojenny miele wrak rydwanu: żelazne bębny, drewno trzaska, metal się wygina, żwir pryska", False),
    "22": ("One enormous boulder heave: deep stone grinding against rock, then a sharp ground crack underfoot as the loudest moment, pebbles and grit showering down after it.",
            "gigantyczny głaz rusza z miejsca: kamień miele o skałę, potem ostry trzask ziemi pod stopami i deszcz kamyków", False),
    "32": ("A large fish lunging out of a rotten wooden hull underwater: one muffled low whoosh of displaced water, then a bright burst of bubbles rising and popping against the planks.",
            "ryba wypada ze zbutwiałego wraku pod wodą: głuchy wir wody, potem jasna chmura bąbli wzbijająca się i pękająca o deski", False),
    # --- r037: czwarte pietro wezlow (po r036: 87 par, bylo 175). Struktura sie
    # splaszczyla - najwieksze wezly maja 3 pary (w r034 bylo 14). Wezly z
    # najwieksza liczba par to karty TRAFIONE z kontraktami (562 Shock 5 par,
    # 261 Universal Solvent 4, 23/26/358 po 3) - celowo nie ruszane.
    # Kryterium wyboru: pary ORAZ za krotka tresc, zeby jedna regeneracja
    # naprawila dwa problemy naraz (461: 2 pary i 1,40 s; 50: 2 pary i 1,71 s).
    # Prompty celowo krotkie (~150 zn), bo doklejka --fill-take wchodzi w limit 450.
    "104": ("A glitch ghost sweeping past: chopped digital stutters snapping in a fast irregular burst as the loudest moment, holographic warble, thin sparks trailing.",
            "hologram zwiadowcy przelatuje z migotaniem: urywane cyfrowe zacięcia trzaskają serią, za nimi cienkie iskry", False),
    "461": ("A spell snuffed mid-flight: a fireball roaring in, then water jets and thick vines erupting to crush it with a violent steam hiss that keeps building.",
            "zaklęcie zduszone w locie: kula ognia nadlatuje, strumienie wody i pnącza miażdżą ją z gwałtownym sykiem pary", False),
    "50": (
        "Three heavy books thud onto stone one by one, pages bursting into a "
        "flutter; after the last, cold luminous mist unfurls and hangs. " + NO_M,
        "trzy ciężkie księgi uderzają o kamień jedna po drugiej, kartki wybuchają furkotem; po ostatniej rozwija się zimna świetlista mgła i pozostaje w powietrzu",
        False,
    ),
    "222": (
        "A conch shell horn blown in three clear blasts: a bright ringing "
        "tonal note held each time, waves crashing and spray hissing beneath. " + NO_M,
        "morski strażnik dmie w muszlę: trzy wyraźne sygnały, za każdym razem jasny dzwoniący ton, pod nim fale i syk piany",
        False,
    ),
    "395": (
        "A corpse unearthed: three wet heavy bursts of mud, then rusted "
        "armour grinding free and roots tearing loose with sharp dry snaps.  " + NO_M,
        "zmarły przebija się przez ziemię: trzy mokre ciężkie wybuchy błota, potem zardzewiała zbroja zgrzyta i korzenie rwą się z suchym trzaskiem",
        False,
    ),
    "419": (
        "A smouldering figure exhaling heat: dry paint blistering and peeling "
        "in rapid sharp cracks, embers popping close, a dry crackling rush.  " + NO_M,
        "postać z lęku przed spaleniem: sucha farba pęcherzy i łuszczy się szybkimi ostrymi trzaskami, węgle strzelają blisko, suchy trzaskający powiew",
        False,
    ),
    "401": (
        "Red hot metal searing: a fierce sustained hiss with molten droplets "
        "spitting and sizzling in rapid bursts, metal skin warping and "
        "cracking.  " + NO_M,
        "rozżarzony metal topi się: ostry nieustanny syk, krople stopionego metalu pryskają i skwierczą szybkimi seriami, skóra metalu pęka",
        False,
    ),
    "295": (
        "Wooden crate dragged across bare boards in three slow rasping "
        "scrapes, each one ending in a hollow wooden knock. Dry and close. " + NO_M,
        "drewniana skrzynia wleczona po deskach: trzy powolne zgrzyty, każdy kończy się głuchym stuknięciem",
        False,
    ),
    "314": (
        "Loose pages spiral upward in two fast turns; dozens of crisp paper "
        "edges flutter and snap together, then the spinning stack lands with "
        "a dry slap. " + NO_M,
        "luźne karty wirują w górę dwoma szybkimi obrotami; dziesiątki ostrych brzegów furkoczą i trzaskają, po czym wirujący stos opada suchym klapnięciem",
        False,
    ),
    "577": (
        "Steel thunderstaff strikes slate: one bright metal clang rings; "
        "three thin electric crackles answer in a rising pattern. The clang "
        "is loudest. " + NO_M,
        "stalowa laska burzy uderza o łupek: rozlega się jeden czysty, dźwięczny brzęk metalu, po czym odpowiadają mu trzy cienkie elektryczne trzaski narastającym wzorem. Najgłośniejszy jest metaliczny dźwięk",
        False,
    ),
    "155": (
        "A sharp detonation crack first, then a stone archway collapsing in a "
        "long grinding rumble with bright debris spattering. " + NO_M,
        "najpierw ostry trzask detonacji, potem kamienny łuk wali się w długim zgrzycie z jasnym pryskaniem odłamków",
        False,
    ),
    "243": (
        "A bolt of energy shrieking upward in a rising pitch sweep that bends "
        "and curves, ending in a sharp hiss of quenching steam. " + NO_M,
        "piorun energii z piskiem wznosi się w górę, skręca z toru i kończy ostrym sykiem gasnącej pary",
        False,
    ),
    "601": (
        "Viscous lava shoving into old forest: thick bubbling blasts and wet "
        "hissing, ancient trunks bursting into flame one after another. " + NO_M,
        "lepka lawa wciska się w las: gęste bulgoczące wybuchy i mokry syk, prastare pnie jeden po drugim stają w płomieniach",
        False,
    ),
    "84": (
        "A huge beast trampling a dead log: three loud dry cracks of "
        "splintering wood in a row, each one snapping sharply. " + NO_M,
        "wielka bestia tratuje zwalony pień: trzy głośne suche trzaski pękającego drewna, jeden za drugim",
        False,
    ),
    "272": (
        "Vines sprouting and wrapping tight around an arm: three sharp "
        "creaking tightenings of green stems, then a low growl. " + NO_M,
        "pnącza wyrastają i oplatają ramię: trzy ostre skrzypiące napięcia zielonych łodyg, potem niski warkot",
        False,
    ),
    "602": (
        "Obsidian shards chiming into being: a cluster of bright glassy "
        "chimes ringing out one after another, a warbled metallic hum "
        "beneath.  " + NO_M,
        "obsydianowe odłamki dzwoniąc pojawiają się jeden po drugim: jasne szklane dźwięki, pod nimi metaliczny pomruk",
        False,
    ),
    "60": (
        "A crystal waterfall pouring steadily: one continuous bright rush of "
        "falling water, a soft splashing veil over it, calm and even.  " + NO_M,
        "krystaliczny wodospad wlewa się stale: jeden ciągły jasny szum spadającej wody, nad nim miękka zasłona plusku",
        False,
    ),
    "458": (
        "An arynx leaping a canyon: claws scraping off the rim, a long rush "
        "of wind, then a heavy landing scattering gravel.  " + NO_M,
        "arynx skacze nad kanionem: pazury zdrapują z krawędzi, długi powiew wiatru, potem ciężkie lądowanie rozrzucające żwir",
        False,
    ),
    "475": (
        "A hydraulic mech arm winds back with a strained piston whine, then "
        "crashes down as a metal club; gears lock with a heavy clang and a "
        "burst of sharp blue electrical sparks.  " + NO_M,
        "hydrauliczne ramię mecha cofa się z jękiem tłoka, po czym wali jak metalowa maczuga; przekładnie blokują się ciężkim brzękiem, a z nich wytryskują ostre niebieskie iskry",
        False,
    ),
    "542": (
        "A panic spellbomb bursts with a sharp pressure crack; the steel spear bounces "
        "across stone in five bright ringing strikes in a row, then rolls to a stop. " + NO_M,
        "bomba zaklęć wybucha ostrym trzaskiem ciśnienia; stalowa włócznia odbija się od kamienia pięcioma jasnymi dzwoniącymi uderzeniami jedno po drugim, po czym zatrzymuje się",
        False,
    ),
    "134": (
        "An aven gliding low over the sea: a long smooth wind rush, then two "
        "clear gull cries ringing out over the hissing wave crests.  " + NO_M,
        "ptakoczłek ślizga się nisko nad morzem: długi gładki szum wiatru, potem dwa wyraźne krzyki mewy nad syczącymi grzbietami fal",
        False,
    ),
    "69": (
        "A brass gauntlet raking a tome: sharp metal styli scraping across "
        "parchment in three long strokes, pages shredding into gritty dust.  " + NO_M,
        "mosiężna rękawica zdziera litery: ostre metalowe rysiki skrobią po pergaminie trzema długimi pociągnięciami, karty szarpią się w ziarnisty pył",
        False,
    ),
    "376": (
        "A swollen corpse rising: soaked leaves sliding off with wet "
        "squelching rustles, a shirt seam tearing wide, a dead lantern "
        "clanking.  " + NO_M,
        "napęczniały nieżywy odszczepieniec wstaje: mokre liście zsuwają się z mlaszczącym szelestem, szew koszuli pęka, martwa latarnia szczęka",
        False,
    ),
    "305": (
        "An illusion collapsing: a dry crumbling sheet breaking into flakes "
        "over a soft low thud, papery crackles settling downward.  " + NO_M,
        "iluzja się rozpada: suchy arkusz kruszy się w płatki nad miękkim niskim łupnięciem, papierowe trzaski opadają w dół",
        False,
    ),
    "575": (
        "A spear thrust through dragon scale: a bright steel tip punching "
        "clean through, scale plates rasping in step, armour ringing.  " + NO_M,
        "pchnięcie włócznią w smoczą łuskę: jasny stalowy grot przebija na wylot, płyty łuski ocierają się rytmicznie, zbroja dzwoni",
        False,
    ),
    "174": (
        "A brass valve blowing open with a low metallic thump, then a fierce "
        "pressurised steam hiss with sharp electric crackles spitting over "
        "it.  " + NO_M,
        "mosiężny zawór otwiera się z niskim metalicznym łupnięciem, potem gwałtowny syk pary pod ciśnieniem i ostre trzaski elektryczne",
        False,
    ),
    "182": (
        "Stone slabs sweeping past: a fast heavy air whoosh with bright grit "
        "and small pebbles rattling and skittering off the stone.  " + NO_M,
        "kamienne płyty przelatują: szybki ciężki świst powietrza z jasnym żwirem i drobnymi kamykami szczękającymi i ślizgającymi się po kamieniu",
        False,
    ),
    "553": (
        "Blades anointed in venom: steel drawn against steel in three long "
        "scraping passes, a blade lifted out of a basin with the liquid "
        "dragging off it, two more scraping passes to the end." + NO_M,
        "ostrza namaszczone jadem: stal ociera się o stal w trzech długich pociągnięciach, ostrze wyjmowane z misy z ociekającą cieczą, jeszcze dwa pociągnięcia do końca",
        False,
    ),
    "554": (
        "A hatchling warning: three bright clipped reptile chirrs close in "
        "the ferns; a huge mother answers twice with a distant throaty roar "
        "and a rush through snapped branches. Keep the little call foremost.  " + NO_M,
        "ostrzeżenie pisklęcia: trzy jasne, krótkie reptyle trele w paprociach; ogromna matka odpowiada dwoma odległymi gardłowymi rykami i szelestem łamanych gałęzi. Na pierwszym planie głos pisklęcia",
        False,
    ),
    "180": (
        "A transformed brute breathing in a dark alley: ragged strained "
        "breaths one after another, broken glass grinding under a heavy boot. " + NO_M,
        "przemieniony brutal oddycha w ciemnej uliczce: jeden za drugim urywane, wysilone oddechy, pod ciężkim butem chrzęści stłuczone szkło",
        False,
    ),
    "485": (
        "A werewolf watching from a ridge: slow deep breaths, claws scraping "
        "into cold stone, a distant lantern creaking in the fog.  " + NO_M,
        "wilkołak czatuje na grzbiecie: powolne głębokie oddechy, pazury skrobiące w zimny kamień, daleka latarnia skrzypi we mgle",
        False,
    ),
    "615": (
        "A naga balancing on a stone beam: scales whispering across stone, "
        "then twin bronze blades slicing the air in two sharp cuts.  " + NO_M,
        "naga balansuje na kamiennej belce: łuski szepczą po kamieniu, potem dwa ostre cięcia podwójnych spiżowych ostrzy",
        False,
    ),
    "100": (
        "A ceremonial escort mech readying: a long energy halberd humming a "
        "steady tone, a pale shield unfolding with a soft snap.  " + NO_M,
        "mech eskortowy szykuje się: długa energetyczna halabarda nuci stały ton, blada tarcza rozkłada się z miękkim trzaskiem",
        False,
    ),
    "28": (
        "A deep underwater bubble collapsing: a round low pulse rising in "
        "pitch, then a bright wet plink as it bursts at the surface.  " + NO_M,
        "głęboka podwodna bańka zapada się: niski okrągły puls wznoszący się tonem, potem jasny mokry plaśnięcie na powierzchni",
        False,
    ),
    "34": (
        "A massive body plunging into molten rock: a thick viscous splash, "
        "then sizzling spatter searing on hot stone in sharp hissing bursts.  " + NO_M,
        "potężne ciało wpada w stopioną skałę: gęsty lepki plusk, potem skwierczące rozpryski palące się na gorącym kamieniu ostrymi sykami",
        False,
    ),
    "46": (
        "Fresh green shoots springing open: many soft sappy pops one after "
        "another, leaves unfurling, light and lively.  " + NO_M,
        "świeże zielone pędy rozwierają się: jeden po drugim miękkie soczyste strzały, liście rozwijają się, lekko i żywo",
        False,
    ),
    "102": (
        "A heavy body diving through air: a rising airy whoosh building in "
        "pitch and speed, wind tearing past, cut short at the lowest point.  " + NO_M,
        "ciężkie ciało pikuje w powietrzu: wznoszący się świst narastający tonem i prędkością, rozdzierany wiatr, urywa się w najniższym punkcie",
        False,
    ),
    "79": (
        "A colossal rune-carved stone shelters a camp: taut tent lines shiver "
        "and twang twice over a steady high crystalline stone hum, the bright "
        "wires ringing as wind rises and fades.  " + NO_M,
        "kolosalny kamień z runami osłania obóz: napięte linki namiotów drżą i dwa razy brzęczą nad stałym wysokim krystalicznym pomrukiem kamienia, jasne druty dźwięczą, gdy wiatr narasta i cichnie",
        False,
    ),
    "291": (
        "A plague beast releases contagion in three uneven wet exhalations, "
        "each followed by a gritty spore hiss and a soft patter of droplets "
        "settling on dead leaves.  " + NO_M,
        "bestia plagi uwalnia skażenie trzema nierównymi mokrymi wydechami; po każdym następuje ziarnisty syk zarodników i miękki stuk kropel osiadających na martwych liściach",
        False,
    ),
    "570": (
        "A heavy iron watergate rises from a flooded channel: a chain ratchet "
        "clanks through three measured pulls, then the loaded grate groans "
        "and a sheet of water slaps the stone basin.  " + NO_M,
        "ciężka żelazna śluza wynurza się z zalanego kanału: zapadka łańcucha klekocze przy trzech równych pociągnięciach, potem napięta krata jęczy, a tafla wody uderza o kamienną nieckę",
        False,
    ),
    "77": (
        "A veteran's triple-barrel gauntlet clicks three times, then fires "
        "three spaced shots; each crack trails a brief electric snap, the "
        "last ring fading.  " + NO_M,
        "potrójna rękawica weteranki klika trzy razy, po czym padają trzy oddzielone strzały; każdy huk wieńczy krótki elektryczny trzask, ostatni dźwięczy i cichnie",
        False,
    ),
    "589": (
        "Acid slime eats steel: plates bend with a wet creak, three heavy "
        "bubbles glug and burst; one sticky drop plops into a stone bowl. "
        "Keep the gurgle close and the pops crisp. " + NO_M,
        "szlam kwasowy zjada stal: płyty wyginają się z mokrym skrzypnięciem, trzy ciężkie pęcherze bulgoczą i pękają; lepka kropla kapie do kamiennej misy. Bulgotanie jest bliskie, pęcherze wyraziste",
        False,
    ),
    "242": (
        "A warhorse trots across polished marble: four measured pairs of hard "
        "hooves, light armor jingles, and the final step rings away.  " + NO_M,
        "koń bojowy kłusuje po wypolerowanym marmurze: cztery równe pary twardych kopyt, lekko brzęczy zbroja, ostatni krok dźwięcznie oddala się",
        False,
    ),
    "499": (
        "One crushing blow cracks a brass monument; the terrace splits and "
        "three marble blocks fall in staggered heavy thuds.  " + NO_M,
        "miażdżący cios pęka mosiężny monument; taras rozdziera się i trzy marmurowe bloki spadają ciężkimi, rozłożonymi uderzeniami",
        False,
    ),
    "367": (
        "A shaman shakes a hollow gourd in three slow double strokes: woody "
        "clacks, dry seeds rattling inside, copper rings quivering briefly. " + NO_M,
        "szaman potrząsa pustą tykwą trzema powolnymi podwójnymi ruchami: drewniane stuki, grzechoczące ziarna i krótko drżące miedziane dzwonki",
        False,
    ),
    "527": (
        "Shiva's ice form locks the battlefield: a cold crystalline rush, "
        "three sharp fractures racing outward, then armor and hooves freeze "
        "with brittle clinks. " + NO_M,
        "lodowa postać Shivy zamraża pole bitwy: zimny krystaliczny pęd, trzy ostre pęknięcia biegnące na zewnątrz, potem zbroja i kopyta zamierają z kruchym brzękiem",
        False,
    ),
    "467": (
        "A mountain flock bursts from monastery towers in three hard "
        "wingbeats; feathers flutter dryly, then small birds call as a "
        "rushing gust sweeps past the stone walls. " + NO_M,
        "górskie stado zrywa się z wież klasztoru trzema mocnymi uderzeniami skrzydeł; pióra sucho furkoczą, potem małe ptaki nawołują, gdy pęd powietrza omiata kamienne mury",
        False,
    ),
    "27": (
        "A curse snaps apart in three crisp glassy fractures; countless tiny "
        "brittle shards scatter in a bright cascade, then dissolve into a "
        "thin fading shimmer. " + NO_M,
        "klątwa pęka trzema czystymi, szklistymi trzaskami; niezliczone drobne kruche odłamki rozsypują się jasną kaskadą, po czym znikają w cienkim, gasnącym migotaniu",
        False,
    ),
    "254": (
        "A giant spider scuttles across ironwood in two rapid runs of eight "
        "hard feet tapping bark; a short pause, then one final pair of dry "
        "clicks. " + NO_M,
        "wielki pająk przebiega po żelaznym drewnie dwoma szybkimi seriami ośmiu twardych stóp stukających w korę; krótka pauza, potem ostatnia para suchych kliknięć",
        False,
    ),
    "484": (
        "Brass rings spin inside a stone housing: a fine metallic whirl slows "
        "through two wavering passes, then a precise click marks their "
        "alignment; the ring hum lingers. " + NO_M,
        "mosiężne pierścienie wirują w kamiennej obudowie: delikatny metaliczny świst zwalnia przez dwa chwiejące obroty, potem precyzyjne kliknięcie oznacza zestrojenie; brzęczenie jeszcze chwilę trwa",
        False,
    ),
    "271": (
        "A sunbeam sweeps over concealed runes in three distinct passes; each "
        "revealed mark crackles, then the forbidden spell breaks into brittle "
        "sparks that fade away. Let the final snap dominate. " + NO_M,
        "promień słońca omiata ukryte runy trzema osobnymi przejściami; każdy odsłonięty znak trzaska, potem zaklęcie pęka w kruche iskry, które gasną. Najmocniejszy jest ostatni trzask",
        False,
    ),
    "389": (
        "An ice colossus buckles at a touch: one knee cracks into packed "
        "snow, frost plates split in two brittle bursts, then a long cold "
        "breath settles. " + NO_M,
        "lodowy kolos ugina się pod dotykiem: jedno kolano pęka w ubitym śniegu, lodowe płyty rozszczepiają się dwoma kruchymi trzaskami, potem osiada długi zimny wydech",
        False,
    ),
    "151": (
        "A golden sandstorm sweeps across the field in two gusts; each tears "
        "away an illusion with a sharp glassy snap, then grit patters down "
        "over stone. " + NO_M,
        "złota burza piaskowa przechodzi przez pole dwoma podmuchami; każdy zrywa iluzję ostrym szklistym trzaskiem, potem ziarnisty piasek bębni o kamień",
        False,
    ),
    "512": (
        "A ninja passes through a warped wall: wood bends inward in two "
        "hollow pulses, a rescuing hand grabs empty air, and the blue "
        "afterimage snaps shut. " + NO_M,
        "ninja przechodzi przez zniekształconą ścianę: drewno ugina się dwoma pustymi pulsami, wyciągnięta dłoń chwyta powietrze, a błękitny ślad zamyka się trzaskiem",
        False,
    ),
    "403": (
        "A metal carapace bursting open in three sharp cracks in a row, a long "
        "pressurised hiss of escaping gas, then droplets pattering on stone one after "
        "another. " + NO_M,
        "metalowy pancerz pęka trzema ostrymi trzaskami jeden po drugim, długi ciśnieniowy syk ulatniającego się gazu, potem krople bębniące o kamień jedna po drugiej",
        False,
    ),
    "443": (
        "At a dying fire, a villager snaps a branch; after a pause, a knife "
        "rasps slowly from its sheath, embers popping as the last log "
        "settles. " + NO_M,
        "przy dogasającym ogniu wieśniak łamie gałąź; po chwili nóż powoli wysuwa się z pochwy, żar trzaska, gdy ostatnie polano osiada",
        False,
    ),
    "288": (
        "A wedge ship powers up: the hatch hisses open, three cables snap "
        "into sockets, a rising coil buzz shakes the copper hull, one bright "
        "charge crackles. " + NO_M,
        "klinowy statek uruchamia napęd: właz syczy, trzy kable wskakują w gniazda, narastające brzęczenie cewek trzęsie miedzianym kadłubem, wyładowanie rozbłyska",
        False,
    ),
    "449": (
        "A giant tanuki rushes through Jukai in three bounding strides: paws "
        "flatten saplings, branches snap across its coat, then a close "
        "breathy huff as it bursts into a clearing. " + NO_M,
        "wielki tanuki pędzi przez Jukai trzema susami: łapy miażdżą młode drzewa, gałęzie strzelają o futro, a przy wyjściu na polanę rozlega się bliski sapnięty chuch",
        False,
    ),
    "450": (
        "Thorn canes rake a wolf's bark-hard hide in two rough passes: dry "
        "bristles scrape, several sharp thorn snaps crack, then the branches "
        "whip back through leaves. " + NO_M,
        "cierniowe pędy dwukrotnie szorują po twardej jak kora skórze wilka: suche włókna trą, kilka ostrych kolców pęka, a gałęzie odskakują przez liście",
        False,
    ),
    "545": (
        "A metal hand catching three spells in a row: three hard glassy clacks as the "
        "loudest moment, energy hissing down conduits each time, the oil tank bubbling "
        "over. " + NO_M,
        "metalowa dłoń chwyta trzy zaklęcia jedno po drugim: trzy twarde szklane klepnięcia jako najgłośniejszy moment, energia sycząca przewodami za każdym razem, zbiornik oleju kipiący",
        False,
    ),
    "561": (
        "A griffin stooping: branches rattling, prey slammed into mud, then both wings "
        "spreading in four heavy beats, two sharp beak strikes finishing the hunt. " + NO_M,
        "gryf spada: gałęzie grzechoczą, zdobycz ciskana w błoto, potem oba skrzydła rozpościerają się w czterech ciężkich uderzeniach, dwa ostre dziobnięcia kończą polowanie",
        False,
    ),
    "393": (
        "A forge devil breaks an archive pillar with three iron-bar blows: "
        "stone cracks, sharp shards ricochet across the floor, and the last "
        "impact scatters burning scrolls. " + NO_M,
        "diabeł kuźni rozbija archiwalny filar trzema uderzeniami żelaznego pręta: kamień pęka, ostre odłamki odbijają się od posadzki, a ostatnie uderzenie rozrzuca płonące zwoje",
        False,
    ),
    "255": (
        "Two drowned warriors rise from black swamp water in separate hollow "
        "whooshes; foamy water shivers, a glassy spirit hiss climbs and fades "
        "after the second apparition. " + NO_M,
        "dwaj utopieni wojownicy unoszą się nad czarną wodą dwoma osobnymi pustymi świstami; piana drży, szklisty syk ducha wznosi się i cichnie po drugim widmie",
        False,
    ),
    "87": (
        "An angel descending: five airy rushes of feathers one after another, each a "
        "dry rustling whisper in the upper range, silken pinions dragging between "
        "them. " + NO_M,
        "anioł zstępuje: pięć przewiewnych powiewów piór jeden po drugim, każdy suchym szeleszczącym szeptem w górze pasma, jedwabiste lotki wlokące się pomiędzy nimi",
        False,
    ),
    "259": (
        "A massive predator's hooked claws rake down fractured obsidian "
        "twice: the first catches with a glassy rasp, the next tears free a "
        "cascade of sharp stone slivers. " + NO_M,
        "zakrzywione szpony ogromnego drapieżnika dwukrotnie rysują pęknięty obsydian: pierwszy zgrzyt jest szklisty, drugi wyrywa kaskadę ostrych kamiennych drzazg",
        False,
    ),
    "563": (
        "A great roc lands on a sandstone shelf: three heavy wingbeats brake "
        "its descent, talons grind into the cracked ledge, a cold power stone "
        "pulses once beneath its feet. " + NO_M,
        "wielki rok ląduje na półce piaskowca: trzy ciężkie uderzenia skrzydeł hamują spadanie, szpony wgryzają się w pękniętą półkę, kamień mocy raz pulsuje pod łapami",
        False,
    ),
    "289": (
        "Three thick oil drops fall one by one onto a copper root; each wet "
        "slap rings a bright metal tick, slow sticky drips follow, and the "
        "root creaks open at the end. " + NO_M,
        "trzy gęste krople oleju spadają kolejno na miedziany korzeń; każdemu mokremu klapnięciu odpowiada jasny metaliczny tik, potem lepki ściek i skrzypnięcie korzenia",
        False,
    ),
    "94": (
        "Fortress braziers ignite one after another along the wall: separate "
        "warm whoomps, flames rising in sequence, the last bowl catching with "
        "a bright crackle and settling to a steady fire. " + NO_M,
        "ofiarne misy zapalają się po kolei wzdłuż muru: osobne ciepłe buchnięcia, płomienie wstają jeden za drugim, ostatnia misa chwyta jasnym trzaskiem i przechodzi w równy ogień",
        False,
    ),
    "219": (
        "A party crossing a crystal portal: eight bootsteps echoing one after another, "
        "a glassy chime answering each step, then the portal hum swelling and "
        "releasing them. " + NO_M,
        "drużyna przechodzi przez kryształowy portal: osiem kroków odbijających się echem jeden po drugim, szklisty dzwonek odpowiadający na każdy krok, potem nabrzmiewający brzęk portalu wypuszczający wędrowców",
        False,
    ),
    "116": (
        "Fire coils around the standing ratfolk in two rapid sweeps; each "
        "wave crackles bright over mail, sparks spit, embers scatter and "
        "fade. " + NO_M,
        "ogień oplata stojących szczurołudzi dwoma szybkimi falami; każda jasno trzaska nad kolczugą, iskry pryskają, żar rozsypuje się i gaśnie",
        False,
    ),
    "311": (
        "A muffled tavern brawl lands in three uneven thumps against the "
        "wall; a stool splinters, boots scuffle, then the last blow rings "
        "through the boards. " + NO_M,
        "stłumiona bijatyka w tawernie uderza o ścianę trzema nierównymi łomotami; stołek pęka, buty szurają, ostatni cios dźwięczy przez deski",
        False,
    ),
    "179": (
        "A heavy index book cracks open; blue sparks leap between pages in "
        "three quick jumps, sheets turn and flutter, the final arc snaps "
        "shut. " + NO_M,
        "ciężki indeks otwiera się trzaskiem; niebieskie iskry przeskakują między stronami trzema szybkimi skokami, kartki przewracają się i furkoczą, ostatni łuk trzaska",
        False,
    ),
    "547": (
        "A chrome dragon fishing: three dives in a row, talons slicing liquid metal "
        "with a sharp bright splash each time, then two heavy wingbeats lifting the "
        "catch. " + NO_M,
        "chromowy smok łowi: trzy nurkowania jedno po drugim, szpony tną ciekły metal z ostrym jasnym pluskiem za każdym razem, potem dwa ciężkie uderzenia skrzydeł unoszące zdobycz",
        False,
    ),
    "65": (
        "A levitating tome snaps open; blue light flares, pages whirl through "
        "two fast turns, ink wisps trail behind, then the book settles with a "
        "soft paper slap. " + NO_M,
        "lewitujący tom otwiera się z trzaskiem; błękitny blask wybucha, kartki wirują dwoma szybkimi obrotami, smugi atramentu podążają za nimi, księga osiada papierowym klapnięciem",
        False,
    ),
    "143": (
        "A horned mount stamps twice as a white battle banner snaps in two "
        "strong gusts; armor jingles, reins pull taut, the cloth cracks once "
        "more overhead. " + NO_M,
        "rogaty wierzchowiec dwukrotnie tupie, gdy biały sztandar bojowy trzaska na dwóch podmuchach; zbroja brzęczy, wodze się napinają, płótno pęka jeszcze raz nad głową",
        False,
    ),
    "379": (
        "A guardian dives to a balcony in two hard wingbeats, claws scrape "
        "stone to brake, then an energy bolt splashes against a blue shield "
        "with a bright crackle. " + NO_M,
        "obrońca nurkuje ku balkonowi dwoma mocnymi uderzeniami skrzydeł, szpony zgrzytają o kamień, potem pocisk energii rozbryzguje się o niebieską tarczę jasnym trzaskiem",
        False,
    ),
    "497": (
        "Electric arcs leap across gear teeth in three bursts; each snap "
        "triggers a short metallic rattle, sparks spit, the iron gears buzz "
        "as they lock. " + NO_M,
        "elektryczne łuki przeskakują po zębach przekładni trzema seriami; każdy trzask wywołuje krótki metaliczny grzechot, iskry pryskają, żelazne koła brzęczą przy blokadzie",
        False,
    ),
    "604": (
        "A bruxa feeding on marble: a body dropped hard, then fangs working "
        "twice at the throat with wet tearing, a long satisfied exhale, blood "
        "dripping.  " + NO_M,
        "bruxa pożywia się na marmurze: ciało upuszczone ciężko, potem kły pracują dwukrotnie przy gardle z mokrym darciem, długi zadowolony wydech, krew kapie",
        False,
    ),
    "19": (
        "Three candles snuffed out one after another: three soft puffs of "
        "air, each with a brief arcane crackle and a thin trail of smoke "
        "hiss.  " + NO_M,
        "trzy świece gaszone jedna po drugiej: trzy miękkie dmuchnięcia, każde z krótkim magicznym trzaskiem i cienkim sykiem dymu",
        False,
    ),
    "267": (
        "Two darts blown in a row from a blowgun: two sharp puffs of breath, "
        "two slender darts hissing through leaves, two faint thuds striking "
        "home.  " + NO_M,
        "dwa strzały z dmuchawki jeden po drugim: dwa ostre dmuchnięcia, dwie smukłe strzałki syczące wśród liści, dwa głuche stuknięcia w cel",
        False,
    ),
    "337": (
        "A bronze shield struck five times in a row: five bright metallic clangs as "
        "the loudest moment, each with a long shimmering ring-out like a small gong. " + NO_M,
        "brązowa tarcza uderzona pięć razy z rzędu: pięć jasnych metalicznych dźwięków jako najgłośniejszy moment, każdy z długim migotliwym wybrzmieniem jak mały gong",
        False,
    ),
    "490": (
        "A wooden shaft snapping: one sharp dry crack, then a long "
        "splintering tear as the halves pull apart, splinters raining down.  " + NO_M,
        "drzewce pęka: jeden suchy ostry trzask, potem długie drzazgowe darciem gdy połówki rozchodzą się, drzazgi sypią się w dół",
        False,
    ),
    "115": (
        "Three fast swirls swept through waist-deep water in a row: loud "
        "churning and splashing each time, water streaming and dripping "
        "between them.  " + NO_M,
        "trzy szybkie zamaszyste wiry przez wodę po pas jeden po drugim: za każdym razem głośne kłębowisko i plusk, woda spływa i kapie pomiędzy nimi",
        False,
    ),
    "41": (
        "Ritual shears snipping three taut cords in a row: three bright metallic "
        "scissor snips, each blade ringing thin, each cut fibre parting with a dry "
        "snap. " + NO_M,
        "rytualne nożyce przecinają trzy napięte nici jedna po drugiej: trzy jasne metaliczne cięcia, każde ostrze cienko dzwoni, każda przecięta nić pęka suchym trzaskiem",
        False,
    ),
    "59": (
        "A mage flame flaring three times above an open palm: three bright airy "
        "whooshes as the loudest moment, a steady gas hiss between them, tiny spark "
        "pops on top. " + NO_M,
        "płomień maga rozbłyska trzy razy nad otwartą dłonią: trzy jasne powiewy jako najgłośniejszy moment, między nimi jednostajny syk gazu, nad tym trzaski iskier",
        False,
    ),
    "13": (
        "Three gentle healing pulses sent one after another: three soft warm chime "
        "swells as the loudest moment, golden sparkles drifting down like dust between "
        "them. " + NO_M,
        "trzy łagodne impulsy uzdrawiania jeden po drugim: trzy miękkie ciepłe uderzenia dzwonu jako najgłośniejszy moment, złote iskry opadające jak pył pomiędzy nimi",
        False,
    ),
    "519": (
        "A dragon breathing in the canopy: four slow deep breaths in a row as the "
        "loudest moment, each with a long hiss of venomous vapour curling from the "
        "nostrils. " + NO_M,
        "smok oddycha w koronach drzew: cztery powolne głębokie oddechy jeden po drugim jako najgłośniejszy moment, każdy z długim sykiem jadowitej pary z nozdrzy",
        False,
    ),
    "584": (
        "A falcon returning to the glove: three heavy wing beats braking hard as the "
        "loudest moment, talons closing on the padded brace, a soft chirr as the hood "
        "slips on. " + NO_M,
        "sokół wraca na rękawicę: trzy ciężkie uderzenia skrzydeł hamujących jako najgłośniejszy moment, szpony zaciskają się na rękawicy, miękkie ćwierknięcie gdy kaptur się nasuwa",
        False,
    ),
    "294": (
        "A tumbleweed rising: three long drags of dry brittle branches over hard "
        "ground as the loudest moment, thin twigs cracking and snapping, dust grit "
        "spraying. " + NO_M,
        "żywiołak z chwastów powstaje: trzy długie pociągnięcia suchych kruchych gałęzi po twardej ziemi jako najgłośniejszy moment, cienkie patyki trzaskają i pękają, pryska kurz i żwir",
        False,
    ),
    "526": (
        "Violet energy pouring over steel plate in three waves: three bright crackling "
        "surges as the loudest moment, armour plates ringing and straining, sparks "
        "spitting. " + NO_M,
        "fioletowa energia spływa na stalowy pancerz trzema falami: trzy jasne trzaskające uderzenia jako najgłośniejszy moment, płyty pancerza dzwonią i pracują, pryskają iskry",
        False,
    ),
    "145": (
        "A cloning pod bursts open in a chain, the first metal bang the "
        "loudest: a shrill metallic ring, then more seal pops and hatches "
        "giving way, thick liquid splashing over iron plates to the end." + NO_M,
        "komora klonująca pęka łańcuchowo, pierwszy metaliczny huk najgłośniejszy: piskliwy metaliczny dzwon, potem kolejne uszczelki i włazy ustępują, gęsty płyn chlapie o żelazne płyty do końca",
        False,
    ),
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
