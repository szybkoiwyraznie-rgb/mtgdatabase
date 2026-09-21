#!/usr/bin/env python3
"""Validate the production CSV contract: id,title,story."""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path

REQUIRED = ("id", "title", "story")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    with args.csv_file.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(REQUIRED):
            print(f"Expected columns exactly {REQUIRED}; got {reader.fieldnames}", file=sys.stderr)
            return 1
        seen = set()
        for line, row in enumerate(reader, 2):
            story_id = (row["id"] or "").strip()
            if not story_id.isdigit() or int(story_id) < 1:
                print(f"Line {line}: id must be a positive integer", file=sys.stderr); return 1
            if story_id in seen:
                print(f"Line {line}: duplicate id {story_id}", file=sys.stderr); return 1
            if not (row["title"] or "").strip() or not (row["story"] or "").strip():
                print(f"Line {line}: title and story are required", file=sys.stderr); return 1
            seen.add(story_id)
    print(f"Valid story CSV: {len(seen)} record(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
