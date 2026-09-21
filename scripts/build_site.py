#!/usr/bin/env python3
"""Build the static Pages preview from a catalog JSON."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audio-root", type=Path)
    args = parser.parse_args()

    if args.output.exists():
        for child in args.output.iterdir():
            if child.is_dir(): shutil.rmtree(child)
            else: child.unlink()
    args.output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(Path("site"), args.output, dirs_exist_ok=True)
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    (args.output / "data").mkdir(exist_ok=True)
    (args.output / "data/catalog.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.audio_root:
        audio_out = args.output / "audio"
        audio_out.mkdir(exist_ok=True)
        for story in data.get("stories", []):
            for version in story.get("versions", []):
                source = args.audio_root / f"{story['id']}.mp3"
                if source.is_file():
                    shutil.copy2(source, audio_out / source.name)
                    version["audio"] = f"audio/{source.name}"
        (args.output / "data/catalog.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
