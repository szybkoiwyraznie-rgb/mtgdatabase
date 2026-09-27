#!/usr/bin/env python3
"""Bramka g004 — wpisy hero zfabrykowane Z FABUŁ (nie „z inwentarza").

Lekcja z werdyktu g002/g003 + fabuł 5/8: role obsadza się klockami
pasującymi DRAMATURGICZNIE; brak wpisu = bramka, nigdy podstawianie.

Trzy wpisy hero (baza heroes), każdy × 3 kandydaci z JEDNEJ rodziny
źródłowej (3 warianty tej samej roli, ADR 0004 + korekta g002):

- ryk-bestii: ogrebane „Monster Sound Effects Pack" (OGA, CC0) —
  potworne ryki (krótkie, grywalne uderzenia bestii);
- rzut-czaru: jaggedstone „Magic Spell SFX" (OGA, CC0) — rzucanie
  czaru (fabuła 5: wir portalu + magia);
- wrzask-wojenny-goblinów: artisticdude „Goblins Sound Pack" (OGA, CC0)
  — szaleńczy wrzask bandy (fabuła 8: gobliny Jundu).

Każdy kandydat: dekodowanie PyAV → lekka saturacja → limiter tanh
(crest ≤12 dB) → normalize RMS → mp3 192k. Sonda słyszalności w
standardowym wyjściu skryptu (protokół: żadnego „pustego dźwięku").

Usage:
  python scripts/build_gate_g004.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

import sig_audio as dsp

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "data" / "gates" / "g004"
CAND = GATE / "candidates"
sys.path.insert(0, str(REPO / "scripts"))
import build_gate_g003 as g003  # noqa: E402  (soft_limit)

PACKS = Path("/tmp/atomcut/packs")


def oga_source(pack_title: str, author: str, homepage: str, rel_file: str) -> dict:
    return {
        "title": f"{pack_title} (OpenGameArt)",
        "author": author,
        "license": "CC0 1.0 (public domain)",
        "url": homepage,
        "channel": "git clone sparse z github.com/novincode/atomcut-library (mirror)",
        "notes": f"{rel_file}; mirror pack.json potwierdza CC0 1.0",
    }


def make_hit(src: Path, name: str, label: str, title: str, entry_id: str,
             norm_db: float, desc: str, character: str, energy: str, distance: str,
             good_for: str, bad_for: str, source: dict,
             layers: list[tuple[float, float]] | None = None) -> dict:
    """Kandydat-uderzenie (layers: [(at_s, gain)] dokładek tej samej rodziny)."""
    wave, _ = dsp.load_any(src)
    if layers:
        sr = dsp.SR
        comp = wave.copy()
        for at, gain in layers:
            comp_wide = np.zeros((2, comp.shape[1] + int(at * sr) + 1), dtype=np.float32)
            comp_wide[:, : comp.shape[1]] = comp * 1.0
            comp_wide[:, int(at * sr): int(at * sr) + wave.shape[1]] += wave * gain
            comp = comp_wide
        wave = comp
    wave = np.tanh(wave * 1.35) / np.tanh(1.35)  # lekka saturacja — „jądro"
    wave = g003.soft_limit(wave, crest_db=12.0)
    wave = dsp.normalize_rms(wave, norm_db)
    wave = dsp.fade(wave, 0.005, min(0.18, wave.shape[1] / dsp.SR * 0.25))
    out = CAND / f"{name}.mp3"
    dsp.encode_mp3(out, wave)
    dur = round(wave.shape[1] / dsp.SR, 2)
    return {
        "label": label, "title": title, "file": f"candidates/{name}.mp3",
        "desc": desc,
        "source": f"{source['title']} — {source['license']}",
        "entry": {
            "id": entry_id, "role": title,
            "character": character, "distance": distance, "energy": energy,
            "duration_sec": dur, "desc": desc,
            "good_for": good_for, "bad_for": bad_for,
            "file": f"audio/library/heroes/{entry_id}.mp3",
            "source": source,
        },
    }


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    mons1 = PACKS / "opengameart-monster-sound-effects-pack/audio"
    magic = PACKS / "opengameart-magic-spell-sfx/audio"
    gobl = PACKS / "opengameart-goblins-sound-pack/audio"

    src_monster = oga_source("Monster Sound Effects Pack", "ogrebane",
                             "https://opengameart.org/content/monster-sound-effects-pack",
                             "packs/opengameart-monster-sound-effects-pack")
    src_magic = oga_source("Magic Spell SFX", "jaggedstone",
                           "https://opengameart.org/content/magic-spell-sfx",
                           "packs/opengameart-magic-spell-sfx")
    src_goblins = oga_source("Goblins Sound Pack", "artisticdude",
                             "https://opengameart.org/content/goblins-sound-pack",
                             "packs/opengameart-goblins-sound-pack")

    candidates_by_entry = {
        "ryk-bestii": {
            "kind": "heroes",
            "role": "pojedynczy, czytelny ryk dużej dzikiej bestii jako hero fabuły",
            "candidates": [
                make_hit(mons1 / "monster-8.m4a", "r_beast_long", "r.1",
                         "ryk długi, niski", "beast_roar_long_01", -14.5,
                         "najdłuższy ryk z zestawu potwora (0,94 s) — niski, pełny; zostawia ogon grozy",
                         "niski, pełny, rozwlekły", "wysoka", "bliski",
                         "zapowiedź bestii, przecięcie sceny, powolny horror",
                         "ultra-krótkie sygnatury interfejsowe",
                         src_monster),
                make_hit(mons1 / "monster-10.m4a", "r_beast_snap", "r.2",
                         "ryk rzucany, agresywny", "beast_roar_snap_01", -14.0,
                         "krótki, ostry zarzut (0,66 s) — atak bestii w miejscu",
                         "agresywny, zasadzkowy", "bardzo wysoka", "bliski",
                         "atak, niespodzianka, agresywna karta",
                         "delikatne, medytacyjne fabuły",
                         src_monster),
                make_hit(mons1 / "monster-6.m4a", "r_beast_wide", "r.3",
                         "ryk szeroki, warstwowy", "beast_roar_wide_01", -14.5,
                         "najdłuższy z szerokim pasmem (1,0 s, pik 510 Hz) + lekka saturacja — brzmi jak pełne gardło",
                         "szeroki, gardłowy", "bardzo wysoka", "bliski",
                         "duża bestia planu, dominujący hero",
                         "kameralność, kamienie runiczne",
                         src_monster),
            ],
        },
        "rzut-czaru": {
            "kind": "heroes",
            "role": "moment rzucenia czaru / rozdarciem portalu jako hero fabuły magicznej",
            "candidates": [
                make_hit(magic / "magical-3.m4a", "m_spell_impact", "m.1",
                         "uderzenie czaru", "spell_cast_impact_01", -15.0,
                         "najmocniejszy z paczki (1,83 s, pik 1327 Hz) — zapłon i rozładowanie energii",
                         "mocny, rozładowujący", "wysoka", "średni",
                         "rzucenie czaru, otwarcie portalu, epicki rozruch magii",
                         "bełkotliwe, ciche scenerie",
                         src_magic),
                make_hit(magic / "magical-1-0.m4a", "m_spell_bolt", "m.2",
                         "pocisk magiczny", "spell_cast_bolt_01", -15.5,
                         "klasyczny błysk zaklęcia (1,62 s, pik 1615 Hz) — czysty strzał energii",
                         "czysty, skupiony", "wysoka", "średni",
                         "celowany czar, pojedynek magów, akademicki talent",
                         "chaos hordy, naturalistyczne scenerie",
                         src_magic),
                make_hit(magic / "magical-4.m4a", "m_spell_weave", "m.3",
                         "tkanie zaklęcia", "spell_cast_weave_01", -15.5,
                         "najdłuższy (2,43 s, narastanie) — czar wiązany warstwami aż do wybuchu",
                         "narastający, warstwowy", "średnia", "średni",
                         "długi rytuał, przywołanie, tajemna akademia",
                         "błyskawiczna akcja, gobliny",
                         src_magic),
            ],
        },
        "wrzask-wojenny-goblinów": {
            "kind": "heroes",
            "role": "szaleńczy okrzyk wojenny drobnej bandy jako hero fabuły plemiennej",
            "candidates": [
                make_hit(gobl / "goblin-3.m4a", "g_warcry_long", "g.1",
                         "długi skowyt wodza", "goblin_warcry_01", -15.0,
                         "najdłuższy gobliński krzyk z paczki (0,96 s) — prowokujący, jazgotliwy",
                         "jazgotliwy, prowokujący", "wysoka", "bliski",
                         "szef bandy goblinów, drwina, wojenne hasło",
                         "groźna cisza, epicka powaga",
                         src_goblins),
                make_hit(gobl / "goblin-9.m4a", "g_warcry_sharp", "g.2",
                         "ostry wrzask szarży", "goblin_shriek_01", -15.0,
                         "najgłośniejszy i najkrótszy atak (0,47 s) — pisk szarżującego goblina",
                         "piskliwy, napastliwy", "bardzo wysoka", "bliski",
                         "nagły atak, rozpoczęcie starcia, chaos",
                         "długie hero, medytacja",
                         src_goblins),
                make_hit(gobl / "goblin-12.m4a", "g_warcry_duo", "g.3",
                         "wrzask ze zwolennikiem", "goblin_warcry_duo_01", -15.0,
                         "ochrypły krzyk (0,68 s) + drugi goblin 0,25 s później z paczki — mini-horda szamana (dwiema ciosy z jednej rodziny)",
                         "ochrypły, plemienny", "wysoka", "bliski",
                         "banda przy wulkanicznym ogniu, chant wojny, Jund",
                         "samotny łowca, eleganckie karty",
                         src_goblins,
                         layers=[(0.25, 0.8)]),
            ],
        },
    }

    entries = [{"slug": slug, **spec} for slug, spec in candidates_by_entry.items()]
    manifest = {
        "id": "g004",
        "created": date.today().isoformat(),
        "note": ("Wpisy hero zfabrykowane z fabuł 2/5/8 (role z narracji, nie z inwentarza). "
                 "ryk-bestii: powtórka po g003 (bison odrzucony) — tym razem prawdziwe "
                 "potworne ryki z paczki OGA (jedna rodzina). Etykiety unikalne: r.*/m.*/g.*."),
        "entries": entries,
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for entry in entries:
        for cand in entry["candidates"]:
            f = CAND / Path(cand["file"]).name
            w, _ = dsp.load_any(f)
            x = w.mean(axis=0)
            peak = float(np.abs(x).max())
            print(f"{cand['label']} {f.name:<28s} {cand['entry']['duration_sec']:5.2f}s  "
                  f"RMS {dsp.rms_db(w):6.1f} dB  peak {peak:.2f}")


if __name__ == "__main__":
    main()
