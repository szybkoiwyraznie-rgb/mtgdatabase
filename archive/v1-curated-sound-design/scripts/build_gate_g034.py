#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g034 — kolejna paczka 5 braków po g033.

Zakres (po 3 kandydatów):
  1) background:step-rownina          — 19 braków, anchory 10/230/396/492
  2) background:kuznia-warsztat       — 19 braków, anchory 16/168/285/355/487
  3) background:krypta-nekropolia     — 15 braków, anchory 42/72/543/600
  4) hero:furkot-mechanizmu           — 16 braków, anchory 19/132/146/228/484
  5) hero:huk-ognia                   — 16 braków, anchory 59/102/209/287/290/314/436/496/507/513

Źródła: istniejące paczki Sample Scout (Freesound CC0) oraz atomcut/OpenGameArt/Kenney CC0.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
from build_gate_g003 import soft_limit  # noqa: E402

GATE = REPO / "data" / "gates" / "g034"
CAND = GATE / "candidates"
ATOM = Path("/tmp/atomcut_probe")


def load_scout_manifest(dir_name: str) -> dict[str, dict]:
    data = json.loads((REPO / "legacy" / "source" / "sample_scout" / dir_name / "manifest.json").read_text(encoding="utf-8"))
    return {Path(item["file"]).name: item for item in data}


def scout_source(item: dict, notes: str) -> dict:
    lic = item.get("license") or "brak informacji"
    if lic == "http://creativecommons.org/publicdomain/zero/1.0/":
        lic = "CC0 1.0 (public domain; wg API Freesound)"
    return {
        "title": f"{item.get('name')} (Freesound)",
        "author": item.get("author") or "brak informacji",
        "license": lic,
        "url": item.get("source_url") or item.get("comments") or "brak informacji",
        "channel": f"sample-scout (preview-hq-mp3); manifest: {item.get('source_id')}",
        "notes": notes,
    }


def atom_source(pack: str, title: str, author: str, notes: str) -> dict:
    return {
        "title": f"{title} (OpenGameArt/Kenney mirror)",
        "author": author,
        "license": "CC0 1.0 (public domain)",
        "url": f"https://opengameart.org/content/{pack}" if not pack.startswith("kenney") else "https://kenney.nl/assets/category:Audio",
        "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
        "notes": notes,
    }


def ensure_sources() -> None:
    needed = [
        REPO / "legacy/source/sample_scout/freesound_battle-swords/03-667115-mongolian-film-windblown-steppe1-wav.mp3",
        REPO / "legacy/source/sample_scout/freesound_battle-swords/02-486295-r27-37-metal-clanks-and-hits-wav.mp3",
        REPO / "legacy/source/sample_scout/freesound_battle-swords/01-767323-weapswrd-sword-blades-grinding-hvd-owsfx.mp3",
        REPO / "legacy/source/sample_scout/freesound_quiet-room-tone/01-637805-room-tone-quiet-cellar-with-distant-noises-flac.mp3",
        REPO / "legacy/source/sample_scout/freesound_quiet-room-tone/03-406507-room-tone-hotel-room-quiet-very-distant-voices-a.mp3",
        REPO / "legacy/source/sample_scout/freesound_battle/01-557594-battle-mech-walks-fast-slow-sequence.mp3",
        ATOM / "packs/opengameart-30-cc0-sfx-loops/audio/saw.m4a",
        ATOM / "packs/opengameart-30-cc0-sfx-loops/audio/ambient-02.m4a",
        ATOM / "packs/opengameart-30-cc0-sfx-loops/audio/machine-04.m4a",
        ATOM / "packs/opengameart-100-cc0-metal-and-wood-sfx/audio/metal-spring-01.m4a",
        ATOM / "packs/kenney-sci-fi-sounds/audio/engine-circular-000.m4a",
        ATOM / "packs/kenney-sci-fi-sounds/audio/thruster-fire-000.m4a",
        ATOM / "packs/opengameart-superpowers-assets-sound-effects/audio/flame-thrower.m4a",
        ATOM / "packs/opengameart-25-cc0-bang-firework-sfx/audio/fw-01.m4a",
    ]
    missing = [str(p) for p in needed if not p.exists()]
    if missing:
        raise SystemExit("Brak źródeł do g034:\n" + "\n".join(missing))


def clean_gate() -> None:
    if GATE.exists():
        shutil.rmtree(GATE)
    CAND.mkdir(parents=True, exist_ok=True)


def process_wave(wave: np.ndarray, target_db: float, fade_in=0.08, fade_out=0.35,
                 highpass: float | None = None, lowpass: float | None = None,
                 length: float | None = None, mono=False) -> np.ndarray:
    seg = wave.copy()
    if mono and seg.shape[0] > 1:
        m = seg.mean(axis=0, keepdims=True)
        seg = np.repeat(m, 2, axis=0)
    if length is not None:
        want = int(length * dsp.SR)
        if seg.shape[1] < want:
            seg = dsp.loop_to_length(seg, want)
        else:
            seg = seg[:, :want]
    if highpass:
        sos = butter(4, highpass, btype="highpass", fs=dsp.SR, output="sos")
        seg = sosfiltfilt(sos, seg, axis=-1)
    if lowpass:
        sos = butter(4, lowpass, btype="lowpass", fs=dsp.SR, output="sos")
        seg = sosfiltfilt(sos, seg, axis=-1)
    seg = dsp.fade(seg, fade_in, fade_out)
    seg = dsp.normalize_rms(seg, target_db)
    return dsp.peak_ceiling(seg, 0.92)


def render_segment(src: Path, out: Path, start: float, end: float, target_db: float,
                   length: float | None = None, **kw) -> tuple[float, float, float]:
    wave, _ = dsp.load_any(src)
    seg = dsp.cut(wave, start, end).copy()
    del wave
    seg = process_wave(seg, target_db, length=length, **kw)
    dsp.encode_mp3(out, seg)
    return round(seg.shape[1] / dsp.SR, 2), round(dsp.rms_db(seg), 1), round(dsp.spectral_share(seg, 6000.0), 3)


def render_full(src: Path, out: Path, target_db: float, length: float | None = None, hero=False, **kw) -> tuple[float, float, float]:
    wave, _ = dsp.load_any(src)
    seg = process_wave(wave, target_db, length=length, **kw)
    del wave
    if hero:
        seg = soft_limit(seg, crest_db=13.0, rounds=4)
        seg = dsp.normalize_rms(seg, target_db)
        seg = dsp.peak_ceiling(seg, 0.92)
    dsp.encode_mp3(out, seg)
    return round(seg.shape[1] / dsp.SR, 2), round(dsp.rms_db(seg), 1), round(dsp.spectral_share(seg, 6000.0), 3)


def bg_candidate(label: str, title: str, fname: str, entry_id: str, typ: str,
                 setting: str, desc: str, src: Path, source: dict,
                 start=0.0, end: float | None = None, target_db=-32.0, length=8.0,
                 traits=None, bad_for=None, **kw) -> dict:
    if end is None:
        dur, rms, hf = render_full(src, CAND / fname, target_db, length=length, **kw)
        window = "pełny/loop"
    else:
        dur, rms, hf = render_segment(src, CAND / fname, start, end, target_db, length=length, **kw)
        window = f"{start:.1f}–{end:.1f} s"
    desc2 = f"{desc} (okno {window}, RMS {rms} dB, HF>6k {hf:.1%})"
    return {
        "label": label,
        "title": title,
        "file": f"candidates/{fname}",
        "desc": desc2,
        "source": source["title"],
        "entry": {
            "id": entry_id,
            "setting": setting,
            "desc": desc2,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": dur,
            "level_ref_db": target_db,
            "loopable": True,
            "semantics": {"type": typ, "traits": traits or [], "bad_for": bad_for or []},
            "source": source,
        },
    }


def hero_candidate(label: str, title: str, fname: str, entry_id: str, typ: str,
                   role: str, character: str, desc: str, src: Path, source: dict,
                   start=0.0, end: float | None = None, target_db=-15.0,
                   traits=None, bad_for=None, good_for="", bad_for_txt="", **kw) -> dict:
    if end is None:
        dur, rms, hf = render_full(src, CAND / fname, target_db, hero=True, **kw)
        window = "pełny"
    else:
        dur, rms, hf = render_segment(src, CAND / fname, start, end, target_db, **kw)
        window = f"{start:.1f}–{end:.1f} s"
    desc2 = f"{desc} (okno {window}, czas {dur:.2f} s, RMS {rms} dB, HF>6k {hf:.1%})"
    return {
        "label": label,
        "title": title,
        "file": f"candidates/{fname}",
        "desc": desc2,
        "source": source["title"],
        "entry": {
            "id": entry_id,
            "role": role,
            "character": character,
            "distance": "bliski",
            "energy": "średnia",
            "duration_sec": dur,
            "desc": desc2,
            "good_for": good_for,
            "bad_for": bad_for_txt,
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "semantics": {"type": typ, "traits": traits or [], "bad_for": bad_for or []},
            "source": source,
        },
    }


def build_manifest() -> dict:
    swords = load_scout_manifest("freesound_battle-swords")
    quiet = load_scout_manifest("freesound_quiet-room-tone")
    battle = load_scout_manifest("freesound_battle")
    fire = load_scout_manifest("freesound_fireplace-crackle")

    wind_item = swords["03-667115-mongolian-film-windblown-steppe1-wav.mp3"]
    clank_item = swords["02-486295-r27-37-metal-clanks-and-hits-wav.mp3"]
    grind_item = swords["01-767323-weapswrd-sword-blades-grinding-hvd-owsfx.mp3"]
    cellar_item = quiet["01-637805-room-tone-quiet-cellar-with-distant-noises-flac.mp3"]
    hotel_item = quiet["03-406507-room-tone-hotel-room-quiet-very-distant-voices-a.mp3"]
    mech_item = battle["01-557594-battle-mech-walks-fast-slow-sequence.mp3"]
    camp_item = fire["05-809834-camp-fire-2.mp3"]

    wind = REPO / wind_item["file"]
    clank = REPO / clank_item["file"]
    grind = REPO / grind_item["file"]
    cellar = REPO / cellar_item["file"]
    hotel = REPO / hotel_item["file"]
    mech = REPO / mech_item["file"]
    camp = REPO / camp_item["file"]

    step_traits = ["otwarta przestrzeń", "wiatr", "suchy teren", "brak wnętrza"]
    step_bad = ["wnętrze", "miasto", "gęsty las", "podziemia"]
    step = [
        bg_candidate("s.1", "łagodny wiatr po równinie", "bg_steppe_wind_soft_01.mp3", "steppe_wind_soft_01",
                     "step-rownina", "step / otwarta równina", "szeroki wiatr bez ścian, ludzi i ptaków — neutralna otwarta przestrzeń",
                     wind, scout_source(wind_item, "Mongolian windblown steppe: okno 8–16 s"), 8, 16, traits=step_traits, bad_for=step_bad, highpass=45, lowpass=10500),
        bg_candidate("s.2", "szorstki wiatr traw", "bg_steppe_wind_grass_01.mp3", "steppe_wind_grass_01",
                     "step-rownina", "step / wiatr po trawach", "bardziej ziarnisty pęd powietrza, jak sucha trawa na rozległym trakcie",
                     wind, scout_source(wind_item, "Mongolian windblown steppe: okno 70–78 s"), 70, 78, traits=step_traits, bad_for=step_bad, highpass=45, lowpass=10500),
        bg_candidate("s.3", "pusty płaskowyż w wietrze", "bg_steppe_wind_empty_01.mp3", "steppe_wind_empty_01",
                     "step-rownina", "step / pusty płaskowyż", "najbardziej puste okno: stabilny wiatr bez zdarzeń, dobre pod samotną równinę",
                     wind, scout_source(wind_item, "Mongolian windblown steppe: okno 126–134 s"), 126, 134, traits=step_traits, bad_for=step_bad, highpass=45, lowpass=10500),
    ]

    workshop_traits = ["metal", "narzędzia", "warsztat", "uderzenia"]
    workshop_bad = ["cisza rytuału", "las", "morze", "sielski plener"]
    loop_src = atom_source("30-cc0-sfx-loops", "30 SFX loops", "rubberduck", "audio/saw.m4a; loop warsztatowy")
    workshop = [
        bg_candidate("k.1", "metalowe uderzenia warsztatu", "bg_workshop_metal_clanks_01.mp3", "workshop_metal_clanks_01",
                     "kuznia-warsztat", "warsztat / metalowe uderzenia", "ciąg metalowych stuków i krótkich rezonansów — aktywny blat warsztatu lub kuźni",
                     clank, scout_source(clank_item, "metal clanks: okno 1–9 s"), 1, 9, traits=workshop_traits, bad_for=workshop_bad, highpass=45, lowpass=11000),
        bg_candidate("k.2", "tarcie ostrzy i imadło", "bg_workshop_blade_grind_01.mp3", "workshop_blade_grind_01",
                     "kuznia-warsztat", "warsztat / tarcie metalu", "długie tarcie metalu i zgrzyt — bardziej precyzyjny warsztat niż bitwa",
                     grind, scout_source(grind_item, "sword blades grinding: okno 1–9 s"), 1, 9, traits=workshop_traits, bad_for=workshop_bad, highpass=60, lowpass=11000),
        bg_candidate("k.3", "piła/maszyna w pracowni", "bg_workshop_saw_loop_01.mp3", "workshop_saw_loop_01",
                     "kuznia-warsztat", "warsztat / piła i maszyna", "regularna praca piły/maszyny, surowa i przemysłowa — dobry warsztat bez tłumu",
                     ATOM / "packs/opengameart-30-cc0-sfx-loops/audio/saw.m4a", loop_src, target_db=-33, traits=workshop_traits + ["maszyna"], bad_for=workshop_bad, highpass=60, lowpass=10000),
    ]

    crypt_traits = ["grobowa cisza", "kamień", "niski pogłos", "martwe wnętrze"]
    crypt_bad = ["targ", "dzień w lesie", "ciepłe palenisko", "otwarta równina"]
    amb_src = atom_source("30-cc0-sfx-loops", "30 SFX loops", "rubberduck", "audio/ambient-02.m4a; ciemny ambient loop")
    crypt = [
        bg_candidate("n.1", "cicha piwnica jak krypta", "bg_crypt_cellar_still_01.mp3", "crypt_cellar_still_01",
                     "krypta-nekropolia", "krypta / nieruchome podziemie", "grobowo spokojny room tone: odległe szmery, mało ruchu, dużo chłodnej pustki",
                     cellar, scout_source(cellar_item, "quiet cellar: okno 20–28 s"), 20, 28, traits=crypt_traits, bad_for=crypt_bad, highpass=35, lowpass=8500),
        bg_candidate("n.2", "daleki hum w pustej sali", "bg_crypt_distant_hum_01.mp3", "crypt_distant_hum_01",
                     "krypta-nekropolia", "krypta / dalekie echo", "niski elektryczny/architektoniczny pomruk i pusta przestrzeń — chłodna sala grobowa bez życia",
                     hotel, scout_source(hotel_item, "quiet room with distant voices/hum: okno 8–16 s; użyte dla martwego, dalekiego wnętrza"), 8, 16, target_db=-33, traits=crypt_traits + ["daleki hum"], bad_for=crypt_bad, highpass=35, lowpass=8000),
        bg_candidate("n.3", "ciemny ambient nekropolii", "bg_crypt_dark_ambient_01.mp3", "crypt_dark_ambient_01",
                     "krypta-nekropolia", "krypta / ciemny ambient", "syntetyczno-terenowy ciemny szum: najmniej dosłowny, ale najbardziej grobowy i nieruchomy",
                     ATOM / "packs/opengameart-30-cc0-sfx-loops/audio/ambient-02.m4a", amb_src, target_db=-33, traits=crypt_traits + ["ciemny ambient"], bad_for=crypt_bad, highpass=35, lowpass=8500),
    ]

    mech_traits = ["mechanizm", "furkot", "metal", "ruch obrotowy"]
    mech_bad = ["organiczne ciało", "ogień", "woda", "głos"]
    mech_scout = scout_source(mech_item, "Battle Mech walks: okno 0.7–2.7 s; rytmiczny metaliczny mechanizm")
    sci_src = atom_source("kenney-sci-fi-sounds", "Sci-Fi Sounds", "Kenney", "engine-circular/space-engine; CC0 wg pack.json")
    metal_src = atom_source("100-cc0-metal-and-wood-sfx", "100 metal and wood SFX", "rubberduck", "metal-spring-01; CC0 wg pack.json")
    mech_hero = [
        hero_candidate("f.1", "kroczący mechanizm bojowy", "h_mechanism_mech_step_01.mp3", "mechanism_mech_step_01",
                       "furkot-mechanizmu", "furkot/obrót mechanizmu", "ciężki, kroczący, metaliczny", "krótka sekwencja serw i ciężkiego mechanicznego kroku",
                       mech, mech_scout, 0.7, 2.7, traits=mech_traits + ["serwo"], bad_for=mech_bad,
                       good_for="artefakty, automaty, tryby, mechaniczne stworzenia", bad_for_txt="żywe skrzydła, ogień, plusk wody", highpass=45, lowpass=10000),
        hero_candidate("f.2", "wirujący silnik/koło zębate", "h_mechanism_engine_circular_01.mp3", "mechanism_engine_circular_01",
                       "furkot-mechanizmu", "furkot/obrót mechanizmu", "okrągły, wirujący, równy", "stabilny obrót jak mały silnik albo koło zębate nabierające tempa",
                       ATOM / "packs/kenney-sci-fi-sounds/audio/engine-circular-000.m4a", sci_src, target_db=-15, traits=mech_traits + ["silnik"], bad_for=mech_bad,
                       good_for="wirujące mechanizmy, artefakty, koła zębate", bad_for_txt="naturalne skrzydła, drewno, magia bez urządzeń", highpass=60, lowpass=11000),
        hero_candidate("f.3", "sprężyna i zapadka", "h_mechanism_spring_click_01.mp3", "mechanism_spring_click_01",
                       "furkot-mechanizmu", "furkot/obrót mechanizmu", "sprężynowy, klikający, drobny", "metalowa sprężyna i zapadka — krótki mechaniczny gest, dobry dla małych urządzeń",
                       ATOM / "packs/opengameart-100-cc0-metal-and-wood-sfx/audio/metal-spring-01.m4a", metal_src, target_db=-15, traits=mech_traits + ["sprężyna", "zapadka"], bad_for=mech_bad,
                       good_for="małe mechanizmy, zamki, artefakty z trybami", bad_for_txt="kolos, eksplozja, żywe ciało", highpass=80, lowpass=11000),
    ]

    fire_traits = ["ogień", "huk", "gwałtowny", "żar"]
    fire_bad = ["woda", "metaliczny mechanizm", "cichy szept", "głos"]
    camp_src = scout_source(camp_item, "Camp fire 2: okno 0.3–2.3 s; żywy płomień z trzaskiem")
    thruster_src = atom_source("kenney-sci-fi-sounds", "Sci-Fi Sounds", "Kenney", "thruster-fire-000; użyte jako mocny ciąg płomienia")
    flame_src = atom_source("superpowers-assets-sound-effects", "Superpowers assets sound effects", "medicinestorm", "flame-thrower.m4a; CC0 wg pack.json")
    fire_hero = [
        hero_candidate("o.1", "żywy trzask płomienia", "h_fire_roar_camp_01.mp3", "fire_roar_camp_01",
                       "huk-ognia", "huk / gwałtowny płomień", "żywy, trzaskający, bliski", "krótki, realny podmuch ognia z trzaskającym drewnem",
                       camp, camp_src, 0.3, 2.3, traits=fire_traits + ["trzask"], bad_for=fire_bad,
                       good_for="płomień, pożoga, nagły rozbłysk ognia", bad_for_txt="ogień bez trzasku? woda, metal, głos", highpass=60, lowpass=10000),
        hero_candidate("o.2", "ciąg palnika / strumień ognia", "h_fire_roar_thruster_01.mp3", "fire_roar_thruster_01",
                       "huk-ognia", "huk / gwałtowny płomień", "ciągły, syczący, energetyczny", "mocny strumień płomienia jak palnik albo magiczna smuga ognia",
                       ATOM / "packs/kenney-sci-fi-sounds/audio/thruster-fire-000.m4a", thruster_src, target_db=-15, traits=fire_traits + ["ciąg", "syk"], bad_for=fire_bad,
                       good_for="smugi ognia, wybuch palnika, magiczny płomień", bad_for_txt="naturalne ognisko spokojne, metal, woda", highpass=70, lowpass=11000),
        hero_candidate("o.3", "miotacz płomieni", "h_fire_roar_flamethrower_01.mp3", "fire_roar_flamethrower_01",
                       "huk-ognia", "huk / gwałtowny płomień", "szeroki, agresywny, pożogowy", "najbardziej agresywny strumień ognia — huk i szum palącego powietrza",
                       ATOM / "packs/opengameart-superpowers-assets-sound-effects/audio/flame-thrower.m4a", flame_src, target_db=-15, traits=fire_traits + ["miotacz", "pożoga"], bad_for=fire_bad,
                       good_for="duży płomień, smoczy oddech, pożoga, ognisty czar", bad_for_txt="małe ognisko, rytuał spokojny, woda", highpass=60, lowpass=11000),
    ]

    return {
        "id": "g034",
        "created": "2026-09-27",
        "note": "PAKIET 5 zestawów po g033: `background:step-rownina`, `background:kuznia-warsztat`, `background:krypta-nekropolia`, `hero:furkot-mechanizmu`, `hero:huk-ognia`. Anchory: 10/230/396/492, 16/168/285/355/487, 42/72/543/600, 19/132/146/228/484, 59/102/209/287/290/314/436/496/507/513. Źródła: Freesound CC0 z wcześniejszych scoutów oraz atomcut/OpenGameArt/Kenney CC0.",
        "entries": [
            {"slug": "tlo-step", "kind": "backgrounds", "role": "jedyny klocek typu tła `step-rownina` (19 fabuł; anchory 10, 230, 396, 492)", "candidates": step},
            {"slug": "tlo-kuznia", "kind": "backgrounds", "role": "jedyny klocek typu tła `kuznia-warsztat` (19 fabuł; anchory 16, 168, 285, 355, 487)", "candidates": workshop},
            {"slug": "tlo-krypta", "kind": "backgrounds", "role": "jedyny klocek typu tła `krypta-nekropolia` (15 fabuł; anchory 42, 72, 543, 600)", "candidates": crypt},
            {"slug": "hero-mechanizm", "kind": "heroes", "role": "jedyny klocek typu hero `furkot-mechanizmu` (16 fabuł; anchory 19, 132, 146, 228, 484)", "candidates": mech_hero},
            {"slug": "hero-ogien", "kind": "heroes", "role": "jedyny klocek typu hero `huk-ognia` (16 fabuł; anchory 59, 102, 209, 287, 290, 314, 436, 496, 507, 513)", "candidates": fire_hero},
        ],
        "verdicts": {},
    }


def main() -> None:
    ensure_sources()
    clean_gate()
    manifest = build_manifest()
    (GATE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (GATE / "verdicts.json").write_text(json.dumps({"gate": "g034", "choices": {}, "notes": {}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {GATE / 'manifest.json'}")
    for entry in manifest["entries"]:
        print(f"- {entry['slug']}: {', '.join(c['label'] for c in entry['candidates'])}")


if __name__ == "__main__":
    main()
