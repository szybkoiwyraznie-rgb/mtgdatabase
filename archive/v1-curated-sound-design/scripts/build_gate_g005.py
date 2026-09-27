#!/usr/bin/env python3
"""Bramka g005 — „wrzask-wojenny-goblinów", runda 2 (pitch-down).

Werdykt g004 dla wpisu: żaden — „brzmią jak kreskówka, g.1 najlepszy,
ale za wysoki". Remedium zgodne z doktryną (warianty jednej rodziny):
TA SAMA paczka Goblins Sound Pack (artisticdude, OGA CC0) obniżona
półtonowo — z piskliwej kreskówki robi się ogrowata horda Jundu.

Trzy warianty, wszystkie z goblin-3/goblin-12/goblin-9:
- w.1: goblin-3 (ten „najlepszy") −5 półtonów — dowódca,
- w.2: goblin-12 (ochrypły) −6 półtonów — niskie warknięcie,
- w.3: duet goblin-3+goblin-9 −4 półtony — chant ze zwolennikiem.

Usage:
  python scripts/build_gate_g005.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g005"
CAND = GATE / "candidates"
sys.path.insert(0, str(REPO / "scripts"))
import build_gate_g003 as g003  # noqa: E402  (to_roar, soft_limit)
import build_gate_g004 as g004  # noqa: E402  (oga_source)

GOBL = Path("/tmp/atomcut/packs/opengameart-goblins-sound-pack/audio")
SRC = g004.oga_source("Goblins Sound Pack", "artisticdude",
                      "https://opengameart.org/content/goblins-sound-pack",
                      "packs/opengameart-goblins-sound-pack")


def make_warcry(name: str, label: str, title: str, entry_id: str,
                layers: list[dict], semitones_down: float, norm_db: float,
                desc: str, character: str) -> dict:
    """Wariant warcry: dokładki tej samej paczki + pitch-down przez resample."""
    sr = dsp.SR
    waves = {}
    for b in layers:
        fn = b["file"]
        if fn not in waves:
            waves[fn], _ = dsp.load_any(GOBL / fn)
    total = max(int(b.get("at", 0.0) * sr) + waves[b["file"]].shape[1] for b in layers)
    comp = np.zeros((2, total), dtype=np.float32)
    for b in layers:
        at = int(b.get("at", 0.0) * sr)
        w = waves[b["file"]]
        comp[:, at:at + w.shape[1]] += w * b.get("gain", 1.0)
    out_wave = g003.to_roar(comp, semitones_down, hp_hz=60.0, lp_hz=5500.0, drive=1.35)
    out_wave = g003.soft_limit(out_wave, crest_db=12.0)
    out_wave = dsp.normalize_rms(out_wave, norm_db)
    out_wave = dsp.fade(out_wave, 0.005, min(0.2, out_wave.shape[1] / sr * 0.22))
    out = CAND / f"{name}.mp3"
    dsp.encode_mp3(out, out_wave)
    dur = round(out_wave.shape[1] / sr, 2)
    files_txt = " + ".join(
        f"{b['file'][0:-4]}{' @ +' + str(b['at']) + ' s' if b.get('at') else ''}"
        for b in layers)
    source = {**SRC, "notes": f"{SRC['notes']}; {files_txt}; obniżenie {semitones_down:.0f} półtonów (tempo x{2 ** (semitones_down / 12.0):.2f})"}
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": f"{SRC['title']} — {SRC['license']}",
        "entry": {
            "id": entry_id,
            "role": "szaleńczy okrzyk wojenny drobnej bandy jako hero fabuły plemiennej",
            "character": character, "distance": "bliski", "energy": "wysoka",
            "duration_sec": dur, "desc": desc,
            "good_for": "warcry hordy, Jund, wojna plemion, otwarcie starcia",
            "bad_for": "kameralne scenerie, samotny łowca, eleganckie karty",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "source": source,
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    candidates = [
        make_warcry(
            "w_horde_chief", "w.1", "dowódca bandy (obniżony g.1)", "horde_warcry_01",
            layers=[dict(file="goblin-3.m4a")],
            semitones_down=5.0, norm_db=-15.0,
            desc="ten sam krzyk, który był „najlepszy” w g004 (goblin-3), ale o 5 półtonów niżej — bez kreskówkowości",
            character="niski, rozkazowy, ogrowaty"),
        make_warcry(
            "w_horde_growl", "w.2", "ochrypłe warknięcie", "horde_warcry_02",
            layers=[dict(file="goblin-12.m4a")],
            semitones_down=6.0, norm_db=-15.0,
            desc="ochrypły goblin-12 pełne 6 półtonów w dół — już „ogr” niż „goblin”, zacięte gardło",
            character="ochrypły, zacięty, nisko"),
        make_warcry(
            "w_horde_duo", "w.3", "chant ze zwolennikiem", "horde_warcry_03",
            layers=[dict(file="goblin-3.m4a"),
                    dict(file="goblin-9.m4a", at=0.35, gain=0.85)],
            semitones_down=4.0, norm_db=-15.0,
            desc="dowódca z g004 + drugi głos paczki 0,35 s później, razem 4 półtony niżej — mini-horda",
            character="wielogłos, plemienny chant"),
    ]
    manifest = {
        "id": "g005",
        "created": date.today().isoformat(),
        "note": ("Runda 2 wpisu wrzasku wojennego po werdykcie g004 (kreskówka/za wysoki): "
                 "TA SAMA paczka CC0 obniżona 4–6 półtonów — warianty jednej rodziny, "
                 "zgodnie z doktryną. Etykiety w.*."),
        "entries": [{
            "slug": "wrzask-wojenny-goblinów",
            "kind": "heroes",
            "role": "szaleńczy okrzyk wojenny drobnej bandy jako hero fabuły plemiennej",
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
        print(f"{cand['label']} {f.name:<22s} {cand['entry']['duration_sec']:5.2f}s  "
              f"RMS {dsp.rms_db(w):6.1f} dB  peak {np.abs(x).max():.2f}  "
              f"centroid {cent:4.0f} Hz  pik {pk:4.0f} Hz")


if __name__ == "__main__":
    main()
