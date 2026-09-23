#!/usr/bin/env python3
"""Bramka g011 — tło „zalany kanion", runda 4: prawdziwe nagrania terenowe.

Trzy odrzucone rundy pokazały, że tła żywiołów nie da się sfabrykować:
g008 syk gorącego źródła („wiatr”), g009 bulgot („gotująca się woda”),
g010 foley z pitch-downu („nienaturalnie nisko, jakby ktoś spitchował”).
Materiał pochodzi teraz z Internet Archive (Sample scout), z dwóch
nagrań terenowych o wolnej licencji:

* **GOLD TAPE 53/54 Water** (CC0) — bliski strumień na taśmie, gęste
  ciurkanie tuż przy mikrofonie;
* **Cedar Creek Park, Allentown PA** (Public Domain Mark, aporee) —
  szerszy, spokojny nurt potoku w parku.

Obróbka celowo minimalna: wybór okna, łagodny filtr rumble, poziom i
przenikanie. **Żadnego przesuwania wysokości** — to właśnie słychać jako
sztuczność. Kontrola czystości okien (brak mowy i ruchu ulicznego):
energia poniżej 200 Hz ≤ 4%, modulacja obwiedni ≤ 0,2.

Usage:
  python scripts/build_gate_g011.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g011"
CAND = GATE / "candidates"
SCOUT = REPO / "legacy/source/sample_scout/archive.org_creek-stream-water"
GOLD = SCOUT / ("01-gold-tape-53-54-water-gold-tape-53-54-water-"
                "g53-18-water-stream-mp3.mp3")
CEDAR = SCOUT / ("02-aporee-26411-30501-cedar-creek-park-parkway-"
                 "boulevard-allentown-pa-.mp3")

TARGET_DB = -33.0
LENGTH = 8.0

SRC_GOLD = {
    "title": "GOLD TAPE 53/54 Water — Water Stream (Internet Archive)",
    "author": "nieznany (taśma biblioteczna, wydana jako CC0)",
    "license": "CC0 1.0 (public domain)",
    "url": "https://archive.org/details/GOLD_TAPE_53_54_Water",
    "channel": "workflow Sample scout (GitHub Actions) → legacy/source/sample_scout",
}
SRC_CEDAR = {
    "title": "Cedar Creek Park, Allentown PA — nagranie terenowe (aporee / Internet Archive)",
    "author": "aporee maps (Jl.purposedart)",
    "license": "Public Domain Mark 1.0",
    "url": "https://archive.org/details/aporee_26411_30501",
    "channel": "workflow Sample scout (GitHub Actions) → legacy/source/sample_scout",
}


def derumble(wave: np.ndarray, hz: float = 70.0) -> np.ndarray:
    """Tylko filtr podmuchowy/rumble — bez zmiany charakteru nagrania."""
    sos = butter(2, hz, btype="highpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1).astype(np.float32)


def soften_top(wave: np.ndarray, hz: float) -> np.ndarray:
    """Łagodne przymknięcie góry (taśmowy szum), 1. rząd = bez „podwodnego” efektu."""
    sos = butter(1, hz, btype="lowpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1).astype(np.float32)


def measure(x: np.ndarray) -> dict:
    sr = dsp.SR
    sp = np.abs(np.fft.rfft(x * np.hanning(x.size)))
    fr = np.fft.rfftfreq(x.size, 1 / sr)
    tot = max(sp.sum(), 1e-9)
    env = np.array([np.sqrt((x[j:j + sr // 20] ** 2).mean())
                    for j in range(0, x.size - sr // 20, sr // 20)])
    env = env / max(env.max(), 1e-9)
    sub = np.array([np.sqrt((x[j:j + sr // 10] ** 2).mean())
                    for j in range(0, x.size - sr // 10, sr // 10)])
    d = np.diff(20 * np.log10(np.maximum(sub, 1e-9)))
    return {
        "centroid": float((sp * fr).sum() / tot),
        "low": float(sp[fr < 1000].sum() / tot),
        "rumble": float(sp[fr < 200].sum() / tot),
        "hiss": float(sp[fr > 6000].sum() / tot),
        "events": float((d > 4).sum() / (x.size / sr)),
        "wobble": float(np.std(20 * np.log10(np.maximum(sub, 1e-9)))),
        "modulation": float(np.std(env)),
    }


def make_bed(name: str, label: str, title: str, entry_id: str, src: Path,
             start: float, top_hz: float, desc: str, setting: str,
             source: dict, window_note: str) -> dict:
    sr = dsp.SR
    wave, _ = dsp.load_any(src)
    seg = wave[:, int(start * sr):int((start + LENGTH) * sr)].copy()
    seg = derumble(seg)
    if top_hz:
        seg = soften_top(seg, top_hz)
    seg = dsp.normalize_rms(seg, TARGET_DB)
    seg = dsp.fade(seg, 0.35, 0.6)
    out = CAND / f"{name}.mp3"
    dsp.encode_mp3(out, seg)
    stats = measure(seg.mean(axis=0))
    assert stats["rumble"] < 0.08, f"{name}: za dużo rumble ({stats['rumble']:.0%})"
    assert stats["modulation"] < 0.25, f"{name}: podejrzana modulacja (mowa?)"
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": f"{source['title']} — {source['license']}",
        "entry": {
            "id": entry_id, "setting": setting, "desc": desc,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": round(seg.shape[1] / sr, 2),
            "level_ref_db": int(TARGET_DB), "loopable": True,
            "source": {**source, "notes": window_note},
        },
        "_stats": stats,
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    candidates = [
        make_bed("r_creek_close", "r.1", "strumień tuż obok", "flooded_canyon_01",
                 GOLD, start=4.0, top_hz=9000.0,
                 desc="bliskie, gęste ciurkanie wody po kamieniach — mikrofon stoi "
                      "przy samym nurcie; nagranie terenowe, bez obróbki wysokości",
                 setting="zalany kanion / strumień tuż obok",
                 source=SRC_GOLD,
                 window_note="GOLD TAPE 53/54 Water, okno 4,0–12,0 s; filtr rumble 70 Hz, "
                             "łagodne przymknięcie góry 9 kHz (szum taśmy), poziom −33 dB"),
        make_bed("r_creek_tape", "r.2", "strumień w skalnym korycie", "flooded_canyon_02",
                 GOLD, start=12.5, top_hz=7500.0,
                 desc="dalszy fragment tej samej taśmy: woda spokojniejsza, bardziej "
                      "„w korycie”, ciemniejsza góra — czytelne pojedyncze przelewy",
                 setting="zalany kanion / woda w korycie",
                 source=SRC_GOLD,
                 window_note="GOLD TAPE 53/54 Water, okno 12,5–20,5 s; filtr rumble 70 Hz, "
                             "przymknięcie góry 7,5 kHz, poziom −33 dB"),
        make_bed("r_park_brook", "r.3", "szeroki potok", "flooded_canyon_03",
                 CEDAR, start=16.0, top_hz=6500.0,
                 desc="nagranie parkowego potoku: szerszy, równy nurt z drobnym "
                      "pluskiem — najspokojniejszy wariant, dobry pod dialog sceny",
                 setting="zalany kanion / szeroki nurt",
                 source=SRC_CEDAR,
                 window_note="Cedar Creek Park (aporee), okno 16,0–24,0 s — najstabilniejszy "
                             "fragment (wahanie 0,6 dB); filtr rumble 70 Hz, przymknięcie "
                             "góry 6,5 kHz, poziom −33 dB"),
    ]
    manifest = {
        "id": "g011",
        "created": date.today().isoformat(),
        "note": ("Runda 4 tła do fabuły 2, pierwsza z PRAWDZIWYCH nagrań terenowych "
                 "(Internet Archive przez Sample scout). Obróbka: tylko okno, filtr "
                 "rumble, łagodne przymknięcie góry i poziom — żadnego pitchowania, "
                 "które właściciel słyszał w g010. Etykiety r.*."),
        "entries": [{
            "slug": "zalany-kanion",
            "kind": "backgrounds",
            "role": "tło fabuły 2: płynąca woda w skalnym kanionie — nurt i ciurkanie",
            "candidates": [{k: v for k, v in c.items() if k != "_stats"}
                           for c in candidates],
        }],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cand in candidates:
        st = cand["_stats"]
        print(f"{cand['label']} {Path(cand['file']).name:<18s} "
              f"{cand['entry']['duration_sec']:5.2f}s  cent {st['centroid']:4.0f} Hz  "
              f"<1k {st['low']:4.0%}  >6k {st['hiss']:4.0%}  rumble {st['rumble']:4.0%}  "
              f"zdarzeń/s {st['events']:4.1f}  wahanie {st['wobble']:4.1f} dB")


if __name__ == "__main__":
    main()
