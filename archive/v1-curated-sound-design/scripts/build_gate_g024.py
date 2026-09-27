#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g024 — instrumentacja `mroczna`, RUNDA 2 (po „żaden" w g023).

Diagnoza właściciela (g023, b.1): „najbliżej mi do organów, ale to nie brzmi
jak niskie tony, tylko wysokie; mroczny kojarzę z organami, ale chorusowymi".
Rodzina organów trafiona → zostajemy w organach, naprawiamy wykonanie:
  z.1  Renaissance FULL  — kilka rzędów na nutę = organowy „chorus" (piki 65 Hz,
                           46% < 250 Hz), wprost ze słowa właściciela;
  z.2  głośny pedał 16'  — ciężar fundamentu (65 Hz), prosto na „niskie tony";
  z.3  Renaissance 8'    — ciemny fleciasty głos (66–72% < 250 Hz, najciemniejszy).
Wszystkie demo grają w REALNYM niskim rejestrze (C2–C3), bez pitchowania.
VCSL, CC0. Etykieta z.* (unikatowa w skali bramek tego typu; b.* zużyta w g023).
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
from build_gate_g015 import VCSL_SRC  # noqa: E402

GATE = REPO / "data" / "gates" / "g024"
CAND = GATE / "candidates"
VCSL = Path("/tmp/vcsl")

NOTE_RE = re.compile(r"([A-G]#?)(\d)")
NOTE_OFF = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
            "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
MAX_MIDI = 51  # banki celowo tylko w strefie ciemnego dołu (C3 i niżej)


def midi_of(name: str) -> int | None:
    m = NOTE_RE.search(name)
    if not m:
        return None
    return NOTE_OFF[m.group(1)] + (int(m.group(2)) + 1) * 12


INSTR = {
    "b_renorgan_full": {
        "dir": VCSL / "Aerophones/Edge-blown Aerophones/Renaissance Organ/Full",
        "trim_sec": 5.0,
        "semantic": "pełny, wielorzędowy — organowy chorus, ciemny dołem",
        "family": "aerophone-organ", "title": "organy renesansowe — dyspozycja full",
        "desc": "pełna dyspozycja: kilka rzędów na jedną nutę — brzmi jak chór piszczałek; "
                "w dolnym rejestrze ciemna, posępna masa",
        "traits": ["ciemny", "wielogłosowy", "chorus", "pełny"],
        "bad_for": ["jasny", "solo", "lekki", "figlarny"],
        "notes": "RenOrgan_Full_Room, low bank C1–C3; demo C2–C3",
    },
    "b_organ_loudpedal": {
        "dir": VCSL / "Aerophones/Edge-blown Aerophones/Pipe Organ/Loud Pedal",
        "trim_sec": 8.0,
        "semantic": "ciężki 16-stopowy fundament — dudniące niskie tony",
        "family": "aerophone-organ", "title": "głośny pedał organowy 16'",
        "desc": "najniższa manualia organów w głośnej dyspozycji — ciężki, "
                "zamulony fundament, którego b.1 nie dał",
        "traits": ["ciemny", "bardzo niski", "dudniący", "ciężki"],
        "bad_for": ["jasny", "wysoki", "lekki", "staccato"],
        "notes": "Rode_Pedal (loud), low bank C1–D#3; demo C1–C2",
    },
    "b_renorgan_8": {
        "dir": VCSL / "Aerophones/Edge-blown Aerophones/Renaissance Organ/8'",
        "trim_sec": 6.0,
        "semantic": "ciemny, fleciasty, przygaszony — 66-72% energii < 250 Hz",
        "family": "aerophone-organ", "title": "organy renesansowe — głos 8'",
        "desc": "pojedynczy ciemny głos fletowy — przygaszony, głuchy, "
                "najbardziej szary z organowych kandydatów",
        "traits": ["ciemny", "fleciasty", "przygaszony", "głuchy"],
        "bad_for": ["jasny", "srebrzysty", "skowany", "figlarny"],
        "notes": "RenOrgan_8foot_Room, low bank C1–C3; demo C1–C2",
    },
}

# fraza demo per instrument — z NAJNIŻSZEJ oktawy banku, bo skarga g023
# dotyczyła braku niskich tonów (b.1 brzmiało za wysoko)
def demo_notes(midis: list[int]) -> dict:
    on_off = [(0.0, 1.2), (0.5, 1.5), (1.0, 1.8), (1.4, 3.2)]
    vels = [0.55, 0.52, 0.52, 0.56]
    return {"notes": [{"midi": m, "on": a, "off": b, "vel": v}
                      for m, (a, b), v in zip(midis, on_off, vels)]}

DEMOS = {
    "b_renorgan_full": demo_notes([24, 28, 32, 36]),   # C1 E1 G#1 C2
    "b_organ_loudpedal": demo_notes([24, 27, 33, 36]),  # C1 D#1 A1 C2
    "b_renorgan_8": demo_notes([24, 28, 32, 36]),        # C1 E1 G#1 C2
}


def probe_line(seg: np.ndarray) -> str:
    rms = dsp.rms_db(seg)
    peak = float(np.max(np.abs(seg)))
    return f"RMS {rms:.1f} dB, peak {20*np.log10(peak):.1f} dBFS"


def instr_cand(iid: str, label: str):
    spec = INSTR[iid]
    files: dict[int, Path] = {}
    for f in sorted(spec["dir"].glob("*.wav")):
        m = midi_of(f.name)
        if m is not None and m <= MAX_MIDI:
            files[m] = f
    assert len(files) >= 6, f"{iid}: za mało nut ({len(files)})"
    gate_sources = {}
    for m, f in sorted(files.items()):
        w, _ = dsp.load_any(f)
        w = w[:, : int(spec["trim_sec"] * dsp.SR)]
        w = dsp.fade(w, 0.005, 0.5)
        name = f"{iid}_{f.name.replace('.wav', '.mp3').replace('#', 's')}"
        out = GATE / "instr_notes" / name
        out.parent.mkdir(parents=True, exist_ok=True)
        dsp.encode_mp3(out, w)
        gate_sources[str(m)] = f"instr_notes/{name}"
    entry = {
        "id": iid, "semantic": spec["semantic"], "family": spec["family"],
        "samples": {m: f"audio/library/instruments/{iid.replace('b_', '')}/{Path(rel).name}"
                    for m, rel in gate_sources.items()},
        "gate_sources": gate_sources,
        "semantics": {"type": "mroczna", "traits": spec["traits"], "bad_for": spec["bad_for"]},
        "source": dict(VCSL_SRC, notes=f"{len(gate_sources)} nut (≤C3); trim {spec['trim_sec']} s; {spec['notes']}"),
    }
    inst_abs = {**entry, "samples": {m: str(GATE / rel) for m, rel in gate_sources.items()}}
    r = coda_synth.render_coda(DEMOS[iid], inst_abs, seed=222)
    dsp.encode_mp3(CAND / f"{iid}_demo.mp3", r.wave)
    print(f"  {label} {spec['title']:40s} {probe_line(r.wave)}  (nut: {len(gate_sources)}; "
          f"adaptacje: {[w for w in r.warnings if 'przeniesiona' in w or 'zastąpiona' in w]})")
    return {
        "label": label, "title": spec["title"], "file": f"candidates/{iid}_demo.mp3",
        "desc": spec["desc"], "source": "VCSL — CC0 (fraza demonstracyjna C2–C3, realny rejestr)",
        "entry": entry,
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    print("INSTRUMENTY (mroczna, runda 2 — organy ciemne/chorusowe, demo C2–C3):")
    cands = [instr_cand("b_renorgan_full", "z.1"),
             instr_cand("b_organ_loudpedal", "z.2"),
             instr_cand("b_renorgan_8", "z.3")]
    manifest = {
        "id": "g024", "created": "2026-09-24", "story_id": "222",
        "note": ("Runda 2 `mroczna` po odrzuceniu rundy 1 (g023). Diagnoza właściciela: rodzina "
                 "organów trafiona, ale wykonanie b.1 brzmiało za wysoko i za solo; "
                 "kierunek: organy ciemne i bardziej chorusowe. Kandydaci: pełna "
                 "dyspozycja renesansowa (chorus), głośny pedał 16' (niskie tony), "
                 "głos 8' (najciemniejszy flet). Fraza demo C2–C3 — realny dół. "
                 "Typ woła 90 fabuł; tło fabuły 222 już w bazie (sea_storm_02, g023)."),
        "entries": [
            {"slug": "instr-mroczna", "kind": "instruments",
             "role": "jedyny klocek typu instrumentacji `mroczna` (90 fabuł; slot b fabuły 222)",
             "candidates": cands},
        ],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for c in cands:
        p = GATE / c["file"]
        print(f"  {c['label']:6s} {p.stat().st_size/1024:5.0f} KB")
    print("manifest g024 zapisany")


if __name__ == "__main__":
    main()
