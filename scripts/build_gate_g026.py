#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g026 — fabuła 249 „Feedback” (losowanie 2026-09-24, ziarno 20260924).

Trzy braki z resolvera (typ bez klocka), trzy wpisy, trzech kandydatów na wpis:
  1) tło `dwor-komnaty`      — cicha komnata maga, skupiona cisza (k.1–k.3),
  2) koda `spokoj-kontemplacja` — oszczędny gest skupienia po ciosie (s.1–s.3),
  3) instrument `ostro-gwaltowna` — nagłe, tnące smyczki (o.1–o.3, sekcja/solo/pizz).

Materiał:
  - Sample Scout (Freesound, CC0): room tone — spokojne wnętrza;
  - VSCO 2 CE (github.com/sgossner, CC0): sekcje/solo smyczkowe, artykulacje
    spiccato i pizzicato (nagłe, tnące — dokładnie typ), próbkowane per nuta,
    wariacje głośności v2 = najostrzejsze uderzenie.
Etykiety unikalne w skali bramki (k/s/o).
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
import coda_synth  # noqa: E402

GATE = REPO / "data" / "gates" / "g026"
CAND = GATE / "candidates"
SCOUT = REPO / "work" / "scout"
VSCO = Path("/tmp/vsco2ce/Strings")

VSCO_SRC = {
    "title": "Versilian Studios Chamber Orchestra 2 CE (VSCO-2-CE)",
    "author": "Sam Gossner / Versilian Studios + społeczność",
    "license": "CC0 1.0",
    "url": "https://github.com/sgossner/VSCO-2-CE",
    "channel": "git clone sparse z github.com/sgossner/VSCO-2-CE",
}


def _src(manifest_dir: str, idx0: int, notes: str) -> dict:
    man = json.loads((SCOUT / manifest_dir / "manifest.json").read_text("utf-8"))
    c = man[idx0]
    return {
        "title": f"{c['name']} (Freesound)",
        "author": c["author"],
        "license": "CC0 / Public Domain (wg API Freesound)",
        "url": c["source_url"],
        "channel": "sample-scout (preview-hq-mp3); manifest: " + manifest_dir,
        "notes": notes + f"; freesound id {c['source_id']}",
    }


def hp(wave: np.ndarray, hz: float) -> np.ndarray:
    sos = butter(2, hz, btype="highpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1)


def steady_bed(seg: np.ndarray, length: float = 8.0) -> np.ndarray:
    out = dsp.loop_to_length(seg, int(length * dsp.SR))
    return dsp.fade(out, 1.5, 1.5)


# ---------------------------------------------------------------- tło: dwor-komnaty
def bg_candidates() -> list[dict]:
    cands: list[dict] = []

    # --- k.1: neutralna skupiona cisza („Calm Room Tone — India”, okno ustabilizowane)
    w, _ = dsp.load_any(SCOUT / "roomtone/04-739159-calm-room-tone-india.mp3")
    seg = hp(dsp.cut(w, 120.0, 128.0), 55.0)
    seg = dsp.normalize_rms(seg, -32.0)
    dsp.encode_mp3(CAND / "k1_skupiona_cisza.mp3", steady_bed(seg))
    cands.append({
        "label": "k.1", "title": "skupiona cisza — jednostajny oddech wnętrza",
        "file": "candidates/k1_skupiona_cisza.mp3",
        "desc": "najrówniejsze wnętrze w paczce (wahanie okienkowe < 1 dB): samo "
                "powietrze komnaty, zero ptaków i zdarzeń — cisza, w której słychać myśl",
        "source": _src("roomtone", 3, "okno 120–128 s; HP 55 Hz; -32 dB"),
        "entry": {
            "id": "chamber_quiet_01",
            "setting": "gmach / komnata — skupiona cisza wnętrza",
            "desc": "jednostajne powietrze cichej komnaty — bez zdarzeń, bez mowy; "
                    "skupienie zawieszone w kamieniu",
            "file": "audio/library/backgrounds/chamber_quiet_01.mp3",
            "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
            "semantics": {"type": "dwor-komnaty",
                          "traits": ["wnętrze", "cisza", "komnata", "skupienie"],
                          "bad_for": ["plener", "bitwa", "tłum"]},
            "source": _src("roomtone", 3, "okno 120–128 s; HP 55 Hz; -32 dB"),
        },
    })
    print("  k.1 zapisany")

    # --- k.2: komnata w kamieniu z dalekimi szumami („quiet cellar”)
    w, _ = dsp.load_any(SCOUT / "roomtone/01-637805-room-tone-quiet-cellar-with-distant-noises-flac.mp3")
    seg = hp(dsp.cut(w, 30.0, 38.0), 45.0)
    seg = dsp.normalize_rms(seg, -32.0)
    dsp.encode_mp3(CAND / "k2_komnata_w_kamieniu.mp3", steady_bed(seg))
    cands.append({
        "label": "k.2", "title": "komnata spod kamienia — mruk murów, szumy za nimi",
        "file": "candidates/k2_komnata_w_kamieniu.mp3",
        "desc": "wnętrze otoczone grubą skałą: 87% energii poniżej 250 Hz — głęboki "
                "oddech murów z bardzo rzadkimi, oddalonymi szumami (zdarzenia wnętrza 250-2k)",
        "source": _src("roomtone", 0, "okno 30–38 s; HP 45 Hz; -32 dB"),
        "entry": {
            "id": "chamber_stone_01",
            "setting": "gmach / wieża — komnata otoczona kamieniem",
            "desc": "niski mruk kamiennego wnętrza z oddalonymi szumami za murami — "
                    "bierna, ciężka cisza architektury",
            "file": "audio/library/backgrounds/chamber_stone_01.mp3",
            "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
            "semantics": {"type": "dwor-komnaty",
                          "traits": ["wnętrze", "kamień", "mury", "ciężka cisza"],
                          "bad_for": ["plener", "lekkie wnętrze", "tłum"]},
            "source": _src("roomtone", 0, "okno 30–38 s; HP 45 Hz; -32 dB"),
        },
    })
    print("  k.2 zapisany")

    # --- k.3: korytarze kolegium za ścianą („hotel room” — bardzo dalekie głosy + niski puls)
    w, _ = dsp.load_any(SCOUT / "roomtone/03-406507-room-tone-hotel-room-quiet-very-distant-voices-a.mp3")
    seg = hp(dsp.cut(w, 60.0, 68.0), 45.0)
    seg = dsp.normalize_rms(seg, -32.0)
    dsp.encode_mp3(CAND / "k3_za_murami.mp3", steady_bed(seg))
    cands.append({
        "label": "k.3", "title": "życie za murami — bardzo dalekie głosy, niski tętent maszyny",
        "file": "candidates/k3_za_murami.mp3",
        "desc": "komnata, gdzie „żyje” tylko budynek: znikome, niezrozumiałe głosy "
                "za ścianą i cichy niski rezonans — jak dalekie sale Kolegium za zamkniętymi drzwiami",
        "source": _src("roomtone", 2, "okno 60–68 s; HP 45 Hz; -32 dB"),
        "entry": {
            "id": "chamber_hall_01",
            "setting": "gmach / komnaty — życie gmachu za murami",
            "desc": "cisza komnaty z niezrozumiałym szeptem dalekich korytarzy i niskim "
                    "tętnem instalacji gmachu",
            "file": "audio/library/backgrounds/chamber_hall_01.mp3",
            "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
            "semantics": {"type": "dwor-komnaty",
                          "traits": ["wnętrze", "dalekie głosy", "gmach", "rezonans"],
                          "bad_for": ["plener", "bitwa", "martwa cisza"]},
            "source": _src("roomtone", 2, "okno 60–68 s; HP 45 Hz; -32 dB"),
        },
    })
    print("  k.3 zapisany")
    return cands


# ---------------------------------------------------------------- koda: spokoj-kontemplacja
# Nuty siatki b_piano_steinway (48,50,54,56,60,64,68,72,74,76,80,84).
GESTURES = {
    "g10a_scar_breath": {
        "semantic": "spokój — oddech z blizną; nauka, która zostaje",
        "desc": "jedna długa niska nuta trwa w skupieniu, pod nią jedno wzniesienie — "
                "jak wdech, który zabolał; kończy niżej, w pokorze",
        "notes": [
            {"midi": 60, "on": 0.0, "off": 2.40, "vel": 0.34},
            {"midi": 68, "on": 0.90, "off": 1.35, "vel": 0.30},
            {"midi": 50, "on": 1.80, "off": 2.80, "vel": 0.32},
        ],
    },
    "g10b_lesson_fall": {
        "semantic": "spokój — nauka spada w dół i nie podnosi się",
        "desc": "dwie nuty: górna pyta, dolna odpowiada o nonę niżej i zostaje — "
                "ciężar, który zamienia się w ciszę",
        "notes": [
            {"midi": 64, "on": 0.0, "off": 0.80, "vel": 0.36},
            {"midi": 54, "on": 0.85, "off": 2.70, "vel": 0.40},
        ],
    },
    "g10c_humble_pulse": {
        "semantic": "spokój — pokorny puls kontemplacji",
        "desc": "trzy ciche, równe dotknięcia tej samej nuty jak odliczanie oddechu, "
                "ostatni przygaszony jeszcze bardziej — myśl wraca do prostoty",
        "notes": [
            {"midi": 56, "on": 0.00, "off": 0.60, "vel": 0.34},
            {"midi": 56, "on": 0.95, "off": 1.55, "vel": 0.34},
            {"midi": 56, "on": 1.90, "off": 2.80, "vel": 0.28},
        ],
    },
}


def gesture_candidates() -> list[dict]:
    instruments = json.loads((REPO / "data/library/instruments.json").read_text("utf-8"))
    piano = next(e for e in instruments["entries"] if e["id"] == "b_piano_steinway")
    piano_abs = {**piano, "samples": {m: str(REPO / p) for m, p in piano["samples"].items()}}
    cands: list[dict] = []
    for gid, spec in GESTURES.items():
        gesture = {"notes": spec["notes"], "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}}}
        r = coda_synth.render_coda(gesture, piano_abs, seed=249)
        for w in r.warnings:
            print(f"  ! {gid}: {w}")
        dsp.encode_mp3(CAND / f"{gid}.mp3", r.wave)
        cands.append({
            "label": {"g10a_scar_breath": "s.1", "g10b_lesson_fall": "s.2",
                      "g10c_humble_pulse": "s.3"}[gid],
            "title": spec["semantic"].split("—", 1)[1].strip(),
            "file": f"candidates/{gid}.mp3",
            "desc": spec["desc"],
            "source": "gest autorski; podgląd na b_piano_steinway (render neutralny)",
            "entry": {
                "id": gid,
                "semantic": spec["semantic"],
                "desc": spec["desc"],
                "notes": spec["notes"],
                "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}},
                "instrument_tags": ["piano", "struck-light", "bowed-hard"],
                "semantics": {"type": "spokoj-kontemplacja",
                              "traits": ["skupiona", "oszczędna", "pokorna", "oddychająca"],
                              "bad_for": ["triumfalna", "taneczna", "gwałtowna", "jałowa"]},
            },
        })
        print(f"  {gid} zapisany")
    return cands


# ---------------------------------------------------------------- instrument: ostro-gwaltowna
NOTE_RE = __import__("re").compile(r"_([A-G][#s]?)(\d)_v")


def midi_of_stem(stem: str) -> int | None:
    m = NOTE_RE.search(stem)
    if not m:
        return None
    base = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
            "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    name = m.group(1).replace("s", "#")
    return base[name] + 12 * (int(m.group(2)) + 1)


# motif demonstracyjny: twarde sztychy (nuty WSPÓLNE wszystkich trzech banków:
# {43,45,57,60,64,67} — zero podstawień rejestrowych w żadnym demo)
DEMO = {
    "notes": [
        {"midi": 57, "on": 0.00, "off": 0.55, "vel": 0.85},
        {"midi": 57, "on": 0.30, "off": 0.85, "vel": 0.85},
        {"midi": 60, "on": 0.60, "off": 1.15, "vel": 0.90},
        {"midi": 64, "on": 0.95, "off": 1.50, "vel": 0.95},
        {"midi": 60, "on": 1.30, "off": 1.85, "vel": 0.85},
        {"midi": 57, "on": 1.70, "off": 2.25, "vel": 0.85},
        {"midi": 45, "on": 2.10, "off": 2.90, "vel": 0.95},
    ],
}


INSTRS = {
    "b_vlnens_spic": {
        "label": "o.1", "title": "sekcja skrzypiec — spiccato (odbijany smyczek)",
        "src_dir": VSCO / "Violin Section/Spic", "prefix": "VlnEns_Spic_",
        "family": "bowed-strings",
        "semantic": "tnące, odbite uderzenia smyczka — sekcja skrzypiec tnie rytm",
        "desc": "odbicie smyczka w sekcji skrzypiec: każda nuta to kłucie z masą "
                "zbiorową — ostre, ale o krawędzi drewna i dętyki, nie metalu",
        "traits": ["ostry", "gwałtowny", "tnący", "perkusyjny smyczek"],
        "bad_for": ["łagodny", "legato", "śpiewny", "mglisty"],
    },
    "b_soloviol_spic": {
        "label": "o.2", "title": "solo skrzypce — spiccato (wyszczerbiony atak)",
        "src_dir": VSCO / "Solo Violin/spic", "prefix": "LLVln_spic_",
        "family": "bowed-strings",
        "semantic": "solo kłucie smyczkiem — bliżej, ostrzej, bardziej brutalnie",
        "desc": "jedno skrzypce, spiccato blisko mikrofonu: szczotkowana, "
                "wyszczerbiona kreska ataku — najostrzejszy z trzech, surowy",
        "traits": ["ostry", "gwałtowny", "solo", "szorstki"],
        "bad_for": ["łagodny", "masa orkiestry", "miękki", "śpiewny"],
    },
    "b_vlnens_pizz": {
        "label": "o.3", "title": "sekcja skrzypiec — pizzicato szarpane",
        "src_dir": VSCO / "Violin Section/Pizz", "prefix": "VlnEns_Pizz_",
        "family": "bowed-strings",
        "semantic": "szarpane struny — sprężyste kliknięcia tnące jak pejcz",
        "desc": "mocne pizzicato sekcji: sprężyste uderzenie palca w strunę — "
                "krótkie, migotliwe, o krawędzi jak warkocz trzaskającego pejcza",
        "traits": ["ostry", "gwałtowny", "szarpany", "migotliwy"],
        "bad_for": ["legato", "ciężki dół", "długi ton", "miękki"],
    },
}


def instr_candidate(iid: str, spec: dict) -> dict:
    # bank: najostrzejsza wariacja (v2), pierwszy round-robin (rr1)
    samples: dict[int, Path] = {}
    for f in sorted(spec["src_dir"].glob(f"{spec['prefix']}*_v2_rr1.wav")):
        midi = midi_of_stem(f.stem)
        if midi is not None:
            samples[midi] = f
    assert len(samples) >= 8, f"{iid}: za mało nut ({len(samples)})"
    notes_dir = GATE / "instr_notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    gate_sources: dict[str, str] = {}
    lib_samples: dict[str, str] = {}
    for midi, src in samples.items():
        out_name = f"{iid}_{src.stem}.mp3"
        w, _ = dsp.load_any(src)
        dsp.encode_mp3(notes_dir / out_name, dsp.cut(w, 0.0, 2.0))
        gate_sources[str(midi)] = f"instr_notes/{out_name}"
        lib_samples[str(midi)] = f"audio/library/instruments/{iid[2:]}/{out_name}"
    inst_abs = {"samples": {m: str(notes_dir / Path(p).name) for m, p in gate_sources.items()}}
    r = coda_synth.render_coda({**DEMO, "delivery": {}}, inst_abs, seed=42)
    for w in r.warnings:
        print(f"  ! demo {iid}: {w}")
    dsp.encode_mp3(CAND / f"{iid}_demo.mp3", r.wave)
    lo = dsp.midi_to_name(min(samples)); hi = dsp.midi_to_name(max(samples))
    return {
        "label": spec["label"], "title": spec["title"],
        "file": f"candidates/{iid}_demo.mp3",
        "desc": spec["desc"] + f" — bank {len(samples)} nut {lo}–{hi}, demo: sztychy na nutach wspólnych banków "
              f"(zero podstawień rejestrowych)",
        "source": f"{VSCO_SRC['title']} — CC0 1.0 (artykulacja jak w nazwie; wariacja v2)",
        "entry": {
            "id": iid,
            "semantic": spec["semantic"],
            "family": spec["family"],
            "samples": lib_samples,
            "gate_sources": gate_sources,
            "semantics": {"type": "ostro-gwaltowna", "traits": spec["traits"],
                          "bad_for": spec["bad_for"]},
            "source": {**VSCO_SRC,
                       "notes": f"{spec['title']}; bank {len(samples)} nut {lo}–{hi} ({VSCO_SRC['url']}); "
                               "wariacja v2 (najostrzejsza), rr1; trim 2.0 s"},
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": "g026",
        "created": "2026-09-24",
        "story_id": "249",
        "note": "Fabuła 249 z losowania sesji (ziarno 20260924; resolver: 3 typy bez klocka z 4 "
                "warstw). Hero `rozblysk-swiatla` obsadzony klockiem light_bloom_01. Tła: "
                "trzy room tone z Freesound (czysta cisza / kamień / życie za murami). "
                "Kody: trzy autorskie gesty skupienia. Instrument: trzy artykulacje "
                "tnącej sekcji/solo smyczkowego z VSCO-2-CE (CC0) — każda z pełnym bankiem nut.",
        "entries": [
            {"slug": "tlo-dwor-komnaty", "kind": "backgrounds",
             "role": "jedyny klocek typu tła `dwor-komnaty` (17 fabuł; slot d fabuły 249)",
             "candidates": bg_candidates()},
            {"slug": "koda-spokoj", "kind": "gestures",
             "role": "jedyny klocek typu kody `spokoj-kontemplacja` (21 fabuł; slot a fabuły 249)",
             "candidates": gesture_candidates()},
            {"slug": "instr-ostro", "kind": "instruments",
             "role": "jedyny klocek typu instrumentacji `ostro-gwaltowna` (30 fabuł; slot b fabuły 249)",
             "candidates": [instr_candidate(iid, spec) for iid, spec in INSTRS.items()]},
        ],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest g026 zapisany ({len(manifest['entries'])} wpisy)")


if __name__ == "__main__":
    main()
