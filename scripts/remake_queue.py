#!/usr/bin/env python3
"""Print the remake queue ranked by each story's BEST rated version.

Clarified loop rule (AGENTS.md #3, 2026-09-22): a poorly rated remake does
not raise a story's remake priority above its best version. If v2 flopped
(3/15) while v1 scored 10/15, the story stands at 10/15 — the queue ranks
stories by their best rated version, and the new vN builds on that version.
A story whose latest version is still waiting for a rating is skipped:
never stack versions while one is being evaluated. Stories without an open
report have nothing to serve.

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
        queue.append((str(story["id"]), best["label"], float(best["score"]), len(open_reports)))

    queue.sort(key=lambda item: item[2])
    print("Kolejka remake'ów — fabuły uszeregowane po NAJLEPSZEJ ocenionej wersji (rosnąco):")
    if queue:
        for position, (sid, label, score, reports) in enumerate(queue, 1):
            print(f"  {position}. fabuła {sid}: najlepsza {label} = {score:.0f}/15, otwartych raportów: {reports}"
                  f" → remakuj kolejną wersję na fundamencie {label}")
    else:
        print("  (pusta — brak fabuł spełniających warunki remaku)")
    print("Pominięte:")
    for sid, why in skipped:
        print(f"  fabuła {sid}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
