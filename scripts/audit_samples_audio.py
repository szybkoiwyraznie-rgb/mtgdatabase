#!/usr/bin/env python3
"""Sygnałowy audyt sampli audio/samples/*.mp3.

Dla każdego pliku liczy metryki i typuje podejrzane:
- ucięty start / ucięty koniec (energia obwiedni tuż przy krawędzi pliku),
- za cicho / za głośno (peak, aktywny RMS, odchylenie od korpusu),
- przester (odsetek sampli przy pełnej skali),
- rozjazd czasu trwania względem scenariusza,
- pliki (prawie) całkiem ciche.

Tylko raportuje — niczego nie zmienia i nie regeneruje.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

EPS = 1e-12


def db(x: float) -> float:
    return 20.0 * math.log10(max(x, EPS))


def frame_rms_db(mono: np.ndarray, sr: int, frame_ms: float = 10.0) -> np.ndarray:
    n = max(1, int(sr * frame_ms / 1000.0))
    usable = len(mono) - (len(mono) % n)
    if usable <= 0:
        return np.array([db(float(np.sqrt(np.mean(mono**2))))])
    frames = mono[:usable].reshape(-1, n)
    rms = np.sqrt(np.mean(frames**2, axis=1))
    return 20.0 * np.log10(np.maximum(rms, EPS))


def segment_rms_db(mono: np.ndarray, sr: int, start_s: float, end_s: float) -> float:
    a = max(0, int(start_s * sr))
    b = min(len(mono), int(end_s * sr))
    if b <= a:
        return db(0.0)
    seg = mono[a:b]
    return db(float(np.sqrt(np.mean(seg**2))))


def analyze(path: Path, expected_duration: float | None) -> dict:
    data, sr = sf.read(str(path), always_2d=True)
    mono = data.mean(axis=1)
    dur = len(mono) / sr

    peak = float(np.max(np.abs(data))) if data.size else 0.0
    peak_db = db(peak)
    clip_frac = float(np.mean(np.abs(data) >= 0.999)) if data.size else 0.0

    frames = frame_rms_db(mono, sr, 10.0)
    max_frame_db = float(np.max(frames))
    # aktywny RMS: tylko ramki > -45 dBFS (pomija ciszę)
    active = frames[frames > -45.0]
    active_rms_db = float(np.mean(active)) if active.size else -120.0
    overall_rms_db = db(float(np.sqrt(np.mean(mono**2))))

    # cisza wiodąca / końcowa (próg -45 dBFS, ramki 10 ms)
    thr = -45.0
    above = np.nonzero(frames > thr)[0]
    if above.size:
        lead_sil = above[0] * 0.010
        trail_sil = (len(frames) - 1 - above[-1]) * 0.010
    else:
        lead_sil = trail_sil = dur

    # energia tuż przy krawędziach pliku
    start_15ms = segment_rms_db(mono, sr, 0.0, 0.015)
    start_50ms = segment_rms_db(mono, sr, 0.0, 0.050)
    end_10ms = segment_rms_db(mono, sr, dur - 0.010, dur)
    end_30ms = segment_rms_db(mono, sr, dur - 0.030, dur)
    end_100ms = segment_rms_db(mono, sr, dur - 0.100, dur)

    return {
        "file": path.name,
        "duration_s": round(dur, 3),
        "expected_s": expected_duration,
        "sr": sr,
        "peak_db": round(peak_db, 2),
        "clip_frac": round(clip_frac, 6),
        "overall_rms_db": round(overall_rms_db, 2),
        "active_rms_db": round(active_rms_db, 2),
        "max_frame_db": round(max_frame_db, 2),
        "lead_silence_s": round(lead_sil, 3),
        "trail_silence_s": round(trail_sil, 3),
        "start_15ms_db": round(start_15ms, 2),
        "start_50ms_db": round(start_50ms, 2),
        "end_10ms_db": round(end_10ms, 2),
        "end_30ms_db": round(end_30ms, 2),
        "end_100ms_db": round(end_100ms, 2),
    }


def flag(metrics: list[dict]) -> None:
    act = np.array([m["active_rms_db"] for m in metrics])
    mean, std = float(np.mean(act)), float(np.std(act))
    for m in metrics:
        flags = []
        # Uwaga kalibracyjna: sample'e SFX z natury startują szybko (mediana
        # energii w pierwszych 15 ms w korpusie to ok. -32 dBFS), więc "szybki
        # atak" NIE jest wadą. Flagujemy tylko start od razu na pełnym
        # poziomie pliku — to brzmi jak wejście w środek dźwięku.
        if m["start_15ms_db"] > -12.0 and m["start_15ms_db"] > m["max_frame_db"] - 4.0:
            flags.append("cut_start_hard")
        # ucięty koniec: plik kończy się na wysokim poziomie, bez wybrzmienia
        if m["end_10ms_db"] > -30.0 or m["end_10ms_db"] > m["max_frame_db"] - 15.0:
            flags.append("cut_end_hard")
        elif m["end_30ms_db"] > -32.0 and m["end_30ms_db"] > m["max_frame_db"] - 20.0:
            flags.append("cut_end_soft")
        # głośność
        if m["peak_db"] < -18.0 or m["active_rms_db"] < mean - 2.5 * std:
            flags.append("too_quiet")
        if m["clip_frac"] > 0.0005:
            flags.append("clipping")
        elif m["active_rms_db"] > mean + 2.5 * std and m["peak_db"] > -1.0:
            flags.append("too_loud")
        # prawie cisza
        if m["max_frame_db"] < -40.0:
            flags.append("near_silent")
        # rozjazd czasu trwania (MP3 dodaje ~25-50 ms paddingu)
        if m["expected_s"] is not None and abs(m["duration_s"] - m["expected_s"]) > 0.20:
            flags.append("duration_mismatch")
        # nietypowo dużo ciszy (w samplach 2-3 s to zauważalna strata treści)
        if m["lead_silence_s"] > 0.6:
            flags.append("long_lead_silence")
        if m["trail_silence_s"] > 1.5:
            flags.append("long_trail_silence")
        m["flags"] = flags
    stats = {"active_rms_mean_db": round(mean, 2), "active_rms_std_db": round(std, 2)}
    metrics.append({"_corpus_stats": stats})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--scenarios", default="data/samples/scenarios.jsonl")
    ap.add_argument("--output", default="/tmp/audio-audit.json")
    args = ap.parse_args()

    expected: dict[str, float] = {}
    for line in Path(args.scenarios).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            row = json.loads(line)
            expected[str(row["story_id"])] = float(row.get("duration_seconds") or 0) or None

    files = sorted(Path(args.samples_dir).glob("*.mp3"), key=lambda p: int(p.stem))
    metrics = []
    for p in files:
        try:
            metrics.append(analyze(p, expected.get(p.stem)))
        except Exception as exc:  # noqa: BLE001
            metrics.append({"file": p.name, "error": str(exc), "flags": ["decode_error"]})
    ok = [m for m in metrics if "error" not in m]
    flag(ok)
    Path(args.output).write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    n_flagged = sum(1 for m in metrics if m.get("flags"))
    print(f"analyzed {len(files)} files, flagged {n_flagged}, report: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
