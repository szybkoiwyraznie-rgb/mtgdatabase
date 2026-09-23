#!/usr/bin/env python3
"""Bramka g014 — hero „odłamki odbite przez magiczną tarczę” dla fabuły 18.

Wylosowana fabuła Lotusguard Disciple pokazuje avena osłaniającego pilota:
iskry i odłamki uderzają w świeżo utworzoną barierę i odbijają się od niej.
Hero to fizyczny moment skutecznej ochrony, nie ogólny czar ani silnik pojazdu.

Źródłem są prawdziwe nagrania metalowych uderzeń (rubberduck, CC0). Trzy
warianty składają po trzy różne uderzenia z tej samej rodziny w jeden krótki
rozprysk; bez pitchowania i bez syntetycznej warstwy „force field”.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np

import sig_audio as dsp
import build_gate_g003 as gate_dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g014"
CAND = GATE / "candidates"
KIT = Path("/tmp/atomcut/packs/opengameart-100-cc0-metal-and-wood-sfx/audio")
SOURCE = {
    "title": "100 metal and wood SFX (OpenGameArt)",
    "author": "rubberduck",
    "license": "CC0 1.0 (public domain)",
    "url": "https://opengameart.org/content/100-cc0-metal-and-wood-sfx",
    "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
}


def compose(files: list[str], times: list[float], gains: list[float]) -> np.ndarray:
    parts = [dsp.load_any(KIT / f)[0] for f in files]
    total = max(int(t * dsp.SR) + p.shape[1] for t, p in zip(times, parts))
    out = np.zeros((2, total), dtype=np.float64)
    for part, at, gain in zip(parts, times, gains):
        i = int(at * dsp.SR)
        out[:, i:i + part.shape[1]] += part * gain
    out = gate_dsp.soft_limit(out, crest_db=12.0, rounds=5)
    out = dsp.normalize_rms(out, -15.0)
    return dsp.fade(out, 0.004, 0.09)


def candidate(name: str, label: str, title: str, entry_id: str,
              files: list[str], times: list[float], gains: list[float],
              desc: str, character: str) -> dict:
    wave = compose(files, times, gains)
    path = CAND / f"{name}.mp3"
    dsp.encode_mp3(path, wave)
    return {
        "label": label,
        "title": title,
        "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": "prawdziwe metalowe uderzenia — rubberduck / OpenGameArt, CC0",
        "entry": {
            "id": entry_id,
            "role": "seria odłamków odbitych przez świeżo utworzoną magiczną tarczę",
            "character": character,
            "distance": "bliski",
            "energy": "wysoka",
            "duration_sec": round(wave.shape[1] / dsp.SR, 2),
            "desc": desc,
            "good_for": "magiczna bariera, odbicie pocisków, ochrona w ostatniej chwili",
            "bad_for": "atak przebijający cel, ciężka brama, komediowy pancerz",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "source": {
                **SOURCE,
                "notes": ("packs/opengameart-100-cc0-metal-and-wood-sfx; "
                          + " + ".join(f"{f.removesuffix('.m4a')} @ {t:.2f}s"
                                     for f, t in zip(files, times))
                          + "; bez pitchowania i syntezy; mirror pack.json potwierdza CC0 1.0"),
            },
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    for old in CAND.glob("*.mp3"):
        old.unlink()
    candidates = [
        candidate(
            "s_solid_deflection", "s.1", "twarde odbicie", "shield_deflect_01",
            ["metal-hit-03.m4a", "metal-hit-01.m4a", "metal-hit-03.m4a"],
            [0.0, 0.22, 0.47], [1.0, 0.78, 0.62],
            "trzy zwarte uderzenia z czytelnym metalowym korpusem — bariera przyjmuje cięższe odłamki",
            "twardy, zwarty, ochronny",
        ),
        candidate(
            "s_ringing_barrier", "s.2", "dźwięczna bariera", "shield_deflect_02",
            ["metal-sheet-05.m4a", "metal-sheet-03.m4a", "metal-sheet-06.m4a"],
            [0.0, 0.17, 0.38], [0.9, 0.76, 0.64],
            "trzy dźwięczne odbicia o dłuższym metalowym ogonie — bariera odpowiada rezonansem",
            "dźwięczny, jasny, rezonujący",
        ),
        candidate(
            "s_rising_ricochet", "s.3", "narastający rykoszet", "shield_deflect_03",
            ["metal-hit-01.m4a", "metal-hit-03.m4a", "metal-hit-05.m4a"],
            [0.0, 0.19, 0.42], [0.58, 0.78, 1.0],
            "kolejne odbicia rosną i kończą się najwyraźniejszym pingiem — tarcza domyka się w ruchu",
            "narastający, sprężysty, triumfalny",
        ),
    ]
    manifest = {
        "id": "g014",
        "created": date.today().isoformat(),
        "note": ("Hero do wylosowanej fabuły 18 (Lotusguard Disciple): odłamki "
                 "odbijają się od magicznej tarczy chroniącej pilota. Trzy warianty "
                 "jednej roli z prawdziwych nagrań metalowych uderzeń. Etykiety s.*."),
        "entries": [{
            "slug": "odlamki-odbite-przez-tarcze",
            "kind": "heroes",
            "role": "seria odłamków odbitych przez świeżo utworzoną magiczną tarczę",
            "candidates": candidates,
        }],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cand in candidates:
        wave, _ = dsp.load_any(GATE / cand["file"])
        peak = 20 * np.log10(max(float(np.max(np.abs(wave))), 1e-9))
        print(f"{cand['label']} {Path(cand['file']).name:<24s} "
              f"{wave.shape[1] / dsp.SR:4.2f}s RMS {dsp.rms_db(wave):5.1f} dB "
              f"peak {peak:5.1f} dB")


if __name__ == "__main__":
    main()
