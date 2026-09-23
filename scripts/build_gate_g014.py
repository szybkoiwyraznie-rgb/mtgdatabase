#!/usr/bin/env python3
"""Bramka g014 — komplet czterech braków dla fabuły 18.

Lotusguard Disciple: aven osłania pędzący rydwan-glider świetlistą barierą.
Zgodnie z polityką różnorodności nie dokładamy kolejnego użycia istniejących
klocków przy małych bazach. Jedna bramka zawiera WSZYSTKIE potrzebne wpisy:

* hero: odłamki odbite przez tarczę — prawdziwe metalowe uderzenia CC0;
* tło: przelot pojazdu nad torem — terenowe nagranie skutera NPS/PD;
* koda: trzy warianty gestu domknięcia ochronnej aury;
* instrument: trzy dynamiki tego samego prawdziwego glockenspielu VCSL/CC0.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import sig_audio as dsp
import coda_synth
import build_gate_g003 as gate_dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g014"
CAND = GATE / "candidates"
METAL = Path("/tmp/atomcut/packs/opengameart-100-cc0-metal-and-wood-sfx/audio")
SNOWMOBILE = Path("/tmp/ysl/Snowmobile/Sound Library - Snowmobile.mp3")
GLOCK = Path("/tmp/vcsl/Idiophones/Struck Idiophones/Glockenspiel")

METAL_SOURCE = {
    "title": "100 metal and wood SFX (OpenGameArt)", "author": "rubberduck",
    "license": "CC0 1.0 (public domain)",
    "url": "https://opengameart.org/content/100-cc0-metal-and-wood-sfx",
    "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
}
YSL_SOURCE = {
    "title": "Yellowstone Sound Library — Snowmobile",
    "author": "National Park Service", "license": "Public Domain (utwór rządu USA)",
    "url": "https://www.nps.gov/yell/learn/photosmultimedia/soundlibrary.htm",
    "channel": "git clone sparse z github.com/rosuH/YSL (mirror)",
}
VCSL_SOURCE = {
    "title": "Versilian Community Sample Library — Glockenspiel",
    "author": "Versilian Studios + społeczność", "license": "CC0 1.0",
    "url": "https://github.com/sgossner/VCSL",
    "channel": "git clone sparse (no-cone) z github.com/sgossner/VCSL",
}


def hero_mix(files: list[str], times: list[float], gains: list[float]) -> np.ndarray:
    parts = [dsp.load_any(METAL / f)[0] for f in files]
    total = max(int(t * dsp.SR) + p.shape[1] for t, p in zip(times, parts))
    out = np.zeros((2, total), dtype=np.float64)
    for part, at, gain in zip(parts, times, gains):
        i = int(at * dsp.SR)
        out[:, i:i + part.shape[1]] += part * gain
    out = gate_dsp.soft_limit(out, crest_db=12.0, rounds=5)
    return dsp.fade(dsp.normalize_rms(out, -15.0), 0.004, 0.09)


def hero_candidate(name: str, label: str, title: str, entry_id: str,
                   files: list[str], times: list[float], gains: list[float],
                   desc: str, character: str) -> dict:
    wave = hero_mix(files, times, gains)
    dsp.encode_mp3(CAND / f"{name}.mp3", wave)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": "prawdziwe metalowe uderzenia — rubberduck, CC0",
        "entry": {
            "id": entry_id,
            "role": "seria odłamków odbitych przez świeżo utworzoną magiczną tarczę",
            "character": character, "distance": "bliski", "energy": "wysoka",
            "duration_sec": round(wave.shape[1] / dsp.SR, 2), "desc": desc,
            "good_for": "magiczna bariera, odbicie pocisków, ochrona w ostatniej chwili",
            "bad_for": "atak przebijający cel, ciężka brama, komediowy pancerz",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "source": {**METAL_SOURCE,
                "notes": ("packs/opengameart-100-cc0-metal-and-wood-sfx; "
                          + " + ".join(f"{f.removesuffix('.m4a')} @ {t:.2f}s"
                                     for f, t in zip(files, times))
                          + "; bez pitchowania i syntezy")},
        },
    }


def background_candidate(name: str, label: str, title: str, entry_id: str,
                         start: float, desc: str, setting: str) -> dict:
    wave, _ = dsp.load_any(SNOWMOBILE)
    seg = wave[:, int(start * dsp.SR):int((start + 8.0) * dsp.SR)].copy()
    hp = butter(2, 65.0, btype="highpass", fs=dsp.SR, output="sos")
    seg = sosfiltfilt(hp, seg, axis=-1)
    seg = dsp.fade(dsp.normalize_rms(seg, -33.0), 0.25, 0.45)
    dsp.encode_mp3(CAND / f"{name}.mp3", seg)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": "terenowy przejazd skutera — Yellowstone NPS, domena publiczna",
        "entry": {
            "id": entry_id, "setting": setting, "desc": desc,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": 8.0, "level_ref_db": -33, "loopable": True,
            "source": {**YSL_SOURCE,
                       "notes": f"Snowmobile {start:.1f}–{start + 8.0:.1f} s; filtr rumble 65 Hz, bez pitchowania"},
        },
    }


def gesture_candidate(label: str, title: str, gdef: dict, desc: str) -> dict:
    piano = next(e for e in json.loads((REPO / "data/library/instruments.json").read_text())[
        "entries"] if e["id"] == "b_piano_steinway")
    rendered = coda_synth.render_coda(gdef, piano, seed=18)
    name = f"a_{gdef['id']}.mp3"
    dsp.encode_mp3(CAND / name, dsp.normalize_rms(rendered.wave, -18.0))
    return {"label": label, "title": title, "file": f"candidates/{name}",
            "desc": desc, "source": "definicja nutowa; demo na zatwierdzonym Steinwayu",
            "entry": gdef}


GLOCK_FILES = {
    "soft": {67: "glock_soft_G4_01.wav", 72: "glock_soft_C5_02.wav",
             79: "glock_soft_G5_01.wav", 84: "glock_soft_C6_01.wav",
             91: "glock_soft_G6_01.wav", 96: "glock_soft_C7_03.wav"},
    "medium": {67: "glock_medium_G4_01.wav", 72: "glock_medium_C5_01.wav",
               79: "glock_medium_G5_01.wav", 84: "glock_medium_C6_01.wav",
               91: "glock_medium_G6_01.wav", 96: "glock_medium_C7_01.wav"},
    "loud": {67: "glock_loud_G4_01.wav", 72: "glock_loud_C5_01.wav",
             79: "glock_loud_G5_01.wav", 84: "glock_loud_C6_01.wav",
             92: "glock_loud_G#6_01.wav", 96: "glock_loud_C7_01.wav"},
}


def instrument_candidate(dynamic: str, label: str, title: str, desc: str,
                         semantic: str) -> dict:
    entry_id = f"b_glockenspiel_{dynamic}"
    gate_sources: dict[str, str] = {}
    target_samples: dict[str, str] = {}
    demo_samples: dict[str, str] = {}
    for midi, filename in GLOCK_FILES[dynamic].items():
        wave, _ = dsp.load_any(GLOCK / filename)
        rel = f"candidates/instruments/{entry_id}/{midi}.mp3"
        dsp.encode_mp3(GATE / rel, wave)
        gate_sources[str(midi)] = rel
        target_samples[str(midi)] = f"audio/library/instruments/glockenspiel_{dynamic}/{midi}.mp3"
        demo_samples[str(midi)] = str(GATE / rel)
    demo_gesture = {
        "id": "demo", "notes": [
            {"midi": 72, "on": 0.0, "off": 0.45, "vel": 0.62},
            {"midi": 79, "on": 0.35, "off": 0.9, "vel": 0.72},
            {"midi": 84, "on": 0.75, "off": 1.7, "vel": 0.8}],
        "delivery": {"humanize": {"timing_ms": 0, "vel": 0.0}}}
    demo_entry = {"id": entry_id, "samples": demo_samples}
    rendered = coda_synth.render_coda(demo_gesture, demo_entry, seed=18)
    demo_name = f"b_{entry_id}.mp3"
    dsp.encode_mp3(CAND / demo_name, dsp.normalize_rms(rendered.wave, -18.0))
    return {
        "label": label, "title": title, "file": f"candidates/{demo_name}",
        "desc": desc, "source": f"VCSL Glockenspiel, dynamika {dynamic}, CC0",
        "entry": {
            "id": entry_id, "semantic": semantic, "family": "idiophone-struck",
            "samples": target_samples, "gate_sources": gate_sources,
            "source": {**VCSL_SOURCE,
                       "notes": f"Glockenspiel {dynamic}; rzeczywiste próbki G/C w zakresie G4–C7; demo w realnym zakresie"},
        },
    }


def main() -> None:
    for required in (METAL, SNOWMOBILE, GLOCK):
        if not required.exists():
            raise SystemExit(f"brak źródła: {required}")
    CAND.mkdir(parents=True, exist_ok=True)
    for old in CAND.glob("*.mp3"):
        old.unlink()

    heroes = [
        hero_candidate("s_solid_deflection", "s.1", "twarde odbicie", "shield_deflect_01",
            ["metal-hit-03.m4a", "metal-hit-01.m4a", "metal-hit-03.m4a"],
            [0.0, 0.22, 0.47], [1.0, 0.78, 0.62],
            "trzy zwarte uderzenia z metalowym korpusem — bariera przyjmuje cięższe odłamki",
            "twardy, zwarty, ochronny"),
        hero_candidate("s_ringing_barrier", "s.2", "dźwięczna bariera", "shield_deflect_02",
            ["metal-sheet-05.m4a", "metal-sheet-03.m4a", "metal-sheet-06.m4a"],
            [0.0, 0.17, 0.38], [0.9, 0.76, 0.64],
            "trzy dźwięczne odbicia o dłuższym ogonie — bariera odpowiada rezonansem",
            "dźwięczny, jasny, rezonujący"),
        hero_candidate("s_rising_ricochet", "s.3", "narastający rykoszet", "shield_deflect_03",
            ["metal-hit-01.m4a", "metal-hit-03.m4a", "metal-hit-05.m4a"],
            [0.0, 0.19, 0.42], [0.58, 0.78, 1.0],
            "kolejne odbicia rosną do końcowego pingu — tarcza domyka się w ruchu",
            "narastający, sprężysty, triumfalny"),
    ]
    backgrounds = [
        background_candidate("w_distant_approach", "w.1", "daleki najazd", "race_glider_pass_01", 3.5,
            "pojazd narasta z dystansu do szybkiego przelotu — szeroka perspektywa toru",
            "tor wyścigowy / pojazd nadciąga"),
        background_candidate("w_close_pass", "w.2", "bliski przelot", "race_glider_pass_02", 5.5,
            "najgłośniejsza część przejazdu: stały mechaniczny pęd i powietrze przy pojeździe",
            "tor wyścigowy / bliski przelot glidera"),
        background_candidate("w_receding_pass", "w.3", "przelot i oddalenie", "race_glider_pass_03", 7.5,
            "pojazd mija punkt odsłuchu i stopniowo odchodzi — wyraźne poczucie prędkości",
            "tor wyścigowy / pojazd oddala się"),
    ]
    gesture_defs = [
        ("a.1", "łuk ochronny", {
            "id": "g18_guardian_arc", "semantic": "ochrona — świetlisty łuk wznosi się i domyka",
            "desc": "trzy stopnie w górę, ostatni dźwięk zostaje jak zamknięta kopuła",
            "notes": [{"midi": 72, "on": 0.0, "off": 0.55, "vel": 0.58},
                      {"midi": 79, "on": 0.32, "off": 0.95, "vel": 0.68},
                      {"midi": 84, "on": 0.72, "off": 2.15, "vel": 0.78}],
            "delivery": {"humanize": {"timing_ms": 14, "vel": 0.03}},
            "instrument_tags": ["bells", "glockenspiel", "glass"]},
            "wznoszący łuk trzech nut kończy się długim stabilnym światłem"),
        ("a.2", "pierścień bariery", {
            "id": "g18_guardian_ring", "semantic": "ochrona — dwa impulsy rozszerzają pierścień bariery",
            "desc": "dwa równe impulsy i wyższe domknięcie — aura pulsuje, potem twardnieje",
            "notes": [{"midi": 72, "on": 0.0, "off": 0.42, "vel": 0.62},
                      {"midi": 79, "on": 0.48, "off": 0.95, "vel": 0.68},
                      {"midi": 84, "on": 1.02, "off": 2.15, "vel": 0.76}],
            "delivery": {"humanize": {"timing_ms": 10, "vel": 0.025}},
            "instrument_tags": ["bells", "glockenspiel", "glass"]},
            "dwa pulsujące kroki rozszerzają pierścień, trzeci zamyka tarczę"),
        ("a.3", "czuwająca korona", {
            "id": "g18_guardian_crown", "semantic": "ochrona — wysoka korona czuwa nad niższym fundamentem",
            "desc": "niski fundament, dwie wysokie odpowiedzi i spokojne wspólne wybrzmienie",
            "notes": [{"midi": 72, "on": 0.0, "off": 2.2, "vel": 0.55},
                      {"midi": 84, "on": 0.28, "off": 0.82, "vel": 0.72},
                      {"midi": 79, "on": 0.86, "off": 2.2, "vel": 0.66}],
            "delivery": {"humanize": {"timing_ms": 12, "vel": 0.03}},
            "instrument_tags": ["bells", "glockenspiel", "glass"]},
            "stały fundament pod dwiema jasnymi odpowiedziami — ochrona zamiast triumfu"),
    ]
    gestures = [gesture_candidate(*spec) for spec in gesture_defs]
    instruments = [
        instrument_candidate("soft", "b.1", "glockenspiel miękki",
            "zaokrąglony atak i jasny ogon — bariera bardziej opiekuńcza niż bojowa",
            "jasny, łagodny, ochronny"),
        instrument_candidate("medium", "b.2", "glockenspiel średni",
            "czytelny metaliczny atak bez ostrości — równowaga światła i odporności",
            "świetlisty, czytelny, stabilny"),
        instrument_candidate("loud", "b.3", "glockenspiel mocny",
            "najtwardszy atak tej samej rodziny — bariera z bojowym konturem",
            "jasny, twardy, bojowy"),
    ]
    manifest = {
        "id": "g014", "created": date.today().isoformat(),
        "note": ("Komplet czterech wpisów do fabuły 18 (Lotusguard Disciple), wystawiony jednocześnie. "
                 "Nowe tło, hero, koda i instrument realizują politykę różnorodności przy małych bazach."),
        "entries": [
            {"slug": "odlamki-odbite-przez-tarcze", "kind": "heroes",
             "role": "seria odłamków odbitych przez świeżo utworzoną magiczną tarczę", "candidates": heroes},
            {"slug": "ped-glidera-nad-torem", "kind": "backgrounds",
             "role": "pęd pojazdu-glidera nad torem wyścigowym", "candidates": backgrounds},
            {"slug": "koda-ochronnej-bariery", "kind": "gestures",
             "role": "jasny gest domknięcia ochronnej aury", "candidates": gestures},
            {"slug": "glockenspiel-ochronny", "kind": "instruments",
             "role": "jasny metaliczny instrument dla ochronnej bariery", "candidates": instruments},
        ],
    }
    (GATE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for entry in manifest["entries"]:
        for cand in entry["candidates"]:
            wave, _ = dsp.load_any(GATE / cand["file"])
            print(f"{cand['label']:<3s} {entry['slug']:<31s} {wave.shape[1]/dsp.SR:4.2f}s RMS {dsp.rms_db(wave):5.1f} dB")


if __name__ == "__main__":
    main()
