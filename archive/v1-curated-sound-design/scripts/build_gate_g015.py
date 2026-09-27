#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g015 — trzy brakujące klocki fabuły 18 (Lotusguard Disciple).

Resolver (model 1:1, taksonomia v5) wskazał braki:
  d  tło    `niebo-przestworza`   — „pęd rydwanu-glidera nad torem — wiatr prędkości"
  c  hero   `bariera-odbicie`     — „iskry i odłamki odbijają się od świetlistej
                                     tarczy — serie dzwoniących odbić" (wymagane:
                                     odbicia od bariery)
  a  koda   `czujnosc-napiecie`   — „jasna czujność strażnika — nikt nie zginie
                                     na tej warcie"
Instrumentacja `jasno-swietlista` -> b_piano_steinway (już w bazie).

Źródła (sandbox bez internetu, lustra GitHub):
  * YSL — Yellowstone Sound Library (NPS, public domain), /tmp/ysl
    (sparse: Hurricane Vent, Snowmobile);
  * VCSL — Versilian Community Sample Library (CC0), /tmp/vcsl
    (sparse: Triangles, Hand Chimes, Glockenspiel).
Obróbka przezroczysta: cięcie, poziom, fade, miękki limiter; serie odbić to
aranżacja RÓŻNYCH ujęć (round-robin) bez pitchowania i syntezy.
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

GATE = REPO / "data" / "gates" / "g015"
CAND = GATE / "candidates"
YSL = Path("/tmp/ysl")
VCSL = Path("/tmp/vcsl/Idiophones/Struck Idiophones")

YSL_SRC = {
    "title": "Yellowstone Sound Library (NPS)",
    "author": "National Park Service",
    "license": "Public Domain (utwór rządu USA)",
    "url": "https://www.nps.gov/yell/learn/photosmultimedia/soundlibrary.htm",
    "channel": "git clone sparse z github.com/rosuH/YSL (mirror)",
}
VCSL_SRC = {
    "title": "Versilian Community Sample Library (VCSL)",
    "author": "Sam Gossner / Versilian Studios + społeczność",
    "license": "CC0 1.0",
    "url": "https://github.com/sgossner/VCSL",
    "channel": "git clone sparse z github.com/sgossner/VCSL",
}


def steadiest_window(wave: np.ndarray, sec: float, step: float = 1.0) -> float:
    """Początek najbardziej wyrównanego okna `sec` (min. wariancja RMS 1 s)."""
    n = wave.shape[1]
    best_t, best_var = 0.0, 1e9
    t = 0.0
    while (t + sec) * dsp.SR < n:
        seg = wave[:, int(t * dsp.SR):int((t + sec) * dsp.SR)]
        rms = [dsp.rms_db(seg[:, i:i + dsp.SR]) for i in range(0, seg.shape[1] - dsp.SR, dsp.SR)]
        var = float(np.var(rms))
        if var < best_var:
            best_t, best_var = t, var
        t += step
    return best_t


def loudest_window(wave: np.ndarray, sec: float, step: float = 0.5) -> float:
    n = wave.shape[1]
    best_t, best = 0.0, -1e9
    t = 0.0
    while (t + sec) * dsp.SR < n:
        seg = wave[:, int(t * dsp.SR):int((t + sec) * dsp.SR)]
        r = dsp.rms_db(seg)
        if r > best:
            best_t, best = t, r
        t += step
    return best_t


def finish_bg(seg: np.ndarray) -> np.ndarray:
    seg = dsp.normalize_rms(seg, -33.0)
    seg = dsp.fade(seg, 0.25, 0.4)
    peak = float(np.max(np.abs(seg)))
    ceiling = dsp.db_to_gain(-1.0)
    if peak > ceiling:
        seg *= ceiling / peak
    return seg


def bg_candidate(name, label, title, entry_id, src_file, t0, dur, desc, notes,
                 highpass=None):
    wave, _ = dsp.load_any(src_file)
    seg = wave[:, int(t0 * dsp.SR):int((t0 + dur) * dsp.SR)].copy()
    if highpass:
        sos = butter(2, highpass, btype="highpass", fs=dsp.SR, output="sos")
        seg = sosfiltfilt(sos, seg, axis=-1)
    seg = finish_bg(seg)
    path = CAND / f"{name}.mp3"
    dsp.encode_mp3(path, seg)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": f"{YSL_SRC['title']} — public domain",
        "entry": {
            "id": entry_id,
            "setting": "przestworza / pęd powietrza",
            "desc": desc,
            "file": f"audio/library/backgrounds/{entry_id}.mp3",
            "duration_sec": round(seg.shape[1] / dsp.SR, 2),
            "level_ref_db": -33,
            "loopable": True,
            "semantics": {
                "type": "niebo-przestworza",
                "traits": ["pęd powietrza", "wysokość", "ciągły", "bez gruntu"],
                "bad_for": ["wnętrze", "sielski spokój"],
            },
            "source": dict(YSL_SRC, notes=notes),
        },
    }


def series(hits: list[tuple[Path, float, float]], total: float) -> np.ndarray:
    """Aranżacja serii odbić: (plik, offset_s, gain_db) — bez pitchowania."""
    out = np.zeros((2, int(total * dsp.SR)))
    for path, at, gain_db in hits:
        w, _ = dsp.load_any(path)
        w = w * dsp.db_to_gain(gain_db)
        i0 = int(at * dsp.SR)
        n = min(w.shape[1], out.shape[1] - i0)
        out[:, i0:i0 + n] += w[:, :n]
    return out


def hero_candidate(name, label, title, entry_id, hits, total, desc, character, notes):
    seg = series(hits, total)
    seg = soft_limit(seg, crest_db=14.0, rounds=4)
    seg = dsp.normalize_rms(seg, -15.0)
    seg = dsp.fade(seg, 0.004, 0.25)
    peak = float(np.max(np.abs(seg)))
    ceiling = dsp.db_to_gain(-1.0)
    if peak > ceiling:
        seg *= ceiling / peak
    path = CAND / f"{name}.mp3"
    dsp.encode_mp3(path, seg)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc, "source": f"{VCSL_SRC['title']} — CC0",
        "entry": {
            "id": entry_id,
            "role": "serie dzwoniących odbić od świetlistej bariery",
            "character": character,
            "distance": "bliski",
            "energy": "wysoka",
            "duration_sec": round(seg.shape[1] / dsp.SR, 2),
            "desc": desc,
            "good_for": "magiczna tarcza, deflektory, iskry o powłokę, święta ochrona",
            "bad_for": "mroczne bariery, organiczne osłony, naturalistyczna fauna",
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "semantics": {
                "type": "bariera-odbicie",
                "traits": ["dzwoniący", "jasny", "seria odbić", "metaliczny"],
                "bad_for": ["mroczny", "organiczny", "głuchy"],
            },
            "source": dict(VCSL_SRC, notes=notes),
        },
    }


# Nuty wyłącznie z siatki próbek b_piano_steinway
# (48,50,54,56,60,64,68,72,74,76,80,84) — zero podstawień przy renderze.
GESTURES = {
    "g6a_watch_pulse": {
        "semantic": "jasna czujność — puls warty nad spokojnym dwudźwiękiem",
        "desc": "cichy, równy puls sekundy nad jasnym dwudźwiękiem — oddech "
                "strażnika, który nie śpi; napięcie sus2 nigdy nie opada",
        "notes": [
            {"midi": 60, "on": 0.0, "off": 2.6, "vel": 0.38},
            {"midi": 64, "on": 0.0, "off": 2.6, "vel": 0.34},
            {"midi": 74, "on": 0.20, "off": 0.55, "vel": 0.46},
            {"midi": 74, "on": 0.80, "off": 1.15, "vel": 0.44},
            {"midi": 74, "on": 1.40, "off": 1.75, "vel": 0.46},
            {"midi": 74, "on": 2.00, "off": 2.55, "vel": 0.42},
        ],
    },
    "g6b_alert_lift": {
        "semantic": "jasna czujność — uniesienie i rozjarzone zawieszenie",
        "desc": "dwie nuty w górę jak uniesienie wzroku, trzecia zawisa "
                "rozjarzona bez rozwiązania — gotowość tuż przed zdarzeniem",
        "notes": [
            {"midi": 72, "on": 0.0, "off": 0.5, "vel": 0.50},
            {"midi": 76, "on": 0.35, "off": 0.95, "vel": 0.54},
            {"midi": 80, "on": 0.75, "off": 2.4, "vel": 0.48},
            {"midi": 60, "on": 0.75, "off": 2.4, "vel": 0.36},
        ],
    },
    "g6c_sentry_return": {
        "semantic": "jasna czujność — obchód i powrót na posterunek",
        "desc": "figura odchodzi o krok w górę i wraca na tę samą jasną nutę — "
                "sprawdzone, bezpiecznie, warta trwa",
        "notes": [
            {"midi": 76, "on": 0.0, "off": 0.45, "vel": 0.48},
            {"midi": 80, "on": 0.35, "off": 0.85, "vel": 0.46},
            {"midi": 76, "on": 0.75, "off": 1.35, "vel": 0.44},
            {"midi": 60, "on": 1.20, "off": 2.5, "vel": 0.38},
            {"midi": 76, "on": 1.60, "off": 2.5, "vel": 0.38},
        ],
    },
}


def gesture_candidate(gid, label, title):
    spec = GESTURES[gid]
    instruments = json.loads((REPO / "data/library/instruments.json").read_text("utf-8"))
    piano = next(e for e in instruments["entries"] if e["id"] == "b_piano_steinway")
    piano_abs = {**piano, "samples": {m: str(REPO / p) for m, p in piano["samples"].items()}}
    gesture = {"notes": spec["notes"], "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}}}
    r = coda_synth.render_coda(gesture, piano_abs, seed=18)
    for w in r.warnings:
        print(f"  ! {gid}: {w}")
    path = CAND / f"{gid}.mp3"
    dsp.encode_mp3(path, r.wave)
    return {
        "label": label, "title": title, "file": f"candidates/{gid}.mp3",
        "desc": spec["desc"],
        "source": "gest autorski; podgląd na b_piano_steinway (render neutralny)",
        "entry": {
            "id": gid,
            "semantic": spec["semantic"],
            "desc": spec["desc"],
            "notes": spec["notes"],
            "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}},
            "instrument_tags": ["struck-light", "zither", "piano"],
            "semantics": {
                "type": "czujnosc-napiecie",
                "traits": ["jasna", "zawieszona", "pulsująca", "bez rozwiązania"],
                "bad_for": ["żałobna", "ciężka", "triumfalna"],
            },
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    vent = YSL / "Hurricane Vent/Sound Library - Hurricane Vent.mp3"
    sled = YSL / "Snowmobile/Sound Library - Snowmobile.mp3"

    wave_v, _ = dsp.load_any(vent)
    t_steady = steadiest_window(wave_v, 8.0)
    wave_s, _ = dsp.load_any(sled)
    t_pass = loudest_window(wave_s, 8.0)
    print(f"okna: vent steady @{t_steady:.1f}s, snowmobile pass @{t_pass:.1f}s")

    tri = VCSL / "Triangles"
    chi = VCSL / "Hand Chimes"
    glo = VCSL / "Glockenspiel"

    entries = [
        {
            "slug": "niebo-przestworza",
            "kind": "backgrounds",
            "role": "pęd powietrza nad torem wyścigowym — tło fabuły 18",
            "candidates": [
                bg_candidate("d_air_rush", "d.1", "ryk pędu powietrza",
                             "sky_rush_01", vent, t_steady, 8.0,
                             "ciągły, wyrównany pęd powietrza — jazda w strudze wiatru",
                             f"Hurricane Vent, okno {t_steady:.1f}–{t_steady+8:.1f} s; poziom i fade"),
                bg_candidate("d_air_bright", "d.2", "jaśniejszy świst pędu",
                             "sky_rush_02", vent, t_steady + 30.0, 8.0,
                             "ten sam pęd z odjętym dołem — lżejszy, szybszy charakter toru",
                             f"Hurricane Vent, okno {t_steady+30:.1f}–{t_steady+38:.1f} s; highpass 180 Hz, poziom i fade",
                             highpass=180.0),
                bg_candidate("d_flyby", "d.3", "przelot pojazdu (doppler)",
                             "sky_flyby_01", sled, max(t_pass - 2.0, 0.0), 8.0,
                             "przejazd pojazdu silnikowego z narastaniem i odjazdem — dosłowny pęd pojazdu (uwaga: słyszalny silnik)",
                             f"Snowmobile, okno {max(t_pass-2,0):.1f}–{max(t_pass-2,0)+8:.1f} s; poziom i fade"),
            ],
        },
        {
            "slug": "bariera-odbicie",
            "kind": "heroes",
            "role": "serie dzwoniących odbić od świetlistej tarczy — hero fabuły 18",
            "candidates": [
                hero_candidate("c_triangle_deflect", "c.1", "iskry o powłokę (trójkąty)",
                               "barrier_ring_01",
                               [(tri / "Triangle1_Hit_v2_rr1_Mid.wav", 0.00, -2),
                                (tri / "Triangle1_HitM_v1_rr2_Mid.wav", 0.16, -5),
                                (tri / "Triangle1_Hit_v1_rr2_Mid.wav", 0.34, -3),
                                (tri / "Triangle1_HitM_v1_rr4_Mid.wav", 0.62, -7),
                                (tri / "Triangle1_Hit_v2_rr2_Mid.wav", 0.95, -9)],
                               2.4,
                               "pięć nieregularnych metalicznych odbić — szybka salwa iskier gasnąca na powłoce",
                               "iskrzący, nieregularny, gasnący",
                               "5 różnych ujęć rr trójkątów (otwarte+tłumione); aranżacja czasowa, bez pitchowania"),
                hero_candidate("c_chime_shield", "c.2", "dzwoniąca tarcza (dzwonki ręczne)",
                               "barrier_ring_02",
                               [(chi / "sus_C5_r01_main.wav", 0.00, -3),
                                (chi / "sus_G#5_r01_main.wav", 0.22, -6),
                                (chi / "sus_E5_r01_main.wav", 0.50, -5),
                                (chi / "sus_C6_r01_main.wav", 0.92, -8)],
                               2.6,
                               "cztery tonalne, śpiewne odbicia — powłoka odpowiada akordem światła",
                               "tonalny, śpiewny, świetlisty",
                               "4 dzwonki ręczne (C5/G#5/E5/C6); aranżacja czasowa, bez pitchowania"),
                hero_candidate("c_glock_sparks", "c.3", "szkliste rykoszety (dzwonki)",
                               "barrier_ring_03",
                               [(glo / "glock_loud_C6_01.wav", 0.00, -4),
                                (glo / "glock_medium_C7_01.wav", 0.13, -8),
                                (glo / "glock_loud_G#6_01.wav", 0.30, -6),
                                (glo / "glock_medium_C6_01.wav", 0.55, -10),
                                (glo / "glock_medium_C7_01.wav", 0.86, -13)],
                               2.2,
                               "wysokie szkliste pingnięcia coraz dalej — odłamki rykoszetują i opadają",
                               "szklisty, wysoki, oddalający się",
                               "5 ujęć dzwonków orkiestrowych (C6/C7/G#6, loud+medium); aranżacja czasowa, bez pitchowania"),
            ],
        },
        {
            "slug": "koda-czujnosc",
            "kind": "gestures",
            "role": "koda `czujnosc-napiecie` — jasna czujność strażnika (fabuła 18)",
            "candidates": [
                gesture_candidate("g6a_watch_pulse", "a.1", "puls warty"),
                gesture_candidate("g6b_alert_lift", "a.2", "uniesienie i zawieszenie"),
                gesture_candidate("g6c_sentry_return", "a.3", "obchód i powrót"),
            ],
        },
    ]

    manifest = {
        "id": "g015",
        "created": "2026-09-24",
        "story_id": "18",
        "note": ("Etap 5 / fabuła 18 (Lotusguard Disciple). Trzy braki wskazane "
                 "przez resolver (model 1:1): tło niebo-przestworza, hero "
                 "bariera-odbicie, koda czujnosc-napiecie. Wszystkie bramki "
                 "fabuły naraz, po jednym werdykcie na slug. Czwarty slot "
                 "(instrumentacja jasno-swietlista) obsadza istniejący "
                 "b_piano_steinway."),
        "entries": entries,
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for e in entries:
        for c in e["candidates"]:
            p = GATE / c["file"]
            print(f"  {c['label']} {c['title']:38s} {p.stat().st_size/1024:6.0f} KB "
                  f"{c['entry'].get('duration_sec', '—')} s")
    print("manifest g015 zapisany")


if __name__ == "__main__":
    main()
