"""Render muzycznego gestu (koda) na zatwierdzonym instrumencie.

Koda jest DEFINICJĄ nutową (docs/gate-protocol.md): absolutne numery MIDI,
czasy on/off i velocity. Instrument to mapa midi -> plik jednostkowy
(prawdziwe nagrania, np. VCSL/VSCO) albo zestaw artykulacji dla
instrumentów nietonowanych. Agent nie „komponuje" — wybiera gest z rejestru.

Deterministyczne: humanizacja (jitter timingu/velocity) jest ziarnicowana
seedem receptury, więc render jest powtarzalny.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

import sig_audio as dsp

MAX_SEMITONE_DISTANCE = 3  # instrument tonowany: najbliższa dostępna nuta w zasięgu ±3 półtony
MIN_NOTE_AUDIBLE_SEC = 1.2  # minimalny czas brzmienia nuty: krótsze wycinki (dł. percypowane
# jako „klik" pod tłem) są przedłużane do 1,2 s z łagodnym zanikiem — deterministycznie


@dataclass
class RenderedCoda:
    wave: np.ndarray  # stereo, zaczyna się w 0.0 s
    warnings: list[str]
    note_count: int
    events: list[dict] = None  # [{index, midi, on_sec, vel}] — faktyczne po humanizacji


def _collect_used_midis(gesture: dict) -> list[int]:
    return sorted({int(n["midi"]) for n in gesture.get("notes", [])})


def resolve_samples(instrument: dict, midis: list[int]) -> tuple[dict[int, Path], list[str]]:
    """Dopasuj żądane nuty do dostępnych sampli instrumentu.

    Instrument tonowany: dokładny midi albo najbliższy w ±3 półtony.
    Instrument nietonowany (samples = {"articulations": {...}}): nuty
    odwzorowywane na artykulacje wg kolejności velocity (soft/mid/hard).
    """
    warnings: list[str] = []
    samples = instrument.get("samples", {})
    if "articulations" in samples:
        art = samples["articulations"]
        order = ["soft", "mid", "hard"]
        chosen: dict[int, Path] = {}
        for m in midis:
            vel_bucket = "mid"
            chosen[m] = Path(art[vel_bucket][0] if isinstance(art[vel_bucket], list) else art[vel_bucket])
        return chosen, warnings
    have = {int(k): v for k, v in samples.items() if str(k).isdigit()}
    bank = sorted(have)

    def nearest(m: int) -> int | None:
        cand = [c for c in bank if abs(c - m) <= MAX_SEMITONE_DISTANCE]
        return min(cand, key=lambda c: abs(c - m)) if cand else None

    # Drabina adaptacji rejestru (deterministyczna, wszystko ląduje w warnings):
    # 1) dokładne midi albo najbliższe w ±3 półtony;
    resolved: dict[int, int] = {}
    for m in midis:
        n = nearest(m)
        if n is not None:
            resolved[m] = n
    # 2) niedopasowane nuty przenosimy o oktawę (±12, ±24), jeśli po przeniesieniu
    #    wpadają w bank w ±3 półtony;
    octave_fixed: set[int] = set()
    for m in midis:
        if m in resolved:
            continue
        choices: list[tuple[int, int, int, int]] = []
        for octs in (12, -12, 24, -24):
            n = nearest(m + octs)
            if n is not None:
                choices.append((abs(n - (m + octs)), abs(octs), -octs, n))
        if choices:
            choices.sort()
            d, _, _, n = choices[0]
            resolved[m] = n
            octave_fixed.add(m)
            warnings.append(f"nuta {dsp.midi_to_name(m)} ({m}) przeniesiona do najbliższej oktawy: {dsp.midi_to_name(n)}")
    # 3) gdy nadal brakuje nut: transponujemy CAŁY gest jednolicie, tak żeby jak
    #    najwięcej nut weszło w bank (rachunek: max skuteczności, potem min korekta,
    #    potem min |t|); kontur i rytm gestu zostają nietknięte.
    if any(m not in resolved for m in midis):
        best: tuple[tuple[int, int, int], int, dict[int, int | None]] | None = None
        for t in range(-24, 25):
            mapped = {m: nearest(m + t) for m in midis}
            cnt = sum(1 for v in mapped.values() if v is not None)
            dist = sum(abs(v - (m + t)) for m, v in mapped.items() if v is not None)
            key = (cnt, -dist, -abs(t))
            if best is None or key > best[0]:
                best = (key, t, mapped)
        assert best is not None
        (cnt, _, _), t, mapped = best
        if cnt > len(resolved):
            warnings.append(f"gest transponowany {t:+d} półtonów do zakresu instrumentu (dopasowane {cnt}/{len(midis)})")
            resolved = {m: v for m, v in mapped.items() if v is not None}
            octave_fixed = set()
    for m in midis:
        if m in resolved:
            if resolved[m] != m and m not in octave_fixed:
                warnings.append(f"nuta {dsp.midi_to_name(m)} zastąpiona najbliższą {dsp.midi_to_name(resolved[m])}")
        else:
            warnings.append(f"brak nuty {dsp.midi_to_name(m)} ({m}) po adaptacji rejestru — nuta pominięta")
    return {m: Path(have[n]) for m, n in resolved.items()}, warnings


def render_coda(gesture: dict, instrument: dict, seed: int = 0, level_ref_db: float = -20.0,
                gain_plan: list[float] | None = None) -> RenderedCoda:
    """Wyrenderuj gest na instrumencie. Zwraca waveform od 0.0 s.

    level_ref_db: docelowy RMS pojedynczej nuty przed skalowaniem velocity —
    względne proporcje velocity w gest zachowane. gain_plan: dodatkowe dB na
    kolejne nuty (w kolejności czasowej) — gałka autokalibracji z render_signature.
    """
    warnings: list[str] = []
    midis = _collect_used_midis(gesture)
    if not midis:
        return RenderedCoda(np.zeros((2, 1)), ["gest nie ma nut"], 0, [])
    resolved, warn = resolve_samples(instrument, midis)
    warnings.extend(warn)
    delivery = gesture.get("delivery", {})
    humanize = delivery.get("humanize", {})
    timing_jitter = float(humanize.get("timing_ms", 0.0)) / 1000.0
    vel_jitter = float(humanize.get("vel", 0.0))
    rng = np.random.default_rng(seed)
    cache: dict[int, np.ndarray] = {}
    for m, path in resolved.items():
        wave, _ = dsp.load_any(path)
        cache[m] = dsp.normalize_rms(wave, level_ref_db)
    end_sec = max((float(n["off"]) + timing_jitter * 3) for n in gesture["notes"]) + 1.0
    out = np.zeros((2, int(end_sec * dsp.SR)))
    placed = 0
    events: list[dict] = []
    for idx, note in enumerate(sorted(gesture["notes"], key=lambda n: float(n["on"]))):
        m = int(note["midi"])
        if m not in cache:
            continue
        wav = cache[m]
        slice_len = max(int((float(note["off"]) - float(note["on"])) * dsp.SR),
                        int(MIN_NOTE_AUDIBLE_SEC * dsp.SR))
        seg = wav[:, :slice_len] if wav.shape[1] > slice_len else wav
        if seg.shape[1] < slice_len:
            seg = np.hstack([seg, np.zeros((2, slice_len - seg.shape[1]))])
        # ucięcie nuty w połowie sustainu: łagodny zanik, żeby nie klikało
        seg = dsp.fade(seg, 0.005, min(0.35, seg.shape[1] / (2 * dsp.SR)))
        on = float(note["on"]) + (rng.uniform(-1, 1) * timing_jitter if timing_jitter else 0.0)
        if slice_len > int((float(note["off"]) - float(note["on"])) * dsp.SR) + 512:
            warnings.append(f"nuta {dsp.midi_to_name(m)}: brzmienie przedłużone do minimum {MIN_NOTE_AUDIBLE_SEC} s")
        vel = float(note.get("vel", 0.8))
        if vel_jitter:
            vel = float(np.clip(vel * (1.0 + rng.uniform(-vel_jitter, vel_jitter)), 0.05, 1.0))
        if gain_plan and idx < len(gain_plan) and gain_plan[idx]:
            vel *= float(dsp.db_to_gain(gain_plan[idx]))
        out = dsp.place(out, seg * vel, max(on, 0.0))
        events.append({"index": idx, "midi": m, "on_sec": round(max(on, 0.0), 3),
                       "vel": round(vel, 3)})
        placed += 1
    return RenderedCoda(out, warnings, placed, events)


def main() -> None:  # szybkie demo: python coda_synth.py gesture.json instrument.json out.mp3
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("gesture", type=Path)
    parser.add_argument("instrument", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    gesture = json.loads(args.gesture.read_text(encoding="utf-8"))
    instrument = json.loads(args.instrument.read_text(encoding="utf-8"))
    result = render_coda(gesture, instrument, seed=args.seed)
    for warning in result.warnings:
        print(f"! {warning}")
    dsp.encode_mp3(args.out, dsp.peak_ceiling(result.wave, 0.9))
    print(f"zapisano {args.out} ({result.note_count} nut)")


if __name__ == "__main__":
    main()
