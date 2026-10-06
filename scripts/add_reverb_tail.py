#!/usr/bin/env python3
"""Wypełnia martwy ogon sample'a pogłosem pomieszczenia.

Problem: część plików ma 2,0-3,0 s długości, ale tylko 0,4-1,2 s słyszalnej
treści — reszta to prawdziwa cisza (RMS -54…-64 dB przy treści -20…-27 dB).
Trym tego nie naprawi, bo zostałoby 0,4 s, czyli daleko poza oknem 2-5 s.

Rozwiązanie bez generowania: jednorazowe zdarzenie (cios, ryk, plusk) naturalnie
dzieje się w jakiejś przestrzeni. Doklejamy syntetyczny ogon pogłosu, który
zaczyna się pod poziomem sygnału suchego i zanika do progu ciszy audytu
(-45 dBFS) dokładnie na końcu pliku. Pogłos jest tłumiony w górze pasma, bo
pomieszczenia wchłaniają wysokie częstotliwości — inaczej dodalibyśmy ostrości.

To nie zastępuje regeneracji tam, gdzie karta obiecuje powtarzalne zdarzenie
(marsz, seria ciosów, kilka szczeknięć) — takie karty wypisuje `--list-repeat`.

Użycie:
    python scripts/add_reverb_tail.py --ids 514,14,268 --wet-db -12 --dry-run
    python scripts/add_reverb_tail.py --ids 514,14,268 --wet-db -12 --apply
Po `--apply` należy przepuścić te id przez `postprocess_samples.py`
(renormalizacja LUFS i spójność z resztą korpusu).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_samples_full import (CUT_START_DB, CUT_START_MARGIN,  # noqa: E402
                                SILENCE_DB, frame_rms_db, integrated_lufs,
                                segment_rms_db)
from postprocess_samples import limit_true_peak  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def silence_edges(mono: np.ndarray, fs: int) -> tuple[float, float]:
    """Cisza początkowa i końcowa w sekundach — tak samo jak w audycie."""
    frames = frame_rms_db(mono, fs, 10.0)
    above = np.nonzero(frames > SILENCE_DB)[0]
    if not above.size:
        return 0.0, len(mono) / fs
    return above[0] * 0.010, (len(frames) - 1 - above[-1]) * 0.010


def make_ir(fs: int, dur_s: float, *, start_db: float, end_db: float,
            damping_hz: float, pre_delay_s: float, seed: int) -> np.ndarray:
    """Impuls pomieszczenia: szum zanikający liniowo w dB od start_db do end_db.

    Liniowy spadek w dB (nie wykładniczy w amplitudzie) daje przewidywalny ogon:
    wiadomo, przy jakim poziomie przekroczy próg ciszy audytu.
    """
    from scipy.signal import butter, sosfilt

    n = max(1, int(round(dur_s * fs)))
    rng = np.random.default_rng(seed)
    ir = rng.standard_normal(n)
    t = np.arange(n) / fs
    env_db = start_db + (end_db - start_db) * (t / dur_s)
    ir *= 10.0 ** (env_db / 20.0)
    sos = butter(2, min(damping_hz, fs / 2 - 1.0) / (fs / 2), btype="low", output="sos")
    ir = sosfilt(sos, ir).astype(np.float64)
    fade = min(int(0.030 * fs), n)
    if fade:
        ir[-fade:] *= np.linspace(1.0, 0.0, fade)
    pre = int(round(pre_delay_s * fs))
    if pre:
        ir = np.concatenate([np.zeros(pre), ir])
    return ir


def add_reverb(path: Path, *, wet_db: float, end_db: float, floor_db: float,
               damping_hz: float, pre_delay_s: float, seed: int,
               target_lufs: float = -20.0, ceiling_db: float = -1.0,
               wet_fade_ms: float = 150.0,
               out_path: Path | None = None) -> dict:
    data, fs = sf.read(str(path), always_2d=True)
    mono = data.mean(axis=1)
    lead, trail = silence_edges(mono, fs)
    dur = len(mono) / fs
    tail_n = int(round(trail * fs))
    result = {
        "id": int(path.stem) if path.stem.isdigit() else path.stem,
        "file": path.name,
        "duration_s": round(dur, 3),
        "content_before_s": round(max(0.0, dur - lead - trail), 3),
        "trail_silence_s": round(trail, 3),
    }
    if tail_n < int(0.15 * fs):
        result["skipped"] = "ogon krotszy niz 0,15 s"
        return result

    # Pogłos ma wypełnić martwy ogon i trzymać się nad progiem ciszy audytu
    # (-45 dBFS dla obwiedni 10 ms). Poziom startowy liczymy od RMS treści,
    # nie od piku — przy piku pogłos wychodził o ~10 dB za cicho i wypełniał
    # tylko początek ogona.
    content = data[: len(data) - tail_n]
    if content.size == 0:
        result["skipped"] = "brak tresci do pobudzenia"
        return result
    c_rms = float(np.sqrt(np.mean(content ** 2)))
    content_rms_db = 20 * np.log10(c_rms) if c_rms > 0 else -120.0
    start_db = min(content_rms_db - wet_db, floor_db)
    ir = make_ir(fs, trail - 0.02, start_db=start_db, end_db=end_db,
                 damping_hz=damping_hz, pre_delay_s=pre_delay_s, seed=seed)

    # fade-in poglosu: bez niego wet doklada energii w pierwszych 15 ms i audyt
    # flaguje cut_start_hard (start_15ms_db rosnie ponad prog).
    n_fade = min(len(ir), int(wet_fade_ms * 1e-3 * fs))
    if n_fade:
        ir = ir.copy()
        ir[:n_fade] *= np.linspace(0.0, 1.0, n_fade)

    out = data.astype(np.float64).copy()
    for ch in range(data.shape[1]):
        wet = np.convolve(content[:, ch], ir, mode="full")
        n = min(len(wet), len(out))
        out[:n, ch] += wet[:n]

    # korekta skalarem: mierzymy RMS pogłosu w oknie startu ogona i dosuwamy
    # do zadanego poziomu (jedno przesuniecie w dB przesuwa cala krzywa)
    wet_only = out - data.astype(np.float64)
    i0 = len(data) - tail_n
    w0 = max(i0, 0)
    seg = wet_only[w0: w0 + int(0.050 * fs)]
    if seg.size:
        got = float(np.sqrt(np.mean(seg ** 2)))
        if got > 0:
            want = 10.0 ** (start_db / 20.0)
            out = data.astype(np.float64) + wet_only * (want / got)

    # renormalizacja glosnosci: poglos dodaje energii, a korpus trzyma -20 LUFS.
    # Robimy to tutaj, bo przepuszczenie pliku przez postprocess_samples.py
    # z --trim-trail-s zjadloby wlasnie dodany ogon.
    # Dwa przebiegi normalizacja -> limiter: poglos podnosi pik (sumowanie z
    # suchym), a globalne sciszenie calego pliku zbijalo LUFS o 3,5 dB.
    # limit_true_peak z postprocess_samples.py lapie tylko transjenty.
    gr_mean = 0.0
    for _ in range(2):
        cur = integrated_lufs(out, fs)  # tak jak audyt: na kanalach, nie mono
        if np.isfinite(cur):
            out *= 10.0 ** ((target_lufs - cur) / 20.0)
        out, _gr_peak, gr_mean = limit_true_peak(out, fs, ceiling_db=ceiling_db)
    result["lufs_after"] = round(float(integrated_lufs(out, fs)), 2)
    result["limiter_mean_gr_db"] = gr_mean

    # Cichy ogon obniza mierzona glosnosc (bramkowanie BS.1770), wiec
    # renormalizacja do -20 LUFS podnosi transjent o kilka dB. Tam, gdzie plik
    # startuje od pelnego poziomu (brak ciszy wstepnej), przekracza to prog
    # audytu i flaguje cut_start_hard — a to realny klik, nie kosmetyka,
    # wiec dokladamy krotki fade-in.
    mono_chk = out.mean(axis=1)
    start_db = segment_rms_db(mono_chk, fs, 0.0, 0.015)
    max_frame = float(np.max(frame_rms_db(mono_chk, fs, 10.0)))
    if start_db > CUT_START_DB and start_db > max_frame - CUT_START_MARGIN:
        n = max(1, int(0.012 * fs))
        out[:n] *= np.linspace(0.0, 1.0, n)[:, None]
        result["start_fade_applied"] = True
        result["start_15ms_db_after"] = round(
            float(segment_rms_db(out.mean(axis=1), fs, 0.0, 0.015)), 2)

    mono_after = out.mean(axis=1)
    lead2, trail2 = silence_edges(mono_after, fs)
    result["content_after_s"] = round(max(0.0, dur - lead2 - trail2), 3)
    result["gained_s"] = round(result["content_after_s"] - result["content_before_s"], 3)

    if out_path is not None:
        tmp = out_path.with_suffix(".tmp.mp3")
        sf.write(str(tmp), out.astype(np.float32), fs, format="MP3",
                 subtype="MPEG_LAYER_III")
        tmp.replace(out_path)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids", required=True, help="id po przecinku")
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--wet-db", type=float, default=10.0,
                    help="ile dB poniżej RMS treści startuje pogłos (domyślnie 10)")
    ap.add_argument("--floor-db", type=float, default=-30.0,
                    help="sufit poziomu startowego pogłosu w dBFS (domyślnie -30)")
    ap.add_argument("--end-db", type=float, default=-46.0,
                    help="poziom, do którego ogon zanika na końcu pliku (próg ciszy -45)")
    ap.add_argument("--damping-hz", type=float, default=3200.0,
                    help="tłumienie góry w pogłosie (pomieszczenie wchłania wysokie)")
    ap.add_argument("--pre-delay-s", type=float, default=0.012)
    ap.add_argument("--target-lufs", type=float, default=-20.0,
                    help="głośność docelowa po dodaniu pogłosu (korpus: -20)")
    ap.add_argument("--wet-fade-ms", type=float, default=150.0,
                    help="fade-in pogłosu; 50 ms nie wystarczało tam, gdzie plik "
                         "startuje od pełnego poziomu (cut_start_hard)")
    ap.add_argument("--ceiling-db", type=float, default=-1.0,
                    help="sufit true peak dla limitera (domyślnie -1 dBTP)")
    ap.add_argument("--seed", type=int, default=20261005)
    ap.add_argument("--dry-run", action="store_true",
                    help="tylko pomiar, bez zapisu (domyślne zachowanie)")
    ap.add_argument("--apply", action="store_true",
                    help="zapisz pliki (bez tego tylko pomiar)")
    ap.add_argument("--report", help="zapisz raport JSON")
    args = ap.parse_args()

    src = Path(args.samples_dir)
    ids = [i.strip() for i in args.ids.split(",") if i.strip()]
    rows = []
    for sid in ids:
        p = src / ("%s.mp3" % sid)
        if not p.exists():
            rows.append({"id": int(sid), "skipped": "brak pliku"})
            continue
        rows.append(add_reverb(
            p, wet_db=args.wet_db, end_db=args.end_db, floor_db=args.floor_db,
            damping_hz=args.damping_hz,
            pre_delay_s=args.pre_delay_s, seed=args.seed,
            target_lufs=args.target_lufs,
            ceiling_db=args.ceiling_db,
            wet_fade_ms=args.wet_fade_ms,
            out_path=p if (args.apply and not args.dry_run) else None))

    for r in rows:
        if "skipped" in r:
            print("%4s  POMINIECY: %s" % (r["id"], r["skipped"]))
            continue
        print("%4s  tresc %.2f -> %.2f s (+%.2f)  ogon %.2f s"
              % (r["id"], r["content_before_s"], r["content_after_s"],
                 r["gained_s"], r["trail_silence_s"]))

    ok = [r for r in rows if "content_after_s" in r]
    if ok:
        still = sum(1 for r in ok if r["content_after_s"] < 2.0)
        print("razem %d plikow | srednio +%.2f s tresci | nadal < 2,0 s: %d%s"
              % (len(ok), sum(r["gained_s"] for r in ok) / len(ok), still,
                 "" if (args.apply and not args.dry_run) else "  (dry-run, pliki nie zmienione)"))
    if args.report:
        Path(args.report).write_text(json.dumps(
            {"wet_db": args.wet_db, "end_db": args.end_db,
             "damping_hz": args.damping_hz, "applied": bool(args.apply),
             "files": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("raport:", args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
