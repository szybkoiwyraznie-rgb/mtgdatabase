#!/usr/bin/env python3
"""Close needs-review reports that a newer rendered version already serves.

Queue semantics (docs/feedback-system.md): an open `needs-review` issue with
marker <!-- jingle-feedback: ID:vN --> is served once data/versions.json on
the current branch contains a version vM for story ID with M > N (a newer
render exists). The script posts a short resolution comment and closes such
issues via the GitHub REST API. Idempotent: closed issues are not fetched
again, so reruns are no-ops. Never closes a report about the newest version
(still awaiting its own rating).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from sync_ratings import MARKER, decode_issue_stream
except ImportError:  # pragma: no cover - defensive for unusual import paths
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from sync_ratings import MARKER, decode_issue_stream


def latest_versions(data: dict) -> dict[str, tuple[int, str]]:
    latest: dict[str, tuple[int, str]] = {}
    for story in data.get("stories", []):
        sid = str(story.get("id"))
        best: tuple[int, str] | None = None
        for version in story.get("versions", []):
            label = str(version.get("label", ""))
            number = int(label[1:]) if label.startswith("v") and label[1:].isdigit() else -1
            if best is None or number > best[0]:
                best = (number, label)
        if best and best[0] >= 0:
            latest[sid] = best
    return latest


def fetch_open_reports() -> list[dict]:
    if not os.environ.get("GH_TOKEN"):
        sys.exit("GH_TOKEN is required unless --issues-file is used")
    cmd = ["gh", "api", "repos/{owner}/{repo}/issues?labels=needs-review&state=open&per_page=100", "--paginate"]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    return decode_issue_stream(out)


def serve_issue(issue_number: int, story_id: str, label: str, repo: str, dry_run: bool) -> None:
    comment = (f"Raport obsłużony automatycznie: dla fabuły {story_id} jest już nowsza wersja {label} "
               f"(render opublikowany). Strona i paczka przebudują się w ciągu kilku minut.")
    if dry_run:
        print(f"dry-run: would close issue #{issue_number} (story {story_id} served by {label})")
        return
    subprocess.run(["gh", "api", f"repos/{repo}/issues/{issue_number}/comments", "-f", f"body={comment}"],
                   check=True, capture_output=True)
    subprocess.run(["gh", "api", "--method", "PATCH", f"repos/{repo}/issues/{issue_number}", "-f", "state=closed"],
                   check=True, capture_output=True)
    print(f"closed issue #{issue_number} (story {story_id} served by {label})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--versions", type=Path, required=True)
    parser.add_argument("--issues-file", type=Path, help="Offline issues JSON instead of gh api (tests).")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""),
                        help="owner/repo (default: $GITHUB_REPOSITORY)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.versions.read_text(encoding="utf-8"))
    latest = latest_versions(data)
    if args.issues_file:
        issues = decode_issue_stream(args.issues_file.read_text(encoding="utf-8"))
    else:
        issues = fetch_open_reports()

    closed = 0
    for issue in issues:
        if issue.get("state") != "open":
            continue
        marker = MARKER.search(issue.get("body") or "")
        if not marker:
            continue
        story_id, label = marker.group("story"), marker.group("version")
        reported_n = int(label[1:])
        best = latest.get(story_id)
        if best and best[0] > reported_n:
            serve_issue(int(issue["number"]), story_id, best[1], args.repo, args.dry_run)
            closed += 1
    print(f"Reports served by newer versions: {closed} closed (of {len(issues)} open needs-review issue(s) scanned).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
