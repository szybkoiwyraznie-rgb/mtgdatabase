#!/usr/bin/env python3
"""Bramka g006 — „wrzask-wojenny-goblinów", runda 3: Poważna rodzina.

Po werdyktach g004 (kreskówka) i g005 (pitch-down nie leczy wady rodziny):
zmiana RODZINY ŹRÓDŁA. Rubberduck „80 creature SFX" (OGA CC0) — kit
stworów z mocnym pasmem głosu 200–900 Hz (grunt/troll), czyli materiał
pokroju „pierścieniowych" orków, nie Smerfów. 3 warianty tej rodziny,
lekkie obniżenie (−2…−3 półtony) + saturacja na ziarno.

- h.1: grunt-02 (pk 213 Hz, 78% pasma głosu) −2 st — warchant wojownika;
- h.2: troll-02 (0,81 s, 59% pasma) −3 st — ochrypły rozkaz;
- h.3: duet grunt-02 + troll-01 @ +0,30 s −3 st — chant klanu.

Usage:
  python scripts/build_gate_g006.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g006"
CAND = GATE / "candidates"
sys.path.insert(0, str(REPO / "scripts"))
import build_gate_g003 as g003  # noqa: E402  (to_roar, soft_limit)
import build_gate_g004 as g004  # noqa: E402  (oga_source)

KIT = Path("/tmp/atomcut/packs/opengameart-80-cc0-creature-sfx/audio")
SRC = g004.oga_source("80 creature SFX", "rubberduck",
                      "https://opengameart.org/content/80-cc0-creature-sfx",
                      "packs/opengameart-80-cc0-creature-sfx")


def make_chant(name: str, label: str, title: str, entry_id: str,
               layers: list[dict], semitones_down: float, desc: str,
               character: str) -> dict:
    sr = dsp.SR
    waves: dict[str, np.ndarray] = {}
    for b in layers:
        if b["file"] not in waves:
            waves[b["file"]], _ = dsp.load_any(KIT / b["file"])
    total = max(int(b.get("at", 0.0) * sr) + waves[b["file"]].shape[1] for b in layers)
    comp = np.zeros((2, total), dtype=np.float32)
    for b in layers:
        at = int(b.get("at", 0.0) * sr)
        w = waves[b["file"]]
        comp[:, at:at + w.shape[1]] += w * b.get("gain", 1.0)
    out_wave = g003.to_roar(comp, semitones_down, hp_hz=50.0, lp_hz=4800.0, drive=1.4)
    out_wave = g003.soft_limit(out_wave, crest_db=12.0)
    out_wave = dsp.normalize_rms(out_wave, -15.0)
    out_wave = dsp.fade(out_wave, 0.005, min(0.2, out_wave.shape[1] / sr * 0.22))
    out = CAND / f"{name}.mp3"
    dsp.encode_mp3(out, out_wave)
    dur = round(out_wave.shape[1] / sr, 2)
    files_txt = " + ".join(
        f"{b['file'][:-4]}{' @ +' + str(b['at']) + ' s' if b.get('at') else ''}"
        for b in layers)
    source = {**SRC, "notes": f"{SRC['notes']}; {files_txt}; obniżenie {semitones_down:.0f} półtonów"}
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": f"{SRC['title']} — {SRC['license']}",
        "entry": {
            "id": entry_id,
            "role": "poważny okrzyk wojenny drobnej bandy jako hero fabuły plemiennej",
            "character": character, "distance": "bliski", "energy": "wysoka",
            "duration_sec": dur, "desc": desc,
            "good_for": "warcry Jundu/Hordy, otwarcie starcia, klan przy ogniu",
            "bad_for": "kameralność, elegancja, samotny strzelec",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "source": source,
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    candidates = [
        make_chant("h_grunt_war", "h.1", "warchant wojownika", "orc_wargrunt_01",
                   layers=[dict(file="grunt-02.m4a")], semitones_down=2.0,
                   desc="najgłębszy głos kitu (78% energii w paśmie głosu, pik 213 Hz) obniżony o 2 półtony — pojedynczy, ciężki okrzyk",
                   character="głuchy, krótki, groźny"),
        make_chant("h_bark_order", "h.2", "ochrypły rozkaz", "orc_order_01",
                   layers=[dict(file="troll-02.m4a")], semitones_down=3.0,
                   desc="trollowy głos (0,81 s) pełne 3 półtony niżej — brzmi jak rozkaz nadawanego przez gardło zwierzę",
                   character="gardłowy, rozkazowy"),
        make_chant("h_chant_duo", "h.3", "chant klanu (duet)", "orc_chant_duo_01",
                   layers=[dict(file="grunt-02.m4a"),
                           dict(file="troll-01.m4a", at=0.30, gain=0.85)],
                   semitones_down=3.0,
                   desc="grunt + trollowy głos 0,30 s później, razem 3 półtony niżej — plemienna odpowiedź za wodzem",
                   character="wielogłos, plemienny"),
    ]
    manifest = {
        "id": "g006",
        "created": date.today().isoformat(),
        "note": ("Runda 3 wrzasku wojennego po g004 (kreskówka) i g005 (pitch nie leczy "
                 "rodziny): nowa rodzina — rubberduck creature kit (paso głosowe), "
                 "cel: gobliny pokroju „Władcy Pierścieni”. Etykiety h.*."),
        "entries": [{
            "slug": "wrzask-wojenny-goblinów",
            "kind": "heroes",
            "role": "poważny okrzyk wojenny drobnej bandy jako hero fabuły plemiennej",
            "candidates": candidates,
        }],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cand in candidates:
        f = CAND / Path(cand["file"]).name
        w, _ = dsp.load_any(f)
        x = w.mean(axis=0)
        sp = np.abs(np.fft.rfft(x * np.hanning(x.size)))
        fr = np.fft.rfftfreq(x.size, 1 / dsp.SR)
        cent = (sp * fr).sum() / max(sp.sum(), 1e-9)
        pk = fr[np.argmax(sp)]
        band = sp[(fr > 200) & (fr < 900)].sum() / max(sp.sum(), 1e-9)
        print(f"{cand['label']} {f.name:<20s} {cand['entry']['duration_sec']:5.2f}s  "
              f"RMS {dsp.rms_db(w):6.1f} dB  peak {np.abs(x).max():.2f}  "
              f"cent {cent:4.0f} Hz  pik {pk:4.0f} Hz  pasmo głosu {band:.0%}")


if __name__ == "__main__":
    main()
