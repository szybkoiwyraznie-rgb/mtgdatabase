#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g032 — PAKIET 5 zestawów naraz (zasada właściciela z 2026-09-25,
zob. AGENTS.md pkt 2): 2 kody-nastroje (gesty autorskie), 2 hero (prawdziwe
nagrania VCSL) i 1 instrumentacja (prawdziwe nagrania VCSL), po 3 kandydatów.

Priorytety z resolver.py --survey (po zamknięciu g031):
  1) koda-furia        mood `furia-dzikosc`        (24 fabuły) — fabuła 179 (Index)
  2) koda-zuchwalosc   mood `zuchwalosc-brawura`   (18 fabuł) — fabuła 8 (Goblin Deathraiders)
  3) hero-rezonans     hero `rezonans-magiczny`    (24 fabuły) — fabuła 5 (Academy Journeymage)
  4) hero-potezny      hero `potezny-cios`         (21 fabuł) — fabuła 84 (Garruk's Companion)
  5) instr-zimno       instrumentacja `zimno-szklista` (21 fabuł) — fabuła 76 (Negate)

Kody (1-2): gesty autorskie, podgląd neutralny na b_piano_steinway (jak g026/g030/g031).
Hero i instrument (3-5): prawdziwe nagrania — VCSL (CC0 1.0, github.com/sgossner/VCSL),
pobrane sparse-checkout do /tmp/vcsl_probe.

Definicje typów (taxonomy.json):
  furia-dzikosc:      "Furia, dzikość, żywioł — koda uderza bez kontroli."
  zuchwalosc-brawura: "Zuchwałość, brawura, pęd, przygoda — koda szarżuje z uśmiechem."
  rezonans-magiczny:  "Rezonans i wibracja magii: zaklęcia, runy, rytualne przepływy energii."
  potezny-cios:       "Pojedynczy ciężki cios, uderzenie, miażdżenie."
  zimno-szklista:     "Zimno: szkliste, kruche, mroźne barwy, brak ciepła."
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
import coda_synth  # noqa: E402
from build_gate_g003 import soft_limit  # noqa: E402

GATE = REPO / "data" / "gates" / "g032"
CAND = GATE / "candidates"
NOTES_DIR = GATE / "instr_notes"

VCSL = Path("/tmp/vcsl_probe")

VCSL_SRC = {
    "title": "Versilian Community Sample Library (VCSL)",
    "author": "Sam Gossner / Versilian Studios + społeczność",
    "license": "CC0 1.0",
    "url": "https://github.com/sgossner/VCSL",
    "channel": "git clone sparse z github.com/sgossner/VCSL",
}

NOTE_IDX = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
            "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+)$")


def note_token_to_midi(stem: str) -> int | None:
    for tok in stem.split("_"):
        m = NOTE_RE.fullmatch(tok)
        if m:
            return NOTE_IDX[m.group(1)] + 12 * (int(m.group(2)) + 1)
    return None


# ============================================================== KODY (gesty)
GESTURE_ENTRIES = {
    "koda-furia": {
        "story_id": "179", "typ": "furia-dzikosc",
        "role": "jedyny klocek typu kody `furia-dzikosc` (24 fabuły; slot a fabuły 179)",
        "gestures": {
            "g_feral_scatter": {
                "label": "f.1", "semantic": "furia — rozprysk bez porządku",
                "desc": "cztery nuty w bardzo nierównych odstępach i różnych rejestrach, "
                        "jakby coś wypadało z rąk w przypadkowej kolejności — żadnego rytmu, "
                        "żadnej kontroli",
                "notes": [
                    {"midi": 66, "on": 0.00, "off": 0.20, "vel": 0.75},
                    {"midi": 51, "on": 0.14, "off": 0.35, "vel": 0.65},
                    {"midi": 78, "on": 0.30, "off": 0.55, "vel": 0.70},
                    {"midi": 57, "on": 0.62, "off": 1.90, "vel": 0.80},
                ],
            },
            "g_feral_snap": {
                "label": "f.2", "semantic": "furia — nagłe pęknięcie iskry",
                "desc": "ostry, dysonansowy trzask bez przygotowania i bez wybrzmienia, "
                        "zaraz po nim drugi, cichszy — jak przeskok iskry między kartkami",
                "notes": [
                    {"midi": 78, "on": 0.00, "off": 0.12, "vel": 0.85},
                    {"midi": 61, "on": 0.00, "off": 0.12, "vel": 0.75},
                    {"midi": 82, "on": 0.30, "off": 0.45, "vel": 0.55},
                ],
            },
            "g_feral_stampede": {
                "label": "f.3", "semantic": "furia — pęd, który się nie zatrzyma",
                "desc": "pięć nisko pulsujących uderzeń przyspieszających bez kontroli, "
                        "urywa się nagle na szczycie napięcia — żywioł, nie muzyka",
                "notes": [
                    {"midi": 48, "on": 0.00, "off": 0.30, "vel": 0.60},
                    {"midi": 48, "on": 0.42, "off": 0.65, "vel": 0.65},
                    {"midi": 48, "on": 0.80, "off": 1.00, "vel": 0.70},
                    {"midi": 48, "on": 1.12, "off": 1.30, "vel": 0.78},
                    {"midi": 61, "on": 1.38, "off": 1.60, "vel": 0.85},
                ],
            },
        },
    },
    "koda-zuchwalosc": {
        "story_id": "8", "typ": "zuchwalosc-brawura",
        "role": "jedyny klocek typu kody `zuchwalosc-brawura` (18 fabuł; slot a fabuły 8)",
        "gestures": {
            "g_brave_charge": {
                "label": "z.1", "semantic": "brawura — szarża z uśmiechem",
                "desc": "trójdźwiękowy skok w górę z synkopowanym poślizgiem, ląduje na "
                        "jasnym, pełnym akordzie — szarża, która się cieszy sobą",
                "notes": [
                    {"midi": 55, "on": 0.00, "off": 0.22, "vel": 0.60},
                    {"midi": 62, "on": 0.20, "off": 0.42, "vel": 0.65},
                    {"midi": 67, "on": 0.38, "off": 0.60, "vel": 0.70},
                    {"midi": 74, "on": 0.58, "off": 1.80, "vel": 0.75},
                    {"midi": 62, "on": 0.58, "off": 1.80, "vel": 0.55},
                ],
            },
            "g_brave_swagger": {
                "label": "z.2", "semantic": "brawura — pewny siebie krok z przytupem",
                "desc": "kołyszący, synkopowany rytm średniego tempa — nie pędzi, "
                        "tylko idzie tak, jakby świat już należał do niego",
                "notes": [
                    {"midi": 60, "on": 0.00, "off": 0.30, "vel": 0.65},
                    {"midi": 60, "on": 0.45, "off": 0.60, "vel": 0.50},
                    {"midi": 64, "on": 0.65, "off": 0.95, "vel": 0.65},
                    {"midi": 67, "on": 1.05, "off": 1.90, "vel": 0.70},
                ],
            },
            "g_brave_leap": {
                "label": "z.3", "semantic": "brawura — jeden zuchwały skok",
                "desc": "pojedynczy, szeroki skok w górę (dziesiąta), lądujący jasno "
                        "i pewnie — jeden gest odwagi, bez wahania",
                "notes": [
                    {"midi": 55, "on": 0.00, "off": 0.25, "vel": 0.65},
                    {"midi": 72, "on": 0.20, "off": 1.90, "vel": 0.75},
                ],
            },
        },
    },
}


def gesture_candidates(spec: dict) -> list[dict]:
    instruments = json.loads((REPO / "data/library/instruments.json").read_text(encoding="utf-8"))
    piano = next(e for e in instruments["entries"] if e["id"] == "b_piano_steinway")
    piano_abs = {**piano, "samples": {m: str(REPO / p) for m, p in piano["samples"].items()}}
    cands: list[dict] = []
    for gid, g in spec["gestures"].items():
        gesture = {"notes": g["notes"], "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}}}
        r = coda_synth.render_coda(gesture, piano_abs, seed=int(spec["story_id"]))
        for w in r.warnings:
            print(f"  ! {gid}: {w}")
        dsp.encode_mp3(CAND / f"{gid}.mp3", r.wave)
        cands.append({
            "label": g["label"],
            "title": g["semantic"].split("—", 1)[1].strip(),
            "file": f"candidates/{gid}.mp3",
            "desc": g["desc"],
            "source": "gest autorski; podgląd na b_piano_steinway (render neutralny)",
            "entry": {
                "id": gid,
                "semantic": g["semantic"],
                "desc": g["desc"],
                "notes": g["notes"],
                "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}},
                "instrument_tags": ["piano", "struck-light", "percussion_low"],
                "semantics": {"type": spec["typ"], "traits": [], "bad_for": []},
            },
        })
        print(f"  {gid} zapisany")
    return cands


# =============================================================== HERO (audio)
def finish_hero(seg: np.ndarray, rms: float = -15.0, fade_out: float = 0.3) -> np.ndarray:
    seg = soft_limit(seg, crest_db=14.0, rounds=4)
    seg = dsp.normalize_rms(seg, rms)
    seg = dsp.fade(seg, 0.01, fade_out)
    peak = float(np.max(np.abs(seg)))
    ceiling = dsp.db_to_gain(-1.0)
    if peak > ceiling:
        seg *= ceiling / peak
    return seg


def hero_entry(entry_id, role, character, desc, sem, src, notes, dur):
    return {
        "id": entry_id, "role": role, "character": character,
        "distance": "bliski", "energy": "średnia",
        "duration_sec": dur, "desc": desc,
        "good_for": sem["good_for"], "bad_for": sem["bad_for_txt"],
        "file": f"audio/library/heroes/{entry_id}.mp3",
        "semantics": {"type": sem["type"], "traits": sem["traits"],
                      "bad_for": sem["bad_for"]},
        "source": dict(src, notes=notes),
    }


def hero_from_file(name, label, title, entry_id, src_path, sem, notes,
                    t0=0.0, t1=None, lowpass=None, rms=-15.0, fade_out=0.3,
                    desc="", character=""):
    w, _ = dsp.load_any(src_path)
    if t1 is None:
        t1 = w.shape[1] / dsp.SR
    seg = w[:, int(t0 * dsp.SR):int(t1 * dsp.SR)].copy()
    if lowpass:
        sos = butter(4, lowpass, btype="lowpass", fs=dsp.SR, output="sos")
        seg = sosfiltfilt(sos, seg, axis=-1)
    seg = finish_hero(seg, rms=rms, fade_out=fade_out)
    path = CAND / f"{name}.mp3"
    dsp.encode_mp3(path, seg)
    dur = round(seg.shape[1] / dsp.SR, 2)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": VCSL_SRC["title"],
        "entry": hero_entry(entry_id, sem["role"], character, desc, sem,
                             VCSL_SRC, notes, dur),
    }


def hero_rezonans_candidates() -> list[dict]:
    sem = {
        "type": "rezonans-magiczny",
        "role": "rezonans i wibracja magii — zaklęcia, runy, rytualne przepływy energii",
        "traits": ["rezonujący", "wibrujący", "eteryczny", "sustain"],
        "bad_for": ["perkusyjny", "suchy", "organiczny"],
        "good_for": "aktywacja zaklęcia, runy, portal, rytuał, przepływ mocy",
        "bad_for_txt": "walka wprost, uderzenia fizyczne, naturalistyczna fauna",
    }
    d = VCSL / "Idiophones/Struck Idiophones/Vibraphone/Bowed"
    fx = VCSL / "Idiophones/Struck Idiophones/Flexatone"
    bt = VCSL / "Idiophones/Struck Idiophones/Bell Tree"
    return [
        hero_from_file("m_vibes_bowed", "r.1", "smyczkowany wibrafon — ciepły rezonans",
                        "resonance_bowed_01", d / "Vibes_bowed_D4_rr1_Main.wav", sem,
                        "Vibraphone Bowed D4 (VCSL); głośny fragment 1.15–4.65 s "
                        "(źródło ma bardzo cichą głowę), poziom, fade",
                        t0=1.15, t1=4.65, rms=-15.0, fade_out=0.6,
                        desc="smyczkowany talerz wibrafonu — długi, aksamitny rezonans, "
                             "jak brzęczenie zaklęcia dochodzące zewsząd naraz",
                        character="ciepły, wibrujący, aksamitny"),
        hero_from_file("m_flexatone", "r.2", "flexaton — falująca, nieziemska wibracja",
                        "resonance_flexatone_01", fx / "flexatone_extralong.wav", sem,
                        "Flexatone extralong (VCSL); głośniejszy fragment 8.0–11.5 s "
                        "po audycji okien, poziom, fade",
                        t0=8.0, t1=11.5, rms=-15.5, fade_out=0.5,
                        desc="metalowa płytka faluje w rękach — niepokojąca, żywa "
                             "wibracja, jakby powietrze samo drżało od magii",
                        character="falujący, niepokojący, żywy"),
        hero_from_file("m_belltree", "r.3", "drzewko dzwonków — kaskada glifów",
                        "resonance_belltree_01", bt / "Stroke/BellTree_Stroke_6_Mid.wav", sem,
                        "Bell Tree stroke 6 (VCSL); aktywny fragment 0.0–2.4 s, poziom, fade",
                        t0=0.0, t1=2.4, rms=-15.0, fade_out=0.45,
                        desc="delikatna kaskada dzwonków — jak seria świecących glifów "
                             "zapalających się jeden po drugim",
                        character="kaskadowy, jasny, delikatny"),
    ]


def hero_potezny_candidates() -> list[dict]:
    sem = {
        "type": "potezny-cios",
        "role": "pojedynczy ciężki cios, uderzenie, miażdżenie",
        "traits": ["ciężki", "niski", "jednorazowy", "masywny"],
        "bad_for": ["subtelny", "wysoki", "delikatny"],
        "good_for": "uderzenie, zmiażdżenie przeszkody, potężny cios, powalenie",
        "bad_for_txt": "magia, subtelność, cichy ruch, delikatne sceny",
    }
    bd = VCSL / "Membranophones/Struck Membranophones/Bass Drum 2"
    gg = VCSL / "Idiophones/Struck Idiophones/Gong 1"
    tp = VCSL / "Membranophones/Struck Membranophones/Timpani 1/Hit"
    return [
        hero_from_file("p_bassdrum_hit", "p.1", "uderzenie w wielki bęben — głuchy łomot",
                        "heavyblow_bassdrum_01", bd / "bassdrum_hit_ff.wav", sem,
                        "Bass Drum 2 hit ff (VCSL); pierwsze 4.5 s (dalej cisza pomieszczenia), poziom, fade",
                        t0=0.0, t1=4.5, rms=-12.0, fade_out=1.0,
                        desc="jedno potężne uderzenie w wielki bęben — głuchy, masywny "
                             "łomot bez wybrzmienia w wysokich tonach",
                        character="głuchy, masywny, krótki"),
        hero_from_file("p_gong_crush", "p.2", "uderzenie w gong — miażdżący rozdzwon",
                        "heavyblow_gong_01", gg / "gong_fff.wav", sem,
                        "Gong 1 fff (VCSL); pierwsze 3 s, poziom, fade",
                        t0=0.0, t1=3.0, rms=-13.0, fade_out=0.8,
                        desc="ogromny gong uderzony z całej siły — metaliczny huk "
                             "rozlewający się i miażdżący wszystko dookoła",
                        character="miażdżący, rozlewający się, metaliczny"),
        hero_from_file("p_timpani_hit", "p.3", "uderzenie w kocioł — grzmiące trzaśnięcie",
                        "heavyblow_timpani_01", tp / "Timpani1_Hit_v4_rr1_Sum.wav", sem,
                        "Timpani 1, uderzenie v4 (VCSL); pierwsze 3.5 s (dalej cisza pomieszczenia), poziom, fade",
                        t0=0.0, t1=3.5, rms=-12.5, fade_out=0.8,
                        desc="grzmiące, napięte uderzenie w kocioł — twardszy atak niż "
                             "bęben, wyraźny ton pod spodem",
                        character="grzmiący, napięty, tonalny"),
    ]


# ========================================================= INSTRUMENTY (audio)
def _load_bank(src_dir: Path, want_sub: str | None, keep_ext: str = ".wav") -> dict[int, Path]:
    bank: dict[int, Path] = {}
    for f in sorted(src_dir.glob(f"*{keep_ext}")):
        if want_sub and want_sub not in f.stem:
            continue
        midi = note_token_to_midi(f.stem)
        if midi is not None:
            bank[midi] = f
    return bank


def _register_instrument(iid: str, label: str, title: str, semantic: str, desc: str,
                          traits: list[str], bad_for: list[str], src_notes: str,
                          bank: dict[int, Path], demo_notes: list[dict],
                          family: str, out_subdir: str) -> dict:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    gate_sources: dict[str, str] = {}
    lib_samples: dict[str, str] = {}
    for midi, src_path in sorted(bank.items()):
        out_name = f"{iid}_{src_path.stem}.mp3"
        w, _ = dsp.load_any(src_path)
        dsp.encode_mp3(NOTES_DIR / out_name, dsp.cut(w, 0.0, 2.2))
        gate_sources[str(midi)] = f"instr_notes/{out_name}"
        lib_samples[str(midi)] = f"audio/library/instruments/{out_subdir}/{out_name}"
    inst_abs = {"samples": {m: str(NOTES_DIR / Path(p).name) for m, p in gate_sources.items()}}
    r = coda_synth.render_coda({"notes": demo_notes, "delivery": {}}, inst_abs, seed=32)
    for w in r.warnings:
        print(f"  ! demo {iid}: {w}")
    dsp.encode_mp3(CAND / f"{iid}_demo.mp3", r.wave)
    lo = dsp.midi_to_name(min(bank)) if bank else "?"
    hi = dsp.midi_to_name(max(bank)) if bank else "?"
    return {
        "label": label, "title": title,
        "file": f"candidates/{iid}_demo.mp3",
        "desc": f"{desc} — bank {len(bank)} nut {lo}–{hi}",
        "source": f"{VCSL_SRC['title']} — {VCSL_SRC['license']}",
        "entry": {
            "id": iid, "semantic": semantic, "family": family,
            "samples": lib_samples, "gate_sources": gate_sources,
            "semantics": {"type": "", "traits": traits, "bad_for": bad_for},
            "source": {**VCSL_SRC, "notes": src_notes},
        },
    }


def instr_zimno_candidates() -> list[dict]:
    typ = "zimno-szklista"
    cands = []
    # i.1 — Vibraphone Hard Mallets (VCSL): zimny, metaliczny mallet, szeroki bank
    vibes_dir = VCSL / "Idiophones/Struck Idiophones/Vibraphone/Hard Mallets"
    bank = _load_bank(vibes_dir, "_v2_")
    demo = [
        {"midi": 41, "on": 0.00, "off": 0.55, "vel": 0.6},
        {"midi": 53, "on": 0.45, "off": 1.00, "vel": 0.6},
        {"midi": 62, "on": 0.90, "off": 1.45, "vel": 0.65},
        {"midi": 76, "on": 1.35, "off": 2.20, "vel": 0.6},
    ]
    cand = _register_instrument(
        "b_vibraphone_cold", "i.1", "wibrafon — zimny, metaliczny mallet",
        "chłodny, metaliczny rezonans wibrafonu — szklisty połysk bez ciepła",
        "twarde pałeczki uderzają w metalowe płytki, długie chłodne wybrzmienie",
        ["zimny", "metaliczny", "szklisty", "rezonujący"], ["ciepły", "organiczny", "matowy"],
        "Vibraphone, twarde pałeczki (mallets), wariacja v2 (VCSL); bank 11 nut F2–E5",
        bank, demo, "idiophone-struck", "vibraphone_cold")
    cand["entry"]["semantics"]["type"] = typ
    cands.append(cand)
    # i.2 — Glockenspiel (VCSL): jasne, lodowate dzwonki
    glock_dir = VCSL / "Idiophones/Struck Idiophones/Glockenspiel"
    bank = _load_bank(glock_dir, "_medium_")
    demo = [
        {"midi": 67, "on": 0.00, "off": 0.45, "vel": 0.6},
        {"midi": 72, "on": 0.40, "off": 0.85, "vel": 0.65},
        {"midi": 79, "on": 0.80, "off": 1.25, "vel": 0.6},
        {"midi": 84, "on": 1.20, "off": 2.00, "vel": 0.65},
    ]
    cand = _register_instrument(
        "b_glockenspiel_cold", "i.2", "dzwonki — jasne, lodowate uderzenie metalu",
        "wysokie, krystalicznie czyste dzwonki — najbardziej dosłowny 'lód i szkło'",
        "cienkie metalowe płytki, ostry, jasny atak i szybkie, zimne wybrzmienie",
        ["zimny", "krystaliczny", "jasny", "cienki"], ["ciepły", "niski", "matowy"],
        "Glockenspiel, dynamika 'medium' (VCSL); bank 6 nut G4–C7 (skala G/C na oktawę)",
        bank, demo, "idiophone-struck", "glockenspiel_cold")
    cand["entry"]["semantics"]["type"] = typ
    cands.append(cand)
    # i.3 — Wine Glasses (VCSL): dosłowne szkło, wąski bank
    glass_dir = VCSL / "Idiophones/Friction Idiophones/Wine Glasses/Sustains/Slow"
    bank: dict[int, Path] = {}
    for f in sorted(glass_dir.glob("*.wav")):
        midi = note_token_to_midi(f.stem)
        if midi is not None:
            bank[midi] = f
    demo = [
        {"midi": 63, "on": 0.00, "off": 0.70, "vel": 0.55},
        {"midi": 66, "on": 0.60, "off": 1.30, "vel": 0.55},
        {"midi": 70, "on": 1.20, "off": 1.90, "vel": 0.6},
        {"midi": 74, "on": 1.80, "off": 2.60, "vel": 0.55},
    ]
    cand = _register_instrument(
        "b_wineglass_cold", "i.3", "szklanki — dosłowne, kruche szkło",
        "prawdziwe kieliszki potarte mokrym palcem — najbardziej dosłowne 'szkło' z całej biblioteki",
        "cienki, szklisty ton z lekkim drżeniem — kruchy, niemal przezroczysty",
        ["zimny", "szklany", "kruchy", "cienki"], ["ciepły", "masywny", "perkusyjny"],
        "Wine Glasses, Sustains/Slow (VCSL); bank 4 nut D#4–D5 (wąski — realizacja rytmiczna)",
        bank, demo, "idiophone-friction", "wineglass_cold")
    cand["entry"]["semantics"]["type"] = typ
    cands.append(cand)
    return cands


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    entries = []
    for slug, spec in GESTURE_ENTRIES.items():
        entries.append({"slug": slug, "kind": "gestures", "role": spec["role"],
                         "candidates": gesture_candidates(spec)})
    entries.append({"slug": "hero-rezonans", "kind": "heroes",
                     "role": "jedyny klocek typu hero `rezonans-magiczny` "
                             "(24 fabuły; slot c fabuły 5)",
                     "candidates": hero_rezonans_candidates()})
    entries.append({"slug": "hero-potezny", "kind": "heroes",
                     "role": "jedyny klocek typu hero `potezny-cios` "
                             "(21 fabuł; slot c fabuły 84)",
                     "candidates": hero_potezny_candidates()})
    entries.append({"slug": "instr-zimno", "kind": "instruments",
                     "role": "jedyny klocek typu instrumentacji `zimno-szklista` "
                             "(21 fabuł; slot b fabuły 76)",
                     "candidates": instr_zimno_candidates()})
    manifest = {
        "id": "g032",
        "created": "2026-09-26",
        "note": "PAKIET 5 zestawów naraz (zasada właściciela z 2026-09-25). 2 kody autorskie "
                "(mood: furia-dzikość, zuchwałość-brawura — podgląd na b_piano_steinway) + "
                "2 hero (rezonans-magiczny: wibrafon smyczkowany/flexaton/drzewko dzwonków; "
                "potężny-cios: bęben/gong/kocioł) + 1 instrumentacja (zimno-szklista: "
                "wibrafon/dzwonki/kieliszki), wszystko VCSL CC0 1.0. Anchory: fabuły 179, 8, "
                "5, 84, 76 (każda miała dokładnie jeden brak — reszta obsadzona przez resolver).",
        "entries": entries,
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest g032 zapisany ({len(manifest['entries'])} wpisów)")


if __name__ == "__main__":
    main()
