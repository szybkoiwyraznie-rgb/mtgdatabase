#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audyt wyrazistości scenariuszy: czy da się to w ogóle nagrać.

Część scenariuszy opisuje obraz, a nie dźwięk — „czarna mgła zamalowująca
zbroję rycerza”, „złota aura na tarczy”, „wielookie spojrzenie koszmaru”.
To opis kadru, nie zlecenie dla realizatora dźwięku. Generator dostaje
wtedy przymiotniki wizualne i odsyła tonalny pomruk, bo nie ma czego
odwzorować.

Skrypt punktuje każdy scenariusz w trzech wymiarach:

1. **nośnik dźwięku** — czy jest rzeczownik/czasownik oznaczający konkretne
   zdarzenie akustyczne (trzask, plusk, szczęk, ryk, syk…),
2. **materiał i kontakt** — czy wiadomo, co uderza o co (stal, drewno,
   kamień, skóra, woda…); model tego potrzebuje, żeby cokolwiek zbudować,
3. **balast wizualny i abstrakcyjny** — kolory, blask, aury, emocje,
   spojrzenia, pojęcia (przekonania, nadzieja, błogosławieństwo).

Wynik 0–100. Niski = scenariusz do przepisania na konkret („skrzyp drzwi”,
„szczęk miecza o miecz”, „pojedynczy krzyk człowieka”).

Użycie:
    python3 scripts/audit_scenario_quality.py \
        --json data/samples/scenario-quality.json \
        --markdown docs/audits/2026-09-29-scenario-quality.md
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# 1. Nośniki dźwięku — konkretne zdarzenia akustyczne
SOUND_WORDS = re.compile(
    r"trzask|trzeszcz|plusk|chlup|bulgot|syk|sycz|świst|gwizd|szum|szelest|"
    r"szur|zgrzyt|chrobot|chrzęst|brzęk|szczęk|dzwon|klang|stuk|puk|łomot|"
    r"huk|grzmot|dudni|tąpnię|łoskot|tupni|tupot|klaśnię|klask|skrzyp|"
    r"ryk|wrzask|krzyk|okrzyk|krakani|skrzek|rżeni|warkot|pisk|wycie|"
    r"szczek|charkot|kwik|jazgot|pomruk|sapani|dysz|wdech|wydech|oddech|"
    r"uderzeni|cios|kopnię|zderzeni|pęknię|rozdarci|rozerwani|chlusnię|"
    r"kapani|kropl|terkot|turkot|furkot|łopot|trzepot|dzwonek|brzdęk|"
    r"zgrzytnię|stuknię|skwiercz|skwierk|bzycz|brzęcz|mlask|siorb|"
    r"grzechot|klekot|chrzęści|chrupnię|wystrzał|strzał|salw|detonacj|"
    r"eksplozj|wybuch|rozbryzg|rozprysk|zatrzask|stukot|szmer|szept"
)

# 2. Materiał i kontakt — z czego i o co
MATERIAL_WORDS = re.compile(
    r"stal|żelaz|metal|mosiądz|brąz|miedz|blach|kut|drewn|dębow|desk|belk|"
    r"pie[ńn]|pnia|kamie|skał|głaz|bazalt|granit|marmur|bruk|mur|ceglan|"
    r"szkł|szklan|kryształ|porcelan|ceramik|glin|wod|błot|śnieg|lód|lodow|"
    r"piask|żwir|ziemi|gleb|liści|gałęz|kor[ay]\b|skór|tkanin|płótn|"
    r"pergamin|papier|kość|kości|chityn|łusk|pancerz|kolcz|siatk|lina|"
    r"sznur|olej|smoł|wosk|krew|mięs|futr|pióro|piór|wełn|słom"
)

# 3. Balast wizualny / abstrakcyjny — tego nie da się nagrać
VISUAL_WORDS = re.compile(
    r"blask|blaskiem|świetlist|jarzą|lśni|połysk|migot|promieni|promień|"
    r"aur[ay]|poświat|łun[ay]|barw|kolor|złocist|złot[aoey]|srebrzyst|"
    r"szmaragdow|turkusow|karmazynow|purpurow|błękitn|lazurow|fioletow|"
    r"bursztynow|opalizuj|tęczow|spojrzeni|wzrok|oczy|oczu|sylwetk|"
    r"postać|wygląd|widok|obraz|scen[ay]|symbol|znak|gest|mina|uśmiech|"
    r"majestat|dostojn|elegancj|piękn|wspaniał|mgł[ay]|opar[ay]|cień|cieni"
)
ABSTRACT_WORDS = re.compile(
    r"przekona|determinacj|nadziej|wiar[ay]|duma|dumn|honor|odwag|męstw|"
    r"strach|groz[ay]|panik|rozpacz|gniew|furi|spokój|harmoni|równowag|"
    r"błogosławie|klątw|przeznacz|los\b|potęg|moc[ąy]?\b|siła woli|"
    r"triumf|zwycięstw|chwał|sław[ay]|pamięć|wspomnie|tęsknot|miłoś|"
    r"więź|przymierz|lojalnoś|zdrad|mądroś|geniusz|szaleństw|energi"
)


def score_one(scenario: str) -> dict:
    text = scenario.lower()
    words = re.findall(r"\w+", text)
    n_words = len(words)

    sound_hits = len(set(m.group(0) for m in SOUND_WORDS.finditer(text)))
    material_hits = len(set(m.group(0) for m in MATERIAL_WORDS.finditer(text)))
    visual_hits = len(set(m.group(0) for m in VISUAL_WORDS.finditer(text)))
    abstract_hits = len(set(m.group(0) for m in ABSTRACT_WORDS.finditer(text)))

    # złożoność: opis sceny zamiast jednego zdarzenia
    connectors = len(re.findall(r"\bi\b|\boraz\b|,|—|;|\bpodczas\b|\bgdy\b|\ba\b", text))

    score = 50.0
    score += min(sound_hits, 3) * 14      # nośnik dźwięku to podstawa
    score += min(material_hits, 3) * 7    # materiał/kontakt
    score -= min(visual_hits, 4) * 9      # balast wizualny
    score -= min(abstract_hits, 3) * 11   # abstrakcja jest najgorsza
    if n_words > 12:
        score -= (n_words - 12) * 1.5     # rozwlekły opis = scena
    if connectors > 2:
        score -= (connectors - 2) * 3
    score = max(0.0, min(100.0, score))

    problems = []
    if sound_hits == 0:
        problems.append("brak słowa opisującego konkretny dźwięk")
    if material_hits == 0:
        problems.append("brak materiału/kontaktu (co uderza o co)")
    if visual_hits >= 2:
        problems.append(f"opis wizualny ({visual_hits} określeń obrazu)")
    if abstract_hits >= 1:
        problems.append(f"pojęcia abstrakcyjne ({abstract_hits})")
    if connectors > 3:
        problems.append("opis sceny złożonej, nie jednego zdarzenia")

    return {
        "score": round(score, 1),
        "sound_hits": sound_hits,
        "material_hits": material_hits,
        "visual_hits": visual_hits,
        "abstract_hits": abstract_hits,
        "words": n_words,
        "problems": problems,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenarios", default="data/samples/scenarios.jsonl")
    ap.add_argument("--json", dest="json_out", default="")
    ap.add_argument("--markdown", default="")
    ap.add_argument("--threshold", type=float, default=40.0)
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()

    rows = []
    for line in Path(args.scenarios).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        s = score_one(r["sample_scenario"])
        rows.append({"id": str(r["story_id"]), "title": r["title"],
                     "scenario": r["sample_scenario"], **s})
    rows.sort(key=lambda r: r["score"])
    weak = [r for r in rows if r["score"] < args.threshold]

    import statistics as st
    scores = [r["score"] for r in rows]
    out = {
        "count": len(rows),
        "median_score": round(st.median(scores), 1),
        "below_threshold": len(weak),
        "threshold": args.threshold,
        "no_sound_word": sum(1 for r in rows if r["sound_hits"] == 0),
        "no_material": sum(1 for r in rows if r["material_hits"] == 0),
        "results": rows,
    }
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
        print(f"JSON: {args.json_out}")

    print(f"scenariuszy: {len(rows)}, mediana wyniku: {out['median_score']}")
    print(f"poniżej progu {args.threshold}: {len(weak)}")
    print(f"bez słowa dźwiękowego: {out['no_sound_word']}, bez materiału: {out['no_material']}")
    print(f"\nNAJSŁABSZE {min(args.top, len(rows))}:")
    for r in rows[:args.top]:
        print(f"  {r['score']:>5.1f}  {r['id']:>4} {r['scenario'][:56]:58} {'; '.join(r['problems'])[:60]}")

    if args.markdown:
        lines = ["# Audyt wyrazistości scenariuszy",
                 "",
                 f"Ocenionych scenariuszy: **{len(rows)}**, mediana wyniku: "
                 f"**{out['median_score']}/100**.",
                 "",
                 f"- poniżej progu {args.threshold}: **{len(weak)}**",
                 f"- bez żadnego słowa opisującego dźwięk: **{out['no_sound_word']}**",
                 f"- bez materiału/kontaktu: **{out['no_material']}**",
                 "",
                 "Niski wynik oznacza opis kadru zamiast zdarzenia dźwiękowego.",
                 "",
                 "| Wynik | ID | Scenariusz | Problemy |", "|---|---|---|---|"]
        for r in rows[:args.top]:
            lines.append(f"| {r['score']:.1f} | {r['id']} | {r['scenario'][:70]} | "
                         f"{'; '.join(r['problems'])} |")
        Path(args.markdown).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Markdown: {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
