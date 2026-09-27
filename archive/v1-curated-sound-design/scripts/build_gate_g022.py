#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g022 — hero `fala-rozbryzg`, runda 2 (po odrzuceniu gejzerów w g020:
„brzmiały jak hałas, nie rozbryzg"). Materiał: zwiad „water splash"
(run 36007698060) — prawdziwe fale i rozbryzgi, CC0. Etykieta `f`.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
from build_gate_g003 import soft_limit  # noqa: E402
from build_gate_g015 import loudest_window  # noqa: E402

GATE = REPO / "data" / "gates" / "g022"
CAND = GATE / "candidates"
BATCH = REPO / "legacy/source/sample_scout/freesound_water-splash"
CHANNEL = "sample-scout run 36007698060 (preview-hq-mp3); manifest sha256: data/gates/g022/source-manifest.json"

SRC = {
    "ocean": {"glob": "01-*", "title": "Ocean Waves Crashing... Big Lagoon, Redwood (Freesound)",
              "author": "CVLTIV8R", "url": "https://freesound.org/people/CVLTIV8R/sounds/711427/"},
    "quarry": {"glob": "02-*", "title": "Quarry Tunnel Ambience 1, Large Splash (Freesound)",
               "author": "ecfike", "url": "https://freesound.org/people/ecfike/sounds/"},
    "splash": {"glob": "04-*", "title": "water splash 2 (Freesound)",
               "author": "swordofkings128", "url": "https://freesound.org/people/swordofkings128/sounds/"},
}


def cand(name, label, title, entry_id, key, t0, dur, desc, character, notes):
    f = sorted(BATCH.glob(SRC[key]["glob"]))[0]
    w, _ = dsp.load_any(f)
    if t0 is None:
        t0 = loudest_window(w, dur)
    seg = w[:, int(t0 * dsp.SR):int((t0 + dur) * dsp.SR)].copy()
    seg = soft_limit(seg, crest_db=14.0, rounds=4)
    seg = dsp.normalize_rms(seg, -15.0)
    seg = dsp.fade(seg, 0.02, 0.3)
    peak = float(np.max(np.abs(seg)))
    ceil = dsp.db_to_gain(-1.0)
    if peak > ceil:
        seg *= ceil / peak
    dsp.encode_mp3(CAND / f"{name}.mp3", seg)
    s = SRC[key]
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": "freesound CC0 — prawdziwa woda",
        "entry": {
            "id": entry_id, "role": "uderzenie wody — fala, rozbryzg, plusk",
            "character": character, "distance": "bliski", "energy": "wysoka",
            "duration_sec": round(seg.shape[1] / dsp.SR, 2), "desc": desc,
            "good_for": "fala, rozbryzg, wynurzenie, wodny żywioł",
            "bad_for": "ogień, suche wnętrza, delikatne sceny",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "semantics": {"type": "fala-rozbryzg",
                          "traits": ["uderzenie wody", "rozbryzg", "naturalny", "dynamiczny"],
                          "bad_for": ["suchy", "ognisty", "metaliczny"]},
            "source": {"title": s["title"], "author": s["author"],
                       "license": "CC0 / Public Domain (wg API Freesound)",
                       "url": s["url"], "channel": CHANNEL,
                       "notes": notes + f" (okno od {t0:.1f} s)"},
        },
    }, t0


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    c1, t1 = cand("f_ocean_crash", "f.1", "fala rozbijająca się o brzeg", "wave_crash_01",
                  "ocean", None, 3.4,
                  "prawdziwa fala oceanu łamie się i rozlewa po kamieniach",
                  "łamiący się, szeroki, pienisty",
                  "najgłośniejsze okno nagrania fal; poziom, fade")
    c2, t2 = cand("f_big_splash", "f.2", "wielki plusk w toni", "wave_crash_02",
                  "quarry", None, 3.0,
                  "pojedynczy wielki plusk z echem podziemnej toni",
                  "pojedynczy, głęboki, z echem",
                  "okno wielkiego plusku; poziom, fade")
    c3, t3 = cand("f_quick_splash", "f.3", "szybki rozbryzg", "wave_crash_03",
                  "splash", 0.0, 1.9,
                  "krótki dynamiczny rozbryzg — czysty chlust bez tła",
                  "krótki, czysty, dynamiczny",
                  "całość 1.9 s; poziom, fade")
    cands = [c1, c2, c3]
    manifest = {
        "id": "g022", "created": "2026-09-24",
        "note": ("Runda 2 `fala-rozbryzg` po odrzuceniu gejzerów (g020). "
                 "Prawdziwe fale/rozbryzgi ze zwiadu. Typ woła 21 fabuł."),
        "entries": [{"slug": "fala-rozbryzg", "kind": "heroes",
                     "role": "jedyny klocek typu hero `fala-rozbryzg` (21 fabuł)",
                     "candidates": cands}],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for c in cands:
        p = GATE / c["file"]
        print(f"  {c['label']} {c['title']:34s} {p.stat().st_size/1024:5.0f} KB {c['entry']['duration_sec']} s")
    print("manifest g022 zapisany")


if __name__ == "__main__":
    main()
