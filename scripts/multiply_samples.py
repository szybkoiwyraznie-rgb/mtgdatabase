#!/usr/bin/env python3
"""Inteligentna multiplikacja pojedynczych zdarzeń w samplach.

Część sampli zużywa czas nieoptymalnie: jedno krótkie zdarzenie (np. 0,1 s
krakania) i 2 s martwego powietrza. Tam, gdzie fabuła uzasadnia powtórzenie
(stado kruków, salwa trzech łuków, trójlufowy rewolwer), zamieniamy pojedyncze
uderzenie na serię 2-4 powtórzeń.

Kluczowe: powtórzenie NIE może brzmieć jak zapętlony sampel, więc każda kopia
dostaje własny mikro-charakter:

* varispeed (resampling) — zmienia jednocześnie wysokość i długość, tak jak
  przy dwóch różnych okrzykach tego samego zwierzęcia,
* własny poziom (dalsze/bliższe źródło),
* tilt barwy (łagodny filtr) — kopia „dalej od mikrofonu” jest ciemniejsza,
* mikro-panorama — źródła nie stoją w jednym punkcie,
* nierówne odstępy — rytm organiczny, nie metronomiczny.

Ogon oryginału (pogłos) zostaje pod całą serią, a końcowy mastering do
wspólnego celu LUFS robi sprawdzony łańcuch z postprocess_samples.py.

Użycie:
    python3 scripts/multiply_samples.py --plan data/samples/multiply-plan.json \
        --report data/samples/multiply-report.json [--dry-run] [--ids 1,304]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_samples_full import integrated_lufs, true_peak_dbtp  # noqa: E402
from postprocess_samples import process_one  # noqa: E402

EPS = 1e-12
SILENCE_DB = -45.0
FRAME_S = 0.01


def envelope_db(mono: np.ndarray, fs: int, frame_s: float = FRAME_S) -> np.ndarray:
    n = max(1, int(fs * frame_s))
    usable = (len(mono) // n) * n
    if usable == 0:
        return np.full(1, -120.0)
    frames = mono[:usable].reshape(-1, n)
    rms = np.sqrt((frames ** 2).mean(axis=1))
    return 20.0 * np.log10(np.maximum(rms, EPS))


def find_events(mono: np.ndarray, fs: int, *, sil_db: float = SILENCE_DB,
                merge_gap_s: float = 0.12) -> list[tuple[float, float]]:
    """Zwraca listę (start_s, end_s) zdarzeń ponad progiem ciszy."""
    db = envelope_db(mono, fs)
    active = db > sil_db
    regions: list[tuple[float, float]] = []
    i = 0
    while i < len(active):
        if not active[i]:
            i += 1
            continue
        last = i
        j = i
        while j < len(active):
            if active[j]:
                last = j
            elif (j - last) * FRAME_S > merge_gap_s:
                break
            j += 1
        regions.append((i * FRAME_S, (last + 1) * FRAME_S))
        i = last + 1
    return regions


def varispeed(seg: np.ndarray, ratio: float) -> np.ndarray:
    """Resampling liniowy: ratio > 1 = szybciej i wyżej."""
    if abs(ratio - 1.0) < 1e-6:
        return seg.copy()
    n_out = max(2, int(round(len(seg) / ratio)))
    src = np.linspace(0.0, len(seg) - 1, n_out)
    idx = np.arange(len(seg), dtype=float)
    return np.stack([np.interp(src, idx, seg[:, ch]) for ch in range(seg.shape[1])], axis=1)


def tilt(seg: np.ndarray, fs: int, cutoff_hz: float) -> np.ndarray:
    """Łagodne przyciemnienie kopii (LP 2. rzędu); 0 = bez zmian."""
    if not cutoff_hz:
        return seg
    nyq = fs / 2.0
    cutoff = min(max(cutoff_hz, 500.0), nyq * 0.98)
    sos = butter(2, cutoff / nyq, btype="low", output="sos")
    return sosfilt(sos, seg, axis=0)


def pan(seg: np.ndarray, amount: float) -> np.ndarray:
    """Mikro-panorama: amount w [-1, 1], realizowana jako różnica poziomów."""
    if seg.shape[1] < 2 or abs(amount) < 1e-6:
        return seg
    a = float(np.clip(amount, -1.0, 1.0))
    out = seg.copy()
    out[:, 0] *= 1.0 - max(0.0, a) * 0.45
    out[:, 1] *= 1.0 - max(0.0, -a) * 0.45
    return out


def fade(seg: np.ndarray, fs: int, in_s: float, out_s: float) -> np.ndarray:
    out = seg.copy()
    n_in = min(int(fs * in_s), len(out))
    n_out = min(int(fs * out_s), len(out))
    if n_in > 1:
        out[:n_in] *= np.linspace(0.0, 1.0, n_in)[:, None] ** 2
    if n_out > 1:
        out[len(out) - n_out:] *= np.linspace(1.0, 0.0, n_out)[:, None] ** 2
    return out


def db_to_lin(x: float) -> float:
    return float(10.0 ** (x / 20.0))


def build_multiplied(data: np.ndarray, fs: int, spec: dict) -> tuple[np.ndarray, dict]:
    """Składa serię powtórzeń pojedynczego zdarzenia."""
    mono = data.mean(axis=1)
    events = find_events(mono, fs)
    if not events:
        raise ValueError("nie znaleziono zdarzenia nad progiem ciszy")

    ev_idx = int(spec.get("source_event", 0))
    ev_start, ev_end = events[min(ev_idx, len(events) - 1)]

    pre_s = float(spec.get("preroll_s", 0.02))
    tail_s = float(spec.get("tail_s", 0.35))
    start = max(0, int((ev_start - pre_s) * fs))
    end = min(len(data), int((ev_end + tail_s) * fs))
    seg = data[start:end]
    seg = fade(seg, fs, 0.004, min(0.12, (end - start) / fs * 0.4))

    onsets = [float(x) for x in spec["onsets"]]
    gains = [float(x) for x in spec.get("gains_db", [0.0] * len(onsets))]
    speeds = [float(x) for x in spec.get("speeds", [1.0] * len(onsets))]
    tilts = [float(x) for x in spec.get("tilt_hz", [0.0] * len(onsets))]
    pans = [float(x) for x in spec.get("pan", [0.0] * len(onsets))]
    for name, seq in (("gains_db", gains), ("speeds", speeds),
                      ("tilt_hz", tilts), ("pan", pans)):
        if len(seq) != len(onsets):
            raise ValueError(f"{name}: oczekiwano {len(onsets)} wartości, jest {len(seq)}")

    total = len(data)
    out = np.zeros((total, data.shape[1]), dtype=float)
    tail_start = min(len(data), int((ev_end + tail_s) * fs))

    # tryb „wzbogacenie ogona”: cały oryginał zostaje nietknięty, a kopie
    # dokładamy wyłącznie w pustym ogonie (np. gruz opadający po uderzeniu).
    if spec.get("keep_original_head", False):
        out[:tail_start] += data[:tail_start]

    # ogon oryginału (pogłos/wybrzmienie po ostatnim zdarzeniu) zostaje w tle
    keep_tail = float(spec.get("keep_original_tail_db", -0.0))
    if spec.get("keep_original_tail", True):
        if tail_start < len(data):
            out[tail_start:] += data[tail_start:] * db_to_lin(keep_tail)

    placed = []
    for k, onset in enumerate(onsets):
        copy = varispeed(seg, speeds[k])
        copy = tilt(copy, fs, tilts[k])
        copy = pan(copy, pans[k])
        copy = copy * db_to_lin(gains[k])
        pos = int(onset * fs)
        if pos >= total:
            continue
        n = min(len(copy), total - pos)
        out[pos:pos + n] += copy[:n]
        placed.append({
            "onset_s": round(onset, 3),
            "gain_db": gains[k],
            "speed": speeds[k],
            "tilt_hz": tilts[k],
            "pan": pans[k],
            "len_s": round(len(copy) / fs, 3),
            "truncated": n < len(copy),
        })

    out = fade(out, fs, 0.003, 0.02)
    peak = float(np.max(np.abs(out)))
    if peak > 0.98:
        out *= 0.98 / peak

    info = {
        "source_event_s": [round(ev_start, 3), round(ev_end, 3)],
        "source_slice_s": round((end - start) / fs, 3),
        "copies": placed,
        "events_in_source": len(events),
    }
    return out, info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", default="data/samples/multiply-plan.json")
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--out-dir", default="", help="pusty = zapis w miejscu")
    ap.add_argument("--ids", default="", help="podzbiór ID po przecinku")
    ap.add_argument("--report", default="")
    ap.add_argument("--target-lufs", type=float, default=-20.0)
    ap.add_argument("--ceiling-dbtp", type=float, default=-1.0)
    ap.add_argument("--hp-hz", type=float, default=25.0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    entries = plan["samples"] if isinstance(plan, dict) else plan
    wanted = {s.strip() for s in args.ids.split(",") if s.strip()}
    if wanted:
        entries = [e for e in entries if str(e["id"]) in wanted]

    src_dir = Path(args.samples_dir)
    out_dir = Path(args.out_dir) if args.out_dir else src_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path("/tmp/multiply-stage")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for spec in entries:
        sid = str(spec["id"])
        src = src_dir / f"{sid}.mp3"
        if not src.exists():
            results.append({"id": sid, "status": "missing"})
            continue
        data, fs = sf.read(str(src), always_2d=True)
        before = {
            "lufs": integrated_lufs(data, fs),
            "true_peak_dbtp": true_peak_dbtp(data, fs),
            "duration_s": round(len(data) / fs, 3),
        }
        try:
            built, info = build_multiplied(data, fs, spec)
        except ValueError as exc:
            results.append({"id": sid, "status": "error", "error": str(exc)})
            continue

        stage = tmp_dir / f"{sid}.wav"
        sf.write(str(stage), built, fs, subtype="FLOAT")
        dst = out_dir / f"{sid}.mp3"
        master = process_one(stage, dst, target_lufs=args.target_lufs,
                             ceiling_db=args.ceiling_dbtp, max_gain_db=15.0,
                             hp_hz=args.hp_hz, dry_run=args.dry_run)

        row = {
            "id": sid,
            "status": "dry-run" if args.dry_run else "ok",
            "note": spec.get("note", ""),
            "repeats": len(spec["onsets"]),
            "before": before,
            "build": info,
            "master": {k: master.get(k) for k in
                       ("gain_db", "lufs_after", "true_peak_after_dbtp",
                        "limiter_gr_db", "limiter_gr_mean_db")},
        }
        results.append(row)
        print(f"{sid:>4} x{row['repeats']}  {before['lufs']:+.2f} -> "
              f"{master.get('lufs_after', float('nan')):+.2f} LUFS  "
              f"gain {master.get('gain_db')} dB  | {spec.get('note','')}")

    summary = {
        "generated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        "plan": args.plan,
        "dry_run": args.dry_run,
        "target_lufs": args.target_lufs,
        "count": len(results),
        "ok": sum(1 for r in results if r["status"] in {"ok", "dry-run"}),
        "samples": results,
    }
    if args.report:
        Path(args.report).write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nraport: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
