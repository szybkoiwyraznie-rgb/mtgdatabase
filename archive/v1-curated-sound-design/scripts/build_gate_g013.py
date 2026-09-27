#!/usr/bin/env python3
"""Bramka g013 — prawdziwy diabelski chichot dla fabuły 3.

Korekta po g012: żadnych składanych wokalizacji z kitu kreskówkowych stworów.
Źródłem jest 26-sekundowe nagranie prawdziwego człowieka wykonującego serię
maniakalnych śmiechów (Huminaatio, Freesound, CC0). Kandydaci to trzy osobne
ujęcia z tej sesji. Obróbka: cięcie, filtr rumble, miękkie ujarzmienie pików,
poziom i fade; bez pitchowania, warstwowania i syntezy.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import sig_audio as dsp
import build_gate_g003 as gate_dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g013"
CAND = GATE / "candidates"
SRC = Path("/tmp/barrel/thirdparty/assets/189278__huminaatio__maniac-kid-laugh-1.flac")
SOURCE = {
    "title": "Maniac kid laugh (1) (Freesound)",
    "author": "Huminaatio",
    "license": "CC0 1.0 (public domain)",
    "url": "https://freesound.org/people/Huminaatio/sounds/189278/",
    "channel": "git clone sparse z github.com/lihop/barrel-of-laughs (mirror z rejestrem licencji)",
}


def make_candidate(name: str, label: str, title: str, entry_id: str,
                   start: float, end: float, desc: str, character: str) -> dict:
    wave, _ = dsp.load_any(SRC)
    segment = wave[:, int(start * dsp.SR):int(end * dsp.SR)].copy()
    sos = butter(2, 70.0, btype="highpass", fs=dsp.SR, output="sos")
    segment = sosfiltfilt(sos, segment, axis=-1)
    # Ujęcia mają naturalnie duży crest. Miękki limiter przed normalizacją
    # wyrównuje głośność bramki bez twardego obcinania pojedynczych sylab.
    segment = gate_dsp.soft_limit(segment, crest_db=12.0, rounds=6)
    segment = dsp.normalize_rms(segment, -15.0)
    segment = dsp.fade(segment, 0.018, 0.10)
    peak = float(np.max(np.abs(segment)))
    ceiling = dsp.db_to_gain(-1.0)
    if peak > ceiling:
        segment *= ceiling / peak
    path = CAND / f"{name}.mp3"
    dsp.encode_mp3(path, segment)
    return {
        "label": label,
        "title": title,
        "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": "prawdziwy ludzki śmiech — Huminaatio / Freesound, CC0",
        "entry": {
            "id": entry_id,
            "role": "prawdziwy diabelski chichot małego demona po udanym sabotażu",
            "character": character,
            "distance": "bliski",
            "energy": "wysoka",
            "duration_sec": round(segment.shape[1] / dsp.SR, 2),
            "desc": desc,
            "good_for": "imp, demon, złodziej artefaktu, maniakalna satysfakcja",
            "bad_for": "komedia, sympatyczne stworzenie, naturalistyczna fauna",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "source": {
                **SOURCE,
                "notes": (f"okno {start:.2f}–{end:.2f} s z nieprzerwanej sesji "
                          "aktorskiej; filtr rumble 70 Hz, miękki limiter, poziom i fade; "
                          "bez pitchowania i warstwowania; licencja potwierdzona "
                          "w objects/hiding_spots/barrel/assets/work/sounds/licenses.txt"),
            },
        },
    }


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"brak źródła: {SRC}")
    CAND.mkdir(parents=True, exist_ok=True)
    candidates = [
        make_candidate(
            "h_low_maniac", "h.1", "niski maniakalny chichot", "demonic_laugh_01",
            13.18, 15.30,
            "jedno zwarte ujęcie: mocny atak przechodzi w nierówny, gasnący rechot",
            "zwarty, złowrogi, gasnący",
        ),
        make_candidate(
            "h_double_cackle", "h.2", "podwójny diabelski rechot", "demonic_laugh_02",
            15.55, 18.35,
            "dwie fale śmiechu w jednym oddechu — druga wraca po krótkim zawahaniu",
            "dwufalowy, maniakalny, nieprzewidywalny",
        ),
        make_candidate(
            "h_triumphant_laugh", "h.3", "triumfalny diabelski śmiech", "demonic_laugh_03",
            21.90, 24.35,
            "najmocniejsze ujęcie sesji: szybkie sylaby rosną do otwartego triumfalnego śmiechu",
            "narastający, triumfalny, bezczelny",
        ),
    ]
    manifest = {
        "id": "g013",
        "created": date.today().isoformat(),
        "note": ("Runda 2 hero do fabuły 3 po odrzuceniu kreskówkowego kitu g012. "
                 "Trzy osobne ujęcia prawdziwego człowieka wykonującego maniakalny "
                 "śmiech; zero pitchowania i składania sylab. Etykiety h.*."),
        "entries": [{
            "slug": "chichot-chochlika",
            "kind": "heroes",
            "role": "prawdziwy diabelski chichot małego demona po udanym sabotażu",
            "candidates": candidates,
        }],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cand in candidates:
        path = GATE / cand["file"]
        wave, _ = dsp.load_any(path)
        peak = 20 * np.log10(max(float(np.max(np.abs(wave))), 1e-9))
        print(f"{cand['label']} {path.name:<24s} {wave.shape[1] / dsp.SR:4.2f}s  "
              f"RMS {dsp.rms_db(wave):5.1f} dB  peak {peak:5.1f} dB")


if __name__ == "__main__":
    main()
