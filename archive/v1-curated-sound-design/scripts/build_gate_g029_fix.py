#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplikacje właścicielskie poprawek do g029 (runda 3 fabuły 110):

- zg1_szarza_stal: zg.1 + „szczęk oręża” — 5 prawdziwych uderzeń metalu
  (486295 R27-37 Metal Clanks, CC0) w litterarowo przestrzennych, nieliniowych
  punktach (seed 110, jitter ±0,15 s / ±1,5 dB), LP 2400 / HP 180, −6 dB pod łóżkiem.
- zg3_przełamanie_stal: zg.3 + ta sama filaryka… 5 innych punktów okien.
- l1_wstrzask_odlotu_ciecie: ł.1 BEZ wzmocnionego ogona z ukrytym „strzałem”
  (w źródle -70 dB → po normie -34 wybuchał do 0,66 peak). Nowa wersja = sam
  odlot-chód 0,60–2,65 s, naturalny zanik.
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
CLANK4 = REPO / "legacy/source/sample_scout/freesound_battle-swords"
PIGEON = REPO / "legacy/source/sample_scout/freesound_pigeon-wings"


def sos_pass(wave: np.ndarray, kind: str, hz: float, order: int = 3) -> np.ndarray:
    sos = butter(order, hz, btype=kind, fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1)


def steel_hit(w_clank: np.ndarray, win_t: float, len_s: float = 0.55) -> np.ndarray:
    seg = dsp.cut(w_clank, win_t, win_t + len_s)
    seg = sos_pass(sos_pass(seg, "highpass", 180.0, order=2), "lowpass", 2400.0)
    return seg


HITS_ZG1 = [(2.85, 1.15), (5.50, 3.05), (8.80, 4.55), (16.70, 6.20), (23.20, 7.35)]
HITS_ZG3 = [(9.55, 0.95), (4.55, 2.55), (13.60, 3.90), (19.45, 5.60), (16.75, 7.10)]

rj = np.random.default_rng(110)


def mix_steel(base_name: str, hits: list[tuple[float, float]], out_name: str) -> np.ndarray:
    base, _ = dsp.load_any(CAND / base_name)
    w_clank, _ = dsp.load_any(next(CLANK4.glob("02-486295*")))
    t = base.copy()
    for win, at in hits:
        at_j = at + float(rj.uniform(-0.15, 0.15))
        gain_j = float(rj.uniform(-1.5, 1.5))
        hit = dsp.normalize_rms(steel_hit(w_clank, win), -40.5 + gain_j)
        t = dsp.place(t, hit, at_j)
    t = dsp.fade(dsp.peak_ceiling(dsp.normalize_rms(dsp.peak_ceiling(t), -33.0)), 1.2, 1.5)
    dsp.encode_mp3(CAND / out_name, t)
    return t


def main() -> None:
    print("buduję wersje z domieszaną stalą i uciętym l1…")
    mix_steel("zg1_szarza.mp3", HITS_ZG1, "zg1_szarza_stal.mp3")
    print("  zg1_szarza_stal zapisany (5 uderzeń, ziarno 110)")
    mix_steel("zg3_przełamanie.mp3", HITS_ZG3, "zg3_przełamanie_stal.mp3")
    print("  zg3_przełamanie_stal zapisany (5 uderzeń, ziarno 110)")

    # ł.1 cięty: sam odlot z źródła 689998 (0,60–2,65 s), bez wzmocnionego ogona
    f = next(PIGEON.glob("05-689998*"))
    w, _ = dsp.load_any(f)
    seg = sos_pass(dsp.cut(w, 0.60, 2.65), "highpass", 60.0, order=2)
    seg = dsp.fade(dsp.peak_ceiling(dsp.normalize_rms(seg, -19.0)), 0.15, 0.45)
    dsp.encode_mp3(CAND / "l1_wstrzask_odlotu_ciecie.mp3", seg)
    print("  l1_wstrzask_odlotu_ciecie zapisany (łuk 0,60–2,65 s, bez „strzału”)")


if __name__ == "__main__":
    main()
