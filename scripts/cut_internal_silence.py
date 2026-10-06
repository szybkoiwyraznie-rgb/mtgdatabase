#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wycina dziury ciszy w ŚRODKU sample'a, zostawiając krótki crossfade.

Po co: audyt archetypów mierzy `attack_s` jako czas od pierwszego dźwięku do
głównego uderzenia. Jeśli model wygenerował „krzyk, pauza, trzepot skrzydeł",
to przerwa w środku rozbija sample na dwa zdarzenia i `attack_s` wychodzi duży
mimo że sam atak jest natychmiastowy. Zmierzony przypadek: karta `269`
(Scouting Hawk) — krzyk 0,0–0,4 s, cisza 0,6–1,0 s (−47…−54 dB), trzepot od 1,0 s,
`attack_s` 1,15 s przy wymaganym ≤ 0,15 dla `beast_screech`.

To montaż, nie generacja, więc kosztuje zero kredytów. Nie dopisuje ciszy
(zakaz właściciela) — odwrotnie, usuwa jej nadmiar ze środka.

Zasady:
- szuka regionów ciszy dłuższych niż `--min-gap-s` i cichszych niż `--floor-db`
  względem RMS całego pliku,
- ZAWSZE zostawia `--keep-s` ciszy w miejscu cięcia, żeby nie skleić dwóch
  zdarzeń w nienaturalny sposób,
- crossfade `--xfade-ms`, żeby nie było kliku na łączeniu,
- na koniec renormalizacja głośności i limiter, bo usunięcie ciszy zmienia
  mierzoną głośność całkowaną.

Użycie:
    python scripts/cut_internal_silence.py --ids 269 --dry-run
    python scripts/cut_internal_silence.py --ids 269 --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_samples_full import (frame_rms_db, integrated_lufs,  # noqa: E402
                                segment_rms_db)
from postprocess_samples import limit_true_peak  # noqa: E402


def find_gaps(mono: np.ndarray, fs: int, *, floor_db: float, min_gap_s: float,
              ref_db: float) -> list[tuple[int, int]]:
    """Zwraca listę (start, end) w próbkach — regiony ciszy w środku pliku."""
    win = max(1, int(0.02 * fs))
    n = len(mono) // win
    rms = np.array([20.0 * np.log10(np.sqrt(np.mean(mono[i * win:(i + 1) * win] ** 2)) + 1e-12)
                    for i in range(n)])
    quiet = rms < (ref_db + floor_db)
    gaps: list[tuple[int, int]] = []
    i = 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * win / fs >= min_gap_s and i > 0 and j < n:
                gaps.append((i * win, j * win))
            i = j
        else:
            i += 1
    return gaps


def cut(path: Path, *, floor_db: float, min_gap_s: float, keep_s: float,
        xfade_ms: float, target_lufs: float, ceiling_db: float,
        out_path: Path | None = None) -> dict:
    data, fs = sf.read(str(path), always_2d=True)
    x = data.astype(np.float64)
    mono = x.mean(axis=1)
    ref = 20.0 * np.log10(np.sqrt(np.mean(mono ** 2)) + 1e-12)
    gaps = find_gaps(mono, fs, floor_db=floor_db, min_gap_s=min_gap_s, ref_db=ref)

    keep = int(keep_s * fs)
    xf = max(1, int(xfade_ms / 1000.0 * fs))
    pieces = []
    pos = 0
    removed = 0.0
    for (a, b) in gaps:
        end = min(a + keep, b)
        pieces.append(x[pos:end])
        removed += (b - end) / fs
        pos = b - keep if b - keep > end else b
    pieces.append(x[pos:])

    if len(pieces) == 1:
        return {"id": int(path.stem) if path.stem.isdigit() else path.stem,
                "gaps": len(gaps), "removed_s": 0.0, "unchanged": True}

    # crossfade na kazdym laczeniu
    out = pieces[0]
    for nxt in pieces[1:]:
        k = min(xf, len(out), len(nxt))
        ramp = np.linspace(0.0, 1.0, k)[:, None]
        head = out[:-k] if k < len(out) else out[:0]
        seam = out[-k:] * (1.0 - ramp) + nxt[:k] * ramp
        out = np.concatenate([head, seam, nxt[k:]])

    for _ in range(2):
        cur = integrated_lufs(out, fs)
        if np.isfinite(cur):
            out *= 10.0 ** ((target_lufs - cur) / 20.0)
        out, _pk, _gr = limit_true_peak(out, fs, ceiling_db=ceiling_db)

    # jesli po cieciu plik startuje od pelnego poziomu, 12 ms fade-in przeciw klikowi
    mono_chk = out.mean(axis=1)
    start_db = segment_rms_db(mono_chk, fs, 0.0, 0.015)
    max_frame = float(np.max(frame_rms_db(mono_chk, fs, 10.0)))
    fade = False
    if start_db > -12.0 and start_db > max_frame - 6.0:
        n = max(1, int(0.012 * fs))
        out[:n] *= np.linspace(0.0, 1.0, n)[:, None]
        fade = True

    res = {"id": int(path.stem) if path.stem.isdigit() else path.stem,
           "gaps": len(gaps), "removed_s": round(removed, 2),
           "duration_before_s": round(len(mono) / fs, 2),
           "duration_after_s": round(len(out) / fs, 2),
           "start_fade_applied": fade,
           "lufs_after": round(float(integrated_lufs(out, fs)), 2)}
    if out_path is not None:
        tmp = out_path.with_suffix(".tmp.mp3")
        sf.write(str(tmp), out.astype(np.float32), fs, format="MP3",
                 subtype="MPEG_LAYER_III")
        tmp.replace(out_path)
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--floor-db", type=float, default=-25.0,
                    help="próg ciszy względem RMS całego pliku (domyślnie −25 dB)")
    ap.add_argument("--min-gap-s", type=float, default=0.25,
                    help="minimalna długość dziury, żeby ją ciąć (domyślnie 0,25 s)")
    ap.add_argument("--keep-s", type=float, default=0.04,
                    help="ile ciszy zostaje w miejscu cięcia (domyślnie 0,04 s)")
    ap.add_argument("--xfade-ms", type=float, default=12.0)
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
        rows.append(cut(p, floor_db=args.floor_db, min_gap_s=args.min_gap_s,
                        keep_s=args.keep_s, xfade_ms=args.xfade_ms,
                        target_lufs=args.target_lufs, ceiling_db=args.ceiling_db,
                        out_path=p if (args.apply and not args.dry_run) else None))
    for r in rows:
        if "skipped" in r:
            print("%5s  POMINIETY: %s" % (r["id"], r["skipped"]))
        elif r.get("unchanged"):
            print("%5s  brak dziur >= %.2f s cichszych niz %.0f dB — bez zmian"
                  % (r["id"], args.min_gap_s, args.floor_db))
        else:
            print("%5s  dziur: %d | usunieto %.2f s | %.2f -> %.2f s | LUFS %.2f%s"
                  % (r["id"], r["gaps"], r["removed_s"], r["duration_before_s"],
                     r["duration_after_s"], r["lufs_after"],
                     "" if (args.apply and not args.dry_run) else "  (dry-run)"))
    if args.report:
        Path(args.report).write_text(json.dumps(
            {"floor_db": args.floor_db, "min_gap_s": args.min_gap_s,
             "keep_s": args.keep_s, "applied": bool(args.apply and not args.dry_run),
             "files": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("raport:", args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
