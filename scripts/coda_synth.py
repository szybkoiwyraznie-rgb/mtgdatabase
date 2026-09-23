"""Render muzycznego gestu (koda) na zatwierdzonym instrumencie.

Koda jest DEFINICJĄ nutową (docs/gate-protocol.md): absolutne numery MIDI,
czasy on/off i velocity. Instrument to mapa midi -> plik jednostkowy
(prawdziwe nagrania, np. VCSL/VSCO) albo zestaw artykulacji dla
instrumentów nietonowanych. Agent nie „komponuje" — wybiera gest z rejestru.

Deterministyczne: humanizacja (jitter timingu/velocity) jest ziarnicowana
seedem receptury, więc render jest powtarzalny.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

import sig_audio as dsp

MAX_SEMITONE_DISTANCE = 3  # instrument tonowany: najbliższa dostępna nuta w zasięgu ±3 półtony


@dataclass
class RenderedCoda:
    wave: np.ndarray  # stereo, zaczyna się w 0.0 s
    warnings: list[str]
    note_count: int


def _collect_used_midis(gesture: dict) -> list[int]:
    return sorted({int(n["midi"]) for n in gesture.get("notes", [])})


def resolve_samples(instrument: dict, midis: list[int]) -> tuple[dict[int, Path], list[str]]:
    """Dopasuj żądane nuty do dostępnych sampli instrumentu.

    Instrument tonowany: dokładny midi albo najbliższy w ±3 półtony.
    Instrument nietonowany (samples = {"articulations": {...}}): nuty
    odwzorowywane na artykulacje wg kolejności velocity (soft/mid/hard).
    """
    warnings: list[str] = []
    samples = instrument.get("samples", {})
    if "articulations" in samples:
        art = samples["articulations"]
        order = ["soft", "mid", "hard"]
        chosen: dict[int, Path] = {}
        for m in midis:
            vel_bucket = "mid"
            chosen[m] = Path(art[vel_bucket][0] if isinstance(art[vel_bucket], list) else art[vel_bucket])
        return chosen, warnings
    have = {int(k): v for k, v in samples.items() if str(k).isdigit()}
    missing = [m for m in midis if m not in have]
    resolved: dict[int, Path] = {}
    for m in midis:
        if m in have:
            resolved[m] = Path(have[m])
            continue
        near = min((c for c in have if abs(c - m) <= MAX_SEMITONE_DISTANCE), key=lambda c: abs(c - m), default=None)
        if near is None:
            warnings.append(f"brak nuty {dsp.midi_to_name(m)} ({m}) w ±{MAX_SEMITONE_DISTANCE} półtony — nuta pominięta")
        else:
            warnings.append(f"nuta {dsp.midi_to_name(m)} zastąpiona najbliższą {dsp.midi_to_name(near)}")
            resolved[m] = Path(have[near])
    return resolved, warnings


def render_coda(gesture: dict, instrument: dict, seed: int = 0, level_ref_db: float = -20.0) -> RenderedCoda:
    """Wyrenderuj gest na instrumencie. Zwraca waveform od 0.0 s.

    level_ref_db: docelowy RMS pojedynczej nuty przed skalowaniem velocity —
    względne proporcje velocity w gest zachowane.
    """
    warnings: list[str] = []
    midis = _collect_used_midis(gesture)
    if not midis:
        return RenderedCoda(np.zeros((2, 1)), ["gest nie ma nut"], 0)
    resolved, warn = resolve_samples(instrument, midis)
    warnings.extend(warn)
    delivery = gesture.get("delivery", {})
    humanize = delivery.get("humanize", {})
    timing_jitter = float(humanize.get("timing_ms", 0.0)) / 1000.0
    vel_jitter = float(humanize.get("vel", 0.0))
    rng = np.random.default_rng(seed)
    cache: dict[int, np.ndarray] = {}
    for m, path in resolved.items():
        wave, _ = dsp.load_any(path)
        cache[m] = dsp.normalize_rms(wave, level_ref_db)
    end_sec = max((float(n["off"]) + timing_jitter * 3) for n in gesture["notes"]) + 1.0
    out = np.zeros((2, int(end_sec * dsp.SR)))
    for note in sorted(gesture["notes"], key=lambda n: float(n["on"])):
        m = int(note["midi"])
        if m not in cache:
            continue
        wav = cache[m]
        slice_len = max(int((float(note["off"]) - float(note["on"])) * dsp.SR), 512)
        seg = wav[:, :slice_len] if wav.shape[1] > slice_len else wav
        if seg.shape[1] < slice_len:
            seg = np.hstack([seg, np.zeros((2, slice_len - seg.shape[1]))])
        # ucięcie nuty w połowie sustainu: łagodny zanik, żeby nie klikało
        seg = dsp.fade(seg, 0.005, min(0.35, seg.shape[1] / (2 * dsp.SR)))
        on = float(note["on"]) + (rng.uniform(-1, 1) * timing_jitter if timing_jitter else 0.0)
        vel = float(note.get("vel", 0.8))
        if vel_jitter:
            vel = float(np.clip(vel * (1.0 + rng.uniform(-vel_jitter, vel_jitter)), 0.05, 1.0))
        out = dsp.place(out, seg * vel, max(on, 0.0))
    return RenderedCoda(out, warnings, len(gesture["notes"]))


def main() -> None:  # szybkie demo: python coda_synth.py gesture.json instrument.json out.mp3
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("gesture", type=Path)
    parser.add_argument("instrument", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    gesture = json.loads(args.gesture.read_text(encoding="utf-8"))
    instrument = json.loads(args.instrument.read_text(encoding="utf-8"))
    result = render_coda(gesture, instrument, seed=args.seed)
    for warning in result.warnings:
        print(f"! {warning}")
    dsp.encode_mp3(args.out, dsp.peak_ceiling(result.wave, 0.9))
    print(f"zapisano {args.out} ({result.note_count} nut)")


if __name__ == "__main__":
    main()
