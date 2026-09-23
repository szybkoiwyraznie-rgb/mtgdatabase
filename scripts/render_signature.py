#!/usr/bin/env python3
"""Render sygnatury fabuły: tło (d) + hero (c) + koda muzyczna (a × b).

Receptura (data/recipes/<id>.json) wskazuje wyłącznie ZATWIERDZONE klocki
z czterech baz (data/library/*.json). Agent nie miks niczego „na słuch" —
poziomy i okna pochodzą z receptury, a bramki QA sprawdzają plik wynikowy.

Twarde reguły produktu:
- długość ≤ 10 s (okno dźwiękowe interfejsu gry);
- hero czytelny: RMS w oknie hero ≥ tło + 6 dB tuż przed hero;
- całość RMS ≥ -26 dBFS (głośność robocza jak w dawnej fabryce);
- udział energii >6 kHz ≤ 20 % (ochrona przed „papierowym" charakterem).

Usage:
  python scripts/render_signature.py data/recipes/1.json --audit
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import coda_synth
import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
LIMITS = {"length_sec": 10.0, "hero_margin_db": 6.0, "rms_min_db": -26.0, "hf_share_max": 0.20}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def registry_path(kind: str) -> Path:
    return REPO / "data" / "library" / f"{kind}.json"


def find_entry(kind: str, entry_id: str) -> dict:
    data = load_json(registry_path(kind))
    for entry in data["entries"]:
        if entry["id"] == entry_id:
            return entry
    raise SystemExit(f"{kind}: brak wpisu {entry_id!r} w {registry_path(kind)}")


def render(recipe: dict) -> tuple[np.ndarray, dict, list[str]]:
    warnings: list[str] = []
    length = float(recipe["length_sec"])
    mix = np.zeros((2, int(length * dsp.SR)))
    audit: dict = {"story_id": recipe["story_id"], "length_sec": length}

    bed_ref = recipe["background"]
    bed_entry = find_entry("backgrounds", bed_ref["id"])
    bed, _ = dsp.load_any(REPO / bed_entry["file"])
    seg = dsp.cut(bed, float(bed_ref.get("offset_sec", 0.0)), float(bed_ref.get("offset_sec", 0.0)) + length)
    if seg.shape[1] < int(length * dsp.SR):
        seg = dsp.loop_to_length(seg, int(length * dsp.SR))
        warnings.append("tło zapętlone (krótsze niż sygnatura)")
    seg = dsp.fade(seg, 0.8, 2.0)
    seg = dsp.normalize_rms(seg, float(bed_ref.get("target_db", -32.0)))
    mix = dsp.place(mix, seg, 0.0)
    audit["bed_rms"] = round(dsp.rms_db(seg), 1)

    hero_ref = recipe["hero"]
    hero_entry = find_entry("heroes", hero_ref["id"])
    hero, _ = dsp.load_any(REPO / hero_entry["file"])
    h_off = float(hero_ref.get("offset_sec", 0.0))
    h_len = hero_ref.get("length_sec")
    hero_seg = dsp.cut(hero, h_off, h_off + h_len) if h_len else hero[:, :]
    hero_seg = dsp.fade(hero_seg, 0.02, min(0.4, hero_seg.shape[1] / (2 * dsp.SR)))
    hero_seg = dsp.normalize_rms(hero_seg, float(hero_ref.get("target_db", -15.0)))
    hero_at = float(hero_ref.get("at_sec", 1.0))
    mix = dsp.place(mix, hero_seg, hero_at)
    audit["hero_at_sec"] = hero_at
    audit["hero_rms"] = round(dsp.rms_db(hero_seg), 1)
    pre_bed = dsp.rms_db(dsp.cut(mix, max(hero_at - 1.0, 0.0), hero_at)) - audit["bed_rms"]  # bed+nic więcej
    audit["hero_over_context_db"] = round(audit["hero_rms"] - dsp.rms_db(dsp.cut(mix, max(hero_at - 1.0, 0.0), hero_at)), 1)

    coda_ref = recipe.get("coda")
    if coda_ref:
        gesture = find_entry("gestures", coda_ref["gesture"])
        instrument = find_entry("instruments", coda_ref["instrument"])
        instrument = {**instrument, "samples": {k: str(REPO / v) for k, v in instrument["samples"].items()}
                      if "articulations" not in instrument.get("samples", {})
                      else {"articulations": {a: [str(REPO / f) for f in fs] for a, fs in instrument["samples"]["articulations"].items()}}}
        result = coda_synth.render_coda(gesture, instrument, seed=int(recipe.get("seed", 0)))
        warnings.extend(result.warnings)
        coda_wave = dsp.normalize_rms(result.wave, float(coda_ref.get("target_db", -21.0)))
        coda_at = float(coda_ref.get("at_sec", 4.0))
        mix = dsp.place(mix, coda_wave, coda_at)
        audit["coda_at_sec"] = coda_at
        audit["coda_notes"] = result.note_count
    return mix, audit, warnings


def check_gates(mix: np.ndarray, recipe: dict, audit: dict) -> list[str]:
    errors: list[str] = []
    length = audit["length_sec"]
    if length > LIMITS["length_sec"]:
        errors.append(f"długość {length:.2f} s > {LIMITS['length_sec']} s")
    rms = dsp.rms_db(mix)
    audit["mix_rms"] = round(rms, 1)
    if rms < LIMITS["rms_min_db"]:
        errors.append(f"całość {rms:.1f} dB < {LIMITS['rms_min_db']} dB")
    margin = audit.get("hero_over_context_db", -99.0)
    if margin < LIMITS["hero_margin_db"]:
        errors.append(f"hero {margin:.1f} dB nad kontekstem < {LIMITS['hero_margin_db']} dB")
    share = dsp.spectral_share(mix, 6000.0)
    audit["hf_share"] = round(share, 3)
    if share > LIMITS["hf_share_max"]:
        errors.append(f"udział >6 kHz {share:.1%} > {LIMITS['hf_share_max']:.0%}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--out", type=Path, help="domyślnie audio/signatures/<id>.mp3")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--force", action="store_true", help="zapisz mimo bramek QA (tylko warsztat)")
    args = parser.parse_args()
    recipe = load_json(args.recipe)
    out = args.out or (REPO / "audio" / "signatures" / f"{recipe['story_id']}.mp3")
    if out.name != f"{recipe['story_id']}.mp3" and not out.name.startswith("gate_"):
        raise SystemExit("nazwa produktu końcowego musi być <id>.mp3")
    mix, audit, warnings = render(recipe)
    mix = dsp.peak_ceiling(mix, 0.92)
    errors = check_gates(mix, recipe, audit)
    for warning in warnings:
        print(f"! {warning}")
    if args.audit:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
    if errors and not args.force:
        for error in errors:
            print(f"BRAK QA: {error}")
        raise SystemExit(1)
    dsp.encode_mp3(out, mix)
    print(f"OK: {out}  (RMS {audit['mix_rms']} dB, hero +{audit['hero_over_context_db']} dB, HF {audit['hf_share']:.1%})")
    if errors:
        print("(zapisano z --force mimo bramek)")


if __name__ == "__main__":
    main()
