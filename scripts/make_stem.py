#!/usr/bin/env python3
"""Cut a production stem (MP3, 44.1 kHz stereo) from any source recording.

Automates the verified sample procedure from docs/sources-and-licensing.md:
decode (PyAV for M4A/AAC, soundfile otherwise), trim to a window, apply short
fades, resample to the engine rate and encode a stem for
legacy/source/game-audio-pipeline/stems/. Register the result in
data/sources.json before using it in a recipe (AGENTS.md #8).

Authoring tool (not CI): `pip install numpy soundfile lameenc av` in the venv.

Usage:
  python scripts/make_stem.py "<source file>" --start 12.5 --end 18.5 \
      --out legacy/source/game-audio-pipeline/stems/wolf_howl.mp3 \
      [--gain-db -3] [--fade-ms 60] [--mono]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

SR = 44_100


def load_any(path: Path) -> tuple[np.ndarray, int]:
    """Return (samples[:, channels], samplerate) for MP3/WAV/M4A/FLAC..."""
    import soundfile as sf

    try:
        data, sr = sf.read(str(path), always_2d=True)
        return data.astype(np.float64), sr
    except Exception:
        pass  # AAC/M4A and friends: decode with PyAV
    import av

    container = av.open(str(path))
    frames = []
    sr = None
    for frame in container.decode(audio=0):
        array = frame.to_ndarray().astype(np.float64)
        if array.ndim == 2 and array.shape[0] <= 8:  # planar layout
            array = array.T
        frames.append(array)
        sr = frame.rate
    return np.concatenate(frames), sr


def resample_linear(data: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return data
    n_out = int(round(len(data) * sr_out / sr_in))
    old_t = np.linspace(0.0, 1.0, len(data), endpoint=False)
    new_t = np.linspace(0.0, 1.0, n_out, endpoint=False)
    if data.ndim == 1:
        return np.interp(new_t, old_t, data)[:, None]
    return np.column_stack([np.interp(new_t, old_t, data[:, ch]) for ch in range(data.shape[1])])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("--start", type=float, required=True, help="window start (seconds)")
    parser.add_argument("--end", type=float, required=True, help="window end (seconds)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--gain-db", type=float, default=0.0)
    parser.add_argument("--fade-ms", type=int, default=60)
    parser.add_argument("--mono", action="store_true", help="downmix to mono (dual-mono stereo file)")
    args = parser.parse_args()

    data, sr = load_any(args.source)
    a, b = int(args.start * sr), int(args.end * sr)
    if not (0 <= a < b <= len(data)):
        raise SystemExit(f"okno {args.start}-{args.end}s poza zakresem pliku (0-{len(data)/sr:.2f}s)")
    seg = data[a:b].copy()
    if args.mono and seg.shape[1] > 1:
        seg = seg.mean(axis=1)[:, None]
        seg = np.repeat(seg, 2, axis=1)
    seg = resample_linear(seg, sr, SR)
    fade = max(1, int(args.fade_ms / 1000 * SR))
    seg[:fade] *= np.linspace(0.0, 1.0, fade)[:, None]
    seg[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    seg *= 10 ** (args.gain_db / 20.0)
    peak = np.max(np.abs(seg)) + 1e-9
    if peak > 0.99:
        seg *= 0.99 / peak

    import lameenc

    pcm = (np.clip(seg, -1.0, 1.0) * 32767.0).astype(np.int16)
    enc = lameenc.Encoder()
    enc.set_bit_rate(128)
    enc.set_in_sample_rate(SR)
    enc.set_channels(seg.shape[1])
    enc.set_quality(2)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(enc.encode(pcm.tobytes()) + enc.flush())

    rms = float(np.sqrt(np.mean(seg ** 2)))
    print(f"Stem zapisany: {args.out} ({args.out.stat().st_size} B, "
          f"{len(seg)/SR:.2f}s, {seg.shape[1]} kanały, peak {np.max(np.abs(seg)):.3f}, RMS {rms:.4f})")
    print("Przypomnienie: zarejestruj sample w data/sources.json (AGENTS.md #8).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
