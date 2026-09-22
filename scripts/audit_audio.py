#!/usr/bin/env python3
"""Standalone acoustic QA audit of a rendered MP3 (CLI).

Same gates and scoring as scripts/render_jingle.py's internal auditor and
scripts/qa_score.py (the single scoring source): DC offset, peak/headroom,
0.35 s dead-window continuity, and the Dynamic Climax Ratio (intro 0-1 s vs
climax window, default 1.5-3.8 s). Use it to audit any file, e.g. to verify
that QA metadata stored in data/versions.json matches the actual audio, or
to check a file produced outside the recipe renderer.

Requires the authoring venv: `pip install numpy soundfile`.

Usage:
  python scripts/audit_audio.py legacy/source/jingle_output/2_v2.mp3
  python scripts/audit_audio.py --versions data/versions.json --audio-root legacy/source/jingle_output
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR_REF = 44_100


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    import soundfile as sf  # authoring-only dependency

    data, sr = sf.read(str(path))
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data.astype(np.float64), sr


def analyze(path: Path, climax: tuple[float, float] = (1.5, 3.8)) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from qa_score import calculate_qa_score  # single scoring source

    data, sr = load_mono(path)
    dc = float(np.abs(np.mean(data)))
    dc_ok = dc <= 0.015
    peak = float(np.max(np.abs(data)))
    peak_ok = 0.25 <= peak <= 0.999  # decoded MP3 may overshoot the 0.99 pre-encode gate
    step = int(sr * 0.35)
    dead = [round(i / sr, 2) for i in range(0, len(data) - step, step)
            if np.sqrt(np.mean(data[i:i + step] ** 2)) < 0.003]
    continuity_ok = len(dead) <= 1
    rms_intro = float(np.sqrt(np.mean(data[: int(sr * 1.0)] ** 2)) + 1e-5)
    c0, c1 = int(climax[0] * sr), int(climax[1] * sr)
    rms_climax = float(np.sqrt(np.mean(data[c0:c1] ** 2)))
    ratio = rms_climax / rms_intro
    result = calculate_qa_score(climax_ratio=ratio, dc_ok=dc_ok, peak_ok=peak_ok, continuity_ok=continuity_ok)
    result.update({
        "file": str(path),
        "climax_ratio": round(ratio, 2),
        "details": [
            ("DC offset: OK" if dc_ok else f"DC offset: FAIL ({dc:.4f})"),
            ("Peak/headroom: OK" if peak_ok else f"Peak/headroom: FAIL ({peak:.2f})"),
            ("Ciągłość tła: OK" if continuity_ok else f"Martwa cisza: {dead}"),
            f"Kontrast dramaturgiczny: {result['dramaturgy']}/30 (ratio {ratio:.2f}x)",
        ],
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path, nargs="?")
    parser.add_argument("--versions", type=Path, help="audit every version listed in versions.json")
    parser.add_argument("--audio-root", type=Path, help="fallback dir for version audio paths")
    parser.add_argument("--climax", nargs=2, type=float, default=[1.5, 3.8], metavar=("START", "END"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    targets: list[tuple[str, Path, dict | None]] = []
    if args.versions:
        data = json.loads(args.versions.read_text(encoding="utf-8"))
        for story in data.get("stories", []):
            for version in story.get("versions", []):
                path = Path(version.get("audio", ""))
                if not path.is_file() and args.audio_root:
                    path = args.audio_root / path.name
                targets.append((f"{story['id']} {version.get('label')}", path, version))
    elif args.audio:
        targets.append((args.audio.stem, args.audio, None))
    else:
        parser.error("podaj plik audio albo --versions")

    worst = 1 if str(targets) else 0
    failures = 0
    for name, path, version in targets:
        if not path.is_file():
            print(f"{name}: MISSING {path}")
            failures += 1
            continue
        report = analyze(path, tuple(args.climax))
        stored = (version or {}).get("project_description", {}).get("qa", {}).get("score")
        drift = ""
        if stored is not None:
            delta = round(report["score"] - stored, 1)
            drift = f" (metadata: {stored}, drift: {delta:+})"
        line = f"{name}: {report['score']}/100 [{report['status']}] ratio={report['climax_ratio']}x{drift}"
        if args.json:
            print(json.dumps({**report, "name": name, "metadata_score": stored}, ensure_ascii=False))
        else:
            print(line)
        if not str(report["status"]).startswith("pass"):
            failures += 1
    if failures:
        print(f"FAILED audits: {failures}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
