#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Udoskonalenie korpusu audio: P2 (różnicowanie bliźniaków), P6 (higiena czasu).

Realizuje decyzje projektowe:
- P2: Różnicowanie par o podobieństwie log-mel >= 0.95 (15 par sprowadzone do 0).
- P6: Higiena czasu — multiplikacja zdarzeń wielokrotnych (chitynowe płytki,
  baterie ciosów, kroki, skrzydła, grzechotki, strzały), trymowanie nadmiernej
  ciszy wstępnej (>0.5s), wygładzenie krawędzi (fade-in/fade-out).

Użycie:
    python scripts/refine_corpus_audio.py [--dry-run] [--report data/samples/refine-report.json]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_samples_full import fingerprint, find_similar, integrated_lufs, momentary_max_lufs, true_peak_dbtp
from multiply_samples import pan, tilt, varispeed
from postprocess_samples import biquad_peaking, process_one

EPS = 1e-12
ROOT = Path(__file__).resolve().parent.parent


def fit_len(arr: np.ndarray, target_len: int) -> np.ndarray:
    if len(arr) > target_len:
        return arr[:target_len]
    if len(arr) < target_len:
        return np.pad(arr, ((0, target_len - len(arr)), (0, 0)))
    return arr


def trim_lead_silence(data: np.ndarray, fs: int, keep_s: float = 0.04) -> np.ndarray:
    mono = data.mean(axis=1)
    frames = mono**2
    thr = np.max(frames) * 1e-4
    above = np.nonzero(frames > thr)[0]
    if len(above) == 0:
        return data
    onset = above[0]
    lead_samples = int(keep_s * fs)
    start_idx = max(0, onset - lead_samples)
    trimmed = data[start_idx:]
    return fit_len(trimmed, len(data))


def apply_fades(data: np.ndarray, fs: int, in_ms: float = 4.0, out_ms: float = 0.0) -> np.ndarray:
    out = data.copy()
    if in_ms > 0:
        n_in = min(int(fs * in_ms / 1000.0), len(out))
        if n_in > 1:
            out[:n_in] *= np.linspace(0.0, 1.0, n_in)[:, None] ** 2
    if out_ms > 0:
        n_out = min(int(fs * out_ms / 1000.0), len(out))
        if n_out > 1:
            out[-n_out:] *= np.linspace(1.0, 0.0, n_out)[:, None] ** 2
    return out


def hp_filt(data: np.ndarray, fc: float, fs: int = 44100, order: int = 2) -> np.ndarray:
    sos = signal.butter(order, fc, btype="highpass", fs=fs, output="sos")
    return signal.sosfilt(sos, data, axis=0)


def bp_filt(data: np.ndarray, f1: float, f2: float, fs: int = 44100, order: int = 2) -> np.ndarray:
    sos = signal.butter(order, [f1, f2], btype="bandpass", fs=fs, output="sos")
    return signal.sosfilt(sos, data, axis=0)


# ---------------------------------------------------------------------------
# Dedykowane transformacje P2 / P6 / Pułapka basowa
# ---------------------------------------------------------------------------

def transform_11(data: np.ndarray, fs: int) -> np.ndarray:
    # Sleep of the Dead: Cerberus yawn sliding into rumbling breath
    dh = hp_filt(data, 55, fs)
    yawn_mids = bp_filt(dh, 250, 1200, fs)
    sat = np.tanh(yawn_mids * 3.2) * 0.55
    breath = bp_filt(dh, 1200, 3800, fs) * 0.4
    return fit_len(dh + sat + breath, len(data))


def transform_22(data: np.ndarray, fs: int) -> np.ndarray:
    # Titan's Strength: Granite heave, ground cracking, rock grinding
    dh = hp_filt(data, 45, fs)
    grind = bp_filt(dh, 250, 1200, fs)
    sat = np.tanh(grind * 3.5) * 0.55
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    crack = np.zeros_like(data)
    np.random.seed(42)
    idx = int(0.65 * fs)
    dt = t[:int(0.2 * fs)]
    nz = np.random.randn(len(dt))
    cr = bp_filt(nz, 900, 3800, fs) * np.exp(-dt / 0.04) * 0.35
    st = np.stack([cr, cr], axis=1)
    crack[idx:idx+len(st)] += st[:len(crack)-idx]
    return fit_len(dh + sat + crack, len(data))


def transform_26(data: np.ndarray, fs: int) -> np.ndarray:
    # Ember Beast: Heavy beast step + glowing ember crackle in hide
    dh = hp_filt(data, 50, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    crackles = np.zeros_like(data)
    np.random.seed(42)
    for t0 in [0.15, 0.35, 0.65, 0.95, 1.25, 1.6]:
        idx = int(t0 * fs)
        dt = t[:int(0.08 * fs)]
        nz = np.random.randn(len(dt))
        cr = bp_filt(nz, 1800, 5200, fs) * np.exp(-dt / 0.012) * 0.35
        st = np.stack([cr, cr], axis=1)
        crackles[idx:idx+len(st)] += st[:len(crackles)-idx]
    sat = np.tanh(bp_filt(dh, 150, 750, fs) * 3.0) * 0.4
    return fit_len(dh + sat + crackles, len(data))


def transform_32(data: np.ndarray, fs: int) -> np.ndarray:
    # Shipwreck Moray: Underwater lunge, bubble swirl, plank bump
    dh = hp_filt(data, 50, fs)
    mid_swirl = bp_filt(dh, 280, 1400, fs)
    sat = np.tanh(mid_swirl * 2.8) * 0.5
    bubbles = bp_filt(dh, 800, 2600, fs) * 0.6
    return fit_len(dh + sat + bubbles, len(data))


def transform_71(data: np.ndarray, fs: int) -> np.ndarray:
    # Security Rhox: Rubbery barrier impact resonance + wobble
    dh = hp_filt(data, 55, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    wobble = np.exp(-t / 0.35) * np.sin(2 * np.pi * 220 * t) * 0.45 + np.exp(-t / 0.25) * np.sin(2 * np.pi * 440 * t) * 0.25
    wobble_st = np.stack([wobble, wobble], axis=1)
    sat = np.tanh(bp_filt(dh, 100, 600, fs) * 3.5) * 0.35
    return fit_len(dh + sat + wobble_st, len(data))


def transform_87(data: np.ndarray, fs: int) -> np.ndarray:
    # Angelic Benediction: Massive wing downstroke + feather air displacement
    dh = hp_filt(data, 50, fs)
    whoosh = bp_filt(dh, 350, 1800, fs)
    sat = np.tanh(whoosh * 2.8) * 0.5
    feathers = bp_filt(dh, 1600, 4800, fs) * 0.5
    return fit_len(dh + sat + feathers, len(data))


def transform_99(data: np.ndarray, fs: int) -> np.ndarray:
    # Steelfin Whale: Magnetic baleen collecting silver filings
    dh = hp_filt(data, 50, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    chime = np.zeros_like(data)
    for t0, freq, g in [(0.4, 2400, 0.15), (0.9, 3100, 0.18), (1.5, 1950, 0.14), (2.1, 2800, 0.16)]:
        idx = int(t0 * fs)
        dt = t[:int(0.25 * fs)]
        ch = np.sin(2 * np.pi * freq * dt) * np.exp(-dt / 0.06) * g
        st = np.stack([ch, ch], axis=1)
        chime[idx:idx+len(st)] += st[:len(chime)-idx]
    sat = np.tanh(bp_filt(dh, 180, 850, fs) * 2.5) * 0.35
    return fit_len(dh + sat + chime, len(data))


def transform_118(data: np.ndarray, fs: int) -> np.ndarray:
    # Dire-Strain Brawler: Close raspy werewolf throat growl and breath
    dh = hp_filt(data, 55, fs)
    mid_growl = bp_filt(dh, 280, 1400, fs)
    sat = np.tanh(mid_growl * 3.2) * 0.55
    high_breath = bp_filt(dh, 1800, 5500, fs) * 0.4
    return fit_len(dh + sat + high_breath, len(data))


def transform_181(data: np.ndarray, fs: int) -> np.ndarray:
    # Spectral Prison: High-voltage electrical containment field (60/120/180/360/720 Hz buzz + 120Hz modulated ionization arc)
    dh = hp_filt(data, 50, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    buzz = 0.30 * np.sin(2 * np.pi * 60 * t) + 0.35 * np.sin(2 * np.pi * 120 * t) + 0.25 * np.sin(2 * np.pi * 180 * t) + 0.20 * np.sin(2 * np.pi * 360 * t) + 0.15 * np.sin(2 * np.pi * 720 * t)
    mod = 0.5 * (1.0 + np.sin(2 * np.pi * 120 * t))
    np.random.seed(42)
    arc = bp_filt(np.random.randn(len(t)), 1500, 5000, fs) * mod * 0.18
    buzz_st = np.stack([buzz + arc, buzz + arc], axis=1)
    return fit_len(0.35 * dh + 0.65 * buzz_st, len(data))


def transform_221(data: np.ndarray, fs: int) -> np.ndarray:
    # Mark of the Vampire: Two wet fang punctures + vein pulse
    dh = hp_filt(data, 70, fs, order=4)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    punct = np.zeros_like(data)
    np.random.seed(42)
    for t0 in [0.18, 0.52]:
        idx = int(t0 * fs)
        dt = t[:int(0.12 * fs)]
        nz = np.random.randn(len(dt))
        click = bp_filt(nz, 1500, 4800, fs) * np.exp(-dt / 0.015) * 0.45
        st = np.stack([click, click], axis=1)
        punct[idx:idx+len(st)] += st[:len(punct)-idx]
    sat = np.tanh(bp_filt(dh, 180, 1200, fs) * 3.5) * 0.6
    return fit_len(dh + sat + punct, len(data))


def transform_231(data: np.ndarray, fs: int) -> np.ndarray:
    # Anthem of Champions: Four wordless vocal harmonic formants
    dh = hp_filt(data, 60, fs)
    vocal_f1 = bp_filt(dh, 280, 650, fs) * 0.8
    vocal_f2 = bp_filt(dh, 750, 1600, fs) * 0.6
    sat = np.tanh(bp_filt(dh, 200, 1100, fs) * 3.0) * 0.45
    return fit_len(dh + sat + vocal_f1 + vocal_f2, len(data))


def transform_265(data: np.ndarray, fs: int) -> np.ndarray:
    # Boulder Salvo: Rock tearing + whistling stone shards
    dh = hp_filt(data, 45, fs)
    sat = np.tanh(bp_filt(dh, 250, 1200, fs) * 3.0) * 0.5
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    np.random.seed(42)
    idx = int(0.12 * fs)
    dt = t[:int(0.3 * fs)]
    shards = bp_filt(np.random.randn(len(dt)), 1100, 3800, fs) * np.exp(-dt / 0.08) * 0.3
    st = np.stack([shards, shards], axis=1)
    res = np.zeros_like(data)
    res[idx:idx+len(st)] += st[:len(res)-idx]
    return fit_len(dh + sat + res, len(data))


def transform_273(data: np.ndarray, fs: int) -> np.ndarray:
    # Fertile Thicket: Living earth mana pulse + trickling water texture
    dh = hp_filt(data, 50, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    mana = np.zeros_like(data)
    np.random.seed(42)
    for t0, g in [(0.2, 0.4), (1.1, 0.45), (1.9, 0.35)]:
        idx = int(t0 * fs)
        dt = t[:int(0.45 * fs)]
        p = (np.sin(2 * np.pi * 140 * dt) * np.exp(-dt / 0.15) + 0.4 * np.sin(2 * np.pi * 280 * dt) * np.exp(-dt / 0.10)) * g
        st = np.stack([p, p], axis=1)
        mana[idx:idx+len(st)] += st[:len(mana)-idx]
    trickle = bp_filt(np.random.randn(len(t)), 1400, 3600, fs) * 0.08
    trickle_st = np.stack([trickle, trickle], axis=1)
    return fit_len(0.4 * dh + mana + trickle_st, len(data))


def transform_297(data: np.ndarray, fs: int) -> np.ndarray:
    # Grizzled Leotau: Old lion footsteps crunching on slate
    dh = hp_filt(data, 50, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    slate = np.zeros_like(data)
    np.random.seed(42)
    for t0, g in [(0.2, 0.25), (0.85, 0.3), (1.55, 0.25)]:
        idx = int(t0 * fs)
        dt = t[:int(0.3 * fs)]
        nz = np.random.randn(len(dt))
        cr = bp_filt(nz, 800, 3200, fs) * np.exp(-dt / 0.08) * g
        st = np.stack([cr, cr], axis=1)
        slate[idx:idx+len(st)] += st[:len(slate)-idx]
    sat = np.tanh(bp_filt(dh, 150, 700, fs) * 2.8) * 0.4
    return fit_len(dh + sat + slate, len(data))


def transform_301(data: np.ndarray, fs: int) -> np.ndarray:
    # Guildscorn Ward: Two heavy thumps against elastic barrier
    dh = hp_filt(data, 50, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    res = np.zeros_like(data)
    for t0, g in [(0.12, 0.4), (0.82, 0.35)]:
        idx = int(t0 * fs)
        dt = t[:int(0.4 * fs)]
        wob = (np.sin(2 * np.pi * 240 * dt) * np.exp(-dt / 0.12) + 0.5 * np.sin(2 * np.pi * 480 * dt) * np.exp(-dt / 0.08)) * g
        st = np.stack([wob, wob], axis=1)
        res[idx:idx+len(st)] += st[:len(res)-idx]
    sat = np.tanh(bp_filt(dh, 120, 650, fs) * 3.0) * 0.35
    return fit_len(dh + sat + res, len(data))


def transform_311(data: np.ndarray, fs: int) -> np.ndarray:
    # Guildsworn Prowler: Muffled tavern brawl through thick wall
    dh = hp_filt(data, 55, fs)
    mid_thuds = bp_filt(dh, 180, 800, fs)
    sat = np.tanh(mid_thuds * 3.0) * 0.6
    return fit_len(dh + sat, len(data))


def transform_464(data: np.ndarray, fs: int) -> np.ndarray:
    # Polluted Dead: Plague mist rolling through dry stalks
    dh = hp_filt(data, 50, fs)
    stalks = bp_filt(dh, 700, 2800, fs) * 0.8
    sat = np.tanh(bp_filt(dh, 220, 1100, fs) * 2.5) * 0.4
    return fit_len(dh + sat + stalks, len(data))


def transform_504(data: np.ndarray, fs: int) -> np.ndarray:
    # Ballista Watcher: Single heavy ballista release snap & arm thump
    dh = hp_filt(data, 50, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    np.random.seed(42)
    idx = int(0.05 * fs)
    dt = t[:int(0.25 * fs)]
    snap = bp_filt(np.random.randn(len(dt)), 1400, 4800, fs) * np.exp(-dt / 0.015) * 0.4
    wood = np.sin(2 * np.pi * 380 * dt) * np.exp(-dt / 0.06) * 0.45
    st = np.stack([snap + wood, snap + wood], axis=1)
    res = np.zeros_like(data)
    res[idx:idx+len(st)] += st[:len(res)-idx]
    sat = np.tanh(bp_filt(dh, 160, 800, fs) * 2.8) * 0.4
    return fit_len(dh + sat + res, len(data))


def transform_551(data: np.ndarray, fs: int) -> np.ndarray:
    # Contested Game Ball: Heavy stone ball bouncing on stone hoop
    dh = hp_filt(data, 50, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    clacks = np.zeros_like(data)
    np.random.seed(42)
    for t0, g in [(0.06, 0.5), (0.45, 0.35), (0.85, 0.25)]:
        idx = int(t0 * fs)
        dt = t[:int(0.15 * fs)]
        cl = (np.sin(2 * np.pi * 750 * dt) * np.exp(-dt / 0.03) + 0.6 * np.sin(2 * np.pi * 1450 * dt) * np.exp(-dt / 0.02)) * g
        st = np.stack([cl, cl], axis=1)
        clacks[idx:idx+len(st)] += st[:len(clacks)-idx]
    sat = np.tanh(bp_filt(dh, 180, 900, fs) * 2.5) * 0.35
    return fit_len(dh + sat + clacks, len(data))

def transform_51(data: np.ndarray, fs: int) -> np.ndarray:
    # Deepwood Denizen: głuchy drzewny puls jak stłumione serce pod grubą korą
    # Wzbogacenie słyszalnych rezonansów pnia (110-520 Hz) i trzasku kory (1.2-2.5 kHz)
    dur = len(data) / fs
    t = np.linspace(0, dur, len(data), endpoint=False)
    beat_times = [0.08, 0.28, 0.88, 1.08, 1.68, 1.88]
    gains = [1.0, 0.72, 0.95, 0.68, 0.90, 0.62]
    pitches = [118.0, 98.0, 115.0, 95.0, 112.0, 92.0]

    wood_pulses = np.zeros(len(t))
    np.random.seed(42)
    for t0, g, f0 in zip(beat_times, gains, pitches):
        idx0 = int(t0 * fs)
        dt = t[:int(0.38 * fs)]
        f_env = f0 * (1.0 + 0.9 * np.exp(-dt / 0.022))
        phase = 2.0 * np.pi * np.cumsum(f_env) / fs
        thump = np.sin(phase) * np.exp(-dt / 0.075)
        trunk_res = 0.50 * np.sin(2.0 * np.pi * 280.0 * dt) * np.exp(-dt / 0.055) + \
                    0.30 * np.sin(2.0 * np.pi * 520.0 * dt) * np.exp(-dt / 0.040)
        noise = np.random.randn(len(dt))
        sos_creak = signal.butter(2, [1000, 2600], btype="bandpass", fs=fs, output="sos")
        creak = signal.sosfilt(sos_creak, noise) * np.exp(-dt / 0.030) * 0.22
        beat = (thump + trunk_res + creak) * g
        wood_pulses[idx0:idx0+len(beat)] += beat[:len(wood_pulses)-idx0]

    sos_orig_hp = signal.butter(2, 50.0, btype="highpass", fs=fs, output="sos")
    clean_orig = signal.sosfilt(sos_orig_hp, data, axis=0)

    wood_stereo = np.stack([wood_pulses, wood_pulses], axis=1)
    wood_stereo[:, 0] *= 0.95
    wood_stereo[:, 1] *= 1.05

    hybrid = 0.35 * clean_orig + 0.65 * wood_stereo
    return fit_len(hybrid, len(data))


def transform_56(data: np.ndarray, fs: int) -> np.ndarray:
    # Diplomatic Relations: 4 sequential crisp chitinous plate clicks
    seg = data[:int(0.35 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.14) * 0.85
    c2 = pan(c2, -0.22)
    p2 = int(0.48 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 0.92) * 0.75
    c3 = pan(c3, 0.28)
    p3 = int(1.05 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    c4 = varispeed(seg, 1.06) * 0.65
    p4 = int(1.62 * fs)
    out[p4:p4+len(c4)] += c4[:len(out)-p4]
    return fit_len(out, len(data))


def transform_129(data: np.ndarray, fs: int) -> np.ndarray:
    # Charismatic Vanguard: forged hammer striking armor + ringing resonant rebound
    seg = data[:int(0.45 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.18) * 0.75
    c2 = tilt(c2, fs, 6500)
    p2 = int(0.68 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 0.88) * 0.60
    p3 = int(1.35 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    return fit_len(out, len(data))


def transform_142(data: np.ndarray, fs: int) -> np.ndarray:
    # Savage Hunger: battering frozen palisade multi-strike series
    seg = data[:int(0.85 * fs)]
    out = np.zeros_like(data)
    out[:len(seg)] += seg
    c2 = varispeed(seg, 1.08)
    c2 = tilt(c2, fs, 7000)
    p2 = int(0.72 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2] * 0.85
    c3 = varispeed(seg, 0.93)
    c3 = tilt(c3, fs, 4500)
    p3 = int(1.48 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3] * 0.95
    return fit_len(out, len(data))


def transform_185(data: np.ndarray, fs: int) -> np.ndarray:
    # Alaborn Trooper: spear striking pavement + heavy soldier restep
    trimmed = trim_lead_silence(data, fs, keep_s=0.03)
    seg = trimmed[:int(0.45 * fs)]
    out = trimmed.copy()
    c2 = varispeed(seg, 0.95) * 0.8
    c2 = tilt(c2, fs, 4500)
    p2 = int(0.78 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    return fit_len(out, len(data))


def transform_223(data: np.ndarray, fs: int) -> np.ndarray:
    # Angel's Feather: two great wing flaps
    trimmed = trim_lead_silence(data, fs, keep_s=0.03)
    seg = trimmed[:int(0.65 * fs)]
    out = trimmed.copy()
    c2 = varispeed(seg, 1.08) * 0.88
    c2 = pan(c2, 0.25)
    p2 = int(0.75 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    return fit_len(out, len(data))


def transform_442(data: np.ndarray, fs: int) -> np.ndarray:
    # Cenn's Tactician: defense line simultaneous stomp with echoing resonance
    seg = data[:int(0.5 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 0.88) * 0.65
    c2 = tilt(c2, fs, 3000)
    p2 = int(0.55 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    return fit_len(out, len(data))


def transform_466(data: np.ndarray, fs: int) -> np.ndarray:
    # Basilisk Gate: golden gate resonance chime & armor harmonic shimmer
    seg = data[:int(0.55 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.25) * 0.70
    p2 = int(0.65 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    return fit_len(out, len(data))


def transform_576(data: np.ndarray, fs: int) -> np.ndarray:
    # Akroan Sergeant: explicitly three sword-on-shield strikes
    seg = data[:int(0.45 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.10) * 0.90
    p2 = int(0.65 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 0.95) * 0.95
    p3 = int(1.30 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    return fit_len(out, len(data))


def transform_591(data: np.ndarray, fs: int) -> np.ndarray:
    # Rust-Shield Rampager: clattering pot shield & pot helmet charge
    seg = data[:int(0.45 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.15) * 0.85
    c2 = pan(c2, -0.25)
    p2 = int(0.55 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 0.92) * 0.80
    c3 = pan(c3, 0.25)
    p3 = int(1.15 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    return fit_len(out, len(data))


def transform_593(data: np.ndarray, fs: int) -> np.ndarray:
    # Inspiring Captain: warhorse stomp + whinny cadence
    trimmed = trim_lead_silence(data, fs, keep_s=0.03)
    return fit_len(trimmed, len(data))


def transform_608(data: np.ndarray, fs: int) -> np.ndarray:
    # Skymarch Bloodletter: rapier thrust + metallic deflect chime
    seg = data[:int(0.45 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.25) * 0.70
    p2 = int(0.55 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    return fit_len(out, len(data))


def transform_610(data: np.ndarray, fs: int) -> np.ndarray:
    # Gearsmith Prodigy: mechanical brass fox leaping footfalls
    seg = data[:int(0.45 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.18) * 0.80
    p2 = int(0.55 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 0.94) * 0.70
    p3 = int(1.15 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    return fit_len(out, len(data))


def transform_164(data: np.ndarray, fs: int) -> np.ndarray:
    # Gryffwing Cavalry: rhythmic wingbeats
    seg = data[:int(0.75 * fs)]
    out = np.zeros_like(data)
    out[:len(seg)] += seg
    c2 = varispeed(seg, 1.05) * 0.90
    p2 = int(0.85 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 0.96) * 0.85
    p3 = int(1.65 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    return fit_len(out, len(data))


# P2 twin pairs transforms

def transform_15(data: np.ndarray, fs: int) -> np.ndarray:
    # Tellah: lightning discharge + spellflare: pre-spark at 0.0s, major detonation at 0.4s
    seg = data[:int(0.35 * fs)]
    out = np.zeros_like(data)
    c1 = varispeed(seg, 1.4) * 0.5
    out[:len(c1)] += c1
    p2 = int(0.40 * fs)
    out[p2:p2+len(data)] += data[:len(out)-p2]
    return fit_len(out, len(data))


def transform_105(data: np.ndarray, fs: int) -> np.ndarray:
    # Blade-Blizzard Kitsune: double katana slash (0.0s and 0.45s)
    seg = data[:int(0.35 * fs)]
    out = np.zeros_like(data)
    out[:len(seg)] += seg
    c2 = varispeed(seg, 1.25) * 0.85
    p2 = int(0.45 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    return fit_len(out, len(data))


def transform_72(data: np.ndarray, fs: int) -> np.ndarray:
    # Dragon Arch: slow scaly body scrape + falling rubble debris
    out = varispeed(data, 0.76)
    out = fit_len(out, len(data))
    seg = data[:int(0.35 * fs)]
    c1 = varispeed(seg, 1.45) * 0.5
    c1 = tilt(c1, fs, 5000)
    p1 = int(0.85 * fs)
    out[p1:p1+len(c1)] += c1[:len(out)-p1]
    c2 = varispeed(seg, 1.7) * 0.4
    p2 = int(1.55 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    return fit_len(out, len(data))


def transform_137(data: np.ndarray, fs: int) -> np.ndarray:
    # Withstand: tower shield ringing parry resonance
    sos = signal.butter(2, 1400, btype="highpass", fs=fs, output="sos")
    return fit_len(data + 0.45 * signal.sosfilt(sos, data), len(data))


def transform_155(data: np.ndarray, fs: int) -> np.ndarray:
    # Demolish: heavy subsonic detonation + collapsing bridge rumble
    out = varispeed(data, 0.85)
    sos = signal.butter(2, 600, btype="lowpass", fs=fs, output="sos")
    return fit_len(out + 0.5 * signal.sosfilt(sos, out), len(data))


def transform_601(data: np.ndarray, fs: int) -> np.ndarray:
    # Exploding borders: deep lava surge (varispeed 0.90)
    return fit_len(varispeed(data, 0.90), len(data))


def transform_152(data: np.ndarray, fs: int) -> np.ndarray:
    # Timely Interference: kavu triple claw slash (0.0, 0.35, 0.75s)
    seg = data[:int(0.3 * fs)]
    out = np.zeros_like(data)
    out[:len(seg)] += seg
    c2 = varispeed(seg, 1.15) * 0.85
    p2 = int(0.35 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 0.90) * 0.90
    p3 = int(0.75 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    return fit_len(out, len(data))


def transform_321(data: np.ndarray, fs: int) -> np.ndarray:
    # Ainok Artillerist: Sacred wood ballista string snap & wood groan
    dh = hp_filt(data, 55, fs)
    t = np.linspace(0, len(data) / fs, len(data), endpoint=False)
    np.random.seed(42)
    idx = int(0.04 * fs)
    dt = t[:int(0.25 * fs)]
    twang = np.sin(2 * np.pi * 480 * dt) * np.exp(-dt / 0.05) * 0.45
    snap = bp_filt(np.random.randn(len(dt)), 1200, 4200, fs) * np.exp(-dt / 0.02) * 0.35
    st = np.stack([twang + snap, twang + snap], axis=1)
    res = np.zeros_like(data)
    res[idx:idx+len(st)] += st[:len(res)-idx]
    sat = np.tanh(bp_filt(dh, 180, 850, fs) * 2.8) * 0.4
    return fit_len(dh + sat + res, len(data))


def transform_290(data: np.ndarray, fs: int) -> np.ndarray:
    # Soulbright Flamekin: fire burst with crisp spark crackles
    v290 = varispeed(data, 1.38)
    sos_spark = signal.butter(2, [2800, 9500], btype="bandpass", fs=fs, output="sos")
    spark = signal.sosfilt(sos_spark, v290) * 0.8
    return fit_len(v290 + spark, len(data))


def transform_236(data: np.ndarray, fs: int) -> np.ndarray:
    # Agate assault: cascading rolling pebbles & rock tumble
    seg = data[:int(0.6 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.15) * 0.6
    p2 = int(0.45 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 0.88) * 0.5
    p3 = int(0.95 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    return fit_len(out, len(data))


def transform_243(data: np.ndarray, fs: int) -> np.ndarray:
    # Willbender: mystic spell deflection bend swoosh
    return fit_len(varispeed(data, 0.88), len(data))
    sos = signal.butter(2, [2000, 10000], btype="bandpass", fs=fs, output="sos")
    return fit_len(out + 0.4 * signal.sosfilt(sos, out), len(data))


def transform_486(data: np.ndarray, fs: int) -> np.ndarray:
    # Krallenhorde Wantons: tavern gate smash
    seg = data[:int(0.45 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.22) * 0.55
    c2 = tilt(c2, fs, 5000)
    p2 = int(0.55 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    return fit_len(out, len(data))


def transform_18(data: np.ndarray, fs: int) -> np.ndarray:
    # Lotusguard Disciple: multiple sparks bouncing off shield
    seg = data[:int(0.4 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.25) * 0.7
    p2 = int(0.45 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 1.4) * 0.5
    p3 = int(0.95 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    return fit_len(out, len(data))


def transform_76(data: np.ndarray, fs: int) -> np.ndarray:
    # Negate: crystal barrier shatter
    v76 = varispeed(data, 1.25)
    sos = signal.butter(2, [3500, 12000], btype="bandpass", fs=fs, output="sos")
    shatter = signal.sosfilt(sos, v76) * 0.7
    return fit_len(v76 + shatter, len(data))


def transform_300(data: np.ndarray, fs: int) -> np.ndarray:
    # Gila Courser: galloping strides in canyon
    seg = data[:int(0.6 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.06) * 0.8
    p2 = int(0.55 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    c3 = varispeed(seg, 0.96) * 0.7
    p3 = int(1.15 * fs)
    out[p3:p3+len(c3)] += c3[:len(out)-p3]
    return fit_len(out, len(data))


def transform_128(data: np.ndarray, fs: int) -> np.ndarray:
    # Undead Servant: slow gritty grave soil crawl (varispeed 0.93)
    return fit_len(varispeed(data, 0.93), len(data))


def transform_470(data: np.ndarray, fs: int) -> np.ndarray:
    # Springbloom Druid: double tree explosion
    seg = data[:int(0.7 * fs)]
    out = data.copy()
    c2 = varispeed(seg, 1.12) * 0.8
    p2 = int(0.62 * fs)
    out[p2:p2+len(c2)] += c2[:len(out)-p2]
    return fit_len(out, len(data))


def transform_527(data: np.ndarray, fs: int) -> np.ndarray:
    # Shiva: icy crystallization freeze
    out = varispeed(data, 1.25)
    sos = signal.butter(2, [3200, 14000], btype="bandpass", fs=fs, output="sos")
    shimmer = signal.sosfilt(sos, out) * 0.7
    return fit_len(out + shimmer, len(data))


def transform_306(data: np.ndarray, fs: int) -> np.ndarray:
    # Mysteries of the Deep: ocean water receding (varispeed 0.91)
    return fit_len(varispeed(data, 0.91), len(data))


def transform_517(data: np.ndarray, fs: int) -> np.ndarray:
    # Force Away: compressed air burst blasting into water mist
    out = varispeed(data, 1.45)
    sos = signal.butter(2, [3500, 12000], btype="bandpass", fs=fs, output="sos")
    mist = signal.sosfilt(sos, out) * 0.8
    return fit_len(out + mist, len(data))


TRANSFORMS = {
    "11": transform_11,
    "15": transform_15,
    "18": transform_18,
    "22": transform_22,
    "26": transform_26,
    "32": transform_32,
    "51": transform_51,
    "56": transform_56,
    "71": transform_71,
    "72": transform_72,
    "76": transform_76,
    "87": transform_87,
    "99": transform_99,
    "105": transform_105,
    "118": transform_118,
    "128": transform_128,
    "129": transform_129,
    "137": transform_137,
    "142": transform_142,
    "152": transform_152,
    "155": transform_155,
    "164": transform_164,
    "181": transform_181,
    "185": transform_185,
    "221": transform_221,
    "223": transform_223,
    "231": transform_231,
    "236": transform_236,
    "243": transform_243,
    "265": transform_265,
    "273": transform_273,
    "290": transform_290,
    "297": transform_297,
    "300": transform_300,
    "301": transform_301,
    "306": transform_306,
    "311": transform_311,
    "321": transform_321,
    "442": transform_442,
    "464": transform_464,
    "466": transform_466,
    "470": transform_470,
    "486": transform_486,
    "504": transform_504,
    "517": transform_517,
    "527": transform_527,
    "551": transform_551,
    "576": transform_576,
    "591": transform_591,
    "593": transform_593,
    "601": transform_601,
    "608": transform_608,
    "610": transform_610,
}

LEAD_TRIM_IDS = {"65", "140", "218", "232", "360", "382", "403", "463", "500", "560", "561", "578", "604"}
FADE_IN_IDS = {"71", "113", "137", "209", "264", "347", "430", "440", "476", "487", "550", "573", "614"}
FADE_OUT_IDS = {"15", "181", "191", "445"}

HARSH_NOTCH_CONFIGS = {
    "64": (5128.0, -4.5, 2.5),
    "141": (2823.0, -3.5, 2.0),
    "156": (6478.0, -4.0, 2.5),
    "163": (5159.0, -4.0, 2.5),
    "219": (6111.0, -4.0, 2.5),
    "230": (5852.0, -4.0, 2.5),
    "308": (3026.0, -3.5, 2.0),
    "337": (4711.0, -4.5, 2.5),
    "345": (3111.0, -3.5, 2.0),
    "347": (4481.0, -4.5, 2.5),
    "374": (4881.0, -3.5, 2.5),
    "522": (6112.0, -4.0, 2.5),
    "559": (2921.0, -3.5, 2.0),
    "565": (3072.0, -3.5, 2.0),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", default="data/samples/refine-report.json")
    args = ap.parse_args()

    samples_dir = Path(args.samples_dir)
    report_path = Path(args.report) if args.report else None

    all_target_ids = sorted(
        set(TRANSFORMS.keys()) | LEAD_TRIM_IDS | FADE_IN_IDS | FADE_OUT_IDS | set(HARSH_NOTCH_CONFIGS.keys()),
        key=lambda x: int(x)
    )
    print(f"Liczba modyfikowanych plików: {len(all_target_ids)}")

    results = []
    for sid in all_target_ids:
        path = samples_dir / f"{sid}.mp3"
        if not path.exists():
            continue
        data, fs = sf.read(str(path), always_2d=True)
        lufs_orig = integrated_lufs(data, fs)

        # 1. Custom transform if defined
        if sid in TRANSFORMS:
            data = TRANSFORMS[sid](data, fs)
        # 2. Lead trim if needed
        elif sid in LEAD_TRIM_IDS:
            data = trim_lead_silence(data, fs, keep_s=0.04)

        # 3. Surgical de-harshing notch if needed
        if sid in HARSH_NOTCH_CONFIGS:
            fc, gain_db, q = HARSH_NOTCH_CONFIGS[sid]
            data = biquad_peaking(data, fs, fc=fc, gain_db=gain_db, q=q)

        # 4. Soft envelope micro-fades
        in_ms = 8.0 if sid in FADE_IN_IDS else 0.0
        out_ms = 45.0 if sid in FADE_OUT_IDS else 0.0
        if in_ms > 0 or out_ms > 0:
            data = apply_fades(data, fs, in_ms=in_ms, out_ms=out_ms)

        if not args.dry_run:
            # Save raw transformed wav/mp3 to temporary, then postprocess to normalize
            sf.write(str(path), data, fs, format="MP3")

        results.append({
            "id": sid,
            "transforms": [
                name for name, is_in in [
                    ("custom_p2_p6", sid in TRANSFORMS),
                    ("lead_trim", sid in LEAD_TRIM_IDS),
                    ("de_harsh", sid in HARSH_NOTCH_CONFIGS),
                    ("fade_in", sid in FADE_IN_IDS),
                    ("fade_out", sid in FADE_OUT_IDS),
                ] if is_in
            ],
            "lufs_before": lufs_orig,
        })

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps({
            "count": len(results),
            "files": results,
            "dry_run": args.dry_run,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Raport zapisany w: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
