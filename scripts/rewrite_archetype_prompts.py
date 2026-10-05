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

# Karty, których prompt musi zostać ręczny (fabuła narzuca konkretne źródło).
OVERRIDES: dict[str, tuple[str, str, bool]] = {
    "515": ("A war gunship's engine: a deep throbbing turbine rumble with heavy rotor blades "
            "beating the air and a metallic rattle of the hull. " + NO_M,
            "gunship: głęboki turbinowy pomruk z biciem ciężkich łopat wirnika i grzechotem kadłuba", False),
    "7": ("A mind stab: an instant piercing psychic shriek, a high tonal scream swelling inside "
          "the skull and cutting off. " + NO_M,
          "pchnięcie psychiczne: natychmiastowy przenikliwy tonalny krzyk w czaszce, urywa się", False),
    "312": ("A goblin jester cackling: a series of sharp mocking cackles, five rapid jeering "
            "bursts, high and cruel. " + NO_M,
            "chichot błazna: seria ostrych kpiących chichotów, pięć szybkich wybuchów", False),
    "521": ("Forest birds at dawn: several distinct whistled bird songs and chirps answering each "
            "other, clear and tonal. " + NO_M,
            "ptaki o świcie: kilka wyraźnych gwizdanych zawołań odpowiadających sobie", False),
    "557": ("Village folk music: a fiddle playing a lively dance tune over a hand drum, warm and "
            "rustic, feet stamping the beat. " + NO_S,
            "wiejska muzyka: skrzypce grają żywą taneczną melodię nad bębenkiem, stopy wybijają rytm", True),
    "568": ("A sentinel robot's servos: a smooth continuous mechanical whirr with a steady hum, "
            "a hydraulic hiss and a precise click at the end. " + NO_M,
            "serwo sentinela: ciągłe gładkie warczenie mechanizmu z syknięciem hydrauliki i kliknięciem", False),
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


def build(row: dict) -> dict | None:
    sid = str(row["story_id"])
    archetype = row.get("archetype")
    if sid in OVERRIDES:
        prompt, pl, music = OVERRIDES[sid]
    elif archetype in TEMPLATES:
        prompt, pl, music = TEMPLATES[archetype]
    else:
        return None
    tail = NO_S if music else NO_M
    clause = card_clause(row)
    body = prompt
    for t_ in TAILS:
        body = body.replace(t_, "")
    prompt = f"{body.rstrip()} {clause.strip()} {tail}"
    return {"prompt": prompt, "sample_scenario": pl, "music_allowed": music,
            "duration_seconds": DURATION}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", type=Path, default=ROOT / "data/samples/scenarios.jsonl")
    ap.add_argument("--audit", type=Path,
                    default=ROOT / "data/samples/archetype-match-2026-10-05-after-r016b.json")
    ap.add_argument("--ids", default="", help="lista ID po przecinku")
    ap.add_argument("--families", default="", help="archetypy do wyboru, po przecinku")
    ap.add_argument("--worst-per-family", type=int, default=0,
                    help="ile najgorszych kart z każdego archetypu (wg punktacji kontraktu)")
    ap.add_argument("--batch", default="r017a")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    rows = [json.loads(l) for l in args.scenarios.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_id = {str(r["story_id"]): r for r in rows}
    wanted: list[str] = [s.strip() for s in args.ids.split(",") if s.strip()]

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
        print(f"{sid:>4} {row.get('title','')[:24]:<24} {row.get('archetype'):<18} "
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
