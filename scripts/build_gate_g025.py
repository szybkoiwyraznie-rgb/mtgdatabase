#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g025 — fabuła 110 „Serra's Embrace” (losowanie 2026-09-24, ziarno 20260924).

Trzy braki z resolvera (typ bez klocka), trzy wpisy, trzech kandydatów na wpis:
  1) tło `bitwa-zgielk`     — cichnące pole bitwy w złotej godzinie (zg.1–zg.3),
  2) hero `lopot-skrzydel`  — zstąpienie anioła: łopot wielkich skrzydeł (ł.1–ł.3),
  3) koda `nadzieja-ukojenie` — gest łaski, podniosły końcówkowy (n.1–n.3).

Materiał:
  - Sample Scout (Freesound, CC0): fireworks-warzone (odległe dudnienie),
    R29-39 Chinese Screams in Battle (krzyki w boju), łopoty ptaków
    (framixo FlapWings / Matteo_Fusi / Clusman);
  - atomcut (CC0): miecze (20 SFX), męskie okrzyki (haeldb), młoty — do
    zmontowanego wariantu zg.3 (technika g007: pitch-down wrzasków).
Zasada etykiet: prefiksy unikalne w skali bramki (zg/ł/n).
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
import coda_synth  # noqa: E402
from build_gate_g003 import to_roar, soft_limit  # noqa: E402

GATE = REPO / "data" / "gates" / "g025"
CAND = GATE / "candidates"
SCOUT = REPO / "work" / "scout"

FS = {
    "warzone": "freesound.org/people/BenjaminNelan/sounds/",  # uzupełniane z manifestów scouta poniżej
}


def _src(manifest_dir: str, idx0: int, notes: str) -> dict:
    """Proweniencja kandydata z manifestu Sample Scouta (wpis nr idx0+1)."""
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


def lp(wave: np.ndarray, hz: float, order: int = 3) -> np.ndarray:
    sos = butter(order, min(hz, dsp.SR * 0.45), btype="lowpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1)


def hp(wave: np.ndarray, hz: float, order: int = 2) -> np.ndarray:
    sos = butter(order, hz, btype="highpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1)


def steady_bed(seg: np.ndarray, length: float = 8.0, fade_edge: float = 1.5) -> np.ndarray:
    """Bed 8 s: pętla fizyczna wyjściowego materiału gdy krótki + miękkie krawędzie."""
    out = dsp.loop_to_length(seg, int(length * dsp.SR))
    return dsp.fade(out, fade_edge, fade_edge)


# ---------------------------------------------------------------- tło: bitwa-zgielk
def bg_candidates() -> list[dict]:
    cands: list[dict] = []

    # --- zg.1: odległe dudnienie oblężnicze (warzone-3 w najspokojniejszym oknie)
    w, _ = dsp.load_any(SCOUT / "battle/freesound_battle-ambience/03-694371-fireworks-warzone-3.mp3")
    seg = dsp.cut(w, 6.0, 14.0)                     # równy, głęboki gwar dalekich wybuchów
    seg = lp(seg, 900.0)                            # strącenie jasności = oddalenie
    seg = dsp.normalize_rms(seg, -32.0)
    dsp.encode_mp3(CAND / "zg1_odlegle_dudnienie.mp3", steady_bed(seg))
    cands.append({
        "label": "zg.1", "title": "dudnienie oblężnicze w oddali",
        "file": "candidates/zg1_odlegle_dudnienie.mp3",
        "desc": "samo głębokie dudnienie zza burz piasku — 63% energii < 250 Hz, "
                "równa masa bez pierwszoplanowych krzyków; cichnąca bitwa słyszana z dala",
        "source": _src("battle/freesound_battle-ambience", 2,
                       "okno 6–14 s; filtr dolnoprzepustowy 900 Hz; poziom -32 dB"),
        "entry": {
            "id": "battle_distant_01",
            "setting": "pole bitwy / oblężenie — oddalenie",
            "desc": "głębokie dudnienie dalekiej bitwy: masa niskich częstotliwości, "
                    "brak bliskich zdarzeń — zgiełk słyszany jak przez kurz zmierzchu",
            "file": "audio/library/backgrounds/battle_distant_01.mp3",
            "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
            "semantics": {"type": "bitwa-zgielk",
                          "traits": ["bitwa", "zgiełk", "oddalona", "dudnienie"],
                          "bad_for": ["spokojna komnata", "sielanka", "kameralna scena"]},
            "source": _src("battle/freesound_battle-ambience", 2,
                           "okno 6–14 s; LP 900 Hz; -32 dB"),
        },
    })
    print("  zg.1 zapisany")

    # --- zg.2: ludzki zgiełk boju w oddali (Chinese Screams przyciemnione + dudnienie)
    y, _ = dsp.load_any(SCOUT / "battle/freesound_battle-ambience/04-479582-r29-39-chinese-screams-in-battle-wav.mp3")
    y = dsp.cut(y, 8.0, 16.0)                       # seria krzyków bitewnych (stabilny fragment)
    y = lp(y, 800.0)                                # pochłania zrozumiałość słów = tylko faktura
    y = dsp.normalize_rms(y, -36.0)
    base, _ = dsp.load_any(SCOUT / "battle/freesound_battle-ambience/03-694371-fireworks-warzone-3.mp3")
    base = lp(dsp.cut(base, 20.0, 28.0), 800.0)
    base = dsp.normalize_rms(base, -33.0)
    mix = dsp.peak_ceiling(base * 1.0 + y)
    dsp.encode_mp3(CAND / "zg2_krzyki_w_oddali.mp3", steady_bed(mix))
    cands.append({
        "label": "zg.2", "title": "wrzawa walczących jak przez mgłę",
        "file": "candidates/zg2_krzyki_w_oddali.mp3",
        "desc": "ludzkie krzyki boju zamienione w oddaloną fakturę (filtr 800 Hz — "
                "słów nie da się rozpoznać) nad równym dudnieniem; ludzie + masa starcia",
        "source": _src("battle/freesound_battle-ambience", 3,
                       "okno 8–16 s, LP 800 Hz (-36 dB) + warzone-3 20–28 s LP (-33 dB)"),
        "entry": {
            "id": "battle_distant_02",
            "setting": "pole bitwy / oblężenie — oddalona wrzawa",
            "desc": "daleka wrzawa wielu walczących nad niskim dudnieniem — "
                    "ludzki zgiełk już po szczycie starcia, jak za zasłoną kurzu",
            "file": "audio/library/backgrounds/battle_distant_02.mp3",
            "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
            "semantics": {"type": "bitwa-zgielk",
                          "traits": ["bitwa", "zgiełk", "krzyki", "oddalona", "wrzawa"],
                          "bad_for": ["spokojna komnata", "sielanka", "kameralna scena"]},
            "source": _src("battle/freesound_battle-ambience", 3,
                           "screams LP 800 Hz -36 dB + warzone-3 LP -33 dB"),
        },
    })
    print("  zg.2 zapisany")

    # --- zg.3: zmontowane pole bitwy (atomcut CC0): szczęk stali + okrzyki (technika g007) + bomby
    AT = Path("/tmp/atomcut/packs")
    swords = [AT / f"opengameart-20-sword-sound-effects-attacks-and-clashes/audio/sword-{i}.m4a" for i in (2, 6, 8)]
    yells = [AT / "opengameart-male-gruntyelling-sounds/audio/1yell13.m4a",
             AT / "opengameart-male-gruntyelling-sounds/audio/2yell10.m4a"]
    total = np.zeros((2, int(8.0 * dsp.SR)))
    # poszczególne szczęki w odstępach — daleki przypływ starcia
    for src, at in zip(swords, (1.2, 3.9, 6.4)):
        s, _ = dsp.load_any(src)
        s = lp(s, 750.0)
        s = dsp.normalize_rms(s, -30.0)
        dsp.place(total, s, at)
    # dwa okrzyki obniżone o 5 półtonów (metoda bramki g007) — ludzkie echa boju
    for src, at in zip(yells, (0.4, 4.8)):
        g, _ = dsp.load_any(src)
        r = to_roar(g, 5.0, hp_hz=60.0, lp_hz=900.0, drive=1.2)
        r = dsp.normalize_rms(r, -37.0)
        dsp.place(total, r[: int(1.6 * dsp.SR)] if len(r) > int(1.6 * dsp.SR) else r, at)
    # podkład dudnienia (warzone-3 inny fragment) — masa oddalonej bitwy
    base2, _ = dsp.load_any(SCOUT / "battle/freesound_battle-ambience/03-694371-fireworks-warzone-3.mp3")
    b2 = lp(dsp.cut(base2, 30.0, 38.0), 700.0)
    b2 = dsp.normalize_rms(b2, -34.0)
    mix = dsp.peak_ceiling(total + b2)
    dsp.encode_mp3(CAND / "zg3_montaz_pole_bitwy.mp3", steady_bed(mix))
    cands.append({
        "label": "zg.3", "title": 'zmontowane "echo starcia": stal, okrzyki, dudnienie',
        "file": "candidates/zg3_montaz_pole_bitwy.mp3",
        "desc": "konstrukcja z realnych sampli CC0: trzy dalekie szczęki broni, "
                "dwa okrzyki obniżone o 5 półtonów (filmowa technika pitch-down), "
                "podkład niskiego dudnienia — pełny obraz wygasającej bitwy",
        "source": "atomcut CC0 (20 sword SFX; male-gruntyelling haeldb) + Freesound 694371; "
                  "okrzyki -5 półtonów (resample), wszystkie warstwy LP 700-900 Hz",
        "entry": {
            "id": "battle_distant_03",
            "setting": "pole bitwy / oblężenie — wygasające starcie",
            "desc": "zmontowany zgiełk dalekiej bitwy: rzadkie szczęki stali, "
                    "obniżone okrzyki wojenne, niski gwar — bitwa, która już cichnie",
            "file": "audio/library/backgrounds/battle_distant_03.mp3",
            "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
            "semantics": {"type": "bitwa-zgielk",
                          "traits": ["bitwa", "zgiełk", "szczęk broni", "okrzyki", "wygasająca"],
                          "bad_for": ["spokojna komnata", "sielanka", "kameralna scena"]},
            "source": {"title": "montaż: atomcut (CC0) + Freesound 694371 (CC0)",
                       "author": "Various (OGA) / BenjaminNelan (Freesound)",
                       "license": "CC0 1.0",
                       "url": "https://opengameart.org/ (packs 20 sword SFX; male gruntyelling)",
                       "channel": "git sparse-checkout atomcut + sample-scout; skrypt build_gate_g025.py",
                       "notes": "okrzyki -5 półtonów to_roar; LP 700-900 Hz warstwy"},
        },
    })
    print("  zg.3 zapisany")
    return cands


# ---------------------------------------------------------------- hero: łopot-skrzydel
def hero_candidates() -> list[dict]:
    cands: list[dict] = []
    W = SCOUT / "wings/freesound_wings-flapping"

    # --- ł.1: framixo FlapWings — naturalna trójka zamachów (okno 40,0–46,8)
    w, _ = dsp.load_any(W / "03-463381-flapwings-aif.mp3")
    seg = dsp.cut(w, 40.0, 46.8)                    # trzy wyraźne zamachy w swobodnym rytmie
    seg = to_roar(seg, 3.0, hp_hz=50.0, lp_hz=3200.0, drive=1.0)   # -3 półtony = większe skrzydła
    seg = dsp.normalize_rms(seg, -18.0)
    seg = dsp.fade(seg, 0.25, 0.5)
    dsp.encode_mp3(CAND / "l1_flapwings_trojka.mp3", seg)
    cands.append({
        "label": "ł.1", "title": "trzy pełne zamachy — spokojne opadanie",
        "file": "candidates/l1_flapwings_trojka.mp3",
        "desc": "naturalna sekwencja trzech zamachów dużego ptaka, zwolniona o 3 półtony — "
                "miękki, głęboki łopot bez ostrości; jak opadanie z wysokości na polanę",
        "source": _src("wings/freesound_wings-flapping", 2,
                       "okno 40,0–46,8 s; -3 półtony (resample); LP 3200 Hz"),
        "entry": {
            "id": "wing_flap_01",
            "role": "łopot wielkich skrzydeł — zstąpienie",
            "character": "miękki, głęboki, oddechowy",
            "distance": "bliski", "energy": "średnia", "duration_sec": 5.5,
            "desc": "trzy pełne zamachy wielkich skrzydeł — miękka moc, spokojny rytm zstępowania",
            "good_for": "zstąpienie istoty skrzydlatej, anioł, duży ptak, miękkie lądowanie",
            "bad_for": "rozpacz, agresja, ptasi trzepot, małe skrzydła",
            "file": "audio/library/heroes/wing_flap_01.mp3",
            "semantics": {"type": "lopot-skrzydel",
                          "traits": ["łopot", "wielkie skrzydła", "miękki", "zstąpienie"],
                          "bad_for": ["trzepot", "pisk", "agresja"]},
            "source": _src("wings/freesound_wings-flapping", 2,
                           "okno 40,0–46,8 s; -3 półtony; LP 3200 Hz; -18 dB"),
        },
    })
    print("  ł.1 zapisany")

    # --- ł.2: Matteo_Fusi — cięższe, szersze zamachy (okno 42,8–52,0)
    w, _ = dsp.load_any(W / "01-843855-bird-wing-flaps-and-leaves-rustling-close-nature.mp3")
    seg = dsp.cut(w, 42.8, 52.0)
    seg = to_roar(seg, 4.0, hp_hz=45.0, lp_hz=2600.0, drive=1.0)   # -4 półtony, ciężej
    seg = dsp.normalize_rms(seg, -18.0)
    seg = dsp.fade(seg, 0.3, 0.7)
    dsp.encode_mp3(CAND / "l2_ciezkie_zamachy.mp3", seg)
    cands.append({
        "label": "ł.2", "title": "ciężkie, szerokie zamachy — jak dwa trzepnięcia płócien",
        "file": "candidates/l2_ciezkie_zamachy.mp3",
        "desc": "najmocniejsze zamachy z nagrania terenowego, obniżone o 4 półtony — "
                "słychać masę powietrza spychana w dół; bardziej „chorągiew na wietrze” niż skrzydło wróbla",
        "source": _src("wings/freesound_wings-flapping", 0,
                       "okno 42,8–52,0 s; -4 półtony; LP 2600 Hz"),
        "entry": {
            "id": "wing_flap_02",
            "role": "łopot wielkich skrzydeł — ciężki zamach",
            "character": "ciężki, szeroki, płócienny",
            "distance": "bliski", "energy": "średnio-wysoka", "duration_sec": 9.2,
            "desc": "ciężkie zamachy wielkich skrzydeł — spychana masa powietrza, szeroki dół",
            "good_for": "duże skrzydła przy lądowaniu, anioł niosący ciężar obecności",
            "bad_for": "trzepot owada, pisk, szybkie trzepotanie",
            "file": "audio/library/heroes/wing_flap_02.mp3",
            "semantics": {"type": "lopot-skrzydel",
                          "traits": ["łopot", "wielkie skrzydła", "ciężki", "szeroki"],
                          "bad_for": ["trzepot", "lekkie skrzydła", "szum całkowity"]},
            "source": _src("wings/freesound_wings-flapping", 0,
                           "okno 42,8–52,0 s; -4 półtony; LP 2600 Hz; -18 dB"),
        },
    })
    print("  ł.2 zapisany")

    # --- ł.3: montaż Clusman (dwie próbki jednego rodzaju) — zstąpienie z postojem
    a, _ = dsp.load_any(W / "02-543110-bird-flapping-1-wav.mp3")
    b, _ = dsp.load_any(W / "05-543117-bird-flapping-9-wav.mp3")
    a = to_roar(a, 4.0, hp_hz=45.0, lp_hz=2800.0, drive=1.0)
    b = to_roar(b, 5.0, hp_hz=45.0, lp_hz=2800.0, drive=1.0)
    a, b = dsp.normalize_rms(a, -20.0), dsp.normalize_rms(b, -22.0)
    total = np.zeros((2, int(4.6 * dsp.SR)))
    dsp.place(total, a, 0.0)
    dsp.place(total, b, 0.85)
    dsp.place(total, dsp.cut(a, 0.0, min(1.2, len(a) / dsp.SR)), 1.75)   # ostatni, najdłuższy zamach
    total = dsp.fade(total, 0.2, 0.8)
    dsp.encode_mp3(CAND / "l3_montaz_zstapienie.mp3", dsp.peak_ceiling(total))
    cands.append({
        "label": "ł.3", "title": "zstąpienie z postojem — dwa zamachy i zawieszenie",
        "file": "candidates/l3_montaz_zstapienie.mp3",
        "desc": 'aranżacja z dwóch nagrań jednego źródła (Clusman): zamach, zamach, '
                "potem dłuższe trzymanie powietrza — jak zwolnienie nad żołnierzem "
                "i nieruchome Trzymanie go w powietrzu",
        "source": _src("wings/freesound_wings-flapping", 1,
                       "łączone z id 543117; -4/-5 półtonów; LP 2800 Hz; montaż 3 zdarzeń"),
        "entry": {
            "id": "wing_flap_03",
            "role": "łopot wielkich skrzydeł — zstąpienie z postojem",
            "character": "skupiony, zwolniały, zawieszony",
            "distance": "bliski", "energy": "średnia", "duration_sec": 4.6,
            "desc": "dwa zamachy i zwolnione trzymanie skrzydeł — obecność, która zatrzymuje "
                    "się dokładnie nad człowiekiem",
            "good_for": "zstąpienie i uniesienie, objawienie, opiekuńcza obecność",
            "bad_for": "panika, tętent, agresja",
            "file": "audio/library/heroes/wing_flap_03.mp3",
            "semantics": {"type": "lopot-skrzydel",
                          "traits": ["łopot", "wielkie skrzydła", "zawieszenie", "zstąpienie"],
                          "bad_for": ["trzepot", "pisk", "agresja"]},
            "source": _src("wings/freesound_wings-flapping", 1,
                           "montaż id 543110 + 543117; -4/-5 półtonów; LP 2800 Hz"),
        },
    })
    print("  ł.3 zapisany")
    return cands


# ---------------------------------------------------------------- koda: nadzieja-ukojenie
# Nuty wyłącznie z siatki b_piano_steinway (48,50,54,56,60,64,68,72,74,76,80,84).
GESTURES = {
    "g9a_grace_lift": {
        "semantic": "nadzieja — ciepłe przyjęcie i uniesienie ku światłu",
        "desc": "niski ciepły dwudźwięk przyjmuje żołnierza, melodia wstępuje o krok "
                "i zostaje na górze — jak dłoń, która podnosi i trzyma",
        "notes": [
            {"midi": 60, "on": 0.0, "off": 1.1, "vel": 0.36},
            {"midi": 64, "on": 0.0, "off": 1.1, "vel": 0.34},
            {"midi": 74, "on": 0.65, "off": 1.30, "vel": 0.44},
            {"midi": 76, "on": 1.15, "off": 2.60, "vel": 0.48},
            {"midi": 68, "on": 1.15, "off": 2.60, "vel": 0.38},
            {"midi": 56, "on": 1.15, "off": 2.60, "vel": 0.34},
        ],
    },
    "g9b_steadfast_bloom": {
        "semantic": "nadzieja — wytrwałość nagrodzona rozkwitaniem",
        "desc": "trzy ciche, równe uderzenia tej samej nuty — stanie mimo wszystko — "
                "a potem jasny dwudźwięk rozpala się nad nimi jak nagroda",
        "notes": [
            {"midi": 64, "on": 0.00, "off": 0.40, "vel": 0.40},
            {"midi": 64, "on": 0.55, "off": 0.95, "vel": 0.40},
            {"midi": 64, "on": 1.10, "off": 1.50, "vel": 0.42},
            {"midi": 72, "on": 1.70, "off": 2.60, "vel": 0.46},
            {"midi": 76, "on": 1.70, "off": 2.60, "vel": 0.42},
        ],
    },
    "g9c_blessing_descend": {
        "semantic": "nadzieja — łaska, która zstępuje i zostaje",
        "desc": "figura schodzi miękkimi skokami z góry — Gis-E-C — i zatrzymuje się "
                "w ciepłym dolnym dwudźwięku; niebo samo schodzi do człowieka",
        "notes": [
            {"midi": 80, "on": 0.00, "off": 0.45, "vel": 0.42},
            {"midi": 76, "on": 0.40, "off": 0.85, "vel": 0.42},
            {"midi": 72, "on": 0.80, "off": 1.35, "vel": 0.44},
            {"midi": 60, "on": 1.30, "off": 2.60, "vel": 0.38},
            {"midi": 64, "on": 1.30, "off": 2.60, "vel": 0.36},
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
        r = coda_synth.render_coda(gesture, piano_abs, seed=110)
        for w in r.warnings:
            print(f"  ! {gid}: {w}")
        path = CAND / f"{gid}.mp3"
        dsp.encode_mp3(path, r.wave)
        cands.append({
            "label": {"g9a_grace_lift": "n.1", "g9b_steadfast_bloom": "n.2",
                      "g9c_blessing_descend": "n.3"}[gid],
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
                "instrument_tags": ["piano", "struck-light", "warm-keys"],
                "semantics": {"type": "nadzieja-ukojenie",
                              "traits": ["podniosła", "ciepła", "koiąca", "łaskawa"],
                              "bad_for": ["groza", "przygnębienie", "ironia", "zniekształcenie"]},
            },
        })
        print(f"  {gid} zapisany")
    return cands


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": "g025",
        "created": "2026-09-24",
        "story_id": "110",
        "note": "Fabuła 110 z losowania sesji (ziarno 20260924; resolver: 3 typy bez klocka z 4 "
                "warstw). Instrumentacja `jasno-swietlista` obsadzona b_piano_steinway. "
                "Kandydaci tła: dudnienie oddalone (Freesound), wrzawa walczących przyciemniona, "
                "montaż stali i okrzyków (atomcut, technika g007). Hero: łopoty zwolnione "
                "3-4 półtony (metryka g007: prawdziwe nagranie + właściwa technika). "
                "Kody: trzy autorskie gesty łaski na siatce steinwaya.",
        "entries": [
            {"slug": "tlo-bitwa-zgielk", "kind": "backgrounds",
             "role": "jedyny klocek typu tła `bitwa-zgielk` (15 fabuł; slot d fabuły 110)",
             "candidates": bg_candidates()},
            {"slug": "hero-lopot", "kind": "heroes",
             "role": "jedyny klocek typu hero `lopot-skrzydel` (18 fabuł; slot c fabuły 110)",
             "candidates": hero_candidates()},
            {"slug": "koda-nadzieja", "kind": "gestures",
             "role": "jedyny klocek typu kody `nadzieja-ukojenie` (22 fabuły; slot a fabuły 110)",
             "candidates": gesture_candidates()},
        ],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest g025 zapisany ({len(manifest['entries'])} wpisy)")


if __name__ == "__main__":
    main()
