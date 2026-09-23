#!/usr/bin/env python3
"""Bramka g007 — „wrzask-wojenny-goblinów", runda 4: prawdziwe gardło.

Trzy odrzucone rundy (g004 surowe gobliny, g005 pitch-down tych samych,
g006 kit stworów) miały wspólną wadę: wszystkie źródła to wokalizacje
UDAWANE pod stwora — stąd „Smerfy". Technika z filmowego fantasy jest
odwrotna: bierze się PRAWDZIWY ludzki wrzask (aktor, tłum), schodzi w dół
i dodaje ziarna. Rodzina: haeldb „Male Grunt/Yelling sounds" (62 nagrania,
OGA, CC0) — pasmo głosu 150–800 Hz sięga tu 41–66% energii, podczas gdy
kreskówkowe gobliny miały 4–22%.

Warianty (jedna rodzina, jedna rola — wrzask bojowy bandy):
- o.1: pojedynczy okrzyk wodza (3grunt1, −4 st);
- o.2: gardłowy rozkaz (yell7, −5 st, mocniejsze ziarno);
- o.3: horda — cztery głosy rozjechane w czasie i wysokości (−4 st).

Usage:
  python scripts/build_gate_g007.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g007"
CAND = GATE / "candidates"
sys.path.insert(0, str(REPO / "scripts"))
import build_gate_g003 as g003  # noqa: E402

KIT = Path("/tmp/atomcut/packs/opengameart-male-gruntyelling-sounds/audio")
SOURCE = {
    "kind": "oga-pack",
    "title": "Male Grunt/Yelling sounds",
    "author": "haeldb",
    "license": "CC0-1.0",
    "homepage": "https://opengameart.org/content/male-gruntyelling-sounds",
    "mirror": "github.com/novincode/atomcut-library",
    "path": "packs/opengameart-male-gruntyelling-sounds",
}


def trim_silence(wave: np.ndarray, thresh_db: float = -42.0) -> np.ndarray:
    """Obcina ciszę na brzegach — nagrania mają nawet 1 s zapasu."""
    x = np.abs(wave).max(axis=0)
    thr = 10 ** (thresh_db / 20) * max(x.max(), 1e-9)
    idx = np.flatnonzero(x > thr)
    if idx.size == 0:
        return wave
    a = max(0, idx[0] - int(0.01 * dsp.SR))
    b = min(wave.shape[1], idx[-1] + int(0.06 * dsp.SR))
    return wave[:, a:b]


def make_warcry(name: str, label: str, title: str, entry_id: str,
                layers: list[dict], semitones: float, drive: float,
                desc: str, character: str) -> dict:
    sr = dsp.SR
    cache: dict[str, np.ndarray] = {}
    for b in layers:
        if b["file"] not in cache:
            w, _ = dsp.load_any(KIT / b["file"])
            cache[b["file"]] = trim_silence(w)
    parts = []
    for b in layers:
        w = cache[b["file"]]
        if b.get("extra_semitones"):
            w = g003.to_roar(w, b["extra_semitones"], hp_hz=40.0, lp_hz=7000.0, drive=1.0)
        parts.append((int(b.get("at", 0.0) * sr), w * b.get("gain", 1.0)))
    total = max(at + w.shape[1] for at, w in parts)
    comp = np.zeros((2, total), dtype=np.float32)
    for at, w in parts:
        comp[:, at:at + w.shape[1]] += w
    out_wave = g003.to_roar(comp, semitones, hp_hz=55.0, lp_hz=5200.0, drive=drive)
    out_wave = g003.soft_limit(out_wave, crest_db=12.0)
    out_wave = dsp.normalize_rms(out_wave, -15.0)
    out_wave = dsp.fade(out_wave, 0.004, min(0.22, out_wave.shape[1] / sr * 0.2))
    out = CAND / f"{name}.mp3"
    dsp.encode_mp3(out, out_wave)
    files_txt = " + ".join(
        f"{b['file'][:-4]}"
        + (f" @ +{b['at']} s" if b.get("at") else "")
        + (f" ({b['extra_semitones']:+.0f} st)" if b.get("extra_semitones") else "")
        for b in layers)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": f"{SOURCE['title']} — haeldb, CC0",
        "entry": {
            "id": entry_id,
            "role": "wrzask bojowy bandy jako hero fabuły plemiennej",
            "character": character, "distance": "bliski", "energy": "wysoka",
            "duration_sec": round(out_wave.shape[1] / sr, 2), "desc": desc,
            "good_for": "warcry Jundu/Hordy, otwarcie starcia, banda przy ognisku",
            "bad_for": "kameralność, elegancja, samotny strzelec",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "source": {**SOURCE,
                       "notes": f"{files_txt}; zbiorcze obniżenie {semitones:.0f} półtonów, drive {drive}"},
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    candidates = [
        make_warcry("o_chief_shout", "o.1", "okrzyk wodza", "warband_cry_01",
                    layers=[dict(file="3grunt1.m4a")], semitones=4.0, drive=1.5,
                    desc="pojedynczy męski okrzyk (53% energii w paśmie gardła) obniżony o 4 półtony — jeden głos, który wydaje rozkaz",
                    character="gardłowy, rozkazujący, ludzki-ale-nie-ludzki"),
        make_warcry("o_guttural_order", "o.2", "gardłowy ryk rozkazu", "warband_cry_02",
                    layers=[dict(file="yell7.m4a")], semitones=5.0, drive=1.9,
                    desc="najniższy wrzask kitu (pik 641 Hz) 5 półtonów niżej z mocnym ziarnem — chrapliwy, zdarty",
                    character="chrapliwy, ciężki, brudny"),
        make_warcry("o_horde_charge", "o.3", "horda rusza", "warband_cry_03",
                    layers=[dict(file="3grunt1.m4a"),
                            dict(file="yell7.m4a", at=0.12, gain=0.8, extra_semitones=2.0),
                            dict(file="2yell8.m4a", at=0.26, gain=0.7),
                            dict(file="3yell5.m4a", at=0.40, gain=0.6, extra_semitones=-2.0)],
                    semitones=4.0, drive=1.6,
                    desc="cztery głosy rozjechane co ~0,13 s i rozstrojone — nie chórek, tylko banda, która podchwytuje krzyk wodza",
                    character="tłum, narastający, groźny"),
    ]
    manifest = {
        "id": "g007",
        "created": date.today().isoformat(),
        "note": ("Runda 4 wrzasku wojennego. Zmiana techniki, nie tylko rodziny: "
                 "prawdziwe męskie wrzaski (haeldb, CC0) obniżone i zaszorstkowane — "
                 "tak robi się orków w filmowym fantasy. Poprzednie rundy brały "
                 "wokalizacje udawane pod stwora, stąd „Smerfy”. Etykiety o.*."),
        "entries": [{
            "slug": "wrzask-wojenny-goblinów",
            "kind": "heroes",
            "role": "wrzask bojowy bandy jako hero fabuły plemiennej",
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
        band = sp[(fr > 150) & (fr < 800)].sum() / max(sp.sum(), 1e-9)
        print(f"{cand['label']} {f.name:<20s} {cand['entry']['duration_sec']:5.2f}s  "
              f"RMS {dsp.rms_db(w):6.1f} dB  cent {cent:4.0f} Hz  "
              f"pik {fr[np.argmax(sp)]:4.0f} Hz  pasmo gardła {band:.0%}")


if __name__ == "__main__":
    main()
