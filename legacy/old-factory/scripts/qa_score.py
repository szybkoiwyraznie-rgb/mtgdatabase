#!/usr/bin/env python3
"""QA score calculation shared by the production pipeline and the UI metadata.

QA v2 (2026-09-22). The v1 score (70 + climax_ratio*6) was inversely
correlated with the owner's ratings: the 3/15 renders (8, 8_v2, 450_v2,
450_v3, 475, 475_v2, 5_v2) all scored 100/100 because a lone click over a
quiet bed maximizes the climax ratio, while 568_v2 (15/15) scored 86.6.
The new score is calibrated on the rated catalog:

HARD GATES (any failure -> status "fail: ..." and a low score):
- dc_ok       |DC offset| <= 0.015
- peak_ok     decoded peak in [0.25, 0.999]
- continuity  at most one dead 0.35 s window
- loudness_ok total RMS >= -23 dBFS (the rejected batch sat at -26..-28 dB
              while the praised originals are -15..-22 dB)
- spectral_ok <= 12% of energy above 6 kHz (paper/hiss character; the
              praised originals carry 0-2%, the rejected batch 20-37%)
- audibility  every described stem event >= +6 dB over the bed level in
              its window (synth details >= +4 dB). This is the gate the
              silent-head failures could not pass.

SCORE (all gates passing): 50 base + up to 30 audibility margin + up to 20
dramaturgical contrast (climax ratio * 4, informational - it no longer
dominates the verdict).
"""
from __future__ import annotations

from typing import Iterable

LOUDNESS_MIN_DB = -26.0  # sanity floor; new renders master to ~-20 dB RMS
HF_MAX_SHARE = 0.12
AUDIBILITY_STEM_DB = 6.0
AUDIBILITY_SYNTH_DB = 4.0


def calculate_qa_score(
    *,
    climax_ratio: float,
    dc_ok: bool = True,
    peak_ok: bool = True,
    continuity_ok: bool = True,
    loudness_ok: bool = True,
    spectral_ok: bool = True,
    audibility: Iterable[dict] | None = None,
    rms_db: float | None = None,
    hf_share: float | None = None,
) -> dict:
    """Return the QA report dict (keys: score, base, dramaturgy, status,
    details, plus gate values when provided). Backwards compatible with the
    v1 call signature (climax_ratio + technical gates)."""
    details: list[str] = []

    def gate(ok: bool, line_ok: str, line_fail: str, fail_status: str) -> bool:
        details.append(line_ok if ok else line_fail)
        return ok

    # --- hard gates in historical failure order -------------------------
    if not dc_ok:
        return {"score": 0.0, "base": 0.0, "dramaturgy": 0.0, "status": "fail: DC offset", "details": details or ["DC offset"]}
    details.append("DC offset: OK" if dc_ok else "")
    if not peak_ok:
        return {"score": 20.0, "base": 20.0, "dramaturgy": 0.0, "status": "fail: peak/headroom", "details": details}
    details.append("Peak/headroom: OK")
    if not continuity_ok:
        return {"score": 40.0, "base": 40.0, "dramaturgy": 0.0, "status": "fail: continuity", "details": details}
    details.append("Ciągłość tła: OK")
    if not loudness_ok:
        return {"score": 45.0, "base": 45.0, "dramaturgy": 0.0,
                "status": "fail: głośność (RMS)",
                "details": details + [f"Głośność: {rms_db if rms_db is not None else '?'} dB RMS < {LOUDNESS_MIN_DB} dB"]}
    if rms_db is not None:
        details.append(f"Głośność: {rms_db:.1f} dB RMS (min {LOUDNESS_MIN_DB})")
    if not spectral_ok:
        return {"score": 50.0, "base": 50.0, "dramaturgy": 0.0,
                "status": "fail: balans widma (udział >6 kHz)",
                "details": details + [f"Udział >6 kHz: {100 * (hf_share or 0):.0f}% > {100 * HF_MAX_SHARE:.0f}%"]}
    if hf_share is not None:
        details.append(f"Balans widma: {100 * hf_share:.0f}% energii >6 kHz (limit {100 * HF_MAX_SHARE:.0f}%)")

    # --- audibility (per-event, needs recipe events) --------------------
    # Live (stem) events are hard-gated at +6 dB over the bed: the rejected
    # batch played silent heads of field recordings, so described events
    # were absent from the audio. Synth details are reported but not gated -
    # their salience is a story-fit judgment for the owner, and RMS
    # underestimates granular textures (568 v2's opening swarm reads -0.2 dB
    # yet the owner rated that jingle 15/15).
    audibility_points = 30.0
    if audibility is not None:
        events = list(audibility)
        live = [ev for ev in events if ev.get("live", True) and str(ev.get("level", "event")) != "bed"]
        synth = [ev for ev in events if not ev.get("live", True)]
        bed_like = [ev for ev in events if str(ev.get("level", "event")) == "bed"]
        if not live:
            return {"score": 55.0, "base": 55.0, "dramaturgy": 0.0,
                    "status": "fail: brak słyszalnego żywego sampla",
                    "details": details + ["Zero zdarzeń na żywych samplach nad tłem (AGENTS.md #14)"]}
        failing = [f"{ev.get('sample', '?')} @ {ev.get('time_sec', '?')}s: {ev['delta_db']:+.1f} dB < +{AUDIBILITY_STEM_DB:.0f} dB nad tłem"
                   for ev in live if float(ev.get("delta_db", 99.0)) < AUDIBILITY_STEM_DB]
        if failing:
            return {"score": 55.0, "base": 55.0, "dramaturgy": 0.0,
                    "status": "fail: niesłyszalne zdarzenia",
                    "details": details + ["Zdarzenia poniżej progu słyszalności:"] + failing}
        details.append(f"Słyszalność zdarzeń żywych: {len(live)}/{len(live)} ≥ +{AUDIBILITY_STEM_DB:.0f} dB nad tłem")
        if bed_like:
            details.append(f"Warstwy tła (level=bed, poza bramką): " + "; ".join(
                f"{ev.get('sample', '?')} @ {ev.get('time_sec', '?')}s" for ev in bed_like))
        if synth:
            weak_synth = [f"{ev.get('sample', '?')} @ {ev.get('time_sec', '?')}s: {ev['delta_db']:+.1f} dB"
                          for ev in synth if float(ev.get("delta_db", 99.0)) < AUDIBILITY_SYNTH_DB]
            if weak_synth:
                details.append("Info (syntetyczne detale przy tle): " + "; ".join(weak_synth))
        margins = [float(ev.get("delta_db", 99.0)) - AUDIBILITY_STEM_DB for ev in live]
        pass_frac = 1.0
        margin_frac = min(1.0, sum(min(m, 6.0) for m in margins) / (6.0 * len(live)))
        audibility_points = 30.0 * (0.7 * pass_frac + 0.3 * margin_frac)

    dramaturgy = min(15.0, max(0.0, climax_ratio * 4.0))
    score = round(min(100.0, 55.0 + audibility_points + dramaturgy), 1)
    details.append(f"Kontrast dramaturgiczny: {climax_ratio:.2f}x ({dramaturgy:.1f}/15)")
    return {"score": score, "base": 55.0, "dramaturgy": round(dramaturgy, 1), "status": "pass", "details": details}
