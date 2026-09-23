#!/usr/bin/env python3
"""Bramka g012 — hero „złośliwy chichot małego demona” dla fabuły 3.

Nefarious Imp właśnie spalił mapę, ukradł kryształ i z satysfakcją pokazuje
skutek sabotażu. Tożsamością sceny jest jego krótki, złośliwy chichot — nie
ryk dużej bestii ani ogólny odgłos magii.

Trzy warianty korzystają z różnych ujęć małego stworzenia z jednego kitu
rubberduck (CC0). Obróbka ogranicza się do ułożenia 2–3 sylab, poziomu i
krótkich fade'ów; bez pitchowania i bez syntezy.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g012"
CAND = GATE / "candidates"
KIT = Path("/tmp/atomcut/packs/opengameart-80-cc0-creature-sfx/audio")
SOURCE = {
    "title": "80 creature SFX (OpenGameArt)",
    "author": "rubberduck",
    "license": "CC0 1.0 (public domain)",
    "url": "https://opengameart.org/content/80-cc0-creature-sfx",
    "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
}


def trim(wave: np.ndarray, threshold: float = 0.015) -> np.ndarray:
    """Usuń wyłącznie techniczną ciszę przed/po krótkiej wokalizacji."""
    env = np.max(np.abs(wave), axis=0)
    active = np.flatnonzero(env >= max(float(env.max()) * threshold, 1e-5))
    if not active.size:
        raise ValueError("pusty kandydat źródłowy")
    pad = int(0.012 * dsp.SR)
    return wave[:, max(0, active[0] - pad):min(wave.shape[1], active[-1] + pad)]


def compose(files: list[str], gaps: list[float]) -> np.ndarray:
    """Ułóż różne naturalne sylaby kolejno — bez zmiany wysokości."""
    if len(gaps) != len(files) - 1:
        raise ValueError("gaps musi mieć o jeden element mniej niż files")
    parts = [trim(dsp.load_any(KIT / name)[0]) for name in files]
    total = sum(p.shape[1] for p in parts) + sum(int(g * dsp.SR) for g in gaps)
    out = np.zeros((2, total), dtype=np.float32)
    at = 0
    for i, part in enumerate(parts):
        out[:, at:at + part.shape[1]] += part
        at += part.shape[1]
        if i < len(gaps):
            at += int(gaps[i] * dsp.SR)
    # Krótkie aktorskie sylaby mają ostre pojedyncze piki. Łagodna kompresja
    # przed normalizacją chroni MP3 przed klipem i wyrównuje odsłuch bramki.
    for _ in range(2):
        out = np.tanh(out * 2.0) / np.tanh(2.0)
    out = dsp.normalize_rms(out, -15.0)
    out = dsp.fade(out, 0.008, 0.055)
    peak = float(np.max(np.abs(out)))
    if peak > dsp.db_to_gain(-1.0):
        out *= dsp.db_to_gain(-1.0) / peak
    return out


def candidate(name: str, label: str, title: str, entry_id: str,
              files: list[str], gaps: list[float], desc: str,
              character: str) -> dict:
    wave = compose(files, gaps)
    path = CAND / f"{name}.mp3"
    dsp.encode_mp3(path, wave)
    return {
        "label": label,
        "title": title,
        "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": "80 creature SFX (OpenGameArt) — rubberduck, CC0",
        "entry": {
            "id": entry_id,
            "role": "złośliwy chichot małego demona po udanym sabotażu",
            "character": character,
            "distance": "bliski",
            "energy": "średnia",
            "duration_sec": round(wave.shape[1] / dsp.SR, 2),
            "desc": desc,
            "good_for": "chochlik, mały demon, złodziej artefaktu, udany sabotaż",
            "bad_for": "duża bestia, heroiczny wojownik, naturalistyczna fauna",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "source": {
                **SOURCE,
                "notes": ("packs/opengameart-80-cc0-creature-sfx; "
                          + " + ".join(f.removesuffix('.m4a') for f in files)
                          + "; różne sylaby ułożone bez pitchowania; "
                            "mirror pack.json potwierdza CC0 1.0"),
            },
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    candidates = [
        candidate(
            "i_dry_snicker", "i.1", "suchy chichot", "imp_snicker_01",
            ["cute-02.m4a", "cute-08.m4a"], [0.055],
            "dwie niskie, krótkie sylaby — powściągana satysfakcja po kradzieży kryształu",
            "krótki, suchy, pod nosem",
        ),
        candidate(
            "i_crooked_giggle", "i.2", "krzywy rechocik", "imp_snicker_02",
            ["weird-01.m4a", "cute-03.m4a"], [0.035],
            "ciemniejsza pierwsza sylaba przechodzi w krótki pisk — uśmiech, który robi się niepokojący",
            "chropawy początek, przewrotny koniec",
        ),
        candidate(
            "i_quick_cackle", "i.3", "szybki trójsylabowy chichot", "imp_snicker_03",
            ["cute-01.m4a", "cute-09.m4a", "cute-06.m4a"], [0.025, 0.02],
            "trzy coraz ciaśniejsze sylaby — jawna, nerwowa radość z udanego sabotażu",
            "żywy, trójsylabowy, zadziorny",
        ),
    ]
    manifest = {
        "id": "g012",
        "created": date.today().isoformat(),
        "note": ("Hero do fabuły 3 (Nefarious Imp): złośliwy chichot małego demona "
                 "po spaleniu mapy i kradzieży kryształu. Trzy warianty jednej roli "
                 "z różnych wokalizacji tego samego kitu CC0; bez pitchowania. Etykiety i.*."),
        "entries": [{
            "slug": "chichot-chochlika",
            "kind": "heroes",
            "role": "złośliwy chichot małego demona po udanym sabotażu",
            "candidates": candidates,
        }],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for cand in candidates:
        path = GATE / cand["file"]
        wave, _ = dsp.load_any(path)
        peak = 20 * np.log10(max(float(np.max(np.abs(wave))), 1e-9))
        print(f"{cand['label']} {path.name:<22s} {wave.shape[1] / dsp.SR:4.2f}s  "
              f"RMS {dsp.rms_db(wave):5.1f} dB  peak {peak:5.1f} dB")


if __name__ == "__main__":
    main()
