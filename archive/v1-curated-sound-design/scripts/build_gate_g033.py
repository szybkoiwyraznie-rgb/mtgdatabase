#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g033 — paczka 5 wpisów po sanity audycie g032.

Zakres (każdy wpis ma po 3 kandydatów):
  1) background:podziemia-jaskinia       — top brak po g032 (29), anchor 428
  2) background:gory-wichry              — top brak po g032 (28), anchor 1/337
  3) hero:przemiana-materializacja       — top brak hero (24), anchor 309
  4) mood:podstep-intryga                — brak kody (17), anchor 104/474
  5) mood:wladza-kontrola                — brak kody dla 607 po audycie g032

Źródła:
- tła: istniejąca paczka Sample Scout (Freesound CC0) + YSL/NPS PD z GitHuba,
- hero: atomcut/OpenGameArt CC0 (magiczne/formujące SFX),
- kody: gesty autorskie, podgląd neutralny na zatwierdzonym b_piano_steinway.

Przed uruchomieniem, jeśli /tmp/ysl_probe albo /tmp/atomcut_probe nie istnieją:
  git clone --depth 1 --filter=blob:none --sparse https://github.com/rosuH/YSL.git /tmp/ysl_probe
  git clone --depth 1 --filter=blob:none --sparse https://github.com/novincode/atomcut-library.git /tmp/atomcut_probe
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
import coda_synth  # noqa: E402
import sig_audio as dsp  # noqa: E402
from build_gate_g003 import soft_limit  # noqa: E402

GATE = REPO / "data" / "gates" / "g033"
CAND = GATE / "candidates"
YSL = Path("/tmp/ysl_probe")
ATOM = Path("/tmp/atomcut_probe")

YSL_SOURCE = {
    "title": "Yellowstone Sound Library (NPS)",
    "author": "National Park Service",
    "license": "Public Domain (utwór rządu USA)",
    "url": "https://www.nps.gov/yell/learn/photosmultimedia/soundlibrary.htm",
    "channel": "git clone sparse z github.com/rosuH/YSL (mirror)",
}


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


def ensure_sources() -> None:
    needed = [
        REPO / "legacy/source/sample_scout/freesound_quiet-room-tone/01-637805-room-tone-quiet-cellar-with-distant-noises-flac.mp3",
        REPO / "legacy/source/sample_scout/freesound_water-splash/02-476318-quarry-tunnel-ambience-1-large-splash.mp3",
        REPO / "legacy/source/sample_scout/freesound_battle-swords/03-667115-mongolian-film-windblown-steppe1-wav.mp3",
        YSL / "The Dragon's Mouth/Sound Library - The Dragon's Mouth.mp3",
        ATOM / "packs/opengameart-magic-spell-sfx/audio/magical-3.m4a",
        ATOM / "packs/opengameart-superpowers-assets-sound-effects/audio/magic.m4a",
        ATOM / "packs/opengameart-superpowers-assets-sound-effects/audio/power-up-2.m4a",
    ]
    missing = [str(p) for p in needed if not p.exists()]
    if missing:
        raise SystemExit("Brak źródeł do g033:\n" + "\n".join(missing))


def clean_gate() -> None:
    if GATE.exists():
        shutil.rmtree(GATE)
    CAND.mkdir(parents=True, exist_ok=True)


def render_segment(src: Path, out: Path, start: float, end: float, target_db: float, fade_in=0.08,
                   fade_out=0.35, highpass: float | None = None, lowpass: float | None = None,
                   mono: bool = False) -> tuple[float, float, float]:
    wave, _ = dsp.load_any(src)
    seg = dsp.cut(wave, start, end).copy()
    if mono and seg.shape[0] > 1:
        m = seg.mean(axis=0, keepdims=True)
        seg = np.repeat(m, 2, axis=0)
    if highpass:
        sos = butter(4, highpass, btype="highpass", fs=dsp.SR, output="sos")
        seg = sosfiltfilt(sos, seg, axis=-1)
    if lowpass:
        sos = butter(4, lowpass, btype="lowpass", fs=dsp.SR, output="sos")
        seg = sosfiltfilt(sos, seg, axis=-1)
    seg = dsp.fade(seg, fade_in, fade_out)
    seg = dsp.normalize_rms(seg, target_db)
    seg = dsp.peak_ceiling(seg, 0.92)
    dsp.encode_mp3(out, seg)
    return round(seg.shape[1] / dsp.SR, 2), round(dsp.rms_db(seg), 1), round(dsp.spectral_share(seg, 6000.0), 3)


def render_hero(src: Path, out: Path, target_db=-15.0, lowpass: float | None = None,
                highpass: float | None = None, stretch_tail: float = 0.0) -> tuple[float, float, float]:
    wave, _ = dsp.load_any(src)
    seg = wave.copy()
    if highpass:
        sos = butter(4, highpass, btype="highpass", fs=dsp.SR, output="sos")
        seg = sosfiltfilt(sos, seg, axis=-1)
    if lowpass:
        sos = butter(4, lowpass, btype="lowpass", fs=dsp.SR, output="sos")
        seg = sosfiltfilt(sos, seg, axis=-1)
    if stretch_tail > 0:
        tail = seg[:, -int(min(stretch_tail, 0.8) * dsp.SR):]
        if tail.shape[1] > 0:
            seg = np.concatenate([seg, dsp.fade(tail.copy(), 0.0, stretch_tail)], axis=1)
    seg = soft_limit(seg, crest_db=13.5, rounds=4)
    seg = dsp.fade(seg, 0.01, min(0.35, seg.shape[1] / (2 * dsp.SR)))
    seg = dsp.normalize_rms(seg, target_db)
    seg = dsp.peak_ceiling(seg, 0.92)
    dsp.encode_mp3(out, seg)
    return round(seg.shape[1] / dsp.SR, 2), round(dsp.rms_db(seg), 1), round(dsp.spectral_share(seg, 6000.0), 3)


def bg_candidate(label: str, title: str, fname: str, entry_id: str, typ: str, setting: str,
                 desc: str, src: Path, source: dict, start: float, end: float,
                 target_db=-32.0, **kw) -> dict:
    dur, rms, hf = render_segment(src, CAND / fname, start, end, target_db, **kw)
    desc2 = f"{desc} (okno {start:.1f}–{end:.1f} s, RMS {rms} dB, HF>6k {hf:.1%})"
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
            "semantics": {
                "type": typ,
                "traits": [],
                "bad_for": [],
            },
            "source": source,
        },
    }


def hero_candidate(label: str, title: str, fname: str, entry_id: str, character: str,
                   desc: str, src: Path, source: dict, **kw) -> dict:
    dur, rms, hf = render_hero(src, CAND / fname, **kw)
    desc2 = f"{desc} (czas {dur:.2f} s, RMS {rms} dB, HF>6k {hf:.1%})"
    return {
        "label": label,
        "title": title,
        "file": f"candidates/{fname}",
        "desc": desc2,
        "source": source["title"],
        "entry": {
            "id": entry_id,
            "role": "przemiana / materializacja / rozpad formy",
            "character": character,
            "distance": "średni",
            "energy": "średnia",
            "duration_sec": dur,
            "desc": desc2,
            "good_for": "formowanie cienia, materializacja postaci, przeobrażenie, rozpłynięcie formy",
            "bad_for": "zwykły pocisk magiczny, fizyczny cios, naturalistyczna fauna",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "semantics": {
                "type": "przemiana-materializacja",
                "traits": ["narastanie", "formowanie", "magiczne", "przejście formy"],
                "bad_for": ["zwykły pocisk", "cios fizyczny", "woda"],
            },
            "source": source,
        },
    }


def gesture_candidate(label: str, title: str, gid: str, typ: str, semantic: str, desc: str,
                      notes: list[dict], traits: list[str], bad_for: list[str]) -> dict:
    instruments = json.loads((REPO / "data/library/instruments.json").read_text(encoding="utf-8"))
    piano = next(e for e in instruments["entries"] if e["id"] == "b_piano_steinway")
    piano_abs = {**piano, "samples": {m: str(REPO / p) for m, p in piano["samples"].items()}}
    gesture = {"notes": notes, "delivery": {"humanize": {"timing_ms": 12, "vel": 0.035}}}
    result = coda_synth.render_coda(gesture, piano_abs, seed=33, level_ref_db=-18.0)
    for warning in result.warnings:
        print(f"  ! {gid}: {warning}")
    dsp.encode_mp3(CAND / f"{gid}.mp3", result.wave)
    return {
        "label": label,
        "title": title,
        "file": f"candidates/{gid}.mp3",
        "desc": desc,
        "source": "gest autorski; podgląd na b_piano_steinway (render neutralny)",
        "entry": {
            "id": gid,
            "semantic": semantic,
            "desc": desc,
            "notes": notes,
            "delivery": {"humanize": {"timing_ms": 12, "vel": 0.035}},
            "instrument_tags": ["piano", "struck-light", "percussion_low", "bells"],
            "semantics": {"type": typ, "traits": traits, "bad_for": bad_for},
        },
    }


def atom_source(pack: str, title: str, author: str, notes: str) -> dict:
    return {
        "title": f"{title} (OpenGameArt)",
        "author": author,
        "license": "CC0 1.0 (public domain)",
        "url": f"https://opengameart.org/content/{pack}",
        "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
        "notes": notes,
    }


def build_manifest() -> dict:
    quiet = load_scout_manifest("freesound_quiet-room-tone")
    water = load_scout_manifest("freesound_water-splash")
    swords = load_scout_manifest("freesound_battle-swords")

    cellar_item = quiet["01-637805-room-tone-quiet-cellar-with-distant-noises-flac.mp3"]
    quarry_item = water["02-476318-quarry-tunnel-ambience-1-large-splash.mp3"]
    wind_item = swords["03-667115-mongolian-film-windblown-steppe1-wav.mp3"]

    cellar = REPO / cellar_item["file"]
    quarry = REPO / quarry_item["file"]
    wind = REPO / wind_item["file"]
    dragons = YSL / "The Dragon's Mouth/Sound Library - The Dragon's Mouth.mp3"

    podziemia = [
        bg_candidate("p.1", "cicha piwnica z dalekimi szmerami", "bg_cave_cellar_01.mp3",
                     "cave_cellar_01", "podziemia-jaskinia", "podziemia / cicha piwnica",
                     "niski room tone piwnicy: chłodne powietrze, daleki pogłos i pojedyncze nieokreślone szmery — dobre dla lochu bez wody",
                     cellar, scout_source(cellar_item, "quiet cellar: okno 12–20 s; wybrane dla podziemnego tła bez ludzi na pierwszym planie"),
                     12.0, 20.0, target_db=-32.0, highpass=45, lowpass=9000),
        bg_candidate("p.2", "tunel kamieniołomu z wilgotnym echem", "bg_cave_quarry_tunnel_01.mp3",
                     "cave_quarry_tunnel_01", "podziemia-jaskinia", "podziemia / tunel kamieniołomu",
                     "wilgotny tunel: niski pogłos, oddech przestrzeni i daleki plusk — bardziej jaskinia niż pokój",
                     quarry, scout_source(quarry_item, "quarry tunnel ambience: okno 2–10 s; kandydat na wilgotne podziemia"),
                     2.0, 10.0, target_db=-32.0, highpass=40, lowpass=8500),
        bg_candidate("p.3", "głuchy przeciąg w grocie", "bg_cave_dragonsmouth_01.mp3",
                     "cave_dragonsmouth_01", "podziemia-jaskinia", "podziemia / gorąca grota",
                     "głęboki, gardłowy szum pary i kamiennego pogłosu; wcześniej nie nadawał się jako woda, ale działa jako mroczna, oddychająca grota",
                     dragons, dict(YSL_SOURCE, notes="The Dragon's Mouth: okno 58–66 s; użyte nie jako woda, tylko jako przeciąg/groto-pogłos"),
                     58.0, 66.0, target_db=-33.0, highpass=35, lowpass=7000),
    ]
    for c in podziemia:
        c["entry"]["semantics"]["traits"] = ["podziemny pogłos", "ciemne powietrze", "kamień", "niski szmer"]
        c["entry"]["semantics"]["bad_for"] = ["ciepłe wnętrze", "otwarty plener", "miasto", "sielski las"]

    gory = [
        bg_candidate("g.1", "stały wiatr wysokości", "bg_mountain_wind_steady_01.mp3",
                     "mountain_wind_steady_01", "gory-wichry", "góry / stały wiatr na grani",
                     "ciągły, szeroki wiatr bez ptaków i bez miasta — neutralna grań albo przełęcz",
                     wind, scout_source(wind_item, "Mongolian windblown steppe: okno 20–28 s; interpretowane jako otwarta wysokość/grzbiet"),
                     20.0, 28.0, target_db=-32.0, highpass=55, lowpass=10000),
        bg_candidate("g.2", "porywy na odkrytym zboczu", "bg_mountain_wind_gusts_01.mp3",
                     "mountain_wind_gusts_01", "gory-wichry", "góry / porywy na zboczu",
                     "bardziej zmienny wiatr: krótkie porywy jak na odkrytym zboczu, bez ludzkiego planu",
                     wind, scout_source(wind_item, "Mongolian windblown steppe: okno 54–62 s; porywy, bez mowy na pierwszym planie"),
                     54.0, 62.0, target_db=-32.0, highpass=55, lowpass=10000),
        bg_candidate("g.3", "surowa wichura na płaskowyżu", "bg_mountain_wind_plateau_01.mp3",
                     "mountain_wind_plateau_01", "gory-wichry", "góry / surowy płaskowyż",
                     "najbardziej szorstkie okno: suchy wiatr po kamieniu, dobre dla wysokiego płaskowyżu lub kanionu",
                     wind, scout_source(wind_item, "Mongolian windblown steppe: okno 96–104 s; szorstki pęd powietrza"),
                     96.0, 104.0, target_db=-32.0, highpass=55, lowpass=10000),
    ]
    for c in gory:
        c["entry"]["semantics"]["traits"] = ["wiatr", "otwarta wysokość", "surowe powietrze", "brak ludzi"]
        c["entry"]["semantics"]["bad_for"] = ["wnętrze", "miasto", "las dzienny", "ciepły spokój"]

    hero_src_magic = atom_source("magic-spell-sfx", "Magic Spell SFX", "jaggedstone",
                                 "packs/opengameart-magic-spell-sfx; magical-3.m4a; nie jest użytym już spell_cast_bolt_01")
    hero_src_super = atom_source("superpowers-assets-sound-effects", "Superpowers assets sound effects", "medicinestorm",
                                 "packs/opengameart-superpowers-assets-sound-effects; magic/power-up; CC0 wg pack.json")
    przemiana = [
        hero_candidate("m.1", "formowanie świetlistej masy", "h_materialize_magic_swell_01.mp3",
                       "materialize_magic_swell_01", "narastający, magiczny, zaokrąglony",
                       "miękkie narastanie i rozbłysk, bardziej powstanie formy niż strzał zaklęcia",
                       ATOM / "packs/opengameart-magic-spell-sfx/audio/magical-3.m4a", hero_src_magic,
                       target_db=-15.0, lowpass=9000),
        hero_candidate("m.2", "ciemne przejście przez formę", "h_materialize_dark_shift_01.mp3",
                       "materialize_dark_shift_01", "ciemny, przeciągły, transformacyjny",
                       "dłuższy mroczny łuk energii: cień rozlewa się i składa w drugą postać",
                       ATOM / "packs/opengameart-superpowers-assets-sound-effects/audio/magic.m4a", hero_src_super,
                       target_db=-15.0, lowpass=8000),
        hero_candidate("m.3", "krystalizacja/power-up formy", "h_materialize_powerup_01.mp3",
                       "materialize_powerup_01", "jasny, wznoszący, krystalizujący",
                       "długie wznoszenie jak przejście od mgły do kształtu; dobre dla materializacji lub przemiany w światło",
                       ATOM / "packs/opengameart-superpowers-assets-sound-effects/audio/power-up-2.m4a", hero_src_super,
                       target_db=-15.0, lowpass=9000),
    ]

    intryga = [
        gesture_candidate("i.1", "sekretne zejście półtonem", "g_intrigue_halfstep",
                          "podstep-intryga", "podstęp — półtonowy cień za plecami",
                          "cztery krótkie wejścia opadające w niepokojących krokach: mały znak zapytania, potem ukryte domknięcie",
                          [
                              {"midi": 64, "on": 0.00, "off": 0.28, "vel": 0.55},
                              {"midi": 60, "on": 0.46, "off": 0.72, "vel": 0.48},
                              {"midi": 56, "on": 0.94, "off": 1.18, "vel": 0.52},
                              {"midi": 54, "on": 1.42, "off": 2.05, "vel": 0.45},
                          ], ["opadający", "sekret", "cichy", "pytający"], ["jawny triumf", "otwarta furia"]),
        gesture_candidate("i.2", "fałszywy trop i nagły skręt", "g_intrigue_false_trail",
                          "podstep-intryga", "podstęp — fałszywy trop i skręt",
                          "dwie pozornie niewinne nuty, potem tritonowy skręt w bok — fortel zamiast otwartego konfliktu",
                          [
                              {"midi": 60, "on": 0.00, "off": 0.25, "vel": 0.48},
                              {"midi": 68, "on": 0.48, "off": 0.72, "vel": 0.44},
                              {"midi": 54, "on": 0.98, "off": 1.28, "vel": 0.60},
                              {"midi": 64, "on": 1.48, "off": 2.00, "vel": 0.50},
                          ], ["triton", "fortel", "skręt", "niepewność"], ["sielskość", "prosty marsz"]),
        gesture_candidate("i.3", "mrugnięcie w cieniu", "g_intrigue_shadow_wink",
                          "podstep-intryga", "podstęp — mrugnięcie w cieniu",
                          "lekka, punktowana figura z pauzami: brzmi jak ktoś, kto wie więcej niż mówi",
                          [
                              {"midi": 60, "on": 0.00, "off": 0.20, "vel": 0.42},
                              {"midi": 64, "on": 0.44, "off": 0.60, "vel": 0.48},
                              {"midi": 60, "on": 0.92, "off": 1.10, "vel": 0.36},
                              {"midi": 54, "on": 1.36, "off": 1.95, "vel": 0.50},
                          ], ["punktowany", "pauzy", "lekki cień", "ironia"], ["makabra", "monumentalność"]),
    ]

    kontrola = [
        gesture_candidate("w.1", "rozkaz opadający", "g_control_descending_order",
                          "wladza-kontrola", "kontrola — rozkaz opadający bez dyskusji",
                          "trzy równe, coraz niższe uderzenia i długi finał: autorytet zamyka przestrzeń",
                          [
                              {"midi": 72, "on": 0.00, "off": 0.30, "vel": 0.62},
                              {"midi": 68, "on": 0.52, "off": 0.82, "vel": 0.68},
                              {"midi": 60, "on": 1.05, "off": 1.35, "vel": 0.74},
                              {"midi": 54, "on": 1.58, "off": 2.35, "vel": 0.70},
                          ], ["autorytet", "opadający", "stanowczy", "domknięcie"], ["beztroska", "chaos"]),
        gesture_candidate("w.2", "klamra podporządkowania", "g_control_locking_frame",
                          "wladza-kontrola", "kontrola — klamra podporządkowania",
                          "ten sam niski ton wraca jak rygiel, między nim krótkie odpowiedzi wyżej — kontrola trzyma wszystko w ramie",
                          [
                              {"midi": 48, "on": 0.00, "off": 0.32, "vel": 0.70},
                              {"midi": 60, "on": 0.50, "off": 0.76, "vel": 0.45},
                              {"midi": 48, "on": 1.00, "off": 1.32, "vel": 0.75},
                              {"midi": 64, "on": 1.52, "off": 1.78, "vel": 0.42},
                              {"midi": 48, "on": 2.02, "off": 2.70, "vel": 0.78},
                          ], ["rygiel", "powrót basu", "ramy", "nadzór"], ["swoboda", "zuchwały pęd"]),
        gesture_candidate("w.3", "zimna pieczęć władzy", "g_control_cold_seal",
                          "wladza-kontrola", "kontrola — zimna pieczęć władzy",
                          "krótki rozkaz, pauza i szerokie, nieruchome domknięcie: nie triumf, tylko pieczęć i zakaz ruchu",
                          [
                              {"midi": 54, "on": 0.00, "off": 0.26, "vel": 0.58},
                              {"midi": 60, "on": 0.48, "off": 0.74, "vel": 0.58},
                              {"midi": 50, "on": 1.06, "off": 1.36, "vel": 0.70},
                              {"midi": 56, "on": 1.06, "off": 1.36, "vel": 0.52},
                              {"midi": 54, "on": 1.70, "off": 2.55, "vel": 0.64},
                          ], ["zimny", "pieczęć", "zakaz", "autorytet"], ["ciepła więź", "furia"]),
    ]

    return {
        "id": "g033",
        "created": "2026-09-26",
        "note": "PAKIET 5 zestawów po sanity audycie g032: topowe braki `background:podziemia-jaskinia`, `background:gory-wichry`, `hero:przemiana-materializacja` oraz dwie kody nastroju `podstep-intryga` i `wladza-kontrola`. Anchory: 428/85, 1/337, 309, 104/474, 607. Tła z Freesound/YSL, hero z atomcut/OpenGameArt CC0, gesty autorskie z neutralnym podglądem na b_piano_steinway.",
        "entries": [
            {"slug": "tlo-podziemia", "kind": "backgrounds", "role": "jedyny klocek typu tła `podziemia-jaskinia` (29 fabuł; anchor 428 Curiosity po korekcie z fałszywej komnaty)", "candidates": podziemia},
            {"slug": "tlo-gory", "kind": "backgrounds", "role": "jedyny klocek typu tła `gory-wichry` (28 fabuł; anchory 1 Dunland Crebain / 337 Glaring Aegis)", "candidates": gory},
            {"slug": "hero-przemiana", "kind": "heroes", "role": "jedyny klocek typu hero `przemiana-materializacja` (24 fabuły; anchor 309 Civilized Scholar)", "candidates": przemiana},
            {"slug": "koda-intryga", "kind": "gestures", "role": "jedyny klocek typu kody `podstep-intryga` (17 fabuł; anchory 104 Glitch Ghost Surveyor / 474 Scroll Thief)", "candidates": intryga},
            {"slug": "koda-wladza", "kind": "gestures", "role": "jedyny klocek typu kody `wladza-kontrola` (5 fabuł; anchor 607 Containment Membrane po sanity audycie g032)", "candidates": kontrola},
        ],
        "verdicts": {},
    }


def main() -> None:
    ensure_sources()
    clean_gate()
    manifest = build_manifest()
    (GATE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (GATE / "verdicts.json").write_text(json.dumps({"gate": "g033", "choices": {}, "notes": {}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {GATE / 'manifest.json'}")
    for entry in manifest["entries"]:
        print(f"- {entry['slug']}: {', '.join(c['label'] for c in entry['candidates'])}")


if __name__ == "__main__":
    main()
