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
import library_tool  # noqa: E402

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


def test_coda_register_adapt() -> None:
    # oktawa: bank wine_glasses {63,66,68,74}; F#3 (54) -> F#4 (66), C5 (72) -> D5 (74)
    inst = {"samples": {"63": "a.wav", "66": "b.wav", "68": "c.wav", "74": "d.wav"}}
    resolved, warn = coda_synth.resolve_samples(inst, [54, 72])
    check("adaptacja oktawą F#3->F#4", resolved.get(54) == Path("b.wav"), str(warn))
    check("C5->D5 w ±3", resolved.get(72) == Path("d.wav"), str(warn))
    check("log adaptacji oktawą", any("oktawy" in w for w in warn))
    # jednolita transpozycja: bank timpani {38,39,41}; gest {33,38} -> 33->38, 38->41
    inst2 = {"samples": {"38": "x.wav", "39": "y.wav", "41": "z.wav"}}
    resolved2, warn2 = coda_synth.resolve_samples(inst2, [33, 38])
    check("transpozycja gestu: 33->38", resolved2.get(33) == Path("x.wav"), str(warn2))
    check("transpozycja gestu: 38->41", resolved2.get(38) == Path("z.wav"), str(warn2))
    check("log transpozycji", any("transponowany" in w for w in warn2))
    # niedopasowalne nuty dalej są pomijane z ostrzeżeniem
    resolved3, warn3 = coda_synth.resolve_samples({"samples": {"60": "q.wav"}}, [30, 90])
    check("niedopasowane pominięte", 30 not in resolved3 and 90 not in resolved3)
    check("log pominięć", any("pominięta" in w for w in warn3))


def test_loop_seam() -> None:
    sr = dsp.SR
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    wave = np.stack([np.sin(2 * np.pi * 220 * t) * 0.5] * 2)
    looped = dsp.loop_to_length(wave, int(sr * 1.4))
    check("loop: docelowa długość", looped.shape[1] == int(sr * 1.4))
    diffs = np.abs(np.diff(looped[0]))
    seam = int(sr * 0.5)
    win = diffs[max(seam - 220, 0): seam + 220]
    base = float(np.median(diffs[:2000]))
    check("loop: szew bez kliku", float(win.max()) < 6 * max(base, 1e-9),
          f"max={win.max():.6f} base={base:.6f}")


def test_coda_min_sustain() -> None:
    # krótka nuta (0.1 s) nie może zniknąć: render dźwięczy co najmniej ~MIN_NOTE_AUDIBLE_SEC
    import soundfile as sf
    sr = dsp.SR
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        t = np.linspace(0, 2.2, int(sr * 2.2), endpoint=False)
        sf.write(tmp / "n48.wav", np.stack([np.sin(2 * np.pi * 300 * t) * 0.3] * 2).T, sr)
        inst = {"samples": {"48": str(tmp / "n48.wav")}}
        r = coda_synth.render_coda({"notes": [{"midi": 48, "on": 0.0, "off": 0.1, "vel": 0.9}]},
                                   inst, seed=3)
        late = r.wave.mean(axis=0)[int(sr * 0.9):int(sr * 1.1)]
        check("nuta: minimum brzmienia", float(late.std()) > 0.01, f"late rms={late.std():.5f}")
        check("nuta: log minimum brzmienia", any("minimum" in w for w in r.warnings), str(r.warnings))


def test_note_attack_gate() -> None:
    import render_signature
    sr = dsp.SR
    t = np.linspace(0, 2.0, int(sr * 2.0), endpoint=False)
    base = {"length_sec": 2.0, "hero_over_context_db": 9.0, "hero_rms": -16.0}
    # nuta słabsza od kontekstu -> bramka odrzuca
    mix = np.stack([np.sin(2 * np.pi * 220 * t) * 0.06] * 2)
    audit = dict(base, coda_notes=1, coda_notes_total=1, coda_note_ons=[1.0])
    errors = render_signature.check_gates(mix, {}, audit)
    check("QA łapie pochowaną nutę", any("atak" in e for e in errors), str(errors))
    # nuta z gestu zagubiona przez adaptację -> błąd liczby nut
    audit2 = dict(base, coda_notes=1, coda_notes_total=2, coda_note_ons=[1.0])
    errors2 = render_signature.check_gates(mix, {}, audit2)
    check("QA łapie zgubioną nutę gestu", any("niezagranych" in e for e in errors2), str(errors2))
    # wyraźny atak -> brak błędu o ataku
    mix3 = np.stack([np.sin(2 * np.pi * 220 * t) * 0.01] * 2)
    a, b = int(sr * 1.0), int(sr * 1.3)
    mix3[:, a:b] += np.stack([np.sin(2 * np.pi * 330 * t) * 0.2] * 2)[:, a:b]
    audit3 = dict(base, coda_notes=1, coda_notes_total=1, coda_note_ons=[1.0])
    errors3 = render_signature.check_gates(mix3, {}, audit3)
    check("QA przepuszcza słyszalną nutę", not any("atak" in e for e in errors3), str(errors3))


def test_usage_policy() -> None:
    def recipe(sid: str, suffix: str) -> dict:
        return {
            "story_id": sid,
            "background": {"id": f"bg_{suffix}"},
            "hero": {"id": f"hero_{suffix}"},
            "coda": {"gesture": f"gesture_{suffix}", "instrument": f"instrument_{suffix}"},
        }

    legacy = recipe("1", "old")
    unique = recipe("18", "new")
    errors, _, growth, _ = library_tool.usage_audit([legacy, unique])
    check("różnorodność: tryb wzrostu aktywny", growth)
    check("różnorodność: nowe cztery klocki przechodzą", not errors, str(errors))
    reused = recipe("18", "old")
    errors2, _, _, _ = library_tool.usage_audit([legacy, reused])
    check("różnorodność: reuse w trybie wzrostu odrzucony",
          len(errors2) == 4, str(errors2))


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
    test_coda_register_adapt()
    test_loop_seam()
    test_coda_min_sustain()
    test_note_attack_gate()
    test_qa_gates()
    test_usage_policy()
    test_registries_and_reading()
    print(f"\n{len(FAILURES)} niepowodzeń" if FAILURES else "\nwszystkie testy OK")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
