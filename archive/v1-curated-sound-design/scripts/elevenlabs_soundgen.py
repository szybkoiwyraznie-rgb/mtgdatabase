#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate one MP3 per story from the v2 AI-SFX prompt manifest.

Requires ELEVENLABS_API_KEY in the environment. This script is intentionally
sequential and resumable: already existing <id>.mp3 files are skipped unless
--force is passed, so large batches can be restarted safely.

Default endpoint matches ElevenLabs text-to-sound-effects API shape used by
ElevenLabs Sound Generation. If the API changes, override with
ELEVENLABS_SOUNDGEN_ENDPOINT without touching committed code.

Usage:
  ELEVENLABS_API_KEY=... python scripts/elevenlabs_soundgen.py \
    --prompts data/ai-sfx/prompts.jsonl \
    --out audio/ai-signatures \
    --manifest data/ai-sfx/generated-manifest.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENDPOINT = "https://api.elevenlabs.io/v1/sound-generation"


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            rows.append(row)
    return rows


def parse_ids(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {x.strip() for x in value.split(",") if x.strip()}


def select_rows(rows: list[dict], ids: set[str] | None, limit: int | None) -> list[dict]:
    out = [r for r in rows if ids is None or str(r["story_id"]) in ids]
    out.sort(key=lambda r: int(str(r["story_id"])))
    if ids:
        found = {str(r["story_id"]) for r in out}
        missing = sorted(ids - found, key=lambda x: int(x) if x.isdigit() else x)
        if missing:
            raise SystemExit(f"Unknown story IDs in --ids: {missing}")
    if limit is not None:
        out = out[:limit]
    return out


def request_sound(api_key: str, endpoint: str, row: dict, prompt_influence: float, timeout: int) -> bytes:
    payload = {
        "text": row["prompt"],
        "duration_seconds": float(row.get("duration_seconds") or 6.0),
        "prompt_influence": float(prompt_influence),
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        method="POST",
        headers={
            "xi-api-key": api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "User-Agent": "mtgdatabase-ai-sfx/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - configured endpoint only
        content_type = resp.headers.get("Content-Type", "")
        body = resp.read()
    if not body:
        raise RuntimeError("empty response body")
    if "json" in content_type.lower():
        raise RuntimeError(f"API returned JSON instead of audio: {body[:500]!r}")
    return body


def append_manifest(path: Path, row: dict, out_file: Path, status: str, error: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "story_id": str(row["story_id"]),
        "title": row.get("title"),
        "duration_seconds": row.get("duration_seconds"),
        "prompt": row.get("prompt"),
        "file": str(out_file.as_posix()),
        "status": status,
        "generated_at_unix": int(time.time()),
    }
    if error:
        rec["error"] = error
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", type=Path, default=ROOT / "data/ai-sfx/prompts.jsonl")
    parser.add_argument("--out", type=Path, default=ROOT / "audio/ai-signatures")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/ai-sfx/generated-manifest.jsonl")
    parser.add_argument("--ids", help="Comma-separated story IDs to generate")
    parser.add_argument("--limit", type=int, help="Only first N selected rows")
    parser.add_argument("--force", action="store_true", help="Regenerate even if <id>.mp3 already exists")
    parser.add_argument("--dry-run", action="store_true", help="Print selected prompts but do not call the API")
    parser.add_argument("--prompt-influence", type=float, default=0.35)
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between successful calls")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    rows = select_rows(read_jsonl(args.prompts), parse_ids(args.ids), args.limit)
    args.out.mkdir(parents=True, exist_ok=True)
    print(f"selected {len(rows)} prompts from {args.prompts}")

    if args.dry_run:
        for row in rows:
            print(f"{row['story_id']}.mp3 — {row.get('title')}: {row['prompt']}")
        return

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("ELEVENLABS_API_KEY is missing. Add it as a GitHub secret or environment variable.")
    endpoint = os.environ.get("ELEVENLABS_SOUNDGEN_ENDPOINT") or DEFAULT_ENDPOINT

    ok = skipped = failed = 0
    for row in rows:
        sid = str(row["story_id"])
        out_file = args.out / f"{sid}.mp3"
        if out_file.exists() and out_file.stat().st_size > 0 and not args.force:
            print(f"SKIP {sid}: {out_file} exists")
            append_manifest(args.manifest, row, out_file, "skipped-existing")
            skipped += 1
            continue
        last_error: str | None = None
        for attempt in range(args.retries + 1):
            try:
                audio = request_sound(api_key, endpoint, row, args.prompt_influence, args.timeout)
                out_file.write_bytes(audio)
                if out_file.stat().st_size < 1024:
                    raise RuntimeError(f"generated file suspiciously small: {out_file.stat().st_size} bytes")
                print(f"OK {sid}: {out_file} ({out_file.stat().st_size} bytes)")
                append_manifest(args.manifest, row, out_file, "generated")
                ok += 1
                last_error = None
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, RuntimeError) as exc:
                if isinstance(exc, urllib.error.HTTPError):
                    try:
                        body = exc.read().decode("utf-8", "replace")[:1000]
                    except Exception:
                        body = ""
                    last_error = f"HTTP {exc.code}: {body or exc.reason}"
                else:
                    last_error = str(exc)
                wait = min(30.0, 2.0 * (attempt + 1))
                print(f"WARN {sid}: attempt {attempt + 1}/{args.retries + 1}: {last_error}", file=sys.stderr)
                if attempt < args.retries:
                    time.sleep(wait)
        if last_error:
            print(f"FAIL {sid}: {last_error}", file=sys.stderr)
            append_manifest(args.manifest, row, out_file, "failed", last_error)
            failed += 1
        time.sleep(args.sleep)

    print(f"done: generated={ok}, skipped={skipped}, failed={failed}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
