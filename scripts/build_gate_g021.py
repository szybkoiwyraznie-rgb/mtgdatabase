#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g021 — jedyny klocek typu hero `weszenie` (v6; domyka fabułę 193).

Materiał: zwiad freesound „dog sniffing" (run 36007326109) — prawdziwe
psie węszenie, CC0. Obróbka: okno, poziom, fade. Etykieta `w`.
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

GATE = REPO / "data" / "gates" / "g021"
CAND = GATE / "candidates"
BATCH = REPO / "legacy/source/sample_scout/freesound_dog-sniffing"
CHANNEL = "sample-scout run 36007326109 (preview-hq-mp3); manifest z sha256 w katalogu paczki"

SRC = {
    "td6d": {"file": "01-467762-dog-snif-sniffing-animal-breathing-search.wav.mp3",
             "title": "Dog - Snif - Sniffing - Animal - Breathing - Search (Freesound)",
             "author": "td6d", "url": "https://freesound.org/people/td6d/sounds/467762/"},
    "cepelak": {"file": "05-534005-2-3-dog-sniffing-wav.mp3",
                "title": "2-3 dog sniffing (Freesound)",
                "author": "15GPanskaCepelak_Adam",
                "url": "https://freesound.org/people/15GPanskaCepelak_Adam/sounds/534005/"},
    "caap": {"file": "03-566052-12-perritoolfateando-wav.mp3",
             "title": "12-PerritoOlfateando (Freesound)",
             "author": "Caap", "url": "https://freesound.org/people/Caap/sounds/566052/"},
}


def meta(key, notes):
    s = SRC[key]
    return {"title": s["title"], "author": s["author"],
            "license": "CC0 / Public Domain (wg API Freesound)",
            "url": s["url"], "channel": CHANNEL, "notes": notes}


def cand(name, label, title, entry_id, key, t0, dur, desc, character):
    files = list(BATCH.glob(SRC[key]["file"].split("-", 1)[0] + "-*"))
    assert files, SRC[key]["file"]
    w, _ = dsp.load_any(files[0])
    seg = w[:, int(t0 * dsp.SR):int((t0 + dur) * dsp.SR)].copy()
    seg = soft_limit(seg, crest_db=14.0, rounds=4)
    seg = dsp.normalize_rms(seg, -17.0)
    seg = dsp.fade(seg, 0.03, 0.25)
    peak = float(np.max(np.abs(seg)))
    ceil = dsp.db_to_gain(-1.0)
    if peak > ceil:
        seg *= ceil / peak
    dsp.encode_mp3(CAND / f"{name}.mp3", seg)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": "freesound CC0 — prawdziwe psie węszenie",
        "entry": {
            "id": entry_id, "role": "węszenie tropiciela przy tropie",
            "character": character, "distance": "bliski", "energy": "niska",
            "duration_sec": round(seg.shape[1] / dsp.SR, 2), "desc": desc,
            "good_for": "tropiciel, ogar, zwiadowca zwierzęcy, poszukiwanie śladu",
            "bad_for": "atak, warkot agresji, wielkie bestie",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "semantics": {"type": "weszenie",
                          "traits": ["pociągnięcia nosem", "rytmiczne", "skupione", "bliskie"],
                          "bad_for": ["agresywny", "głośny", "mechaniczny"]},
            "source": meta(key, f"okno {t0:.1f}–{t0+dur:.1f} s; poziom -17, fade; bez pitchowania"),
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    f1 = list(BATCH.glob("01-*"))[0]
    w1, _ = dsp.load_any(f1)
    t1 = loudest_window(w1, 3.0)
    cands = [
        cand("w_search_long", "w.1", "węszenie poszukujące (seria)", "sniff_track_01",
             "td6d", t1, 3.0,
             "gęsta seria pociągnięć nosem z oddechem — pies pracuje na tropie",
             "rytmiczny, pracowity, bliski"),
        cand("w_two_dogs", "w.2", "węszenie przy ziemi", "sniff_track_02",
             "cepelak", 1.0, 3.0,
             "węszenie tuż przy gruncie z krótkimi sapnięciami",
             "przyziemny, sapiący, skupiony"),
        cand("w_quick_snuffle", "w.3", "krótkie obwąchanie", "sniff_track_03",
             "caap", 0.0, 2.1,
             "krótkie, ciekawskie obwąchanie — dwa-trzy pociągnięcia i decyzja",
             "krótki, ciekawski, lekki"),
    ]
    manifest = {
        "id": "g021", "created": "2026-09-24", "story_id": "193",
        "note": ("Jedyny klocek typu `weszenie` (v6, decyzja właściciela przy "
                 "g020). Prawdziwe psie węszenie ze zwiadu; domyka fabułę 193."),
        "entries": [{"slug": "weszenie", "kind": "heroes",
                     "role": "jedyny klocek typu hero `weszenie` (domyka fabułę 193)",
                     "candidates": cands}],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for c in cands:
        p = GATE / c["file"]
        print(f"  {c['label']} {c['title']:34s} {p.stat().st_size/1024:5.0f} KB {c['entry']['duration_sec']} s")
    print("manifest g021 zapisany")


if __name__ == "__main__":
    main()
