#!/usr/bin/env python3
"""Bramka g003 — naprawcza „ryk-bestii” (wersja po werdykcie g002).

Korekta doktryny właściciela: 3 kandydatów na wpis = 3 RYKI tej samej
bestii (warianty charakteru: ciężki / krótki / masywny), NIE 3 różne
gatunki. Źródło: jedyne czytelne zwierzę z g002 — żubr/byk w rui
(Yellowstone Sound Library, Public Domain), „przerobiony na ryk”
przez zwolnienie tempa (pitch w dół) — jeden gatunek, trzy warianty.

Wymaga sparse clone'y /tmp/ysl (patrz LESSONS.md).

Usage:
  python scripts/build_gate_g003.py
"""
from __future__ import annotations

import json
from datetime import date
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.signal import butter, resample_poly, sosfiltfilt

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g003"
CAND = GATE / "candidates"
SRC_WAV = "/tmp/ysl/Bison (rut)/Sound Library - Bison.mp3"

SOURCE = {
    "title": "Yellowstone Sound Library (NPS)",
    "author": "National Park Service",
    "license": "Public Domain (utwór rządu USA)",
    "url": "https://www.nps.gov/yell/learn/photosmultimedia/soundlibrary.htm",
    "channel": "git clone sparse z github.com/rosuH/YSL (mirror)",
}


def cut(wave: np.ndarray, start: float, end: float) -> np.ndarray:
    sr = dsp.SR
    seg = wave[:, int(start * sr):int(end * sr)].copy()
    return dsp.fade(seg, 0.04, min(0.6, seg.shape[1] / sr * 0.3))


def to_roar(seg: np.ndarray, semitones_down: float, hp_hz: float = 45.0,
            lp_hz: float = 2800.0, drive: float = 1.0) -> np.ndarray:
    """Zwolnij nagranie (pitch w dół + dłuższy czas) i wyczyść pasmo."""
    ratio = 2 ** (semitones_down / 12.0)  # nowa_długość = stara * ratio
    frac = Fraction(ratio).limit_denominator(96)
    out = resample_poly(seg, frac.numerator, frac.denominator, axis=-1)
    sr = dsp.SR
    sos_hp = butter(2, hp_hz, btype="highpass", fs=sr, output="sos")
    sos_lp = butter(3, min(lp_hz, sr * 0.45), btype="lowpass", fs=sr, output="sos")
    out = sosfiltfilt(sos_hp, out, axis=-1)
    out = sosfiltfilt(sos_lp, out, axis=-1)
    if drive > 1.0:
        out = np.tanh(out * drive) / np.tanh(drive)
    return out


def soft_limit(wav: np.ndarray, crest_db: float = 12.0, rounds: int = 4) -> np.ndarray:
    """Miękki limiter: compress peaks przez tanh, aż crest (peak−RMS) spadnie
    pod crest_db. Body rośnie wolniej niż piki, więc materiał się zagęszcza
    bez twardego klipu."""
    drive = 2.0
    out = np.tanh(wav * drive) / np.tanh(drive)
    for _ in range(rounds):
        peak = float(np.abs(out).max())
        rms = float(np.sqrt(np.mean(out * out)))
        crest = 20 * np.log10(peak / max(rms, 1e-9))
        if crest <= crest_db:
            break
        out = np.tanh(out * drive) / np.tanh(drive)
    return out


def make_candidate(wave: np.ndarray, name: str, label: str, title: str,
                   entry_id: str, builds: list[dict], semitones_down: float,
                   norm_db: float, desc: str, character: str, energy: str,
                   good_for: str, bad_for: str, drive: float = 1.0) -> dict:
    """Zbuduj jednego kandydata-ryk (builds = lista warstw do złożenia)."""
    sr = dsp.SR
    layers = [cut(wave, b["start"], b["end"]) for b in builds]
    total = max(int((b.get("at", 0.0) * sr)) + l.shape[1] for b, l in zip(builds, layers))
    comp = np.zeros((2, total), dtype=np.float32)
    for b, l in zip(builds, layers):
        at = int(b.get("at", 0.0) * sr)
        gain = b.get("gain", 1.0)
        comp[:, at:at + l.shape[1]] += l * gain
    roar = to_roar(comp, semitones_down, drive=drive)
    roar = dsp.fade(roar, 0.03, min(0.5, roar.shape[1] / sr * 0.2))
    roar = soft_limit(roar, crest_db=12.0)
    roar = dsp.normalize_rms(roar, norm_db)
    out = CAND / f"{name}.mp3"
    dsp.encode_mp3(out, roar)
    dur = round(roar.shape[1] / sr, 2)
    windows_txt = " + ".join(f"{b['start']}-{b['end']} s" for b in builds)
    return {
        "label": label,
        "title": title,
        "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": f"{SOURCE['title']} — Bison (rut); {SOURCE['license']}",
        "entry": {
            "id": entry_id,
            "role": "ryk dużej dzikiej bestii",
            "character": character,
            "distance": "bliski",
            "energy": energy,
            "duration_sec": dur,
            "desc": desc,
            "good_for": good_for,
            "bad_for": bad_for,
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "source": {**SOURCE,
                       "notes": (f"Bison (rut) {windows_txt}; zwolnienie "
                                 f"{semitones_down:.0f} półtonów w dół "
                                 f"(tempo x{2 ** (semitones_down / 12.0):.2f})")},
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    wave, _ = dsp.load_any(SRC_WAV)
    candidates = [
        make_candidate(
            wave, "r_roar_heavy_01", "r.1", "ciężki, długi ryk", "beast_bison_roar_01",
            builds=[dict(start=77.8, end=81.2)],
            semitones_down=4.0, norm_db=-15.0,
            desc="jedno długie wycięcie pomruku żubra zwolnione o 4 półtony — ciężki, toczący ryk",
            character="ciężki, niski, toczący się",
            energy="wysoka",
            good_for="wielka bestia nadchodzi, groźba balotha, marsz",
            bad_for="zwinne stwory, magiczne fabuły",
        ),
        make_candidate(
            wave, "r_roar_hard_01", "r.2", "krótki, gwałtowny ryk", "beast_bison_roar_02",
            builds=[dict(start=82.6, end=84.3)],
            semitones_down=3.0, norm_db=-14.0,
            desc="najgłośniejszy pomruk żubra (sr. 83 s) zwolniony o 3 półtony — krótki, rzucany atak",
            character="gwałtowny, agresywny, krótki",
            energy="bardzo wysoka",
            good_for="atak bestii, niespodziewany skok, przecięcie akcji",
            bad_for="budowanie napięcia (za krótki na długie hero)",
        ),
        make_candidate(
            wave, "r_roar_mass_01", "r.3", "masywny ryk podwójny", "beast_bison_roar_mass_01",
            builds=[dict(start=78.3, end=81.0),
                    dict(start=82.8, end=84.2, at=1.05, gain=0.85)],
            semitones_down=5.0, norm_db=-14.5, drive=1.35,
            desc="dwa pomruki tego samego żubra złożone (drugie 1,05 s później), 5 półtonów w dół + saturacja — jak większa, starsza bestia",
            character="masywny, warstwowy, dominujący",
            energy="bardzo wysoka",
            good_for="największy drapieżnik sceny, finale hero, dominacja",
            bad_for="kameralne scenerie, małe zwierzęta",
        ),
    ]
    manifest = {
        "id": "g003",
        "created": date.today().isoformat(),
        "note": ("Naprawcza po g002: właściciel odrzucił ryk-bestii — 3 kandydatów "
                 "na wpis mają być 3 RYKAMI tej samej bestii (warianty charakteru), "
                 "nie 3 różnymi zwierzętami. Etykiety unikalne w skali bramki (r.*)."),
        "entries": [{
            "slug": "ryk-bestii",
            "kind": "heroes",
            "role": "pojedynczy, czytelny ryk dużej dzikiej bestii jako hero fabuły",
            "candidates": candidates,
        }],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cand in candidates:
        f = CAND / Path(cand["file"]).name
        w, _ = dsp.load_any(f)
        print(f"{cand['label']}: {f.name} — {cand['entry']['duration_sec']} s, "
              f"RMS {dsp.rms_db(w):.1f} dB, peak {np.abs(w).max():.2f}")
    print("manifest:", GATE / "manifest.json")


if __name__ == "__main__":
    main()
