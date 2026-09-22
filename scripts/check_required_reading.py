#!/usr/bin/env python3
"""Check the size of the documents every agent must read."""
from __future__ import annotations
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ["AGENTS.md", "README.md", "CONTRIBUTING.md", "ENVIRONMENT.md", "docs/required-reading.md", "docs/agent-workflow.md", "docs/architecture.md", "docs/feedback-system.md", "docs/sources-and-licensing.md", "docs/LESSONS.md"]

def estimate_tokens(text: str) -> int:
    # Conservative, dependency-free estimate; real tokenizer counts may differ.
    return max(1, (len(text) + 3) // 4)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-tokens", type=int, default=50_000)
    args = parser.parse_args()
    paths = [ROOT / item for item in BASE]
    paths += sorted((ROOT / "docs/decisions").glob("*.md"))
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        print("Missing required-reading files: " + ", ".join(missing))
        return 1
    total = sum(estimate_tokens(path.read_text(encoding="utf-8")) for path in paths)
    print(f"Required reading estimate: {total} / {args.max_tokens} tokens ({len(paths)} files)")
    if total > args.max_tokens:
        print("ERROR: reduce duplication or move historical detail to docs/archive/ without losing decisions, rules, or procedures.")
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
