#!/usr/bin/env python3
"""Standalone acoustic QA audit of a rendered MP3 (CLI).

QA v2 gates (scripts/qa_score.py is the single scoring source): DC offset,
peak/headroom, 0.35 s dead-window continuity, total loudness (RMS >= -23
dBFS), spectral balance (<= 12% energy above 6 kHz) and - when a recipe or
event list is supplied - per-event audibility (every described stem event
>= +6 dB over the bed level in its window).

Use it to audit any file, e.g. to verify that QA metadata stored in
data/versions.json matches the actual audio, to check a file produced
outside the recipe renderer, or to re-run the calibration over the whole
catalog:

  python scripts/audit_audio.py legacy/source/jingle_output/2_v2.mp3
  python scripts/audit_audio.py --recipe data/recipes/8_v2.json
  python scripts/audit_audio.py --versions data/versions.json --audio-root legacy/source/jingle_output

Requires the authoring venv: `pip install numpy soundfile`.
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


def rms(sig: np.ndarray) -> float:
    return float(np.sqrt(np.mean(sig ** 2)) + 1e-12)


def bed_level(data: np.ndarray, sr: int, events: list[dict]) -> float:
    """Robust bed level: 15th percentile of 0.35 s window RMS.

    With several events per jingle there is no event-free stretch to measure,
    so the old 'RMS outside event windows' estimator collapsed into the
    quieter half of the file - which contains events - and deflated every
    audibility delta. A low percentile of windowed RMS tracks the continuous
    bed under transients instead."""
    win = int(0.35 * sr)
    if len(data) <= win:
        return rms(data)
    levels = [rms(data[i:i + win]) for i in range(0, len(data) - win, win // 2)]
    levels.sort()
    k = max(0, int(0.15 * (len(levels) - 1)))
    return levels[k]


def analyze(path: Path, climax: tuple[float, float] = (1.5, 3.8),
            events: list[dict] | None = None) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from qa_score import calculate_qa_score, LOUDNESS_MIN_DB, HF_MAX_SHARE

    data, sr = load_mono(path)
    dc = float(np.abs(np.mean(data)))
    dc_ok = dc <= 0.015
    peak = float(np.max(np.abs(data)))
    peak_ok = 0.25 <= peak <= 0.999  # decoded MP3 may overshoot the 0.99 pre-encode gate
    step = int(sr * 0.35)
    dead = [round(i / sr, 2) for i in range(0, len(data) - step, step)
            if np.sqrt(np.mean(data[i:i + step] ** 2)) < 0.003]
    continuity_ok = len(dead) <= 1
    rms_total = rms(data)
    rms_db = 20 * np.log10(rms_total)
    loudness_ok = rms_db >= LOUDNESS_MIN_DB
    spec = np.abs(np.fft.rfft(data)) ** 2
    freqs = np.fft.rfftfreq(len(data), 1.0 / sr)
    hf = float(spec[freqs >= 6000].sum() / (spec.sum() + 1e-12))
    spectral_ok = hf <= HF_MAX_SHARE
    rms_intro = float(np.sqrt(np.mean(data[: int(sr * 1.0)] ** 2)) + 1e-5)
    c0, c1 = int(climax[0] * sr), int(climax[1] * sr)
    rms_climax = float(np.sqrt(np.mean(data[c0:c1] ** 2)))
    ratio = rms_climax / rms_intro

    audibility = None
    if events:
        bed = bed_level(data, sr, events)
        bed_db = 20 * np.log10(bed)
        # Neighbouring distinct events cap the measurement window: a weak
        # event must not pass by borrowing the next event's loudness (the
        # 450 v3 failure mode). Near-simultaneous events (<0.15 s apart) are
        # one compound beat and share the window.
        times = sorted(float(ev.get("time_sec", 0)) for ev in events)
        audibility = []
        w = int(0.35 * sr)
        for ev in events:
            t = float(ev.get("time_sec", 0))
            limit = t + 1.0
            for other in times:
                if t + 0.15 < other < limit:
                    limit = other
                    break
            i0 = int(t * sr)
            # sub-windows must fit entirely before the next distinct onset,
            # so a weak event cannot borrow the neighbour's loudness
            last_start = min(int(limit * sr) - w, i0 + int(1.0 * sr) - w)
            if last_start < i0:
                last_start = i0  # crowded: fall back to the plain window
            ev_rms = 1e-12
            for j in range(i0, last_start + 1, max(1, w // 2)):
                ev_rms = max(ev_rms, rms(data[j:j + w]))
            live = not str(ev.get("sample", "")).startswith("synth:")
            audibility.append({
                "sample": ev.get("sample", "?"),
                "time_sec": t,
                "live": live,
                "level": str(ev.get("level", "event")),
                "delta_db": 20 * np.log10(ev_rms) - bed_db,
            })

    result = calculate_qa_score(
        climax_ratio=ratio, dc_ok=dc_ok, peak_ok=peak_ok, continuity_ok=continuity_ok,
        loudness_ok=loudness_ok, spectral_ok=spectral_ok,
        audibility=audibility, rms_db=rms_db, hf_share=hf,
    )
    result.update({
        "file": str(path),
        "climax_ratio": round(ratio, 2),
        "rms_db": round(rms_db, 1),
        "hf_share": round(hf, 3),
        "audibility": audibility,
    })
    if not dc_ok:
        result["details"].insert(0, f"DC offset: {dc:.4f}!")
    if not peak_ok:
        result["details"].insert(0, f"Peak: {peak:.3f} poza [0.25, 0.999]!")
    if dead:
        result["details"].append(f"Martwe okna: {dead}s")
    return result


def recipe_events(recipe_path: Path) -> tuple[str, str, list[dict]]:
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    story = str(recipe.get("story_id", ""))
    label = str(recipe.get("label", ""))
    audio_name = f"{story}.mp3" if label in ("", "v1") else f"{story}_{label}.mp3"
    events = [
        {"time_sec": float(ev.get("time_sec", 0)),
         "sample": ev.get("file") or f"synth:{ev.get('kind')}",
         "level": str(ev.get("level", "event"))}
        for ev in recipe.get("events", [])
    ]
    return audio_name, str(recipe.get("climax_window", "[1.5, 3.8]")), events


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", type=Path)
    parser.add_argument("--recipe", type=Path, help="audit the MP3 rendered from this recipe (event audibility)")
    parser.add_argument("--versions", type=Path, help="audit all versions in this metadata file (drift control)")
    parser.add_argument("--audio-root", type=Path, default=Path("legacy/source/jingle_output"))
    args = parser.parse_args()

    if args.recipe:
        audio_name, cw, events = recipe_events(args.recipe)
        path = Path(args.audio_root) / audio_name
        window = tuple(json.loads(cw))
        report = analyze(path, window, events=events)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if str(report["status"]).startswith("pass") else 1

    if args.versions:
        data = json.loads(args.versions.read_text(encoding="utf-8"))
        bad = 0
        drift = 0
        for story in data.get("stories", []):
            for version in story.get("versions", []):
                audio = version.get("audio", "")
                path = (ROOT / audio) if audio.startswith("legacy") else (args.audio_root / Path(audio).name)
                if not path.is_file():
                    print(f"{story['id']} {version['label']}: BRAK PLIKU {path}")
                    bad += 1
                    continue
                design = version.get("project_description", {})
                events = design.get("events")
                report = analyze(path, tuple(design.get("climax_window", [1.5, 3.8])), events=events)
                mark = "OK " if str(report["status"]).startswith("pass") else "FAIL"
                stored = design.get("qa", {}).get("score")
                drift_note = ""
                if stored is not None and abs(float(stored) - report["score"]) > 0.05:
                    drift_note = f"  DRYF: metadata {stored} vs plik {report['score']}"
                    drift += 1
                print(f"{story['id']:>4} {version['label']}: {mark} QA={report['score']:5.1f} RMS={report['rms_db']:6.1f} dB HF={100 * report['hf_share']:4.0f}% [{report['status']}]{drift_note}")
                if mark == "FAIL":
                    bad += 1
        if drift:
            print(f"Uwaga: {drift} wersji ma dryf metadata↔plik (cel 0.0).")
        return 0 if bad == 0 else 1

    if not args.file:
        parser.error("podaj plik, --recipe lub --versions")
        return 2
    report = analyze(args.file)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if str(report["status"]).startswith("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
