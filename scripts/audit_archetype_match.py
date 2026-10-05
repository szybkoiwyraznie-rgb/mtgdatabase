#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audyt rozpoznawalności: czy sample brzmi jak ARCHETYP, nie jak tekstura.

Dotychczasowe audyty mierzyły jakość realizacji (głośność, pasmo, cisza) i
zgodność z grubą klasą (`metal`, `woda`, `ogień`). Żaden nie odpowiadał na
pytanie właściciela: „czy z zamkniętymi oczami wiem, że to ta karta?”.
Spłukiwanie toalety i wytrysk oazy to dla audytu semantycznego ta sama woda —
oba przechodzą z 0 pkt, a oba są bezużyteczne jako sygnatura karty.

Ten skrypt wprowadza **archetypy**: dźwięki, które mają własną, kulturowo
utrwaloną tożsamość akustyczną — ryk bestii, krakanie, dzwon, wybuch, chór,
muzyka ludowa, silnik wojennej machiny. Każdy archetyp ma mierzalny kontrakt:
co MUSI być prawdą w sygnale, jeśli sample naprawdę jest tym, co deklaruje
scenariusz.

Kontrakt jest celowo o archetyp, nie o fabułę: `creature_roar` musi być
harmoniczny, niski i trwać, bo ryk bez harmonicznego tonu i bez czasu trwania
jest sykaniem — czyli dokładnie tym, na co właściciel się skarżył.

Deklaracja w `data/samples/scenarios.jsonl`:

    {"story_id": "396", "archetype": "creature_roar", ...}

Wpisy bez pola `archetype` są pomijane — skrypt nie zgaduje archetypu z tekstu,
bo zgadywanie to źródło pierwotnego problemu.

Użycie:
    python scripts/audit_archetype_match.py \
        --audit data/samples/audio-audit-latest.json \
        --json data/samples/archetype-match.json \
        --markdown docs/audits/<data>-archetype-match.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from audit_semantic_match import extra_features  # noqa: E402

# --------------------------------------------------------------------------
# Kontrakty archetypów
# --------------------------------------------------------------------------
# Każdy warunek: (metryka, operator, wartość, waga, opis po polsku).
# Operator: ">=", "<=", "between". Suma wag naruszeń daje punktację:
# 0 = archetyp trafiony, <2 = prawdopodobnie trafiony, >=2 = nie trafiony.
CONTRACTS: dict[str, dict] = {
    "creature_roar": {
        "label": "ryk / porykiwanie dużego zwierzęcia",
        "checks": [
            ("voiced_fraction", ">=", 0.30, 1.5, "ryk musi być harmoniczny (voiced)"),
            ("spectral_flatness", "<=", 0.15, 1.5, "ryk nie może być szumem"),
            ("spectral_centroid_hz", "between", (150.0, 1600.0), 1.0, "ryk siedzi w niskim środku pasma"),
            ("low_all", ">=", 0.45, 1.0, "ryk ma ciało w dole pasma"),
            ("decay_s", ">=", 0.40, 1.0, "ryk musi trwać, nie kliknąć"),
        ],
    },
    "creature_cackle": {
        "label": "chichot / pokrzykiwanie stworzenia",
        "checks": [
            ("onset_count", ">=", 3, 1.5, "chichot to seria wybuchów, nie jeden dźwięk"),
            ("spectral_centroid_hz", "between", (700.0, 4500.0), 1.0, "chichot jest ostry i wysoki"),
            ("mod_peak_hz", "between", (2.5, 14.0), 1.0, "chichot pulsuje w tempie śmiechu"),
            ("content_rel_s", ">=", 1.00, 1.0, "chichot musi potrwać"),
        ],
    },
    "undead_groan": {
        "label": "jęk / pomruk nieumarłego",
        "checks": [
            ("spectral_centroid_hz", "between", (120.0, 1000.0), 1.5, "jęk jest niski"),
            ("decay_s", ">=", 0.60, 1.5, "jęk się ciągnie"),
            ("sustain_ratio", ">=", 0.25, 1.0, "jęk trzyma poziom, nie gaśnie od razu"),
            ("low_all", ">=", 0.55, 1.0, "jęk ma ciało w dole"),
            ("spectral_flatness", "<=", 0.40, 0.5, "jęk nie jest czystym szumem"),
        ],
    },
    "beast_screech": {
        "label": "wrzask / pisk potwora",
        "checks": [
            ("crest_db", ">=", 12.0, 1.5, "wrzask ma gwałtowny atak"),
            ("attack_s", "<=", 0.15, 1.0, "wrzask uderza od razu"),
            ("spectral_centroid_hz", "between", (600.0, 4500.0), 1.0, "wrzask jest ostry"),
            ("high_all", ">=", 0.20, 1.0, "wrzask ma energię w górze"),
        ],
    },
    "war_machine": {
        "label": "silnik i mechanizm wojennej machiny",
        "checks": [
            ("low_all", ">=", 0.35, 1.5, "machina dudni dołem"),
            ("spectral_centroid_hz", "<=", 2600.0, 1.0, "machina nie jest cienka"),
            ("onset_count", ">=", 2, 1.0, "machina ma rytmiczne uderzenia"),
            ("content_rel_s", ">=", 1.50, 1.0, "machina pracuje, nie stuka raz"),
        ],
    },
    "psychic_shriek": {
        "label": "przenikliwy jęk / uderzenie psychiczne",
        "checks": [
            ("attack_s", "<=", 0.10, 1.5, "uderzenie psychiczne jest natychmiastowe"),
            ("tonal_frame_fraction", ">=", 0.30, 1.5, "to ton, nie szum"),
            ("spectral_centroid_hz", "between", (1200.0, 7000.0), 1.0, "jęk jest wysoki i przenikliwy"),
            ("crest_db", ">=", 10.0, 0.5, "jęk ma szczyt"),
        ],
    },
    "forest_birdsong": {
        "label": "śpiew ptaków",
        "checks": [
            ("onset_count", ">=", 4, 1.5, "ptaki to wiele zawołań"),
            ("spectral_centroid_hz", "between", (1500.0, 6500.0), 1.5, "śpiew ptaków jest wysoki"),
            ("tonal_frame_fraction", ">=", 0.25, 1.0, "zawołania ptaków są tonalne"),
            ("mod_peak_hz", "between", (3.0, 22.0), 1.0, "trele są szybkie"),
        ],
    },
    "robot_servo": {
        "label": "serwo i mechanizm robota",
        "checks": [
            ("tonal_frame_fraction", ">=", 0.35, 1.5, "serwo trzyma ton"),
            ("f0_semitone_std", "<=", 4.0, 1.0, "ton serwa jest stabilny"),
            ("onset_count", ">=", 2, 1.0, "robot klika i pracuje"),
            ("sustain_ratio", ">=", 0.20, 0.5, "serwo pracuje ciągiem"),
        ],
    },
    "arcane_choir": {
        "label": "chór / zaświatowy śpiew bez słów",
        "checks": [
            ("tonal_frame_fraction", ">=", 0.45, 1.5, "chór jest harmoniczny"),
            ("voiced_fraction", ">=", 0.25, 1.5, "chór ma wyraźną wysokość"),
            ("sustain_ratio", ">=", 0.35, 1.0, "chór płynie, nie pulsuje"),
            ("decay_s", ">=", 0.80, 1.0, "chór wybrzmiewa"),
            ("spectral_centroid_hz", "between", (250.0, 2800.0), 1.0, "chór siedzi w środku pasma"),
        ],
    },
    "folk_music": {
        "label": "muzyka ludowa / taneczna",
        "checks": [
            ("tonal_frame_fraction", ">=", 0.30, 1.5, "melodia jest harmoniczna"),
            ("f0_semitone_std", ">=", 2.0, 1.5, "melodia zmienia wysokość"),
            ("onset_count", ">=", 4, 1.0, "taniec ma rytm"),
            ("mod_peak_hz", "between", (1.2, 6.0), 1.0, "rytm taneczny 1–6 Hz"),
            ("content_rel_s", ">=", 2.00, 1.0, "muzyka musi potrwać"),
        ],
    },
    "earth_rumble": {
        "label": "grzmot ziemi / osuwisko skalne",
        "checks": [
            ("low_all", ">=", 0.50, 1.5, "grzmot ziemi jest w dole pasma"),
            ("spectral_centroid_hz", "<=", 900.0, 1.0, "grzmot ziemi jest niski"),
            ("decay_s", ">=", 0.80, 1.0, "grzmot się toczy"),
            ("content_rel_s", ">=", 1.50, 1.0, "grzmot trwa"),
            ("mid_up", ">=", 0.10, 1.0,
             "grzmot musi być słyszalny też na małych głośnikach, nie sam infrabas"),
        ],
    },
    "heavy_impact": {
        "label": "potężne uderzenie / upadek ciała",
        "checks": [
            ("crest_db", ">=", 14.0, 1.5, "uderzenie ma ostry szczyt"),
            ("attack_s", "<=", 0.15, 1.0, "uderzenie jest natychmiastowe"),
            ("decay_s", "<=", 1.40, 1.0, "uderzenie gaśnie, nie ciągnie się"),
            ("low_all", ">=", 0.25, 0.5, "uderzenie ma masę"),
        ],
    },
    "volcanic_eruption": {
        "label": "wybuch wulkanu / lawy",
        "checks": [
            ("low_all", ">=", 0.35, 1.5, "erupcja ma masę w dole"),
            ("crest_db", ">=", 12.0, 1.0, "erupcja uderza"),
            ("spectral_flatness", ">=", 0.04, 1.0, "erupcja jest szumowa, nie tonalna"),
            ("decay_s", ">=", 0.80, 1.0, "erupcja się toczy"),
            ("content_rel_s", ">=", 1.50, 1.0, "erupcja trwa"),
        ],
    },

    # ----------------------------------------------------------------------
    # Tranche 2 (2026-10-05): archetypy do triage'u całego katalogu.
    # Progi v0 — ustawione względem rozkładu korpusu z audytu
    # `audio-audit-latest.json` (553 pliki): centroid p50 2,66 kHz / p75 5,84 kHz,
    # low_all p50 0,034 / p75 0,204, flatness p50 0,097, decay_s p50 0,21 s,
    # content_rel_s p50 2,09 s, onset_count p50 5, mod_peak p50 1,87 Hz.
    # Warunki opisują tożsamość archetypu (dzwon musi dzwonić, miecz musi
    # błyszczeć górą), a nie średnią korpusu — dlatego wiele kart je obleje.
    # To lista priorytetów do odsłuchu, nie wyrok: kalibracja należy do ucha
    # właściciela.
    # ----------------------------------------------------------------------
    "temple_bell": {
        "label": "dzwon / dzwonek / gong",
        "checks": [
            ("tonal_frame_fraction", ">=", 0.50, 1.5, "dzwon jest tonalny, nie szumowy"),
            ("decay_s", ">=", 0.80, 1.5, "dzwon wybrzmiewa"),
            ("spectral_centroid_hz", "between", (400.0, 3000.0), 1.0, "dzwon siedzi w środku pasma"),
            ("sustain_ratio", ">=", 0.20, 1.0, "dzwon trzyma poziom"),
            ("content_rel_s", ">=", 1.50, 1.0, "dzwon musi potrwać"),
        ],
    },
    "sword_clash": {
        "label": "starcie stali / cios miecza",
        "checks": [
            ("crest_db", ">=", 18.0, 1.0, "cios stali jest ostry"),
            ("attack_s", "<=", 0.05, 1.0, "stal uderza natychmiast"),
            ("spectral_centroid_hz", ">=", 2500.0, 1.0, "stal błyszczy górą pasma"),
            ("high_all", ">=", 0.30, 1.0, "cios ma energię w górze"),
            ("spectral_flatness", ">=", 0.05, 0.5, "uderzenie ma szumowy transient"),
        ],
    },
    "anvil_strike": {
        "label": "uderzenie młota w kowadło",
        "checks": [
            ("crest_db", ">=", 19.0, 1.0, "młot uderza twardo"),
            ("spectral_centroid_hz", "between", (1500.0, 7000.0), 1.0, "kowadło dzwoni wysoko"),
            ("onset_count", ">=", 2, 1.0, "kucie to seria uderzeń"),
            ("decay_s", "<=", 1.00, 0.5, "uderzenie kowadła nie ciągnie się jak dzwon"),
        ],
    },
    "arrow_flight": {
        "label": "strzała / świst pocisku",
        "checks": [
            ("attack_s", "<=", 0.10, 1.0, "strzała startuje od razu"),
            ("decay_s", "<=", 0.80, 1.0, "przelot jest krótki"),
            ("spectral_flatness", ">=", 0.10, 1.0, "świst jest szumowy"),
            ("spectral_centroid_hz", "between", (800.0, 6000.0), 1.0, "świst siedzi w środku i górze"),
        ],
    },
    "thunder_clap": {
        "label": "grzmot / uderzenie pioruna",
        "checks": [
            ("low_all", ">=", 0.50, 1.5, "grzmot jest w dole pasma"),
            ("spectral_centroid_hz", "<=", 800.0, 1.0, "grzmot jest niski"),
            ("crest_db", ">=", 18.0, 1.0, "grzmot uderza"),
            ("decay_s", ">=", 0.50, 1.0, "grzmot się toczy"),
        ],
    },
    "heavy_footsteps": {
        "label": "ciężkie kroki / kopyta",
        "checks": [
            ("onset_count", ">=", 3, 1.5, "kroki to seria uderzeń"),
            ("ioi_cv", "<=", 0.60, 1.0, "kroki mają równy rytm"),
            ("low_all", ">=", 0.15, 1.0, "ciężki krok ma masę w dole"),
            ("spectral_centroid_hz", "<=", 2000.0, 1.0, "krok nie jest cienki"),
        ],
    },
    "wing_flutter": {
        "label": "trzepot skrzydeł",
        "checks": [
            ("onset_count", ">=", 6, 1.5, "skrzydła biją wielokrotnie"),
            ("mod_peak_hz", "between", (4.0, 20.0), 1.0, "trzepot pulsuje w tempie machania"),
            ("spectral_centroid_hz", "between", (800.0, 6000.0), 1.0, "trzepot jest szelestem w środku pasma"),
        ],
    },
    "fire_crackle": {
        "label": "trzask ognia / żaru",
        "checks": [
            ("spectral_flatness", ">=", 0.10, 1.5, "ogień jest szumowy"),
            ("onset_count", ">=", 8, 1.5, "ogień strzela wieloma trzaskami"),
            ("spectral_centroid_hz", "between", (1000.0, 6000.0), 1.0, "trzaski są jasne"),
            ("content_rel_s", ">=", 1.50, 1.0, "ogień trwa"),
        ],
    },
    "water_splash": {
        "label": "plusk / uderzenie w wodę",
        "checks": [
            ("spectral_flatness", ">=", 0.08, 1.5, "plusk jest szumowy"),
            ("high_all", ">=", 0.25, 1.0, "plusk chlapie górą"),
            ("crest_db", ">=", 15.0, 1.0, "plusk ma szczyt"),
            ("attack_s", "<=", 0.10, 1.0, "plusk zaczyna się od razu"),
        ],
    },
    "liquid_pour": {
        "label": "lanie cieczy / bulgot mikstury",
        "checks": [
            ("sustain_ratio", ">=", 0.30, 1.0, "lanie jest ciągłe"),
            ("spectral_flatness", ">=", 0.05, 1.0, "ciecz szumi"),
            ("spectral_centroid_hz", "between", (500.0, 4000.0), 1.0, "ciecz siedzi w środku pasma"),
            ("content_rel_s", ">=", 1.50, 1.0, "lanie trwa"),
        ],
    },
    "door_creak": {
        "label": "skrzypienie drewna / zawiasów",
        "checks": [
            ("tonal_frame_fraction", ">=", 0.30, 1.5, "skrzypienie jest tonalne"),
            ("mod_peak_hz", "between", (2.0, 12.0), 1.0, "skrzypienie faluje"),
            ("spectral_centroid_hz", "between", (700.0, 4000.0), 1.0, "skrzypienie siedzi w środku"),
            ("decay_s", ">=", 0.30, 1.0, "skrzypienie się ciągnie"),
        ],
    },
    "stone_slide": {
        "label": "osuwisko / tarcie skał",
        "checks": [
            ("low_all", ">=", 0.25, 1.5, "skały mają masę w dole"),
            ("spectral_centroid_hz", "<=", 2000.0, 1.0, "skały są niskie"),
            ("decay_s", ">=", 0.50, 1.0, "osuwisko się toczy"),
            ("content_rel_s", ">=", 1.50, 1.0, "osuwisko trwa"),
        ],
    },
    "chain_rattle": {
        "label": "grzechot łańcuchów / kolczugi",
        "checks": [
            ("onset_count", ">=", 6, 1.5, "łańcuch dzwoni wieloma ogniwami"),
            ("spectral_centroid_hz", ">=", 2000.0, 1.0, "łańcuch jest jasny"),
            ("decay_s", "<=", 1.00, 1.0, "ogniwa gasną szybko"),
        ],
    },
    "magic_shimmer": {
        "label": "magiczne migotanie / aureola",
        "checks": [
            ("high_all", ">=", 0.40, 1.5, "magia świeci górą pasma"),
            ("tonal_frame_fraction", ">=", 0.30, 1.0, "migotanie jest tonalne"),
            ("sustain_ratio", ">=", 0.30, 1.0, "magia płynie, nie klika"),
            ("attack_s", ">=", 0.10, 1.0, "magia narasta, nie uderza"),
        ],
    },
    "insect_swarm": {
        "label": "rój owadów / bzykanie",
        "checks": [
            ("tonal_frame_fraction", ">=", 0.30, 1.5, "bzykanie jest harmoniczne"),
            ("sustain_ratio", ">=", 0.40, 1.0, "rój brzmi ciągiem"),
            ("spectral_centroid_hz", "between", (1000.0, 6000.0), 1.0, "bzykanie jest wysokie"),
            ("content_rel_s", ">=", 1.50, 1.0, "rój trwa"),
        ],
    },
    "horn_call": {
        "label": "róg bojowy / sygnał dęty",
        "checks": [
            ("voiced_fraction", ">=", 0.30, 1.5, "róg jest harmoniczny"),
            ("tonal_frame_fraction", ">=", 0.50, 1.0, "róg jest tonalny"),
            ("spectral_centroid_hz", "between", (200.0, 1500.0), 1.0, "róg siedzi nisko w środku"),
            ("decay_s", ">=", 0.60, 1.0, "sygnał rogu wybrzmiewa"),
        ],
    },
    "glass_shatter": {
        "label": "tłuczenie szkła / kryształu",
        "checks": [
            ("crest_db", ">=", 18.0, 1.0, "szkło pęka gwałtownie"),
            ("spectral_centroid_hz", ">=", 3000.0, 1.5, "szkło dzwoni bardzo wysoko"),
            ("onset_count", ">=", 5, 1.0, "odłamki dzwonią serią"),
            ("spectral_flatness", ">=", 0.05, 0.5, "tłuczenie ma szum"),
        ],
    },
    "wind_gust": {
        "label": "podmuch wiatru",
        "checks": [
            ("sustain_ratio", ">=", 0.30, 1.0, "podmuch płynie"),
            ("spectral_flatness", ">=", 0.05, 1.0, "wiatr jest szumowy"),
            ("attack_s", ">=", 0.30, 1.0, "podmach narasta"),
            ("spectral_centroid_hz", "between", (300.0, 3000.0), 1.0, "wiatr siedzi w środku pasma"),
        ],
    },
    "bone_snap": {
        "label": "trzask kości / łamanie",
        "checks": [
            ("crest_db", ">=", 18.0, 1.0, "kość pęka gwałtownie"),
            ("attack_s", "<=", 0.05, 1.0, "pęknięcie jest natychmiastowe"),
            ("spectral_centroid_hz", "between", (500.0, 4000.0), 1.0, "trzask kości jest suchy i średni"),
            ("decay_s", "<=", 0.60, 1.0, "trzask gaśnie szybko"),
        ],
    },
    "mechanism_click": {
        "label": "zegarowy mechanizm / zamek / zapadka",
        "checks": [
            ("onset_count", ">=", 3, 1.5, "mechanizm klika serią"),
            ("crest_db", ">=", 16.0, 1.0, "klik jest ostry"),
            ("spectral_centroid_hz", "between", (800.0, 6000.0), 1.0, "klik jest suchy i jasny"),
            ("ioi_cv", "<=", 0.80, 1.0, "mechanizm ma rytm"),
        ],
    },
    "whip_crack": {
        "label": "trzask bicza",
        "checks": [
            ("crest_db", ">=", 20.0, 1.5, "bicz strzela bardzo ostro"),
            ("attack_s", "<=", 0.03, 1.0, "bicz pęka natychmiast"),
            ("spectral_centroid_hz", ">=", 2000.0, 1.0, "trzask bicza jest jasny"),
            ("decay_s", "<=", 0.50, 1.0, "trzask jest krótki"),
        ],
    },
    "plate_clank": {
        "label": "pancerz / płyty stalowe",
        "checks": [
            ("crest_db", ">=", 17.0, 1.0, "płyty pancerza uderzają ostro"),
            ("spectral_centroid_hz", "between", (1000.0, 6000.0), 1.0, "stal pancerza jest jasna"),
            ("onset_count", ">=", 2, 1.0, "pancerz dzwoni kilkoma płytami"),
            ("spectral_flatness", ">=", 0.03, 1.0, "brzęk stali ma szum"),
            ("decay_s", "<=", 1.20, 0.5, "płyty gasną szybciej niż dzwon"),
        ],
    },
    "electric_zap": {
        "label": "wyładowanie / iskra",
        "checks": [
            ("attack_s", "<=", 0.03, 1.5, "wyładowanie jest natychmiastowe"),
            ("crest_db", ">=", 18.0, 1.0, "wyładowanie ma ostry szczyt"),
            ("spectral_centroid_hz", ">=", 2500.0, 1.0, "iskra jest bardzo jasna"),
            ("spectral_flatness", ">=", 0.10, 1.0, "wyładowanie jest szumowe"),
            ("decay_s", "<=", 0.80, 1.0, "iskra gaśnie szybko"),
        ],
    },
    "steam_hiss": {
        "label": "syk pary / gazu",
        "checks": [
            ("spectral_flatness", ">=", 0.15, 1.5, "syk jest szumem"),
            ("high_all", ">=", 0.30, 1.0, "syk siedzi w górze pasma"),
            ("sustain_ratio", ">=", 0.30, 1.0, "syk jest ciągły"),
            ("content_rel_s", ">=", 1.50, 1.0, "syk trwa"),
        ],
    },
}

# metryki pochodne z pasm audytu sygnałowego
DERIVED = {
    "low_all": lambda m: m["bands"]["sub_0_60"] + m["bands"]["low_60_250"],
    "high_all": lambda m: m["bands"]["high_2k_8k"] + m["bands"]["air_8k_plus"],
    "mid_up": lambda m: m["bands"]["mid_250_2k"] + m["bands"]["high_2k_8k"] + m["bands"]["air_8k_plus"],
}


def metric(metrics: dict, name: str):
    if name in DERIVED:
        return DERIVED[name](metrics)
    return metrics.get(name)


def evaluate(archetype: str, metrics: dict) -> tuple[float, list[dict]]:
    contract = CONTRACTS.get(archetype)
    if contract is None:
        return 0.0, [{"reason": f"nieznany archetyp {archetype!r}", "weight": 0.0}]
    broken: list[dict] = []
    for key, op, want, weight, why in contract["checks"]:
        got = metric(metrics, key)
        if got is None:
            broken.append({"check": key, "reason": f"brak metryki {key}", "weight": weight})
            continue
        ok = (
            (op == ">=" and got >= want)
            or (op == "<=" and got <= want)
            or (op == "between" and want[0] <= got <= want[1])
        )
        if not ok:
            shown = f"{got:.3f}" if isinstance(got, float) else str(got)
            target = f"{want[0]}–{want[1]}" if op == "between" else f"{op} {want}"
            broken.append({"check": key, "reason": f"{why} ({key}={shown}, oczekiwane {target})",
                           "weight": weight})
    return round(sum(b["weight"] for b in broken), 2), broken


def verdict(score: float) -> str:
    if score == 0.0:
        return "trafiony"
    if score < 2.0:
        return "prawdopodobnie"
    return "nie trafiony"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, default=ROOT / "data/samples/audio-audit-latest.json")
    ap.add_argument("--scenarios", type=Path, default=ROOT / "data/samples/scenarios.jsonl")
    ap.add_argument("--samples-dir", type=Path, default=ROOT / "audio/samples")
    ap.add_argument("--json", type=Path, dest="json_out")
    ap.add_argument("--markdown", type=Path)
    args = ap.parse_args()

    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    files = {str(f["id"]): f for f in audit.get("files", [])}
    rows = [json.loads(l) for l in args.scenarios.read_text(encoding="utf-8").splitlines() if l.strip()]

    results = []
    for row in rows:
        archetype = row.get("archetype")
        sid = str(row["story_id"])
        if not archetype or sid not in files:
            continue
        metrics = dict(files[sid])
        path = args.samples_dir / f"{sid}.mp3"
        if path.exists():
            metrics.update(extra_features(path))
        score, broken = evaluate(archetype, metrics)
        results.append({
            "id": sid, "title": row.get("title"), "archetype": archetype,
            "archetype_label": CONTRACTS.get(archetype, {}).get("label", archetype),
            "score": score, "verdict": verdict(score), "violations": broken,
        })

    results.sort(key=lambda r: (-r["score"], int(r["id"])))
    by_verdict: dict[str, int] = {}
    for r in results:
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1

    out = {
        "audit": str(args.audit),
        "checked": len(results),
        "by_verdict": by_verdict,
        "results": results,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"JSON: {args.json_out}")

    print(f"sprawdzono {len(results)} sampli z zadeklarowanym archetypem: {by_verdict}")
    for r in results[:20]:
        why = "; ".join(b["reason"] for b in r["violations"]) or "kontrakt spełniony"
        print(f"  {r['score']:>4} {r['id']:>4} {r['archetype']:<18} {r['title'][:26]:<26} {why[:80]}")

    if args.markdown:
        lines = [
            "# Audyt rozpoznawalności — czy sample brzmi jak archetyp",
            "",
            f"Sprawdzono **{len(results)}** sampli z zadeklarowanym polem `archetype`.",
            "",
            "| Wynik | ID | Karta | Archetyp | Co nie gra |",
            "|---|---|---|---|---|",
        ]
        for r in results:
            why = "; ".join(b["reason"] for b in r["violations"]) or "—"
            lines.append(f"| {r['score']} | {r['id']} | {r['title']} | `{r['archetype']}` "
                         f"({r['archetype_label']}) | {why} |")
        lines += [
            "",
            f"Werdykty: {by_verdict}",
            "",
            "0 pkt = kontrakt archetypu spełniony w całości. ≥ 2 pkt = sample nie jest tym,",
            "co deklaruje scenariusz, i nie da się go rozpoznać z zamkniętymi oczami.",
            "",
        ]
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text("\n".join(lines), encoding="utf-8")
        print(f"Markdown: {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
