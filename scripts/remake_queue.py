#!/usr/bin/env python3
"""Print the remake queue ranked by each story's BEST rated version.

Clarified loop rule (AGENTS.md #3, 2026-09-22): a poorly rated remake does
not raise a story's remake priority above its best version. If v2 flopped
(3/15) while v1 scored 10/15, the story stands at 10/15 — the queue ranks
stories by their best rated version, and the new vN builds on that version.
A story whose latest version is still waiting for a rating is skipped:
never stack versions while one is being evaluated. Stories without an open
report have nothing to serve.

Pinned samples rule (owner decision 2026-09-23): any version rated above
10/15 pins the samples its comments explicitly praise — the remake must
reuse those exact stem files with the same mastering. A from-scratch
concept is allowed only when no version of the story exceeded 10/15.

Usage:
  python scripts/remake_queue.py --versions data/versions.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def version_number(version: dict) -> int:
    try:
        return int(str(version.get("label", "v0")).lstrip("v"))
    except ValueError:
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--versions", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.versions.read_text(encoding="utf-8"))

    queue: list[tuple[str, str, float, int]] = []
    skipped: list[tuple[str, str]] = []
    for story in data.get("stories", []):
        versions = story.get("versions", [])
        rated = [v for v in versions if isinstance(v.get("score"), (int, float))]
        if not rated:
            skipped.append((str(story["id"]), "brak ocenionej wersji"))
            continue
        best = max(rated, key=lambda v: (v["score"], version_number(v)))
        latest = max(versions, key=version_number)
        if not isinstance(latest.get("score"), (int, float)):
            skipped.append((str(story["id"]), f"najnowsza {latest['label']} czeka na ocenę (najlepsza: {best['label']} = {best['score']}/15)"))
            continue
        open_reports = [r for v in versions for r in v.get("reports", []) if r.get("state") == "open"]
        if not open_reports:
            skipped.append((str(story["id"]), f"brak otwartych raportów (najlepsza: {best['label']} = {best['score']}/15)"))
            continue
        # Owner rule (2026-09-23): every version rated ABOVE 10/15 pins the
        # samples its comments explicitly praise — a remake must reuse those
        # exact stem files with the same mastering, not "similar" sounds.
        pinned = [
            (v["label"], float(v["score"]), [str(r.get("comment", "")).strip() for r in v.get("reports", []) if str(r.get("comment", "")).strip()])
            for v in rated if float(v["score"]) > 10 and any(str(r.get("comment", "")).strip() for r in v.get("reports", []))
        ]
        queue.append((str(story["id"]), best["label"], float(best["score"]), len(open_reports), pinned))

    queue.sort(key=lambda item: item[2])
    print("Kolejka remake'ów — fabuły uszeregowane po NAJLEPSZEJ ocenionej wersji (rosnąco):")
    if queue:
        for position, (sid, label, score, reports, pinned) in enumerate(queue, 1):
            if score <= 10:
                plan = "OD ZERA (żadna wersja fabuły nie przekroczyła 10/15)"
            elif score < 12:
                plan = f"na fundamencie {label} — obowiązkowo te same pochwalone sample (decyzja właściciela 2026-09-23)"
            else:
                plan = f"powyżej progu remaków (<12/15) — remake niewymagany; jeśli już, to na fundamencie {label} z obowiązkowymi pochwalonymi samplami"
            print(f"  {position}. fabuła {sid}: najlepsza {label} = {score:.0f}/15, otwartych raportów: {reports}"
                  f" → remakuj kolejną wersję {plan}")
            for pinned_label, pinned_score, comments in pinned:
                print(f"     OBOWIĄZEK ({pinned_label}, {pinned_score:.0f}/15 > 10/15): przeanalizuj komentarze i zachowaj WPROST pochwalone sample — te same pliki i to samo masterowanie ('podobne' nie wystarczy):")
                for comment in comments:
                    print(f"       „{comment}”")
    else:
        print("  (pusta — brak fabuł spełniających warunki remaku)")
    print("Pominięte:")
    for sid, why in skipped:
        print(f"  fabuła {sid}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
