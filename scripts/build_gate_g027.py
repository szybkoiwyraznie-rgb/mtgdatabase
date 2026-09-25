#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g027 — fabuła 110 „Serra's Embrace”, RUNDA 2 (po „żadne” w g025).

Diagnoza właściciela (data/gates/g025/verdicts.json::notes):
  * bitwa: kandydaci to bitwy WSPÓŁCZESNE (fajerwerkowe wybuchy); potrzebny
    zgiełk bitwy fantasy/średniowiecznej — szczęk oręża, krzyki rannych.
  * łopot: nieokreślony szum / trele ptaka / jeden zamach i grzmot; potrzebne
    WYRAŹNE odbicia skrzydeł.
  * nadzieja: wszystkie molowe; nadzieja = składowe akordu DUROWEGO.

Runda 2 — trzy nowe zestawy (zg.1–3 / ł.1–3 / n.1–3):
  * zg: WYŁĄCZNIE stal + ludzie, atomcut CC0 (sword-clash, młoty, okrzyki
    i jęki ranion −4/−5 półtonów techniką g007). Zero wybuchów.
  * ł: foley dużych skrzydeł (Freesound CC0): suwy peleryn superbohatera,
    seria łękotu, ciężkie odbicia tkaniny — bez pitch-down, HP przeciw
    grzmotowi, 3–5 czytelnych odbić.
  * n: DUROWE gesty ok.2 — C-dur rodzina / lydyjski D / C powrotna, na
    siatce steinwaya (C-E / C-aug / D-F#); finały jasne.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
import coda_synth  # noqa: E402
from build_gate_g003 import to_roar  # noqa: E402

GATE = REPO / "data" / "gates" / "g027"
CAND = GATE / "candidates"
SCOUT = REPO / "work" / "scout"
AT = Path("/tmp/atomcut/packs")

ATOMCUT_SRC = {
    "title": "atomcut-library — paczki OpenGameArt (CC0): 20 sword SFX, "
             "male-gruntyelling (haeldb), 15 vocal male strain/hurt (cc0), metal&wood",
    "author": "Various OpenGameArt artists",
    "license": "CC0 1.0",
    "url": "https://github.com/novincode/atomcut-library",
    "channel": "git sparse-checkout /tmp/atomcut; montaż skryptem build_gate_g027.py",
}


def _scout_src(manifest_dir: str, idx0: int, notes: str) -> dict:
    man = json.loads((SCOUT / manifest_dir / "manifest.json").read_text("utf-8"))
    c = man[idx0]
    return {
        "title": f"{c['name']} (Freesound)",
        "author": c["author"],
        "license": "CC0 / Public Domain (wg API Freesound)",
        "url": c["source_url"],
        "channel": "sample-scout (preview-hq-mp3); manifest: " + manifest_dir,
        "notes": notes + f"; freesound id {c['source_id']}",
    }


def lp(wave: np.ndarray, hz: float) -> np.ndarray:
    sos = butter(3, min(hz, dsp.SR * 0.45), btype="lowpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1)


def hp(wave: np.ndarray, hz: float) -> np.ndarray:
    sos = butter(2, hz, btype="highpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1)


def battle_far(wave: np.ndarray, peak_db: float) -> np.ndarray:
    """Oddalenie ataku: wycinamy dół-wybuch i jasność, stawiamy na plan średnicy."""
    return dsp.normalize_rms(hp(lp(wave, 2600.0), 110.0), peak_db)


def voice_far(path: Path, semitones: float, peak_db: float, lp_hz: float = 1500.0) -> np.ndarray:
    """Filmowy fantasy-pitch-down (g007) + oddalenie."""
    w, _ = dsp.load_any(path)
    v = to_roar(w, semitones, hp_hz=90.0, lp_hz=lp_hz, drive=1.25)
    return dsp.normalize_rms(v, peak_db)


def crowd_floor(peak_db: float = -43.0) -> np.ndarray:
    """Równy, niezrozumiały gwar wielu ludzi — jęki i okrzyki bardzo głęboko."""
    t = np.zeros((2, int(8.0 * dsp.SR)))
    g, _ = dsp.load_any(AT / "opengameart-male-gruntyelling-sounds/audio/2yell6.m4a")
    v = to_roar(g, 5.0, hp_hz=80.0, lp_hz=700.0, drive=1.0)
    v = dsp.loop_to_length(v, int(8.0 * dsp.SR), crossfade_ms=500.0)
    v = dsp.normalize_rms(v, peak_db)
    return t + v


def finish_bed(total: np.ndarray, rms: float | None = None) -> np.ndarray:
    total = dsp.peak_ceiling(total)
    if rms is not None:
        total = dsp.peak_ceiling(dsp.normalize_rms(total, rms))
    total = dsp.fade(total, 1.2, 1.5)
    return total


# ---------------------------------------------------------------- tło: bitwa-zgielk r2
def bg_candidates() -> list[dict]:
    S = "opengameart-20-sword-sound-effects-attacks-and-clashes/audio/"
    Y1 = "opengameart-male-gruntyelling-sounds/audio/1yell"
    Y2 = "opengameart-male-gruntyelling-sounds/audio/2yell"
    X = "opengameart-15-vocal-male-strainhurtpainjump-sounds/audio/slightscream-0"
    H = "opengameart-100-cc0-metal-and-wood-sfx/audio/hammer-"
    cands: list[dict] = []

    # --- zg.1: front stali — szczęk prowadzący, pojedyncze okrzyki i jęki
    t = crowd_floor(-44.0)
    for idx, (f, at) in enumerate(zip(
            [f"{S}sword-clash-2.m4a", f"{S}sword-clash-5.m4a", f"{S}sword-clash-6.m4a",
             f"{S}sword-clash-1.m4a", f"{S}sword-clash-8.m4a", f"{S}sword-clash-4.m4a"],
            (0.5, 1.6, 2.8, 4.0, 5.4, 6.8))):
        w, _ = dsp.load_any(AT / f)
        pan_l = 0.72 if idx % 2 else 1.0
        seg = battle_far(w, -27.0) * np.array([[pan_l], [1.0 if pan_l == 0.72 else 0.72]])
        t = dsp.place(t, seg, at)
    for f, at in zip([f"{Y1}4.m4a", f"{Y2}10.m4a"], (1.1, 4.7)):
        t = dsp.place(t, voice_far(AT / f, 4.0, -34.0), at)
    t = dsp.place(t, voice_far(AT / f"{X}5.m4a", 3.0, -33.0), 3.3)
    for f, at in zip([f"{H}01.m4a", f"{H}04.m4a"], (2.2, 7.0)):
        w, _ = dsp.load_any(AT / f)
        t = dsp.place(t, dsp.normalize_rms(lp(w, 500.0), -36.0), at)
    dsp.encode_mp3(CAND / "zg1_front_stali.mp3", finish_bed(t, rms=-32.0))
    cands.append({
        "label": "zg.1", "title": "front stali — szczęk oręża prowadzi",
        "file": "candidates/zg1_front_stali.mp3",
        "desc": "sześć zderzeń mieczy na pierwszym planie oddali, dwa wojenne okrzyki "
                "(−4 półtony), jeden jęk rannego i puste uderzenia tarcz; spód = "
                "gwar wielu ludzi, zero wybuchów — czysta średniowieczna bitwa",
        "source": {**ATOMCUT_SRC, "notes": "sword-clash 1,2,4,5,6,8 (LP 2600/HP 110, -27 dB); "
                                          "1yell4/2yell10 −4 półt.; slightscream-05 −3 półt.; "
                                          "hammer LP 500; gwar-podkład 2yell6 −5 półt."},
        "entry": {
            "id": "battle_medieval_01",
            "setting": "pole bitwy — starcie stali oddalone",
            "desc": "szczęk oręża niesie się z pola, pojedyncze okrzyki i jęk — "
                    "linia frontu słyszana z tyłu, bez prochu",
            "file": "audio/library/backgrounds/battle_medieval_01.mp3",
            "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
            "semantics": {"type": "bitwa-zgielk",
                          "traits": ["bitwa", "zgiełk", "szczęk broni", "okrzyki", "średniowieczna"],
                          "bad_for": ["spokojna komnata", "sielanka", "kameralna scena"]},
            "source": {**ATOMCUT_SRC, "notes": "jak wyżej; montaż 6 zderzeń + 2 okrzyki + jęk"},
        },
    })
    print("  zg.1 zapisany")

    # --- zg.2: pole rannych — głównie krzyki i jęki, stal już rzadka
    t = crowd_floor(-42.0)
    for f, at in zip([f"{X}1.m4a", f"{X}4.m4a", f"{X}5.m4a", f"{X}9.m4a"],
                     (0.7, 2.3, 4.1, 6.2)):
        t = dsp.place(t, voice_far(AT / f, 3.0, -31.0, lp_hz=1800.0), at)
    for f, at in zip([f"{Y1}6.m4a"], (3.4,)):
        t = dsp.place(t, voice_far(AT / f, 4.0, -36.0), at)
    for f, at in zip([f"{S}sword-clash-3.m4a", f"{S}sword-clash-9.m4a", f"{S}sword-clash-10.m4a"],
                     (0.9, 3.9, 6.6)):
        w, _ = dsp.load_any(AT / f)
        t = dsp.place(t, battle_far(w, -32.0), at)
    dsp.encode_mp3(CAND / "zg2_pole_rannych.mp3", finish_bed(t, rms=-31.5))
    cands.append({
        "label": "zg.2", "title": "pole rannych — krzyki i jęki ponad wygasającą stalą",
        "file": "candidates/zg2_pole_rannych.mp3",
        "desc": "cztery jęki i krzyki rannych (obniżone 3 półtony — ludzie, nie ptactwo) "
                "nad gasnącymi pojedynczymi zderzeniami mieczy; bitwa po szczycie, "
                "pole pełne ranionych",
        "source": {**ATOMCUT_SRC, "notes": "slightscream 1,4,5,9 −3 półt. (-31 dB); sword-clash "
                                          "3,9,10 (-32 dB); 1yell6 −4 półt.; gwar 2yell6 −5 półt."},
        "entry": {
            "id": "battle_medieval_02",
            "setting": "pole bitwy — po szczycie, krzyki rannych",
            "desc": "wygasające starcie: struna jęków rannych, sporadyczny szczęk — "
                    "zgiełk bitwy skręcający ku zmierzchowi",
            "file": "audio/library/backgrounds/battle_medieval_02.mp3",
            "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
            "semantics": {"type": "bitwa-zgielk",
                          "traits": ["bitwa", "zgiełk", "krzyki rannych", "wygasająca", "średniowieczna"],
                          "bad_for": ["spokojna komnata", "sielanka", "kameralna scena"]},
            "source": {**ATOMCUT_SRC, "notes": "jak wyżej; montaż 4 jęki + 3 zderzenia + okrzyk"},
        },
    })
    print("  zg.2 zapisany")

    # --- zg.3: wir walki — gęste zderzenia i takty machiny uderzeniowej
    t = crowd_floor(-43.0)
    clash_files = [f"{S}sword-clash-{i}.m4a" for i in (1, 5, 3, 7, 2, 9, 6, 10, 4)]
    ats = (0.3, 1.0, 1.8, 2.5, 3.2, 4.0, 4.9, 5.7, 6.5)
    for idx, (f, at) in enumerate(zip(clash_files, ats)):
        w, _ = dsp.load_any(AT / f)
        g = -28.0 if idx < 6 else -31.0
        t = dsp.place(t, battle_far(w, g), at)
    for f, at in zip([f"{H}01.m4a", f"{H}02.m4a", f"{H}01.m4a"], (1.3, 3.7, 6.2)):
        w, _ = dsp.load_any(AT / f)
        t = dsp.place(t, dsp.normalize_rms(lp(w, 450.0), -33.0), at)
    t = dsp.place(t, voice_far(AT / f"{Y1}13.m4a", 4.0, -35.0), 4.6)
    t = dsp.place(t, voice_far(AT / f"{X}7.m4a", 3.0, -34.0), 5.8)
    bed = finish_bed(t, rms=-30.5)
    # cichnięcie zmierzchu: ostatnie 2 s schodzi o ~6 dB (fabuła: bitwa cichnie)
    tail = int(2.0 * dsp.SR)
    env = np.linspace(1.0, dsp.db_to_gain(-6.0), tail)
    bed[:, -tail:] *= env
    dsp.encode_mp3(CAND / "zg3_wir_walki.mp3", bed)
    cands.append({
        "label": "zg.3", "title": "wir walki — gęsty szczęk, machina uderzeniowa w tękcie",
        "file": "candidates/zg3_wir_walki.mp3",
        "desc": "dziewięć zderzeń mieczy w przyspieszonym rytmie, potem rzadsze — "
                "plus trzy głuche uderzenia taranu/tarcz, okrzyk i jęk; ostatnie 2 s "
                "zamiera o 6 dB: cichnące pole bitwy o zmierzchu",
        "source": {**ATOMCUT_SRC, "notes": "9× sword-clash (-28→-31 dB); hammer ×3 LP 450; "
                                          "1yell13 −4 półt.; slightscream-07 −3 półt.; ogon -6 dB"},
        "entry": {
            "id": "battle_medieval_03",
            "setting": "pole bitwy — wir starcia cichnący o zmierzchu",
            "desc": "gęsty szczęk wielu zderzeń z pulsem taranu, kończący się"
                    " w kierunku wieczora — zgiełk aktywnej bitwy, która gaśnie",
            "file": "audio/library/backgrounds/battle_medieval_03.mp3",
            "duration_sec": 8.0, "level_ref_db": -32, "loopable": False,
            "semantics": {"type": "bitwa-zgielk",
                          "traits": ["bitwa", "zgiełk", "szczęk broni", "gęsta", "cichnąca"],
                          "bad_for": ["spokojna komnata", "sielanka", "kameralna scena"]},
            "source": {**ATOMCUT_SRC, "notes": "jak wyżej; montaż 9 zderzeń + 3 młoty + głosy"},
        },
    })
    print("  zg.3 zapisany")
    return cands


# ---------------------------------------------------------------- hero: łopot-skrzydel r2
def hero_candidates() -> list[dict]:
    F = SCOUT / "wings-foley/freesound_wing-flap-foley"
    cands: list[dict] = []

    # --- ł.1: suwy wielkiej peleryny (foley) — cztery potężne odbicia
    w, _ = dsp.load_any(F / "03-711122-large-wings-superhero-cape-foley.mp3")
    seg = dsp.cut(w, 3.9, 13.2)
    seg = hp(seg, 55.0)
    seg = dsp.normalize_rms(seg, -19.0)
    seg = dsp.fade(seg, 0.25, 0.6)
    dsp.encode_mp3(CAND / "l1_suwy_peleryny.mp3", seg)
    cands.append({
        "label": "ł.1", "title": "cztery potężne suwy peleryny — foley kinowy",
        "file": "candidates/l1_suwy_peleryny.mp3",
        "desc": "filmowa technika (pękata peleryna superbohatera): cztery szerokie, "
                "silne odbicia jedno za drugim — czysty atak, bez treli, bez grzmota; "
                "brzmi jak powietrze spychane wielkim skrzydłem",
        "source": _scout_src("wings-foley/freesound_wing-flap-foley", 2,
                             "okno 3,9–13,2 s; HP 55 Hz; bez zmiany wysokości; -19 dB"),
        "entry": {
            "id": "wing_foley_cape",
            "role": "łopot wielkich skrzydeł — suwy górą powietrza",
            "character": "potężny, szeroki, miarowy",
            "distance": "bliski", "energy": "wysoka", "duration_sec": 9.3,
            "desc": "cztery pełne suwy wielkich skrzydeł — moc i majestat zstąpienia",
            "good_for": "zstąpienie wielkiej istoty, anioł, smok, majestat",
            "bad_for": "trzepot, drobne skrzydła, kameralny nastrój",
            "file": "audio/library/heroes/wing_foley_cape.mp3",
            "semantics": {"type": "lopot-skrzydel",
                          "traits": ["łopot", "wielkie skrzydła", "wyraźne odbicia", "potężny"],
                          "bad_for": ["trzepot", "trele", "szum bez rytmu"]},
            "source": _scout_src("wings-foley/freesound_wing-flap-foley", 2,
                                 "okno 3,9–13,2 s; HP 55; natywna wysokość"),
        },
    })
    print("  ł.1 zapisany")

    # --- ł.2: seria łękotu przed lądowaniem (foley) — sześć szybkich odbić
    w, _ = dsp.load_any(F / "05-506940-flapping-wings-foley.mp3")
    seg = dsp.cut(w, 3.1, 6.9)
    seg = hp(seg, 70.0)
    seg = dsp.normalize_rms(seg, -19.0)
    seg = dsp.fade(seg, 0.2, 0.5)
    dsp.encode_mp3(CAND / "l2_lekot_seria.mp3", seg)
    cands.append({
        "label": "ł.2", "title": "seria łękotu — sześć szybkich odbić jak hamowanie w locie",
        "file": "candidates/l2_lekot_seria.mp3",
        "desc": "gęsta seria czystych odbić skrzydeł (foley): wielka istota wyhamowuje "
                "tuż nad żołnierzem — żywe, wyraźne zamachy bez tła terenowego",
        "source": _scout_src("wings-foley/freesound_wing-flap-foley", 4,
                             "okno 3,1–6,9 s; HP 70 Hz; bez zmiany wysokości; -19 dB"),
        "entry": {
            "id": "wing_foley_hover",
            "role": "łopot wielkich skrzydeł — łękot hamowania",
            "character": "żywy, gęsty, bliski",
            "distance": "bliski", "energy": "średnio-wysoka", "duration_sec": 3.8,
            "desc": "seria szybkich odbić skrzydeł przy zwolnieniu przed postojem",
            "good_for": "lądowanie skrzydlatej istoty, pobliskie zawisanie",
            "bad_for": "powolne majestatyczne suwy, kameralna cisza",
            "file": "audio/library/heroes/wing_foley_hover.mp3",
            "semantics": {"type": "lopot-skrzydel",
                          "traits": ["łopot", "wielkie skrzydła", "gęste odbicia", "żywy"],
                          "bad_for": ["trzepot owada", "trele", "statyczny szum"]},
            "source": _scout_src("wings-foley/freesound_wing-flap-foley", 4,
                                 "okno 3,1–6,9 s; HP 70; natywna wysokość"),
        },
    })
    print("  ł.2 zapisany")

    # --- ł.3: trzy ciężkie odbicia tkaniny (foley) — montaż z jednego źródła
    w, _ = dsp.load_any(F / "04-616859-wing-flap-flutter-carpet-fabric-foley-2012-wav.mp3")
    cuts = [(0.55, 1.55), (4.55, 5.95), (25.6, 27.4)]
    t = np.zeros((2, int(4.2 * dsp.SR)))
    for (a, b), at in zip(cuts, (0.0, 1.35, 2.7)):
        seg = hp(dsp.cut(w, a, b), 60.0)
        t = dsp.place(t, seg, at)
    t = dsp.normalize_rms(t, -19.0)
    t = dsp.fade(t, 0.2, 0.7)
    dsp.encode_mp3(CAND / "l3_ciezkie_od_bicia.mp3", dsp.peak_ceiling(t))
    cands.append({
        "label": "ł.3", "title": "trzy ciężkie odbicia tkaniny — jak uderzenia płócien",
        "file": "candidates/l3_ciezkie_od_bicia.mp3",
        "desc": "najcięższe zamachy z taśmy foley (dywan/tkanina), ułożone w rytm "
                "zstąpienia — potężne, pojedyncze trzepnięcia powietrza; "
                "aranżacja z jednego nagrania, bez spowolnienia",
        "source": _scout_src("wings-foley/freesound_wing-flap-foley", 3,
                             "okna 0,55–1.55 / 4,55–5,95 / 25,6–27,4; HP 60; -19 dB; montaż"),
        "entry": {
            "id": "wing_foley_fabric",
            "role": "łopot wielkich skrzydeł — ciężkie trzepnięcie",
            "character": "ciężki, materiałowy, mięsisty",
            "distance": "bliski", "energy": "wysoka", "duration_sec": 4.2,
            "desc": "trzy ciężkie odbicia jak płótno wiatrem — masa wielkich skrzydeł",
            "good_for": "potężne skrzydła, anioł niosący ciężar, duży ptaszek",
            "bad_for": "miękkie fale, subtelne tła, trele",
            "file": "audio/library/heroes/wing_foley_fabric.mp3",
            "semantics": {"type": "lopot-skrzydel",
                          "traits": ["łopot", "wielkie skrzydła", "ciężkie odbicia", "materiałowy"],
                          "bad_for": ["trzepot owada", "pisk", "metla szumu"]},
            "source": _scout_src("wings-foley/freesound_wing-flap-foley", 3,
                                 "3 okna; HP 60; natywna wysokość; montaż"),
        },
    })
    print("  ł.3 zapisany")
    return cands


# ---------------------------------------------------------------- koda: nadzieja DUROWA r2
GESTURES = {
    "g11a_major_bloom": {
        "semantic": "nadzieja — durowa łuna rozświetlająca (C-dur z lydyjskim błyskiem)",
        "desc": "ciepły durowy dwudźwięk nisko, nad nim rozjarza się aug (błysk), "
                "a na szczycie czyste C5+E5 — jak niebo otwierane warstwami światła",
        "notes": [
            {"midi": 60, "on": 0.0, "off": 1.10, "vel": 0.40},
            {"midi": 64, "on": 0.0, "off": 1.10, "vel": 0.38},
            {"midi": 68, "on": 0.75, "off": 1.65, "vel": 0.38},
            {"midi": 72, "on": 1.25, "off": 2.70, "vel": 0.46},
            {"midi": 76, "on": 1.25, "off": 2.70, "vel": 0.42},
        ],
    },
    "g11b_lydian_summit": {
        "semantic": "nadzieja — lydyjski wierzchołek nad durowym D",
        "desc": "bas D-F# trzyma durowy grunt, a melodia wspina się przez lydyjską "
                "kwartę Gis — światło, które nie chce spaść; wznoszenie jak błogość",
        "notes": [
            {"midi": 50, "on": 0.0, "off": 2.70, "vel": 0.36},
            {"midi": 54, "on": 0.0, "off": 2.70, "vel": 0.34},
            {"midi": 74, "on": 0.55, "off": 1.00, "vel": 0.44},
            {"midi": 80, "on": 1.05, "off": 2.00, "vel": 0.46},
            {"midi": 76, "on": 1.85, "off": 2.70, "vel": 0.40},
        ],
    },
    "g11c_home_arrival": {
        "semantic": "nadzieja — powrót do domu: durowy dopływ w C",
        "desc": "skoki radości E4→C5→E5 z lądowaniem na pełnym durowym dnie C3: "
                "melodia wraca tam, skąd wyszła — pociecha i należność",
        "notes": [
            {"midi": 64, "on": 0.00, "off": 0.50, "vel": 0.44},
            {"midi": 72, "on": 0.45, "off": 0.95, "vel": 0.44},
            {"midi": 76, "on": 0.95, "off": 2.70, "vel": 0.46},
            {"midi": 48, "on": 0.95, "off": 2.70, "vel": 0.36},
            {"midi": 60, "on": 1.30, "off": 2.70, "vel": 0.34},
        ],
    },
}


def gesture_candidates() -> list[dict]:
    instruments = json.loads((REPO / "data/library/instruments.json").read_text("utf-8"))
    piano = next(e for e in instruments["entries"] if e["id"] == "b_piano_steinway")
    piano_abs = {**piano, "samples": {m: str(REPO / p) for m, p in piano["samples"].items()}}
    cands: list[dict] = []
    labels = {"g11a_major_bloom": "n.1", "g11b_lydian_summit": "n.2", "g11c_home_arrival": "n.3"}
    for gid, spec in GESTURES.items():
        gesture = {"notes": spec["notes"], "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}}}
        r = coda_synth.render_coda(gesture, piano_abs, seed=110)
        for w in r.warnings:
            print(f"  ! {gid}: {w}")
        dsp.encode_mp3(CAND / f"{gid}.mp3", r.wave)
        cands.append({
            "label": labels[gid],
            "title": spec["semantic"].split("—", 1)[1].strip(),
            "file": f"candidates/{gid}.mp3",
            "desc": spec["desc"],
            "source": "gest autorski; podgląd na b_piano_steinway (render neutralny)",
            "entry": {
                "id": gid,
                "semantic": spec["semantic"],
                "desc": spec["desc"],
                "notes": spec["notes"],
                "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}},
                "instrument_tags": ["piano", "struck-light", "warm-keys"],
                "semantics": {"type": "nadzieja-ukojenie",
                              "traits": ["podniosła", "ciepła", "durowa", "rozświetlona"],
                              "bad_for": ["groza", "przygnębienie", "ironia", "molowa"]},
            },
        })
        print(f"  {gid} zapisany")
    return cands


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": "g027",
        "created": "2026-09-24",
        "story_id": "110",
        "note": "RUNDA 2 fabuły 110 po odrzuceniu g025 („żadne” ×3 z diagnozą właściciela). "
                "Bitwa: wyłącznie stal i ludzie z atomcut (CC0) — mediewalny zgiełk bez prochu; "
                "łopot: foley dużych skrzydeł (Freesound) z wyraźnymi odbiciami, bez pitch-down; "
                "nadzieja: gesty DUROWE (C-dur/lydyjski-D/powrót-C) na siatce steinwaya.",
        "entries": [
            {"slug": "tlo-bitwa-zgielk", "kind": "backgrounds",
             "role": "jedyny klocek typu tła `bitwa-zgielk` (15 fabuł; slot d fabuły 110)",
             "candidates": bg_candidates()},
            {"slug": "hero-lopot", "kind": "heroes",
             "role": "jedyny klocek typu hero `lopot-skrzydel` (18 fabuł; slot c fabuły 110)",
             "candidates": hero_candidates()},
            {"slug": "koda-nadzieja", "kind": "gestures",
             "role": "jedyny klocek typu kody `nadzieja-ukojenie` (22 fabuły; slot a fabuły 110)",
             "candidates": gesture_candidates()},
        ],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest g027 zapisany ({len(manifest['entries'])} wpisy)")


if __name__ == "__main__":
    main()
