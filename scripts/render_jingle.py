#!/usr/bin/env python3
"""Render a 5.5 s story jingle MP3 from a recipe JSON.

STATUS: authoring tool for agents, not used in CI. Dependencies (not part of
the system env): `pip install numpy soundfile lameenc`.

Recipe format (see data/recipes/*.json):

{
  "story_id": "568", "label": "v1", "duration_sec": 5.5,
  "genre": "sci-fi",
  "climax_window": [1.5, 3.8],
  "bed": {
    "ambience": {"type": "wind|station_hum|cave_water|terrace", "target_db": -30.0, "params": {...}},
    "drone":    {"type": "cinematic_sub|synth_pad|bowl", "freq": 44.0, "target_db": -27.0, "params": {...}}
  },
  "events": [
    {"time_sec": 2.0, "type": "synth", "kind": "swarm|crackle|sweep|chime|flutter|banish|thump|drip",
     "length_sec": 1.0, "gain": 1.0, "pan": 0.0, "role": "warstwa foley / kulminacja", "params": {...}},
    {"time_sec": 1.7, "type": "stem", "file": "impact_smack.mp3", "pitch": 1.0, "offset_sec": 0.0,
     "length_sec": 0.9, "hp_hz": 150, "target_db": -16.0, "pan": -0.2, "role": "warstwa foley"}
  ],
  "ducking": [1.8, 3.6, 0.45],
  "post": {"echo_ms": [140, 280], "echo_gains": [0.16, 0.09], "room": 0.5,
           "compressor": {"threshold_db": -16.0, "ratio": 3.5, "attack_ms": 12.0, "release_ms": 180.0}},
  "project_description": {"summary": "...", "ambience": "...", "drone": "...",
    "mix_notes": "...", "description": "..."}
}

The engine mirrors the legacy three-layer dramaturgy (ambience+drone bed,
foley events, center-panned stinger inside the climax window with ducking)
and emits QA metadata compatible with scripts/qa_score.py +
scripts/validate_versions.py. Used stems are read from
legacy/source/game-audio-pipeline/stems/.

v2 engine (2026-09-22, after the quality audit of the 3-5/15 batch):
- EVENTS MIX BY LOUDNESS, NOT BLIND PEAK*GAIN. Every event carries a target
  RMS (defaults: climax -16 dB, support -21 dB, detail -26 dB). The old
  peak-normalize-then-gain scheme rendered long field recordings at their
  silent heads (raven: first 4 s at -71..-55 dB), so "events" existed only
  in the description. Root cause of "nic z tego co opisujesz nie jest
  słyszalne" (issues for 8, 450, 475).
- SILENT-HEAD GATE: the used segment of a stem must sit within 12 dB of the
  stem's loudest 0.5 s window, otherwise the render is rejected with the
  suggested offset. Long stems (>3 s) additionally require an explicit
  offset_sec/length_sec plan.
- MODERATE PITCH-DOWN ALLOWED (owner decision 2026-09-22): 0.7 <= pitch
  <= 1.0. The owner-praised jingles pitched real recordings down (raven
  -12%, grizzly -25%, 568 v2 impact at 0.72) - pitch UP is what failed.
- COMPOUND EVENTS: several events may share a timestamp (the original
  agent's beast step = sub thump + gravel crunch + water splash at once).
- GLUE CHAIN mirroring the original ffmpeg post (aecho + acompressor +
  normalize 0.92): two-tap echo, feed-forward compressor, peak 0.90.
- HF TAMING: if the >6 kHz energy share exceeds 12% (paper/hiss character
  of the rejected batch - gravel_feet alone carries 36%), the top band is
  attenuated before mastering.
- QA v2 (scripts/qa_score.py): technical gates + per-event audibility
  (every described event >= +6 dB over the bed) + loudness + spectral
  balance. The old climax-ratio-only score rated the 3/15 renders 100/100.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import lameenc

ROOT = Path(__file__).resolve().parents[1]
STEMS = ROOT / "legacy/source/game-audio-pipeline/stems"
SR = 44_100
STORY_SECONDS_DEFAULT = 5.5

# Loudness doctrine (dBFS RMS over a segment's active part), calibrated on
# the owner-praised catalog (2.mp3 total RMS -15 dB, 4.mp3 -22 dB).
TARGET_CLIMAX_DB = -16.0
TARGET_SUPPORT_DB = -21.0
TARGET_DETAIL_DB = -26.0
TARGET_AMBIENCE_DB = -30.0
TARGET_DRONE_DB = -27.0

PITCH_MIN, PITCH_MAX = 0.7, 1.0  # down-only, owner decision 2026-09-22
HF_LIMIT = 0.12                  # max share of energy above 6 kHz
SILENT_HEAD_TOLERANCE_DB = 12.0  # used segment vs stem's loudest window


def validate_live_samples(recipe: dict) -> None:
    """Hard rules (AGENTS.md #14/#15 as amended 2026-09-22).

    Structural checks only (no audio deps -> CI-safe): genre declared,
    non-SF needs >=2 live stems with one in the climax window, SF needs >=1,
    pitch restricted to the down-only moderate range. Segment audibility
    (silent-head gate) is enforced at render time, when stems are loaded.
    """
    genre = str(recipe.get("genre", "")).strip().lower()
    if not genre:
        raise ValueError(
            "brak pola 'genre' w recepturze — od zasady żywych sampli "
            "(AGENTS.md #14) każda receptura deklaruje gatunek sceny, "
            "np. 'sci-fi', 'fantasy', 'nature', 'history'"
        )
    events = recipe.get("events", [])
    stems = [ev for ev in events if ev.get("type") == "stem" and str(ev.get("level", "")) != "bed"]
    for event in stems:
        pitch = event.get("pitch", 1.0)
        if pitch is not None and (float(pitch) < PITCH_MIN - 1e-6 or float(pitch) > PITCH_MAX + 1e-6):
            raise ValueError(
                f"stem '{event.get('file')}' ma pitch={pitch} — dozwolone jest wyłącznie "
                f"umiarkowane obniżanie {PITCH_MIN}-{PITCH_MAX} (decyzja właściciela; podbicie "
                "w górę niszczyło rozpoznawalność). Wybierz inny sample z biblioteki."
            )
    lo, hi = recipe.get("climax_window", [1.5, 3.8])
    if genre == "sci-fi":
        if not stems:
            raise ValueError(
                "scena sci-fi zwalnia minimum do jednego żywego samplu, ale "
                "co najmniej jedno zdarzenie musi być nagraniem (stem)"
            )
        return
    if len(stems) < 2:
        raise ValueError(
            f"scena nie-SF ('{genre}') wymaga co najmniej dwóch zdarzeń na "
            f"żywych samplach (stems); znaleziono {len(stems)} — bez żywych "
            "sampli projekt nie ma sensu (AGENTS.md #14)"
        )
    if not any(lo <= float(ev.get("time_sec", -1.0)) <= hi for ev in stems):
        raise ValueError(
            f"scena nie-SF ('{genre}') wymaga żywego samplu w oknie "
            f"kulminacji [{lo}, {hi}] — kulminacja nie może być syntetyczna"
        )


# --------------------------------------------------------------------------
# Filters: windowed-sinc FIR (no scipy needed), 2*half+1 taps, soft edges
# --------------------------------------------------------------------------
def apply_fir(x: np.ndarray, kind: str, f_lo: float, f_hi: float | None = None,
              half: int = 400, sr: int = SR) -> np.ndarray:
    n_fft = 1 << (len(x) + 2 * half - 1).bit_length()
    spec = np.fft.rfft(x, n_fft)
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    edge = 60.0
    if kind == "low":
        soft = np.clip(1.0 - (freqs - f_hi) / (2 * edge), 0.0, 1.0)
    elif kind == "high":
        soft = np.clip((freqs - f_lo) / (2 * edge) + 0.5, 0.0, 1.0)
    else:  # band
        center, width = (f_lo + f_hi) / 2, max((f_hi - f_lo) / 2, 1.0)
        soft = np.clip(1.0 - (np.abs(freqs - center) - width) / (2 * edge), 0.0, 1.0)
    if kind == "low":
        resp = np.zeros_like(freqs)
        resp[freqs <= f_hi] = 1.0
    elif kind == "high":
        resp = np.zeros_like(freqs)
        resp[freqs >= f_lo] = 1.0
    else:
        resp = np.zeros_like(freqs)
        resp[(freqs >= f_lo) & (freqs <= f_hi)] = 1.0
    spec *= resp * soft
    y = np.fft.irfft(spec, n_fft)[: len(x)]
    return y


def filter_signal(x: np.ndarray, kind: str, f_lo: float, f_hi: float | None = None) -> np.ndarray:
    if kind == "low" and (f_hi or f_lo) >= SR / 2 - 1:
        return x
    y = apply_fir(x, kind, f_lo, f_hi)
    return y


def resample_linear(x: np.ndarray, new_len: int) -> np.ndarray:
    if new_len == len(x):
        return x
    old_t = np.linspace(0.0, 1.0, len(x), endpoint=False)
    new_t = np.linspace(0.0, 1.0, new_len, endpoint=False)
    return np.interp(new_t, old_t, x).astype(np.float64)


# --------------------------------------------------------------------------
# Stem loading + audition (the fix for the silent-head failures)
# --------------------------------------------------------------------------
_STEM_CACHE: dict[str, dict] = {}


def stem_profile(name: str) -> dict:
    """Loudness profile of a stem: loudest 0.5 s window + per-0.5 s RMS.

    The rejected 3-5/15 batch played long field recordings from their silent
    heads (raven_call: -71 dB for the first 4 s). The renderer now refuses
    segments that sit more than SILENT_HEAD_TOLERANCE_DB under the stem's
    loudest window.
    """
    if name in _STEM_CACHE:
        return _STEM_CACHE[name]
    import soundfile as sf  # authoring-only dependency

    path = STEMS / name
    if not path.is_file():
        raise FileNotFoundError(f"stem not found: {path}")
    data, sr = sf.read(str(path))
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != SR:
        data = resample_linear(data, int(round(len(data) * SR / sr)))
    data = data.astype(np.float64)
    win = int(0.5 * SR)
    if len(data) <= win:
        windows = [float(np.sqrt(np.mean(data ** 2)) + 1e-12)]
    else:
        windows = [float(np.sqrt(np.mean(data[i:i + win] ** 2)) + 1e-12)
                   for i in range(0, len(data) - win + 1, win // 2)]
    loudest_idx = int(np.argmax(windows))
    profile = {
        "data": data,
        "dur": len(data) / SR,
        "windows": windows,
        "loudest_t": loudest_idx * 0.25,  # hop = 0.25 s
        "loudest_rms": max(windows),
    }
    _STEM_CACHE[name] = profile
    return profile


def load_stem(name: str, pitch: float = 1.0, offset_sec: float = 0.0) -> np.ndarray:
    data = stem_profile(name)["data"]
    if offset_sec > 0:
        data = data[int(offset_sec * SR):]
    if pitch != 1.0:
        data = resample_linear(data, max(8, int(len(data) / pitch)))
    return data


def active_rms(sig: np.ndarray) -> float:
    """RMS of the loudest 0.3 s window - the part the listener hears."""
    win = min(len(sig), int(0.3 * SR))
    if win <= 0:
        return 1e-12
    hop = max(1, win // 3)
    best = 0.0
    for i in range(0, max(1, len(sig) - win + 1), hop):
        best = max(best, float(np.mean(sig[i:i + win] ** 2)))
    return float(np.sqrt(best) + 1e-12)


def gate_silent_segment(name: str, seg: np.ndarray) -> None:
    """Reject a stem segment that plays a quiet head instead of the event."""
    profile = stem_profile(name)
    seg_rms = active_rms(seg)
    limit = profile["loudest_rms"] * (10 ** (-SILENT_HEAD_TOLERANCE_DB / 20.0))
    if seg_rms < limit:
        raise ValueError(
            f"stem '{name}': użyty fragment ma RMS {20 * np.log10(seg_rms):.1f} dB, "
            f"ponad {SILENT_HEAD_TOLERANCE_DB} dB pod najgłośniejszym okiem nagrania "
            f"({20 * np.log10(profile['loudest_rms']):.1f} dB @ ~{profile['loudest_t']:.1f} s) — "
            "to była przyczyna niewysłyszalnych zdarzeń z partii 3-5/15. "
            f"Ustaw offset_sec ~{profile['loudest_t']:.1f} (patrz scripts/stem_probe.py)."
        )


# --------------------------------------------------------------------------
# Synth layers
# --------------------------------------------------------------------------
def env_rise_fall(n: int, attack: float, release: float, sr: int = SR) -> np.ndarray:
    env = np.ones(n)
    a = max(1, int(attack * sr))
    r = max(1, int(release * sr))
    env[:a] = np.sin(0.5 * np.pi * np.linspace(0, 1, a)) ** 1.5
    env[-r:] *= np.cos(0.5 * np.pi * np.linspace(0, 1, r)) ** 1.5
    return env


def drone_layer(kind: str, freq: float, dur: float, gain: float, params: dict) -> tuple[np.ndarray, np.ndarray]:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    if kind == "cinematic_sub":
        sig = 0.5 * np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 1.5 * t)
        env = np.clip(t / 2.0, 0.2, 1.0)
        env[-int(0.9 * SR):] *= np.linspace(1.0, 0.0, int(0.9 * SR))
        sig = np.tanh(sig * env * 1.5) * 0.45
    elif kind == "synth_pad":
        f2 = freq * 1.5
        lfo = 0.06 * np.sin(2 * np.pi * 0.37 * t)
        sig = (0.55 * np.sin(2 * np.pi * freq * t) +
               0.30 * np.sin(2 * np.pi * (f2 + 2.0 * lfo) * t) +
               0.18 * np.sin(2 * np.pi * freq * 2.0 * t + 0.3))
        rng = np.random.default_rng(params.get("seed", 11))  # deterministic shimmer
        tre = rng.normal(0, 1, n)
        tre = filter_signal(tre, "band", 2400, 4800) * (0.05 + 0.05 * np.sin(2 * np.pi * 0.13 * t + 1.0))
        sig = sig + tre
        env = env_rise_fall(n, 0.9, 1.1)
        sig = np.tanh(sig * 1.1) * env * 0.42
    elif kind == "bowl":
        partials = params.get("partials", [freq, freq * 2.83, freq * 6.07])
        gains = params.get("gains", [1.0, 0.42, 0.22])
        decays = params.get("decays", [7.0, 4.0, 2.0])
        sig = np.zeros(n)
        for p, g, d in zip(partials, gains, decays):
            beat = 1.0 + 0.12 * np.sin(2 * np.pi * 0.8 * t + p * 0.01)
            sig += g * np.sin(2 * np.pi * (p + 0.4 * np.sin(2 * np.pi * 0.5 * t)) * t) * np.exp(-t / d) * beat
        sig = np.tanh(sig * 0.9) * (env_rise_fall(n, 0.06, 1.3) ** 0.5) * 0.34
    elif kind == "eldrazi_alien":
        # Dissonant alien drone, mirrors the legacy build_v2_scenes formula.
        sig = (0.35 * np.sin(2 * np.pi * freq * t) +
               0.25 * np.sin(2 * np.pi * (freq * 1.414) * t) +
               0.18 * np.sin(2 * np.pi * (freq * 2.828) * t + 0.6 * np.sin(2 * np.pi * 3.2 * t)))
        env = 0.35 + 0.45 * (1 - np.cos(np.pi * t / dur))
        sig = np.tanh(sig * env * 1.2) * 0.38
    else:
        raise ValueError(f"unknown drone kind: {kind}")
    sig *= gain
    return sig * 0.95, sig * 1.05


def ambience_layer(kind: str, dur: float, gain: float, params: dict) -> tuple[np.ndarray, np.ndarray]:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    rng = np.random.default_rng(params.get("seed", 7))
    noise = rng.normal(0, 1, n)
    if kind == "wind":
        sig = filter_signal(noise, "low", 0, 380)
        sig *= np.sin(np.pi * t / dur) ** 0.5
        return sig * gain * 0.8, sig * gain * 1.1
    if kind == "station_hum":
        hum = 0.18 * np.sin(2 * np.pi * 60 * t) + 0.10 * np.sin(2 * np.pi * 120 * t + 0.4)
        air = filter_signal(noise, "band", 500, 1500)
        lfo = 0.55 + 0.45 * np.sin(2 * np.pi * 0.09 * t + 0.7)
        fan = filter_signal(rng.normal(0, 1, n), "low", 0, 220) * lfo
        sig = hum + air * 0.30 + fan * 0.9
        return sig * gain * 0.95, sig * gain * 1.05
    if kind == "cave_water":
        sig = filter_signal(noise, "band", 70, 600) * 0.9
        return sig * gain * 0.8, sig * gain * 0.9
    if kind == "terrace":
        base = filter_signal(noise, "band", 300, 2400) * 0.6
        airy = filter_signal(rng.normal(0, 1, n), "high", 3500, None) * 0.15
        slow = 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t + 2.0)
        sig = (base + airy) * slow
        return sig * gain * 0.85, sig * gain * 1.0
    if kind == "forest_night":
        left = filter_signal(noise, "low", 0, 480) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * t))
        right = left * rng.uniform(0.9, 1.1)
        # Procedural crickets: short 4.2-4.5 kHz chirps in small clusters.
        for _ in range(int(params.get("crickets", 7))):
            start = rng.uniform(0.15, dur - 0.9)
            chirps = int(rng.integers(2, 5))
            pan_pos = float(rng.uniform(-0.55, 0.55))
            gL, gR = pan_gains(pan_pos)
            for j in range(chirps):
                s0 = int((start + j * rng.uniform(0.085, 0.12)) * SR)
                L0 = int(0.05 * SR)
                if s0 + L0 >= n:
                    continue
                tt = np.linspace(0, 0.05, L0, endpoint=False)
                f = float(rng.uniform(4100, 4500))
                chirp = np.sin(2 * np.pi * f * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 65 * tt)) * np.exp(-tt * 42)
                level = float(rng.uniform(0.05, 0.11))
                left[s0:s0 + L0] += chirp * level * gL
                right[s0:s0 + L0] += chirp * level * gR
        left += filter_signal(rng.normal(0, 1, n), "high", 5200, None) * 0.012
        right += filter_signal(rng.normal(0, 1, n), "high", 5200, None) * 0.014
        return left * gain, right * gain
    raise ValueError(f"unknown ambience kind: {kind}")


def synth_event(kind: str, dur: float, params: dict, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    if kind == "swarm":
        sig = np.zeros(n)
        n_grains = int(params.get("grains", 220))
        bloom_start = params.get("bloom", 0.0)
        for _ in range(n_grains):
            g_len = int(rng.uniform(0.025, 0.10) * SR)
            g_start = int(rng.uniform(0, max(1e-9, dur - g_len / SR)) * SR)
            frac = g_start / max(1, n)
            amp = min(1.0, frac / 0.35 + 0.08) * (1.0 - 0.55 * max(0.0, frac - 0.6))
            f = rng.uniform(1900, 5400)
            gt = np.linspace(0, g_len / SR, g_len, endpoint=False)
            grain = np.sin(2 * np.pi * (f + rng.uniform(-40, 40) * gt) * gt) * np.hanning(g_len)
            end = min(n, g_start + g_len)
            sig[g_start:end] += grain[: end - g_start] * amp
        sig = filter_signal(sig, "high", 1400, None)
        return np.tanh(sig * 0.6) * env_rise_fall(n, 0.25 + bloom_start, 0.5)
    if kind == "crackle":
        sig = np.zeros(n)
        for _ in range(int(params.get("bursts", 22))):
            b_len = int(rng.uniform(0.006, 0.02) * SR)
            b_start = int(rng.uniform(0, dur - b_len / SR) * SR)
            burst = rng.normal(0, 1, b_len) * np.exp(-np.linspace(0, 6, b_len))
            end = min(n, b_start + b_len)
            sig[b_start:end] += burst[: end - b_start] * rng.uniform(0.4, 1.0)
        sig = filter_signal(sig, "band", 900, 6500)
        return sig * env_rise_fall(n, 0.003, 0.1)
    if kind == "sweep":
        f1, f2 = params.get("f1", 140.0), params.get("f2", 920.0)
        k = np.log(f2 / f1) / dur
        phase = 2 * np.pi * f1 * (np.exp(k * t) - 1.0) / k
        sig = np.sin(phase) + 0.4 * np.sin(2.0 * phase)
        return np.tanh(sig * 1.4) * env_rise_fall(n, 0.35 * dur, 0.3 * dur) * 0.8
    if kind == "chime":
        partials = params.get("partials", [660, 990, 1320, 1980])
        decays = params.get("decays", [0.9, 0.7, 0.55, 0.4])
        sig = np.zeros(n)
        for i, (p, d) in enumerate(zip(partials, decays)):
            atk = np.minimum(1.0, t / 0.006) ** 0.5
            sig += (1.0 / (i + 1)) * np.sin(2 * np.pi * p * t) * np.exp(-t / d) * atk
        return np.tanh(sig * 0.9) * env_rise_fall(n, 0.005, 0.25)
    if kind == "flutter":
        sig = np.zeros(n)
        for _ in range(int(params.get("bursts", 6))):
            b_len = int(rng.uniform(0.03, 0.09) * SR)
            b_start = int(rng.uniform(0, dur - b_len / SR) * SR)
            burst = rng.normal(0, 1, b_len) * np.hanning(b_len)
            end = min(n, b_start + b_len)
            sig[b_start:end] += burst[: end - b_start] * rng.uniform(0.5, 1.0)
        return filter_signal(sig, "high", 2400, None) * env_rise_fall(n, 0.02, 0.15) * 2.2
    if kind == "banish":
        f1, f2 = params.get("f1", 980.0), params.get("f2", 80.0)
        k = np.log(f2 / f1) / (dur * 0.5)
        tt = np.minimum(t, dur * 0.5)
        phase = 2 * np.pi * f1 * (np.exp(k * tt) - 1.0) / k
        down = np.sin(phase) * np.exp(-t * 5.5)
        sub_f1, sub_f2 = 72.0, 26.0
        ks = np.log(sub_f2 / sub_f1) / dur
        sub = np.sin(2 * np.pi * sub_f1 * (np.exp(ks * t) - 1.0) / ks) * np.exp(-t * 3.2)
        snap = np.where(t < 0.012, np.sin(2 * np.pi * 2100 * t) * np.exp(-t * 280), 0.0)
        sig = down * 0.9 + sub * 1.1 + snap * 0.7
        return np.tanh(sig * 1.5) * env_rise_fall(n, 0.002, 0.45) * 0.95
    if kind == "thump":
        freq = np.linspace(params.get("f1", 80.0), params.get("f2", 28.0), n)
        sig = np.sin(2 * np.pi * freq * t) * np.exp(-t / max(0.05, dur * 0.35))
        return np.tanh(sig * 1.6) * 0.85
    if kind == "drip":
        # Falling cave drip: fast pitch glide 2.3k->0.9k with sharp exponential decay.
        f1, f2 = params.get("f1", 2300.0), params.get("f2", 900.0)
        k = np.log(f2 / f1) / max(1e-6, dur)
        phase = 2 * np.pi * f1 * (np.exp(k * t) - 1.0) / k
        return np.sin(phase) * np.exp(-t * 42) * (0.75 + 0.25 * np.sin(2 * np.pi * 300 * t))
    raise ValueError(f"unknown synth kind: {kind}")


# --------------------------------------------------------------------------
# Mix engine
# --------------------------------------------------------------------------
def pan_gains(pan: float) -> tuple[float, float]:
    return (0.95 - 0.25 * pan), (0.95 + 0.25 * pan)


def db_to_amp(db: float) -> float:
    return float(10.0 ** (db / 20.0))


def normalize_rms(sig: np.ndarray, target_db: float, floor_db: float = -70.0) -> np.ndarray:
    rms = active_rms(sig)
    if 20 * np.log10(rms) < floor_db:
        raise ValueError(f"segment zbyt cichy ({20 * np.log10(rms):.1f} dB) do normalizacji")
    return sig * (db_to_amp(target_db) / rms)


def event_target_db(ev: dict, climax_window: tuple[float, float]) -> float:
    if "target_db" in ev:
        return float(ev["target_db"])
    lo, hi = climax_window
    in_climax = lo <= float(ev.get("time_sec", -1)) <= hi
    if in_climax and ev.get("type") == "stem":
        return TARGET_CLIMAX_DB
    if ev.get("type") == "stem":
        return TARGET_SUPPORT_DB
    return TARGET_DETAIL_DB


def fade_edges(sig: np.ndarray, ms: float = 6.0) -> np.ndarray:
    n = min(len(sig), int(ms / 1000.0 * SR))
    if n > 0 and len(sig) > 2 * n:
        ramp = np.linspace(0.0, 1.0, n)
        sig[:n] *= ramp
        sig[-n:] *= ramp[::-1]
    return sig


def hf_share(mix: np.ndarray) -> float:
    mono = mix.mean(axis=1) if mix.ndim > 1 else mix
    spec = np.abs(np.fft.rfft(mono)) ** 2
    freqs = np.fft.rfftfreq(len(mono), 1.0 / SR)
    return float(spec[freqs >= 6000].sum() / (spec.sum() + 1e-12))


def tame_hf(mix: np.ndarray) -> np.ndarray:
    """Attenuate the >6.5 kHz band when the mix turns papery/hissy.

    Applies the same zero-phase spectral scale to both channels via a
    per-sample gain derived from the mono signal (stable, no image smear).
    """
    mono = mix.mean(axis=1) if mix.ndim > 1 else mix
    spec = np.abs(np.fft.rfft(mono))
    freqs = np.fft.rfftfreq(len(mono), 1.0 / SR)
    spec[freqs >= 6500] *= 10 ** (-9.0 / 20.0)  # -9 dB on the top band
    shaped = np.fft.irfft(spec, len(mono))
    gain = shaped / (mono + 1e-9)
    gain = np.clip(gain, 0.0, 1.0)
    if mix.ndim > 1:
        return mix * gain[:, None]
    return mix * gain


def compress(mix: np.ndarray, threshold_db: float = -16.0, ratio: float = 3.5,
             attack_ms: float = 12.0, release_ms: float = 180.0) -> np.ndarray:
    """Feed-forward compressor (glue), mirroring the legacy acompressor
    chain that made the original v1-v5 catalog dense and loud."""
    mono = mix.max(axis=1) if mix.ndim > 1 else mix
    win = max(1, int(0.02 * SR))
    kernel = np.ones(win) / win
    env = np.sqrt(np.convolve(mono ** 2, kernel, mode="same") + 1e-12)
    env_db = 20 * np.log10(env + 1e-12)
    over = np.clip(env_db - threshold_db, 0.0, None)
    gain_db = -(1.0 - 1.0 / ratio) * over
    # smooth gain movement (attack/release averaged)
    sm = max(1, int(release_ms / 1000.0 * SR / 4))
    gain = 10 ** (np.convolve(gain_db, np.ones(sm) / sm, mode="same") / 20.0)
    makeup = db_to_amp((1.0 - 1.0 / ratio) * 6.0)  # modest auto-makeup
    return mix * gain[:, None] * makeup if mix.ndim > 1 else mix * gain * makeup


def render(recipe: dict) -> tuple[np.ndarray, dict]:
    dur = float(recipe.get("duration_sec", STORY_SECONDS_DEFAULT))
    n = int(dur * SR)
    climax_window = tuple(recipe.get("climax_window", [1.5, 3.8]))
    L = np.zeros(n)
    R = np.zeros(n)

    bed = recipe.get("bed", {})
    bedL = np.zeros(n)
    bedR = np.zeros(n)
    if bed.get("ambience"):
        amb = bed["ambience"]
        aL, aR = ambience_layer(amb["type"], dur, float(amb.get("gain", 0.3)), amb.get("params", {}))
        target = float(amb.get("target_db", TARGET_AMBIENCE_DB))
        ref = np.sqrt(np.mean((aL + aR) ** 2) / 2) + 1e-12
        scale = db_to_amp(target) / ref
        bedL += aL * scale
        bedR += aR * scale
    if bed.get("drone"):
        dr = bed["drone"]
        dL, dR = drone_layer(dr["type"], float(dr.get("freq", 44.0)), dur, float(dr.get("gain", 0.4)), dr.get("params", {}))
        target = float(dr.get("target_db", TARGET_DRONE_DB))
        ref = np.sqrt(np.mean((dL + dR) ** 2) / 2) + 1e-12
        scale = db_to_amp(target) / ref
        bedL += dL * scale
        bedR += dR * scale

    # ducking mask for the bed during the stinger window
    duck = np.ones(n)
    if recipe.get("ducking"):
        d0, d1, depth = recipe["ducking"]
        i0, i1 = int(d0 * SR), int(d1 * SR)
        ramp = int(0.18 * SR)
        duck[i0:i1] = depth
        duck[i0 - ramp:i0] = np.linspace(1.0, depth, ramp)
        duck[i1:i1 + ramp] = np.linspace(depth, 1.0, ramp)
    L += bedL * duck
    R += bedR * duck

    qa_events = []
    for idx, ev in enumerate(recipe.get("events", [])):
        pan = float(ev.get("pan", 0.0))
        gL, gR = pan_gains(pan)
        if ev["type"] == "stem":
            sig = load_stem(ev["file"], pitch=float(ev.get("pitch", 1.0)), offset_sec=float(ev.get("offset_sec", 0.0)))
            if ev.get("length_sec"):
                sig = sig[: int(float(ev["length_sec"]) * SR)]
            else:
                sig = sig[: int(1.6 * SR)]  # never let a long tail bury the scene
            gate_silent_segment(ev["file"], sig)
            sig = fade_edges(sig)
            if ev.get("hp_hz"):
                sig = filter_signal(sig, "high", float(ev["hp_hz"]), None)
            sig = normalize_rms(sig, event_target_db(ev, climax_window))
        elif ev["type"] == "synth":
            sig = synth_event(ev["kind"], float(ev.get("length_sec", 1.0)), ev.get("params", {}), seed=1000 + idx)
            sig = normalize_rms(sig, event_target_db(ev, climax_window))
        else:
            raise ValueError(f"unknown event type: {ev['type']}")
        start = int(float(ev["time_sec"]) * SR)
        end = min(n, start + len(sig))
        if end <= start:
            continue
        seg = sig[: end - start]
        L[start:end] += seg * gL
        R[start:end] += seg * gR
        qa_events.append({
            "time_sec": float(ev["time_sec"]),
            "sample": ev.get("file") or f"synth:{ev.get('kind')}",
            "role": ev.get("role", "warstwa foley"),
            "level": str(ev.get("level", "event")),
        })

    mix = np.column_stack([L, R])

    post = recipe.get("post", {})
    echo_ms = post.get("echo_ms", [])
    echo_gains = post.get("echo_gains", [])
    room = float(post.get("room", 0.4))
    if echo_ms:
        wet = np.zeros_like(mix)
        for ms, g in zip(echo_ms, echo_gains):
            shift = int(ms / 1000.0 * SR)
            if shift < len(mix):
                wet[shift:] += mix[:-shift] * g
        mix = mix + wet * room

    # spectral taming (paper/hiss guard), glue compressor, master normalize
    if hf_share(mix) > HF_LIMIT:
        mix = tame_hf(mix)
    comp = post.get("compressor", {})
    if comp is not None:
        mix = compress(mix,
                       threshold_db=float(comp.get("threshold_db", -16.0)),
                       ratio=float(comp.get("ratio", 3.5)),
                       attack_ms=float(comp.get("attack_ms", 12.0)),
                       release_ms=float(comp.get("release_ms", 180.0)))
    mix = np.tanh(mix * 1.05)
    dc = mix.mean(axis=0)
    mix = mix - dc  # kill any DC component before encoding
    peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / peak * 0.90  # legacy catalog loudness (0.92 ffmpeg master)
    return mix, {"events": qa_events, "climax_window": climax_window}


def qa_audit_file(out_path: Path, climax_window: tuple[float, float],
                  events: list | None = None) -> dict:
    """Audit the actual encoded MP3 (post-encode), not the pre-encode mix.

    QA v2: technical gates (DC, peak, continuity) + loudness + spectral
    balance + per-event audibility (every described event >= +6 dB over the
    bed; the old score rated the 3/15 batch 100/100 because a lone click
    over silence maxed the climax ratio).
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_audio import analyze

    report = analyze(out_path, climax_window, events=events)
    return report


def encode_mp3(mix: np.ndarray, out_path: Path, bitrate: int = 128) -> None:
    pcm = (np.clip(mix, -1.0, 1.0) * 32767.0).astype(np.int16)
    enc = lameenc.Encoder()
    enc.set_bit_rate(bitrate)
    enc.set_in_sample_rate(SR)
    enc.set_channels(2)
    enc.set_quality(2)
    data = enc.encode(pcm.tobytes()) + enc.flush()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--min-score", type=float, default=85.0,
                        help="minimum QA score to accept the render (default 85)")
    parser.add_argument("--print-description", action="store_true",
                        help="print project_description JSON for data/versions.json")
    args = parser.parse_args()

    recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
    try:
        validate_live_samples(recipe)
    except ValueError as error:
        print(f"  ! Receptura odrzucona: {error}", file=sys.stderr)
        return 1
    try:
        mix, qa_meta = render(recipe)
    except ValueError as error:
        print(f"  ! Render przerwany: {error}", file=sys.stderr)
        return 1
    encode_mp3(mix, args.out)
    qa = qa_audit_file(args.out, qa_meta["climax_window"], events=qa_meta["events"])
    print(f"Rendered {args.out} ({args.out.stat().st_size} B); QA {qa['score']}/100 [{qa['status']}], "
          f"climax ratio {qa.get('climax_ratio', 0)}x", file=sys.stderr)
    # Self-correction gate (legacy quality doctrine): a render below the
    # minimum score must not be registered as metadata; fix the recipe and
    # re-render instead of shipping it.
    passed = str(qa["status"]).startswith("pass") and qa["score"] >= args.min_score
    if not passed:
        # A rejected render must not linger on disk pretending to be accepted.
        if args.out.exists():
            args.out.unlink()
        for line in qa["details"]:
            print(f"  ! {line}", file=sys.stderr)
        print(f"  ! QA {qa['score']} poniżej progu {args.min_score} — popraw recepturę i renderuj ponownie.", file=sys.stderr)
        return 1
    if args.print_description:
        desc = dict(recipe.get("project_description", {}))
        desc["genre"] = str(recipe.get("genre", "")).strip().lower()
        desc["events"] = qa_meta["events"]
        desc["qa"] = {k: qa[k] for k in ("score", "base", "dramaturgy", "status", "details") if k in qa}
        print(json.dumps(desc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
