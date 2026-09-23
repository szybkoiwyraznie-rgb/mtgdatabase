#!/usr/bin/env python3
"""Testy systemu sygnatur. Bez pytesta: uruchamiane w CI i lokalnie.

Pokrywa: mapowanie nut MIDI, rejestry (przez library_tool.check),
regułę nazw paczki, render kodu na syntetycznych próbkach, bramki QA.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coda_synth  # noqa: E402
import sig_audio as dsp  # noqa: E402
import build_pack  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(name: str, cond: bool, info: str = "") -> None:
    if cond:
        print(f"ok  {name}")
    else:
        FAILURES.append(name)
        print(f"FAIL {name} {info}")


def test_midi() -> None:
    check("midi C4", dsp.midi_from_token("C4") == 60)
    check("midi A2", dsp.midi_from_token("A2") == 45)
    check("midi A#3", dsp.midi_from_token("A#3") == 58)
    check("midi roundtrip", dsp.midi_to_name(dsp.midi_from_token("F#5")) == "F#5")


def test_pack_rule(tmp: Path) -> None:
    good = tmp / "good"
    good.mkdir()
    (good / "1.mp3").write_bytes(b"fake")
    (good / "212.mp3").write_bytes(b"fake")
    names = build_pack.zip_pack(good, tmp / "pack.zip")
    check("pack flat names", names == ["1.mp3", "212.mp3"])
    import zipfile
    with zipfile.ZipFile(tmp / "pack.zip") as z:
        check("pack flat zip", z.namelist() == ["1.mp3", "212.mp3"])
    bad = tmp / "bad"
    bad.mkdir()
    (bad / "1_v2.mp3").write_bytes(b"fake")
    try:
        build_pack.zip_pack(bad, tmp / "bad.zip")
        check("pack rejects 1_v2.mp3", False, "- zaakceptowano złą nazwę")
    except SystemExit:
        check("pack rejects 1_v2.mp3", True)


def test_coda_render(tmp: Path) -> None:
    sr = dsp.SR
    for midi, hz in [(48, 130.0), (55, 196.0)]:
        t = np.linspace(0, 1.2, int(sr * 1.2), endpoint=False)
        wave = np.stack([np.sin(2 * np.pi * hz * t) * 0.3, np.zeros_like(t)])
        import soundfile as sf
        sf.write(tmp / f"n{midi}.wav", wave.T, sr)
    instrument = {"samples": {"48": str(tmp / "n48.wav"), "55": str(tmp / "n55.wav")}}
    gesture = {"notes": [{"midi": 48, "on": 0.0, "off": 0.8, "vel": 0.9},
                         {"midi": 55, "on": 0.6, "off": 1.4, "vel": 0.8}],
               "delivery": {"humanize": {"timing_ms": 15.0, "vel": 0.05}}}
    r1 = coda_synth.render_coda(gesture, instrument, seed=42)
    r2 = coda_synth.render_coda(gesture, instrument, seed=42)
    check("coda deterministyczna", np.allclose(r1.wave, r2.wave))
    check("coda niepusta", len(r1.wave[0]) > sr * 1.3 and float(np.abs(r1.wave).max()) > 0.01)
    gesture_missing = {"notes": [{"midi": 90, "on": 0.0, "off": 0.5, "vel": 0.9}]}
    r3 = coda_synth.render_coda(gesture_missing, instrument, seed=1)
    check("coda ostrzega o braku nuty", any("brak nuty" in w for w in r3.warnings))


def test_qa_gates() -> None:
    import render_signature
    sr = dsp.SR
    mix = np.stack([np.full(2 * sr, 0.06), np.full(2 * sr, 0.06)])
    audit = {"length_sec": 2.0, "hero_over_context_db": 9.0, "hero_rms": -16.0}
    errors = render_signature.check_gates(mix, {}, audit)
    check("QA przepuszcza poprawną", errors == [], f"-> {errors}")
    quiet = mix * 0.01
    errors = render_signature.check_gates(quiet, {}, audit)
    check("QA łapie cichy mix", any("dB" in e for e in errors))
    bad_audit = {"length_sec": 2.0, "hero_over_context_db": 2.0}
    errors = render_signature.check_gates(mix, {}, bad_audit)
    check("QA łapie słyszalność hero", any("hero" in e for e in errors))
    long_audit = {"length_sec": 11.0, "hero_over_context_db": 9.0}
    errors = render_signature.check_gates(mix, {}, long_audit)
    check("QA łapie >10 s", any("10" in e for e in errors))


def test_registries_and_reading() -> None:
    result = subprocess.run([sys.executable, str(REPO / "scripts" / "library_tool.py"), "check"],
                            capture_output=True, text=True, cwd=REPO)
    check("library_tool check", result.returncode == 0, result.stdout[-400:])
    result = subprocess.run([sys.executable, str(REPO / "scripts" / "check_required_reading.py")],
                            capture_output=True, text=True, cwd=REPO)
    check("budżet lektury", result.returncode == 0, result.stdout[-300:])


def main() -> None:
    test_midi()
    with tempfile.TemporaryDirectory() as td:
        test_pack_rule(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_coda_render(Path(td))
    test_qa_gates()
    test_registries_and_reading()
    print(f"\n{len(FAILURES)} niepowodzeń" if FAILURES else "\nwszystkie testy OK")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
