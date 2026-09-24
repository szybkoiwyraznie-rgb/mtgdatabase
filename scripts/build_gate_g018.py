#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g018 — komplet czterech klocków dla wylosowanej fabuły 575
(Dromoka Warrior). Wszystkie braki naraz, po jednym werdykcie na wpis;
etykiety UNIKATOWE per wpis (d/c/a/b — zasada z gate-protocol).

  d  tło    `oboz-wojenny`        — porządek wojskowy: tabor, kroki, brzęk
  c  hero   `marsz-oddzialu`      — miarowy marsz wielu par nóg (stylizowany
                                    rytm z prawdziwych uderzeń; brak CC0
                                    nagrań butów w dostępnych lustrach —
                                    uczciwie opisane, właściciel może odrzucić)
  a  koda   `precyzja-dyscyplina` — czysta, kontrolowana figura (autorska)
  b  instr  `sucho-surowa`        — drewno/skóra bez pogłosu (VCSL)

Źródła: YSL (public domain), VCSL (CC0). Obróbka opisana per kandydat.
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
from build_gate_g003 import soft_limit  # noqa: E402
from build_gate_g015 import YSL_SRC, VCSL_SRC, finish_bg, series  # noqa: E402

GATE = REPO / "data" / "gates" / "g018"
CAND = GATE / "candidates"
YSL = Path("/tmp/ysl")
VC = Path("/tmp/vcsl/Idiophones/Struck Idiophones")
VCM = Path("/tmp/vcsl/Membranophones/Struck Membranophones")

WAGON = YSL / "Horse-Drawn Wagon/Sound Library - Silver Tip Ranch Horse-Drawn Wagon.mp3"
FIRE = YSL / "Fire/Sound Library - Fire.mp3"


def encode(path, seg):
    path.parent.mkdir(parents=True, exist_ok=True)
    dsp.encode_mp3(path, seg)


def finish_hero(seg, rms=-15.0, fade_out=0.3):
    seg = soft_limit(seg, crest_db=14.0, rounds=4)
    seg = dsp.normalize_rms(seg, rms)
    seg = dsp.fade(seg, 0.01, fade_out)
    peak = float(np.max(np.abs(seg)))
    ceil = dsp.db_to_gain(-1.0)
    if peak > ceil:
        seg *= ceil / peak
    return seg


# ---------- d: tło oboz-wojenny ----------

def bg_entry(entry_id, desc, notes):
    return {
        "id": entry_id, "setting": "obóz wojenny / porządek formacji",
        "desc": desc, "file": f"audio/library/backgrounds/{entry_id}.mp3",
        "duration_sec": 8.0, "level_ref_db": -33, "loopable": True,
        "semantics": {"type": "oboz-wojenny",
                      "traits": ["tabor", "kroki", "brzęk rynsztunku", "porządek"],
                      "bad_for": ["dzika natura", "wnętrze", "miasto"]},
        "source": dict(YSL_SRC, notes=notes),
    }


def build_bg():
    w_w, _ = dsp.load_any(WAGON)
    w_f, _ = dsp.load_any(FIRE)
    out = []
    # d.1 — tabor
    seg = w_w[:, int(2.0 * dsp.SR):int(10.0 * dsp.SR)].copy()
    seg = finish_bg(seg)
    encode(CAND / "d_wagon.mp3", seg)
    e = bg_entry("warcamp_01",
                 "tabor obozu: skrzyp uprzęży, kroki koni, brzęk okuć — logistyka wojenna w ruchu",
                 "Horse-Drawn Wagon 2–10 s; poziom +~13 dB (ciche nagranie terenowe), fade")
    out.append({"label": "d.1", "title": "tabor obozu", "file": "candidates/d_wagon.mp3",
                "desc": e["desc"], "source": "YSL — public domain", "entry": e})
    # d.2 — tabor + oddalone ognie (miks dokumentowany)
    fire = w_f[:, int(5.0 * dsp.SR):int(13.0 * dsp.SR)].copy()
    sos = butter(4, 1800.0, btype="lowpass", fs=dsp.SR, output="sos")
    fire = sosfiltfilt(sos, fire, axis=-1) * dsp.db_to_gain(-6.0)
    wag = w_w[:, int(12.0 * dsp.SR):int(20.0 * dsp.SR)].copy()
    wag = dsp.normalize_rms(wag, -33.0)
    fire = dsp.normalize_rms(fire, -39.0)
    mix = finish_bg(wag + fire)
    encode(CAND / "d_wagon_fire.mp3", mix)
    e = bg_entry("warcamp_02",
                 "tabor z ogniami obozowymi w oddali — skrzyp, kroki i ciepły trzask na dystansie",
                 "miks: Wagon 12–20 s (-33) + Fire 5–13 s lowpass 1.8 kHz (-39); poziomy i fade")
    out.append({"label": "d.2", "title": "tabor przy ogniach", "file": "candidates/d_wagon_fire.mp3",
                "desc": e["desc"], "source": "YSL — public domain (miks 2 nagrań)", "entry": e})
    # d.3 — ognie obozowe na dystansie
    fire3 = w_f[:, int(20.0 * dsp.SR):int(28.0 * dsp.SR)].copy()
    fire3 = sosfiltfilt(sos, fire3, axis=-1)
    fire3 = finish_bg(fire3)
    encode(CAND / "d_fires.mp3", fire3)
    e = bg_entry("warcamp_03",
                 "szerokie ognie obozowe na dystansie — trzask wielu palenisk, bez taboru",
                 "Fire 20–28 s; lowpass 1.8 kHz (dystans), poziom, fade")
    out.append({"label": "d.3", "title": "ognie obozowe w oddali", "file": "candidates/d_fires.mp3",
                "desc": e["desc"], "source": "YSL — public domain", "entry": e})
    return out


# ---------- c: hero marsz-oddzialu ----------

def march_pattern(paths, period, steps, jitter, layers, gain_db=0.0, seed=575):
    rng = np.random.default_rng(seed)
    hits = []
    for lay in range(layers):
        off0 = lay * 0.018
        for i in range(steps):
            p = paths[(i + lay) % len(paths)]
            t = off0 + i * period + float(rng.uniform(-jitter, jitter))
            hits.append((p, max(t, 0.0), gain_db + float(rng.uniform(-1.5, 0.0))))
    total = steps * period + 0.8
    return series(hits, total)


def hero_c(name, label, title, entry_id, seg, desc, character, notes):
    seg = finish_hero(seg, rms=-15.0, fade_out=0.25)
    encode(CAND / f"{name}.mp3", seg)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": "VCSL — CC0 (aranżacja rytmiczna, bez pitchowania)",
        "entry": {
            "id": entry_id, "role": "miarowy marsz oddziału",
            "character": character, "distance": "średni", "energy": "średnia",
            "duration_sec": round(seg.shape[1] / dsp.SR, 2), "desc": desc,
            "good_for": "kolumna wojska, natarcie w szyku, patrol, falanga",
            "bad_for": "pojedynczy wędrowiec, skradanie, kawaleria",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "semantics": {"type": "marsz-oddzialu",
                          "traits": ["miarowy", "wielogłosowy krok", "zdyscyplinowany"],
                          "bad_for": ["chaotyczny", "pojedynczy", "galop"]},
            "source": dict(VCSL_SRC, notes=notes),
        },
    }


def build_hero():
    fd = [VCM / "Frame Drum" / f for f in
          ["HDrumL_HitMuted_v2_rr1_Sum.wav", "HDrumL_HitMuted_v3_rr1_Sum.wav",
           "HDrumL_HitMuted_v2_rr2_Sum.wav", "HDrumL_HitMuted_v3_rr2_Sum.wav"]]
    logs = [VC / "Slit Drum" / f for f in
            ["LogDrumLo_MedM_v1_rr1_Sum.wav", "LogDrumLo_MedM_v2_rr1_Sum.wav",
             "LogDrumLo_MedM_v3_rr1_Sum.wav"]]
    clav = [VC / "Claves" / f for f in
            ["Claves1_Hit_v1_rr1_Mid.wav", "Claves1_Hit_v2_rr1_Mid.wav",
             "Claves2_Hit_v1_rr1_Mid.wav"]]
    out = []
    out.append(hero_c("c_march_muted", "c.1", "głuchy marsz (bęben obręczowy)",
                      "troop_march_01",
                      march_pattern(fd, 0.5, 6, 0.012, layers=2),
                      "sześć miarowych, głuchych stąpnięć w dwóch warstwach — kolumna idzie równym krokiem",
                      "głuchy, miarowy, zwarty",
                      "frame drum HitMuted, 4 ujęcia rr; rytm 0.5 s × 6, dwie warstwy ±18 ms; stylizowany marsz"),
    )
    out.append(hero_c("c_march_wood", "c.2", "drewniany krok kolumny",
                      "troop_march_02",
                      march_pattern(logs, 0.5, 6, 0.010, layers=2),
                      "głęboki drewniany krok — jak tarany stóp w suchym pyle",
                      "drewniany, głęboki, surowy",
                      "log drum Lo, 3 ujęcia rr; rytm 0.5 s × 6, dwie warstwy; stylizowany marsz"),
    )
    both = march_pattern(fd, 0.5, 6, 0.012, layers=2)
    acc = march_pattern(clav, 1.0, 3, 0.008, layers=1, gain_db=-7.0)
    n = max(both.shape[1], acc.shape[1])
    mix = np.zeros((2, n)); mix[:, :both.shape[1]] += both; mix[:, :acc.shape[1]] += acc
    out.append(hero_c("c_march_accent", "c.3", "marsz z akcentem broni",
                      "troop_march_03", mix,
                      "miarowy marsz z suchym akcentem co drugi krok — pancerz i drzewce w rytmie",
                      "miarowy, akcentowany, wojskowy",
                      "frame drum jak c.1 + claves co 1.0 s (-7 dB); stylizowany marsz"),
    )
    return out


# ---------- a: koda precyzja-dyscyplina ----------

GESTURES = {
    "g7a_even_rank": {
        "semantic": "precyzja — równy szereg",
        "desc": "cztery identyczne staccato w idealnych odstępach i czyste "
                "domknięcie — szereg wyrównany co do milimetra",
        "notes": [
            {"midi": 72, "on": 0.00, "off": 0.22, "vel": 0.50},
            {"midi": 72, "on": 0.40, "off": 0.62, "vel": 0.50},
            {"midi": 72, "on": 0.80, "off": 1.02, "vel": 0.50},
            {"midi": 72, "on": 1.20, "off": 1.42, "vel": 0.50},
            {"midi": 60, "on": 1.60, "off": 2.4, "vel": 0.46},
            {"midi": 76, "on": 1.60, "off": 2.4, "vel": 0.42},
        ],
    },
    "g7b_order_cadence": {
        "semantic": "precyzja — kadencja rozkazu",
        "desc": "trzy kroki w górę wykonane co do joty i twarde osadzenie na "
                "tonice — rozkaz wydany i wykonany",
        "notes": [
            {"midi": 60, "on": 0.00, "off": 0.30, "vel": 0.50},
            {"midi": 64, "on": 0.35, "off": 0.65, "vel": 0.50},
            {"midi": 72, "on": 0.70, "off": 1.00, "vel": 0.52},
            {"midi": 60, "on": 1.15, "off": 2.3, "vel": 0.48},
        ],
    },
    "g7c_lockstep": {
        "semantic": "precyzja — dwugłos w kroku",
        "desc": "dwa głosy idą równolegle w oktawie, żaden nie wyprzedza — "
                "dyscyplina jako spokój, nie musztra",
        "notes": [
            {"midi": 60, "on": 0.00, "off": 0.35, "vel": 0.46},
            {"midi": 72, "on": 0.00, "off": 0.35, "vel": 0.42},
            {"midi": 64, "on": 0.50, "off": 0.85, "vel": 0.46},
            {"midi": 76, "on": 0.50, "off": 0.85, "vel": 0.42},
            {"midi": 60, "on": 1.00, "off": 2.2, "vel": 0.44},
            {"midi": 72, "on": 1.00, "off": 2.2, "vel": 0.40},
        ],
    },
}


def gesture_cand(gid, label, title):
    spec = GESTURES[gid]
    instruments = json.loads((REPO / "data/library/instruments.json").read_text("utf-8"))
    piano = next(e for e in instruments["entries"] if e["id"] == "b_piano_steinway")
    piano_abs = {**piano, "samples": {m: str(REPO / p) for m, p in piano["samples"].items()}}
    gesture = {"notes": spec["notes"], "delivery": {"humanize": {"timing_ms": 8, "vel": 0.02}}}
    r = coda_synth.render_coda(gesture, piano_abs, seed=575)
    encode(CAND / f"{gid}.mp3", r.wave)
    return {
        "label": label, "title": title, "file": f"candidates/{gid}.mp3",
        "desc": spec["desc"],
        "source": "gest autorski; podgląd na b_piano_steinway (render neutralny)",
        "entry": {
            "id": gid, "semantic": spec["semantic"], "desc": spec["desc"],
            "notes": spec["notes"],
            "delivery": {"humanize": {"timing_ms": 8, "vel": 0.02}},
            "instrument_tags": ["struck-light", "struck-dry", "piano"],
            "semantics": {"type": "precyzja-dyscyplina",
                          "traits": ["równy", "kontrolowany", "czysty", "bez rubato"],
                          "bad_for": ["rozlewny", "chaotyczny", "sentymentalny"]},
        },
    }


# ---------- b: instrument sucho-surowa ----------

INSTR = {
    "b_woodblock": {
        "semantic": "suchy, twardy, bez pogłosu",
        "family": "idiophone-struck",
        "dir": VC / "Woodblock",
        "notes": {"38": "wood_click_mp.wav", "39": "wood_click_f_rr1.wav", "41": "wood_click_ff.wav"},
        "title": "pudełko drewniane",
        "desc": "krótki twardy klik drewna — zero ogona, sama krawędź",
    },
    "b_claves": {
        "semantic": "suchy, dźwięczno-drewniany",
        "family": "idiophone-struck",
        "dir": VC / "Claves",
        "notes": {"38": "Claves1_Hit_v1_rr1_Mid.wav", "39": "Claves1_Hit_v2_rr1_Mid.wav", "41": "Claves1_Hit_v3_rr1_Mid.wav"},
        "title": "klawesy",
        "desc": "sucha, dźwięczna kość drewna — odrobina tonu w klikanym ataku",
    },
    "b_logdrum": {
        "semantic": "suchy, głucho-drewniany",
        "family": "idiophone-struck",
        "dir": VC / "Slit Drum",
        "notes": {"38": "LogDrumLo_MedM_v1_rr1_Sum.wav", "39": "LogDrumLo_MedM_v2_rr1_Sum.wav", "41": "LogDrumHi_MedM_v1_rr1_Sum.wav"},
        "title": "bęben szczelinowy",
        "desc": "głuchy drewniany puls — ciemniejszy i głębszy niż woodblock",
    },
}

DEMO_DRUM = {"notes": [
    {"midi": 38, "on": 0.0, "off": 0.3, "vel": 0.8},
    {"midi": 38, "on": 0.5, "off": 0.8, "vel": 0.8},
    {"midi": 39, "on": 1.0, "off": 1.3, "vel": 0.85},
    {"midi": 41, "on": 1.6, "off": 2.4, "vel": 0.9},
]}


def instr_cand(iid, label):
    spec = INSTR[iid]
    gate_sources = {}
    for midi, fname in spec["notes"].items():
        w, _ = dsp.load_any(spec["dir"] / fname)
        out = GATE / "instr_notes" / f"{iid}_{fname.replace('.wav', '.mp3').replace('#', 's')}"
        encode(out, w)
        gate_sources[midi] = f"instr_notes/{out.name}"
    entry = {
        "id": iid, "semantic": spec["semantic"], "family": spec["family"],
        "samples": {m: f"audio/library/instruments/{iid.replace('b_', '')}/{Path(rel).name}"
                    for m, rel in gate_sources.items()},
        "gate_sources": gate_sources,
        "semantics": {"type": "sucho-surowa",
                      "traits": ["suchy", "drewniany", "bez pogłosu", "twardy atak"],
                      "bad_for": ["rozmyty", "dzwoniący", "syntetyczny"]},
        "source": dict(VCSL_SRC, notes="nuty 38/39/41 = progi uderzenia mp/f/ff"),
    }
    inst_abs = {**entry, "samples": {m: str(GATE / rel) for m, rel in gate_sources.items()}}
    r = coda_synth.render_coda(DEMO_DRUM, inst_abs, seed=575)
    encode(CAND / f"{iid}_demo.mp3", r.wave)
    return {
        "label": label, "title": spec["title"], "file": f"candidates/{iid}_demo.mp3",
        "desc": spec["desc"], "source": "VCSL — CC0 (fraza demonstracyjna)",
        "entry": entry,
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    entries = [
        {"slug": "oboz-wojenny", "kind": "backgrounds",
         "role": "jedyny klocek typu tła `oboz-wojenny` (woła 30 fabuł; domyka slot d fabuły 575)",
         "candidates": build_bg()},
        {"slug": "marsz-oddzialu", "kind": "heroes",
         "role": "jedyny klocek typu hero `marsz-oddzialu` (7 fabuł; slot c fabuły 575)",
         "candidates": build_hero()},
        {"slug": "koda-precyzja", "kind": "gestures",
         "role": "koda `precyzja-dyscyplina` (17 fabuł; slot a fabuły 575)",
         "candidates": [gesture_cand("g7a_even_rank", "a.1", "równy szereg"),
                        gesture_cand("g7b_order_cadence", "a.2", "kadencja rozkazu"),
                        gesture_cand("g7c_lockstep", "a.3", "dwugłos w kroku")]},
        {"slug": "instrument-suchy", "kind": "instruments",
         "role": "instrument `sucho-surowa` (19 fabuł; slot b fabuły 575)",
         "candidates": [instr_cand("b_woodblock", "b.1"),
                        instr_cand("b_claves", "b.2"),
                        instr_cand("b_logdrum", "b.3")]},
    ]
    manifest = {
        "id": "g018", "created": "2026-09-24", "story_id": "575",
        "note": ("Etap 5, tryb losowy (decyzja właściciela): fabuła 575 "
                 "Dromoka Warrior wylosowana; brakowały WSZYSTKIE cztery "
                 "klocki — komplet bramek naraz. Etykiety unikatowe per wpis "
                 "(d/c/a/b). Kandydaci pod definicje typów."),
        "entries": entries,
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for e in entries:
        for c in e["candidates"]:
            p = GATE / c["file"]
            print(f"  {e['slug'][:16]:16s} {c['label']} {c['title']:34s} {p.stat().st_size/1024:5.0f} KB")
    print("manifest g018 zapisany")


if __name__ == "__main__":
    main()
