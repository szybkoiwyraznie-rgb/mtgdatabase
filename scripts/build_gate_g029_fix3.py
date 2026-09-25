#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stal v3 do bramki g029 — jasny ring miecza (wyrok właściciela z 2026-09-25:
„zamiast wysokich tonów szczęku miecz o miecz słychać niskie dudnienie,
jak uderzanie w kocioł”).

Diagnoza: (a) v2 cięło LP 2400 → drewno; (b) sam łupnięcia z paczki „Metal
Clanks and Hits” miały niski rezonans kociołkowy. Terapia: NOWA PALETA —
atomcut „20 sword sound effects — attacks & clashes” (CC0): prawdziwe
sword-clash-i z 24–37% energii w 2–6 kHz i ~0% poniżej 300 Hz (zmierzone).
Obróbka: HP 220 (zabija polexdrowisko), żadnego LP na górze — ring leci
naturalnie do 9–10 kHz. Poziom jak w v2 (-40 ±1,5, jitter ziarna 110).
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

GATE = REPO / "data" / "gates" / "g029"
CAND = GATE / "candidates"
CLASH = Path("/tmp/atomcut/packs/opengameart-20-sword-sound-effects-attacks-and-clashes/audio")

HITS_ZG1 = [("sword-clash-4.m4a", 1.15), ("sword-clash-6.m4a", 3.05), ("sword-clash-8.m4a", 4.55),
            ("sword-clash-9.m4a", 6.20), ("sword-clash-10.m4a", 7.35)]
HITS_ZG3 = [("sword-clash-9.m4a", 0.95), ("sword-clash-4.m4a", 2.55), ("sword-clash-10.m4a", 3.90),
            ("sword-clash-6.m4a", 5.60), ("sword-clash-8.m4a", 7.10)]

rj = np.random.default_rng(110)


def bright_hit(fname: str) -> np.ndarray:
    w, _ = dsp.load_any(CLASH / fname)
    sos = butter(2, 220.0, btype="highpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, w, axis=-1)


def mix_steel3(base_name: str, hits: list[tuple[str, float]], out_name: str) -> None:
    base, _ = dsp.load_any(CAND / base_name)
    t = base.copy()
    for fname, at in hits:
        at_j = at + float(rj.uniform(-0.15, 0.15))
        gain_j = float(rj.uniform(-1.5, 1.5))
        hit = dsp.normalize_rms(bright_hit(fname), -40.0 + gain_j)
        t = dsp.place(t, hit, at_j)
    t = dsp.fade(dsp.peak_ceiling(dsp.normalize_rms(dsp.peak_ceiling(t), -33.0)), 1.2, 1.5)
    dsp.encode_mp3(CAND / out_name, t)
    print(f"  {out_name} zapisany")


def upsert_candidates() -> None:
    p = GATE / "manifest.json"
    m = json.loads(p.read_text("utf-8"))
    sw = {"title": "20 sword sound effects — attacks & clashes (OpenGameArt/CC0)",
          "author": "OpenGameArt artists (pack w atomcut-library)",
          "license": "CC0 1.0",
          "url": "https://github.com/novincode/atomcut-library",
          "channel": "git sparse-checkout /tmp/atomcut; skrypt build_gate_g029_fix3.py",
          "notes": "5 starć sword-clash-4/6/8/9/10 (jasność 24–37% w 2–6 kHz); HP 220; "
                   "-40 ±1,5 dB; ziarno 110 (jitter ±0,15 s)"}
    for e in m["entries"]:
        if e["slug"] != "tlo-bitwa-zgielk":
            continue
        # usuń drewniane v2 z decyzji (archiwum trwalo w gate)
        e["candidates"] = [c for c in e["candidates"] if c["label"] not in ("zg.1s", "zg.3s")]
        e["candidates"].append({
            "label": "zg.1v3", "title": "szarża + stal jasna (v3) — miecz o miecz",
            "file": "candidates/zg1_szarza_stal3.mp3",
            "desc": "na prośbę właściciela: kocioł z v2 usunięty — teraz prawdziwe starcia "
                    "mieczy atomcut (ring 2–6 kHz, zero niskiego brzęku), 5 rozróżnionych "
                    "punktów 1,1 / 3,0 / 4,6 / 6,2 / 7,4 ± jitter; jasno, ale pod bedem",
            "source": {"base": "zg1_szarza.mp3", **sw},
        })
        e["candidates"].append({
            "label": "zg.3v3", "title": "przełamanie + stal jasna (v3) — miecz o miecz",
            "file": "candidates/zg3_przełamanie_stal3.mp3",
            "desc": "ta sama jasna paleta na łóżku agonii: 5 starć 0,9 / 2,6 / 3,9 / 5,6 / 7,1 "
                    "± jitter; ring miecza przebija krzyki, niski brzęk usunięty HP 220",
            "source": {"base": "zg3_przełamanie.mp3", **sw},
        })
    m["note"] += " STAL v3: nowa paleta atomcut sword-clash (jasny ring 2–6 kHz, HP 220, bez LP); v2 z kociołem wycofane z decyzji."
    p.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  manifest: zg.1v3 / zg.3v3 dodane, v2 wycofane z wyborów")


def main() -> None:
    mix_steel3("zg1_szarza.mp3", HITS_ZG1, "zg1_szarza_stal3.mp3")
    mix_steel3("zg3_przełamanie.mp3", HITS_ZG3, "zg3_przełamanie_stal3.mp3")
    upsert_candidates()


if __name__ == "__main__":
    main()
