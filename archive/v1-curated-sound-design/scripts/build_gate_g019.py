#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g019 — hero `marsz-oddzialu`, runda 2 (po odrzuceniu stylizacji
bębnowych z g018). Materiał: PRAWDZIWE kroki z zwiadu freesound
(run 36001624763, paczka legacy/source/sample_scout/freesound_marching-footsteps).

  m.1 — surowe okno prawdziwego marszu (lyghtningwither, „Marching Sound");
  m.2 — kolumna na żwirze: 4 warstwy tego samego PRAWDZIWEGO piechura
        (felix.blume) z przesunięciami — standardowa praktyka foley,
        żadnej syntezy ani bębnów;
  m.3 — kolumna na otoczakach: jak wyżej z nagrania guyburns.

Etykieta `m` (unikatowa — zasada z gate-protocol).
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

GATE = REPO / "data" / "gates" / "g019"
CAND = GATE / "candidates"
BATCH = REPO / "legacy/source/sample_scout/freesound_marching-footsteps"

SOURCES = {
    "march": {
        "file": "04-771884-marching-sound.mp3",
        "title": "Marching Sound (Freesound)", "author": "lyghtningwither",
        "url": "https://freesound.org/people/lyghtningwither/sounds/771884/",
    },
    "gravel": {
        "file": "02-779884-footsteps-wearing-leather-shoes-on-gravel.mp3",
        "title": "Footsteps wearing leather shoes on gravel (Freesound)", "author": "felix.blume",
        "url": "https://freesound.org/people/felix.blume/sounds/779884/",
    },
    "pebbles": {
        "file": "05-464800-footsteps-on-pebbles-m4a.mp3",
        "title": "Footsteps on pebbles (Freesound)", "author": "guyburns",
        "url": "https://freesound.org/people/guyburns/sounds/464800/",
    },
}
CHANNEL = ("sample-scout run 36001624763 (preview-hq-mp3; klucz API nie "
           "autoryzuje /download — lekcja 2026-09-24); manifest z sha256 w "
           "legacy/source/sample_scout/freesound_marching-footsteps/")


def src_meta(key):
    s = SOURCES[key]
    return {"title": s["title"], "author": s["author"],
            "license": "CC0 / Public Domain (wg API Freesound)",
            "url": s["url"], "channel": CHANNEL}


def finish(seg, rms=-15.0):
    seg = soft_limit(seg, crest_db=14.0, rounds=4)
    seg = dsp.normalize_rms(seg, rms)
    seg = dsp.fade(seg, 0.05, 0.35)
    peak = float(np.max(np.abs(seg)))
    ceil = dsp.db_to_gain(-1.0)
    if peak > ceil:
        seg *= ceil / peak
    return seg


def entry(entry_id, character, desc, notes, dur, key):
    return {
        "id": entry_id, "role": "miarowy marsz oddziału",
        "character": character, "distance": "średni", "energy": "średnia",
        "duration_sec": dur, "desc": desc,
        "good_for": "kolumna wojska, natarcie w szyku, patrol, falanga",
        "bad_for": "pojedynczy wędrowiec, skradanie, kawaleria",
        "file": f"audio/library/heroes/{entry_id}.mp3",
        "semantics": {"type": "marsz-oddzialu",
                      "traits": ["miarowy", "prawdziwe kroki", "wielu maszerujących"],
                      "bad_for": ["chaotyczny", "pojedynczy", "galop"]},
        "source": dict(src_meta(key), notes=notes),
    }


def layered_column(wave, t0, step_period, layers=4, dur=3.6, seed=575):
    """Kolumna z JEDNEGO prawdziwego piechura: warstwy przesunięte o ułamki
    kroku (jak w plutonie — nikt nie idzie idealnie równo)."""
    rng = np.random.default_rng(seed)
    out = np.zeros((2, int(dur * dsp.SR)))
    for lay in range(layers):
        off = t0 + lay * 7.31  # inne kroki tego samego nagrania
        jit = float(rng.uniform(0.05, 0.45)) * step_period
        seg = wave[:, int((off + jit) * dsp.SR):int((off + jit + dur) * dsp.SR)]
        n = min(seg.shape[1], out.shape[1])
        out[:, :n] += seg[:, :n] * dsp.db_to_gain(float(rng.uniform(-4.0, 0.0)))
    return out


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    cands = []

    # m.1 — surowy prawdziwy marsz
    w, _ = dsp.load_any(BATCH / SOURCES["march"]["file"])
    t0 = loudest_window(w, 3.6)
    seg = finish(w[:, int(t0 * dsp.SR):int((t0 + 3.6) * dsp.SR)].copy())
    dsp.encode_mp3(CAND / "m_real_march.mp3", seg)
    cands.append({
        "label": "m.1", "title": "prawdziwy marsz (surowe okno)",
        "file": "candidates/m_real_march.mp3",
        "desc": "nieprzetworzone okno nagrania maszerującego oddziału — krok co ~0,54 s",
        "source": "freesound CC0 — lyghtningwither",
        "entry": entry("troop_march_04", "miarowy, zwarty, naturalny",
                       "nieprzetworzone okno nagrania maszerującego oddziału — krok co ~0,54 s",
                       f"okno {t0:.1f}–{t0+3.6:.1f} s; tylko poziom i fade",
                       3.6, "march"),
    })

    # m.2 — kolumna na żwirze (4 warstwy prawdziwego piechura)
    w2, _ = dsp.load_any(BATCH / SOURCES["gravel"]["file"])
    t2 = loudest_window(w2[:, :int(120 * dsp.SR)], 30.0)
    seg2 = finish(layered_column(w2, t2, step_period=1.14))
    dsp.encode_mp3(CAND / "m_gravel_column.mp3", seg2)
    cands.append({
        "label": "m.2", "title": "kolumna na żwirze (4 warstwy)",
        "file": "candidates/m_gravel_column.mp3",
        "desc": "cztery warstwy PRAWDZIWYCH kroków po żwirze, przesunięte jak w plutonie — zero syntezy",
        "source": "freesound CC0 — felix.blume",
        "entry": entry("troop_march_05", "żwirowy, ciężki, wielonożny",
                       "cztery warstwy prawdziwych kroków po żwirze, przesunięte jak w plutonie",
                       f"4 warstwy z różnych fragmentów od {t2:.0f} s; przesunięcia losowe seed 575; poziom, fade",
                       3.6, "gravel"),
    })

    # m.3 — kolumna na otoczakach
    w3, _ = dsp.load_any(BATCH / SOURCES["pebbles"]["file"])
    seg3 = finish(layered_column(w3, 2.0, step_period=0.64))
    dsp.encode_mp3(CAND / "m_pebble_column.mp3", seg3)
    cands.append({
        "label": "m.3", "title": "kolumna na otoczakach (4 warstwy)",
        "file": "candidates/m_pebble_column.mp3",
        "desc": "cztery warstwy prawdziwych kroków po otoczakach — suchszy, ostrzejszy chrzęst",
        "source": "freesound CC0 — guyburns",
        "entry": entry("troop_march_06", "chrzęszczący, suchy, wielonożny",
                       "cztery warstwy prawdziwych kroków po otoczakach",
                       "4 warstwy z różnych fragmentów od 2 s; przesunięcia losowe seed 575; poziom, fade",
                       3.6, "pebbles"),
    })

    manifest = {
        "id": "g019", "created": "2026-09-24", "story_id": "575",
        "note": ("Runda 2 hero `marsz-oddzialu` po odrzuceniu stylizacji "
                 "bębnowych (g018). Prawdziwe kroki ze zwiadu freesound; "
                 "m.2/m.3 to wielowarstwowe złożenia PRAWDZIWYCH kroków "
                 "(praktyka foley), nie synteza. Domyka fabułę 575."),
        "entries": [{"slug": "marsz-oddzialu", "kind": "heroes",
                     "role": "jedyny klocek typu hero `marsz-oddzialu` (7 fabuł; domyka 575)",
                     "candidates": cands}],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for c in cands:
        p = GATE / c["file"]
        print(f"  {c['label']} {c['title']:36s} {p.stat().st_size/1024:5.0f} KB")
    print("manifest g019 zapisany")


if __name__ == "__main__":
    main()
