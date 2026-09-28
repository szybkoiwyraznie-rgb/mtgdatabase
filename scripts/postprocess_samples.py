#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postprodukcja korpusu sampli: wyrównanie głośności, limiter, filtr DC.

Powód (audyt 2026-09-28, `docs/audits/2026-09-28-audio-audit-fullscan.md`):
korpus miał rozpiętość głośności 43,9 LU, 58 plików z true peakiem powyżej
+1 dBTP, 19 z offsetem DC i 28 z energią zepchniętą w infradźwięki. Przy
odsłuchu seryjnym „cichy" myliło się z „zły".

Łańcuch na plik:

1. filtr górnoprzepustowy — 25 Hz dla wszystkich (offset DC i subsonic),
   45 Hz dla plików oflagowanych w audycie jako `sub_dominant` (> 80 %
   energii poniżej 60 Hz — na typowym sprzęcie to i tak niesłyszalne,
   a zjada cały headroom),
2. pomiar głośności (LUFS wg BS.1770-4) i wzmocnienie do wspólnego celu,
   z limitem wzmocnienia (domyślnie +15 dB — powyżej wychodzi szum tła),
3. limiter true peak z miękką obwiednią, sufit domyślnie −1 dBTP,
4. zapis MP3 (VBR, jakość 0) + weryfikacja **na zapisanym pliku**:
   ponowny pomiar LUFS/true peak i SNR transkodowania.

Operacja jest odwracalna: poprzednia wersja plików siedzi w historii gita.

Użycie:
    python scripts/postprocess_samples.py --dry-run
    python scripts/postprocess_samples.py --report data/samples/postprocess.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import ndimage, signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_samples_full import integrated_lufs, true_peak_dbtp  # noqa: E402

EPS = 1e-12
ROOT = Path(__file__).resolve().parent.parent


def db_to_lin(x: float) -> float:
    return 10.0 ** (x / 20.0)


def highpass(data: np.ndarray, fs: int, cutoff: float) -> np.ndarray:
    """Filtr górnoprzepustowy bez przesunięcia fazy (filtfilt, 2. rzędu)."""
    sos = signal.butter(2, cutoff, btype="highpass", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, data, axis=0)


def limit_true_peak(data: np.ndarray, fs: int, ceiling_db: float,
                    attack_ms: float = 1.5) -> tuple[np.ndarray, float]:
    """Limiter działający na obwiedni nadpróbkowanej 4x.

    Zwraca (sygnał, maksymalna redukcja wzmocnienia w dB). Zamiast twardego
    obcinania próbek liczymy gładką krzywą wzmocnienia (minimum filter +
    wygładzenie gaussowskie), więc nie powstają trzaski ani zniekształcenia
    schodkowe.
    """
    ceiling = db_to_lin(ceiling_db)
    up = signal.resample_poly(data, 4, 1, axis=0)
    env = np.max(np.abs(up), axis=1)
    if float(np.max(env)) <= ceiling:
        return data, 0.0

    gain = np.minimum(1.0, ceiling / np.maximum(env, EPS))
    win = max(3, int(attack_ms * 1e-3 * fs * 4))
    gain = ndimage.minimum_filter1d(gain, size=2 * win + 1, mode="nearest")
    gain = ndimage.gaussian_filter1d(gain, sigma=win / 2.0, mode="nearest")
    gain_ds = gain[::4][: len(data)]
    if len(gain_ds) < len(data):  # dopchnięcie po zaokrągleniu długości
        gain_ds = np.pad(gain_ds, (0, len(data) - len(gain_ds)), mode="edge")
    out = data * gain_ds[:, None]

    # zabezpieczenie: po wygładzeniu obwiedni może zostać ułamek dB nad sufitem
    tp = db_to_lin(true_peak_dbtp(out, fs))
    if tp > ceiling:
        out = out * (ceiling / tp)
    return out, round(20.0 * math.log10(max(float(np.min(gain_ds)), EPS)), 2)


def transcode_snr(before: np.ndarray, after: np.ndarray) -> float:
    """SNR między sygnałem przed i po zapisie MP3 (wyrównany o opóźnienie)."""
    a, b = before.mean(axis=1), after.mean(axis=1)
    n = min(len(a), len(b))
    if n < 64:
        return 0.0
    a, b = a[:n], b[:n]
    corr = np.fft.irfft(np.fft.rfft(b, 2 * n) * np.conj(np.fft.rfft(a, 2 * n)))
    lag = int(np.argmax(corr[:2000]))
    bb = b[lag:]
    aa = a[: len(bb)]
    err = aa - bb
    return round(float(10.0 * np.log10(np.sum(aa**2) / max(float(np.sum(err**2)), EPS))), 1)


def process_one(path: Path, out_path: Path, *, target_lufs: float, ceiling_db: float,
                max_gain_db: float, hp_hz: float, dry_run: bool,
                encoder_headroom_db: float = 0.7) -> dict:
    data, fs = sf.read(str(path), always_2d=True)
    lufs_before = integrated_lufs(data, fs)
    tp_before = true_peak_dbtp(data, fs)
    dc_before = float(np.mean(data))

    filtered = highpass(data, fs, hp_hz)
    lufs_filtered = integrated_lufs(filtered, fs)

    raw_gain = target_lufs - lufs_filtered
    gain_db = min(raw_gain, max_gain_db)
    gained = filtered * db_to_lin(gain_db)
    # Koder MP3 potrafi podnieść true peak o ~1 dB, więc limitujemy z zapasem
    # i i tak weryfikujemy wynik na zapisanym pliku.
    processed, limiter_gr = limit_true_peak(gained, fs, ceiling_db - encoder_headroom_db)

    result = {
        "id": path.stem,
        "hp_hz": hp_hz,
        "lufs_before": lufs_before,
        "lufs_after_hp": lufs_filtered,
        "gain_db": round(gain_db, 2),
        "gain_wanted_db": round(raw_gain, 2),
        "gain_capped": bool(raw_gain > max_gain_db + 1e-9),
        "limiter_gr_db": limiter_gr,
        "true_peak_before": tp_before,
        "dc_before": round(dc_before, 5),
    }
    if dry_run:
        result["lufs_after"] = integrated_lufs(processed, fs)
        result["true_peak_after"] = true_peak_dbtp(processed, fs)
        return result

    bytes_before = path.stat().st_size
    tmp = out_path.with_suffix(".tmp.mp3")
    headroom = encoder_headroom_db
    attempts = 0
    while True:
        attempts += 1
        sf.write(str(tmp), processed, fs, format="MP3", subtype="MPEG_LAYER_III",
                 bitrate_mode="VARIABLE", compression_level=0.0)
        written, fs2 = sf.read(str(tmp), always_2d=True)
        tp_written = true_peak_dbtp(written, fs2)
        if tp_written <= ceiling_db + 0.02 or attempts >= 3:
            break
        # zapisany plik przekroczył sufit — powtarzamy z większym zapasem
        headroom += (tp_written - ceiling_db) + 0.15
        processed, limiter_gr = limit_true_peak(gained, fs, ceiling_db - headroom)
    os.replace(tmp, out_path)

    result.update({
        "encode_attempts": attempts,
        "encoder_headroom_db": round(headroom, 2),
        "limiter_gr_db": limiter_gr,
        "lufs_after": integrated_lufs(written, fs2),
        "true_peak_after": true_peak_dbtp(written, fs2),
        "dc_after": round(float(np.mean(written)), 5),
        "transcode_snr_db": transcode_snr(processed, written),
        "bytes_before": bytes_before,
        "bytes_after": out_path.stat().st_size,
    })
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--out-dir", default="", help="pusty = zapis w miejscu")
    ap.add_argument("--audit", default="data/samples/audio-audit-2026-09-28-fullscan.json",
                    help="JSON audytu — z niego bierzemy listę plików sub_dominant")
    ap.add_argument("--target-lufs", type=float, default=-20.0)
    ap.add_argument("--ceiling-dbtp", type=float, default=-1.0)
    ap.add_argument("--max-gain-db", type=float, default=15.0)
    ap.add_argument("--encoder-headroom", type=float, default=0.7,
                    help="zapas pod overshoot kodera MP3 (dB)")
    ap.add_argument("--hp-default", type=float, default=25.0)
    ap.add_argument("--hp-sub", type=float, default=45.0)
    ap.add_argument("--ids", default="", help="opcjonalna lista ID po przecinku")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--report", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sub_dominant: set[str] = set()
    audit_path = Path(args.audit)
    if audit_path.exists():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        sub_dominant = {str(r["id"]) for r in audit.get("files", [])
                        if "sub_dominant" in r.get("flags", [])}

    src_dir = Path(args.samples_dir)
    out_dir = Path(args.out_dir) if args.out_dir else src_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(src_dir.glob("*.mp3"), key=lambda p: int(p.stem) if p.stem.isdigit() else 10**9)
    if args.ids:
        wanted = {i.strip() for i in args.ids.split(",") if i.strip()}
        files = [f for f in files if f.stem in wanted]
    if args.limit:
        files = files[: args.limit]

    rows: list[dict] = []
    for n, path in enumerate(files, 1):
        hp = args.hp_sub if path.stem in sub_dominant else args.hp_default
        try:
            rows.append(process_one(path, out_dir / path.name,
                                    target_lufs=args.target_lufs,
                                    ceiling_db=args.ceiling_dbtp,
                                    max_gain_db=args.max_gain_db,
                                    hp_hz=hp, dry_run=args.dry_run,
                                    encoder_headroom_db=args.encoder_headroom))
        except Exception as exc:  # noqa: BLE001
            rows.append({"id": path.stem, "error": str(exc)})
        if n % 50 == 0:
            print(f"  … {n}/{len(files)}", flush=True)

    ok = [r for r in rows if "error" not in r]
    after = np.array([r["lufs_after"] for r in ok]) if ok else np.zeros(1)
    tp_after = np.array([r.get("true_peak_after", -99) for r in ok]) if ok else np.zeros(1)
    snr = np.array([r["transcode_snr_db"] for r in ok if "transcode_snr_db" in r])
    summary = {
        "files": len(ok),
        "errors": len(rows) - len(ok),
        "target_lufs": args.target_lufs,
        "ceiling_dbtp": args.ceiling_dbtp,
        "max_gain_db": args.max_gain_db,
        "dry_run": args.dry_run,
        "lufs_after_median": round(float(np.median(after)), 2),
        "lufs_after_min": round(float(np.min(after)), 2),
        "lufs_after_max": round(float(np.max(after)), 2),
        "lufs_after_std": round(float(np.std(after)), 2),
        "true_peak_after_max": round(float(np.max(tp_after)), 2),
        "gain_capped_count": sum(1 for r in ok if r.get("gain_capped")),
        "limited_count": sum(1 for r in ok if r.get("limiter_gr_db", 0.0) < -0.01),
        "over_ceiling_after_encode": sum(1 for r in ok
                                         if r.get("true_peak_after", -99) > args.ceiling_dbtp + 0.02),
        "reencoded_count": sum(1 for r in ok if r.get("encode_attempts", 1) > 1),
        "transcode_snr_median_db": round(float(np.median(snr)), 1) if snr.size else None,
        "transcode_snr_min_db": round(float(np.min(snr)), 1) if snr.size else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"summary": summary, "files": rows},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"raport: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
