#!/usr/bin/env python3
"""QA score calculation shared by the production pipeline and the UI metadata."""
from __future__ import annotations


def calculate_qa_score(*, climax_ratio: float, dc_ok: bool = True, peak_ok: bool = True, continuity_ok: bool = True) -> dict:
    """Mirror the scoring rule from legacy audio_qa_engine.py.

    A failed technical gate returns the same early-failure bands as the legacy
    auditor. A passing track receives 70 base points plus up to 30 points for
    dramaturgical contrast.
    """
    if not dc_ok:
        return {"score": 0.0, "base": 0.0, "dramaturgy": 0.0, "status": "fail: DC offset"}
    if not peak_ok:
        return {"score": 20.0, "base": 20.0, "dramaturgy": 0.0, "status": "fail: peak/headroom"}
    if not continuity_ok:
        return {"score": 40.0, "base": 40.0, "dramaturgy": 0.0, "status": "fail: continuity"}
    dramaturgy = min(30.0, max(0.0, climax_ratio * 6.0))
    return {"score": round(min(100.0, 70.0 + dramaturgy), 1), "base": 70.0, "dramaturgy": round(dramaturgy, 1), "status": "pass"}
