#!/usr/bin/env python3
"""Zdejmuje syk z plików flagowanych `harsh`, mierząc efekt zamiast strzelać stałą.

Flaga `harsh` w audycie to `spectral_centroid_hz > 9000 Hz` ORAZ udział energii
powyżej 8 kHz > 0,50. W praktyce te pliki mają 0,85-0,95 energii nad 8 kHz, czyli
są zdominowane przez syk — niezależnie od tego, czy karta jest jasna z natury
(dzwonek, iskra), czy powinna być niska (ciężkie kroki, kruszenie kamienia).

`postprocess_samples.py --fix-spectral` tnie −3,5 dB przy 4,5 kHz (Q 1,2), co przy
centroidzie 9-12 kHz nie zmienia nic: sprawdzone na 23 plikach, flaga została na
wszystkich. Dlatego półka jest tu dobrana iteracyjnie: tniemy, mierzymy widmo z
audytu i dokładamy, aż zejdziemy pod próg albo dojdziemy do sufitu cięcia.

Użycie:
    python scripts/tame_harsh.py --ids 93,437 --dry-run
    python scripts/tame_harsh.py --ids 93,437 --apply
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
                                CUT_START_MARGIN, HARSH_AIR_SHARE_MIN,
                                HARSH_CENTROID_MIN, frame_rms_db,
                                integrated_lufs, segment_rms_db,
                                spectral_profile)
from postprocess_samples import biquad_high_shelf, limit_true_peak  # noqa: E402


def measure(data: np.ndarray, fs: int) -> tuple[float, float]:
    mono = data.mean(axis=1) if data.ndim > 1 else data
    spec = spectral_profile(mono, fs)
    return float(spec["spectral_centroid_hz"]), float(spec["bands"]["air_8k_plus"])


def tame(path: Path, *, step_db: float, max_cut_db: float, shelf_hz: float,
         target_lufs: float, ceiling_db: float, out_path: Path | None = None) -> dict:
    data, fs = sf.read(str(path), always_2d=True)
    out = data.astype(np.float64).copy()
    c0, a0 = measure(out, fs)
    cut = 0.0
    steps = 0
    centroid, air = c0, a0
    while (centroid > HARSH_CENTROID_MIN or air > HARSH_AIR_SHARE_MIN) and cut > -max_cut_db:
        out = biquad_high_shelf(out, fs, fc=shelf_hz, gain_db=step_db)
        cut += step_db
        steps += 1
        centroid, air = measure(out, fs)

    # renormalizacja: cięcie góry obniza glosnosc, a korpus trzyma -20 LUFS
    for _ in range(2):
        cur = integrated_lufs(out, fs)
        if np.isfinite(cur):
            out *= 10.0 ** ((target_lufs - cur) / 20.0)
        out, _pk, _mean = limit_true_peak(out, fs, ceiling_db=ceiling_db)

    # Ciecie gory obniza mierzona glosnosc, wiec renormalizacja do -20 LUFS
    # podnosi transjent i plik startujacy od pelnego poziomu lapie
    # cut_start_hard (ten sam mechanizm co w add_reverb_tail.py).
    mono_chk = out.mean(axis=1)
    start_db = segment_rms_db(mono_chk, fs, 0.0, 0.015)
    max_frame = float(np.max(frame_rms_db(mono_chk, fs, 10.0)))
    if start_db > CUT_START_DB and start_db > max_frame - CUT_START_MARGIN:
        n = max(1, int(0.012 * fs))
        out[:n] *= np.linspace(0.0, 1.0, n)[:, None]
        result_fade = True
    else:
        result_fade = False

    c1, a1 = measure(out, fs)
    result = {
        "id": int(path.stem) if path.stem.isdigit() else path.stem,
        "cut_db": round(cut, 1),
        "steps": steps,
        "centroid_before": round(c0, 1),
        "centroid_after": round(c1, 1),
        "air8k_before": round(a0, 4),
        "air8k_after": round(a1, 4),
        "cleared": bool(c1 <= HARSH_CENTROID_MIN or a1 <= HARSH_AIR_SHARE_MIN),
        "lufs_after": round(float(integrated_lufs(out, fs)), 2),
        "start_fade_applied": result_fade,
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
    ap.add_argument("--step-db", type=float, default=-3.0,
                    help="krok półki wysokotonowej (domyślnie -3 dB)")
    ap.add_argument("--max-cut-db", type=float, default=18.0,
                    help="sufit łącznego cięcia (domyślnie 18 dB)")
    ap.add_argument("--shelf-hz", type=float, default=6000.0,
                    help="częstotliwość półki (domyślnie 6 kHz)")
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
        rows.append(tame(p, step_db=args.step_db, max_cut_db=args.max_cut_db,
                         shelf_hz=args.shelf_hz, target_lufs=args.target_lufs,
                         ceiling_db=args.ceiling_db,
                         out_path=p if (args.apply and not args.dry_run) else None))

    for r in rows:
        if "skipped" in r:
            print("%5s  POMINIECY: %s" % (r["id"], r["skipped"]))
            continue
        print("%5s  ciecie %5.1f dB (%d krokow)  centroid %6.0f -> %-6.0f  "
              "air8k %.3f -> %.3f  %s"
              % (r["id"], r["cut_db"], r["steps"], r["centroid_before"],
                 r["centroid_after"], r["air8k_before"], r["air8k_after"],
                 "OK" if r["cleared"] else "NADAL HARSH"))
    ok = [r for r in rows if "cleared" in r]
    if ok:
        print("razem %d | zdejeta flaga: %d | srednie ciecie %.1f dB%s"
              % (len(ok), sum(1 for r in ok if r["cleared"]),
                 sum(r["cut_db"] for r in ok) / len(ok),
                 "" if (args.apply and not args.dry_run) else "  (dry-run)"))
    if args.report:
        Path(args.report).write_text(json.dumps(
            {"shelf_hz": args.shelf_hz, "step_db": args.step_db,
             "max_cut_db": args.max_cut_db,
             "applied": bool(args.apply and not args.dry_run), "files": rows},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print("raport:", args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
