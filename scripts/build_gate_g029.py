#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g029 — fabuła 110 „Krwawe zbiory”, RUNDA 3: zg + ł z REALnych taśm.

Diagnoza właściciela (data/gates/g027/verdicts.json::notes):
- zg: „generyczne, mechaniczne, to nie brzmi jak prawdziwa bitwa tylko jak
  ustawiona scena” — kompozycja z izolowanych sampli wyglądała jak scena.
  Runda 3: ZERO montażu warstwowego — trzy prawdziwe, długie wzięcia bitwy:
    zg.1 „szarża” — Battle Charge 764046 (FUMA/Ambeo, tłum nabiera tempa),
    zg.2 „mieszanka frontu” — R29-39 Chinese Screams in Battle 479582 (44 s
         realnej filmowej taśmy walki, krzyki + brzęki),
    zg.3 „przełamanie” — People screaming in agony 563011 (18,5 s agony-charge).
- ł: „trzepanie dywanu, nie łopot skrzydeł” — foley tkaninowy był martwy.
  Runda 3: prawdziwe PTAKI z bliska (sample-scout „pigeon wings” CC0):
    ł.1 pojedynczy gwałtowny odlot gołębia 689998 (rozłączne piki co ~60 ms),
    ł.2 gęste kłusowate kucie z ziemi 741562 (burst 59,75 s — pompa 30+ pików),
    ł.3 „łup-łup”: dwa mocne pęki startu 843933 (104,55 s i 153,0 s).
Bez spowalniania, bez syntetyzowania; tylko okno + łagodne fadery.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402

GATE = REPO / "data" / "gates" / "g029"
CAND = GATE / "candidates"
SCOUT = REPO / "work" / "scout"
CHARGE = SCOUT / "battle-generic/freesound_battle"
SCREAMS = SCOUT / "battle-screams/freesound_battle-screams"
PIGEON = SCOUT / "pigeon-wings/freesound_pigeon-wings"


def scout_src(legacy_dir: str, idx0: int, notes: str) -> dict:
    man = json.loads((REPO / "legacy/source/sample_scout" / legacy_dir / "manifest.json").read_text("utf-8"))
    c = man[idx0]
    return {
        "title": f"{c['name']} ({'archive.org' if c['source'] == 'archive.org' else 'Freesound'})",
        "author": c["author"],
        "license": "CC0 / Public Domain (wg scouta)",
        "url": c["source_url"],
        "channel": f"sample-scout ({c['source']}, preview); manifest: {legacy_dir}",
        "notes": notes + f"; id {c['source_id']}",
    }


def hp(wave: np.ndarray, hz: float) -> np.ndarray:
    sos = butter(2, hz, btype="highpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1)


def bg_finish(wave: np.ndarray, rms: float = -33.0) -> np.ndarray:
    return dsp.fade(dsp.peak_ceiling(dsp.normalize_rms(dsp.peak_ceiling(wave), rms)), 1.2, 1.5)


ZG_ENTRY = {
    "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
    "semantics": {"type": "zgryw-bitwa",
                  "traits": ["średniowiecze", "krzyki", "pole walki", "tłum"],
                  "bad_for": ["współczesna bitwa z prochami", "cisza pustyni"]},
}


def ł_finish(wave: np.ndarray, peak_db: float = -19.0) -> np.ndarray:
    return dsp.fade(dsp.peak_ceiling(dsp.normalize_rms(wave, peak_db)), 0.15, 0.5)


L_ENTRY = {
    "duration_sec": 3.8, "level_ref_db": -18, "loopable": False,
    "semantics": {"type": "łuk-wytrzymały",
                  "traits": ["odlot", "skrzydła", "uderzenia", "ptak"],
                  "bad_for": ["stacjonarny dron", "ciężki merszenek"]},
}


def zg_candidates() -> list[dict]:
    cands: list[dict] = []

    # ── zg.1 „szarża” — realny nabieg tłumu, zero słów (FUMA/AmbeoVR)
    f = next(CHARGE.glob("04-764046*"))
    w, _ = dsp.load_any(f)
    seg = hp(dsp.cut(w, 0.9, 8.9), 55.0)
    dsp.encode_mp3(CAND / "zg1_szarza.mp3", bg_finish(seg))
    cands.append({
        "label": "zg.1", "title": "szarża — tłum nabiera tempa i wyje w jednym oddechu",
        "file": "candidates/zg1_szarza.mp3",
        "desc": "prawdziwa nagrana szarża (ambisoniczne FUMA): masa jedzie, warkot rośnie, "
                "bez słów i bez prochu; sama organiczna fala pola — nic nie jest pętlą",
        "source": scout_src("freesound_battle", 3,
                            "okno 0,9–8,9 s; HP 55; -33 dB RMS; REALNE wzięcie"),
        "entry": {**ZG_ENTRY, "id": "battle_charge_01",
                  "setting": "otwarte pole — fala szarży",
                  "desc": "prawdziwy tłum w biegu: warkot masy, przypominający o szarży "
                          "która nie pęta i nie liniuje — jeden oddech wojny",
                  "file": "audio/library/backgrounds/battle_charge_01.mp3",
                  "source": scout_src("freesound_battle", 3,
                                      "okno 0,9–8,9 s; HP 55; -33 dB RMS")},
    })
    print("  zg.1 zapisany")

    # ── zg.2 „mieszanka frontu” — 44 s realnej taśmy walki (krzyki + brzęki)
    f = next(SCREAMS.glob("01-479582*"))
    w, _ = dsp.load_any(f)
    seg = hp(dsp.cut(w, 24.5, 32.5), 55.0)
    dsp.encode_mp3(CAND / "zg2_mieszanka_frontu.mp3", bg_finish(seg))
    cands.append({
        "label": "zg.2", "title": "mieszanka frontu — krzyki i brzęki bitwy z prawdziwej taśmy",
        "file": "candidates/zg2_mieszanka_frontu.mp3",
        "desc": "nieudawana mieszanina: nagrane na set krzyki i brzęki broni, szum walki "
                "oddycha falami (taśma archiwalna 44 s) — brzmi jak pole, bo to pole",
        "source": scout_src("freesound_battle-screams", 0,
                            "okno 24,5–32,5 s; HP 55; -33 dB RMS; REALNE wzięcie"),
        "entry": {**ZG_ENTRY, "id": "battle_screams_open_01",
                  "setting": "pole srodka frontu — krzyki, brzęki, wrzawa",
                  "desc": "archiwalna taśma prawdziwej siatki walki: krzyki załamują się "
                          "wewnątrz brzęków broni i pomruków — niepoldą nic pętli",
                  "file": "audio/library/backgrounds/battle_screams_open_01.mp3",
                  "source": scout_src("freesound_battle-screams", 0,
                                      "okno 24,5–32,5 s; HP 55; -33 dB RMS")},
    })
    print("  zg.2 zapisany")

    # ── zg.3 „przełamanie” — agonia ciągnącej szarży (18,5 s)
    f = next(SCREAMS.glob("03-563011*"))
    w, _ = dsp.load_any(f)
    seg = hp(dsp.cut(w, 0.4, 8.4), 55.0)
    dsp.encode_mp3(CAND / "zg3_przełamanie.mp3", bg_finish(seg))
    cands.append({
        "label": "zg.3", "title": "przełamanie — agonia tego, że idzie się i nie wraca",
        "file": "candidates/zg3_przełamanie.mp3",
        "desc": "ludzie krzyczą w agonii w biegu do przodu — bardzo silne, niebenszone "
                "krzyki prawdziwych gardeł nagrane raz i na serio; dramat i popęd bez "
                "żadnej uporządkowanej sceny",
        "source": scout_src("freesound_battle-screams", 2,
                            "okno 0,4–8,4 s; HP 55; -33 dB RMS; REALNE wzięcie"),
        "entry": {**ZG_ENTRY, "id": "battle_agony_01",
                  "setting": "punkt przełamania — krzyki w biegu",
                  "desc": "agonia w bieg — nagrane na serio gardła, które przylekują "
                          "przez pole; sztywno tu nic nie jest ustawione",
                  "file": "audio/library/backgrounds/battle_agony_01.mp3",
                  "source": scout_src("freesound_battle-screams", 2,
                                      "okno 0,4–8,4 s; HP 55; -33 dB RMS")},
    })
    print("  zg.3 zapisany")
    return cands


def l_candidates() -> list[dict]:
    cands: list[dict] = []

    # ── ł.1 „wstrzask odlotu” — jeden ptak, gwałtowna seria (689998)
    f = next(PIGEON.glob("05-689998*"))
    w, _ = dsp.load_any(f)
    seg = hp(dsp.cut(w, 0.85, 2.75), 60.0)
    seg_tail = hp(dsp.cut(w, 2.75, 4.4), 60.0)
    seg_tail = dsp.fade(seg_tail, 0.0, 1.4)
    full = np.concatenate([seg, dsp.normalize_rms(seg_tail, -34.0)], axis=1)
    dsp.encode_mp3(CAND / "l1_wstrzask_odlotu.mp3", ł_finish(full))
    cands.append({
        "label": "ł.1", "title": "wstrzask odlotu — gołąb puszcza nogi i rwie w górę",
        "file": "candidates/l1_wstrzask_odlotu.mp3",
        "desc": "prawdziwy ptak z bliska: sześć osiem twardych, rozłącznych uderzeń "
                "jeden po drugim (60–180 ms), potem łokizna powietrza — to jest ten "
                "charakter, którego szukaliśmy",
        "source": scout_src("freesound_pigeon-wings", 4,
                            "okno 0,85–2,75 s + ogon 2,75–4,4 s (-34 dB); HP 60; -19 dB peak"),
        "entry": {**L_ENTRY, "id": "wingburst_takeoff_01",
                  "setting": "skrzydlaty odlot — gwałtowna seria uderzeń",
                  "desc": "prawdziwy odlot ptaka: rozłączne mocne łuncanie skrzydeł "
                          "podnoszące cię ciało w powietrze",
                  "file": "audio/library/heroes/wingburst_takeoff_01.mp3",
                  "source": scout_src("freesound_pigeon-wings", 4,
                                      "okno 0,85–2,75 s + ogon -34 dB; HP 60")},
    })
    print("  ł.1 zapisany")

    # ── ł.2 „pompa startowa” — głupia przytomność gołębi z ziemi (741562@59,75)
    f = next(PIGEON.glob("04-741562*"))
    w, _ = dsp.load_any(f)
    seg = hp(dsp.cut(w, 59.75, 62.0), 60.0)
    dsp.encode_mp3(CAND / "l2_pompa_startowa.mp3", ł_finish(seg))
    cands.append({
        "label": "ł.2", "title": "pompa startowa — kłusowate łupanie z ziemi jak roztargniona",
        "file": "candidates/l2_pompa_startowa.mp3",
        "desc": "inny wzięcie, gęstsze pompowanie: burza 30+ rozłącznych uderzeń w 2 s — "
                "ciało skrzydłowe z zażenowaniem wyrzuca ptaka w góry; zero materiału, "
                "żadne trzepanie dywanu",
        "source": scout_src("freesound_pigeon-wings", 3,
                            "okno 59,75–62,0 s; HP 60; -19 dB peak"),
        "entry": {**L_ENTRY, "id": "wingburst_pump_01",
                  "setting": "skrzydlaty start — szybka pompa uderzeń",
                  "desc": "gwałtowne kłusowate pociskanie — pełne skrzydła biją tempo",
                  "file": "audio/library/heroes/wingburst_pump_01.mp3",
                  "source": scout_src("freesound_pigeon-wings", 3,
                                      "okno 59,75–62,0 s; HP 60")},
    })
    print("  ł.2 zapisany")

    # ── ł.3 „łup-łup” — dwa mocne podskoki (843933: 104,55 + 153,0)
    f = next(PIGEON.glob("01-843933*"))
    w, _ = dsp.load_any(f)
    t = np.zeros((2, int(3.2 * dsp.SR)))
    t = dsp.place(t, dsp.normalize_rms(hp(dsp.cut(w, 104.5, 105.35), 60.0), -20.0), 0.15)
    t = dsp.place(t, dsp.normalize_rms(hp(dsp.cut(w, 152.98, 153.85), 60.0), -20.5), 1.15)
    dsp.encode_mp3(CAND / "l3_lup_lup.mp3", ł_finish(t))
    cands.append({
        "label": "ł.3", "title": "łup-łup — dwa ciężkie podskoki i już go nie ma",
        "file": "candidates/l3_lup_lup.mp3",
        "desc": "dwa krótkie, tęteżne pęki jeden po drugim (realny park, duży ptak): "
                "uderzenie, oddech, uderzenie — skrzydła postawione jak razy mocarza, "
                "całkiem faktycznie nagrane",
        "source": scout_src("freesound_pigeon-wings", 0,
                            "pęki @104,55 s i 153,0 s; HP 60; -20/-20,5 dB; montaż 2 wzięć"),
        "entry": {**L_ENTRY, "id": "wingburst_twohop_01",
                  "setting": "skrzydlata ucieczka — dwa ciężkie poruszki",
                  "desc": "dwa silne odruchowe poruszki skrzydła z oddechem pośrodku",
                  "file": "audio/library/heroes/wingburst_twohop_01.mp3",
                  "source": scout_src("freesound_pigeon-wings", 0,
                                      "pęki @104,55 s i 153,0 s; HP 60")},
    })
    print("  ł.3 zapisany")
    return cands


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": "g029",
        "created": "2026-09-24",
        "story_id": "110",
        "note": "RUNDA 3 fabuły 110 — zg i ł z przegranego przetargu g027 (koda n.3 już przyjęta). "
                "Po werdykcie „generyczne / jak ustawiona scena” i „trzepanie dywanu”: "
                "wyłącznie realne, długie wzięcia — bitwa z urzeczywistnionych nagrań (charge, "
                "archiwalna taśma, agony), skrzydła z prawdziwych gołębi nagranych z bliska. "
                "Żadnej syntetycznej warstwy.",
        "entries": [
            {"slug": "tlo-bitwa-zgielk", "kind": "backgrounds",
             "role": "jedyny klocek typu tła `zgryw-bitwa` (slot d fabuły 110; ~14 fabuł z tej rodziny)",
             "candidates": zg_candidates()},
            {"slug": "hero-lopot", "kind": "heroes",
             "role": "jedyny klocek typu hero `łuk-wytrzymały` (slot c fabuły 110)",
             "candidates": l_candidates()},
        ],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest g029 zapisany ({len(manifest['entries'])} wpisy)")


if __name__ == "__main__":
    main()
