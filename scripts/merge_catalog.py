#!/usr/bin/env python3
"""Merge collection.csv stories with generated jingle/version state."""
from __future__ import annotations
import argparse, json, subprocess, tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--versions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.NamedTemporaryFile(suffix=".json") as imported:
        subprocess.run(["python", "scripts/import_collection.py", str(args.collection), "--output", imported.name], check=True, capture_output=True)
        catalog = json.loads(Path(imported.name).read_text(encoding="utf-8"))
    version_data = json.loads(args.versions.read_text(encoding="utf-8"))
    versions = {str(item["id"]): item.get("versions", item.get("ratings", [])) for item in version_data.get("stories", [])}
    visible = []
    for story in catalog["stories"]:
        story["versions"] = versions.get(story["id"], [])
        if story["versions"]:
            visible.append(story)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"stories": visible}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Merged {len(visible)} story/stories with existing jingles")

if __name__ == "__main__":
    main()
