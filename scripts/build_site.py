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
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    args.output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(Path("site"), args.output, dirs_exist_ok=True)
    # Templates and example configuration are source files, not public assets.
    for private_file in (args.output / "story-template.html", args.output / "data/config.example.json"):
        if private_file.exists(): private_file.unlink()
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    (args.output / "data").mkdir(exist_ok=True)
    config = Path("site/data/config.example.json")
    if config.is_file():
        shutil.copy2(config, args.output / "data/config.json")

    # The catalog uses root-relative paths for the homepage. Story pages rewrite
    # those paths to their own nested URL depth without mutating catalog data.
    if args.audio_root:
        audio_out = args.output / "audio"
        audio_out.mkdir(exist_ok=True)
        for story in data.get("stories", []):
            for version in story.get("versions", []):
                source = args.audio_root / f"{story['id']}.mp3"
                if source.is_file():
                    shutil.copy2(source, audio_out / source.name)
                    version["audio"] = f"audio/{source.name}"

    (args.output / "data/catalog.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    template = Path("site/story-template.html").read_text(encoding="utf-8")
    for story in data.get("stories", []):
        versions = story.get("versions", [])
        cards = []
        for version in versions:
            audio = version.get("audio", "").replace("audio/", "../../audio/", 1)
            score = version.get("score")
            label = f"{score}/15" if score is not None else "oczekuje na ocenę"
            cards.append(
                f'<div class="version"><div><strong>{version["label"]}</strong>'
                f'<br><small>{label}</small></div><audio controls preload="none" '
                f'src="{audio}"></audio></div>'
            )
        latest = versions[-1]["label"] if versions else "v1"
        page = (template.replace("__ID__", str(story["id"]))
                .replace("__TITLE__", story["title"])
                .replace("__STORY__", story["story"])
                .replace("__VERSIONS__", "".join(cards))
                .replace("__LATEST__", latest))
        destination = args.output / "stories" / str(story["id"]) / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
