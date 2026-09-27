#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print the next unplanned stories as a writing queue for v2 sample scenarios."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/catalog.json")
    parser.add_argument("--scenarios", type=Path, default=ROOT / "data/samples/scenarios.jsonl")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--ids", help="Comma-separated story IDs instead of next missing")
    parser.add_argument("--jsonl", action="store_true", help="Emit draft JSONL skeletons")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))["stories"]
    done = {str(r["story_id"]) for r in read_jsonl(args.scenarios)}
    want = {x.strip() for x in args.ids.split(",") if x.strip()} if args.ids else None
    selected = []
    for story in sorted(catalog, key=lambda s: int(s["id"])):
        sid = str(story["id"])
        if want is not None:
            if sid not in want:
                continue
        elif sid in done:
            continue
        selected.append(story)
        if len(selected) >= args.limit:
            break
    if args.jsonl:
        for story in selected:
            row = {
                "story_id": str(story["id"]),
                "title": story["title"],
                "sample_scenario": "TODO: jeden krótki, jednorodny dźwięk",
                "prompt": "TODO: one short homogeneous sound effect, no music, no speech.",
                "duration_seconds": 2.5,
                "status": "draft",
                "batch": "TODO",
            }
            print(json.dumps(row, ensure_ascii=False, sort_keys=True))
    else:
        for story in selected:
            print(f"## {story['id']} — {story['title']} ({story.get('art_id','')})")
            print(story["story"])
            print()


if __name__ == "__main__":
    main()
