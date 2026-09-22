#!/usr/bin/env python3
"""Validate that every rendered jingle version has a project description."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

REQUIRED = ("description", "ambience", "drone", "events", "mix_notes", "qa")

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
    print(f"Valid project descriptions: {count} version(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
