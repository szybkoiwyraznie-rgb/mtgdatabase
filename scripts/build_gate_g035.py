#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g035 — kolejna paczka 5 braków po zamknięciu g034.

Zakres (po 3 kandydatów):
  1) background:step-rownina            — poprawka po g034: dużo ciszej, bez muzyki
  2) background:kuznia-warsztat         — poprawka po g034: miarowe kucie młotem w kuźni
  3) background:noc-ksiezyc             — nocne tło: księżyc, owady/wiatr, bez dziennego lasu
  4) background:laboratorium-technika   — techniczny hum / aparatura / terminale
  5) background:swiatynia-sanktuarium   — spokojna przestrzeń sakralna / rezonans dzwonu

Źródła: istniejące Freesound CC0 z sample-scout oraz atomcut/OpenGameArt/Kenney CC0.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
from build_gate_g003 import soft_limit  # noqa: E402

GATE = REPO / "data" / "gates" / "g035"
CAND = GATE / "candidates"
ATOM = Path("/tmp/atomcut_probe")


def load_scout_manifest(dir_name: str) -> dict[str, dict]:
    data = json.loads((REPO / "legacy" / "source" / "sample_scout" / dir_name / "manifest.json").read_text(encoding="utf-8"))
    return {Path(item["file"]).name: item for item in data}


def scout_source(item: dict, notes: str) -> dict:
    lic = item.get("license") or "brak informacji"
    if lic == "http://creativecommons.org/publicdomain/zero/1.0/":
        lic = "CC0 1.0 (public domain; wg API Freesound)"
    return {
        "title": f"{item.get('name')} (Freesound)",
        "author": item.get("author") or "brak informacji",
        "license": lic,
        "url": item.get("source_url") or item.get("comments") or "brak informacji",
        "channel": f"sample-scout (preview-hq-mp3); manifest: {item.get('source_id')}",
        "notes": notes,
    }


def pack_meta(pack: str) -> dict:
    p = ATOM / "packs" / pack / "pack.json"
    return json.loads(p.read_text(encoding="utf-8"))


def atom_source(pack: str, notes: str, files: list[str] | None = None) -> dict:
    meta = pack_meta(pack)
    return {
        "title": f"{meta['title']} (OpenGameArt/Kenney mirror)",
        "author": meta.get("publisher", {}).get("name") or meta.get("attribution", "brak informacji"),
        "license": "CC0 1.0 (public domain)",
        "url": meta.get("homepage", "brak informacji"),
        "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
        "notes": notes + (("; pliki: " + ", ".join(files)) if files else ""),
    }


def mixed_source(title: str, notes: str, sources: list[dict]) -> dict:
    return {
        "title": title,
        "author": "warstwowanie własne z próbek CC0",
        "license": "CC0 1.0 (public domain; wszystkie warstwy źródłowe CC0)",
        "url": "różne źródła CC0 — szczegóły w notes",
        "channel": "lokalny montaż bramki z próbek sample-scout/atomcut",
        "notes": notes + " | źródła: " + " ; ".join(f"{s['title']} [{s.get('notes','')} ]" for s in sources),
    }


def ensure_sources() -> None:
    needed = [
        REPO / "legacy/source/sample_scout/freesound_battle-swords/03-667115-mongolian-film-windblown-steppe1-wav.mp3",
        REPO / "legacy/source/sample_scout/freesound_quiet-room-tone/01-637805-room-tone-quiet-cellar-with-distant-noises-flac.mp3",
        REPO / "legacy/source/sample_scout/freesound_quiet-room-tone/02-724113-240219-002-tr1-2-ambient-roomtone-bedroom-open-w.mp3",
        REPO / "legacy/source/sample_scout/freesound_quiet-room-tone/04-739159-calm-room-tone-india.mp3",
        ATOM / "packs/opengameart-100-cc0-metal-and-wood-sfx/audio/hammer-01.m4a",
        ATOM / "packs/opengameart-100-cc0-metal-and-wood-sfx/audio/hammer-03.m4a",
        ATOM / "packs/opengameart-100-cc0-metal-and-wood-sfx/audio/metal-hit-02.m4a",
        ATOM / "packs/kenney-impact-sounds/audio/impact-mining-000.m4a",
        ATOM / "packs/kenney-impact-sounds/audio/impact-metal-heavy-001.m4a",
        ATOM / "packs/opengameart-swamp-environment-audio/audio/cricket-1.m4a",
        ATOM / "packs/opengameart-swamp-environment-audio/audio/cricket-2.m4a",
        ATOM / "packs/opengameart-swamp-environment-audio/audio/atmosphere-1.m4a",
        ATOM / "packs/opengameart-swamp-environment-audio/audio/cicada-1.m4a",
        ATOM / "packs/kenney-sci-fi-sounds/audio/computer-noise-000.m4a",
        ATOM / "packs/kenney-sci-fi-sounds/audio/computer-noise-003.m4a",
        ATOM / "packs/opengameart-30-cc0-sfx-loops/audio/machine-04.m4a",
        ATOM / "packs/opengameart-50-cc0-sci-fi-sfx/audio/loop-machine-01.m4a",
        ATOM / "packs/opengameart-100-cc0-sfx/audio/bell-01.m4a",
        ATOM / "packs/opengameart-100-cc0-sfx/audio/gong-01.m4a",
        ATOM / "packs/kenney-impact-sounds/audio/impact-bell-heavy-000.m4a",
    ]
    missing = [str(p) for p in needed if not p.exists()]
    if missing:
        raise SystemExit("Brak źródeł do g035:\n" + "\n".join(missing))


def clean_gate() -> None:
    if GATE.exists():
        shutil.rmtree(GATE)
    CAND.mkdir(parents=True, exist_ok=True)


def filt(x: np.ndarray, highpass: float | None = None, lowpass: float | None = None) -> np.ndarray:
    y = x.copy()
    if highpass:
        sos = butter(4, highpass, btype="highpass", fs=dsp.SR, output="sos")
        y = sosfiltfilt(sos, y, axis=-1)
    if lowpass:
        sos = butter(4, lowpass, btype="lowpass", fs=dsp.SR, output="sos")
        y = sosfiltfilt(sos, y, axis=-1)
    return y


def finalize(seg: np.ndarray, target_db: float, fade_in=0.08, fade_out=0.45,
             highpass: float | None = None, lowpass: float | None = None,
             limit=False) -> np.ndarray:
    seg = filt(seg, highpass, lowpass)
    seg = dsp.fade(seg, fade_in, fade_out)
    seg = dsp.normalize_rms(seg, target_db)
    if limit:
        seg = soft_limit(seg, crest_db=12.0, rounds=4)
        seg = dsp.normalize_rms(seg, target_db)
    return dsp.peak_ceiling(seg, 0.92)


def load_cut(src: Path, start: float, length: float) -> np.ndarray:
    wave, _ = dsp.load_any(src)
    seg = dsp.cut(wave, start, start + length)
    if seg.shape[1] < int(length * dsp.SR):
        seg = dsp.loop_to_length(seg, int(length * dsp.SR))
    return seg[:, : int(length * dsp.SR)]


def write_mp3(out: Path, seg: np.ndarray) -> tuple[float, float, float]:
    dsp.encode_mp3(out, seg)
    return round(seg.shape[1] / dsp.SR, 2), round(dsp.rms_db(seg), 1), round(dsp.spectral_share(seg, 6000.0), 3)


def bg_candidate(label: str, title: str, fname: str, entry_id: str, typ: str,
                 setting: str, desc: str, seg: np.ndarray, source: dict,
                 target_db: float, traits=None, bad_for=None, level_ref_db: float | None = None) -> dict:
    dur, rms, hf = write_mp3(CAND / fname, seg)
    desc2 = f"{desc} (czas {dur:.2f} s, RMS {rms} dB, HF>6k {hf:.1%})"
    return {
        "label": label,
        "title": title,
        "file": f"candidates/{fname}",
        "desc": desc2,
        "source": source["title"],
        "entry": {
            "id": entry_id,
            "setting": setting,
            "desc": desc2,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": dur,
            "level_ref_db": level_ref_db if level_ref_db is not None else target_db,
            "loopable": True,
            "semantics": {"type": typ, "traits": traits or [], "bad_for": bad_for or []},
            "source": source,
        },
    }


def rhythmic_forge(out_len: float, hits: list[Path], bed: np.ndarray | None,
                   times: list[float], target_db: float, hit_db: float = -24.0,
                   lowpass: float | None = 10500) -> np.ndarray:
    n = int(out_len * dsp.SR)
    mix = np.zeros((2, n))
    if bed is not None:
        bed = dsp.loop_to_length(bed, n)
        bed = finalize(bed[:, :n], -39.0, fade_in=0.4, fade_out=0.8, highpass=45, lowpass=5000)
        mix += bed
    for i, t in enumerate(times):
        src, _ = dsp.load_any(hits[i % len(hits)])
        seg = src[:, : min(src.shape[1], int(0.75 * dsp.SR))]
        seg = finalize(seg, hit_db + (1.0 if i % 4 == 0 else 0.0), fade_in=0.002, fade_out=0.25,
                       highpass=55, lowpass=lowpass, limit=True)
        mix = dsp.place(mix, seg, t)
    mix = dsp.fade(mix[:, :n], 0.02, 0.45)
    mix = dsp.normalize_rms(mix, target_db)
    return dsp.peak_ceiling(mix, 0.92)


def sparse_bells(out_len: float, room: np.ndarray, bells: list[Path], times: list[float],
                 target_db: float, bell_db: float) -> np.ndarray:
    n = int(out_len * dsp.SR)
    base = dsp.loop_to_length(room, n)[:, :n]
    base = finalize(base, -38.0, fade_in=0.8, fade_out=1.2, highpass=60, lowpass=8500)
    mix = base.copy()
    for i, t in enumerate(times):
        src, _ = dsp.load_any(bells[i % len(bells)])
        seg = src[:, : min(src.shape[1], int(2.5 * dsp.SR))]
        # długi, spokojny rezonans; nie robimy melodii, tylko pojedyncze oddechy przestrzeni
        seg = finalize(seg, bell_db + (0.8 if i == 0 else 0.0), fade_in=0.005, fade_out=1.8,
                       highpass=80, lowpass=10000, limit=True)
        mix = dsp.place(mix, seg, t)
    mix = dsp.fade(mix[:, :n], 0.15, 1.2)
    mix = dsp.normalize_rms(mix, target_db)
    return dsp.peak_ceiling(mix, 0.92)


def build_manifest() -> dict:
    swords = load_scout_manifest("freesound_battle-swords")
    quiet = load_scout_manifest("freesound_quiet-room-tone")
    wind_item = swords["03-667115-mongolian-film-windblown-steppe1-wav.mp3"]
    cellar_item = quiet["01-637805-room-tone-quiet-cellar-with-distant-noises-flac.mp3"]
    bedroom_item = quiet["02-724113-240219-002-tr1-2-ambient-roomtone-bedroom-open-w.mp3"]
    calm_item = quiet["04-739159-calm-room-tone-india.mp3"]

    wind = REPO / wind_item["file"]
    cellar = REPO / cellar_item["file"]
    bedroom = REPO / bedroom_item["file"]
    calm_room = REPO / calm_item["file"]

    metal_pack = "opengameart-100-cc0-metal-and-wood-sfx"
    impact_pack = "kenney-impact-sounds"
    swamp_pack = "opengameart-swamp-environment-audio"
    sci_pack = "kenney-sci-fi-sounds"
    loops_pack = "opengameart-30-cc0-sfx-loops"
    scifi50_pack = "opengameart-50-cc0-sci-fi-sfx"
    sfx100_pack = "opengameart-100-cc0-sfx"

    # 1. STEP — ta sama realna przestrzeń, ale wyraźnie ciszej niż g034 i bez okna s.3.
    step_traits = ["otwarta przestrzeń", "wiatr", "suchy teren", "równina", "brak muzyki"]
    step_bad = ["wnętrze", "miasto", "gęsty las", "podziemia", "muzyka"]
    step_src = scout_source(wind_item, "okna dobrane po g034: cicho, bez muzyki, poziom tła niższy niż poprzednio")
    step = [
        bg_candidate("s.1", "bardzo cichy wiatr równiny", "bg_steppe_quiet_wind_01.mp3", "steppe_quiet_wind_01",
                     "step-rownina", "step / otwarta równina", "subtelny wiatr i pusta przestrzeń, bez melodii i bez nagłych zdarzeń",
                     finalize(load_cut(wind, 16, 8.0), -38.0, fade_in=0.5, fade_out=1.0, highpass=55, lowpass=7800),
                     step_src, -38.0, step_traits, step_bad),
        bg_candidate("s.2", "suchy płaski wiatr", "bg_steppe_dry_wind_01.mp3", "steppe_dry_wind_01",
                     "step-rownina", "step / sucha równina", "trochę bardziej ziarnisty szum traw, nadal niski poziom i bez muzyki",
                     finalize(load_cut(wind, 44, 8.0), -39.0, fade_in=0.5, fade_out=1.0, highpass=65, lowpass=7200),
                     step_src, -39.0, step_traits, step_bad),
        bg_candidate("s.3", "daleki wiatr pustego traktu", "bg_steppe_distant_wind_01.mp3", "steppe_distant_wind_01",
                     "step-rownina", "step / pusty trakt", "najcichszy wariant: daleki, stabilny wiatr pod samotną równinę; bez warstwy muzycznej",
                     finalize(load_cut(wind, 88, 8.0), -40.0, fade_in=0.7, fade_out=1.2, highpass=70, lowpass=6500),
                     step_src, -40.0, step_traits, step_bad),
    ]

    # 2. KUŹNIA — miarowe kucie, zgodnie z korektą właściciela.
    hammer1 = ATOM / "packs" / metal_pack / "audio/hammer-01.m4a"
    hammer3 = ATOM / "packs" / metal_pack / "audio/hammer-03.m4a"
    metal_hit = ATOM / "packs" / metal_pack / "audio/metal-hit-02.m4a"
    mining = ATOM / "packs" / impact_pack / "audio/impact-mining-000.m4a"
    metal_heavy = ATOM / "packs" / impact_pack / "audio/impact-metal-heavy-001.m4a"
    forge_src1 = atom_source(metal_pack, "miarowy montaż z pojedynczych uderzeń młota/metal-hit", ["hammer-01.m4a", "hammer-03.m4a", "metal-hit-02.m4a"])
    forge_src2 = atom_source(impact_pack, "miarowy montaż z uderzeń mining/metal heavy", ["impact-mining-000.m4a", "impact-metal-heavy-001.m4a"])
    forge_traits = ["kuźnia", "warsztat", "miarowe kucie", "młot", "metal", "rytm"]
    forge_bad = ["losowy hałas", "muzyka", "las", "morze", "cisza"]
    forge = [
        bg_candidate("k.1", "miarowy młot na kowadle", "bg_forge_even_hammer_01.mp3", "forge_even_hammer_01",
                     "kuznia-warsztat", "kuźnia / kucie", "równy rytm młota co około sekundę; nie przypadkowe trzaski metalu",
                     rhythmic_forge(8.0, [hammer1, metal_hit], load_cut(cellar, 0, 2.0), [0.35,1.15,1.95,2.75,3.55,4.35,5.15,5.95,6.75], -31.0, -23.0),
                     mixed_source("Miarowy forge mix — metal/wood CC0 + cellar room tone", "hammer na kowadle z lekkim pomieszczeniem", [forge_src1, scout_source(cellar_item, "lekki room tone jako wnętrze")]),
                     -31.0, forge_traits, forge_bad),
        bg_candidate("k.2", "cięższe kucie warsztatowe", "bg_forge_heavy_hammer_01.mp3", "forge_heavy_hammer_01",
                     "kuznia-warsztat", "kuźnia / ciężki młot", "wolniejsze, cięższe uderzenia; rytm pracy kowala zamiast chaotycznych klanków",
                     rhythmic_forge(8.0, [mining, metal_heavy], load_cut(cellar, 3, 2.0), [0.45,1.45,2.45,3.45,4.45,5.45,6.45], -30.5, -22.0, lowpass=9000),
                     mixed_source("Miarowy forge mix — Kenney impacts CC0 + cellar room tone", "cięższe miarowe uderzenia", [forge_src2, scout_source(cellar_item, "lekki room tone jako wnętrze")]),
                     -30.5, forge_traits, forge_bad),
        bg_candidate("k.3", "szybsze drobne kucie", "bg_forge_quick_hammer_01.mp3", "forge_quick_hammer_01",
                     "kuznia-warsztat", "kuźnia / drobne kucie", "bardziej pracowity, ale nadal regularny wzór: dwa krótsze uderzenia i przerwa",
                     rhythmic_forge(8.0, [hammer3, hammer1, metal_hit], load_cut(cellar, 5, 2.0), [0.32,0.82,1.62,2.12,2.92,3.42,4.22,4.72,5.52,6.02,6.82], -31.5, -24.0),
                     mixed_source("Miarowy forge mix — metal/wood CC0 + cellar room tone", "szybsze, powtarzalne kucie", [forge_src1, scout_source(cellar_item, "lekki room tone jako wnętrze")]),
                     -31.5, forge_traits, forge_bad),
    ]

    # 3. NOC — realne owady/atmosfera, nie dzień i nie ptaki dzienne.
    cr1 = ATOM / "packs" / swamp_pack / "audio/cricket-1.m4a"
    cr2 = ATOM / "packs" / swamp_pack / "audio/cricket-2.m4a"
    cic = ATOM / "packs" / swamp_pack / "audio/cicada-1.m4a"
    atm = ATOM / "packs" / swamp_pack / "audio/atmosphere-1.m4a"
    night_src = atom_source(swamp_pack, "nocne owady/atmosfera z paczki środowiskowej; użyte bez chlupotu wody", ["cricket-1.m4a", "cricket-2.m4a", "cicada-1.m4a", "atmosphere-1.m4a"])
    night_traits = ["noc", "księżyc", "świerszcze", "owady", "ciemność", "bez dnia"]
    night_bad = ["dzień", "ptaki dzienne", "miasto", "wnętrze", "burza"]
    def layer_night(layers: list[tuple[Path,float,float,float]], target: float) -> np.ndarray:
        n=int(8*dsp.SR); mix=np.zeros((2,n))
        for path, start, db, lp in layers:
            seg=load_cut(path,start,8.0)
            seg=finalize(seg, db, fade_in=0.5, fade_out=1.2, highpass=120, lowpass=lp)
            mix += seg
        mix=dsp.fade(mix,0.5,1.1)
        mix=dsp.normalize_rms(mix,target)
        return dsp.peak_ceiling(mix,0.92)
    night = [
        bg_candidate("n.1", "księżycowe świerszcze", "bg_night_crickets_moon_01.mp3", "night_crickets_moon_01",
                     "noc-ksiezyc", "noc / księżycowa polana", "stabilny nocny dywan świerszczy, bez dziennych ptaków i bez muzyki",
                     layer_night([(cr1,0,-32,9000),(atm,0,-39,5000)], -32.5), night_src, -32.5, night_traits, night_bad),
        bg_candidate("n.2", "ciemna noc z owadami", "bg_night_insects_dark_01.mp3", "night_insects_dark_01",
                     "noc-ksiezyc", "noc / ciemny plener", "niższy, ciemniejszy wariant: mniej jasnych cykad, więcej pustej nocy",
                     layer_night([(cr2,0,-33,7600),(atm,2,-38,4200)], -33.0), night_src, -33.0, night_traits, night_bad),
        bg_candidate("n.3", "żywsza noc pod księżycem", "bg_night_cicada_moon_01.mp3", "night_cicada_moon_01",
                     "noc-ksiezyc", "noc / żywszy plener", "bardziej żywy nocny krajobraz owadów; nadal bez ptaków dziennych i bez wody jako motywu",
                     layer_night([(cic,0,-34,8500),(cr1,1,-35,8500),(atm,3,-40,4500)], -32.0), night_src, -32.0, night_traits, night_bad),
    ]

    # 4. LABORATORIUM — technologiczne tło, terminale, aparatura.
    comp0 = ATOM / "packs" / sci_pack / "audio/computer-noise-000.m4a"
    comp3 = ATOM / "packs" / sci_pack / "audio/computer-noise-003.m4a"
    machine4 = ATOM / "packs" / loops_pack / "audio/machine-04.m4a"
    loop_machine = ATOM / "packs" / scifi50_pack / "audio/loop-machine-01.m4a"
    lab_src1 = atom_source(sci_pack, "komputerowe szumy i krótkie pikania jako aparatura", ["computer-noise-000.m4a", "computer-noise-003.m4a"])
    lab_src2 = atom_source(loops_pack, "maszynowy loop pod laboratorium/technikę", ["machine-04.m4a"])
    lab_src3 = atom_source(scifi50_pack, "sci-fi machine loop pod terminale", ["loop-machine-01.m4a"])
    lab_traits = ["laboratorium", "technika", "aparatura", "komputer", "maszyna", "terminal"]
    lab_bad = ["las", "świątynia", "wieś", "ogień", "woda"]
    def layer_lab(srcs: list[tuple[Path,float,float,float,float]], target: float) -> np.ndarray:
        n=int(8*dsp.SR); mix=np.zeros((2,n))
        for path, start, db, hp, lp in srcs:
            seg=load_cut(path,start,8.0)
            seg=finalize(seg, db, fade_in=0.15, fade_out=0.7, highpass=hp, lowpass=lp)
            mix += seg
        mix=dsp.fade(mix,0.1,0.7)
        mix=dsp.normalize_rms(mix,target)
        return dsp.peak_ceiling(mix,0.92)
    lab = [
        bg_candidate("l.1", "cichy terminal i aparatura", "bg_lab_terminal_hum_01.mp3", "lab_terminal_hum_01",
                     "laboratorium-technika", "laboratorium / terminale", "cichy elektroniczny hum i drobne komputerowe impulsy; nie muzyka",
                     layer_lab([(comp0,0,-32,70,11000),(loop_machine,0,-38,80,7000)], -31.5),
                     mixed_source("Laboratorium mix — Kenney computer + OGA sci-fi machine", "terminal i aparatura", [lab_src1, lab_src3]), -31.5, lab_traits, lab_bad),
        bg_candidate("l.2", "maszyna badawcza w tle", "bg_lab_machine_pulse_01.mp3", "lab_machine_pulse_01",
                     "laboratorium-technika", "laboratorium / maszyna", "równiejszy puls aparatury, dobry pod techniczną salę lub kapsułę",
                     layer_lab([(machine4,0,-31,80,9000),(comp3,0,-37,90,12000)], -31.0),
                     mixed_source("Laboratorium mix — OGA machine + Kenney computer", "maszyna badawcza", [lab_src2, lab_src1]), -31.0, lab_traits, lab_bad),
        bg_candidate("l.3", "zimna sala techniczna", "bg_lab_cold_equipment_01.mp3", "lab_cold_equipment_01",
                     "laboratorium-technika", "laboratorium / zimna aparatura", "bardziej chłodny, stały szum urządzeń bez wyraźnej melodii; SF/technika",
                     layer_lab([(loop_machine,0,-31.5,75,8500),(comp0,2,-40,120,10500)], -32.0),
                     mixed_source("Laboratorium mix — OGA sci-fi machine + Kenney computer", "zimna aparatura", [lab_src3, lab_src1]), -32.0, lab_traits, lab_bad),
    ]

    # 5. ŚWIĄTYNIA — cisza przestrzeni + pojedynczy rezonans, bez muzycznej melodii.
    bell = ATOM / "packs" / sfx100_pack / "audio/bell-01.m4a"
    gong = ATOM / "packs" / sfx100_pack / "audio/gong-01.m4a"
    heavy_bell = ATOM / "packs" / impact_pack / "audio/impact-bell-heavy-000.m4a"
    bell_src = atom_source(sfx100_pack, "pojedyncze dzwony/gong jako rezonans sakralny", ["bell-01.m4a", "gong-01.m4a"])
    bell_src2 = atom_source(impact_pack, "ciężki dzwon jako pojedynczy rezonans sanktuarium", ["impact-bell-heavy-000.m4a"])
    temple_traits = ["świątynia", "sanktuarium", "dzwon", "rezonans", "cisza", "kamień"]
    temple_bad = ["miasto", "kuźnia", "laboratorium", "las dzienny", "muzyka"]
    temple = [
        bg_candidate("t.1", "cichy dzwon w sanktuarium", "bg_temple_soft_bell_01.mp3", "temple_soft_bell_01",
                     "swiatynia-sanktuarium", "świątynia / spokojne sanktuarium", "cichy room tone i pojedyncze oddechy dzwonu; przestrzeń sakralna bez melodii",
                     sparse_bells(8.0, load_cut(calm_room,0,4.0), [bell], [0.8,4.7], -33.0, -23.5),
                     mixed_source("Temple mix — room tone + OGA bell", "spokojne sanktuarium", [scout_source(calm_item, "cichy room tone"), bell_src]), -33.0, temple_traits, temple_bad),
        bg_candidate("t.2", "kamienny rezonans gongu", "bg_temple_stone_gong_01.mp3", "temple_stone_gong_01",
                     "swiatynia-sanktuarium", "świątynia / kamienny rezonans", "ciemniejszy wariant: głęboki gong i długa cisza kamiennej przestrzeni",
                     sparse_bells(8.0, load_cut(cellar,0,4.0), [gong], [1.0,5.2], -32.5, -22.5),
                     mixed_source("Temple mix — cellar tone + OGA gong", "kamienne sanktuarium", [scout_source(cellar_item, "cichy room tone"), bell_src]), -32.5, temple_traits, temple_bad),
        bg_candidate("t.3", "oddalony ciężki dzwon", "bg_temple_heavy_bell_01.mp3", "temple_heavy_bell_01",
                     "swiatynia-sanktuarium", "świątynia / oddalony dzwon", "najbardziej uroczysty wariant: ciężki dzwon z dużymi odstępami, bez ciągłej muzyki",
                     sparse_bells(8.0, load_cut(bedroom,0,4.0), [heavy_bell], [0.7,5.0], -32.0, -22.0),
                     mixed_source("Temple mix — room tone + Kenney heavy bell", "uroczysty oddalony dzwon", [scout_source(bedroom_item, "cichy room tone"), bell_src2]), -32.0, temple_traits, temple_bad),
    ]

    return {
        "id": "g035",
        "created": "2026-09-27",
        "note": "PAKIET 5 zestawów po g034: corrected `background:step-rownina` (ciszej, bez muzyki), corrected `background:kuznia-warsztat` (miarowe kucie), oraz duże braki `background:noc-ksiezyc`, `background:laboratorium-technika`, `background:swiatynia-sanktuarium`. Anchory jedynego braku: step 10/230/396/492/616; kuźnia 16/113/168/285/355/487; noc 42/78/171/281/478/543/600; laboratorium 47/93/100/275/345/545; świątynia 121/273/308/352/435/440/480/565.",
        "entries": [
            {"slug": "tlo-step", "kind": "backgrounds", "role": "jedyny klocek typu tła `step-rownina` (19 fabuł) — poprawka po g034: dużo ciszej, bez muzyki", "candidates": step},
            {"slug": "tlo-kuznia", "kind": "backgrounds", "role": "jedyny klocek typu tła `kuznia-warsztat` (19 fabuł) — poprawka po g034: miarowe kucie w kuźni", "candidates": forge},
            {"slug": "tlo-noc", "kind": "backgrounds", "role": "jedyny klocek typu tła `noc-ksiezyc` (21 fabuł)", "candidates": night},
            {"slug": "tlo-laboratorium", "kind": "backgrounds", "role": "jedyny klocek typu tła `laboratorium-technika` (21 fabuł)", "candidates": lab},
            {"slug": "tlo-swiatynia", "kind": "backgrounds", "role": "jedyny klocek typu tła `swiatynia-sanktuarium` (21 fabuł)", "candidates": temple},
        ],
        "verdicts": {},
    }


def main() -> None:
    ensure_sources()
    clean_gate()
    manifest = build_manifest()
    (GATE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (GATE / "verdicts.json").write_text(json.dumps({"gate": "g035", "choices": {}, "notes": {}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"zbudowano {GATE} ({sum(len(e['candidates']) for e in manifest['entries'])} kandydatów)")


if __name__ == "__main__":
    main()
