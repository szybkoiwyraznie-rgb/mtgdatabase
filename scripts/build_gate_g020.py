#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g020 — trzy braki wylosowanej fabuły 193 (Floodhound):

  c  hero   `fala-rozbryzg`            — uderzenie wody: kipiel, rozbryzg (19 fabuł)
  a  koda   `determinacja-niezlomnosc` — nieustępliwość, miarowy upór (32 fabuły)
  b  instr  `cicho-kameralna`          — drobno, oszczędnie, blisko ucha (65 fabuł!)

Tło fabuły 193 (burza-zywiol -> thunder_far_01) już w bazie.
Kandydaci pod definicje TYPÓW. Źródła: YSL (public domain), VCSL (CC0).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
import coda_synth  # noqa: E402
from build_gate_g003 import soft_limit  # noqa: E402
from build_gate_g015 import YSL_SRC, VCSL_SRC, loudest_window  # noqa: E402

GATE = REPO / "data" / "gates" / "g020"
CAND = GATE / "candidates"
YSL = Path("/tmp/ysl")

NOTE_RE = re.compile(r"([A-G]#?)(\d)")
NOTE_OFF = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
            "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def midi_of(name: str) -> int | None:
    m = NOTE_RE.search(name)
    if not m:
        return None
    return NOTE_OFF[m.group(1)] + (int(m.group(2)) + 1) * 12


def finish_hero(seg, rms=-15.0):
    seg = soft_limit(seg, crest_db=14.0, rounds=4)
    seg = dsp.normalize_rms(seg, rms)
    seg = dsp.fade(seg, 0.03, 0.35)
    peak = float(np.max(np.abs(seg)))
    ceil = dsp.db_to_gain(-1.0)
    if peak > ceil:
        seg *= ceil / peak
    return seg


def hero_cand(name, label, title, entry_id, src, t0, dur, desc, character, notes):
    w, _ = dsp.load_any(src)
    seg = finish_hero(w[:, int(t0 * dsp.SR):int((t0 + dur) * dsp.SR)].copy())
    dsp.encode_mp3(CAND / f"{name}.mp3", seg)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": "YSL — public domain",
        "entry": {
            "id": entry_id, "role": "uderzenie wody — fala, kipiel, rozbryzg",
            "character": character, "distance": "bliski", "energy": "wysoka",
            "duration_sec": round(seg.shape[1] / dsp.SR, 2), "desc": desc,
            "good_for": "fala, rozbryzg, kipiel, wodny żywioł, wynurzenie",
            "bad_for": "ogień, suche wnętrza, delikatne sceny",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "semantics": {"type": "fala-rozbryzg",
                          "traits": ["uderzenie wody", "kipiel", "naturalny", "dynamiczny"],
                          "bad_for": ["suchy", "ognisty", "metaliczny"]},
            "source": dict(YSL_SRC, notes=notes),
        },
    }


GESTURES = {
    "g8a_step_by_step": {
        "semantic": "determinacja — krok za krokiem, nigdy wstecz",
        "desc": "pary niskich nut wspinają się bez cofnięcia i osiadają na "
                "wyższym stopniu — upór, który nie zna odwrotu",
        "notes": [
            {"midi": 48, "on": 0.0, "off": 0.4, "vel": 0.46},
            {"midi": 48, "on": 0.5, "off": 0.9, "vel": 0.46},
            {"midi": 50, "on": 1.0, "off": 1.4, "vel": 0.48},
            {"midi": 50, "on": 1.5, "off": 1.9, "vel": 0.48},
            {"midi": 54, "on": 2.0, "off": 2.7, "vel": 0.50},
        ],
    },
    "g8b_knocked_returns": {
        "semantic": "determinacja — zbity, wraca wyżej",
        "desc": "figura schodzi o stopień jak po ciosie i natychmiast wraca "
                "ponad punkt wyjścia — nieustępliwość w jednym geście",
        "notes": [
            {"midi": 60, "on": 0.00, "off": 0.35, "vel": 0.50},
            {"midi": 56, "on": 0.45, "off": 0.80, "vel": 0.44},
            {"midi": 60, "on": 0.90, "off": 1.25, "vel": 0.50},
            {"midi": 64, "on": 1.35, "off": 2.3, "vel": 0.52},
        ],
    },
    "g8c_steady_pulse": {
        "semantic": "determinacja — puls, który nie gaśnie",
        "desc": "niski fundament trwa, a nad nim równy puls powtarza się bez "
                "jednego zawahania — cierpliwy pościg",
        "notes": [
            {"midi": 48, "on": 0.0, "off": 2.5, "vel": 0.40},
            {"midi": 60, "on": 0.0, "off": 0.4, "vel": 0.46},
            {"midi": 60, "on": 0.6, "off": 1.0, "vel": 0.46},
            {"midi": 60, "on": 1.2, "off": 1.6, "vel": 0.46},
            {"midi": 60, "on": 1.8, "off": 2.5, "vel": 0.46},
        ],
    },
}


def gesture_cand(gid, label, title):
    spec = GESTURES[gid]
    instruments = json.loads((REPO / "data/library/instruments.json").read_text("utf-8"))
    piano = next(e for e in instruments["entries"] if e["id"] == "b_piano_steinway")
    piano_abs = {**piano, "samples": {m: str(REPO / p) for m, p in piano["samples"].items()}}
    r = coda_synth.render_coda({"notes": spec["notes"],
                                "delivery": {"humanize": {"timing_ms": 12, "vel": 0.03}}},
                               piano_abs, seed=193)
    dsp.encode_mp3(CAND / f"{gid}.mp3", r.wave)
    return {
        "label": label, "title": title, "file": f"candidates/{gid}.mp3",
        "desc": spec["desc"],
        "source": "gest autorski; podgląd na b_piano_steinway (render neutralny)",
        "entry": {
            "id": gid, "semantic": spec["semantic"], "desc": spec["desc"],
            "notes": spec["notes"],
            "delivery": {"humanize": {"timing_ms": 12, "vel": 0.03}},
            "instrument_tags": ["struck-light", "plucked", "piano"],
            "semantics": {"type": "determinacja-niezlomnosc",
                          "traits": ["miarowy", "nieustępliwy", "prosty", "bez wahania"],
                          "bad_for": ["chwiejny", "żałobny", "figlarny"]},
        },
    }


INSTR = {
    "b_kalimba": {
        "dir": Path("/tmp/vcsl/Idiophones/Plucked Idiophones/Kalimba, Kenya"),
        "pick": "vl3_rr2", "semantic": "cichy, ciepły, blisko ucha",
        "family": "lamellophone", "title": "kalimba",
        "desc": "drewniane języczki tuż przy uchu — ciepło i intymnie",
    },
    "b_dantranh": {
        "dir": Path("/tmp/vcsl/Chordophones/Zithers/Dan Tranh/Normal"),
        "pick": "_mf_", "fallback": "_f_", "semantic": "cichy, srebrzysty, kameralny",
        "family": "zither-plucked", "title": "cytra dan tranh",
        "desc": "delikatnie szarpana cytra — srebrzysta nić melodii",
    },
    "b_handchimes": {
        "dir": Path("/tmp/vcsl/Idiophones/Struck Idiophones/Hand Chimes"),
        "pick": "sus_", "semantic": "cichy, dzwonkowy, miękki",
        "family": "idiophone-struck", "title": "dzwonki ręczne",
        "desc": "miękkie pojedyncze dzwonki — kameralne, bez blasku orkiestry",
    },
}

DEMO = {"notes": [
    {"midi": 60, "on": 0.0, "off": 0.7, "vel": 0.55},
    {"midi": 63, "on": 0.25, "off": 1.0, "vel": 0.55},
    {"midi": 66, "on": 0.5, "off": 1.3, "vel": 0.55},
    {"midi": 71, "on": 0.8, "off": 2.2, "vel": 0.6},
]}


def instr_cand(iid, label):
    spec = INSTR[iid]
    files = {}
    for f in sorted(spec["dir"].glob("*.wav")):
        if spec["pick"] not in f.name and spec.get("fallback", "\x00") not in f.name:
            continue
        m = midi_of(f.name)
        if m is None or not (45 <= m <= 86):
            continue
        if m not in files or spec["pick"] in f.name:
            files[m] = f
    assert len(files) >= 6, f"{iid}: za mało nut ({len(files)})"
    gate_sources = {}
    for m, f in sorted(files.items()):
        w, _ = dsp.load_any(f)
        out = GATE / "instr_notes" / f"{iid}_{f.name.replace('.wav', '.mp3').replace('#', 's')}"
        out.parent.mkdir(parents=True, exist_ok=True)
        dsp.encode_mp3(out, w)
        gate_sources[str(m)] = f"instr_notes/{out.name}"
    entry = {
        "id": iid, "semantic": spec["semantic"], "family": spec["family"],
        "samples": {m: f"audio/library/instruments/{iid.replace('b_', '')}/{Path(rel).name}"
                    for m, rel in gate_sources.items()},
        "gate_sources": gate_sources,
        "semantics": {"type": "cicho-kameralna",
                      "traits": ["cichy", "drobny", "blisko ucha", "mała dynamika"],
                      "bad_for": ["monumentalny", "huczny", "industrialny"]},
        "source": dict(VCSL_SRC, notes=f"{len(gate_sources)} nut; wybór {spec['pick']}"),
    }
    inst_abs = {**entry, "samples": {m: str(GATE / rel) for m, rel in gate_sources.items()}}
    r = coda_synth.render_coda(DEMO, inst_abs, seed=193)
    dsp.encode_mp3(CAND / f"{iid}_demo.mp3", r.wave)
    return {
        "label": label, "title": spec["title"], "file": f"candidates/{iid}_demo.mp3",
        "desc": spec["desc"], "source": "VCSL — CC0 (fraza demonstracyjna)",
        "entry": entry,
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    castle = YSL / "Castle Geyser/Sound Library - Castle Geyser.mp3"
    grand = YSL / "Grand Geyser/Sound Library - Grand Geyser.mp3"
    faithful = YSL / "Old Faithful Geyser/Sound Library - Old Faithful.mp3"

    w_c, _ = dsp.load_any(castle)
    w_g, _ = dsp.load_any(grand)
    w_f, _ = dsp.load_any(faithful)
    t_c = loudest_window(w_c, 3.2)
    t_g = loudest_window(w_g, 3.2)
    t_f = loudest_window(w_f, 3.2)
    print(f"okna: castle @{t_c:.1f}, grand @{t_g:.1f}, faithful @{t_f:.1f}")

    entries = [
        {"slug": "fala-rozbryzg", "kind": "heroes",
         "role": "jedyny klocek typu hero `fala-rozbryzg` (19 fabuł; slot c fabuły 193)",
         "candidates": [
             hero_cand("c_castle_surge", "c.1", "kipiel gejzeru (Castle)", "wave_crash_01",
                       castle, t_c, 3.2,
                       "wzburzona kipiel wody — masa wody przewala się i rozbryzguje",
                       "kipiący, masywny, naturalny",
                       f"Castle Geyser, okno {t_c:.1f}–{t_c+3.2:.1f} s; poziom i fade"),
             hero_cand("c_grand_wave", "c.2", "szeroka fala erupcji (Grand)", "wave_crash_02",
                       grand, t_g, 3.2,
                       "szerokie uderzenie fali z długim mokrym ogonem",
                       "szeroki, falujący, mokry",
                       f"Grand Geyser, okno {t_g:.1f}–{t_g+3.2:.1f} s; poziom i fade"),
             hero_cand("c_faithful_burst", "c.3", "rozbryzg u podstawy erupcji (Old Faithful)", "wave_crash_03",
                       faithful, t_f, 3.2,
                       "gwałtowny rozbryzg i syczący opad kropel",
                       "gwałtowny, rozpryskowy, syczący",
                       f"Old Faithful, okno {t_f:.1f}–{t_f+3.2:.1f} s; poziom i fade"),
         ]},
        {"slug": "koda-determinacja", "kind": "gestures",
         "role": "koda `determinacja-niezlomnosc` (32 fabuły; slot a fabuły 193)",
         "candidates": [gesture_cand("g8a_step_by_step", "a.1", "krok za krokiem"),
                        gesture_cand("g8b_knocked_returns", "a.2", "zbity, wraca wyżej"),
                        gesture_cand("g8c_steady_pulse", "a.3", "puls, który nie gaśnie")]},
        {"slug": "instrument-kameralny", "kind": "instruments",
         "role": "instrument `cicho-kameralna` (65 fabuł! — slot b fabuły 193)",
         "candidates": [instr_cand("b_kalimba", "b.1"),
                        instr_cand("b_dantranh", "b.2"),
                        instr_cand("b_handchimes", "b.3")]},
    ]
    manifest = {
        "id": "g020", "created": "2026-09-24", "story_id": "193",
        "note": ("Tryb losowy: fabuła 193 Floodhound. Trzy braki naraz "
                 "(tło thunder_far_01 już w bazie). `cicho-kameralna` to "
                 "najczęściej wołany brakujący instrument (65 fabuł)."),
        "entries": entries,
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for e in entries:
        for c in e["candidates"]:
            p = GATE / c["file"]
            print(f"  {e['slug'][:20]:20s} {c['label']} {c['title']:40s} {p.stat().st_size/1024:5.0f} KB")
    print("manifest g020 zapisany")


if __name__ == "__main__":
    main()
