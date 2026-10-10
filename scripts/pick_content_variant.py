#!/usr/bin/env python3
"""Wybiera wariant dla kart BEZ archetypu — po długości treści, nie po kontrakcie.

`pick_archetype_variant.py` pomija karty bez pola `archetype` (nie ma kontraktu,
więc nie ma czego punktować). Transza r027 dotyczyła właśnie takich kart: karta
obiecuje zdarzenie powtarzalne, a stary sample miał jedno i resztę ciszy.
Kryterium wyboru jest więc to, co naprawiamy: ile sekund słyszalnej treści
(`content_s = plik - cisza początkowa - cisza końcowa`) mieści się w wariancie.

Kolejność kryteriów:
1. wariant bez flag głównych audytu (near_silent, clipping, too_quiet, ...)
2. dłuższa treść `content_s`
3. mniej flag w ogóle
4. dłuższy plik (remis rozstrzyga pełniejsza treść)

Użycie:
    python scripts/pick_content_variant.py --variants-dir variants/r027 --ids 10,218
    python scripts/pick_content_variant.py --variants-dir variants/r027 --ids 10,218 --apply
Po `--apply` trzeba przepuścić te id przez `postprocess_samples.py`
BEZ `--trim-trail-s`, bo trym zjada właśnie tę treść, którą tu wybieramy.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_samples_full import analyze  # noqa: E402

MAIN_FLAGS = {"near_silent", "cut_end_hard", "too_quiet", "too_loud", "clipping",
              "duration_mismatch", "sub_dominant", "muffled", "short_content",
              "dc_offset"}


def measure(path: Path) -> dict:
    res = analyze(path, None, False)
    m = dict(res.metrics)
    m["flags"] = list(res.metrics.get("flags") or [])
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variants-dir", required=True, type=lambda p: Path(p).resolve())
    ap.add_argument("--ids", required=True, help="id po przecinku")
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", dest="json_out", help="zapisz raport JSON")
    args = ap.parse_args()

    ids = [i.strip() for i in args.ids.split(",") if i.strip()]
    out_dir = Path(args.samples_dir)
    results = []
    for sid in ids:
        cands = []
        for sub in sorted(p for p in args.variants_dir.iterdir() if p.is_dir()):
            f = sub / ("%s.mp3" % sid)
            if f.exists():
                cands.append((sub.name, f))
        if not cands:
            print("%5s  brak wariantow" % sid, file=sys.stderr)
            continue
        rows = []
        for name, f in cands:
            m = measure(f)
            rows.append({
                "variant": name,
                "file": str(f.relative_to(Path.cwd())) if f.is_relative_to(Path.cwd()) else str(f),
                "duration_s": round(m["duration_s"], 3),
                "content_s": round(m["content_s"], 3),
                "lufs": m.get("lufs"),
                "flags": m["flags"],
                "main_flags": sorted(set(m["flags"]) & MAIN_FLAGS),
            })
        # 1) bez flag glownych, 2) dluzsza tresc, 3) mniej flag, 4) dluzszy plik
        rows.sort(key=lambda r: (len(r["main_flags"]), -r["content_s"],
                                 len(r["flags"]), -r["duration_s"]))
        best = rows[0]
        results.append({"id": sid, "chosen": best["variant"], "variants": rows})
        print("%5s  wybrany %s | tresc %.2f s (pliki %.2f/%.2f s) | flagi %s%s"
              % (sid, best["variant"], best["content_s"],
                 rows[0]["duration_s"], rows[-1]["duration_s"],
                 ",".join(best["flags"]) or "-",
                 "" if not best["main_flags"] else "  [%s]" % ",".join(best["main_flags"])))
        if args.apply:
            src = Path(best["file"])
            if not src.is_absolute():
                src = Path.cwd() / src
            import shutil
            shutil.copyfile(src, out_dir / ("%s.mp3" % sid))

    ok = [r for r in results]
    if ok:
        cs = [r["variants"][0]["content_s"] for r in ok]
        print("razem %d kart | srednia tresc wybranego wariantu %.2f s | "
              "ponizej 2 s: %d%s" % (len(ok), sum(cs) / len(cs),
                                     sum(1 for x in cs if x < 2.0),
                                     "" if args.apply else "  (bez --apply)"))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(
            {"variants_dir": str(args.variants_dir), "applied": bool(args.apply),
             "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("raport:", args.json_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
