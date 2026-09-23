#!/usr/bin/env python3
"""Budowa bramki g002 (tryb wpisowy, ADR 0004): 6 wpisów × 3 kandydaci.

Wpisy (decyzja agenta, leżą pod przyszłe fabuły kolekcji):
  grandpiano      (b) — pianino koncertowe/referencyjne: Kawai / Steinway B / Yamaha Upright
  beben-wojenny   (b) — niski bęben marszowy: Bass Drum 1 / Bass Drum 2 / Frame Drum
  ryk-bestii      (c) — okrzyk wielkiej dzikiej bestii: elk bugle / kojoty / bizon
  ogien-palenisko (d) — trzaskający ogień: 3 natężenia
  wir-energia     (d) — rozdarcie/portal: syk i bąbel pary/gorąca glina
  koda-swiatlo    (a) — jasny gest muzyczny (magia, runy, uzdrowienie): 3 figury

Uruchomienie: .venv/bin/python scripts/build_gate_g002.py
Wymaga: /tmp/ysl (sparse: Coyotes, Elk, Bison (rut), Fire, Fumaroles,
Black Growler Steam Vent, Artist Paint Pots) i /tmp/vcsl (pliki per lista niżej).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import av
import lameenc

import sys

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
import coda_synth  # noqa: E402

GATE_SOURCES_GLOBAL: dict[str, dict[str, str]] = {}  # wypełniane przez convert_notes()

YSL = Path("/tmp/ysl")
VCSL = Path("/tmp/vcsl")
G = REPO / "data" / "gates" / "g002"
YSL_SRC = {
    "title": "Yellowstone Sound Library (NPS)",
    "author": "National Park Service",
    "license": "Public Domain (utwór rządu USA)",
    "url": "https://www.nps.gov/yell/learn/photosmultimedia/soundlibrary.htm",
    "channel": "git clone sparse z github.com/rosuH/YSL (mirror)",
}
VCSL_SRC = {
    "title": "Versilian Studios Chamber Orchestra (VCSL)",
    "author": "Sam Gossner / Versilian Studios",
    "license": "CC0",
    "url": "https://github.com/sgossner/VCSL",
    "channel": "git clone sparse z github.com/sgossner/VCSL",
}


def encode128(path: Path, wave: np.ndarray) -> None:
    w = np.clip(wave, -1.0, 1.0)
    pcm16 = (w * 32767).astype(np.int16)
    inter = np.stack([pcm16[0], pcm16[1] if pcm16.shape[0] > 1 else pcm16[0]], axis=1).tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(128)
    enc.set_in_sample_rate(dsp.SR)
    enc.set_channels(2)
    enc.set_quality(2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(enc.encode(inter) + enc.flush())


def load_src(args) -> tuple[np.ndarray, int]:
    return dsp.load_any(args)


def field_stem(src: Path, t0: float, t1: float, out: Path, fade_i=0.08, fade_o=0.4) -> float:
    w, _ = load_src(src)
    seg = dsp.cut(w, t0, t1).copy()
    seg = dsp.fade(seg, fade_i, min(fade_o, seg.shape[1] / (2 * dsp.SR)))
    encode128(out, seg)
    rms = dsp.rms_db(seg)
    print(f"  stem {out.name}: {t0}–{t1} s, {seg.shape[1]/dsp.SR:.1f} s, {rms:.1f} dB")
    return round(seg.shape[1] / dsp.SR, 2)


# ---------- 1. Polowe stemmy z YSL ----------

def build_field_stems() -> dict[str, dict]:
    print("== stemmy polowe (YSL)")
    info: dict[str, dict] = {}

    def ysl(folder: str) -> Path:
        hits = list((YSL / folder).glob("Sound Library*.mp3"))
        assert hits, f"brak mp3 w {YSL/folder} — sprawdź sparse-checkout"
        return hits[0]

    # hero: ryk bestii
    spec_heroes = {
        "beast_elk_bugle_01": ("Elk", 73.0, 77.0, "kwik łosia w rui — długi, metaliczny, przenikliwy", "c_bugle_01.mp3"),
        "beast_coyote_yip_01": ("Coyotes", 3.2, 5.6, "zbiorowe skomlenie-wyje kojotów — rójne, dzikie", "c_yip_01.mp3"),
        "beast_bison_bellow_01": ("Bison (rut)", 82.8, 84.8, "niski pomruk bizona — ciężki, z gruntu", "c_llow_01.mp3"),
    }
    for eid, (folder, t0, t1, desc, fname) in spec_heroes.items():
        dur = field_stem(ysl(folder), t0, t1, G / "candidates" / fname, fade_i=0.02, fade_o=0.3)
        info[eid] = {"dur": dur, "desc": desc, "src_label": folder, "notes": f"{folder} {t0}-{t1} s"}

    # tła: ogień ×3 i wir-energia ×3
    spec_beds = {
        "fire_hearth_small_01": ("Fire", 5.0, 13.0, "małe ognisko — oszczędne trzaski"),
        "fire_hearth_full_01": ("Fire", 14.0, 22.0, "rozłożony ogień — pełne palenisko"),
        "fire_hearth_dim_01": ("Fire", 38.0, 46.0, "przygaszony dogorywający ogień"),
        "energy_steam_roar_01": ("Black Growler Steam Vent", 4.0, 12.0, "groźny ryk pary ze szczeliny — ciągły"),
        "energy_steam_light_01": ("Fumaroles", 6.0, 14.0, "lekki szum fumaroli — zawiesista mgła dźwiękowa"),
        "energy_mud_bubble_01": ("Artist Paint Pots", 18.0, 26.0, "bulgotanie gorącej gliny — organiczna magia"),
    }
    for eid, (folder, t0, t1, desc) in spec_beds.items():
        dur = field_stem(ysl(folder), t0, t1, G / "candidates" / f"d_{eid[:14]}.mp3")
        info[eid] = {"dur": dur, "desc": desc, "src_label": folder, "notes": f"{folder} {t0}-{t1} s"}
    return info


# ---------- 2. Nuty z VCSL + banki instrumentów ----------

INSTRUMENTS = {
    "b_piano_kawai": {
        "semantic": "czyste, referencyjne",
        "family": "zither-struck",
        "vcsl_dir": "Chordophones/Zithers/Grand Piano, Kawai/Sustains",
        "notes": {str(m): f"GPiano_sus_{n}_v1_rr1_Player.wav" for m, n in [
            (48, "C3"), (50, "D3"), (54, "F#3"), (58, "A#3"),
            (62, "D4"), (66, "F#4"), (70, "A#4"), (72, "C5"),
            (75, "D#5"), (78, "F#5"), (81, "A5"), (84, "C6")]},
        "label": "Kawai Grand",
        "caveat": "",
    },
    "b_piano_steinway": {
        "semantic": "jasne, koncertowe",
        "family": "zither-struck",
        "vcsl_dir": "Chordophones/Zithers/Grand Piano, Steinway B/NoSus",
        "notes": {str(m): f"JHPiano_NoSus_Close_{n}_vl3_rr1.wav" for m, n in [
            (48, "C3"), (50, "D3"), (54, "F#3"), (56, "G#3"),
            (60, "C4"), (64, "E4"), (68, "G#4"), (72, "C5"),
            (74, "D5"), (76, "E5"), (80, "G#5"), (84, "C6")]},
        "label": "Steinway B",
        "caveat": "odbiór bliski (NoSus Close)",
    },
    "b_piano_yamaha": {
        "semantic": "intymne, pokojowe",
        "family": "zither-struck",
        "vcsl_dir": "Chordophones/Zithers/Upright Piano, Yamaha/Sustains",
        "notes": {str(m): f"Upright1_Sus_{n}_vl3_rr1.wav" for m, n in [
            (36, "C2"), (43, "G2"), (48, "C3"), (55, "G3"),
            (60, "C4"), (67, "G4"), (72, "C5")]},
        "label": "Yamaha Upright",
        "caveat": "UWAGA: bank rzadki (tylko tony C i G) — demo z adaptacją skali; "
                  "gesty spoza tych tonów będą przestrajane",
    },
    "b_bassdrum_new": {
        "semantic": "suchy, uderzeniowy",
        "family": "membranophone",
        "vcsl_dir": "Membranophones/Struck Membranophones/Bass Drum 1",
        "notes": {"38": "BDrumNew_hit_v2_rr1_Sum.wav", "39": "BDrumNew_hit_v3_rr1_Sum.wav",
                  "41": "BDrumNew_hit_v5_rr1_Sum.wav"},
        "label": "Bass Drum 1 (soft/mid/hard)",
    },
    "b_bassdrum": {
        "semantic": "teatralny, z wybrzmieniem",
        "family": "membranophone",
        "vcsl_dir": "Membranophones/Struck Membranophones/Bass Drum 2",
        "notes": {"38": "bassdrum_hit_mf1.wav", "39": "bassdrum_hit_f.wav", "41": "bassdrum_hit_ff.wav"},
        "label": "Bass Drum 2 (mf/f/ff)",
    },
    "b_frame_drum": {
        "semantic": "pierwotny, plemienny",
        "family": "membranophone",
        "vcsl_dir": "Membranophones/Struck Membranophones/Frame Drum",
        "notes": {"38": "HDrumL_HitMuted_v2_rr1_Sum.wav", "39": "HDrumL_Hit_v2_rr1_Sum.wav",
                  "41": "HDrumL_Hand_rr1_Sum.wav"},
        "label": "Frame Drum (muted/hit/hand)",
    },
}

DEMO_PIANO = {"notes": [
    {"midi": 48, "on": 0.0, "off": 0.7, "vel": 0.55},
    {"midi": 60, "on": 0.20, "off": 1.0, "vel": 0.6},
    {"midi": 66, "on": 0.40, "off": 1.4, "vel": 0.55},
    {"midi": 72, "on": 0.60, "off": 2.3, "vel": 0.5},
]}
DEMO_DRUM = {"notes": [
    {"midi": 38, "on": 0.0, "off": 0.30, "vel": 0.85},
    {"midi": 38, "on": 0.40, "off": 0.70, "vel": 0.82},
    {"midi": 41, "on": 0.95, "off": 2.4, "vel": 0.9},
]}

GESTURES = {
    "g5a_shimmer_up": {
        "semantic": "jasny błysk wznoszący",
        "desc": "szybka kaskada w górę przez kwinty — rozjarowienie, odkrycie",
        "notes": [{"midi": 66, "on": 0.0, "off": 0.4, "vel": 0.52},
                  {"midi": 72, "on": 0.16, "off": 0.6, "vel": 0.55},
                  {"midi": 78, "on": 0.32, "off": 0.9, "vel": 0.58},
                  {"midi": 84, "on": 0.48, "off": 1.9, "vel": 0.62}],
        "instrument_tags": ["struck-light", "zither", "piano"],
    },
    "g5b_light_bell": {
        "semantic": "jasny dzwon odpowiedzi",
        "desc": "wysoki sygnał zamieniający się w cichsze echo — znak z drugiej strony",
        "notes": [{"midi": 84, "on": 0.0, "off": 1.05, "vel": 0.60},
                  {"midi": 78, "on": 0.60, "off": 1.9, "vel": 0.50},
                  {"midi": 72, "on": 1.50, "off": 2.5, "vel": 0.42}],
        "instrument_tags": ["struck-light", "zither", "piano"],
    },
    "g5c_light_ripple": {
        "semantic": "jasną falujące otwarcie",
        "desc": "migocząca kwinta jak odbicie na wodzie — napięcie złagodzone",
        "notes": [{"midi": 72, "on": 0.0, "off": 1.0, "vel": 0.50},
                  {"midi": 78, "on": 0.25, "off": 1.2, "vel": 0.46},
                  {"midi": 72, "on": 0.90, "off": 1.9, "vel": 0.42},
                  {"midi": 78, "on": 1.30, "off": 2.4, "vel": 0.38}],
        "instrument_tags": ["struck-light", "zither", "piano"],
    },
}


def convert_notes() -> dict[str, dict[str, str]]:
    print("== konwersje nut (VCSL → mp3)")
    gate_sources: dict[str, dict[str, str]] = {}
    for iid, spec in INSTRUMENTS.items():
        gate_sources[iid] = {}
        for midi, fname in spec["notes"].items():
            src = VCSL / spec["vcsl_dir"] / fname
            assert src.exists(), f"brak {src} — dołóż do sparse-checkout /tmp/vcsl"
            w, _ = load_src(src)
            out = G / "instr_notes" / f"{iid}_{fname.replace('.wav', '.mp3')}"
            encode128(out, w)
            gate_sources[iid][midi] = f"instr_notes/{out.name}"
        print(f"  {iid}: {len(spec['notes'])} nut")
    return gate_sources


def instrument_def(iid: str, gate_sources: dict[str, str]) -> dict:
    spec = INSTRUMENTS[iid]
    return {
        "id": iid,
        "semantic": spec["semantic"],
        "family": spec["family"],
        "samples": {midi: f"audio/library/instruments/{iid.replace('b_', '')}/{Path(rel).name}"
                    for midi, rel in gate_sources.items()},
        "gate_sources": gate_sources,
        "source": dict(VCSL_SRC, notes=f"żądana nuta per plik; okno demo seed 7"),
    }


def render_demos(gate_sources: dict[str, dict[str, str]]) -> None:
    print("== demo instrumentów (fraza w realnym zakresie)")
    piano_demo = dict(DEMO_PIANO)
    drum_demo = dict(DEMO_DRUM)
    kawai_def = instrument_def("b_piano_kawai", gate_sources["b_piano_kawai"])
    for iid, spec in INSTRUMENTS.items():
        idef = instrument_def(iid, gate_sources[iid])
        idef_gate = {**idef, "samples": {m: str(G / rel) for m, rel in idef["gate_sources"].items()}}
        demo_g = piano_demo if spec["family"].startswith("zither") else drum_demo
        r = coda_synth.render_coda(demo_g, idef_gate, seed=7)
        encode128(G / "candidates" / f"b_{spec['label'].split()[0].lower()}_{iid[-6:]}demo.mp3", r.wave)
        for w in r.warnings:
            print("   !", w)
        print(f"  {iid}: demo ({r.note_count} nut)")
    print("== demo gestów koda-światło (referencja: Kawai)")
    ref = {**kawai_def, "samples": {m: str(G / rel) for m, rel in kawai_def["gate_sources"].items()}}
    for gid, gdef in GESTURES.items():
        r = coda_synth.render_coda(gdef, ref, seed=3)
        encode128(G / "candidates" / f"a_{gid}.mp3", r.wave)
        for w in r.warnings:
            print("   !", w)
        (G / "defs").mkdir(exist_ok=True)
        (G / "defs" / f"{gid}.json").write_text(json.dumps(gdef, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
        print(f"  {gid}: demo ({r.note_count} nut)")


# ---------- 3. Manifest trybu wpisowego ----------

def cand(label, title, file, desc, source, entry):
    return {"label": label, "title": title, "file": file, "desc": desc, "source": source, "entry": entry}


def ysl_entry_source(eid_info) -> dict:
    return dict(YSL_SRC, notes=eid_info["notes"])


def build_manifest(field: dict[str, dict]) -> None:
    entries = []

    def bg_entry(eid):
        inf = field[eid]
        return {
            "id": eid, "setting": "ogień / palenisko" if eid.startswith("fire") else "energia / rozdarcie",
            "desc": inf["desc"],
            "file": f"audio/library/backgrounds/{eid}.mp3",
            "duration_sec": inf["dur"], "level_ref_db": -33, "loopable": True,
            "source": ysl_entry_source(inf),
        }

    def hero_entry(eid, character, good, bad):
        inf = field[eid]
        return {
            "id": eid, "role": "okrzyk dużej dzikiej bestii", "character": character,
            "distance": "średni", "energy": "wysoka", "duration_sec": inf["dur"],
            "desc": inf["desc"], "good_for": good, "bad_for": bad,
            "file": f"audio/library/heroes/{eid}.mp3",
            "source": ysl_entry_source(inf),
        }

    ysl_src_lbl = lambda folder: f"Yellowstone Sound Library (NPS) — {folder}; Public Domain (utwór rządu USA)"

    # grandpiano
    pianos = ["b_piano_kawai", "b_piano_steinway", "b_piano_yamaha"]
    entries.append({
        "slug": "grandpiano", "kind": "instruments",
        "role": "pianino koncertowe — instrument referencyjny gestów i jasny głos kodu",
        "candidates": [
            cand(f"p.{i+1}", INSTRUMENTS[iid]["label"],
                 f"candidates/b_{INSTRUMENTS[iid]['label'].split()[0].lower()}_{iid[-6:]}demo.mp3",
                 INSTRUMENTS[iid]["semantic"]
                 + (f"; {INSTRUMENTS[iid]['caveat']}" if INSTRUMENTS[iid].get("caveat") else "")
                 + f" ({len(INSTRUMENTS[iid]['notes'])} próbek w banku)",
                 "VCSL (CC0) — " + INSTRUMENTS[iid]["label"],
                 instrument_def(iid, GATE_SOURCES_GLOBAL[iid]))
            for i, iid in enumerate(pianos)],
    })
    # beben-wojenny
    drums = ["b_bassdrum_new", "b_bassdrum", "b_frame_drum"]
    entries.append({
        "slug": "beben-wojenny", "kind": "instruments",
        "role": "niski bęben marszowo-bojowy — puls armii, szarży, ryku startu",
        "candidates": [
            cand(f"b.{i+1}", INSTRUMENTS[iid]["label"],
                 f"candidates/b_{INSTRUMENTS[iid]['label'].split()[0].lower()}_{iid[-6:]}demo.mp3",
                 INSTRUMENTS[iid]["semantic"] + " (3 dynamiki)",
                 "VCSL (CC0) — " + INSTRUMENTS[iid]["label"],
                 instrument_def(iid, GATE_SOURCES_GLOBAL[iid]))
            for i, iid in enumerate(drums)],
    })
    # ryk-bestii
    entries.append({
        "slug": "ryk-bestii", "kind": "heroes",
        "role": "pojedynczy, czytelny okrzyk dużej dzikiej bestii jako hero fabuły",
        "candidates": [
            cand("c.1", "kwik łosia", "candidates/c_bugle_01.mp3",
                 field["beast_elk_bugle_01"]["desc"], ysl_src_lbl("Elk"),
                 hero_entry("beast_elk_bugle_01", "ostry, przenikliwy",
                            "najeźdźczą dzicz, baloth, fanfara bestii", "kameralne, magiczne fabuły")),
            cand("c.2", "skomlenie kojotów", "candidates/c_yip_01.mp3",
                 field["beast_coyote_yip_01"]["desc"], ysl_src_lbl("Coyotes"),
                 hero_entry("beast_coyote_yip_01", "rójny, histeryczny",
                            "pogranicze, sfora, opuszczone ziemie", "heroiczne, uroczyste fabuły")),
            cand("c.3", "pomruk bizona", "candidates/c_llow_01.mp3",
                 field["beast_bison_bellow_01"]["desc"], ysl_src_lbl("Bison (rut)"),
                 hero_entry("beast_bison_bellow_01", "ciężki, ziemisty",
                            "gigant, rozpęd, potęga ziemi", "zręczne, przestronne fabuły")),
        ],
    })
    # ogień-palenisko
    entries.append({
        "slug": "ogien-palenisko", "kind": "backgrounds",
        "role": "trzaskający ogień jako tło obozu / komnaty / pożogi",
        "candidates": [
            cand("d.1", "małe ognisko", "candidates/d_fire_hearth_sm.mp3",
                 field["fire_hearth_small_01"]["desc"], ysl_src_lbl("Fire"), bg_entry("fire_hearth_small_01")),
            cand("d.2", "rozłożony ogień", "candidates/d_fire_hearth_fu.mp3",
                 field["fire_hearth_full_01"]["desc"], ysl_src_lbl("Fire"), bg_entry("fire_hearth_full_01")),
            cand("d.3", "dogorywający", "candidates/d_fire_hearth_di.mp3",
                 field["fire_hearth_dim_01"]["desc"], ysl_src_lbl("Fire"), bg_entry("fire_hearth_dim_01")),
        ],
    })
    # wir-energia
    entries.append({
        "slug": "wir-energia", "kind": "backgrounds",
        "role": "fasada-dźwiękowa rozdarcia/portalu: ciągły syk, drganie, bulgot",
        "candidates": [
            cand("d.1", "ryczenie pary", "candidates/d_energy_steam_r.mp3",
                 field["energy_steam_roar_01"]["desc"], ysl_src_lbl("Black Growler Steam Vent"), bg_entry("energy_steam_roar_01")),
            cand("d.2", "lekki szum pary", "candidates/d_energy_steam_l.mp3",
                 field["energy_steam_light_01"]["desc"], ysl_src_lbl("Fumaroles"), bg_entry("energy_steam_light_01")),
            cand("d.3", "bulgot gorącej gliny", "candidates/d_energy_mud_bub.mp3",
                 field["energy_mud_bubble_01"]["desc"], ysl_src_lbl("Artist Paint Pots"), bg_entry("energy_mud_bubble_01")),
        ],
    })
    # koda-swiatlo
    entries.append({
        "slug": "koda-swiatlo", "kind": "gestures",
        "role": "jasny muzyczny znak (magia, runa, uzdrowienie, otwarcie portalu)",
        "candidates": [
            cand("a.1", "kaskada wznosząca", "candidates/a_g5a_shimmer_up.mp3",
                 GESTURES["g5a_shimmer_up"]["desc"] + " (na pianinie, seed 3)",
                 "definicja własna, CC0",
                 dict(GESTURES["g5a_shimmer_up"], id="g5a_shimmer_up")),
            cand("a.2", "dzwon odpowiedzi", "candidates/a_g5b_light_bell.mp3",
                 GESTURES["g5b_light_bell"]["desc"] + " (na pianinie, seed 3)",
                 "definicja własna, CC0",
                 dict(GESTURES["g5b_light_bell"], id="g5b_light_bell")),
            cand("a.3", "fala-otwarcie", "candidates/a_g5c_light_ripple.mp3",
                 GESTURES["g5c_light_ripple"]["desc"] + " (na pianinie, seed 3)",
                 "definicja własna, CC0",
                 dict(GESTURES["g5c_light_ripple"], id="g5c_light_ripple")),
        ],
    })

    manifest = {
        "id": "g002",
        "created": "2026-09-23",
        "note": "Tryb wpisowy (ADR 0004): dla każdego wpisu 3 kandydaci; wybór właściciela = dokładnie 1 na wpis.",
        "entries": entries,
    }
    G.mkdir(parents=True, exist_ok=True)
    (G / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8")
    n = sum(len(e["candidates"]) for e in entries)
    print(f"== manifest: {len(entries)} wpisów, {n} kandydatów -> {G/'manifest.json'}")


def main() -> None:
    global GATE_SOURCES_GLOBAL
    field = build_field_stems()
    GATE_SOURCES_GLOBAL = convert_notes()
    render_demos(GATE_SOURCES_GLOBAL)
    build_manifest(field)
    print("gotowe. Następnie: .venv/bin/python scripts/gate_preview.py data/gates/g002 --port 8080")


if __name__ == "__main__":
    main()
