#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wybór najlepszego wariantu generacji kontraktem archetypu.

Jedna generacja z tego samego promptu trafia raz lepiej, raz gorzej — karta
`312` miała w prompcie „a shrill wordless cackle of mockery”, a wyszło
skrzypienie piasku. Skoro nie da się tego wyczytać z promptu, generujemy kilka
wariantów i wybieramy mierzalnie: ten, który najlepiej spełnia kontrakt
archetypu zadeklarowanego w scenariuszu (`scripts/audit_archetype_match.py`).

To nie jest wyrok estetyczny — audyt jest proxy dla ucha właściciela i dopóki
nie jest skalibrowany, służy do **sortowania**, a nie do zastępowania odsłuchu.
Dlatego raport zawsze pokazuje punktację wszystkich wariantów, a nie tylko
zwycięzcę.

Struktura wejściowa (po generacji w Actions):

    variants/r016/v1/<id>.mp3
    variants/r016/v2/<id>.mp3
    variants/r016/v3/<id>.mp3

Użycie:
    python scripts/pick_archetype_variant.py --variants-dir variants/r016
    python scripts/pick_archetype_variant.py --variants-dir variants/r016 --apply
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from audit_archetype_match import CONTRACTS, evaluate, metric, verdict  # noqa: E402
from audit_samples_full import analyze  # noqa: E402
from audit_semantic_match import extra_features  # noqa: E402


def score_file(path: Path, expected: float, music_allowed: bool, archetype: str):
    metrics = analyze(path, expected, music_allowed).metrics
    metrics.update(extra_features(path))
    score, broken = evaluate(archetype, metrics)
    return score, broken, metrics


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants-dir", type=Path, required=True)
    ap.add_argument("--scenarios", type=Path, default=ROOT / "data/samples/scenarios.jsonl")
    ap.add_argument("--out", type=Path, default=ROOT / "audio/samples")
    ap.add_argument("--json", type=Path, dest="json_out")
    ap.add_argument("--apply", action="store_true",
                    help="kopiuj zwycięski wariant do --out (domyślnie tylko raport)")
    args = ap.parse_args()

    rows = [json.loads(l) for l in args.scenarios.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_id = {str(r["story_id"]): r for r in rows}
    args.variants_dir = args.variants_dir.resolve()
    variant_dirs = sorted(p for p in args.variants_dir.iterdir() if p.is_dir())
    if not variant_dirs:
        raise SystemExit(f"{args.variants_dir}: brak katalogów wariantów")

    ids = sorted({p.stem for d in variant_dirs for p in d.glob("*.mp3")}, key=int)
    report = []
    for sid in ids:
        row = by_id.get(sid, {})
        archetype = row.get("archetype")
        if not archetype:
            print(f"{sid}: brak pola archetype w scenariuszu — pomijam", file=sys.stderr)
            continue
        expected = float(row.get("duration_seconds") or 4.0)
        music = bool(row.get("music_allowed"))
        variants = []
        for d in variant_dirs:
            f = d / f"{sid}.mp3"
            if not f.exists():
                continue
            score, broken, metrics = score_file(f, expected, music, archetype)
            variants.append({
                "variant": d.name, "file": str(f.relative_to(ROOT)), "score": score,
                "violations": [b["reason"] for b in broken],
                "verdict": verdict(score),
                "metrics": {
                    k: (round(v, 3) if isinstance(v := metric(metrics, k), float) else v)
                    for k in ("duration_s", "content_rel_s", "lufs", "low_all",
                              "spectral_centroid_hz", "spectral_flatness",
                              "tonal_frame_fraction", "voiced_fraction", "crest_db",
                              "attack_s", "decay_s", "onset_count", "sustain_ratio",
                              "mod_peak_hz") if metric(metrics, k) is not None},
            })
        if not variants:
            continue
        # Równorzędne wyniki rozstrzyga dłuższa słyszalna treść: kontrakt nie
        # widzi estetyki, a sample z 2,8 s treści jest gorszy niż z 3,5 s.
        variants.sort(key=lambda v: (v["score"], -v["metrics"].get("content_rel_s", 0.0), v["variant"]))
        best = variants[0]
        report.append({
            "id": sid, "title": row.get("title"), "archetype": archetype,
            "archetype_label": CONTRACTS.get(archetype, {}).get("label", archetype),
            "chosen": best["variant"], "chosen_score": best["score"],
            "spread": round(variants[-1]["score"] - best["score"], 2),
            "variants": variants,
        })
        print(f"{sid:>4} {row.get('title','')[:24]:<24} {archetype:<18} "
              f"wybór {best['variant']} ({best['score']} pkt), "
              f"pozostałe {[v['score'] for v in variants[1:]]}")
        if args.apply:
            dst = args.out / f"{sid}.mp3"
            shutil.copyfile(ROOT / best["file"], dst)
            print(f"     -> {dst.relative_to(ROOT)}")

    out = {"variants_dir": str(args.variants_dir), "applied": bool(args.apply), "results": report}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"raport: {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
