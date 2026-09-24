#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g017 — dwa jedyne klocki hero: `rozblysk-swiatla` i `skradanie-cisza`.

Kandydaci oceniani pod definicje TYPÓW (lekcja g015):
  * rozblysk-swiatla — „Narastający świetlisty rozbłysk, aura, promień, snop
    światła." Domyka fabułę 23; docelowo woła go ~25 fabuł.
  * skradanie-cisza — „Niemal bezgłośny ruch, cicha warta — napięcie zamiast
    hałasu." Domyka fabuły 166 i 519; docelowo 22 fabuły.

Źródła: VCSL (CC0) — mark trees / bell tree / talerz; YSL (public domain) —
cichy ruch powietrza. Obróbka przezroczysta i opisana per kandydat.
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
from build_gate_g003 import soft_limit  # noqa: E402
from build_gate_g015 import YSL_SRC, VCSL_SRC  # noqa: E402

GATE = REPO / "data" / "gates" / "g017"
CAND = GATE / "candidates"
YSL = Path("/tmp/ysl")
VC = Path("/tmp/vcsl/Idiophones/Struck Idiophones")


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


def from_file(name, label, title, entry_id, src_path, sem, src_meta, notes,
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
        "desc": desc, "source": f"{src_meta['title']}",
        "entry": hero_entry(entry_id, sem["role"], character, desc, sem,
                            src_meta, notes, dur),
    }


def quietest_window(wave: np.ndarray, sec: float, step: float = 0.5) -> float:
    n = wave.shape[1]
    best_t, best = 0.0, 1e9
    t = 0.0
    while (t + sec) * dsp.SR < n:
        seg = wave[:, int(t * dsp.SR):int((t + sec) * dsp.SR)]
        r = dsp.rms_db(seg)
        if r < best:
            best_t, best = t, r
        t += step
    return best_t


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)

    SEM_ROZBLYSK = {
        "type": "rozblysk-swiatla",
        "role": "narastający świetlisty rozbłysk",
        "traits": ["narastający", "jasny", "dzwoniący", "kaskadowy"],
        "bad_for": ["mroczny", "ciężki", "perkusyjny huk"],
        "good_for": "magiczne ujawnienie, aura światła, promień, uświęcenie",
        "bad_for_txt": "mroczne zaklęcia, eksplozje, naturalistyczna fauna",
    }
    SEM_SKRADANIE = {
        "type": "skradanie-cisza",
        "role": "niemal bezgłośny ruch — napięcie zamiast hałasu",
        "traits": ["cichy", "powolny", "napięty", "powietrzny"],
        "bad_for": ["głośny", "gwałtowny", "dzwoniący"],
        "good_for": "infiltracja, cicha warta, czatowanie, bezszelestny ruch",
        "bad_for_txt": "walka wprost, fanfary, jawne wejścia",
    }

    entries = [
        {
            "slug": "rozblysk-swiatla",
            "kind": "heroes",
            "role": "jedyny klocek typu `rozblysk-swiatla` (domyka fabułę 23; woła ~25 fabuł)",
            "candidates": [
                from_file("c_chimes_asc", "c.1", "wznosząca kaskada dzwonków",
                          "light_bloom_01", VC / "Mark Trees/Legacy/windchimes_asc1.wav",
                          SEM_ROZBLYSK, VCSL_SRC,
                          "Mark Trees windchimes_asc1, pierwsze 3.5 s; poziom, fade — bez pitchowania",
                          t0=0.0, t1=3.5, fade_out=0.5,
                          desc="dzwonki wiatrowe wznoszą się kaskadą — światło rozlewa się w górę",
                          character="wznoszący, migotliwy"),
                from_file("c_belltree", "c.2", "pociągnięcie drzewka dzwonków",
                          "light_bloom_02", VC / "Bell Tree/Stroke/BellTree_Stroke_4_Mid.wav",
                          SEM_ROZBLYSK, VCSL_SRC,
                          "Bell Tree stroke 4, pierwsze 3.5 s; poziom, fade — bez pitchowania",
                          t0=0.0, t1=3.5, fade_out=0.5,
                          desc="jedno płynne pociągnięcie drzewka dzwonków — snop światła w jednym geście",
                          character="płynny, świetlisty"),
                from_file("c_cym_swell", "c.3", "rozjarzenie talerza",
                          "light_bloom_03", VC / "Suspended Cymbal 1/susCymb1_cresc_2s.wav",
                          SEM_ROZBLYSK, VCSL_SRC,
                          "Suspended Cymbal cresc 2 s + 1.5 s wybrzmienia; poziom, fade",
                          t0=0.0, t1=3.5, fade_out=0.8,
                          desc="dwusekundowe crescendo talerza — aura narasta i rozjarza się",
                          character="narastający, szumiąco-świetlisty"),
            ],
        },
        {
            "slug": "skradanie-cisza",
            "kind": "heroes",
            "role": "jedyny klocek typu `skradanie-cisza` (domyka fabuły 166 i 519; woła 22 fabuły)",
            "candidates": [],
        },
    ]

    vent = YSL / "Hurricane Vent/Sound Library - Hurricane Vent.mp3"
    scape = YSL / "Soundscapes/Soundscapes.mp3"
    w_s, _ = dsp.load_any(scape)
    t_q = quietest_window(w_s, 3.0)
    print(f"najcichsze okno Soundscapes @{t_q:.1f}s")

    entries[1]["candidates"] = [
        from_file("s_air_slide", "c.1", "cichy przesuw powietrza",
                  "stealth_move_01", vent, SEM_SKRADANIE, YSL_SRC,
                  "Hurricane Vent 12–15 s; lowpass 500 Hz (odjęte syczenie), poziom, długie fade",
                  t0=12.0, t1=15.0, lowpass=500.0, rms=-18.0, fade_out=0.8,
                  desc="miękki, ciemny przesuw powietrza — ktoś przemieszcza się tuż obok, bez jednego szelestu",
                  character="ciemny, płynny, wstrzymany"),
        from_file("s_held_space", "c.2", "zamarła przestrzeń",
                  "stealth_move_02", scape, SEM_SKRADANIE, YSL_SRC,
                  f"Soundscapes {t_q:.1f}–{t_q+3:.1f} s (najcichsze okno nagrania); poziom, długie fade",
                  t0=t_q, t1=t_q + 3.0, rms=-20.0, fade_out=0.8,
                  desc="niemal martwa cisza z ledwie obecnym ruchem tła — czatowanie z wstrzymanym oddechem",
                  character="statyczny, napięty, ledwie obecny"),
        from_file("s_bowed_cym", "c.3", "smyczek po talerzu pp",
                  "stealth_move_03", VC / "Suspended Cymbal 1/susCymb1_bow_13.wav",
                  SEM_SKRADANIE, VCSL_SRC,
                  "Suspended Cymbal bow 13, pierwsze 4 s; poziom -18, fade — bez pitchowania",
                  t0=0.0, t1=4.0, rms=-18.0, fade_out=0.8,
                  desc="smyczkowany talerz pianissimo — cienka, nieziemska nić napięcia w ciszy",
                  character="szklisty, widmowy, napięty"),
    ]

    manifest = {
        "id": "g017",
        "created": "2026-09-24",
        "note": ("Etap 5. Dwa jedyne klocki hero w jednej rundzie werdyktów: "
                 "rozblysk-swiatla (domyka 23) i skradanie-cisza (domyka 166 "
                 "i 519). Kandydaci pod definicje typów."),
        "entries": entries,
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for e in entries:
        for c in e["candidates"]:
            p = GATE / c["file"]
            print(f"  {e['slug'][:18]:18s} {c['label']} {c['title']:32s} "
                  f"{p.stat().st_size/1024:5.0f} KB {c['entry']['duration_sec']} s")
    print("manifest g017 zapisany")


if __name__ == "__main__":
    main()
