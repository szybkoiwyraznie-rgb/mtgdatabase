#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bramka g031 — PAKIET 5 zestawów (na życzenie właściciela: „większe paczki,
przynajmniej pięć zestawów naraz", 2026-09-25), po 3 kandydatów każdy.

Priorytety z resolver.py --survey (po zamknięciu g030/fabuł 433+506):
  1) koda-wspolnota      mood `wspolnota-wiez`             (34 fabuł) — fabuła 585
  2) koda-duma           mood `duma-majestat`              (31 fabuł) — fabuła 64
  3) koda-bezwzglednosc  mood `bezwzglednosc-drapieznosc`  (31 fabuł) — fabuła 437
  4) instr-cieplo        instrumentacja `cieplo-serdeczna`   (33 fabuł) — fabuła 206
  5) instr-metal         instrumentacja `metaliczno-mechaniczna` (30 fabuł) — fabuła 191

Kody (1-3): gesty autorskie, podgląd neutralny na b_piano_steinway (jak g026/g030).
Instrumenty (4-5): prawdziwe nagrania — VCSL (Marimba/Anvil/Brake Drum/Tubular
Bells, CC0 1.0, github.com/sgossner/VCSL) i VSCO-2-CE (F Horn/Clarinet sus,
CC0 1.0, github.com/sgossner/VSCO-2-CE), pobrane sparse-checkout do /tmp.

Definicje typów (taxonomy.json):
  wspolnota-wiez:           "Wspólnota, więź, wierność — koda łączy."
  duma-majestat:            "Duma, majestat, dostojeństwo, potęga — koda rośnie szeroko."
  bezwzglednosc-drapieznosc:"Bezwzględność, drapieżność, dominacja — koda jest zimna i ostateczna."
  cieplo-serdeczna:         "Ciepło i miękko: łagodne barwy, zaokrąglone ataki, organiczne ciepło."
  metaliczno-mechaniczna:   "Metal i mechanika: blachy, tryby, industrialne faktury, precyzyjne rytmy."
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import sig_audio as dsp  # noqa: E402
import coda_synth  # noqa: E402

GATE = REPO / "data" / "gates" / "g031"
CAND = GATE / "candidates"
NOTES_DIR = GATE / "instr_notes"

VCSL = Path("/tmp/vcsl_probe/Idiophones/Struck Idiophones")
VSCO = Path("/tmp/vsco_probe")

VCSL_SRC = {
    "title": "Versilian Community Sample Library (VCSL)",
    "author": "Sam Gossner / Versilian Studios + społeczność",
    "license": "CC0 1.0",
    "url": "https://github.com/sgossner/VCSL",
    "channel": "git clone sparse z github.com/sgossner/VCSL",
}
VSCO_SRC = {
    "title": "Versilian Studios Chamber Orchestra 2 CE (VSCO-2-CE)",
    "author": "Sam Gossner / Versilian Studios + społeczność",
    "license": "CC0 1.0",
    "url": "https://github.com/sgossner/VSCO-2-CE",
    "channel": "git clone sparse z github.com/sgossner/VSCO-2-CE",
}

NOTE_IDX = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
            "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
NOTE_RE = re.compile(r"^([A-G]#?)(-?\d+)$")


def note_token_to_midi(stem: str) -> int | None:
    """Szuka tokenu nuty (np. 'A#2', 'C4') między podkreślnikami nazwy pliku."""
    for tok in stem.split("_"):
        m = NOTE_RE.fullmatch(tok)
        if m:
            return NOTE_IDX[m.group(1)] + 12 * (int(m.group(2)) + 1)
    return None


# ============================================================== KODY (gesty)
GESTURE_ENTRIES = {
    "koda-wspolnota": {
        "story_id": "585", "typ": "wspolnota-wiez",
        "role": "jedyny klocek typu kody `wspolnota-wiez` (34 fabuły; slot a fabuły 585)",
        "gestures": {
            "g_bond_converge": {
                "label": "w.1", "semantic": "wspólnota — dystans, który zamyka się w jedność",
                "desc": "dwa oddalone głosy (tryton) najpierw brzmią osobno, potem oba "
                        "schodzą się w czystą oktawę — różnica staje się jednością",
                "notes": [
                    {"midi": 56, "on": 0.00, "off": 0.50, "vel": 0.45},
                    {"midi": 50, "on": 0.00, "off": 0.50, "vel": 0.45},
                    {"midi": 60, "on": 0.70, "off": 2.60, "vel": 0.55},
                    {"midi": 48, "on": 0.70, "off": 2.60, "vel": 0.50},
                ],
            },
            "g_bond_embrace": {
                "label": "w.2", "semantic": "wspólnota — uścisk równoległych głosów",
                "desc": "dwa głosy poruszają się razem w konsonansowych tercjach, "
                        "jak dwoje idących tym samym krokiem — ciepło, bez napięcia",
                "notes": [
                    {"midi": 60, "on": 0.00, "off": 0.90, "vel": 0.50},
                    {"midi": 64, "on": 0.00, "off": 0.90, "vel": 0.45},
                    {"midi": 56, "on": 0.85, "off": 2.60, "vel": 0.55},
                    {"midi": 60, "on": 0.85, "off": 2.60, "vel": 0.50},
                ],
            },
            "g_bond_echo": {
                "label": "w.3", "semantic": "wspólnota — wezwanie i odpowiedź, potem razem",
                "desc": "jeden głos woła, drugi odpowiada tuż po nim tą samą barwą, "
                        "na koniec oba trwają razem — więź potwierdzona",
                "notes": [
                    {"midi": 64, "on": 0.00, "off": 0.60, "vel": 0.55},
                    {"midi": 60, "on": 0.55, "off": 1.30, "vel": 0.50},
                    {"midi": 60, "on": 1.60, "off": 2.80, "vel": 0.45},
                    {"midi": 64, "on": 1.60, "off": 2.80, "vel": 0.40},
                ],
            },
        },
    },
    "koda-duma": {
        "story_id": "64", "typ": "duma-majestat",
        "role": "jedyny klocek typu kody `duma-majestat` (31 fabuł; slot a fabuły 64)",
        "gestures": {
            "g_pride_broadening": {
                "label": "d.1", "semantic": "duma — dwa kroki i rozstąpienie się na oścież",
                "desc": "dwa krótkie stąpnięcia w górę, potem rejestr rozstępuje się naraz "
                        "w dół i w górę — przestrzeń rośnie szeroko wokół jednego środka",
                "notes": [
                    {"midi": 60, "on": 0.00, "off": 0.45, "vel": 0.50},
                    {"midi": 68, "on": 0.40, "off": 0.85, "vel": 0.55},
                    {"midi": 48, "on": 0.80, "off": 2.60, "vel": 0.60},
                    {"midi": 84, "on": 0.80, "off": 2.60, "vel": 0.55},
                ],
            },
            "g_pride_ascent": {
                "label": "d.2", "semantic": "duma — wspinaczka do pełnej wysokości",
                "desc": "trzy kroki wspinają się oktawami do samego szczytu banku, "
                        "gdzie ląduje pełny, szeroki akord — koronacja",
                "notes": [
                    {"midi": 48, "on": 0.00, "off": 0.40, "vel": 0.55},
                    {"midi": 60, "on": 0.35, "off": 0.75, "vel": 0.60},
                    {"midi": 72, "on": 0.70, "off": 1.15, "vel": 0.65},
                    {"midi": 84, "on": 1.10, "off": 2.80, "vel": 0.70},
                    {"midi": 48, "on": 1.10, "off": 2.80, "vel": 0.50},
                ],
            },
            "g_pride_spread": {
                "label": "d.3", "semantic": "duma — środek trwa, ramiona się otwierają",
                "desc": "jedna centralna nuta trwa przez całą frazę, a wokół niej dokładane "
                        "są kolejne głosy w górę i w dół — gest otwierających się ramion",
                "notes": [
                    {"midi": 60, "on": 0.00, "off": 2.80, "vel": 0.50},
                    {"midi": 68, "on": 0.60, "off": 2.80, "vel": 0.50},
                    {"midi": 50, "on": 1.20, "off": 2.80, "vel": 0.50},
                    {"midi": 84, "on": 1.80, "off": 2.80, "vel": 0.55},
                ],
            },
        },
    },
    "koda-bezwzglednosc": {
        "story_id": "437", "typ": "bezwzglednosc-drapieznosc",
        "role": "jedyny klocek typu kody `bezwzglednosc-drapieznosc` (31 fabuł; slot a fabuły 437)",
        "gestures": {
            "g_ruthless_strike": {
                "label": "b.1", "semantic": "bezwzględność — jedno zimne, ostateczne uderzenie",
                "desc": "pojedynczy twardy dysonansowy akord (tryton), bardzo krótki, "
                        "bez wybrzmienia i bez odpowiedzi — cios i cisza",
                "notes": [
                    {"midi": 48, "on": 0.00, "off": 0.30, "vel": 0.80},
                    {"midi": 54, "on": 0.00, "off": 0.30, "vel": 0.75},
                ],
            },
            "g_ruthless_press": {
                "label": "b.2", "semantic": "bezwzględność — narastający nacisk i finalny cios",
                "desc": "trzy rosnące kroki napięcia, jak drapieżnik zamykający dystans, "
                        "kończy się jednym twardym, niskim ciosem — bez litości",
                "notes": [
                    {"midi": 56, "on": 0.00, "off": 0.50, "vel": 0.50},
                    {"midi": 60, "on": 0.45, "off": 0.95, "vel": 0.60},
                    {"midi": 64, "on": 0.85, "off": 1.30, "vel": 0.65},
                    {"midi": 48, "on": 1.25, "off": 1.55, "vel": 0.85},
                ],
            },
            "g_ruthless_verdict": {
                "label": "b.3", "semantic": "bezwzględność — dwa identyczne, chłodne wyroki",
                "desc": "dwa równe, twarde dysonansowe stuknięcia w równym odstępie — "
                        "bez eskalacji, bez emocji, tylko powtórzony wyrok",
                "notes": [
                    {"midi": 54, "on": 0.00, "off": 0.25, "vel": 0.80},
                    {"midi": 48, "on": 0.00, "off": 0.25, "vel": 0.75},
                    {"midi": 54, "on": 1.00, "off": 1.25, "vel": 0.85},
                    {"midi": 48, "on": 1.00, "off": 1.25, "vel": 0.80},
                ],
            },
        },
    },
}


def gesture_candidates(spec: dict) -> list[dict]:
    instruments = json.loads((REPO / "data/library/instruments.json").read_text(encoding="utf-8"))
    piano = next(e for e in instruments["entries"] if e["id"] == "b_piano_steinway")
    piano_abs = {**piano, "samples": {m: str(REPO / p) for m, p in piano["samples"].items()}}
    cands: list[dict] = []
    for gid, g in spec["gestures"].items():
        gesture = {"notes": g["notes"], "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}}}
        r = coda_synth.render_coda(gesture, piano_abs, seed=int(spec["story_id"]))
        for w in r.warnings:
            print(f"  ! {gid}: {w}")
        dsp.encode_mp3(CAND / f"{gid}.mp3", r.wave)
        cands.append({
            "label": g["label"],
            "title": g["semantic"].split("—", 1)[1].strip(),
            "file": f"candidates/{gid}.mp3",
            "desc": g["desc"],
            "source": "gest autorski; podgląd na b_piano_steinway (render neutralny)",
            "entry": {
                "id": gid,
                "semantic": g["semantic"],
                "desc": g["desc"],
                "notes": g["notes"],
                "delivery": {"humanize": {"timing_ms": 15, "vel": 0.04}},
                "instrument_tags": ["piano", "strings", "bells", "organ"],
                "semantics": {"type": spec["typ"], "traits": [], "bad_for": []},
            },
        })
        print(f"  {gid} zapisany")
    return cands


# ========================================================= INSTRUMENTY (audio)
def _load_bank(src_dir: Path, want_sub: str, keep_ext: str = ".wav") -> dict[int, Path]:
    bank: dict[int, Path] = {}
    for f in sorted(src_dir.glob(f"*{keep_ext}")):
        if want_sub not in f.stem:
            continue
        midi = note_token_to_midi(f.stem)
        if midi is not None:
            bank[midi] = f
    return bank


def _register_instrument(iid: str, label: str, title: str, semantic: str, desc: str,
                          traits: list[str], bad_for: list[str], src: dict, src_notes: str,
                          bank: dict[int, Path], demo_notes: list[dict],
                          family: str, out_subdir: str) -> dict:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    gate_sources: dict[str, str] = {}
    lib_samples: dict[str, str] = {}
    for midi, src_path in sorted(bank.items()):
        out_name = f"{iid}_{src_path.stem}.mp3"
        w, _ = dsp.load_any(src_path)
        dsp.encode_mp3(NOTES_DIR / out_name, dsp.cut(w, 0.0, 2.2))
        gate_sources[str(midi)] = f"instr_notes/{out_name}"
        lib_samples[str(midi)] = f"audio/library/instruments/{out_subdir}/{out_name}"
    inst_abs = {"samples": {m: str(NOTES_DIR / Path(p).name) for m, p in gate_sources.items()}}
    r = coda_synth.render_coda({"notes": demo_notes, "delivery": {}}, inst_abs, seed=31)
    for w in r.warnings:
        print(f"  ! demo {iid}: {w}")
    dsp.encode_mp3(CAND / f"{iid}_demo.mp3", r.wave)
    lo = dsp.midi_to_name(min(bank)) if bank else "?"
    hi = dsp.midi_to_name(max(bank)) if bank else "?"
    return {
        "label": label, "title": title,
        "file": f"candidates/{iid}_demo.mp3",
        "desc": f"{desc} — bank {len(bank)} nut {lo}–{hi}",
        "source": f"{src['title']} — {src['license']}",
        "entry": {
            "id": iid, "semantic": semantic, "family": family,
            "samples": lib_samples, "gate_sources": gate_sources,
            "semantics": {"type": "", "traits": traits, "bad_for": bad_for},
            "source": {**src, "notes": src_notes},
        },
    }


def instr_cieplo_candidates() -> list[dict]:
    typ = "cieplo-serdeczna"
    cands = []
    # o.1 — Marimba (VCSL): drewniany, ciepły mallet
    marimba_dir = VCSL / "Marimba"
    bank = _load_bank(marimba_dir, "_med_")
    demo = [
        {"midi": 36, "on": 0.00, "off": 0.55, "vel": 0.7},
        {"midi": 53, "on": 0.45, "off": 1.00, "vel": 0.7},
        {"midi": 60, "on": 0.90, "off": 1.45, "vel": 0.75},
        {"midi": 67, "on": 1.35, "off": 2.20, "vel": 0.7},
    ]
    cand = _register_instrument(
        "b_marimba_warm", "c.1", "marimba — drewniany, ciepły mallet",
        "drewniany rezonans marimby — ciepłe, zaokrąglone uderzenie",
        "miękkie uderzenie w drewniane płytki, ciepły rezonans bez metalicznego błysku — "
        "'lekko, drewniannie, pogodnie'",
        ["ciepły", "miękki", "drewniany", "organiczny"], ["ostry", "zimny", "metaliczny"],
        VCSL_SRC, "Marimba, dynamika 'med' (VCSL); bank 10 nut F1–F5", bank, demo,
        "idiophone-struck", "marimba_warm")
    cand["entry"]["semantics"]["type"] = typ
    cands.append(cand)
    # o.2 — French Horn sus (VSCO): ciepła miedź
    horn_dir = VSCO / "Brass" / "F Horn" / "sus"
    bank = _load_bank(horn_dir, "_v1_")
    demo = [
        {"midi": 34, "on": 0.00, "off": 0.75, "vel": 0.5},
        {"midi": 38, "on": 0.70, "off": 1.45, "vel": 0.5},
        {"midi": 45, "on": 1.40, "off": 2.10, "vel": 0.55},
        {"midi": 48, "on": 2.05, "off": 2.90, "vel": 0.5},
    ]
    cand = _register_instrument(
        "b_frenchhorn_warm", "c.2", "waltornia — ciepła, sustainowana miedź",
        "spokojny, sustainowany oddech waltorni — miękka, aksamitna miedź",
        "długie, ciepłe tony rogu bez ataku blachy — pełna, otulająca barwa",
        ["ciepły", "miękki", "aksamitny", "sustain"], ["ostry", "metaliczny", "perkusyjny"],
        VSCO_SRC, "F Horn, artykulacja 'sus', wariacja v1 (VSCO-2-CE); bank 11 nut A0–F4",
        bank, demo, "aerophone-brass", "frenchhorn_warm")
    cand["entry"]["semantics"]["type"] = typ
    cands.append(cand)
    # o.3 — Clarinet susLong (VSCO): ciepły, okrągły drewniany dęty
    clar_dir = VSCO / "Woodwinds" / "Clarinet" / "susLong"
    bank = _load_bank(clar_dir, "_v1_")
    demo = [
        {"midi": 46, "on": 0.00, "off": 0.70, "vel": 0.5},
        {"midi": 50, "on": 0.65, "off": 1.35, "vel": 0.5},
        {"midi": 58, "on": 1.30, "off": 2.00, "vel": 0.55},
        {"midi": 62, "on": 1.95, "off": 2.80, "vel": 0.5},
    ]
    cand = _register_instrument(
        "b_clarinet_warm", "c.3", "klarnet — okrągły, ciepły drewniany dęty",
        "gładki, sustainowany klarnet w rejestrze piersiowym — okrągły, bez świstu trzciny",
        "ciepły, zaokrąglony ton drewnianego dętego — miękka alternatywa dla miedzi",
        ["ciepły", "miękki", "okrągły", "sustain"], ["ostry", "metaliczny", "chłodny"],
        VSCO_SRC, "Clarinet, artykulacja 'susLong', wariacja v1 (VSCO-2-CE); bank 11 nut D2–F#5",
        bank, demo, "aerophone-reed", "clarinet_warm")
    cand["entry"]["semantics"]["type"] = typ
    cands.append(cand)
    return cands


def instr_metal_candidates() -> list[dict]:
    typ = "metaliczno-mechaniczna"
    cands = []
    # m.1 — Anvil (VCSL): surowe, industrialne uderzenie kowadła (bez realnej wysokości)
    anvil_dir = VCSL / "Anvil"
    files = {36: anvil_dir / "Anvil_Hit1_v1_rr1_Mid.wav",
             48: anvil_dir / "Anvil_Hit2_v2_rr1_Mid.wav",
             60: anvil_dir / "Anvil_Hit3_v3_rr1_Mid.wav"}
    demo = [
        {"midi": 36, "on": 0.00, "off": 0.25, "vel": 0.8},
        {"midi": 48, "on": 0.35, "off": 0.60, "vel": 0.8},
        {"midi": 36, "on": 0.70, "off": 0.95, "vel": 0.75},
        {"midi": 60, "on": 1.10, "off": 1.40, "vel": 0.85},
    ]
    cand = _register_instrument(
        "b_anvil_metal", "m.1", "kowadło — surowe, industrialne uderzenie metalu",
        "trzy realne kolory uderzenia w kowadło (bez tonalnej wysokości — czysta faktura)",
        "surowy metaliczny brzęk kucia, zero tonu muzycznego — najbardziej dosłowny 'metal'",
        ["metaliczny", "mechaniczny", "surowy", "przemysłowy"],
        ["ciepły", "organiczny", "miękki", "melodyjny"],
        VCSL_SRC, "Anvil, trzy kolory uderzenia Hit1/Hit2/Hit3 (VCSL); bank bez realnej wysokości "
                  "(3 barwy przypisane umownym numerom MIDI)", files, demo,
        "idiophone-struck", "anvil_metal")
    cand["entry"]["semantics"]["type"] = typ
    cands.append(cand)
    # m.2 — Brake Drum, Hammer (VCSL): mechaniczna część samochodu jako instrument
    bd_dir = VCSL / "Brake Drum"
    files = {36: bd_dir / "BrakeDrum1_Hammer_v1_rr1_Mid.wav",
             48: bd_dir / "BrakeDrum1_Hammer_v2_rr1_Mid.wav",
             60: bd_dir / "BrakeDrum1_Hammer_v3_rr1_Mid.wav"}
    demo = [
        {"midi": 36, "on": 0.00, "off": 0.30, "vel": 0.75},
        {"midi": 60, "on": 0.30, "off": 0.60, "vel": 0.8},
        {"midi": 48, "on": 0.75, "off": 1.05, "vel": 0.7},
        {"midi": 36, "on": 1.10, "off": 1.40, "vel": 0.8},
    ]
    cand = _register_instrument(
        "b_brakedrum_metal", "m.2", "tarcza hamulcowa — mechaniczny, warsztatowy metal",
        "prawdziwa część samochodu (tarcza hamulcowa) uderzana młotkiem — dosłownie mechaniczne",
        "krótki, suchy metaliczny brzęk warsztatu — bardziej 'techniczny' niż muzyczny kowal",
        ["metaliczny", "mechaniczny", "warsztatowy", "suchy"],
        ["ciepły", "organiczny", "miękki", "melodyjny"],
        VCSL_SRC, "Brake Drum 1, artykulacja Hammer, wariacje v1/v2/v3 (VCSL); bank bez realnej "
                  "wysokości (3 barwy przypisane umownym numerom MIDI)", files, demo,
        "idiophone-struck", "brakedrum_metal")
    cand["entry"]["semantics"]["type"] = typ
    cands.append(cand)
    # m.3 — Tubular Bells 1 (VCSL): metalowe, ale tonalne — kontrast dla m.1/m.2
    tb_dir = VCSL / "Tubular Bells 1"
    bank = {}
    for f in sorted(tb_dir.glob("*.wav")):
        if "_ff_" not in f.stem and "_fff_" not in f.stem:
            continue
        midi = note_token_to_midi(f.stem)
        if midi is not None:
            bank[midi] = f
    demo = [
        {"midi": 50, "on": 0.00, "off": 0.80, "vel": 0.7},
        {"midi": 52, "on": 0.70, "off": 1.50, "vel": 0.7},
        {"midi": 54, "on": 1.40, "off": 2.20, "vel": 0.75},
        {"midi": 56, "on": 2.10, "off": 3.00, "vel": 0.7},
    ]
    cand = _register_instrument(
        "b_tubularbells_metal", "m.3", "dzwony rurowe — metaliczne, ale tonalne",
        "całotonowy bieg po dzwonach rurowych, dynamika ff — metal z melodią",
        "jedyny tonalny kandydat metalu: prawdziwe dzwony rurowe, jasne i rezonujące",
        ["metaliczny", "mechaniczny", "dzwoniący", "rezonujący"],
        ["ciepły", "organiczny", "miękki", "stłumiony"],
        VCSL_SRC, "Tubular Bells 1, dynamika ff/fff (VCSL); bank 8 nut D3–E4 (skala całotonowa)",
        bank, demo, "idiophone-struck", "tubularbells_metal")
    cand["entry"]["semantics"]["type"] = typ
    cands.append(cand)
    return cands


def main() -> None:
    CAND.mkdir(parents=True, exist_ok=True)
    entries = []
    for slug, spec in GESTURE_ENTRIES.items():
        entries.append({"slug": slug, "kind": "gestures", "role": spec["role"],
                         "candidates": gesture_candidates(spec)})
    entries.append({"slug": "instr-cieplo", "kind": "instruments",
                     "role": "jedyny klocek typu instrumentacji `cieplo-serdeczna` "
                             "(33 fabuły; slot b fabuły 206)",
                     "candidates": instr_cieplo_candidates()})
    entries.append({"slug": "instr-metal", "kind": "instruments",
                     "role": "jedyny klocek typu instrumentacji `metaliczno-mechaniczna` "
                             "(30 fabuł; slot b fabuły 191)",
                     "candidates": instr_metal_candidates()})
    manifest = {
        "id": "g031",
        "created": "2026-09-25",
        "note": "PAKIET 5 zestawów naraz (na życzenie właściciela po g030: „większe paczki, "
                "przynajmniej pięć zestawów\"). 3 kody autorskie (mood: wspólnota-więź, "
                "duma-majestat, bezwzględność-drapieżność — podgląd na b_piano_steinway) + "
                "2 zestawy prawdziwych instrumentów (instrumentacja: ciepło-serdeczna — "
                "marimba/waltornia/klarnet; metaliczno-mechaniczna — kowadło/tarcza hamulcowa/"
                "dzwony rurowe), wszystko VCSL/VSCO-2-CE CC0 1.0. Anchory: fabuły 585, 64, 437, "
                "206, 191 (każda miała dokładnie jeden brak — reszta obsadzona przez resolver).",
        "entries": entries,
    }
    (GATE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest g031 zapisany ({len(manifest['entries'])} wpisów)")


if __name__ == "__main__":
    main()
