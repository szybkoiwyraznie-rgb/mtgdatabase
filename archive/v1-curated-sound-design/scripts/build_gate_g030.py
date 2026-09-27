#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g030 — mood `groza-przerazenie` (najczęściej wołany brak, 59 fabuł).

Zakotwiczona na fabule 433 "Inspire Awe" (jedyny brak: koda mood
`groza-przerazenie`; tło/hero/instrumentacja już obsadzone przez resolver:
forest_day_01 / light_bloom_01 / b_bassdrum). Trzech kandydatów na jedyny
klocek typu (ADR 0004) — bez sięgania do sample-scout: to gesty autorskie
(nuty), podgląd renderowany neutralnie na b_piano_steinway (jak w g026/g027).

Definicja typu (taxonomy.json, mood.groza-przerazenie):
  "Groza, strach, makabra — koda mrozi."
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
import coda_synth  # noqa: E402

GATE = REPO / "data" / "gates" / "g030"
CAND = GATE / "candidates"

GESTURES = {
    # Nuty dobrane na siatce b_piano_steinway (48,50,54,56,60,64,68,72,74,76,80,84),
    # żeby podgląd nie zniekształcał kontrastów przez adaptację oktawową/rejestrową
    # (docelowy instrument fabuły 433 to b_bassdrum — bank wąski, gest i tak zostanie
    # zrealizowany rytmicznie; podgląd pokazuje INTENCJĘ typu, nie finalny render 433).
    "g_dread_freeze": {
        "label": "z.1",
        "semantic": "groza — zimny oddech, który zamiera nagle",
        "desc": "niski klaster (seksta... sekunda wielka C3/D3) narasta i dociąga wyższy ton "
                "napięcia, po czym urywa się bez wybrzmienia — strach, który mrozi w miejscu, "
                "nie gaśnie",
        "notes": [
            {"midi": 48, "on": 0.00, "off": 2.30, "vel": 0.55},
            {"midi": 50, "on": 0.00, "off": 2.30, "vel": 0.42},
            {"midi": 60, "on": 1.30, "off": 2.30, "vel": 0.35},
        ],
    },
    "g_dread_descent": {
        "label": "z.2",
        "semantic": "groza — pełznące zejście w makabryczny dół",
        "desc": "trzy stąpnięcia w dół jak kroki czegoś, co się zbliża, po czym nagły spadek "
                "w dysonansowe dno i podszyty pod spodem ton wielkiej sekundy — bez rozwiązania",
        "notes": [
            {"midi": 64, "on": 0.00, "off": 0.40, "vel": 0.55},
            {"midi": 60, "on": 0.40, "off": 0.80, "vel": 0.58},
            {"midi": 56, "on": 0.80, "off": 1.30, "vel": 0.62},
            {"midi": 48, "on": 1.25, "off": 3.00, "vel": 0.70},
            {"midi": 50, "on": 2.00, "off": 3.00, "vel": 0.40},
        ],
    },
    "g_dread_pulse": {
        "label": "z.3",
        "semantic": "groza — nawiedzone pulsowanie w ciszy",
        "desc": "pojedynczy ostry szturchaniec wysoko, potem cisza i niski powidok, w którym "
                "dopiero po chwili budzi się dysonansowy podszept — coś czeka, coś się skrada",
        "notes": [
            {"midi": 74, "on": 0.00, "off": 0.25, "vel": 0.65},
            {"midi": 48, "on": 0.85, "off": 2.60, "vel": 0.50},
            {"midi": 50, "on": 1.70, "off": 2.60, "vel": 0.42},
            {"midi": 54, "on": 2.20, "off": 2.90, "vel": 0.30},
        ],
    },
}


def gesture_candidates() -> list[dict]:
    instruments = json.loads((REPO / "data/library/instruments.json").read_text(encoding="utf-8"))
    piano = next(e for e in instruments["entries"] if e["id"] == "b_piano_steinway")
    piano_abs = {**piano, "samples": {m: str(REPO / p) for m, p in piano["samples"].items()}}
    cands: list[dict] = []
    for gid, spec in GESTURES.items():
        gesture = {"notes": spec["notes"], "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}}}
        r = coda_synth.render_coda(gesture, piano_abs, seed=433)
        for w in r.warnings:
            print(f"  ! {gid}: {w}")
        dsp.encode_mp3(CAND / f"{gid}.mp3", r.wave)
        cands.append({
            "label": spec["label"],
            "title": spec["semantic"].split("—", 1)[1].strip(),
            "file": f"candidates/{gid}.mp3",
            "desc": spec["desc"],
            "source": "gest autorski; podgląd na b_piano_steinway (render neutralny — instrument "
                      "docelowy fabuły 433 to b_bassdrum, ale typ mood jest niezależny od instrumentacji)",
            "entry": {
                "id": gid,
                "semantic": spec["semantic"],
                "desc": spec["desc"],
                "notes": spec["notes"],
                "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}},
                "instrument_tags": ["piano", "low_strings", "percussion_low", "organ"],
                "semantics": {"type": "groza-przerazenie",
                              "traits": ["dysonans", "niski", "zawieszony", "bez rozwiązania"],
                              "bad_for": ["radość", "triumf", "sielanka", "nadzieja"]},
            },
        })
        print(f"  {gid} zapisany")
    return cands


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": "g030",
        "created": "2026-09-25",
        "story_id": "433",
        "note": "Priorytet z resolver.py --survey: mood `groza-przerazenie` blokuje 59 fabuł — "
                "najczęstszy brak w katalogu. Zakotwiczone na fabule 433 \"Inspire Awe\" (jedyny "
                "brak fabuły; tło forest_day_01, hero light_bloom_01, instrumentacja b_bassdrum "
                "już obsadzone przez resolver). Trzy autorskie gesty pod definicję typu "
                "(taxonomy.json: \"Groza, strach, makabra — koda mrozi\"), podgląd neutralny "
                "na b_piano_steinway.",
        "entries": [
            {"slug": "koda-groza", "kind": "gestures",
             "role": "jedyny klocek typu kody `groza-przerazenie` (59 fabuł; slot a fabuły 433)",
             "candidates": gesture_candidates()},
        ],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest g030 zapisany ({len(manifest['entries'])} wpis)")


if __name__ == "__main__":
    main()
