#!/usr/bin/env python3
"""Bramka g009 — tło „zalany kanion", runda 2: sama woda, bez wiatru.

Werdykt g008: „to nie brzmi jak woda tylko jak szum wiatru — woda gdzieś
tam jest, ale zagłuszona; potrzebujemy chlupotania, ciurkania".

Diagnoza liczbowa: gorące źródła NPS (Dragon's Mouth) to w większości syk
pary — energia rozlana szerokim pasmem, centroid 2100–2700 Hz, brak
tranzjentów. Ucho czyta taki sygnał jako wiatr. Woda słyszalna jako WODA
ma dwie cechy: masę poniżej 1 kHz (rezonans pęcherzyków i wnęki) oraz
policzalne zdarzenia — chlupnięcia, bulgoty, krople.

| materiał | < 1 kHz | centroid | skoki energii /s |
|---|---|---|---|
| Dragon's Mouth (g008, odrzucony) | ~20% | 2100–2700 Hz | ~0 |
| loop-water-* (rubberduck) | 13–36% | 3200–4300 Hz | 0,0–1,2 |
| **bąble/bulgot (ta bramka)** | **67–73%** | **1400–2100 Hz** | **1,7–2,7** |

Rodzina: bulgot i bąble wodne (CC0). Dodatkowo dolnoprzepustowo ścinamy
pasmo syku powyżej 6 kHz, które nadaje charakter „wiatru".

Usage:
  python scripts/build_gate_g009.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g009"
CAND = GATE / "candidates"
ATOM = Path("/tmp/atomcut/packs")
SWAMP = ATOM / "opengameart-swamp-environment-audio/audio"
WATER = ATOM / "opengameart-40-cc0-water-splash-slime-sfx/audio"
TARGET_DB = -33.0
LENGTH = 8.0

SRC_SWAMP = {
    "title": "Swamp Environment Audio (OpenGameArt)",
    "author": "lokif",
    "license": "CC0 1.0 (public domain)",
    "url": "https://opengameart.org/content/swamp-environment-audio",
    "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
}
SRC_WATER = {
    "title": "40 water / splash / slime SFX (OpenGameArt)",
    "author": "rubberduck",
    "license": "CC0 1.0 (public domain)",
    "url": "https://opengameart.org/content/40-cc0-water-splash-slime-sfx",
    "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
}


def tame_hiss(wave: np.ndarray, lp_hz: float = 6000.0, hp_hz: float = 60.0) -> np.ndarray:
    """Ścina syk (charakter wiatru) i rumble, zostawia korpus wody."""
    sos_lp = butter(3, lp_hz, btype="lowpass", fs=dsp.SR, output="sos")
    sos_hp = butter(2, hp_hz, btype="highpass", fs=dsp.SR, output="sos")
    out = sosfiltfilt(sos_lp, wave, axis=-1)
    return sosfiltfilt(sos_hp, out, axis=-1).astype(np.float32)


def tile(wave: np.ndarray, seconds: float) -> np.ndarray:
    """Zapętla materiał do żądanej długości z krótkim przenikaniem."""
    need = int(seconds * dsp.SR)
    if wave.shape[1] >= need:
        return wave[:, :need]
    xf = int(0.25 * dsp.SR)
    out = wave.copy()
    while out.shape[1] < need:
        nxt = wave
        head = out[:, -xf:] * np.linspace(1, 0, xf, dtype=np.float32)
        tail = nxt[:, :xf] * np.linspace(0, 1, xf, dtype=np.float32)
        out = np.concatenate([out[:, :-xf], head + tail, nxt[:, xf:]], axis=1)
    return out[:, :need]


def make_bed(name: str, label: str, title: str, entry_id: str,
             layers: list[dict], desc: str, setting: str, source: dict,
             notes: str) -> dict:
    sr = dsp.SR
    mix = np.zeros((2, int(LENGTH * sr)), dtype=np.float32)
    for spec in layers:
        w, _ = dsp.load_any(spec["path"])
        if spec.get("start"):
            w = w[:, int(spec["start"] * sr):]
        w = tame_hiss(w, spec.get("lp", 6000.0))
        w = tile(w, LENGTH)
        mix += w * spec.get("gain", 1.0)
    mix = dsp.normalize_rms(mix, TARGET_DB)
    mix = dsp.fade(mix, 0.3, 0.5)
    out = CAND / f"{name}.mp3"
    dsp.encode_mp3(out, mix)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": f"{source['title']} — {source['author']}, CC0",
        "entry": {
            "id": entry_id, "setting": setting, "desc": desc,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": round(mix.shape[1] / sr, 2),
            "level_ref_db": int(TARGET_DB), "loopable": True,
            "source": {**source, "notes": notes},
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    candidates = [
        make_bed("w_trickle_pool", "w.1", "chlupot w kamiennej misie",
                 "flooded_canyon_01",
                 layers=[dict(path=WATER / "loop-bubbles-02.m4a", lp=5500.0)],
                 desc="równy chlupot i bulgotanie wody stojącej w kamiennej misie "
                      "(69% energii poniżej 1 kHz, ~2,7 zdarzenia na sekundę) — "
                      "słychać pojedyncze bąble, nie szum",
                 setting="zalany kanion / woda w kamiennej misie",
                 source=SRC_WATER,
                 notes="loop-bubbles-02, filtr dolnoprzepustowy 5,5 kHz (ścięty syk), "
                       "pętla 8 s z przenikaniem 0,25 s"),
        make_bed("w_deep_gurgle", "w.2", "głęboki bulgot w szczelinie",
                 "flooded_canyon_02",
                 layers=[dict(path=SWAMP / "bubbling-2.m4a", lp=6000.0)],
                 desc="najniższy materiał (73% poniżej 1 kHz): ciężka woda bulgocze "
                      "w wąskiej szczelinie, dużo rezonansu wnęki, prawie brak syku",
                 setting="zalany kanion / bulgot w szczelinie",
                 source=SRC_SWAMP,
                 notes="bubbling-2 (Swamp Environment Audio), filtr dolnoprzepustowy 6 kHz, "
                       "pętla 8 s z przenikaniem 0,25 s"),
        make_bed("w_drip_cave", "w.3", "ciurkanie i krople w jaskini",
                 "flooded_canyon_03",
                 layers=[dict(path=SWAMP / "bubbling-2.m4a", lp=6000.0, gain=0.75),
                         dict(path=WATER / "loop-bubbles-1.m4a", lp=5000.0, gain=0.55,
                              start=0.4)],
                 desc="bulgot w tle plus bliższe, rzadsze krople — woda ciurka po "
                      "kamieniu i kapie ze sklepienia; najbardziej „jaskiniowy” wariant",
                 setting="zalany kanion / ciurkanie i krople",
                 source=SRC_SWAMP,
                 notes="bubbling-2 (lokif, CC0) + loop-bubbles-1 (rubberduck, "
                       "40 water/splash/slime SFX, CC0) od 0,4 s, ×0,55; "
                       "oba filtrowane dolnoprzepustowo, pętla 8 s"),
    ]
    manifest = {
        "id": "g009",
        "created": date.today().isoformat(),
        "note": ("Runda 2 tła do fabuły 2 po werdykcie g008 („szum wiatru, nie woda”). "
                 "Zmiana rodziny: bulgot/bąble zamiast gorących źródeł. Kryterium "
                 "liczbowe: >65% energii poniżej 1 kHz i policzalne zdarzenia "
                 "chlupotu; syk powyżej 5–6 kHz ścięty filtrem. Etykiety w.*."),
        "entries": [{
            "slug": "zalany-kanion",
            "kind": "backgrounds",
            "role": "tło fabuły 2: woda w skalnej szczelinie — chlupot i ciurkanie, "
                    "przez które przeciska się bestia",
            "candidates": candidates,
        }],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sr = dsp.SR
    for cand in candidates:
        f = CAND / Path(cand["file"]).name
        w, _ = dsp.load_any(f)
        x = w.mean(axis=0)
        sp = np.abs(np.fft.rfft(x * np.hanning(x.size)))
        fr = np.fft.rfftfreq(x.size, 1 / sr)
        tot = sp.sum()
        sub = np.array([np.sqrt((x[j:j + sr // 10] ** 2).mean())
                        for j in range(0, x.size - sr // 10, sr // 10)])
        d = np.diff(20 * np.log10(np.maximum(sub, 1e-9)))
        print(f"{cand['label']} {f.name:<18s} {cand['entry']['duration_sec']:5.2f}s  "
              f"RMS {dsp.rms_db(w):6.1f} dB  cent {(sp * fr).sum() / tot:4.0f} Hz  "
              f"<1k {sp[fr < 1000].sum() / tot:4.0%}  >6k {sp[fr > 6000].sum() / tot:4.0%}  "
              f"chlupnięć/s {(d > 4).sum() / (x.size / sr):4.1f}")


if __name__ == "__main__":
    main()
