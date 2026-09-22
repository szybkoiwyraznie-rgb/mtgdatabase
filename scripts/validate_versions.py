#!/usr/bin/env python3
"""Validate that every rendered jingle version has a project description.

Versions whose project_description carries a "genre" field (introduced with
the live-samples rule, AGENTS.md #14) are additionally checked against it:
sci-fi needs >=1 live (non-synth) event, every other genre needs >=2 live
events. Versions predating the rule have no genre and stay valid as history.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

REQUIRED = ("description", "ambience", "drone", "events", "mix_notes", "qa")

def live_events(design: dict) -> list:
    return [event for event in design.get("events", [])
            if not str(event.get("sample", "")).startswith("synth:")]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    count = 0
    for story in data.get("stories", []):
        for version in story.get("versions", []):
            count += 1
            design = version.get("project_description")
            if not isinstance(design, dict) or any(not design.get(key) for key in REQUIRED):
                print(f"{story.get('id')} {version.get('label')}: incomplete project_description", file=sys.stderr)
                return 1
            if not isinstance(design["events"], list) or not isinstance(design["qa"].get("score"), (int, float)):
                print(f"{story.get('id')} {version.get('label')}: events or qa score invalid", file=sys.stderr)
                return 1
            genre = str(design.get("genre", "")).strip().lower()
            if genre:
                minimum = 1 if genre == "sci-fi" else 2
                live = live_events(design)
                if len(live) < minimum:
                    print(f"{story.get('id')} {version.get('label')}: genre '{genre}' wymaga >= {minimum} "
                          f"żywych sampli w events, znaleziono {len(live)} (AGENTS.md #14)", file=sys.stderr)
                    return 1
    print(f"Valid project descriptions: {count} version(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
