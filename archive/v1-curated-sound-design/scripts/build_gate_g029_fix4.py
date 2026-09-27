#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stal v4 do bramki g029 — „szczęk idealny, ale ciut ciszej i częściej”
(właściciel, 2026-09-25).

Baza: v3 (atomcut sword-clash, jasny ring 2–6 kHz, HP 220, zero LP).
Zmiany względem v3:
- poziom uderzeń: -40 ±1,5 → **-42 ±1,0** (ciut ciszej)
- gęstość: 5 → **9 starć** w zg.1 (co ~0,85 s) i 5 → **8** w zg.3 (co ~0,95 s)
- cała dziesiątka sword-clash-1…10 w rotacji (większa róż norodność przy
  częstszym rytmie), jitter czasowy ±0,12 s, ziarno 110.
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

rj = np.random.default_rng(110)

# rotacja stoczonych starć: kolejność do-szyta by sąsiady się różniły
PLAN_ZG1 = [4, 8, 6, 10, 2, 9, 5, 4, 7]   # start 0,65 s co 0,85 s
PLAN_ZG3 = [9, 10, 4, 6, 1, 9, 3, 8]      # start 0,55 s co 0,95 s


def bright_hit(idx: int) -> np.ndarray:
    w, _ = dsp.load_any(CLASH / f"sword-clash-{idx}.m4a")
    sos = butter(2, 220.0, btype="highpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, w, axis=-1)


def mix_steel4(base_name: str, plan: list[int], start: float, step: float,
               out_name: str) -> None:
    base, _ = dsp.load_any(CAND / base_name)
    t = base.copy()
    for i, idx in enumerate(plan):
        at = start + i * step + float(rj.uniform(-0.12, 0.12))
        hit = dsp.normalize_rms(bright_hit(idx), -42.0 + float(rj.uniform(-1.0, 1.0)))
        t = dsp.place(t, hit, at)
    t = dsp.fade(dsp.peak_ceiling(dsp.normalize_rms(dsp.peak_ceiling(t), -33.0)), 1.2, 1.5)
    dsp.encode_mp3(CAND / out_name, t)
    print(f"  {out_name} zapisany ({len(plan)} starć)")


def upsert_candidates() -> None:
    p = GATE / "manifest.json"
    m = json.loads(p.read_text("utf-8"))
    sw = {"title": "20 sword sound effects — attacks & clashes (OpenGameArt/CC0)",
          "author": "OpenGameArt artists (pack w atomcut-library)",
          "license": "CC0 1.0",
          "url": "https://github.com/novincode/atomcut-library",
          "channel": "git sparse-checkout /tmp/atomcut; skrypt build_gate_g029_fix4.py",
          "notes": "sword-clash-1…10 w rotacji (jasność 24–37% w 2–6 kHz); HP 220; "
                   "-42 ±1,0 dB; ziarno 110 (jitter ±0,12 s)"}
    for e in m["entries"]:
        if e["slug"] != "tlo-bitwa-zgielk":
            continue
        e["candidates"] = [c for c in e["candidates"] if c["label"] not in ("zg.1s", "zg.3s", "zg.1v3", "zg.3v3")]
        e["candidates"].append({
            "label": "zg.1v4", "title": "szarża + stal jasna (v4) — ciszej i częściej",
            "file": "candidates/zg1_szarza_stal4.mp3",
            "desc": "dostrojenie werdyktu właściciela („szczęk idealny, ciut ciszej i "
                    "częściej”): 9 starć mieczy co ~0,9 s, -42 ±1 dB; ring 2–6 kHz, "
                    "zero niskiego brzęku; rotacja wszystkich 10 clash-i",
            "source": {"base": "zg1_szarza.mp3", **sw},
        })
        e["candidates"].append({
            "label": "zg.3v4", "title": "przełamanie + stal jasna (v4) — ciszej i częściej",
            "file": "candidates/zg3_przełamanie_stal4.mp3",
            "desc": "ta sama strojenie na łóżku agonii: 8 starć co ~0,95 s, -42 ±1 dB; "
                    "ring przebija krzyki, nie nadpisuje ich",
            "source": {"base": "zg3_przełamanie.mp3", **sw},
        })
    m["note"] += " STAL v4: werdykt „szczęk idealny, ciut ciszej i częściej” → -42 ±1 dB, 9/8 starć, rotacja 1…10; v3 wycofane z decyzji (zatwierdzony materiał zostaje w archiwum)."
    p.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  manifest: zg.1v4 / zg.3v4 dodane, v3 wycofane z wyborów")


def main() -> None:
    mix_steel4("zg1_szarza.mp3", PLAN_ZG1, 0.65, 0.85, "zg1_szarza_stal4.mp3")
    mix_steel4("zg3_przełamanie.mp3", PLAN_ZG3, 0.55, 0.95, "zg3_przełamanie_stal4.mp3")
    upsert_candidates()


if __name__ == "__main__":
    main()
