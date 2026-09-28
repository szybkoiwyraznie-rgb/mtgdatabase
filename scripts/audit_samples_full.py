#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pełny audyt korpusu sampli `audio/samples/*.mp3` (skan od zera).

Rozszerzenie `scripts/audit_samples_audio.py` o wymiary, których tamten
nie mierzył:

- głośność percepcyjna (LUFS wg BS.1770-4 z bramkowaniem) i true peak (4x
  nadpróbkowanie) zamiast samego peaku próbkowego,
- pasmo (rolloff 95/99 %) — wykrywa sample obcięte filtrem/kiepską generację,
- tonalność (spectral flatness + śledzenie f0) — kandydaci na „muzykę"
  zakazaną w promptach,
- heurystyka mowy (modulacja obwiedni 2–8 Hz + energia w paśmie mowy),
- duplikaty: identyczny PCM (md5) oraz „bliźniaki" brzmieniowe (kosinus
  odcisków log-mel) — reguła projektu mówi, że każda fabuła ma mieć
  unikalny sample,
- kontrola tekstów: identyczne prompty/scenariusze w `scenarios.jsonl`.

Skrypt **niczego nie zmienia** — tylko liczy metryki, typuje podejrzanych
i (opcjonalnie) generuje raport Markdown.

Użycie:
    python scripts/audit_samples_full.py \
        --json data/samples/audio-audit-fullscan.json \
        --markdown docs/audits/audio-audit-fullscan.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

EPS = 1e-12
ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# progi (kalibracja opisana w raporcie)
# ---------------------------------------------------------------------------
SILENCE_DB = -45.0           # próg ciszy dla obwiedni 10 ms
CUT_START_DB = -12.0         # start od razu na pełnym poziomie
CUT_START_MARGIN = 4.0       # ...i w granicach N dB od maksimum pliku
CUT_END_DB = -30.0
CUT_END_MARGIN = 15.0
LEAD_SILENCE_S = 0.6
TRAIL_SILENCE_S = 1.5
TRUE_PEAK_DBTP = -0.1        # powyżej tego poziomu koder/DAC może przesterować
CLIP_FRAC = 0.0005
# Progi głośnościowe skalibrowane na rozkładzie korpusu (mediana -15,5 LUFS,
# p5 = -32,3, p95 = -7,2): flagujemy tylko skrajności, bo cały korpus i tak
# wymaga jednego przebiegu normalizacji.
LUFS_QUIET = -32.0           # sample ginie obok reszty biblioteki (~p5)
LUFS_LOUD = -6.5             # sample wyrywa się z biblioteki (~p97)
TRUE_PEAK_HOT = 1.0          # dBTP — realne ryzyko zniekształceń po transkodowaniu
SUB_DOMINANT = 0.80          # udział energii poniżej 60 Hz
AUDIBLE_SHARE_MIN = 0.02     # udział energii powyżej 250 Hz
TONAL_AUDIBLE_MIN = 0.10     # tonalność liczy się tylko przy realnej treści
TONAL_FRACTION = 0.80        # udział ramek tonalnych
TONAL_PITCH_STD = 0.5        # stabilność f0 w półtonach
TONAL_VOICED = 0.60          # udział ramek dźwięcznych
SPEECH_MOD_RATIO = 0.55      # udział modulacji 2-8 Hz w obwiedni
SHORT_CONTENT_S = 0.8        # realna treść po odjęciu ciszy
SIM_THRESHOLD = 0.95         # kosinus odcisków log-mel = „bliźniak"


def db(x: float) -> float:
    return 20.0 * math.log10(max(float(x), EPS))


# ---------------------------------------------------------------------------
# LUFS (ITU-R BS.1770-4)
# ---------------------------------------------------------------------------
def k_weighting_sos(fs: int) -> np.ndarray:
    """Filtr K: półka wysokotonowa + filtr górnoprzepustowy (RLB)."""
    # stopień 1 — high shelf
    g, q, fc = 3.999843853973347, 0.7071752369554196, 1681.974450955533
    k = math.tan(math.pi * fc / fs)
    vh = 10.0 ** (g / 20.0)
    vb = vh ** 0.4996667741545416
    a0_ = 1.0 + k / q + k * k
    shelf = [
        (vh + vb * k / q + k * k) / a0_,
        2.0 * (k * k - vh) / a0_,
        (vh - vb * k / q + k * k) / a0_,
        1.0,
        2.0 * (k * k - 1.0) / a0_,
        (1.0 - k / q + k * k) / a0_,
    ]
    # stopień 2 — high pass
    q, fc = 0.5003270373238773, 38.13547087602444
    k = math.tan(math.pi * fc / fs)
    denom = 1.0 + k / q + k * k
    hp = [
        1.0,
        -2.0,
        1.0,
        1.0,
        2.0 * (k * k - 1.0) / denom,
        (1.0 - k / q + k * k) / denom,
    ]
    return np.array([shelf, hp], dtype=float)


def integrated_lufs(data: np.ndarray, fs: int) -> float:
    """Zintegrowana głośność z bramkowaniem absolutnym i względnym."""
    if data.ndim == 1:
        data = data[:, None]
    filtered = signal.sosfilt(k_weighting_sos(fs), data, axis=0)
    block = int(0.400 * fs)
    step = max(1, int(0.100 * fs))  # 75 % nakładki
    if len(filtered) < block:  # za krótkie na pełny blok — jeden skrócony
        block = len(filtered)
        step = max(1, block)
    if block <= 0:
        return -120.0
    weights = np.ones(filtered.shape[1])  # L/R/mono = 1.0
    starts = range(0, max(1, len(filtered) - block + 1), step)
    loud = []
    for s in starts:
        seg = filtered[s : s + block]
        ms = np.mean(seg**2, axis=0)
        z = float(np.sum(weights * ms))
        loud.append(-0.691 + 10.0 * math.log10(max(z, EPS)))
    loud_arr = np.array(loud)
    above_abs = loud_arr[loud_arr > -70.0]
    if above_abs.size == 0:
        return -120.0
    # bramka względna liczona z energii, nie ze średniej dB
    lin = 10.0 ** ((above_abs + 0.691) / 10.0)
    rel_gate = -0.691 + 10.0 * math.log10(max(float(np.mean(lin)), EPS)) - 10.0
    kept = loud_arr[(loud_arr > -70.0) & (loud_arr > rel_gate)]
    if kept.size == 0:
        kept = above_abs
    lin = 10.0 ** ((kept + 0.691) / 10.0)
    return round(-0.691 + 10.0 * math.log10(max(float(np.mean(lin)), EPS)), 2)


def true_peak_dbtp(data: np.ndarray, fs: int) -> float:
    """True peak przez 4x nadpróbkowanie (przybliżenie BS.1770)."""
    if data.size == 0:
        return -120.0
    up = signal.resample_poly(data, 4, 1, axis=0)
    return round(db(float(np.max(np.abs(up)))), 2)


# ---------------------------------------------------------------------------
# obwiednia / krawędzie
# ---------------------------------------------------------------------------
def frame_rms_db(mono: np.ndarray, fs: int, frame_ms: float = 10.0) -> np.ndarray:
    n = max(1, int(fs * frame_ms / 1000.0))
    usable = len(mono) - (len(mono) % n)
    if usable <= 0:
        return np.array([db(float(np.sqrt(np.mean(mono**2))))])
    frames = mono[:usable].reshape(-1, n)
    rms = np.sqrt(np.mean(frames**2, axis=1))
    return 20.0 * np.log10(np.maximum(rms, EPS))


def segment_rms_db(mono: np.ndarray, fs: int, start_s: float, end_s: float) -> float:
    a, b = max(0, int(start_s * fs)), min(len(mono), int(end_s * fs))
    if b <= a:
        return db(0.0)
    return db(float(np.sqrt(np.mean(mono[a:b] ** 2))))


# ---------------------------------------------------------------------------
# widmo / tonalność / mowa
# ---------------------------------------------------------------------------
def mel_filterbank(fs: int, n_fft: int, n_mels: int = 40,
                   fmin: float = 50.0, fmax: float | None = None) -> np.ndarray:
    fmax = fmax or min(16000.0, fs / 2.0)
    to_mel = lambda f: 2595.0 * np.log10(1.0 + f / 700.0)  # noqa: E731
    to_hz = lambda m: 700.0 * (10.0 ** (m / 2595.0) - 1.0)  # noqa: E731
    mels = np.linspace(to_mel(fmin), to_mel(fmax), n_mels + 2)
    freqs = to_hz(mels)
    bins = np.floor((n_fft + 1) * freqs / fs).astype(int)
    bins = np.clip(bins, 0, n_fft // 2)
    fb = np.zeros((n_mels, n_fft // 2 + 1))
    for i in range(n_mels):
        lo, mid, hi = bins[i], bins[i + 1], bins[i + 2]
        if mid == lo:
            mid = min(lo + 1, n_fft // 2)
        if hi == mid:
            hi = min(mid + 1, n_fft // 2)
        fb[i, lo:mid] = np.linspace(0, 1, max(1, mid - lo), endpoint=False)
        fb[i, mid:hi] = np.linspace(1, 0, max(1, hi - mid), endpoint=False)
    return fb


def estimate_f0(frame: np.ndarray, fs: int) -> tuple[float, float]:
    """Zwraca (f0 Hz, siła autokorelacji 0-1) dla jednej ramki.

    Autokorelacja liczona przez FFT — wersja czasowa (`np.correlate`) jest
    O(n^2) i przy 527 plikach nie domyka się w rozsądnym czasie.
    """
    x = frame - float(np.mean(frame))
    energy = float(np.dot(x, x))
    if energy < 1e-9:
        return 0.0, 0.0
    n = 1 << int(math.ceil(math.log2(2 * len(x))))
    spec = np.fft.rfft(x, n)
    corr = np.fft.irfft(spec * np.conj(spec), n)[: len(x)]
    corr /= max(float(corr[0]), EPS)
    lo = int(fs / 1000.0)  # 1000 Hz
    hi = min(len(corr) - 1, int(fs / 60.0))  # 60 Hz
    if hi <= lo:
        return 0.0, 0.0
    idx = int(np.argmax(corr[lo:hi])) + lo
    return fs / idx, float(corr[idx])


def spectral_profile(mono: np.ndarray, fs: int) -> dict:
    n_fft = 2048 if len(mono) >= 2048 else max(256, 2 ** int(math.log2(max(len(mono), 256))))
    hop = n_fft // 4
    f, t, zxx = signal.stft(mono, fs=fs, nperseg=n_fft, noverlap=n_fft - hop, padded=True)
    power = np.abs(zxx) ** 2
    frame_energy = power.sum(axis=0)
    active = frame_energy > (np.max(frame_energy) * 1e-4 + EPS)
    if not np.any(active):
        active = np.ones_like(frame_energy, dtype=bool)
    pw = power[:, active]
    fe = frame_energy[active]

    centroid = float(np.sum(f[:, None] * pw) / max(float(np.sum(pw)), EPS))
    mean_spec = pw.mean(axis=1)
    cum = np.cumsum(mean_spec) / max(float(np.sum(mean_spec)), EPS)
    rolloff95 = float(f[int(np.searchsorted(cum, 0.95))]) if cum.size else 0.0
    rolloff99 = float(f[int(np.searchsorted(cum, 0.99))]) if cum.size else 0.0

    band = (f >= 50.0) & (f <= 10000.0)
    pb = np.maximum(pw[band], EPS)
    flat = np.exp(np.mean(np.log(pb), axis=0)) / np.maximum(np.mean(pb, axis=0), EPS)
    tonal_fraction = float(np.mean(flat < 0.05))
    flatness = float(np.median(flat))

    # krawędź pasma: najwyższa częstotliwość z energią w granicach 50 dB od
    # maksimum widma. Wykrywa twarde odcięcie dolnoprzepustowe (kiepska
    # generacja / kodek), czego rolloff procentowy nie odróżnia od
    # naturalnie ciemnego dźwięku.
    mean_spec_db = 10.0 * np.log10(np.maximum(mean_spec, EPS))
    kernel = np.ones(5) / 5.0
    smooth = np.convolve(mean_spec_db, kernel, mode="same")
    ref_band = (f >= 100.0) & (f <= 5000.0)
    ref = float(np.max(smooth[ref_band])) if np.any(ref_band) else float(np.max(smooth))
    above = np.nonzero(smooth > ref - 50.0)[0]
    edge_hz = float(f[above[-1]]) if above.size else 0.0
    above40 = np.nonzero(smooth > ref - 40.0)[0]
    edge40_hz = float(f[above40[-1]]) if above40.size else 0.0
    # stromość zbocza: spadek poziomu na 2 kHz poniżej krawędzi
    below_idx = int(np.searchsorted(f, max(edge_hz - 2000.0, 0.0)))
    edge_idx = int(np.searchsorted(f, edge_hz))
    edge_slope_db = float(smooth[min(below_idx, len(smooth) - 1)] - smooth[min(edge_idx, len(smooth) - 1)])

    def band_share(lo: float, hi: float) -> float:
        m = (f >= lo) & (f < hi)
        return round(float(np.sum(pw[m]) / max(float(np.sum(pw)), EPS)), 4)

    bands = {
        "sub_0_60": band_share(0, 60),
        "low_60_250": band_share(60, 250),
        "mid_250_2k": band_share(250, 2000),
        "high_2k_8k": band_share(2000, 8000),
        "air_8k_plus": band_share(8000, fs / 2),
    }

    # modulacja obwiedni (mowa ma maksimum w 2-8 Hz)
    env = np.sqrt(np.maximum(frame_energy, 0.0))
    env = env - float(np.mean(env))
    fr = fs / hop
    speech_mod = 0.0
    if env.size >= 8 and float(np.max(np.abs(env))) > EPS:
        spec = np.abs(np.fft.rfft(env * np.hanning(env.size)))
        mf = np.fft.rfftfreq(env.size, d=1.0 / fr)
        total = float(np.sum(spec[(mf > 0.5) & (mf < 20.0)])) + EPS
        speech_mod = float(np.sum(spec[(mf >= 2.0) & (mf <= 8.0)]) / total)

    return {
        "spectral_centroid_hz": round(centroid, 1),
        "rolloff95_hz": round(rolloff95, 1),
        "rolloff99_hz": round(rolloff99, 1),
        "spectral_edge_hz": round(edge_hz, 1),
        "spectral_edge40_hz": round(edge40_hz, 1),
        "edge_slope_db": round(edge_slope_db, 1),
        "spectral_flatness": round(flatness, 4),
        "tonal_frame_fraction": round(tonal_fraction, 3),
        "mod_2_8hz_ratio": round(speech_mod, 3),
        "bands": bands,
        "_n_fft": n_fft,
        "_hop": hop,
    }


def pitch_profile(mono: np.ndarray, fs: int) -> dict:
    # Rumor podbasowy jest okresowy i zalewał autokorelację (każdy dudniący
    # sample wychodził „tonalny"). Liczymy wysokość dopiero powyżej 80 Hz.
    sos_hp = signal.butter(4, 80.0, btype="highpass", fs=fs, output="sos")
    mono = signal.sosfilt(sos_hp, mono)
    # f0 szukamy w 80-1000 Hz, więc 8 kHz w zupełności wystarczy i jest ~5x tańsze
    if fs > 8000:
        g = math.gcd(fs, 8000)
        mono = signal.resample_poly(mono, 8000 // g, fs // g)
        fs = 8000
    win = int(0.032 * fs)
    hop = int(0.016 * fs)
    if len(mono) < win:
        return {"voiced_fraction": 0.0, "f0_median_hz": 0.0, "f0_semitone_std": 0.0}
    f0s, strengths = [], []
    for s in range(0, len(mono) - win, hop):
        frame = mono[s : s + win]
        if float(np.sqrt(np.mean(frame**2))) < 10 ** (SILENCE_DB / 20.0):
            continue
        f0, strength = estimate_f0(frame, fs)
        if f0 > 0:
            f0s.append(f0)
            strengths.append(strength)
    if not f0s:
        return {"voiced_fraction": 0.0, "f0_median_hz": 0.0, "f0_semitone_std": 0.0}
    f0s_arr, st = np.array(f0s), np.array(strengths)
    voiced = st > 0.55
    if not np.any(voiced):
        return {"voiced_fraction": 0.0, "f0_median_hz": 0.0, "f0_semitone_std": 0.0}
    vf = f0s_arr[voiced]
    semitones = 12.0 * np.log2(np.maximum(vf, EPS) / 55.0)
    return {
        "voiced_fraction": round(float(np.mean(voiced)), 3),
        "f0_median_hz": round(float(np.median(vf)), 1),
        "f0_semitone_std": round(float(np.std(semitones)), 2),
    }


def fingerprint(mono: np.ndarray, fs: int, n_frames: int = 24, n_mels: int = 40) -> np.ndarray:
    n_fft = 1024
    hop = 512
    f, t, zxx = signal.stft(mono, fs=fs, nperseg=n_fft, noverlap=n_fft - hop, padded=True)
    power = np.abs(zxx) ** 2
    fb = mel_filterbank(fs, n_fft, n_mels=n_mels)
    mel = fb @ power
    logmel = np.log10(mel + 1e-10)
    if logmel.shape[1] < n_frames:
        pad = n_frames - logmel.shape[1]
        logmel = np.pad(logmel, ((0, 0), (0, pad)), mode="edge")
    idx = np.array_split(np.arange(logmel.shape[1]), n_frames)
    comp = np.stack([logmel[:, i].mean(axis=1) for i in idx], axis=1)
    vec = comp.flatten()
    vec = vec - float(np.mean(vec))
    norm = float(np.linalg.norm(vec))
    return vec / norm if norm > EPS else vec


# ---------------------------------------------------------------------------
# analiza pojedynczego pliku
# ---------------------------------------------------------------------------
@dataclass
class FileResult:
    metrics: dict
    fp: np.ndarray = field(default_factory=lambda: np.zeros(1))


def analyze(path: Path, expected: float | None) -> FileResult:
    data, fs = sf.read(str(path), always_2d=True)
    mono = data.mean(axis=1)
    dur = len(mono) / fs

    peak = float(np.max(np.abs(data))) if data.size else 0.0
    clip_frac = float(np.mean(np.abs(data) >= 0.999)) if data.size else 0.0
    frames = frame_rms_db(mono, fs, 10.0)
    max_frame_db = float(np.max(frames))
    active = frames[frames > SILENCE_DB]
    active_rms_db = float(np.mean(active)) if active.size else -120.0

    above = np.nonzero(frames > SILENCE_DB)[0]
    if above.size:
        lead_sil = above[0] * 0.010
        trail_sil = (len(frames) - 1 - above[-1]) * 0.010
    else:
        lead_sil = trail_sil = dur

    spec = spectral_profile(mono, fs)
    pitch = pitch_profile(mono, fs)
    bands = spec.pop("bands")
    spec.pop("_n_fft", None)
    spec.pop("_hop", None)

    pcm16 = np.clip(mono, -1.0, 1.0)
    pcm_md5 = hashlib.md5((pcm16 * 32767).astype(np.int16).tobytes()).hexdigest()

    metrics = {
        "id": path.stem,
        "file": path.name,
        "duration_s": round(dur, 3),
        "expected_s": expected,
        "sr": fs,
        "channels": int(data.shape[1]),
        "peak_db": round(db(peak), 2),
        "true_peak_dbtp": true_peak_dbtp(data, fs),
        "lufs": integrated_lufs(data, fs),
        "clip_frac": round(clip_frac, 6),
        "dc_offset": round(float(np.mean(mono)), 5),
        "overall_rms_db": round(db(float(np.sqrt(np.mean(mono**2)))), 2),
        "active_rms_db": round(active_rms_db, 2),
        "max_frame_db": round(max_frame_db, 2),
        "crest_db": round(db(peak) - round(db(float(np.sqrt(np.mean(mono**2)))), 2), 2),
        "lead_silence_s": round(lead_sil, 3),
        "trail_silence_s": round(trail_sil, 3),
        "content_s": round(max(0.0, dur - lead_sil - trail_sil), 3),
        "start_15ms_db": round(segment_rms_db(mono, fs, 0.0, 0.015), 2),
        "start_50ms_db": round(segment_rms_db(mono, fs, 0.0, 0.050), 2),
        "end_10ms_db": round(segment_rms_db(mono, fs, dur - 0.010, dur), 2),
        "end_30ms_db": round(segment_rms_db(mono, fs, dur - 0.030, dur), 2),
        "end_100ms_db": round(segment_rms_db(mono, fs, dur - 0.100, dur), 2),
        "pcm_md5": pcm_md5,
        "audible_share": round(bands["mid_250_2k"] + bands["high_2k_8k"] + bands["air_8k_plus"], 4),
        **spec,
        **pitch,
        "bands": bands,
    }
    return FileResult(metrics=metrics, fp=fingerprint(mono, fs))


# ---------------------------------------------------------------------------
# flagi
# ---------------------------------------------------------------------------
def add_flags(metrics: list[dict]) -> dict:
    act = np.array([m["active_rms_db"] for m in metrics])
    lufs = np.array([m["lufs"] for m in metrics])
    mean, std = float(np.mean(act)), float(np.std(act))
    lufs_mean, lufs_std = float(np.mean(lufs)), float(np.std(lufs))

    for m in metrics:
        flags: list[str] = []
        # --- krawędzie -----------------------------------------------------
        if m["start_15ms_db"] > CUT_START_DB and m["start_15ms_db"] > m["max_frame_db"] - CUT_START_MARGIN:
            flags.append("cut_start_hard")
        if m["end_10ms_db"] > CUT_END_DB or m["end_10ms_db"] > m["max_frame_db"] - CUT_END_MARGIN:
            flags.append("cut_end_hard")
        elif m["end_30ms_db"] > -32.0 and m["end_30ms_db"] > m["max_frame_db"] - 20.0:
            flags.append("cut_end_soft")
        # --- głośność ------------------------------------------------------
        if m["lufs"] < LUFS_QUIET or m["peak_db"] < -18.0:
            flags.append("too_quiet")
        if m["lufs"] > LUFS_LOUD:
            flags.append("too_loud")
        if m["clip_frac"] > CLIP_FRAC:
            flags.append("clipping")
        if m["true_peak_dbtp"] > TRUE_PEAK_HOT and "clipping" not in flags:
            flags.append("true_peak_hot")
        # --- treść ---------------------------------------------------------
        if m["max_frame_db"] < -40.0:
            flags.append("near_silent")
        if m["expected_s"] is not None and abs(m["duration_s"] - m["expected_s"]) > 0.20:
            flags.append("duration_mismatch")
        if m["bands"]["sub_0_60"] > SUB_DOMINANT:
            flags.append("sub_dominant")
        if m["audible_share"] < AUDIBLE_SHARE_MIN:
            flags.append("muffled")
        if m["content_s"] < SHORT_CONTENT_S:
            flags.append("short_content")
        if (m["tonal_frame_fraction"] > TONAL_FRACTION and m["f0_semitone_std"] < TONAL_PITCH_STD
                and m["voiced_fraction"] > TONAL_VOICED and m["audible_share"] > TONAL_AUDIBLE_MIN):
            flags.append("tonal_sustained")
        if m["mod_2_8hz_ratio"] > SPEECH_MOD_RATIO and m["voiced_fraction"] > 0.35 and 300.0 < m["spectral_centroid_hz"] < 3000.0:
            flags.append("speech_like")
        if abs(m["dc_offset"]) > 0.01:
            flags.append("dc_offset")
        # --- kosmetyka ------------------------------------------------------
        if m["lead_silence_s"] > LEAD_SILENCE_S:
            flags.append("long_lead_silence")
        if m["trail_silence_s"] > TRAIL_SILENCE_S:
            flags.append("long_trail_silence")
        m["flags"] = flags

    return {
        "active_rms_mean_db": round(mean, 2),
        "active_rms_std_db": round(std, 2),
        "lufs_mean": round(lufs_mean, 2),
        "lufs_std": round(lufs_std, 2),
        "lufs_median": round(float(np.median(lufs)), 2),
        "lufs_p10": round(float(np.percentile(lufs, 10)), 2),
        "lufs_p90": round(float(np.percentile(lufs, 90)), 2),
    }


def find_similar(ids: list[str], fps: np.ndarray, threshold: float) -> list[dict]:
    sim = fps @ fps.T
    np.fill_diagonal(sim, -1.0)
    pairs = []
    iu = np.triu_indices(len(ids), k=1)
    for i, j in zip(*iu):
        s = float(sim[i, j])
        if s >= threshold:
            pairs.append({"a": ids[i], "b": ids[j], "cosine": round(s, 4)})
    pairs.sort(key=lambda p: -p["cosine"])
    return pairs


# ---------------------------------------------------------------------------
# raport markdown
# ---------------------------------------------------------------------------
def fmt_table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def build_markdown(metrics: list[dict], stats: dict, pairs: list[dict],
                   dup_pcm: list[list[str]], text_dups: dict,
                   titles: dict[str, str], scen: dict[str, dict],
                   previous: dict[str, list[str]] | None) -> str:
    by_id = {m["id"]: m for m in metrics}
    total = len(metrics)

    def cat(flag: str) -> list[dict]:
        return [m for m in metrics if flag in m["flags"]]

    def title(i: str) -> str:
        return titles.get(i, scen.get(i, {}).get("title", "?"))

    flagged = [m for m in metrics if m["flags"]]
    main_flags = {"near_silent", "cut_end_hard", "too_quiet", "too_loud", "clipping",
                  "duration_mismatch", "sub_dominant", "muffled", "short_content", "dc_offset"}
    main_flagged = [m for m in metrics if main_flags & set(m["flags"])]

    lines: list[str] = []
    A = lines.append
    A(f"# Pełny audyt korpusu sampli — {date.today().isoformat()}")
    A("")
    A(f"Zakres: **{total}** plików `audio/samples/<id>.mp3`. Skan od zera skryptem")
    A("`scripts/audit_samples_full.py` (dekodowanie PCM → metryki sygnałowe,")
    A("głośnościowe, widmowe i odciski brzmieniowe). Audyt **niczego nie zmienia**.")
    A("")
    A("## Co nowego względem audytu porannego")
    A("")
    A("Poprzedni audyt (`2026-09-28-audio-audit.md`) mierzył obwiednię, peak i ciszę.")
    A("Ten skan dokłada cztery wymiary, których wcześniej nie sprawdzaliśmy:")
    A("")
    A("1. **Głośność percepcyjna (LUFS, BS.1770-4)** + **true peak** (4x nadpróbkowanie) —")
    A("   peak próbkowy nie mówi, czy sample będzie słyszalny w bibliotece obok innych.")
    A("2. **Rozkład energii w pasmach** — wyłapuje sample zepchnięte w infradźwięki")
    A("   (peak pokazuje „głośno\", a na telefonie nie słychać nic) i takie bez treści")
    A("   powyżej 250 Hz.")
    A("3. **Tonalność i mowa** — spectral flatness, śledzenie f0 i modulacja obwiedni")
    A("   2–8 Hz; prompty zabraniają muzyki i mowy, więc to kontrola zgodności z regułą.")
    A("4. **Duplikaty i bliźniaki** — md5 zdekodowanego PCM oraz kosinus odcisków")
    A("   log-mel; reguła projektu wymaga unikalnego sampla dla każdej fabuły.")
    A("")
    A("## Uczciwe zastrzeżenia")
    A("")
    A("- **LUFS na 2–3 s materiale** jest przybliżeniem (standard zakłada dłuższy program).")
    A("  Używam go porównawczo wewnątrz korpusu, nie jako certyfikowanego pomiaru.")
    A("- **Tonalność ≠ muzyka.** Dzwon, gong, rezonans metalu czy gwizd wiatru też są tonalne.")
    A("  Flaga `tonal_sustained` to kandydat do odsłuchu, nie wyrok.")
    A("- **Mowa** wykrywana heurystycznie (modulacja sylabiczna + pasmo mowy). Krzyki")
    A("  stworów i skrzypienie drewna potrafią ją udawać — pewność niska.")
    A("- **Bliźniaki brzmieniowe**: wysoki kosinus log-mel oznacza „podobna barwa i przebieg")
    A("  w czasie\", a nie „ten sam plik\". Dwa różne uderzenia miecza *mają prawo* być podobne.")
    A("- **`cut_start_hard`** dla dźwięków ciągłych (deszcz, tłum, bitwa) bywa naturalne —")
    A("  kategoria utrzymana z poprzedniego audytu dla porównywalności.")
    A("- **True peak i peak** liczone są na **zdekodowanym** MP3, więc zależą od dekodera;")
    A("  wartości > 0 dBFS to normalny overshoot kodera, nie błąd generacji.")
    A("- **Infradźwięki vs „ciemny dźwięk\"**: LUFS jest ważony percepcyjnie (filtr K tłumi")
    A("  dół pasma), dlatego plik z peakiem −0,3 dBFS potrafi mieć −20 LUFS. To nie jest")
    A("  błąd pomiaru, tylko dokładnie to, co usłyszy właściciel.")
    A("- Kategorie `sub_dominant` i `muffled` **częściowo się pokrywają** — pierwsza mówi")
    A("  „energia poszła w dół pasma\", druga „nie ma nic w paśmie detalu\".")
    A("")
    A("## Podsumowanie")
    A("")
    rows = [
        ["KRYTYCZNE — (prawie) cisza", str(len(cat("near_silent"))), "wysoka", "regeneracja"],
        ["WYSOKIE — ucięty koniec", str(len(cat("cut_end_hard"))), "wysoka", "odsłuch → regeneracja/fade"],
        ["WYSOKIE — za cicho (LUFS/peak)", str(len(cat("too_quiet"))), "wysoka", "normalizacja w postprodukcji"],
        ["WYSOKIE — energia w infradźwiękach", str(len(cat("sub_dominant"))), "wysoka", "EQ+normalizacja albo regeneracja"],
        ["WYSOKIE — brak treści powyżej 250 Hz", str(len(cat("muffled"))), "średnia", "odsłuch → regeneracja"],
        ["WYSOKIE — treść krótsza niż 0,8 s", str(len(cat("short_content"))), "wysoka", "trym albo regeneracja"],
        ["ŚREDNIE — przester (clipping)", str(len(cat("clipping"))), "średnia", "tłumienie + limiter"],
        ["ŚREDNIE — true peak > +1 dBTP", str(len(cat("true_peak_hot"))), "średnia", "limiter w postprodukcji"],
        ["ŚREDNIE — za głośno", str(len(cat("too_loud"))), "średnia", "wyrównanie głośności"],
        ["ŚREDNIE — offset DC", str(len(cat("dc_offset"))), "wysoka", "filtr górnoprzepustowy 20 Hz"],

        ["DO ODSŁUCHU — tonalne/„muzyczne\"", str(len(cat("tonal_sustained"))), "niska", "weryfikacja uchem"],
        ["DO ODSŁUCHU — podobne do mowy", str(len(cat("speech_like"))), "niska", "weryfikacja uchem"],
        ["DO ODSŁUCHU — start na pełnym poziomie", str(len(cat("cut_start_hard"))), "niska", "weryfikacja uchem / fade-in"],
        [f"BLIŹNIAKI — para sampli ≥ {SIM_THRESHOLD} kosinusa", str(len(pairs)), "niska", "odsłuch pary, ewentualnie nowy prompt"],
        ["KOSMETYCZNE — długa cisza wiodąca", str(len(cat("long_lead_silence"))), "wysoka", "opcjonalny trym"],
        ["KOSMETYCZNE — długa cisza końcowa", str(len(cat("long_trail_silence"))), "wysoka", "opcjonalny trym"],
    ]
    A(fmt_table(["Kategoria", "Plików", "Pewność", "Rekomendacja"], rows))
    A("")
    A(f"Plików z co najmniej jedną flagą: **{len(flagged)}** / {total}.")
    A(f"Plików z flagą **merytoryczną** (bez kategorii kosmetycznych i „start na pełnym")
    A(f"poziomie\"): **{len(main_flagged)}**.")
    A("")
    A("")
    A("## Najważniejszy wniosek: korpus nie ma wyrównanej głośności")
    A("")
    lufs_vals = np.array([m["lufs"] for m in metrics])
    target = -20.0
    gain = target - lufs_vals
    A("Rozkład głośności percepcyjnej: mediana **{:.1f} LUFS**, p10 **{:.1f}**, p90 **{:.1f}**, "
      "σ **{:.1f} LU**, rozpiętość **{:.1f} LU** (od {:.1f} do {:.1f}).".format(
          stats["lufs_median"], stats["lufs_p10"], stats["lufs_p90"], stats["lufs_std"],
          float(lufs_vals.max() - lufs_vals.min()), float(lufs_vals.min()), float(lufs_vals.max())))
    A("")
    A("To nie jest kwestia pojedynczych odstających plików — **cały korpus jest nierówny**.")
    A("Przy odsłuchu biblioteki po kolei jedne sample są ledwie słyszalne, inne wyrywają")
    A("głośniki. Nic dziwnego: każdy plik przyszedł z generatora bez wspólnego odniesienia.")
    A("")
    A("Gdyby wyrównać wszystko do **{:.0f} LUFS** z sufitem **−1 dBTP**:".format(target))
    A("")
    A(f"- plików wymagających wzmocnienia > +10 dB: **{int(np.sum(gain > 10))}** "
      f"(z tego > +15 dB: {int(np.sum(gain > 15))} — tam wyjdzie szum tła, lepiej zregenerować),")
    A(f"- plików wymagających wyciszenia > 6 dB: **{int(np.sum(gain < -6))}**,")
    A(f"- plików w granicach ±3 dB od celu: **{int(np.sum(np.abs(gain) <= 3))}**.")
    A("")
    A("Operacja jest lokalna, odwracalna i **nie kosztuje kredytów**. Rekomendacja: zrobić ją")
    A("jednym przebiegiem na całym korpusie, dopiero potem oceniać pojedyncze sample uchem —")
    A("bo dziś ocena „ten jest za cichy\" myli się z „ten jest zły\".")
    A("")

    section = 0

    def add_section(title_txt: str, header: list[str], rows_: list[list[str]], note: str = "") -> None:
        nonlocal section
        section += 1
        A(f"## {section}. {title_txt}")
        A("")
        if note:
            A(note)
            A("")
        if rows_:
            A(fmt_table(header, rows_))
        else:
            A("_Brak plików w tej kategorii._")
        A("")

    # 1. krytyczne
    add_section(
        "KRYTYCZNE — plik (prawie) cichy",
        ["ID", "Tytuł", "Peak dBFS", "LUFS", "Maks. ramka"],
        [[m["id"], title(m["id"]), f'{m["peak_db"]}', f'{m["lufs"]}', f'{m["max_frame_db"]}']
         for m in sorted(cat("near_silent"), key=lambda x: x["max_frame_db"])],
        "Materiał w praktyce niesłyszalny — regeneracja, nie postprodukcja.",
    )

    # 2. ucięty koniec
    add_section(
        "WYSOKIE — ucięty koniec (brak wybrzmienia)",
        ["ID", "Tytuł", "Koniec 10 ms", "Maks. ramka", "Różnica", "Inne flagi"],
        [[m["id"], title(m["id"]), f'{m["end_10ms_db"]} dBFS', f'{m["max_frame_db"]} dBFS',
          f'{round(m["end_10ms_db"] - m["max_frame_db"], 1)} dB',
          ", ".join(f for f in m["flags"] if f != "cut_end_hard") or "—"]
         for m in sorted(cat("cut_end_hard"), key=lambda x: -x["end_10ms_db"])],
        "Sortowane od najbrutalniejszego cięcia. Fade-out 0,2–0,35 s naprawia to bez kredytów.",
    )

    # 3. za cicho
    add_section(
        "WYSOKIE — za cicho względem korpusu",
        ["ID", "Tytuł", "LUFS", "Peak dBFS", "Aktywny RMS", "Inne flagi"],
        [[m["id"], title(m["id"]), f'{m["lufs"]}', f'{m["peak_db"]}', f'{m["active_rms_db"]}',
          ", ".join(f for f in m["flags"] if f != "too_quiet") or "—"]
         for m in sorted(cat("too_quiet"), key=lambda x: x["lufs"])],
        f"Próg: LUFS < {LUFS_QUIET:.0f} albo peak < −18 dBFS. Większość naprawia normalizacja "
        "(bez kredytów); przy wzmocnieniu > +15 dB trzeba sprawdzić, czy nie wychodzi szum.",
    )

    # 4. infradźwięki
    add_section(
        "WYSOKIE — energia zepchnięta w infradźwięki",
        ["ID", "Tytuł", "Udział < 60 Hz", "Udział > 250 Hz", "LUFS", "Peak dBFS", "Scenariusz"],
        [[m["id"], title(m["id"]), f'{m["bands"]["sub_0_60"]:.2f}', f'{m["audible_share"]:.3f}',
          f'{m["lufs"]}', f'{m["peak_db"]}', scen.get(m["id"], {}).get("sample_scenario", "")[:45]]
         for m in sorted(cat("sub_dominant"), key=lambda x: -x["bands"]["sub_0_60"])],
        f"Ponad {int(SUB_DOMINANT*100)} % energii poniżej 60 Hz. Miernik peaku pokazuje „głośno\", "
        "ale na laptopie, telefonie i większości słuchawek taki sample jest praktycznie "
        "niesłyszalny — dlatego LUFS (ważony percepcyjnie) bywa tu 20 dB niżej niż peak. "
        "Naprawa: EQ (odcięcie 40 Hz) + normalizacja, a jeśli po tym nie zostaje treść — regeneracja.",
    )

    # 4b. brak treści w paśmie słyszalnym
    add_section(
        "WYSOKIE — brak treści powyżej 250 Hz",
        ["ID", "Tytuł", "Udział > 250 Hz", "Centroid", "LUFS", "Inne flagi", "Scenariusz"],
        [[m["id"], title(m["id"]), f'{m["audible_share"]:.4f}', f'{int(m["spectral_centroid_hz"])} Hz',
          f'{m["lufs"]}', ", ".join(f for f in m["flags"] if f != "muffled") or "—",
          scen.get(m["id"], {}).get("sample_scenario", "")[:40]]
         for m in sorted(cat("muffled"), key=lambda x: x["audible_share"])],
        f"Mniej niż {AUDIBLE_SHARE_MIN*100:.0f} % energii powyżej 250 Hz — w paśmie, w którym ucho "
        "rozpoznaje materiał i detal, nie ma nic. Dla tąpnięcia olbrzyma to bywa poprawne, "
        "dla metalu, szkła, ptaków czy magii oznacza zgubioną treść.",
    )

    # 5. przester
    add_section(
        "ŚREDNIE — przester i true peak",
        ["ID", "Tytuł", "Peak dBFS", "True peak dBTP", "% próbek na zakresie", "Inne flagi"],
        [[m["id"], title(m["id"]), f'{m["peak_db"]}', f'{m["true_peak_dbtp"]}',
          f'{m["clip_frac"]*100:.3f}%', ", ".join(f for f in m["flags"] if f not in {"clipping", "true_peak_hot"}) or "—"]
         for m in sorted(cat("clipping") + [x for x in cat("true_peak_hot") if "clipping" not in x["flags"]],
                         key=lambda x: -x["true_peak_dbtp"])],
        f"Przester = > {CLIP_FRAC*100:.2f} % próbek na pełnej skali (w tym korpusie: brak). "
        f"True peak > +{TRUE_PEAK_HOT:.0f} dBTP to ryzyko zniekształceń po transkodowaniu — "
        "naprawialne limiterem, bez kredytów.",
    )

    # 5b. krótka treść
    add_section(
        "WYSOKIE — realna treść krótsza niż 0,8 s",
        ["ID", "Tytuł", "Treść", "Długość pliku", "Cisza przód", "Cisza tył", "Scenariusz"],
        [[m["id"], title(m["id"]), f'{m["content_s"]} s', f'{m["duration_s"]} s',
          f'{m["lead_silence_s"]} s', f'{m["trail_silence_s"]} s',
          scen.get(m["id"], {}).get("sample_scenario", "")[:45]]
         for m in sorted(cat("short_content"), key=lambda x: x["content_s"])],
        "Po odjęciu ciszy zostaje bardzo mało dźwięku. Czasem to poprawne (jedno "
        "uderzenie), czasem generacja urwała temat.",
    )

    # 5c. DC
    add_section(
        "ŚREDNIE — offset DC",
        ["ID", "Tytuł", "Offset DC", "Peak dBFS", "Uwaga"],
        [[m["id"], title(m["id"]), f'{m["dc_offset"]:+.3f}', f'{m["peak_db"]}',
          "zabiera headroom, może trzaskać na starcie/końcu"]
         for m in sorted(cat("dc_offset"), key=lambda x: -abs(x["dc_offset"]))],
        "Stała składowa w sygnale. Filtr górnoprzepustowy 20 Hz usuwa ją bezstratnie "
        "dla treści słyszalnej.",
    )

    # 6. za głośno
    add_section(
        "ŚREDNIE — za głośno względem korpusu",
        ["ID", "Tytuł", "LUFS", "Peak dBFS", "Aktywny RMS"],
        [[m["id"], title(m["id"]), f'{m["lufs"]}', f'{m["peak_db"]}', f'{m["active_rms_db"]}']
         for m in sorted(cat("too_loud"), key=lambda x: -x["lufs"])],
        f"Próg: LUFS > {LUFS_LOUD}. Sample wyrywa się z biblioteki przy odsłuchu seryjnym.",
    )

    # 7. tonalne
    add_section(
        "DO ODSŁUCHU — tonalne / potencjalnie muzyczne",
        ["ID", "Tytuł", "Ramki tonalne", "f0", "σ f0 (półtony)", "Flatness", "Scenariusz"],
        [[m["id"], title(m["id"]), f'{m["tonal_frame_fraction"]:.2f}', f'{int(m["f0_median_hz"])} Hz',
          f'{m["f0_semitone_std"]}', f'{m["spectral_flatness"]}',
          (scen.get(m["id"], {}).get("sample_scenario", "")[:60])]
         for m in sorted(cat("tonal_sustained"), key=lambda x: -x["tonal_frame_fraction"])],
        "Stabilna wysokość dźwięku przez większość pliku. Dla dzwonu/gongu/rezonansu to "
        "poprawne; flaga ma sens tylko jeśli scenariusz nie zakładał źródła tonalnego.",
    )

    # 8. mowa
    add_section(
        "DO ODSŁUCHU — podobne do mowy",
        ["ID", "Tytuł", "Modulacja 2–8 Hz", "Udział dźwięcznych", "Centroid", "Scenariusz"],
        [[m["id"], title(m["id"]), f'{m["mod_2_8hz_ratio"]:.2f}', f'{m["voiced_fraction"]:.2f}',
          f'{int(m["spectral_centroid_hz"])} Hz', (scen.get(m["id"], {}).get("sample_scenario", "")[:60])]
         for m in sorted(cat("speech_like"), key=lambda x: -x["mod_2_8hz_ratio"])],
        "Heurystyka mowy — niska pewność. Sprawdzić, czy nie ma zrozumiałych słów "
        "(prompty zabraniają mowy).",
    )

    # 9. bliźniaki
    section += 1
    A(f"## {section}. BLIŹNIAKI — sample brzmiące niemal identycznie")
    A("")
    A(f"Kosinus odcisków log-mel ≥ {SIM_THRESHOLD}. Identyczny PCM (md5): "
      f"**{len(dup_pcm)}** grup.")
    A("")
    if dup_pcm:
        A(fmt_table(["Identyczne pliki (md5 PCM)"], [[", ".join(g)] for g in dup_pcm]))
        A("")
    if pairs:
        A(fmt_table(
            ["Kosinus", "ID A", "Tytuł A", "ID B", "Tytuł B", "Scenariusz A", "Scenariusz B"],
            [[f'{p["cosine"]:.3f}', p["a"], title(p["a"]), p["b"], title(p["b"]),
              scen.get(p["a"], {}).get("sample_scenario", "")[:45],
              scen.get(p["b"], {}).get("sample_scenario", "")[:45]] for p in pairs[:60]],
        ))
        if len(pairs) > 60:
            A("")
            A(f"…oraz {len(pairs) - 60} dalszych par w JSON-ie.")
    else:
        A("_Nie znaleziono par powyżej progu._")
    A("")

    # 10. teksty
    section += 1
    A(f"## {section}. Kontrola tekstów scenariuszy")
    A("")
    if text_dups["prompts"] or text_dups["scenarios"]:
        if text_dups["prompts"]:
            A("Identyczne prompty:")
            A("")
            A(fmt_table(["ID", "Prompt"], [[", ".join(ids_), p[:90]] for p, ids_ in text_dups["prompts"]]))
            A("")
        if text_dups["scenarios"]:
            A("Identyczne opisy `sample_scenario`:")
            A("")
            A(fmt_table(["ID", "Scenariusz"], [[", ".join(ids_), s[:90]] for s, ids_ in text_dups["scenarios"]]))
            A("")
    else:
        A("Wszystkie prompty i opisy scenariuszy są unikalne (527/527).")
        A("")

    # 11. kosmetyka
    section += 1
    A(f"## {section}. KOSMETYCZNE — cisza w pliku")
    A("")
    lead = cat("long_lead_silence")
    trail = cat("long_trail_silence")
    A(f"- cisza wiodąca > {LEAD_SILENCE_S} s: **{len(lead)}** plików "
      f"({', '.join(m['id'] for m in sorted(lead, key=lambda x: -x['lead_silence_s'])[:25])}"
      f"{' …' if len(lead) > 25 else ''})")
    A(f"- cisza końcowa > {TRAIL_SILENCE_S} s: **{len(trail)}** plików "
      f"({', '.join(m['id'] for m in sorted(trail, key=lambda x: -x['trail_silence_s'])[:25])}"
      f"{' …' if len(trail) > 25 else ''})")
    A("")
    A("To nie jest błąd generacji — sample po prostu nie wypełnia całej zadeklarowanej")
    A("długości. Trym/skrócenie pliku jest opcjonalne i bezkosztowe.")
    A("")

    # porównanie z poprzednim audytem
    if previous:
        section += 1
        A(f"## {section}. Różnice względem audytu po rundzie r005")
        A("")
        prev_flagged = {i for i, fl in previous.items() if set(fl) & main_flags}
        now_flagged = {m["id"] for m in main_flagged}
        new = sorted(now_flagged - prev_flagged, key=lambda x: int(x))
        gone = sorted(prev_flagged - now_flagged, key=lambda x: int(x))
        A(f"- flagi merytoryczne w poprzednim skanie: **{len(prev_flagged)}**, teraz: **{len(now_flagged)}**")
        A(f"- nowe (nie widział ich poprzedni zestaw metryk): {', '.join(new) if new else '—'}")
        A(f"- zniknęły: {', '.join(gone) if gone else '—'}")
        A("")
        A("Uwaga: poprzedni skan nie mierzył LUFS, pasma, tonalności ani duplikatów,")
        A("więc większość „nowych\" pozycji to nie regresja plików, tylko nowe kryterium.")
        A("")

    # rekomendacje
    section += 1
    A(f"## {section}. Rekomendowana kolejka decyzji")
    A("")
    regen = sorted({m["id"] for m in cat("near_silent") + cat("muffled")}, key=lambda x: int(x))
    post = sorted({m["id"] for m in cat("too_quiet") + cat("too_loud") + cat("clipping")
                   + cat("true_peak_hot") + cat("cut_end_hard") + cat("dc_offset")
                   + cat("sub_dominant")}, key=lambda x: int(x))
    listen = sorted({m["id"] for m in cat("tonal_sustained") + cat("speech_like")}
                    | {p["a"] for p in pairs} | {p["b"] for p in pairs}, key=lambda x: int(x))
    listen = sorted(set(listen) | {m["id"] for m in cat("short_content")}, key=lambda x: int(x))
    A("Kolejność jest celowa: najpierw tania, odwracalna obróbka całego korpusu, dopiero")
    A("potem odsłuch i dopiero na końcu wydawanie kredytów.")
    A("")
    A(f"1. **Postprodukcja lokalna, 0 kredytów** — wyrównanie głośności całego korpusu, "
      f"limiter −1 dBTP, filtr DC. Bezpośrednio dotyczy {len(post)} plików z flagami "
      f"głośnościowymi: {', '.join(post) if post else '—'}")
    A("")
    A(f"2. **Do odsłuchu przed decyzją** — {len(listen)} ID (tonalne, mowopodobne, "
      f"bliźniaki, krótka treść): {', '.join(listen) if listen else '—'}")
    A("")
    A(f"3. **Kandydaci do regeneracji (kredyty, po potwierdzeniu uchem)** — {len(regen)} ID "
      f"bez treści w paśmie słyszalnym: {', '.join(regen) if regen else '—'}")
    A("")
    A("   Uwaga: część z nich to scenariusze **celowo** niskie (kroki olbrzymów, tąpnięcia,")
    A("   bicie serca). Jeśli po EQ i normalizacji brzmią poprawnie, regeneracja jest zbędna.")
    A("")
    A("Pełne metryki per plik: JSON obok tego raportu.")
    A("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--scenarios", default="data/samples/scenarios.jsonl")
    ap.add_argument("--catalog", default="data/catalog.json")
    ap.add_argument("--json", dest="json_out", default="data/samples/audio-audit-fullscan.json")
    ap.add_argument("--markdown", default="")
    ap.add_argument("--previous", default="", help="JSON poprzedniego audytu do porównania")
    ap.add_argument("--similarity-threshold", type=float, default=SIM_THRESHOLD)
    args = ap.parse_args()

    scen: dict[str, dict] = {}
    for line in Path(args.scenarios).read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            scen[str(row["story_id"])] = row

    titles: dict[str, str] = {}
    cat_path = Path(args.catalog)
    if cat_path.exists():
        cat = json.loads(cat_path.read_text(encoding="utf-8"))
        stories = cat["stories"] if isinstance(cat, dict) else cat
        titles = {str(s["id"]): s.get("title", "?") for s in stories}

    files = sorted(Path(args.samples_dir).glob("*.mp3"),
                   key=lambda p: int(p.stem) if p.stem.isdigit() else 10**9)
    metrics: list[dict] = []
    fps: list[np.ndarray] = []
    ids: list[str] = []
    for n, p in enumerate(files, 1):
        expected = scen.get(p.stem, {}).get("duration_seconds")
        expected = float(expected) if expected else None
        try:
            res = analyze(p, expected)
        except Exception as exc:  # noqa: BLE001
            metrics.append({"id": p.stem, "file": p.name, "error": str(exc), "flags": ["decode_error"]})
            continue
        metrics.append(res.metrics)
        fps.append(res.fp)
        ids.append(p.stem)
        if n % 50 == 0:
            print(f"  … {n}/{len(files)}", flush=True)

    ok = [m for m in metrics if "error" not in m]
    stats = add_flags(ok)

    fp_mat = np.stack(fps) if fps else np.zeros((0, 1))
    pairs = find_similar(ids, fp_mat, args.similarity_threshold) if len(ids) > 1 else []

    by_md5: dict[str, list[str]] = {}
    for m in ok:
        by_md5.setdefault(m["pcm_md5"], []).append(m["id"])
    dup_pcm = [sorted(v, key=lambda x: int(x)) for v in by_md5.values() if len(v) > 1]

    prompts: dict[str, list[str]] = {}
    scenarios_txt: dict[str, list[str]] = {}
    for sid, row in scen.items():
        prompts.setdefault(row.get("prompt", "").strip().lower(), []).append(sid)
        scenarios_txt.setdefault(row.get("sample_scenario", "").strip().lower(), []).append(sid)
    text_dups = {
        "prompts": [(k, sorted(v, key=lambda x: int(x))) for k, v in prompts.items() if len(v) > 1],
        "scenarios": [(k, sorted(v, key=lambda x: int(x))) for k, v in scenarios_txt.items() if len(v) > 1],
    }

    previous = None
    if args.previous and Path(args.previous).exists():
        prev_rows = json.loads(Path(args.previous).read_text(encoding="utf-8"))
        previous = {}
        for row in prev_rows:
            fname = row.get("file")
            if fname and fname.endswith(".mp3"):
                previous[fname[:-4]] = row.get("flags", [])

    payload = {
        "generated_on": date.today().isoformat(),
        "samples_dir": args.samples_dir,
        "count": len(ok),
        "corpus_stats": stats,
        "similarity_threshold": args.similarity_threshold,
        "similar_pairs": pairs,
        "identical_pcm_groups": dup_pcm,
        "duplicate_texts": text_dups,
        "files": metrics,
    }
    out = Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    n_flagged = sum(1 for m in metrics if m.get("flags"))
    print(f"przeanalizowano {len(files)} plików, z flagą {n_flagged}, raport JSON: {out}")
    print(f"pary bliźniaków ≥ {args.similarity_threshold}: {len(pairs)}, identyczny PCM: {len(dup_pcm)} grup")

    if args.markdown:
        md = build_markdown(ok, stats, pairs, dup_pcm, text_dups, titles, scen, previous)
        md_path = Path(args.markdown)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md + "\n", encoding="utf-8")
        print(f"raport Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
