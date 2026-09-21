#!/usr/bin/env python3
"""Build a flat ZIP containing the best rated MP3 for each story.

Input JSON format:
{
  "stories": [
    {"id": "67", "ratings": [{"version": "v1", "audio": "...", "scores": {"feeling": 4, "story_fit": 5, "sample_quality": 3}}]}
  ]
}
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

FIELDS = ("feeling", "story_fit", "sample_quality")


def score(rating: dict) -> int:
    scores = rating.get("scores", {})
    values = [scores.get(field) for field in FIELDS]
    if any(not isinstance(value, int) or not 1 <= value <= 5 for value in values):
        raise ValueError(f"Invalid scores in rating: {rating!r}")
    return sum(values)


def best_rating(story: dict) -> dict | None:
    rated = [item for item in story.get("ratings", []) if item.get("audio")]
    if not rated:
        return None
    # Stable tie-breakers: feeling, story fit, sample quality, then older version.
    return max(
        rated,
        key=lambda item: (score(item), item["scores"]["feeling"],
                          item["scores"]["story_fit"],
                          item["scores"]["sample_quality"],
                          -int(str(item.get("version", "v0")).lstrip("v"))),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--versions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.versions.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    included = 0

    with tempfile.TemporaryDirectory() as temp:
        staging = Path(temp)
        for story in data.get("stories", []):
            chosen = best_rating(story)
            if not chosen:
                continue
            source = Path(chosen["audio"])
            if not source.is_file() or source.suffix.lower() != ".mp3":
                raise FileNotFoundError(f"Missing MP3 for {story.get('id')}: {source}")
            shutil.copy2(source, staging / f"{story['id']}.mp3")
            included += 1
        with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(staging.glob("*.mp3"), key=lambda item: int(item.stem) if item.stem.isdigit() else item.stem):
                archive.write(path, arcname=path.name)

    print(f"Created {args.output} with {included} MP3 file(s)")


if __name__ == "__main__":
    main()
