#!/usr/bin/env python3
"""Probe a stem's loudness profile before using it in a recipe.

The original agent auditioned every recording and cut its loud segment by
hand (raven 7.75-9.2 s, grizzly 2.2-3.8 s, gravel 1.2-1.8 s, splash
3.2-4.6 s). The 3-5/15 batch skipped that step: recipes played the silent
heads of long field recordings, so events existed only in descriptions
(raven_call: -71..-55 dB for the first 4 s). render_jingle.py now rejects
such segments; this tool tells you where the good material is.

For every stem it prints: duration, spectral character (centroid, share of
energy <250 / 250-2k / 2-6k / >6 kHz - gravel_feet carries 36% above 6 kHz
= the "paper tearing" character), the RMS profile per 0.5 s window, and
the suggested offset_sec / length_sec for the recipe.

Requires the authoring venv: `pip install numpy soundfile`.

Usage:
  python scripts/stem_probe.py                      # all stems
  python scripts/stem_probe.py wolf_howl.mp3        # one stem
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STEMS = ROOT / "audio/library"  # domyślny katalog odniesienia dla ścieżek względnych
SR = 44_100


def load(name: str) -> np.ndarray:
    import soundfile as sf

    path = STEMS / name
    data, sr = sf.read(str(path))
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != SR:
        old = np.linspace(0.0, 1.0, len(data), endpoint=False)
        new = np.linspace(0.0, 1.0, int(len(data) * SR / sr), endpoint=False)
        data = np.interp(new, old, data)
    return data.astype(np.float64)


def windows_rms(data: np.ndarray, win_sec: float = 0.5, hop_sec: float = 0.25) -> list[tuple[float, float]]:
    win, hop = int(win_sec * SR), int(hop_sec * SR)
    out = []
    for i in range(0, max(1, len(data) - win + 1), hop):
        seg = data[i:i + win]
        out.append((i / SR, float(np.sqrt(np.mean(seg ** 2)) + 1e-12)))
    return out


def describe(name: str) -> None:
    data = load(name)
    dur = len(data) / SR
    spec = np.abs(np.fft.rfft(data)) ** 2
    freqs = np.fft.rfftfreq(len(data), 1.0 / SR)
    total = spec.sum() + 1e-12

    def band(lo: float, hi: float) -> float:
        m = (freqs >= lo) & (freqs < hi)
        return float(spec[m].sum() / total)

    centroid = float((freqs * spec).sum() / total)
    prof = windows_rms(data)
    loudest_t, loudest_rms = max(prof, key=lambda p: p[1])
    quiet_head = prof[0][1]

    chars = []
    if band(0, 250) > 0.7:
        chars.append("mroczne dno/mruk (<250 Hz)")
    if band(250, 2000) > 0.5:
        chars.append("czytelne średnie (250-2k)")
    if band(6000, 22050) > 0.2:
        chars.append("UWAGA: dużo >6 kHz — charakter papieru/syku")
    print(f"== {name}  ({dur:.1f} s) ==")
    print(f"   charakter: {'; '.join(chars) if chars else 'mieszany'} | centroid {centroid:.0f} Hz")
    print(f"   udziały: <250 Hz {100 * band(0, 250):.0f}% | 250-2k {100 * band(250, 2000):.0f}% | "
          f"2-6k {100 * band(2000, 6000):.0f}% | >6k {100 * band(6000, 22050):.0f}%")
    print("   profil RMS (co 0.25 s):")
    line = "   "
    for t, r in prof:
        db = 20 * np.log10(r)
        bar = "#" * max(0, int((db + 70) / 3))
        line += f"{t:4.1f}s {db:6.1f} {bar}\n   "
    print(line.rstrip())
    print(f"   → SUGESTIA: offset_sec ≈ {loudest_t:.1f} (najgłośniejsze okno {20 * np.log10(loudest_rms):.1f} dB; "
          f"głowa nagrania {20 * np.log10(quiet_head):.1f} dB)")
    if dur > 3.0:
        print("   → nagranie >3 s: receptura MUSI mieć offset_sec (i zwykle length_sec ≤ 1.5)")
    print()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stem", nargs="?", help="nazwa pliku np. wolf_howl.mp3 (domyślnie: wszystkie)")
    args = parser.parse_args()
    if args.stem:
        names = [args.stem]
    else:
        names = sorted(p.name for p in STEMS.glob("*.mp3"))
    for name in names:
        if not (STEMS / name).is_file():
            print(f"nie znaleziono: {STEMS / name}", file=sys.stderr)
            return 1
        describe(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
