#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g028 — fabuła 249 „Feedback”, RUNDA 2 wpisu `dwor-komnaty`.

Diagnoza właściciela (data/gates/g026/verdicts.json::notes): czysta cisza
i szum nie przypominają nic; potrzebny dźwięk kojarzący się z KOMNATĄ
w zamku/wieży. Runda 2 — komnata Z ROZPOZNAWALNYM SERCEM:
  k.1 palenisko trzaskające w komnacie (Freesound CC0, realny hearth),
  k.2 „znaki pracują” — delikatny rezonans szklany z bazy (b_wine_glasses)
      nad cichym powietrzem izby (archiwalne k.2 z g026 jako podkład),
  k.3 życie gmachu za murami — rzadkie kroki na kamieniu, dalekie drzwi,
      brzęk przekładanych zwojów (atomcut/Sparkstream, CC0).
Baza podkładowa k.2 i k.3 = cisza odrzucona w r.1 obniżona do -38 dB —
zostaje tylko powietrze, które niesie zdarzenia.
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

GATE = REPO / "data" / "gates" / "g028"
CAND = GATE / "candidates"
SCOUT = REPO / "work" / "scout"
AT = Path("/tmp/atomcut/packs")
SP = Path("/tmp/sparkstream/sounds/impacts")


def _scout_src(manifest_dir: str, idx0: int, notes: str) -> dict:
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


def lp(wave: np.ndarray, hz: float) -> np.ndarray:
    sos = butter(3, min(hz, dsp.SR * 0.45), btype="lowpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1)


def hp(wave: np.ndarray, hz: float) -> np.ndarray:
    sos = butter(2, hz, btype="highpass", fs=dsp.SR, output="sos")
    return sosfiltfilt(sos, wave, axis=-1)


def air(peak_db: float = -41.0) -> np.ndarray:
    """Powietrze izby — archiwalne k.2 z g026 jako czysty, cichy podkład (dokładnie 8 s)."""
    w, _ = dsp.load_any(REPO / "data/gates/g026/candidates/k2_komnata_w_kamieniu.mp3")
    return dsp.normalize_rms(dsp.cut(w, 0.0, 8.0), peak_db)


def finish(total: np.ndarray) -> np.ndarray:
    return dsp.fade(dsp.peak_ceiling(total), 1.2, 1.5)


K_ENTRY = {
    "duration_sec": 8.0, "level_ref_db": -32, "loopable": True,
    "semantics": {"type": "dwor-komnaty",
                  "traits": ["wnętrze", "komnata", "skupienie"],
                  "bad_for": ["plener", "bitwa", "tłum uliczny"]},
}


def bg_candidates() -> list[dict]:
    cands: list[dict] = []

    # --- k.1: palenisko trzaskające w komnacie (realny hearth z Freesound)
    w, _ = dsp.load_any(SCOUT / "fireplace/freesound_fireplace-crackle/01-549208-fireplace-wav.mp3")
    seg = hp(dsp.cut(w, 4.0, 12.0), 70.0)
    seg = dsp.normalize_rms(seg, -32.0)
    mix = seg + air(-44.0)
    mix = np.tanh(mix)          # trzaski: crest ~44 dB — miękki saturator łagodzi piko, ciało nietknięte
    mix = dsp.peak_ceiling(dsp.normalize_rms(mix, -32.5))
    dsp.encode_mp3(CAND / "k1_palenisko_trzaska.mp3", dsp.fade(mix, 1.2, 1.5))
    e = dict(K_ENTRY)
    e["semantics"] = {"type": "dwor-komnaty",
                      "traits": ["wnętrze", "palenisko", "trzask", "komnata", "ciepło"],
                      "bad_for": ["plener", "bitwa", "mokre podziemia"]}
    cands.append({
        "label": "k.1", "title": "palenisko trzaskające w komnacie",
        "file": "candidates/k1_palenisko_trzaska.mp3",
        "desc": "prawdziwy kominek w izbie: trzaski drzewa w pasmach 2-6 kHz nosi "
                "charakter, niski dół palenia daje ciepło; nad oddechem wnętrza — "
                "komnata, w której ktoś czuwa przy ogniu",
        "source": _scout_src("fireplace/freesound_fireplace-crackle", 0,
                             "okno 4–12 s; HP 70 Hz; -32 dB; podkład-powietrze -44 dB"),
        "entry": {**e, "id": "chamber_hearth_01", "setting": "gmach / komnata — palenisko w izbie",
                  "desc": "trzask paleniska nad powietrzem cichej komnaty — ciepłe, "
                          "zamieszkałe wnętrze wieży",
                  "file": "audio/library/backgrounds/chamber_hearth_01.mp3",
                  "source": _scout_src("fireplace/freesound_fireplace-crackle", 0,
                                       "okno 4–12 s; HP 70; -32 dB")},
    })
    print("  k.1 zapisany")

    # --- k.2: „znaki pracują” — rezonans szklany z bazy + pojedyncze pobrzęki
    t = air(-38.0)
    insts = json.loads((REPO / "data/library/instruments.json").read_text("utf-8"))
    wg = next(x for x in insts["entries"] if x["id"] == "b_wine_glasses")
    ring, _ = dsp.load_any(REPO / wg["samples"]["63"])          # D#4 — długi rezonans
    ring_loop = dsp.loop_to_length(lp(ring, 2600.0), int(8.0 * dsp.SR), crossfade_ms=900.0)
    ring_loop = dsp.normalize_rms(ring_loop, -42.0)
    t = t + ring_loop
    for midi, at in (("66", 1.8), ("68", 5.1)):
        ping, _ = dsp.load_any(REPO / wg["samples"][midi])
        ping = dsp.cut(ping, 0.0, 3.2)
        ping = dsp.normalize_rms(lp(hp(ping, 200.0), 5000.0), -35.5)
        t = dsp.place(t, ping, at)
    dsp.encode_mp3(CAND / "k2_znaki_pracuja.mp3", finish(t))
    e = dict(K_ENTRY)
    e["semantics"] = {"type": "dwor-komnaty",
                      "traits": ["wnętrze", "komnata", "rezonans", "magia", "szklisty"],
                      "bad_for": ["plener", "bitwa", "hałaśliwy gwar"]}
    cands.append({
        "label": "k.2", "title": "znaki pracują — cichy rezonans wypełnia komnatę",
        "file": "candidates/k2_znaki_pracuja.mp3",
        "desc": "utrzymany, prawie niesłyszalny szklany rezonans (kieliszek z bazy "
                "wlożony nisko) z dwoma pojedynczymi pobrzękami — jak świecące znaki "
                "wisiorkujące w powietrzu komnaty maga",
        "source": "b_wine_glasses z bazy (VSCO-2-CE, CC0): warkot D#4 w pętli -38.5 dB, "
                  "pobrzęki F#4/A#4 -35.5 dB; podkład-powietrze -38 dB",
        "entry": {**e, "id": "chamber_runes_01", "setting": "gmach / komnata — rezonans zaklęć",
                  "desc": "cienki szklany rezonans utrzymujący się pod sufitem komnaty z "
                          "pojedynczymi dzwiękami — powietrze pracującej magii",
                  "file": "audio/library/backgrounds/chamber_runes_01.mp3",
                  "source": {"title": "b_wine_glasses (wpis z bramki g010) w pętli/rezerwie",
                             "author": "Sam Gossner / Versilian Studios + społeczność",
                             "license": "CC0 1.0",
                             "url": "https://github.com/sgossner/VSCO-2-CE",
                             "channel": "z bazy projektu; montaż skryptem build_gate_g028.py",
                             "notes": "ring D#4 -38.5 dB pętla 8 s; pingi F#4/A#4 -35.5 dB"}},
    })
    print("  k.2 zapisany")

    # --- k.3: życie gmachu za murami — kroki na kamieniu, dalekie drzwi, brzęk zwojów
    t = air(-36.5)
    steps = [f"impact-sounds-footstep_concrete_00{i}.wav" for i in (0, 2, 4, 1)]
    for f, at in zip(steps, (0.9, 2.7, 5.2, 7.1)):
        w, _ = dsp.load_any(SP / f)
        t = dsp.place(t, dsp.normalize_rms(lp(w, 1100.0), -32.5), at)
    w, _ = dsp.load_any(AT / "opengameart-100-cc0-metal-and-wood-sfx/audio/door-open-01.m4a")
    t = dsp.place(t, dsp.normalize_rms(lp(w, 900.0), -35.5), 3.7)
    w, _ = dsp.load_any(AT / "opengameart-100-cc0-metal-and-wood-sfx/audio/keys-02.m4a")
    t = dsp.place(t, dsp.normalize_rms(lp(hp(w, 300.0), 4500.0), -38.5), 6.4)
    dsp.encode_mp3(CAND / "k3_gmach_zyje.mp3", finish(t))
    e = dict(K_ENTRY)
    e["semantics"] = {"type": "dwor-komnaty",
                      "traits": ["wnętrze", "gmach", "kroki", "daleki", "komnata"],
                      "bad_for": ["plener", "bitwa", "martwa cisza"]}
    cands.append({
        "label": "k.3", "title": "życie gmachu za murami — kroki, drzwi, zwoje",
        "file": "candidates/k3_gmach_zyje.mp3",
        "desc": "cztery rzadkie kroki na kamieniu za ścianą, jedno dalekie domknięcie/otwarcie "
                "i cichy brzęk przekładanych przedmiotów — komnata w środku żyjącego "
                "Kolegium, gdzie praca trwa także gdzie indziej",
        "source": "atomcut CC0 (metal&wood: door-open-01, keys-02) + Sparkstream Kenney "
                  "(footstep_concrete, CC0); wszystko LP 900-4500 Hz, -34..-39.5 dB; podkład -38 dB",
        "entry": {**e, "id": "chamber_school_01", "setting": "gmach / komnaty — życie za murami",
                  "desc": "cicha izba, za której kamiennymi ścianami gmach dalej żyje — "
                          "rekolekcje kroków, drzwi i pracy",
                  "file": "audio/library/backgrounds/chamber_school_01.mp3",
                  "source": {"title": "montaż: atomcut-library + sparkstream-sounds",
                             "author": "Various OpenGameArt artists / Kenney",
                             "license": "CC0 1.0",
                             "url": "https://github.com/novincode/atomcut-library",
                             "channel": "git sparse-checkout /tmp/atomcut + /tmp/sparkstream; "
                                        "skrypt build_gate_g028.py",
                             "notes": "kroki beton LP 1100 (-34), drzwi LP 900 (-36.5), klucze (-39.5)"}},
    })
    print("  k.3 zapisany")
    return cands


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": "g028",
        "created": "2026-09-24",
        "story_id": "249",
        "note": "RUNDA 2 fabuły 249 — wyłącznie wpis `dwor-komnaty` (koda s.3 i instrument o.2 "
                "z g026 zaakceptowane). Diagnoza właściciela: cisza i szum niczego nie "
                "przypominają, komnata potrzebuje dźwięku-reprezentanta. Kandydaci: "
                "palenisko / rezonans znaków / życie gmachu.",
        "entries": [
            {"slug": "tlo-dwor-komnaty", "kind": "backgrounds",
             "role": "jedyny klocek typu tła `dwor-komnaty` (17 fabuł; slot d fabuły 249)",
             "candidates": bg_candidates()},
        ],
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest g028 zapisany ({len(manifest['entries'])} wpis)")


if __name__ == "__main__":
    main()
