#!/usr/bin/env python3
"""Bramka g010 — tło „zalany kanion", runda 3: nurt, nie gotująca się woda.

Werdykt g009: „bardziej ciurkanie, mniej bulgotanie — teraz wszystko brzmi
jak gotująca się woda, a woda w kanionie płynie i ciurka. To powinno być
coś jak kroki w wodzie, płynąca rzeka, woda płynąca po kamieniach”.

Diagnoza: bulgot (`bubbling-*`, `loop-bubbles-*`) to woda STOJĄCA — bąble
wypływające na powierzchnię. Nurt ma inną sygnaturę: ciągła płynąca masa
w paśmie średnio-niskim plus nieregularne chlupnięcia o wodę i kamień.
W osiągalnych bibliotekach nie ma nagrania rzeki (YSL: wyłącznie gejzery,
źródła i jezioro; OGA `water-flowing`: syk o centroidzie 5160 Hz i 39%
energii ponad 6 kHz). Dlatego nurt składamy **foleyem**, jak w dźwięku
filmowym:

  warstwa 1 — nurt: szum wody obniżony o 7–9 półtonów i przefiltrowany,
              wchodzi w pasmo płynącej masy (centroid ~1100–1300 Hz);
  warstwa 2 — chlupnięcia: pojedyncze plusknięcia i krople rozsiane
              nierównomiernie (ziarno stałe → wynik powtarzalny);
  warstwa 3 (s.3) — brodzenie: rzadsze, cięższe plaśnięcia = kroki w wodzie.

Kryteria liczbowe roli: > 50% energii poniżej 1 kHz, < 5% powyżej 6 kHz
(zero syku), 1,5–3 zdarzenia na sekundę (chlupot jako zdarzenia, nie wrzenie).

Usage:
  python scripts/build_gate_g010.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g010"
CAND = GATE / "candidates"
sys.path.insert(0, str(REPO / "scripts"))
import build_gate_g003 as g003  # noqa: E402  (to_roar = resample + filtry)

ATOM = Path("/tmp/atomcut/packs")
FLOW_SRC = ATOM / "opengameart-100-cc0-sfx-2/audio/sfx100v2-loop-water-02.m4a"
SPLASH_DIR = ATOM / "opengameart-40-cc0-water-splash-slime-sfx/audio"
DROP_DIR = ATOM / "opengameart-fantasy-sound-effects-tinysized-sfx/audio"
MUD_DIR = ATOM / "opengameart-25-cc0-mud-sfx/audio"

TARGET_DB = -33.0
LENGTH = 8.0

SRC_FLOW = {
    "title": "100 CC0 SFX #2 (OpenGameArt)",
    "author": "rubberduck",
    "license": "CC0 1.0 (public domain)",
    "url": "https://opengameart.org/content/100-cc0-sfx-2",
    "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
}


def lowpass(wave: np.ndarray, hz: float) -> np.ndarray:
    sos = butter(3, hz, btype="lowpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1).astype(np.float32)


def highpass(wave: np.ndarray, hz: float) -> np.ndarray:
    sos = butter(2, hz, btype="highpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1).astype(np.float32)


def tile(wave: np.ndarray, seconds: float) -> np.ndarray:
    need = int(seconds * dsp.SR)
    if wave.shape[1] >= need:
        return wave[:, :need]
    xf = int(0.3 * dsp.SR)
    out = wave.copy()
    while out.shape[1] < need:
        head = out[:, -xf:] * np.linspace(1, 0, xf, dtype=np.float32)
        tail = wave[:, :xf] * np.linspace(0, 1, xf, dtype=np.float32)
        out = np.concatenate([out[:, :-xf], head + tail, wave[:, xf:]], axis=1)
    return out[:, :need]


def flow_layer(semitones: float, lp_hz: float) -> np.ndarray:
    """Ciągły nurt: szum wody zepchnięty w pasmo płynącej masy."""
    w, _ = dsp.load_any(FLOW_SRC)
    w = g003.to_roar(w, semitones, hp_hz=80.0, lp_hz=lp_hz, drive=1.0)
    return tile(w, LENGTH)


def scatter(files: list[Path], rate: float, gain: float, seed: int,
            lp_hz: float, jitter: float = 0.45,
            semitones: float = 4.0) -> np.ndarray:
    """Rozsiewa krótkie chlupnięcia nierównomiernie w czasie (deterministycznie).

    Chlupnięcia z bibliotek gier są jasne (pyknięcia pod efekt w grze);
    obniżenie o kilka półtonów daje im masę wody i utrzymuje tło w paśmie
    poniżej 1 kHz zamiast ciągnąć centroid w górę.
    """
    rng = np.random.default_rng(seed)
    out = np.zeros((2, int(LENGTH * dsp.SR)), dtype=np.float32)
    cache = []
    for f in files:
        w, _ = dsp.load_any(f)
        if semitones:
            w = g003.to_roar(w, semitones, hp_hz=70.0, lp_hz=lp_hz, drive=1.0)
        w = lowpass(highpass(w, 90.0), lp_hz)
        peak = float(np.abs(w).max())
        cache.append(w / peak if peak > 0 else w)
    t = float(rng.uniform(0.1, 0.6))
    while t < LENGTH - 0.4:
        w = cache[int(rng.integers(len(cache)))]
        at = int(t * dsp.SR)
        seg = w[:, :out.shape[1] - at]
        amp = gain * float(rng.uniform(0.55, 1.0))
        pan = float(rng.uniform(-0.35, 0.35))
        out[0, at:at + seg.shape[1]] += seg[0] * amp * (1 - max(pan, 0.0))
        out[1, at:at + seg.shape[1]] += seg[1] * amp * (1 + min(pan, 0.0))
        t += float(rng.uniform(1 - jitter, 1 + jitter)) / rate
    return out


def measure(x: np.ndarray) -> tuple[float, float, float, float]:
    sr = dsp.SR
    sp = np.abs(np.fft.rfft(x * np.hanning(x.size)))
    fr = np.fft.rfftfreq(x.size, 1 / sr)
    tot = max(sp.sum(), 1e-9)
    sub = np.array([np.sqrt((x[j:j + sr // 10] ** 2).mean())
                    for j in range(0, x.size - sr // 10, sr // 10)])
    d = np.diff(20 * np.log10(np.maximum(sub, 1e-9)))
    return ((sp * fr).sum() / tot, sp[fr < 1000].sum() / tot,
            sp[fr > 6000].sum() / tot, (d > 4).sum() / (x.size / sr))


def make_bed(name: str, label: str, title: str, entry_id: str,
             flow: np.ndarray, events: np.ndarray, desc: str, setting: str,
             notes: str) -> dict:
    mix = flow + events
    mix = dsp.normalize_rms(mix, TARGET_DB)
    mix = dsp.fade(mix, 0.3, 0.5)
    out = CAND / f"{name}.mp3"
    dsp.encode_mp3(out, mix)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": "100 CC0 SFX #2 + 40 water/splash/slime + 25 mud SFX (rubberduck) "
                  "+ fantasy tiny SFX — CC0",
        "entry": {
            "id": entry_id, "setting": setting, "desc": desc,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": round(mix.shape[1] / dsp.SR, 2),
            "level_ref_db": int(TARGET_DB), "loopable": True,
            "source": {**SRC_FLOW, "notes": notes},
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    splashes = [SPLASH_DIR / f"splash-{i:02d}.m4a" for i in (4, 9, 12, 14)]
    drops = [DROP_DIR / f"water-drop-{i:02d}.m4a" for i in (1, 2, 3)]
    muds = [MUD_DIR / f"mud-{i:02d}.m4a" for i in (1, 5, 9)]

    candidates = [
        make_bed("s_stream_stones", "s.1", "strumień po kamieniach",
                 "flooded_canyon_01",
                 flow=flow_layer(8.0, 3200.0) * 0.62,
                 events=scatter(splashes + drops, rate=3.1, gain=0.70, seed=11,
                                lp_hz=3200.0, semitones=5.0),
                 desc="równy nurt płynący po kamieniach z gęstym, drobnym chlupotem — "
                      "woda cały czas się przelewa, nic nie bulgocze",
                 setting="zalany kanion / strumień po kamieniach",
                 notes="nurt: sfx100v2-loop-water-02 obniżony o 8 półtonów, filtr 3,2 kHz; "
                       "chlupot: splash-04/09/12/14 + water-drop-01..03 rozsiane ~3,1/s "
                       "(ziarno 11, deterministycznie)"),
        make_bed("s_canyon_run", "s.2", "nurt w ciasnym kanionie",
                 "flooded_canyon_02",
                 flow=flow_layer(9.0, 2800.0) * 0.70,
                 events=scatter(splashes + drops, rate=2.2, gain=0.62, seed=23,
                                lp_hz=2800.0, semitones=6.0),
                 desc="cięższa, głębsza woda w wąskim gardle kanionu: nurt niżej "
                      "i ciemniej, chlupnięcia rzadsze i bardziej odległe",
                 setting="zalany kanion / ciasne gardło",
                 notes="nurt: sfx100v2-loop-water-02 obniżony o 9 półtonów, filtr 2,8 kHz; "
                       "chlupot: splash + krople ~2,2/s (ziarno 23)"),
        make_bed("s_wading_steps", "s.3", "brodzenie w nurcie",
                 "flooded_canyon_03",
                 flow=flow_layer(8.0, 3000.0) * 0.58,
                 events=(scatter(muds + splashes[:2], rate=1.5, gain=0.95, seed=37,
                                 lp_hz=2600.0, jitter=0.30, semitones=6.0)
                         + scatter(drops, rate=1.8, gain=0.40, seed=53, lp_hz=3400.0, semitones=4.0)),
                 desc="nurt plus cięższe, regularniejsze plaśnięcia — ktoś brodzi "
                      "przez płynącą wodę; między krokami drobne krople",
                 setting="zalany kanion / brodzenie w nurcie",
                 notes="nurt: sfx100v2-loop-water-02 −8 półtonów, filtr 3 kHz; "
                       "kroki: mud-01/05/09 + splash ~1,5/s (ziarno 37); "
                       "krople: water-drop ~1,8/s (ziarno 53)"),
    ]
    manifest = {
        "id": "g010",
        "created": date.today().isoformat(),
        "note": ("Runda 3 tła do fabuły 2. g008 brzmiała jak wiatr (syk pary), "
                 "g009 jak gotująca się woda (bulgot = woda stojąca). Tu nurt "
                 "budowany foleyem: ciągła płynąca masa + rozsiane chlupnięcia, "
                 "bez bąbli. Etykiety s.*."),
        "entries": [{
            "slug": "zalany-kanion",
            "kind": "backgrounds",
            "role": "tło fabuły 2: płynąca woda w skalnym kanionie — nurt, ciurkanie "
                    "i chlupot o kamienie",
            "candidates": candidates,
        }],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cand in candidates:
        f = CAND / Path(cand["file"]).name
        w, _ = dsp.load_any(f)
        cent, lo, hi, ev = measure(w.mean(axis=0))
        print(f"{cand['label']} {f.name:<18s} {cand['entry']['duration_sec']:5.2f}s  "
              f"RMS {dsp.rms_db(w):6.1f} dB  cent {cent:4.0f} Hz  <1k {lo:4.0%}  "
              f">6k {hi:4.0%}  chlupnięć/s {ev:4.1f}")


if __name__ == "__main__":
    main()
