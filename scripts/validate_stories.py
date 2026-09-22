#!/usr/bin/env python3
"""Validate the collection.csv contract."""
from __future__ import annotations
import argparse, csv, re, sys
from pathlib import Path

EXPECTED = ("Ilustracja", "Nazwa Karty", "Narracja")
PATTERN = re.compile(r"^\d+[A-Za-z0-9_-]+$")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    with args.csv_file.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != list(EXPECTED):
            print(f"Expected tab-separated columns {EXPECTED}; got {reader.fieldnames}", file=sys.stderr)
            return 1
        seen = set()
        for line, row in enumerate(reader, 2):
            if not any((value or "").strip() for value in row.values()):
                continue
            art_id = (row["Ilustracja"] or "").strip()
            numeric = re.match(r"^(\d+)", art_id)
            if not PATTERN.fullmatch(art_id) or not numeric:
                print(f"Line {line}: invalid artID {art_id!r}", file=sys.stderr); return 1
            if numeric.group(1) in seen:
                print(f"Line {line}: duplicate numeric ID {numeric.group(1)}", file=sys.stderr); return 1
            if not (row["Nazwa Karty"] or "").strip() or not (row["Narracja"] or "").strip():
                print(f"Line {line}: title and narration are required", file=sys.stderr); return 1
            seen.add(numeric.group(1))
    print(f"Valid collection CSV: {len(seen)} record(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
