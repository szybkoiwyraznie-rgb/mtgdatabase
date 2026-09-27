#!/usr/bin/env python3
"""Bramka g008 — tło „wąski zalany kanion" dla fabuły 2 (Coralhelm Guide).

Rola z narracji, nie z magazynu: merfolk prowadzi Balotha zalanym kanionem
wśród skał; „fontanny wody wzbijane jej cielskiem są jedynym dźwiękiem".
Potrzebne tło to woda uwięziona w kamieniu — chlupot z pogłosem skalnej
szczeliny, nie otwarte jezioro ani deszcz.

Rodzina źródła: Yellowstone Sound Library (NPS, domena publiczna).
„The Dragon's Mouth Spring" to woda bijąca o ściany jaskini — naturalny
pogłos kamienia jest w nagraniu, nie doklejony efektem. Trzy okna tego
samego nagrania różnią się charakterem chlupotu (sito: wahanie RMS w
podoknach 0,5 s oraz udział pasma > 4 kHz = ilość rozprysku).

Usage:
  python scripts/build_gate_g008.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g008"
CAND = GATE / "candidates"
SRC = Path("/tmp/ysl/The Dragon's Mouth/Sound Library - The Dragon's Mouth.mp3")
SOURCE = {
    "title": "Yellowstone Sound Library (NPS)",
    "author": "National Park Service",
    "license": "Public Domain (utwór rządu USA)",
    "url": "https://www.nps.gov/yell/learn/photosmultimedia/soundlibrary.htm",
    "channel": "git clone sparse z github.com/rosuH/YSL (mirror)",
}
TARGET_DB = -33.0


def make_bed(name: str, label: str, title: str, entry_id: str,
             start: float, end: float, desc: str, setting: str) -> dict:
    wave, _ = dsp.load_any(SRC)
    sr = dsp.SR
    seg = wave[:, int(start * sr):int(end * sr)].copy()
    # tło nie może wnosić dudnienia poniżej pasma wody (rumble mikrofonu)
    sos = butter(2, 70.0, btype="highpass", fs=sr, output="sos")
    seg = sosfiltfilt(sos, seg, axis=-1).astype(np.float32)
    seg = dsp.normalize_rms(seg, TARGET_DB)
    seg = dsp.fade(seg, 0.25, 0.4)
    out = CAND / f"{name}.mp3"
    dsp.encode_mp3(out, seg)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": "Yellowstone Sound Library (NPS) — domena publiczna",
        "entry": {
            "id": entry_id,
            "setting": setting,
            "desc": desc,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": round(seg.shape[1] / sr, 2),
            "level_ref_db": int(TARGET_DB),
            "loopable": True,
            "source": {**SOURCE,
                       "notes": f"The Dragon's Mouth {start:.1f}-{end:.1f} s "
                                "(woda bijąca o ściany jaskini — pogłos skalny jest "
                                "w nagraniu, nie doklejony)"},
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    candidates = [
        make_bed("k_cave_lap", "k.1", "woda chlupie o kamień", "flooded_canyon_01",
                 21.0, 29.0,
                 desc="najspokojniejsze okno nagrania: równomierny chlupot w kamiennej misie, "
                      "mało rozprysku (15% energii powyżej 4 kHz) — przejście, którym da się "
                      "iść cicho",
                 setting="zalany kanion / woda w skale"),
        make_bed("k_surge_rock", "k.2", "woda napiera na skałę", "flooded_canyon_02",
                 39.0, 47.0,
                 desc="okno o 4 dB głośniejsze, wyraźne uderzenia fali o ścianę (22% powyżej "
                      "4 kHz) — ciaśniejsza szczelina, woda pod naporem",
                 setting="zalany kanion / woda pod naporem"),
        make_bed("k_deep_echo", "k.3", "echo w głębi jaskini", "flooded_canyon_03",
                 60.0, 68.0,
                 desc="najgłębsze okno: chlupot słyszany z dystansu przez kamienny korytarz, "
                      "najwięcej pogłosu — jakby kanion ciągnął się dalej niż widać",
                 setting="zalany kanion / głęboka szczelina"),
    ]
    manifest = {
        "id": "g008",
        "created": date.today().isoformat(),
        "note": ("Tło do fabuły 2 (Coralhelm Guide): wąski zalany kanion Zendikaru. "
                 "Trzy okna jednego nagrania NPS „The Dragon's Mouth” — woda w kamieniu "
                 "z naturalnym pogłosem jaskini. Etykiety k.*."),
        "entries": [{
            "slug": "zalany-kanion",
            "kind": "backgrounds",
            "role": "tło fabuły 2: woda uwięziona w skalnej szczelinie, przez którą "
                    "przeciska się bestia",
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
        sub = [np.sqrt((x[j:j + dsp.SR // 2] ** 2).mean())
               for j in range(0, x.size - dsp.SR // 2, dsp.SR // 2)]
        stab = np.std(20 * np.log10(np.maximum(sub, 1e-9)))
        print(f"{cand['label']} {f.name:<16s} {cand['entry']['duration_sec']:5.2f}s  "
              f"RMS {dsp.rms_db(w):6.1f} dB  cent {(sp * fr).sum() / sp.sum():5.0f} Hz  "
              f"rozprysk>4k {sp[fr > 4000].sum() / sp.sum():4.0%}  wahanie {stab:4.1f} dB")


if __name__ == "__main__":
    main()
