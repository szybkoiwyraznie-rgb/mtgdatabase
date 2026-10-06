#!/usr/bin/env python3
"""Wprowadza centroid widma do zadanego okna — tnie ALBO podbija, mierząc efekt.

Po co: `tame_harsh.py` celuje w progi flagi `harsh` (centroid 9000 Hz / air8k 0,50)
i tylko tnie. Tymczasem kontrakty archetypów mają OKNA, np. `mechanism_click`
i `arrow_flight` 800–6000 Hz, `insect_swarm` 1000–6000 Hz — więc część kart jest
za jasna, a część za ciemna. W korpusie zdarzają się oba przypadki:
`52` centroid 7588 Hz (za jasno) i `610` centroid 163 Hz (za ciemno, po tym jak
prompt „low dull wooden knocks" przesterował w drugą stronę).

Pętla: mierzy centroid funkcjami audytu, dokłada krok półki w odpowiednią stronę
i mierzy znowu, aż trafi w okno albo dojdzie do sufitu łącznej korekty. Po drodze
renormalizacja głośności przez `limit_true_peak` (korekta widma zmienia mierzoną
głośność) i warunkowy fade-in, jeśli plik startuje od pełnego poziomu.

To postprodukcja, więc stosować ostrożnie na kartach z kontraktem: korekta widma
zmienia też `spectral_flatness` i `tonal_frame_fraction`. Po każdym użyciu trzeba
przepuścić `audit_archetype_match.py` i cofnąć karty, które straciły.

Użycie:
    python scripts/tame_spectrum.py --ids 52,132 --centroid-max 6000
    python scripts/tame_spectrum.py --ids 610 --centroid-min 800 --centroid-max 6000 --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_samples_full import (CUT_START_DB,  # noqa: E402
                                CUT_START_MARGIN, frame_rms_db,
                                integrated_lufs, segment_rms_db,
                                spectral_profile)
from postprocess_samples import biquad_high_shelf, limit_true_peak  # noqa: E402


def measure(data: np.ndarray, fs: int) -> dict:
    mono = data.mean(axis=1) if data.ndim > 1 else data
    spec = spectral_profile(mono, fs)
    return {"centroid": float(spec["spectral_centroid_hz"]),
            "air8k": float(spec["bands"]["air_8k_plus"]),
            "flatness": float(spec["spectral_flatness"])}


def tune(path: Path, *, cmin: float, cmax: float, step_db: float, max_db: float,
         shelf_hz: float, target_lufs: float, ceiling_db: float,
         out_path: Path | None = None) -> dict:
    data, fs = sf.read(str(path), always_2d=True)
    out = data.astype(np.float64).copy()
    m0 = measure(out, fs)
    total = 0.0
    steps = 0
    m = m0
    while (m["centroid"] > cmax or m["centroid"] < cmin) and abs(total) < max_db:
        gain = -step_db if m["centroid"] > cmax else step_db
        out = biquad_high_shelf(out, fs, fc=shelf_hz, gain_db=gain)
        total += gain
        steps += 1
        m = measure(out, fs)

    # korekta widma zmienia mierzona glosnosc -> renormalizacja + limiter
    for _ in range(2):
        cur = integrated_lufs(out, fs)
        if np.isfinite(cur):
            out *= 10.0 ** ((target_lufs - cur) / 20.0)
        out, _pk, _gr = limit_true_peak(out, fs, ceiling_db=ceiling_db)

    # cisza/brak wysokich obniza glosnosc, wiec renormalizacja podnosi transjent
    mono_chk = out.mean(axis=1)
    start_db = segment_rms_db(mono_chk, fs, 0.0, 0.015)
    max_frame = float(np.max(frame_rms_db(mono_chk, fs, 10.0)))
    fade = False
    if start_db > CUT_START_DB and start_db > max_frame - CUT_START_MARGIN:
        n = max(1, int(0.012 * fs))
        out[:n] *= np.linspace(0.0, 1.0, n)[:, None]
        fade = True

    m1 = measure(out, fs)
    result = {
        "id": int(path.stem) if path.stem.isdigit() else path.stem,
        "correction_db": round(total, 1),
        "steps": steps,
        "centroid_before": round(m0["centroid"], 1),
        "centroid_after": round(m1["centroid"], 1),
        "flatness_before": round(m0["flatness"], 4),
        "flatness_after": round(m1["flatness"], 4),
        "in_window": bool(cmin <= m1["centroid"] <= cmax),
        "start_fade_applied": fade,
        "lufs_after": round(float(integrated_lufs(out, fs)), 2),
    }
    if out_path is not None:
        tmp = out_path.with_suffix(".tmp.mp3")
        sf.write(str(tmp), out.astype(np.float32), fs, format="MP3",
                 subtype="MPEG_LAYER_III")
        tmp.replace(out_path)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--centroid-min", type=float, default=0.0)
    ap.add_argument("--centroid-max", type=float, default=1e9)
    ap.add_argument("--step-db", type=float, default=3.0,
                    help="wysokość jednego kroku półki (domyślnie 3 dB)")
    ap.add_argument("--max-db", type=float, default=24.0,
                    help="sufit łącznej korekty w jedną stronę (domyślnie 24 dB)")
    ap.add_argument("--shelf-hz", type=float, default=3500.0)
    ap.add_argument("--target-lufs", type=float, default=-20.0)
    ap.add_argument("--ceiling-db", type=float, default=-1.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report")
    args = ap.parse_args()

    src = Path(args.samples_dir)
    rows = []
    for sid in [i.strip() for i in args.ids.split(",") if i.strip()]:
        p = src / ("%s.mp3" % sid)
        if not p.exists():
            rows.append({"id": int(sid), "skipped": "brak pliku"})
            continue
        rows.append(tune(p, cmin=args.centroid_min, cmax=args.centroid_max,
                         step_db=args.step_db, max_db=args.max_db,
                         shelf_hz=args.shelf_hz, target_lufs=args.target_lufs,
                         ceiling_db=args.ceiling_db,
                         out_path=p if (args.apply and not args.dry_run) else None))

    for r in rows:
        if "skipped" in r:
            print("%5s  POMINIETY: %s" % (r["id"], r["skipped"]))
            continue
        print("%5s  korekta %+5.1f dB (%d krokow)  centroid %7.0f -> %-7.0f  "
              "flatness %.3f -> %.3f  %s"
              % (r["id"], r["correction_db"], r["steps"], r["centroid_before"],
                 r["centroid_after"], r["flatness_before"], r["flatness_after"],
                 "W OKNIE" if r["in_window"] else "POZA OKNEM"))
    ok = [r for r in rows if "in_window" in r]
    if ok:
        print("razem %d | w oknie: %d | srednia korekta %+.1f dB%s"
              % (len(ok), sum(1 for r in ok if r["in_window"]),
                 sum(r["correction_db"] for r in ok) / len(ok),
                 "" if (args.apply and not args.dry_run) else "  (dry-run)"))
    if args.report:
        Path(args.report).write_text(json.dumps(
            {"centroid_min": args.centroid_min, "centroid_max": args.centroid_max,
             "shelf_hz": args.shelf_hz, "step_db": args.step_db,
             "applied": bool(args.apply and not args.dry_run), "files": rows},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print("raport:", args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
