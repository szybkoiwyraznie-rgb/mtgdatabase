#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g023 — dwa braki fabuły 222 (Maritime Guard), wszystko naraz:

  d  tło   `morze-wybrzeze` — czarne skaliste wybrzeże, fale, wichura (21 fabuł)
  b  instr `mroczna`        — ciemna barwa brzmienia (90 fabuł — najczęstszy
                              brak katalogu; slot b fabuły 222)

Hero (skradanie-cisza -> stealth_move_03) i koda (czujnosc-napiecie ->
g6c_sentry_return) fabuły 222 są już w bazie.

Kandydaci pod definicje TYPÓW (1:1), nie pod pojedynczą fabułę.
Tła: prawdziwe fale oceanu — okna nagrania CC0 z g022 (CVLTIV8R, Big Lagoon)
+ ewentualnie świeży zwiad freesound „storm sea waves rocks coast".
Instrumenty: VCSL (CC0) — pedał organowy, gong, niska marimba; kandydaci grają
frazę demo W REALNYM NISKIM REJESTRZE (ciemno), bez pitchowania.
Etykiety: m.* (morze), b.* (instrument) — unikatowe w skali bramki.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
import coda_synth  # noqa: E402
from build_gate_g003 import soft_limit  # noqa: E402
from build_gate_g015 import YSL_SRC, VCSL_SRC  # noqa: E402

GATE = REPO / "data" / "gates" / "g023"
CAND = GATE / "candidates"
VCSL = Path("/tmp/vcsl")
# batch g022 odzyskany z historii gita do /tmp — kolejne uruchomienie zwiadu
# CZYSCI legacy/source/sample_scout/ (workaround: trzymać surowce poza repo)
BATCH22 = Path("/tmp/water-splash")
PENMON = REPO / "legacy/source/sample_scout/freesound_storm-sea-waves-rocks-coast/01-857837-penmon-wind-11-11-2025.mp3"

SCOUT_CHANNEL = ("sample-scout run 36012073697 (preview-hq-mp3); manifest sha256: "
                 "data/gates/g023/source-manifest.json")
OCEAN_SRC = {
    "title": "Ocean Waves Crashing... Big Lagoon, Redwood (Freesound)",
    "author": "CVLTIV8R",
    "license": "CC0 / Public Domain (wg API Freesound)",
    "url": "https://freesound.org/people/CVLTIV8R/sounds/803679/",
    "channel": ("sample-scout run 36007698060 (preview-hq-mp3); manifest sha256: "
                "data/gates/g022/source-manifest.json"),
}

NOTE_RE = re.compile(r"([A-G]#?)(\d)")
NOTE_OFF = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
            "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def midi_of(name: str) -> int | None:
    m = NOTE_RE.search(name)
    if not m:
        return None
    return NOTE_OFF[m.group(1)] + (int(m.group(2)) + 1) * 12


def probe_line(seg: np.ndarray) -> str:
    rms = dsp.rms_db(seg)
    peak = float(np.max(np.abs(seg)))
    subs = [dsp.rms_db(seg[:, i:i + dsp.SR // 2]) for i in range(0, seg.shape[1] - dsp.SR // 2, dsp.SR // 2)]
    wobble = max(subs) - min(subs)
    return f"RMS {rms:.1f} dB, peak {20*np.log10(peak):.1f} dBFS, wahanie {wobble:.1f} dB"


def finish_bed(seg: np.ndarray, target: float = -32.0) -> np.ndarray:
    seg = soft_limit(seg, crest_db=14.0, rounds=4)
    seg = dsp.normalize_rms(seg, target)
    seg = dsp.fade(seg, 0.4, 0.6)
    peak = float(np.max(np.abs(seg)))
    ceiling = dsp.db_to_gain(-1.0)
    if peak > ceiling:
        seg *= ceiling / peak
    return seg


def bg_cand(name: str, label: str, title: str, entry_id: str, src: Path,
            t0: float, dur: float, desc: str, source: dict, notes: str):
    w, _ = dsp.load_any(src)
    seg = finish_bed(w[:, int(t0 * dsp.SR):int((t0 + dur) * dsp.SR)].copy())
    dsp.encode_mp3(CAND / f"{name}.mp3", seg)
    print(f"  {label} {title:38s} {probe_line(seg)}")
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": f"{source['title'].split('(')[0].strip()} — {source['license'].split('(')[0].strip()}",
        "entry": {
            "id": entry_id, "setting": "morze / sztormowe wybrzeże",
            "desc": desc,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": round(seg.shape[1] / dsp.SR, 2),
            "level_ref_db": -32, "loopable": True,
            "semantics": {"type": "morze-wybrzeze",
                          "traits": ["fale", "przybój", "szum morza", "wichura"],
                          "bad_for": ["wnętrze", "martwa cisza", "suchy krajobraz"]},
            "source": {**source, "notes": notes},
        },
    }


INSTR = {
    "b_pipeorgan_pedal": {
        "dir": VCSL / "Aerophones/Edge-blown Aerophones/Pipe Organ/Quiet Pedal",
        "pick": "PedalQuiet", "trim_sec": 8.0,
        "semantic": "głęboki, posępny pedał — przygaszony pomruk organów",
        "family": "aerophone-organ", "title": "cichy pedał organowy",
        "desc": "najniższe piszczałki organów w cichej dyspozycji — ciemny, "
                "dudniący fundament bez blasku",
        "traits": ["ciemny", "niski", "dudniący", "posępny"],
        "bad_for": ["jasny", "srebrzysty", "lekki", "figlarny"],
    },
    "b_gong": {
        "dir": VCSL / "Idiophones/Struck Idiophones/Gong 1",
        "pick": "gong_", "trim_sec": 6.0, "dyn_map": {"38": "gong_p", "39": "gong_mf", "41": "gong_f"},
        "semantic": "ciemny, metaliczny huk z długim ciemnym pogłosem",
        "family": "idiophone-struck", "title": "gong",
        "desc": "głęboki huk gongu — metaliczny cień, który długo nie umiera",
        "traits": ["ciemny", "metaliczny", "złowieszczy", "długi pogłos"],
        "bad_for": ["melodyczny", "figlarny", "jasny", "staccato"],
    },
    "b_marimba": {
        "dir": VCSL / "Idiophones/Struck Idiophones/Marimba",
        "pick": "_med_", "trim_sec": 4.0,
        "semantic": "ciemny, głucho-drzewny, miękki atak",
        "family": "idiophone-struck", "title": "niska marimba",
        "desc": "dolny rejestr marimby — drzewny, przytłumiony, poważny",
        "traits": ["ciemny", "drzewny", "przytłumiony", "miękki atak"],
        "bad_for": ["srebrzysty", "jasny", "metaliczny połysk", "wysoki"],
    },
}

# fraza demo w DÓŁ: C3–C4, żeby pokazać ciemny charakter (nie środkowy rejestr)
DEMO = {"notes": [
    {"midi": 48, "on": 0.0, "off": 0.7, "vel": 0.55},
    {"midi": 51, "on": 0.25, "off": 1.0, "vel": 0.55},
    {"midi": 54, "on": 0.5, "off": 1.3, "vel": 0.55},
    {"midi": 60, "on": 0.8, "off": 2.2, "vel": 0.6},
]}


def instr_cand(iid: str, label: str):
    spec = INSTR[iid]
    files: dict[int, Path] = {}
    for f in sorted(spec["dir"].glob("*.wav")):
        if "dyn_map" in spec:
            for midi_s, frag in spec["dyn_map"].items():
                if f.stem == frag:
                    files[int(midi_s)] = f
            continue
        if spec["pick"] not in f.name:
            continue
        m = midi_of(f.name)
        if m is not None:
            files[m] = f
    assert len(files) >= 3, f"{iid}: za mało nut ({len(files)})"
    gate_sources = {}
    for m, f in sorted(files.items()):
        w, _ = dsp.load_any(f)
        w = w[:, : int(spec["trim_sec"] * dsp.SR)]
        w = dsp.fade(w, 0.005, 0.5)
        name = f"{iid}_{f.name.replace('.wav', '.mp3').replace('#', 's')}"
        out = GATE / "instr_notes" / name
        out.parent.mkdir(parents=True, exist_ok=True)
        dsp.encode_mp3(out, w)
        gate_sources[str(m)] = f"instr_notes/{name}"
    entry = {
        "id": iid, "semantic": spec["semantic"], "family": spec["family"],
        "samples": {m: f"audio/library/instruments/{iid.replace('b_', '')}/{Path(rel).name}"
                    for m, rel in gate_sources.items()},
        "gate_sources": gate_sources,
        "semantics": {"type": "mroczna", "traits": spec["traits"], "bad_for": spec["bad_for"]},
        "source": dict(VCSL_SRC, notes=f"{len(gate_sources)} nut; wybór {spec['pick']}; trim {spec['trim_sec']} s"),
    }
    inst_abs = {**entry, "samples": {m: str(GATE / rel) for m, rel in gate_sources.items()}}
    r = coda_synth.render_coda(DEMO, inst_abs, seed=222)
    dsp.encode_mp3(CAND / f"{iid}_demo.mp3", r.wave)
    print(f"  {label} {spec['title']:38s} {probe_line(r.wave)}  (nut: {len(gate_sources)})")
    return {
        "label": label, "title": spec["title"], "file": f"candidates/{iid}_demo.mp3",
        "desc": spec["desc"], "source": "VCSL — CC0 (fraza demonstracyjna, realny rejestr)",
        "entry": entry,
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    print("TŁA (morze-wybrzeze, 8.0 s):")
    ocean = sorted(BATCH22.glob("01-*.mp3"))[0]
    sea_cands = [
        bg_cand("m_surf_surge", "m.1", "seria przypływu o skały", "sea_storm_01",
                ocean, 7.5, 8.0,
                "kolejne fale przewalają się jedna po drugiej — głęboki nurkujący pomruk "
                "i pienisty atak, jak uderzenia o czarne skały",
                OCEAN_SRC, "okno 7.5–15.5 s nagrania 01 (najbardziej energetyczna seria); poziom, fade"),
        bg_cand("m_heavy_roll", "m.2", "ciężki toczący się przypływ", "sea_storm_02",
                ocean, 55.5, 8.0,
                "ciężka, tocząca masa wody — wolniejszy rytm, głębszy rejestr, "
                "jak przypływ w nocy pod klifem",
                OCEAN_SRC, "okno 55.5–63.5 s nagrania 01; poziom, fade"),
        bg_cand("m_far_breakers", "m.3", "spokojniejsza toń z łękami", "sea_storm_03",
                ocean, 19.5, 8.0,
                "równiejszy szum toni z pojedynczymi łękami fal — przestrzeń "
                "między uderzeniami, surowa i szeroka",
                OCEAN_SRC, "okno 19.5–27.5 s nagrania 01; poziom, fade"),
    ]
    # m.4: świeży zwiad — Penmon wind (nadmorska wichura z tońszczą przypływu)
    if PENMON.exists():
        penmon_src = {
            "title": "Penmon wind 11-11-2025 (Freesound)",
            "author": "Noisyjones",
            "license": "CC0 (wg API Freesound)",
            "url": "https://freesound.org/people/Noisyjones/sounds/857837/",
            "channel": SCOUT_CHANNEL,
        }
        sea_cands.append(
            bg_cand("m_gale_surf", "m.4", "wichura nad przypływem (zwiad)",
                    "sea_storm_04", PENMON, 61.0, 8.0,
                    "nadmorska wichura ponad szumiącym przypływem — wiatr dominuje, "
                    "fale słychać głęboko pod spodem; najbardziej sztormowy z kandydatów",
                    penmon_src, "okno 61.0–69.0 s (najsilniejszy podmuch); CC0 wg API Freesound"))
    print("INSTRUMENTY (mroczna, fraza demo C4–B4 -> realny niski rejestr):")
    inst_cands = [instr_cand("b_pipeorgan_pedal", "b.1"),
                  instr_cand("b_gong", "b.2"),
                  instr_cand("b_marimba", "b.3")]
    manifest = {
        "id": "g023", "created": "2026-09-24", "story_id": "222",
        "note": ("Fabuła 222 Maritime Guard: dwa braki naraz (hero i koda już w bazie: "
                 "stealth_move_03 + g6c_sentry_return). `mroczna` to najczęściej wołany "
                 "brak katalogu (90 fabuł), `morze-wybrzeze` woła 21 fabuł — ten sam "
                 "duet braków ma też fabuła 28. Instrumenty grają frazę demo w realnym "
                 "niskim rejestrze (kodowa aranżuada C4–B4 przenosi się w dół)."),
        "entries": [
            {"slug": "morze-wybrzeze", "kind": "backgrounds",
             "role": "jedyny klocek typu tła `morze-wybrzeze` (21 fabuł; slot d fabuły 222)",
             "candidates": sea_cands},
            {"slug": "instr-mroczna", "kind": "instruments",
             "role": "jedyny klocek typu instrumentacji `mroczna` (90 fabuł; slot b fabuły 222)",
             "candidates": inst_cands},
        ],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    # proweniencja zwiadu (sumy sha256) — jak w g022
    srcs = []
    for p in [BATCH22 / "manifest.json",
              REPO / "legacy/source/sample_scout/freesound_storm-sea-waves-rocks-coast/manifest.json"]:
        if p.exists():
            srcs.extend(json.loads(p.read_text("utf-8")))
    (GATE / "source-manifest.json").write_text(
        json.dumps(srcs, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for c in sea_cands + inst_cands:
        p = GATE / c["file"]
        print(f"  {c['label']:6s} {p!s:70s} {p.stat().st_size/1024:5.0f} KB")
    print("manifest g023 zapisany")


if __name__ == "__main__":
    main()
