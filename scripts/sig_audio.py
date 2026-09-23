"""Rdzeń DSP systemu sygnatur dźwiękowych (docs/signature-system.md).

Współdzielony przez render_signature.py, coda_synth.py i narzędzia bramkowe.
Zasady: 44,1 kHz stereo, float64 w środku, MP3 na wyjściu, deterministiczność.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

SR = 44_100
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def load_any(path: Path | str) -> tuple[np.ndarray, int]:
    """Wczytaj audio (MP3/WAV/M4A/FLAC) jako (float64[kanały, próbki], sr)."""
    path = Path(path)
    import soundfile as sf

    try:
        data, sr = sf.read(str(path), always_2d=True)
        data = data.astype(np.float64)
    except Exception:
        import av

        container = av.open(str(path))
        frames: list[np.ndarray] = []
        sr = None
        for frame in container.decode(audio=0):
            array = frame.to_ndarray().astype(np.float64)
            if array.ndim == 1:
                array = array[None, :]
            elif array.shape[0] <= 8:
                array = array.T
            frames.append(array.T)
            sr = frame.rate
        data = np.concatenate(frames, axis=1)
    if data.ndim == 2 and data.shape[0] > data.shape[1]:
        data = data.T
    if data.ndim == 1:
        data = data[None, :]
    if sr != SR:
        data = resample_linear(data, int(sr), SR)
        sr = SR
    if data.shape[0] == 1:
        data = np.vstack([data, data])
    return data, int(sr)


def resample_linear(data: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return data
    n_out = int(round(data.shape[1] * sr_out / sr_in))
    old_t = np.linspace(0.0, 1.0, data.shape[1], endpoint=False)
    new_t = np.linspace(0.0, 1.0, n_out, endpoint=False)
    return np.stack([np.interp(new_t, old_t, ch) for ch in data])


def rms_db(x: np.ndarray) -> float:
    if x.size == 0:
        return -120.0
    return float(20.0 * np.log10(float(np.sqrt(np.mean(x**2))) + 1e-9))


def db_to_gain(db: float) -> float:
    return float(10.0 ** (db / 20.0))


def normalize_rms(x: np.ndarray, target_db: float) -> np.ndarray:
    return x * db_to_gain(target_db - rms_db(x))


def fade(x: np.ndarray, fade_in_sec: float, fade_out_sec: float) -> np.ndarray:
    y = x.copy()
    n_in = min(int(fade_in_sec * SR), y.shape[1])
    n_out = min(int(fade_out_sec * SR), y.shape[1])
    if n_in > 1:
        y[:, :n_in] *= np.linspace(0.0, 1.0, n_in)
    if n_out > 1:
        y[:, -n_out:] *= np.linspace(1.0, 0.0, n_out)
    return y


def cut(x: np.ndarray, start_sec: float, end_sec: float) -> np.ndarray:
    s = int(start_sec * SR)
    e = min(int(end_sec * SR), x.shape[1])
    return x[:, s:e]


def place(timeline: np.ndarray, seg: np.ndarray, at_sec: float) -> np.ndarray:
    """Umieść seg na timeline (dopisując próbki). Zwraca timeline."""
    at = int(at_sec * SR)
    need = at + seg.shape[1]
    if need > timeline.shape[1]:
        timeline = np.hstack([timeline, np.zeros((2, need - timeline.shape[1]))])
    timeline[:, at:need] += seg
    return timeline


def peak_ceiling(mix: np.ndarray, ceiling: float = 0.92) -> np.ndarray:
    peak = float(np.max(np.abs(mix))) if mix.size else 0.0
    if peak > ceiling:
        mix = mix * (ceiling / peak)
    return mix


def minutes_of(x: np.ndarray) -> float:
    return x.shape[1] / SR


def encode_mp3(path: Path | str, mix: np.ndarray, bitrate: int = 192) -> None:
    import lameenc

    pcm = np.clip(mix, -1.0, 1.0)
    pcm16 = (pcm * 32767.0).astype(np.int16)
    interleaved = np.stack([pcm16[0], pcm16[1]], axis=1).tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(bitrate)
    enc.set_in_sample_rate(SR)
    enc.set_channels(2)
    enc.set_quality(2)
    data = enc.encode(interleaved) + enc.flush()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(data)


def spectral_share(x: np.ndarray, hz: float = 6000.0) -> float:
    """Udział energii powyżej hz w widmie (0..1) — ochrona przed 'papierem'."""
    mono = x.mean(axis=0)
    spec = np.abs(np.fft.rfft(mono)) ** 2
    freqs = np.fft.rfftfreq(len(mono), 1.0 / SR)
    total = float(spec.sum())
    if total <= 0:
        return 0.0
    return float(spec[freqs >= hz].sum() / total)


def window_rms_db(x: np.ndarray, at_sec: float, length_sec: float) -> float:
    return rms_db(cut(x, at_sec, at_sec + length_sec))


def midi_from_token(token: str) -> int:
    """'A#2'/'F2'/'C4' -> numer MIDI (C4 = 60)."""
    token = token.strip().replace("b", "#")
    name = token[:-1].upper()
    octave = int(token[-1])
    if name not in NOTE_NAMES:
        raise ValueError(f"nieznana nuta: {token!r}")
    return NOTE_NAMES.index(name) + (octave + 1) * 12


def midi_to_name(midi: int) -> str:
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"
