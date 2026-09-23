#!/usr/bin/env python3
"""Build a flat ZIP containing the best rated MP3 for each story.

Input JSON format (data/versions.json):
{
  "stories": [
    {"id": "67", "versions": [{"label": "v1", "audio": "path/to/67.mp3",
      "scores": {"feeling": 4, "story_fit": 5, "sample_quality": 3}}]}
  ]
}

Only versions with a complete, valid 1-5 user rating are considered; unrated
versions are skipped (never crash the release). The legacy "ratings" key with
"version" labels is still accepted as a fallback.
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

FIELDS = ("feeling", "story_fit", "sample_quality")


def entries_of(story: dict) -> list[dict]:
    return story.get("versions", story.get("ratings", []))


def label_of(entry: dict) -> str:
    return str(entry.get("version", entry.get("label", "v0")))


def valid_scores(entry: dict) -> bool:
    scores = entry.get("scores") or {}
    values = [scores.get(field) for field in FIELDS]
    return all(isinstance(value, int) and 1 <= value <= 5 for value in values)


def score(entry: dict) -> int:
    return sum(int(entry["scores"][field]) for field in FIELDS)


def best_entry(story: dict) -> dict | None:
    candidates = [entry for entry in entries_of(story) if entry.get("audio") and valid_scores(entry)]
    if not candidates:
        return None
    # Stable tie-breakers: feeling, story fit, sample quality, then older version.
    return max(
        candidates,
        key=lambda entry: (score(entry), entry["scores"]["feeling"],
                           entry["scores"]["story_fit"],
                           entry["scores"]["sample_quality"],
                           -int(label_of(entry).lstrip("v"))),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--versions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.versions.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    included = 0
    skipped = 0

    with tempfile.TemporaryDirectory() as temp:
        staging = Path(temp)
        for story in data.get("stories", []):
            chosen = best_entry(story)
            if not chosen:
                skipped += 1
                continue
            source = Path(chosen["audio"])
            if not source.is_file() or source.suffix.lower() != ".mp3":
                raise FileNotFoundError(f"Missing MP3 for {story.get('id')}: {source}")
            shutil.copy2(source, staging / f"{story['id']}.mp3")
            included += 1
        with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(staging.glob("*.mp3"), key=lambda item: int(item.stem) if item.stem.isdigit() else item.stem):
                archive.write(path, arcname=path.name)

    print(f"Created {args.output} with {included} MP3 file(s); {skipped} stor(y/ies) without ratings skipped")


if __name__ == "__main__":
    main()
