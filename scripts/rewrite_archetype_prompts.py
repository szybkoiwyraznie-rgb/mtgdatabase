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
    "7": ("A mind stab: a sudden piercing shriek at full volume from the very first "
          "millisecond, no fade-in at all, a high tonal scream cut off short. " + NO_M,
          "pchnięcie psychiczne: nagły przenikliwy krzyk od pierwszej milisekundy, bez narastania", False),
    # 31 i 456: kontrakt chce harmonicznego bzyczenia, a „suchy szelest" dał szum 8,5-9,3 kHz.
    # 568: tonal_frame_fraction 0,000 — serwo wyszło szumowe, ma być ton o stałej wysokości.
    # r023 (kliki przecinające ton) dał najwyżej onset 1 i stonizowany ton
    # (0,767 / f0_std 3,3) — model rozstrzyga konflikt ton-vs-klik kosztem tonu.
    # Próg klików jest dobrze skalibrowany: mediana korpusu 4, a pozostałe karty
    # robot_servo mają 2-29, więc to realna wada, nie zły próg.
    # r024 odwraca hierarchię: rytm jest zdarzeniem głównym, ton — tłem.
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
    "52": ("A clockwork mechanism turning: a row of low dull wooden knocks in a steady rhythm, "
           "deep and soft-edged, with no bright ticking and no hiss. " + NO_M,
           "mechanizm zegarowy: rząd niskich głuchych drewnianych stuków, bez jasnego cykania i syku", False),
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
    "218": ("Three tanks of dark green substance bubbling in turn: each one gives two or three thick wet blorp sounds, one tank after the next across the whole take.",
            "trzy zbiorniki ciemnozielonej substancji bulgoczą po kolei: każdy daje dwa-trzy grube mokre bulgoty", False),
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
    "470": ("A sacrifice of fertile soil, then two trees bursting apart in ash: two successive deep woody explosions, each with a shower of crackling embers.",
            "ofiara z żyznej gleby i wybuch dwóch drzew w popiele: dwie kolejne głębokie drewniane eksplozje z deszczem trzaskających iskier", False),
    "482": ("Two blades meeting edge to edge and pressing on: three violent steel strikes in "
           "quick succession, the first at the very first instant, each with a harsh gritty ring.",
            "dwa ostrza schodzą się krawędziami i napierają: trzy gwałtowne ciosy stali kolejno, pierwszy w pierwszej chwili, każdy z chropawym brzękiem", False),
    "487": ("A geometric resonance shield breaking a fire projectile: four successive sharp crystalline shatter bursts as the shield facets break one by one.",
            "geometryczna tarcza rezonansu rozbija ognisty pocisk: cztery kolejne ostre krystaliczne pęknięcia, faseta po fetce", False),
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
    "250": ("A steel blade snapping back together: one bright hard clash at the very first instant, then four short sharp metallic clicks as the crack seals, each with a gritty shimmer.",
            "ostrze scala się po pęknięciu: jeden jasny twardy szczęk w pierwszej chwili, potem cztery ostre metaliczne kliki", False),
    "73": ("A golden construct's blade snapping out and striking: an instant bright steel hit at the very first moment, then three more crisp clashes with a harsh metallic ring.",
            "ostrze konstrukta wysuwa się i uderza: natychmiastowy jasny cios stali, potem trzy kolejne szczęki z ostrym brzękiem", False),
    "344": ("Crossed kavu blades: one violent steel strike landing at the very first instant, then three more harsh gritty clashes in quick succession ringing across the whole take.",
            "krzyżowe ostrza kavu: jeden gwałtowny cios w pierwszej chwili, potem trzy chrapliwe szczęki kolejno", False),
    "525": ("A rapier thrust throwing a wave of glacial spikes: one instant bright steel impact, then four sharp cracking strikes as the ice splinters, each with a glassy metallic ring.",
            "fala lodowcowych kolców od ciosu rapiera: natychmiastowy jasny cios, potem cztery ostre trzaski pękanego lodu", False),
    "594": ("A sword wrenched out of mud and struck: an instant hard bright steel clash at the very first moment, then three more gritty ringing strikes.",
            "miecz wyrwany z błota i cios: natychmiastowy twardy szczęk stali, potem trzy chrapliwe dzwoniące uderzenia", False),
    "140": ("A fighter rolling up from a packed yard: five separate steel plates clanking one "
           "after another, each distinct, sharply struck and mid-pitched, with a gritty scrape.",
            "przewrotka po ubitym placu: pięć osobnych płyt zbroi dzwoni kolejno, każda wyraźna i ze środka pasma", False),
    "232": ("A goblin shifting in oversized plate armour: six uneven dull steel clanks, each plate knocking separately, mid-pitched and weighty, with short scrapes between.",
            "goblin przestępuje w za dużej zbroi: sześć nierównych głuchych brzęków, każda płyta osobno, ze środka pasma", False),
    "16": ("A heavy breastplate lifted off a stone table: four separate steel plates clanking one after another, each distinct and sharply struck, mid-pitched with body.",
            "podniesienie ciężkiego napierśnika ze stołu: cztery osobne płyty dzwonią kolejno, każda wyraźna i z ciałem", False),
    "460": ("A horned breastplate buckled onto a young centaur: five firm knocks of plate against plate, each separate and mid-pitched, with a short leather creak between.",
            "dopasowanie rogowego napierśnika: pięć mocnych stuków płyty o płytę, każdy osobny, ze środka pasma", False),
    "176": ("Two clawed kicks landing on plate armour: one heavy blow then a lighter one, followed by four separate steel plates clanking loose, each distinct and mid-pitched.",
            "podwójne kopnięcie szponów w płytową zbroję: jedno ciężkie, jedno lżejsze, potem cztery osobne płyty dzwonią", False),
    "194": ("A warhorse's steel caparison rattling: seven quick separate plate chinks in an uneven cluster, each mid-pitched and sharply struck, ending in a short scrape.",
            "grzechot stalowego kropierza rumaka: siedem szybkich osobnych brzęków w nierównej grupie, ze środka pasma", False),
    "56": ("Chitin plates snapping shut one after another: six short dry clicks, each distinct and mid-pitched, evenly spaced with a faint gritty edge.",
            "chitynowe płytki zatrzaskują się kolejno: sześć krótkich suchych klików, każdy wyraźny i ze środka pasma", False),
    "355": ("Armour and keepsakes set down on a workbench: five separate steel plates clanking one after another, each distinct and mid-pitched, with a dull wooden knock beneath.",
            "odkładanie zbroi na stół warsztatu: pięć osobnych płyt dzwoni kolejno, każda wyraźna, z głuchym drewnianym stukiem", False),
    "39": ("An orc stamping into soft mud: five heavy sodden footsteps in a steady even rhythm, each deep and low with a wet mud splash, filling the whole take.",
            "grząskie tupnięcie orka w błocie: pięć ciężkich mokrych kroków równym rytmem, każdy niski z rozbryzgiem", False),
    "442": ("A rank of defenders stamping in unison: four heavy boot stamps in a strict even rhythm, each one deep and low with a grounded thud.",
            "równoczesne tupnięcie szeregu obrońców: cztery ciężkie kroki w ścisłym równym rytmie, każdy głęboki i niski", False),
    "565": ("Dew dripping into a wooden bowl in a forest clearing: six clear piped drops in an uneven rhythm, each with a soft tonal plink, and small bird chirps answering between them.",
            "krople rosy do drewnianej czary: sześć czystych dzwięcznych kropli w nierównym rytmie, z ptasimi świergotami między nimi", False),
    "434": ("A mizzium reactor overloading: a very low throbbing engine note with thick bass building under four heavy rhythmic metallic pounds, gritty in the mid-range.",
            "przeciążenie reaktora mizzium: bardzo niski pulsujący ton z grubym basem i czterema ciężkimi rytmicznymi uderzeniami", False),
    "2": ("A stone thrown into deep water: one bright hard splash at the very first instant, then a hissing spray of droplets and three smaller plops spreading outward.",
            "kamień rzucony w głęboką wodę: jeden jasny twardy plusk w pierwszej chwili, potem syk drobnego rozbryzgu i trzy mniejsze pluski", False),
    "559": ("A sharp cat screech starting at the very first instant, then two more rasping cries, each with a leathery wing snap underneath.",
            "ostry skrzek kota od pierwszej chwili, potem dwa chrapliwe zawołania, każde z trzaskiem skórzastych skrzydeł", False),
    "292": ("A slow building gust: a swelling hissing rush of turbulent air that grows, then holds at a steady level continuously through the whole second half of the take.",
            "powoli narastający podmuch: wzbierający szumiący pęd powietrza, który rośnie, a potem trwa równo przez całą drugą połowę", False),
    "173": ("A warrior's roar taking bear form: a long deep chest roar with enormous low-frequency body underneath, dark and massive, sustained across the whole take.",
            "ryk wojownika przybierającego postać niedźwiedzia: długi głęboki piersiowy ryk z olbrzymim niskim ciałem pod spodem, masywny", False),
    "478": ("Claws raking a hard glassy barrier: a bright scraping screech then a shattering burst of many small glass shards ticking down, at least eight separate tinkling impacts.",
            "zgrzyt pazurów po szklistej barierze: jasny pisk zgrzytu, potem pęknięcie z gradem odłamków, co najmniej osiem osobnych dzwięków", False),
    "26": ("A molten beast's heavy step: a deep low grinding slide of cracked rock, rumbling and rolling across the whole take with crackling fissures beneath.",
            "ciężki krok żarnej bestii: głęboki niski zgrzyt osuwających się pękniętych skał, toczy się przez cały sample", False),
    "129": ("A forging hammer striking steel armour in a raised salute: four hard bright hammer blows in a steady rhythm, each with a sharp metallic ring that dies quickly.",
            "kuty młot uderza o stalowy pancerz: cztery twarde jasne uderzenia równym rytmem, każde z ostrym brzękiem, który szybko gaśnie", False),
    "23": ("An iron monastery bell struck once and left to ring: a mid-pitched struck tone that swells and sustains evenly across the whole take, with a faint second hum beneath.",
            "żelazny dzwon klasztorny uderzony raz i zostawiony: ton ze środka pasma narasta i równo wybrzmiewa przez cały sample", False),
    "522": ("Luminous chains snapping taut around a running beast: a long bright rattling cascade of many small links, at least ten separate metallic ticks across the whole take.",
            "świetliste łańcuchy napinają się na biegnącej bestii: długa jasna kaskada grzechotu wielu ogniw, co najmniej dziesięć osobnych stuków", False),
    "244": ("A stone monolith pushed out of clay soil in a forest: four deep gritty scraping pushes in an even rhythm, with tonal bird calls answering between them.",
            "kamienny monolit wypychany z gliny w lesie: cztery głębokie chropawe pchnięcia równym rytmem, z dzwięcznymi ptasimi zawołaniami między nimi", False),
    "12": ("A dock robot's servo running: a smooth continuous tonal hum at a steady pitch with an even buzzing undertone, plus two soft mechanical clicks, held for the whole take.",
            "serwo robota dźwigowego: gładki ciągły tonalny pomruk o stałej wysokości z równym brzęczeniem i dwoma miękkimi klikami", False),
    "5": ("An arcane spell igniting: a bright crystalline shimmer high in the treble, sparkling glassy overtones rising, swelling and holding steadily across the whole take.",
            "zaklęcie zapala się: jasne krystaliczne migotanie wysoko w górze pasma, szkliste iskry narastają i trwają przez cały sample", False),
    "253": ("An elven bard's lute at dawn: a short plucked phrase of five or six separate clear string notes played with even rhythm, warm and bright.",
            "lutnia elfiego barda o świcie: krótka fraza z pięciu-sześciu osobnych wyraźnych dźwięków strun w równym rytmie", False),
    # --- r029: 33 karty, kazda z DOKLADNIE jednym zlamanym progiem kontraktu.
    # Prompt celuje w ta jedna ceche. Uwaga: insect_swarm potrzebuje raz
    # nizszego centroidu (98, 106, 456, 81), a raz wiecej tonalnosci (31, 540) -
    # dlatego tylko wpisy per karta, profil rodzinny by je pogodzic nie mogl.
    "308": ("A greatsword clashing: one brutal steel impact built from harsh broadband scraping noise, gritty and rough, with no smooth pitched ring underneath.",
            "cios wielkiego miecza: brutalne uderzenie z chrapliwego szerokopasmowego zgrzytu, bez gładkiego tonu", False),
    "9": ("A gust of wind: broadband hissing white noise of turbulent air, swelling and easing, with no whistle, no pitched note and no tonal hum anywhere in it.",
            "podmuch wiatru: szerokopasmowy szumiący szum białego turbulentnego powietrza, bez gwizdu i bez tonu", False),
    "67": ("A war machine's engine: a deep rumble kept low in level, with loud gritty metallic knocking and clanking clearly forward in the middle of the range.",
            "silnik machiny: głęboki pomruk nisko, a głośny chrapliwy metaliczny stukot wyraźnie w środku pasma", False),
    "80": ("An armored vehicle idling: a moderate low engine rumble under loud gritty mechanical clatter and metal knocking that sits forward in the mid range.",
            "opancerzony pojazd na biegu: umiarkowany pomruk pod głośnym chrapliwym metalicznym terkotem w środku", False),
    "501": ("A double plasma volley from a reactor: two heavy blasts with a low thump, over loud gritty metallic knocking and clanking carried clearly in the middle of the range.",
            "podwójna salwa plazmowa: dwa ciężkie wybuchy z basowym łupnięciem, nad głośnym metalicznym stukotem w środku", False),
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
    "17": ("One hard bright steel strike at the very first instant, no build-up, and that strike is a harsh broadband burst of gritty metallic noise, rough-edged, not a clean ring.",
            "dwa ostrza krawędziami: jeden twardy jasny cios w pierwszej chwili, z chrapliwego szerokopasmowego szumu stali", False),
    "20": ("A sword hitting a sword: an instantaneous hard bright impact at the very first sample, made of harsh broadband gritty metal noise with a rough noisy edge, no smooth pitch.",
            "miecz uderza o miecz: natychmiastowy twardy jasny cios z chrapliwego szumu, bez gładkiego tonu", False),
    "345": ("A porcelain blade striking: one hard impact with zero wind-up at the very start, built from harsh broadband gritty ceramic-and-steel noise, bright and rough-edged.",
            "porcelanowe ostrze uderza: twarde uderzenie bez zamachu, z chrapliwego szerokopasmowego szumu", False),
    "435": ("A crimson blade striking as it crystallises: an instant hard bright impact in the very first moment, a harsh broadband burst of gritty metal noise with no clean ring.",
            "karmazynowe ostrze uderza: natychmiastowy twardy jasny cios, chrapliwy szerokopasmowy szum bez tonu", False),
    "608": ("Two blades meeting edge to edge: a sudden hard bright steel clash at the very first instant, harsh broadband gritty noise, rough rather than ringing.",
            "dwa ostrza krawędziami: nagły twardy jasny szczęk w pierwszej chwili, chrapliwy szum bez dzwonienia", False),
    "98": ("One steady pitched drone held unbroken from start to finish with a clear fundamental note, buzzing in the middle of the range, warm and rounded, with no high whine and no hiss above it.",
            "rój osiada na drewnie: jeden równy bzyk trzymany bez przerwy z wyraźnym tonem, w środku pasma, bez pisku", False),
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
    "531": ("Heavy doors: a drawn-out tonal creak ringing on past a second with a steady medium pitch wobble, about five or six fluctuations a second rather than one slow slide.",
            "przeciągłe tonalne skrzypienie ponad sekundę ze średnim falowaniem wysokości pięć-sześć razy na sekundę", False),
    "103": ("A broad gust that builds slowly over a third of a second and holds, broadband hissing air noise whose weight sits low - deep rumbling air, no bright hiss on top.",
            "wiatr w gałęziach: szeroki podmuch narastający powoli i trzymany, o ciężarze nisko, bez jasnego syku", False),
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
    "4": ("A body slamming into a pool: a bright wide hissing spray of water droplets flying up, sharp and sparkling in the upper range, with only a brief gurgle under it.",
            "ciało wpada do wody: jasny szeroki syk kropel rozbryzgujących się w górę, ostry i iskrzący w górze pasma", False),
    "40": ("Thick armour plates knocked together: two or three mid-pitched metal clanks, weighty and dull rather than bright, each plate struck separately.",
            "grube płyty pancerza zderzają się: dwa-trzy klanki w środku pasma, ciężkie i matowe raczej niż jasne", False),
    "96": ("A stream of emerald magic: one continuous flowing shimmering tone with a clear sustained pitch and bright sparkling overtones, smooth and even throughout.",
            "strumień szmaragdowej magii: jeden ciągły płynący migotliwy ton o wyraźnej wysokości i jasnych iskrzących alikwotach", False),
    "113": ("A drone's servo locking: one clear continuous electronic tone at a fixed pitch, dominant and unbroken like a tuning fork, with just two faint clicks over it.",
            "serwo drona się blokuje: jeden wyraźny ciągły elektroniczny ton o stałej wysokości, dominujący jak kamerton, z dwoma cichymi klikami", False),
    "118": ("A monster's close roar: a guttural bellow sitting clearly in the low middle of the range, rough and raspy, well above a pure sub-bass rumble.",
            "bliski ryk potwora: gardłowy wrzask wyraźnie w niskim środku pasma, chropawy, dobrze ponad czystym infrabasem", False),
    "126": ("Wild birds feeding from a hand: several clear melodic chirps on distinct notes, each one tonal and bright, with soft wing flutters between them.",
            "dzikie ptaki karmione z ręki: kilka wyraźnych melodyjnych świergotów na różnych nutach, każdy tonalny i jasny", False),
    "156": ("A heavy flat stone slab slamming onto marble: one massive crushing impact with deep weighty low frequency thud, then a short sharp crack of stone.",
            "ciężka kamienna płyta uderza o marmur: jedno miazdzące uderzenie z głębokim basowym łupnięciem, potem krótki ostry trzask", False),
    "164": ("A great winged creature taking off: several crisp wingbeats with a bright leathery snap and a high rushing hiss of air, each beat clearly in the middle of the range.",
            "wielka skrzydlata istota startuje: kilka sprężystych uderzeń skrzydeł z jasnym skórzanym trzaskiem i wysokim pędem powietrza", False),
    "216": ("A stitched skaab shifting its armour: two hard sharp metal plate strikes that peak abruptly and separately, each far more sudden than the scraping around it.",
            "zszyty skaab porusza pancerzem: dwa ostre twarde uderzenia blachy osiągające szczyt nagle i osobno, znacznie gwałtowniejsze niż zgrzyt wokół", False),
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
    "558": ("A bronze temple bell struck once: a low mid-range tone that holds a steady even level while it rings rather than fading quickly, sustained to the end.",
            "brązowy dzwon świątynny uderzony raz: niski ton w środku pasma trzymający równy poziom, nie gasnący szybko", False),
    "562": ("A thunderclap overhead: one very sharp sudden crack that peaks hard and abruptly, then a deep rolling rumble fading slowly.",
            "grzmot nad głową: jeden bardzo ostry nagły trzask osiągający szczyt twardo i nagle, potem głęboki toczący się pomruk", False),
    # --- r032: 14 kart wybranych pomiarem, nie zgadywaniem. 269 - kontrakt
    # attack_s przy dzwieku wieloudarzeniowym wymaga, zeby najglosniejszy byl
    # PIERWSZY cios (attack_s liczy sie wstecz od globalnego szczytu). Reszta to
    # karty, ktore w r031 drgnely ku celowi albo dostaly nowa metryke po
    # naprawieniu poprzedniej.
    "269": ("One piercing hawk screech as the loudest moment of the take, hitting hard at the very first instant, bright and high, with two quick wingbeats after it kept clearly quieter than the cry.",
            "jastrząb: jeden przenikliwy krzyk jako najgłośniejszy moment, uderzający w pierwszej chwili, potem dwa cichsze uderzenia skrzydeł", False),
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
