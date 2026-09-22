#!/usr/bin/env python3
"""Sync feedback issue ratings into data/versions.json.

Feedback issues are created by the Cloudflare worker from the Pages form
(labels: feedback, needs-review, story:<id>). The newest issue per
(story_id, version) defines the current score, while every issue is kept in
the per-version "reports" history. Ratings apply only to stories/versions
that already exist in --versions (rendered jingles); unknown targets are
reported and skipped so the file always passes validate_versions.py.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

FIELDS = ("feeling", "story_fit", "sample_quality")
FIELD_LABELS = {"feeling": "Feeling", "story_fit": "Story fit", "sample_quality": "Sample quality"}
MARKER = re.compile(r"<!-- jingle-feedback: (?P<story>[A-Za-z0-9_-]{1,64}):(?P<version>v[0-9]+) -->")


def decode_issue_stream(text: str) -> list[dict]:
    # `gh api --paginate` prints one JSON array per page, back to back; plain
    # json.loads rejects such a stream once feedback grows past the first page.
    issues: list[dict] = []
    decoder = json.JSONDecoder()
    index = 0
    length = len(text)
    while index < length:
        while index < length and text[index] in " \r\n\t":
            index += 1
        if index >= length:
            break
        page, index = decoder.raw_decode(text, index)
        issues.extend(item for item in page if "pull_request" not in item)
    return issues


def fetch_issues() -> list[dict]:
    if not os.environ.get("GH_TOKEN"):
        sys.exit("GH_TOKEN is required unless --issues-file is used")
    cmd = ["gh", "api", "repos/{owner}/{repo}/issues?labels=feedback&state=all&per_page=100", "--paginate"]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    return decode_issue_stream(out)


def parse_issue(issue: dict) -> dict | None:
    body = issue.get("body") or ""
    marker = MARKER.search(body)
    if not marker:
        return None
    scores: dict[str, int] = {}
    for field, label in FIELD_LABELS.items():
        found = re.search(rf"\*\*{re.escape(label)}:\*\*\s*([0-9]+)/5", body)
        if not found:
            return None
        scores[field] = int(found.group(1))
    if not all(1 <= value <= 5 for value in scores.values()):
        return None
    comment = ""
    comment_match = re.search(r"\*\*Comment:\*\*\s*(.+)", body, re.S)
    if comment_match:
        comment = comment_match.group(1).strip()
        if comment == "_No comment._":
            comment = ""
    return {
        "story_id": marker.group("story"),
        "version": marker.group("version"),
        "scores": scores,
        "total": sum(scores.values()),
        "comment": comment,
        "issue_url": issue.get("html_url", ""),
        "created_at": issue.get("created_at", ""),
        "state": issue.get("state", "open"),
    }


def apply_ratings(data: dict, ratings: list[dict]) -> tuple[int, int, list[str]]:
    stories = {str(story.get("id")): story for story in data.get("stories", [])}
    applied_targets: set[tuple[str, str]] = set()
    skipped_notes: dict[tuple[str, str], str] = {}

    # Chronological pass: every report lands in history, the newest one wins
    # the current score. Re-runs are idempotent via issue_url dedupe.
    for rating in sorted(ratings, key=lambda item: item.get("created_at", "")):
        story_id, label = rating["story_id"], rating["version"]
        story = stories.get(story_id)
        version = next((v for v in (story or {}).get("versions", []) if v.get("label") == label), None)
        if version is None:
            note = f"{story_id} {label}: brak wyrenderowanej wersji w pliku wersji (issue {rating['issue_url']})"
            if (story_id, label) not in skipped_notes:
                skipped_notes[(story_id, label)] = note
                print(f"skip: {note}")
            continue
        version["scores"] = rating["scores"]
        version["score"] = rating["total"]
        version["rated_at"] = rating["created_at"]
        version["feedback_issue"] = rating["issue_url"]
        reports = version.setdefault("reports", [])
        existing = next((report for report in reports if report.get("issue_url") == rating["issue_url"]), None)
        if existing is None:
            reports.append({
                "issue_url": rating["issue_url"],
                "created_at": rating["created_at"],
                "state": rating["state"],
                "scores": rating["scores"],
                "total": rating["total"],
                "comment": rating["comment"],
            })
            reports.sort(key=lambda report: report.get("created_at", ""))
        else:
            # Issues get closed by close_served_reports after a newer version
            # ships; history stays, but the mutable state must refresh so the
            # remake queue (scripts/remake_queue.py) sees the real status.
            existing["state"] = rating["state"]
        applied_targets.add((story_id, label))
    return len(applied_targets), len(skipped_notes), sorted(skipped_notes.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--versions", type=Path, required=True)
    parser.add_argument("--issues-file", type=Path, help="Offline issues JSON instead of gh api (tests).")
    args = parser.parse_args()

    data = json.loads(args.versions.read_text(encoding="utf-8"))
    if args.issues_file:
        issues = decode_issue_stream(args.issues_file.read_text(encoding="utf-8"))
    else:
        issues = fetch_issues()

    ratings = [parsed for parsed in (parse_issue(issue) for issue in issues) if parsed]
    applied, skipped, _notes = apply_ratings(data, ratings)
    args.versions.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Parsed {len(ratings)} feedback issue(s); applied {applied} rating(s), skipped {skipped}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
