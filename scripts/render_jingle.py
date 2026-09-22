#!/usr/bin/env python3
"""Render a 5.5 s story jingle MP3 from a recipe JSON.

STATUS: authoring tool for agents, not used in CI. Dependencies (not part of
the system env): `pip install numpy soundfile lameenc`.

Recipe format (see data/recipes/*.json):

{
  "story_id": "568", "label": "v1", "duration_sec": 5.5,
  "climax_window": [1.5, 3.8],
  "bed": {
    "ambience": {"type": "wind|station_hum|cave_water|terrace", "gain": 0.3, "params": {...}},
    "drone":    {"type": "cinematic_sub|synth_pad|bowl", "freq": 44.0, "gain": 0.4, "params": {...}}
  },
  "events": [
    {"time_sec": 2.0, "type": "synth", "kind": "swarm|crackle|sweep|chime|flutter|banish|thump",
     "gain": 1.0, "pan": 0.0, "role": "warstwa foley / kulminacja", "params": {...}},
    {"time_sec": 1.7, "type": "stem", "file": "impact_smack.mp3", "pitch": 1.3, "offset_sec": 0.0,
     "hp_hz": 150, "gain": 1.1, "pan": -0.2, "role": "warstwa foley"}
  ],
  "ducking": [1.8, 3.6, 0.45],
  "post": {"echo_ms": [140, 280], "echo_gains": [0.16, 0.09], "room": 0.5},
  "project_description": {"summary": "...", "ambience": "...", "drone": "...",
    "mix_notes": "...", "description": "..."}
}

The engine mirrors the legacy three-layer dramaturgy (ambience+drone bed,
foley events, center-panned stinger inside the climax window with ducking)
and emits QA metadata compatible with scripts/qa_score.py +
scripts/validate_versions.py. Used stems are read from
legacy/source/game-audio-pipeline/stems/.
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


# --------------------------------------------------------------------------
# Filters: windowed-sinc FIR (no scipy needed), 2*half+1 taps, zero-phase-ish
# --------------------------------------------------------------------------
def fir_response(freqs: np.ndarray, kind: str, f_lo: float, f_hi: float) -> np.ndarray:
    resp = np.zeros_like(freqs)
    if kind == "low":
        resp[freqs <= f_hi] = 1.0
    elif kind == "high":
        resp[freqs >= f_lo] = 1.0
    elif kind == "band":
        resp[(freqs >= f_lo) & (freqs <= f_hi)] = 1.0
    return resp


def apply_fir(x: np.ndarray, kind: str, f_lo: float, f_hi: float | None = None,
              half: int = 400, sr: int = SR) -> np.ndarray:
    n_fft = 1 << (len(x) + 2 * half - 1).bit_length()
    spec = np.fft.rfft(x, n_fft)
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    resp = fir_response(freqs, kind, f_lo, f_hi if f_hi is not None else f_lo)
    # cosine soft edges to avoid ringing around the cutoff
    edge = 60.0
    soft = 0.5 * (np.tanh((freqs - (f_lo - edge)) / edge) + 1.0) if kind != "low" else 0.5 * (1.0 - np.tanh((freqs - (f_hi + 0)) / edge - edge / edge)) + 0.5
    if kind == "low":
        soft = np.clip(1.0 - (freqs - f_hi) / (2 * edge), 0.0, 1.0)
    elif kind == "high":
        soft = np.clip((freqs - f_lo) / (2 * edge) + 0.5, 0.0, 1.0)
    else:
        soft = np.clip(1.0 - np.abs(freqs - (f_lo + f_hi) / 2) / (max((f_hi - f_lo) / 2, 1.0) + 2 * edge), 0.0, 1.0)
        soft = np.clip(soft * 4.0, 0.0, 1.0)
    spec *= resp * soft if np.any(resp) else resp
    y = np.fft.irfft(spec, n_fft)[: len(x)]
    return y


def filter_signal(x: np.ndarray, kind: str, f_lo: float, f_hi: float | None = None) -> np.ndarray:
    if kind == "low" and (f_hi or f_lo) >= SR / 2 - 1:
        return x
    y = apply_fir(x, kind, f_lo, f_hi)
    peak = np.max(np.abs(y)) + 1e-9
    return y / peak * min(1.0, np.max(np.abs(x)) / peak if np.max(np.abs(x)) > 0 else 1.0)


def resample_linear(x: np.ndarray, new_len: int) -> np.ndarray:
    if new_len == len(x):
        return x
    old_t = np.linspace(0.0, 1.0, len(x), endpoint=False)
    new_t = np.linspace(0.0, 1.0, new_len, endpoint=False)
    return np.interp(new_t, old_t, x).astype(np.float64)


def load_stem(name: str, pitch: float = 1.0, offset_sec: float = 0.0) -> np.ndarray:
    import soundfile as sf  # authoring-only dependency

    path = STEMS / name
    if not path.is_file():
        raise FileNotFoundError(f"stem not found: {path}")
    data, sr = sf.read(str(path))
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != SR:
        data = resample_linear(data, int(round(len(data) * SR / sr)))
    if offset_sec > 0:
        data = data[int(offset_sec * SR):]
    if pitch != 1.0:
        data = resample_linear(data, max(8, int(len(data) / pitch)))
    return data


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
        tre = np.random.normal(0, 1, n)
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
    raise ValueError(f"unknown synth kind: {kind}")


# --------------------------------------------------------------------------
# Mix engine
# --------------------------------------------------------------------------
def pan_gains(pan: float) -> tuple[float, float]:
    return (0.95 - 0.25 * pan), (0.95 + 0.25 * pan)


def render(recipe: dict) -> tuple[np.ndarray, dict]:
    dur = float(recipe.get("duration_sec", STORY_SECONDS_DEFAULT))
    n = int(dur * SR)
    L = np.zeros(n)
    R = np.zeros(n)

    bed = recipe.get("bed", {})
    bedL = np.zeros(n)
    bedR = np.zeros(n)
    if bed.get("ambience"):
        amb = bed["ambience"]
        aL, aR = ambience_layer(amb["type"], dur, float(amb.get("gain", 0.3)), amb.get("params", {}))
        bedL += aL
        bedR += aR
    if bed.get("drone"):
        dr = bed["drone"]
        dL, dR = drone_layer(dr["type"], float(dr.get("freq", 44.0)), dur, float(dr.get("gain", 0.4)), dr.get("params", {}))
        bedL += dL
        bedR += dR

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
        gain = float(ev.get("gain", 1.0))
        pan = float(ev.get("pan", 0.0))
        gL, gR = pan_gains(pan)
        if ev["type"] == "stem":
            sig = load_stem(ev["file"], pitch=float(ev.get("pitch", 1.0)), offset_sec=float(ev.get("offset_sec", 0.0)))
            if ev.get("hp_hz"):
                sig = filter_signal(sig, "high", float(ev["hp_hz"]), None)
            peak = np.max(np.abs(sig)) + 1e-9
            sig = sig / peak * 0.95
        elif ev["type"] == "synth":
            sig = synth_event(ev["kind"], float(ev.get("length_sec", 1.0)), ev.get("params", {}), seed=1000 + idx)
        else:
            raise ValueError(f"unknown event type: {ev['type']}")
        start = int(float(ev["time_sec"]) * SR)
        end = min(n, start + len(sig))
        if end <= start:
            continue
        seg = sig[: end - start] * gain
        L[start:end] += seg * gL
        R[start:end] += seg * gR
        qa_events.append({
            "time_sec": float(ev["time_sec"]),
            "sample": ev.get("file") or f"synth:{ev.get('kind')}",
            "role": ev.get("role", "warstwa foley"),
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

    # soft limiter + normalize (QA gates: peak in [0.25, 0.99), |DC| < 0.015)
    # Target 0.55 pre-encode: matches the legacy v1-v5 catalog loudness
    # (decoded peak ~0.48-0.60) and leaves headroom for MP3 overshoot, which
    # can add ~15% on transient-dense stingers.
    mix = np.tanh(mix * 1.05)
    dc = mix.mean(axis=0)
    mix = mix - dc  # kill any DC component before encoding
    peak = np.max(np.abs(mix)) + 1e-9
    mix = mix / peak * 0.55

    qa = qa_audit(mix, tuple(recipe.get("climax_window", [1.5, 3.8])))
    return mix, {"events": qa_events, "qa": qa}


def qa_audit(mix: np.ndarray, climax_window: tuple[float, float]) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from qa_score import calculate_qa_score  # single scoring source

    mono = mix.mean(axis=1)
    dc_ok = bool(np.abs(np.mean(mono)) <= 0.015)
    peak = float(np.max(np.abs(mono)))
    peak_ok = 0.25 <= peak <= 0.99
    step = int(SR * 0.35)
    dead = [i / SR for i in range(0, len(mono) - step, step)
            if np.sqrt(np.mean(mono[i:i + step] ** 2)) < 0.003]
    continuity_ok = len(dead) <= 1
    rms_intro = float(np.sqrt(np.mean(mono[: int(SR * 1.0)] ** 2)) + 1e-5)
    c0, c1 = int(climax_window[0] * SR), int(climax_window[1] * SR)
    rms_climax = float(np.sqrt(np.mean(mono[c0:c1] ** 2)))
    ratio = rms_climax / rms_intro
    result = calculate_qa_score(climax_ratio=ratio, dc_ok=dc_ok, peak_ok=peak_ok, continuity_ok=continuity_ok)
    result["details"] = [
        ("DC offset: OK" if dc_ok else "DC offset: FAIL"),
        ("Peak/headroom: OK" if peak_ok else f"Peak/headroom: FAIL ({peak:.2f})"),
        ("Ciągłość tła: OK" if continuity_ok else f"Martwa cisza: {dead}"),
        f"Kontrast dramaturgiczny: {result['dramaturgy']}/30 (ratio {ratio:.2f}x)",
    ]
    result["climax_ratio"] = round(ratio, 2)
    return result


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
    parser.add_argument("--print-description", action="store_true",
                        help="print project_description JSON for data/versions.json")
    args = parser.parse_args()

    recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
    mix, meta = render(recipe)
    encode_mp3(mix, args.out)
    qa = meta["qa"]
    print(f"Rendered {args.out} ({args.out.stat().st_size} B); QA {qa['score']}/100 [{qa['status']}], "
          f"climax ratio {qa['climax_ratio']}x", file=sys.stderr)
    if qa["score"] < 70 or not str(qa["status"]).startswith("pass"):
        for line in qa["details"]:
            print(f"  ! {line}")
        return 1
    if args.print_description:
        desc = dict(recipe.get("project_description", {}))
        desc["events"] = meta["events"]
        desc["qa"] = {k: qa[k] for k in ("score", "base", "dramaturgy", "status", "details")}
        print(json.dumps(desc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
