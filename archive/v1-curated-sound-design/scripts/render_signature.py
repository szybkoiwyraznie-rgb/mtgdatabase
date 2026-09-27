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
LIMITS = {"length_sec": 10.0, "hero_margin_db": 6.0, "rms_min_db": -26.0, "hf_share_max": 0.20,
          "note_attack_margin_db": 2.5, "note_attack_window_sec": 0.30}
# note_attack_*: twarde „słychać wszystkie klocki" — każda nuta kodu musi dawać mierzalny
# atak w finalnym mixie: RMS w oknie ataku ≥ RMS kontekstu tuż przed +2,5 dB.
# AUTOKALIBRACJA: render sam podbija maskowane nuty o brakujący margin (+0,5 dB zapasu,
# sufit 8 dB, ≤6 iteracji). Wszystkie podbicia lądują w warnings i audycie.


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
    mix_len = int(length * dsp.SR)
    audit: dict = {"story_id": recipe["story_id"], "length_sec": length}

    bed_ref = recipe["background"]
    bed_entry = find_entry("backgrounds", bed_ref["id"])
    bed, _ = dsp.load_any(REPO / bed_entry["file"])
    seg = dsp.cut(bed, float(bed_ref.get("offset_sec", 0.0)), float(bed_ref.get("offset_sec", 0.0)) + length)
    if seg.shape[1] < mix_len:
        seg = dsp.loop_to_length(seg, mix_len)
        warnings.append("tło zapętlone (krótsze niż sygnatura)")
    seg = dsp.fade(seg, 0.8, 2.0)
    seg = dsp.normalize_rms(seg, float(bed_ref.get("target_db", -32.0)))
    base_chunk = seg[:, :mix_len]
    audit["bed_rms"] = round(dsp.rms_db(base_chunk), 1)

    hero_ref = recipe["hero"]
    hero_entry = find_entry("heroes", hero_ref["id"])
    hero, _ = dsp.load_any(REPO / hero_entry["file"])
    h_off = float(hero_ref.get("offset_sec", 0.0))
    h_len = hero_ref.get("length_sec")
    hero_seg = dsp.cut(hero, h_off, h_off + h_len) if h_len else hero[:, :]
    hero_seg = dsp.fade(hero_seg, 0.02, min(0.4, hero_seg.shape[1] / (2 * dsp.SR)))
    hero_seg = dsp.normalize_rms(hero_seg, float(hero_ref.get("target_db", -15.0)))
    hero_at = float(hero_ref.get("at_sec", 1.0))
    audit["hero_at_sec"] = hero_at
    audit["hero_rms"] = round(dsp.rms_db(hero_seg), 1)
    audit["hero_over_context_db"] = round(
        audit["hero_rms"] - dsp.rms_db(dsp.cut(base_chunk, max(hero_at - 1.0, 0.0), hero_at)), 1)

    # tło + hero = kanwa, na której autokalibracja sprawdza ataki nut kodu
    base_mix = dsp.place(np.zeros((2, mix_len)), base_chunk, 0.0)
    base_mix = dsp.place(base_mix, hero_seg, hero_at)
    mix = base_mix.copy()

    coda_ref = recipe.get("coda")
    if coda_ref:
        gesture = find_entry("gestures", coda_ref["gesture"])
        instrument = find_entry("instruments", coda_ref["instrument"])
        instrument = {**instrument, "samples": {k: str(REPO / v) for k, v in instrument["samples"].items()}
                      if "articulations" not in instrument.get("samples", {})
                      else {"articulations": {a: [str(REPO / f) for f in fs] for a, fs in instrument["samples"]["articulations"].items()}}}
        coda_at = float(coda_ref.get("at_sec", 4.0))
        target = float(coda_ref.get("target_db", -21.0))
        seed = int(recipe.get("seed", 0))
        n_notes = len(gesture.get("notes", []))
        # target_db receptury = poziom RMS POJEDYNCZEJ nuty (przed velocity), nie całej
        # kody. AUTOKALIBRACJA: tę samą bramkę ataków, którą pilnuje check_gates,
        # render mierzy w locie i podbija maskowane nuty do +2,5 dB (+0,5 dB zapasu).
        plan = [0.0] * n_notes
        want_mix_len = int(length * dsp.SR)
        mix = None
        result = None
        for _iteration in range(6):
            result = coda_synth.render_coda(gesture, instrument, seed=seed,
                                            level_ref_db=target, gain_plan=plan,
                                            damp_db=float(coda_ref.get("damp_db", 0.0)))
            candidate = dsp.place(base_mix.copy(), result.wave, coda_at)
            if candidate.shape[1] > want_mix_len:
                candidate = dsp.fade(candidate[:, :want_mix_len].copy(), 0.0, min(1.6, length * 0.3))
            width = float(LIMITS["note_attack_window_sec"])
            need = float(LIMITS["note_attack_margin_db"]) + 0.5
            ok = True
            for event in result.events:
                t = coda_at + event["on_sec"]
                seg_on = dsp.cut(candidate, t, t + width)
                if seg_on.shape[1] < int(0.1 * dsp.SR):
                    continue
                seg_ctx = dsp.cut(candidate, max(t - width, 0.0), t)
                ctx = dsp.rms_db(seg_ctx) if seg_ctx.shape[1] else -80.0
                margin = dsp.rms_db(seg_on) - ctx
                if margin < need:
                    gain = min(need - margin + 0.5, 8.0 - plan[event["index"]])
                    if gain <= 0:
                        continue
                    plan[event["index"]] += gain
                    ok = False
            if ok:
                break
        warnings.extend(result.warnings)
        for idx, boost in enumerate(plan):
            if boost:
                warnings.append(f"autokalibracja nuty {idx} kody: +{boost:.1f} dB (maskowanie kontekstu)")
        mix = dsp.place(base_mix.copy(), result.wave, coda_at)
        want_mix_len = mix_len
        if mix.shape[1] > want_mix_len:
            over = (mix.shape[1] - want_mix_len) / dsp.SR
            mix = dsp.fade(mix[:, :want_mix_len].copy(), 0.0, min(1.6, length * 0.3))
            warnings.append(f"ogon kody ucięty o {over:.2f} s w master-fade do {length:.2f} s")
        audit["coda_at_sec"] = coda_at
        audit["coda_notes"] = result.note_count
        audit["coda_notes_total"] = n_notes
        audit["coda_note_ons"] = sorted(round(coda_at + ev["on_sec"], 3) for ev in result.events)
        audit["coda_boosts_db"] = [round(b, 1) for b in plan if b]
        audit["coda_rms"] = round(dsp.rms_db(result.wave), 1)
    else:
        # twarde dopasowanie długości produktu (jak wyżej, dla śladu bez kodu)
        want = int(length * dsp.SR)
        if mix.shape[1] > want:
            over = (mix.shape[1] - want) / dsp.SR
            mix = mix[:, :want].copy()
            mix = dsp.fade(mix, 0.0, min(1.6, length * 0.3))
            warnings.append(f"ogon kody ucięty o {over:.2f} s w master-fade do {length:.2f} s")
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
    # bramka słyszalności kodu: żadna nuta z gestu nie może zniknąć w mixie
    ons = audit.get("coda_note_ons") or []
    if ons:
        total = audit.get("coda_notes_total")
        placed = audit.get("coda_notes")
        if total is not None and placed is not None and placed < total:
            errors.append(f"koda: {total - placed} z {total} nut gestu niezagranych (adaptacja rejestru)")
        width = float(LIMITS["note_attack_window_sec"])
        margins: list[float] = []
        for t in sorted(set(round(float(t), 3) for t in ons)):
            seg_on = dsp.cut(mix, t, t + width)
            if seg_on.shape[1] < int(0.1 * dsp.SR):
                continue  # nuta ucięta w master-fade: niedostateczna na bramkę
            seg_ctx = dsp.cut(mix, max(t - width, 0.0), t)
            ctx = dsp.rms_db(seg_ctx) if seg_ctx.shape[1] else -80.0
            margin_note = dsp.rms_db(seg_on) - ctx
            margins.append(round(margin_note, 1))
            if margin_note < LIMITS["note_attack_margin_db"]:
                errors.append(f"nuta kody o {t:.2f} s: atak {margin_note:+.1f} dB ponad kontekst "
                              f"(< {LIMITS['note_attack_margin_db']} dB)")
        if margins:
            audit["note_attack_margins_db"] = margins
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
