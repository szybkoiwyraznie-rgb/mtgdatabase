#!/usr/bin/env python3
"""Convert the collection CSV/TSV into the site catalog format."""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path

ART_ID = re.compile(r"^(\d+)([A-Za-z0-9_-]+)$")
EXPECTED = ["Ilustracja", "Nazwa Karty", "Narracja"]


def detect_delimiter(header_line: str) -> str:
    # Existing repo file is TSV despite the .csv extension; new user files may
    # be real comma-separated CSV. Use only the header, because narrations
    # contain many commas.
    return "\t" if "\t" in header_line else ","


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.csv_file.open(encoding="utf-8-sig", newline="") as handle:
        header = handle.readline()
        handle.seek(0)
        reader = csv.DictReader(handle, delimiter=detect_delimiter(header))
        if reader.fieldnames != EXPECTED:
            raise SystemExit(f"Expected columns {EXPECTED}; got {reader.fieldnames}")
        stories, seen = [], set()
        for line, row in enumerate(reader, 2):
            if not any((value or "").strip() for value in row.values()):
                continue
            art_id = (row["Ilustracja"] or "").strip()
            match = ART_ID.fullmatch(art_id)
            if not match:
                raise SystemExit(f"Line {line}: invalid artID {art_id!r}")
            numeric_id = match.group(1)
            if numeric_id in seen:
                raise SystemExit(f"Line {line}: duplicate numeric ID {numeric_id}")
            seen.add(numeric_id)
            stories.append({"id": numeric_id, "art_id": art_id, "title": row["Nazwa Karty"].strip(), "story": row["Narracja"].strip(), "versions": []})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"stories": stories}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Imported {len(stories)} stories from {args.csv_file} into {args.output}")

if __name__ == "__main__":
    main()
