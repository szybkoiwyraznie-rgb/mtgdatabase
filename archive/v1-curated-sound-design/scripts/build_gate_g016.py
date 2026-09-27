#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g016 — jedyny klocek typu tła `las-dzienny`.

Definicja typu (taxonomy v5): „Las za dnia: szum liści, ptaki, lekki wiatr
w koronach." Kandydatów przesłuchujemy POD TĘ DEFINICJĘ (lekcja g015 —
klocek obsadza typ, nie pojedynczą fabułę). Klocek od razu domyka obsadę
fabuł 468 (Cacophodon) i 578 (Savage Surge); docelowo woła go 67 fabuł.

Źródło: YSL — Yellowstone Sound Library (NPS, public domain), /tmp/ysl.
Obróbka przezroczysta: cięcie okna, poziom -33 dB RMS, fade.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
from build_gate_g015 import YSL_SRC, steadiest_window, finish_bg  # noqa: E402

GATE = REPO / "data" / "gates" / "g016"
CAND = GATE / "candidates"
YSL = Path("/tmp/ysl")


def bg_candidate(name, label, title, entry_id, src_file, t0, dur, desc, notes):
    wave, _ = dsp.load_any(src_file)
    seg = wave[:, int(t0 * dsp.SR):int((t0 + dur) * dsp.SR)].copy()
    seg = finish_bg(seg)
    path = CAND / f"{name}.mp3"
    dsp.encode_mp3(path, seg)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": f"{YSL_SRC['title']} — public domain",
        "entry": {
            "id": entry_id,
            "setting": "las za dnia",
            "desc": desc,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": round(seg.shape[1] / dsp.SR, 2),
            "level_ref_db": -33,
            "loopable": True,
            "semantics": {
                "type": "las-dzienny",
                "traits": ["ptaki", "szum liści", "dzień", "spokojny"],
                "bad_for": ["noc", "wnętrze", "martwa cisza"],
            },
            "source": dict(YSL_SRC, notes=notes),
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    dawn = YSL / "Dawn Chorus/Sound Library - Dawn Chorus.mp3"
    birds = YSL / "Birds - Bird Chorus/Sound Library - Bird Chorus.mp3"
    scape = YSL / "Soundscapes/Soundscapes.mp3"

    w_d, _ = dsp.load_any(dawn)
    w_b, _ = dsp.load_any(birds)
    w_s, _ = dsp.load_any(scape)
    t_d = steadiest_window(w_d, 8.0)
    t_b = steadiest_window(w_b, 8.0)
    t_s = steadiest_window(w_s, 8.0)
    print(f"okna: dawn @{t_d:.1f}s, birds @{t_b:.1f}s, soundscape @{t_s:.1f}s")

    entries = [{
        "slug": "las-dzienny",
        "kind": "backgrounds",
        "role": "jedyny klocek typu tła `las-dzienny` (woła go 67 fabuł; od razu domyka 468 i 578)",
        "candidates": [
            bg_candidate("d_dawn_chorus", "d.1", "poranny chór ptaków",
                         "forest_day_01", dawn, t_d, 8.0,
                         "gęsty poranny chór ptaków — las budzi się, wyraźne ptactwo blisko i w głębi",
                         f"Dawn Chorus, okno {t_d:.1f}–{t_d+8:.1f} s; poziom i fade"),
            bg_candidate("d_bird_chorus", "d.2", "dzienny chór w koronach",
                         "forest_day_02", birds, t_b, 8.0,
                         "równy dzienny śpiew ptaków w koronach — mniej gęsty, więcej powietrza między głosami",
                         f"Bird Chorus, okno {t_b:.1f}–{t_b+8:.1f} s; poziom i fade"),
            bg_candidate("d_soundscape", "d.3", "szeroki pejzaż dnia",
                         "forest_day_03", scape, t_s, 8.0,
                         "szeroki naturalny pejzaż — ptaki dalej, więcej tła przestrzeni i lekkiego wiatru",
                         f"Soundscapes, okno {t_s:.1f}–{t_s+8:.1f} s; poziom i fade"),
        ],
    }]

    manifest = {
        "id": "g016",
        "created": "2026-09-24",
        "note": ("Etap 5. Jedyny klocek typu `las-dzienny` (najczęściej wołany "
                 "typ tła: 67 fabuł). Kandydaci oceniani pod definicję typu, "
                 "nie pod pojedynczą fabułę (lekcja g015). Po akceptacji "
                 "produkcja fabuł 468 (Cacophodon) i 578 (Savage Surge) bez "
                 "dodatkowych bramek."),
        "entries": entries,
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for c in entries[0]["candidates"]:
        p = GATE / c["file"]
        print(f"  {c['label']} {c['title']:28s} {p.stat().st_size/1024:6.0f} KB")
    print("manifest g016 zapisany")


if __name__ == "__main__":
    main()
