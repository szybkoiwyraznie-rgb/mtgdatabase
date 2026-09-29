#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audyt semantyczny: czy sample brzmi jak to, co obiecuje scenariusz.

Wszystkie dotychczasowe audyty są czysto sygnałowe — sprawdzają głośność,
pasmo czy ciszę, ale nie to, *co* słychać. Ten skrypt zamyka tę lukę bez
modeli zewnętrznych.

Zasada: konkretne rodzaje dźwięku mają przewidywalny podpis akustyczny.
Dzwon jest tonalny i długo wybrzmiewa. Syk pary to szerokopasmowy szum bez
wyraźnej wysokości. Uderzenie ma ostry atak i szybki zanik. Skrzydła
modulują obwiednię kilka razy na sekundę. Jeżeli scenariusz obiecuje dzwon,
a plik jest płaskim szumem, to nie jest kwestia gustu — to policzalna
sprzeczność.

Działanie:
1. ze scenariusza (PL) wyciągamy oczekiwane klasy dźwięku po słowach kluczowych,
2. z pliku liczymy cechy (część bierzemy z gotowego audytu, resztę dokładamy),
3. każda klasa ma zestaw twardych predykatów; ich naruszenia sumujemy w wynik
   podejrzliwości wraz z czytelnym uzasadnieniem.

Wynik to lista kandydatów do odsłuchu i ewentualnej regeneracji, posortowana
od najbardziej rażących sprzeczności.

Użycie:
    python3 scripts/audit_semantic_match.py \
        --audit data/samples/audio-audit-2026-09-29-after-b055.json \
        --json data/samples/semantic-audit.json \
        --markdown docs/audits/2026-09-29-semantic-match.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-12
FRAME_S = 0.01


# --------------------------------------------------------------------------
# 1. Leksykon: słowo w scenariuszu -> oczekiwana klasa dźwięku
# --------------------------------------------------------------------------
LEXICON: dict[str, str] = {
    # tonalne, długo wybrzmiewające
    r"dzwon|gong|dzwonk|dzwonow|kurant|struna|harf|cymbał|rezonans krysz": "tonal_ring",
    r"krystaliczn\w* dźwięk|szklist\w* ton|czyst\w* ton": "tonal_ring",
    # uderzenia, transjenty
    r"uderzeni|cios|trzask|tupni|tupot|huk|łomot|walnięc|stukni|stuk\b|klaśnię|"
    r"grzmotnię|zderzeni|taranowa|miażdż|roztrzask|rozbici|pęknięc|kopnię": "impact",
    # metal
    r"szczęk|brzęk|klang|stal\w*|żelaz\w*|miecz|ostrz|klin|kling|zbroj|"
    r"pancerz|kowad|młot|mosiądz|brąz\b|blach": "metal",
    # szum, syk, para
    r"syk|sycz|para\b|pary\b|świst|szum|wydech|podmuch|wiatr|przeciąg|"
    r"upust|gwizd": "noise_hiss",
    # woda
    r"plusk|kropl|wod[aya]|wodn|bulgot|fal[aey]|toń|bańk|zanurz|ociek|"
    r"chlup|rozbryzg|deszcz|strumie[ńn]": "water",
    # głos zwierzęcy / ludzki
    r"ryk|wrzask|krzyk|krakani|skrzek|rżeni|warkot|pisk|wycie|szczek|"
    r"charkot|jazgot|kwik|miaucz|beczen|gdakani|syk węż|wrzeszcz|okrzyk|"
    r"pohukiw|zawodzeni": "voice",
    # skrzydła, łopot
    r"skrzyd|łopot|machnięc\w* skrzyd|trzepot": "wings",
    # kroki, rytm
    r"krok|marsz|galop|kopyt|stąpani|przestępow|bieg\b|biegn": "steps",
    # ogień
    r"ogie[ńn]|ognist|płomie|pożar|żar\b|lawa|magma|iskrzen|spopiel": "fire",
    # elektryczność
    r"elektry|wyładowan|prąd|iskr|piorun|błyskawic|statyk|łuk elektr": "electric",
    # skrzypienie, zgrzyt
    r"skrzyp|trzeszcz|zgrzyt|chrobot|chrzęst|rzężen": "creak",
    # niskie dudnienie
    r"dudni|grzmot|tąpnięc|wstrząs|lawin|osuwisk|rumor|pomruk|dygot": "rumble",
    # sypki materiał
    r"sypi|piask|żwir|gruz|okruch|kurz|proch|ziarn": "granular",
    # drewno
    r"drewn|dębow|desk|belk|pie[ńn]|pnia|kołek|drzazg": "wood",
}

# czytelne nazwy klas
CLASS_PL = {
    "tonal_ring": "dźwięk tonalny z długim wybrzmieniem (dzwon, struna)",
    "impact": "uderzenie — ostry atak, szybki zanik",
    "metal": "metal — jasne pasmo i dzwoniący ogon",
    "noise_hiss": "szerokopasmowy szum/syk bez wyraźnej wysokości",
    "water": "woda — rozproszone transjenty, szerokie pasmo",
    "voice": "głos (zwierzęcy lub ludzki) — wyraźna harmoniczność",
    "wings": "skrzydła — powolna modulacja obwiedni",
    "steps": "kroki — powtarzalne, rozłożone w czasie uderzenia",
    "fire": "ogień — nieregularne mikrotrzaski w szumie",
    "electric": "elektryczność — jasne, chaotyczne trzaski",
    "creak": "skrzypienie — wolna modulacja, średnie pasmo",
    "rumble": "niskie dudnienie — dominacja dołu pasma",
    "granular": "materiał sypki — gęste, drobne ziarna",
    "wood": "drewno — matowy, krótki rezonans",
}


# Słowa użyte przenośnie nie opisują materiału: „fala aury”, „strumień ognia”,
# „iskra nadziei”. Bez tego filtra detektor żąda od nich brzmienia wody czy
# elektryczności i produkuje fałszywe alarmy.
METAPHOR_GUARDS: dict[str, re.Pattern] = {
    "water": re.compile(
        r"(fal[aeiy]\w*|strumie\w+|kaskad\w+|przypływ\w*|toni\w*)\s+"
        r"(\w+\s+)?(aur|energi|mocy|moc\b|ogni|ognia|świat|blask|magi|dźwięk|"
        r"cieni|ciemnoś|krwi|lawy|many|płomien|iskier|pyłu|piasku|czasu)"),
    "electric": re.compile(r"iskr\w*\s+(nadziei|wiary|gniewu|życia|geniuszu)"),
    "fire": re.compile(r"(żar|ogie\w+|płomie\w+)\s+(walki|bitwy|serc|wiary|gniewu|spojrzeń)"),
}


def classes_for(scenario: str) -> list[str]:
    text = scenario.lower()
    found: list[str] = []
    for pattern, cls in LEXICON.items():
        if not re.search(pattern, text) or cls in found:
            continue
        guard = METAPHOR_GUARDS.get(cls)
        if guard and guard.search(text):
            # dopuszczamy klasę tylko wtedy, gdy poza metaforą jest też
            # dosłowne słowo z tej rodziny (np. „plusk” obok „fali energii”)
            literal = {
                "water": r"plusk|kropl|bulgot|bańk|chlup|rozbryzg|zanurz|ociek|deszcz|wodn",
                "electric": r"wyładowan|prąd|piorun|błyskawic|statyk|elektry",
                "fire": r"trzask ogn|płomie\w+ liż|pożar|lawa|magma|spopiel",
            }[cls]
            if not re.search(literal, text):
                continue
        found.append(cls)
    return found


# --------------------------------------------------------------------------
# 2. Cechy dodatkowe (poza tym, co liczy audit_samples_full.py)
# --------------------------------------------------------------------------
def extra_features(path: Path) -> dict:
    data, fs = sf.read(str(path), always_2d=True)
    mono = data.mean(axis=1)
    if not len(mono):
        return {}
    n = max(1, int(fs * FRAME_S))
    usable = (len(mono) // n) * n
    frames = mono[:usable].reshape(-1, n)
    env = np.sqrt((frames ** 2).mean(axis=1))
    env_db = 20 * np.log10(np.maximum(env, EPS))
    peak_i = int(np.argmax(env))
    peak_db = float(env_db[peak_i])

    # czas ataku: od -20 dB względem szczytu do szczytu
    attack_s = 0.0
    thr = peak_db - 20.0
    i = peak_i
    while i > 0 and env_db[i] > thr:
        i -= 1
    attack_s = (peak_i - i) * FRAME_S

    # czas zaniku: od szczytu do -20 dB poniżej
    j = peak_i
    while j < len(env_db) - 1 and env_db[j] > thr:
        j += 1
    decay_s = (j - peak_i) * FRAME_S

    # onsety: lokalne skoki energii
    d = np.diff(env_db, prepend=env_db[0])
    onset_idx = [k for k in range(1, len(d)) if d[k] > 6.0 and env_db[k] > peak_db - 30]
    merged: list[int] = []
    for k in onset_idx:
        if not merged or (k - merged[-1]) * FRAME_S > 0.06:
            merged.append(k)
    iois = np.diff(merged) * FRAME_S if len(merged) > 1 else np.array([])
    ioi_cv = float(np.std(iois) / np.mean(iois)) if len(iois) >= 2 and np.mean(iois) > 0 else None

    # widmo modulacji obwiedni (jak szybko pulsuje dźwięk)
    act = env[env > np.max(env) * 10 ** (-40 / 20)] if np.max(env) > 0 else env
    mod_peak_hz = None
    if len(act) >= 16:
        a = act - act.mean()
        spec = np.abs(np.fft.rfft(a * np.hanning(len(a))))
        freqs = np.fft.rfftfreq(len(a), FRAME_S)
        band = (freqs >= 1.0) & (freqs <= 20.0)
        if band.any() and spec[band].max() > 0:
            mod_peak_hz = float(freqs[band][int(np.argmax(spec[band]))])

    # udział „ciągły” — ile ramek trzyma się blisko szczytu
    sustain_ratio = float(np.mean(env_db > peak_db - 12.0))

    return {
        "attack_s": round(attack_s, 3),
        "decay_s": round(decay_s, 3),
        "onset_count": len(merged),
        "ioi_cv": round(ioi_cv, 3) if ioi_cv is not None else None,
        "mod_peak_hz": round(mod_peak_hz, 2) if mod_peak_hz else None,
        "sustain_ratio": round(sustain_ratio, 3),
    }


# --------------------------------------------------------------------------
# 3. Predykaty: co MUSI być prawdą, jeśli scenariusz obiecuje daną klasę
# --------------------------------------------------------------------------
def percentiles(rows: list[dict]) -> dict:
    """Progi liczone z rozkładu całego korpusu — audyt kalibruje się sam."""
    keys = ["spectral_flatness", "tonal_frame_fraction", "voiced_fraction",
            "spectral_centroid_hz", "attack_s", "decay_s", "sustain_ratio",
            "rolloff95_hz", "mod_peak_hz"]
    q: dict[str, dict[str, float]] = {}
    for k in keys:
        vals = [r[k] for r in rows if r.get(k) is not None]
        if not vals:
            continue
        arr = np.array(vals, dtype=float)
        q[k] = {f"p{p}": float(np.percentile(arr, p)) for p in (5, 25, 50, 75, 95)}
    return q


def check(cls: str, m: dict, q: dict) -> list[tuple[str, float]]:
    """Zwraca listę (opis naruszenia, waga). Pusta lista = zgodne.

    Progi są pozycjami w rozkładzie korpusu: „dolny kwartyl cechy, której
    dana klasa dźwięku wymaga” to twardy argument, a nie zgadywanie.
    """
    def thr(key: str, p: str, fallback: float) -> float:
        return q.get(key, {}).get(p, fallback)

    bands = m.get("bands", {}) or {}
    low = bands.get("sub_0_60", 0) + bands.get("low_60_250", 0)
    high = bands.get("high_2k_8k", 0) + bands.get("air_8k_plus", 0)
    mid = bands.get("mid_250_2k", 0)
    flat = m.get("spectral_flatness", 0)
    tonal = m.get("tonal_frame_fraction", 0)
    voiced = m.get("voiced_fraction", 0)
    cent = m.get("spectral_centroid_hz", 0)
    decay = m.get("decay_s", 0)
    attack = m.get("attack_s", 0)
    onsets = m.get("onset_count", 0)
    modpk = m.get("mod_peak_hz")
    sustain = m.get("sustain_ratio", 0)
    rolloff = m.get("rolloff95_hz", 0)

    flat_lo, flat_hi = thr("spectral_flatness", "p25", 0.007), thr("spectral_flatness", "p75", 0.24)
    tonal_lo, tonal_hi = thr("tonal_frame_fraction", "p25", 0.011), thr("tonal_frame_fraction", "p75", 0.93)
    voiced_hi = thr("voiced_fraction", "p75", 0.34)
    cent_lo, cent_hi = thr("spectral_centroid_hz", "p25", 1000), thr("spectral_centroid_hz", "p95", 9230)
    attack_hi = thr("attack_s", "p75", 0.37)
    decay_lo = thr("decay_s", "p25", 0.08)
    sustain_hi = thr("sustain_ratio", "p75", 0.43)
    roll_lo = thr("rolloff95_hz", "p25", 2196)
    mod_hi = thr("mod_peak_hz", "p95", 13.7)

    bad: list[tuple[str, float]] = []
    if cls == "tonal_ring":
        if tonal < tonal_lo:
            bad.append((f"brak tonalności (tonal={tonal:.2f} < dolny kwartyl {tonal_lo:.2f})", 2.0))
        if flat > flat_hi:
            bad.append((f"widmo szumowe (flatness={flat:.2f} > górny kwartyl {flat_hi:.2f})", 1.5))
        if decay < decay_lo:
            bad.append((f"brak wybrzmienia (zanik {decay:.2f} s < dolny kwartyl {decay_lo:.2f} s)", 1.5))
    elif cls == "impact":
        if attack > attack_hi:
            bad.append((f"atak zbyt wolny ({attack:.2f} s > górny kwartyl {attack_hi:.2f} s)", 1.5))
        if sustain > sustain_hi and onsets <= 1:
            bad.append((f"dźwięk ciągły zamiast uderzenia (sustain={sustain:.2f})", 1.5))
    elif cls == "metal":
        if cent < cent_lo:
            bad.append((f"pasmo zbyt ciemne jak na metal (centroid={cent:.0f} Hz < dolny kwartyl {cent_lo:.0f})", 1.5))
        if rolloff < roll_lo:
            bad.append((f"brak jasnego ogona (rolloff95={rolloff:.0f} Hz < dolny kwartyl {roll_lo:.0f})", 1.0))
    elif cls == "noise_hiss":
        if flat < flat_lo:
            bad.append((f"widmo tonalne zamiast szumu (flatness={flat:.3f} < dolny kwartyl {flat_lo:.3f})", 2.0))
        if voiced > voiced_hi:
            bad.append((f"wyraźna wysokość dźwięku (voiced={voiced:.2f} > górny kwartyl {voiced_hi:.2f})", 1.5))
    elif cls == "water":
        # dźwięk podwodny albo wprost opisany jako stłumiony jest ciemny
        # z fizyki, nie z wady generacji — nie wymagamy od niego góry pasma
        muffled_ok = m.get("_muffled_by_design", False)
        if mid + high < 0.4 and not muffled_ok:
            bad.append((f"woda bez średnicy i góry (mid+high={mid + high:.1%})", 1.5))
        if tonal > tonal_hi:
            bad.append((f"dźwięk tonalny zamiast wody (tonal={tonal:.2f} > górny kwartyl {tonal_hi:.2f})", 1.5))
    elif cls == "voice":
        if voiced < 0.05:
            bad.append((f"brak harmoniczności głosu (voiced={voiced:.2f}, głos wymaga wyraźnego f0)", 2.0))
        if flat > flat_hi:
            bad.append((f"czysty szum zamiast głosu (flatness={flat:.2f})", 1.5))
    elif cls == "wings":
        if modpk is None or modpk > mod_hi:
            bad.append((f"brak pulsacji skrzydeł (modulacja={modpk} Hz, oczekiwana <{mod_hi:.1f} Hz)", 1.5))
    elif cls == "steps":
        if onsets < 2:
            bad.append((f"tylko {onsets} zdarzenie — kroki wymagają powtórzeń", 2.0))
    elif cls == "fire":
        if flat < flat_lo:
            bad.append((f"brak szumowej natury ognia (flatness={flat:.3f} < dolny kwartyl {flat_lo:.3f})", 1.5))
        if high < 0.02:
            bad.append((f"ogień bez trzasków w górze pasma (high={high:.1%})", 1.0))
    elif cls == "electric":
        if cent < cent_lo:
            bad.append((f"zbyt ciemne jak na wyładowanie (centroid={cent:.0f} Hz < dolny kwartyl {cent_lo:.0f})", 1.5))
        if high < 0.05:
            bad.append((f"brak jasnych trzasków (high={high:.1%})", 1.5))
    elif cls == "creak":
        if modpk is None and sustain > 0.8:
            bad.append(("brak modulacji typowej dla skrzypienia", 1.0))
    elif cls == "rumble":
        if low < 0.20:
            bad.append((f"brak dołu pasma (low={low:.1%}, oczekiwane >20%)", 1.5))
    elif cls == "granular":
        if flat < flat_lo:
            bad.append((f"brak ziarnistej szumowości (flatness={flat:.3f})", 1.0))
    elif cls == "wood":
        if cent > cent_hi:
            bad.append((f"zbyt jasne jak na drewno (centroid={cent:.0f} Hz > {cent_hi:.0f})", 1.0))
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit", default="data/samples/audio-audit-2026-09-29-after-b055.json")
    ap.add_argument("--scenarios", default="data/samples/scenarios.jsonl")
    ap.add_argument("--samples-dir", default="audio/samples")
    ap.add_argument("--json", dest="json_out", default="")
    ap.add_argument("--markdown", default="")
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()

    audit = json.loads(Path(args.audit).read_text(encoding="utf-8"))
    base = {f["id"]: f for f in audit["files"]}
    scen = {}
    for line in Path(args.scenarios).read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            scen[str(r["story_id"])] = r

    # przebieg 1: cechy wszystkich plików (do kalibracji progów)
    measured: dict[str, dict] = {}
    for i, (sid, s) in enumerate(sorted(scen.items(), key=lambda kv: int(kv[0])), 1):
        if i % 100 == 0:
            print(f"  … cechy {i}/{len(scen)}")
        path = Path(args.samples_dir) / f"{sid}.mp3"
        if not path.exists():
            continue
        m = dict(base.get(sid, {}))
        m.update(extra_features(path))
        measured[sid] = m
    q = percentiles(list(measured.values()))

    # przebieg 2: ocena zgodności ze scenariuszem
    results = []
    no_class = []
    for sid, s in sorted(scen.items(), key=lambda kv: int(kv[0])):
        m = measured.get(sid)
        if m is None:
            continue
        cls = classes_for(s["sample_scenario"])
        if not cls:
            no_class.append(sid)
            continue
        import re as _re
        m["_muffled_by_design"] = bool(_re.search(
            r"podwodn|pod wodą|w głębi|w toni|stłumion|zanurz|przez ścianę|zza ściany",
            s["sample_scenario"].lower()))
        violations = []
        for c in cls:
            for reason, weight in check(c, m, q):
                violations.append({"class": c, "reason": reason, "weight": weight})
        score = round(sum(v["weight"] for v in violations), 2)
        results.append({
            "id": sid,
            "title": s["title"],
            "scenario": s["sample_scenario"],
            "classes": cls,
            "score": score,
            "violations": violations,
            "metrics": {k: m.get(k) for k in
                        ("spectral_centroid_hz", "spectral_flatness", "tonal_frame_fraction",
                         "voiced_fraction", "attack_s", "decay_s", "onset_count",
                         "mod_peak_hz", "sustain_ratio", "rolloff95_hz", "bands")},
        })

    results.sort(key=lambda r: -r["score"])
    suspects = [r for r in results if r["score"] > 0]
    out = {
        "thresholds_from_corpus": q,
        "checked": len(results),
        "without_class": no_class,
        "suspects": len(suspects),
        "by_severity": {
            "rażące (>=3.0)": sum(1 for r in results if r["score"] >= 3.0),
            "wyraźne (1.5-3.0)": sum(1 for r in results if 1.5 <= r["score"] < 3.0),
            "drobne (<1.5)": sum(1 for r in results if 0 < r["score"] < 1.5),
        },
        "results": results,
    }
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
        print(f"JSON: {args.json_out}")

    print(f"sprawdzono {len(results)} sampli z rozpoznaną klasą dźwięku, "
          f"bez klasy: {len(no_class)}")
    print(f"podejrzanych: {len(suspects)} — {out['by_severity']}")
    print(f"\nTOP {min(args.top, len(suspects))} sprzeczności:")
    for r in suspects[:args.top]:
        print(f"  {r['score']:>4.1f}  {r['id']:>4} {r['scenario'][:52]:54} "
              f"{', '.join(v['reason'][:46] for v in r['violations'][:2])}")

    if args.markdown:
        lines = ["# Audyt semantyczny — czy sample brzmi jak scenariusz",
                 "",
                 f"Sprawdzono **{len(results)}** sampli z rozpoznaną klasą dźwięku. "
                 f"Bez rozpoznanej klasy: **{len(no_class)}** (scenariusze bez konkretnego "
                 "słowa dźwiękowego — osobna lista do przepisania).",
                 "",
                 f"- rażące sprzeczności (≥3,0): **{out['by_severity']['rażące (>=3.0)']}**",
                 f"- wyraźne (1,5–3,0): **{out['by_severity']['wyraźne (1.5-3.0)']}**",
                 f"- drobne (<1,5): **{out['by_severity']['drobne (<1.5)']}**",
                 "",
                 "## Kandydaci do odsłuchu i regeneracji", "",
                 "| Wynik | ID | Scenariusz | Oczekiwano | Zmierzono |",
                 "|---|---|---|---|---|"]
        for r in suspects[:args.top]:
            exp = "; ".join(CLASS_PL.get(c, c) for c in r["classes"])
            got = "; ".join(v["reason"] for v in r["violations"])
            lines.append(f"| {r['score']:.1f} | {r['id']} | {r['scenario'][:70]} | "
                         f"{exp[:70]} | {got[:110]} |")
        Path(args.markdown).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Markdown: {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
