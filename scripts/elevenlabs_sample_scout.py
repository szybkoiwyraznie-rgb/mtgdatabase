#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ElevenLabs scout for v2 homogeneous story samples.

Input: data/samples/scenarios.jsonl, hand-written in small batches.
Output: audio/samples/<id>.mp3 plus data/samples/generated-manifest.jsonl.

Secret/env: ELEVENLABS. Token budget is limited, so the script is resumable and
small-batch friendly. It only generates rows with status=ready by default.
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
NEGATIVE = "No music, no melody, no speech, no narration, no ambience bed, no multi-layer cinematic scene."


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            raw = line.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            row["_line"] = line_no
            rows.append(row)
    return rows


def parse_ids(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {x.strip() for x in value.split(",") if x.strip()}


def select_rows(rows: list[dict], ids: set[str] | None, batch: str | None, include_drafts: bool, limit: int | None) -> list[dict]:
    selected = []
    for row in rows:
        sid = str(row["story_id"])
        if ids is not None and sid not in ids:
            continue
        if batch and str(row.get("batch")) != batch:
            continue
        if not include_drafts and row.get("status") != "ready":
            continue
        selected.append(row)
    selected.sort(key=lambda r: int(str(r["story_id"])))
    if ids:
        found = {str(r["story_id"]) for r in selected}
        missing = sorted(ids - found, key=lambda x: int(x) if x.isdigit() else x)
        if missing:
            raise SystemExit(f"No selected ready scenario for IDs: {missing}")
    if limit is not None:
        selected = selected[:limit]
    return selected


def api_payload(row: dict, prompt_influence: float) -> dict:
    prompt = str(row["prompt"]).strip()
    low = prompt.lower()
    additions: list[str] = []
    # music_allowed = fabuła uzasadnia grę na instrumencie w kadrze
    # (bard, myszy z fujarkami, róg bojowy). Wtedy NIE dopisujemy zakazu,
    # bo skasowałby sens promptu. Zakaz mowy zostaje zawsze.
    if not row.get("music_allowed") and "no music" not in low:
        additions.append("No music.")
    if "no speech" not in low and "no spoken" not in low:
        additions.append("No speech.")
    if "no ambience bed" not in low and "no ambient bed" not in low:
        additions.append("No ambience bed.")
    if "multi-layer" not in low and "full scene" not in low:
        additions.append("No multi-layer cinematic scene.")
    if additions:
        prompt = f"{prompt} {' '.join(additions)}"
    return {
        "text": prompt,
        "duration_seconds": float(row.get("duration_seconds") or 2.5),
        "prompt_influence": float(prompt_influence),
    }


def request_sound(api_key: str, endpoint: str, row: dict, prompt_influence: float, timeout: int) -> bytes:
    data = json.dumps(api_payload(row, prompt_influence), ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        method="POST",
        headers={
            "xi-api-key": api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "User-Agent": "mtgdatabase-elevenlabs-sample-scout/2.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - configured API endpoint
        body = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    if not body:
        raise RuntimeError("empty response body")
    if "json" in ctype.lower():
        raise RuntimeError(f"API returned JSON instead of audio: {body[:500]!r}")
    return body


def append_manifest(path: Path, row: dict, out_file: Path, status: str, error: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "story_id": str(row["story_id"]),
        "title": row.get("title"),
        "batch": row.get("batch"),
        "duration_seconds": row.get("duration_seconds"),
        "sample_scenario": row.get("sample_scenario"),
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
    parser.add_argument("--scenarios", type=Path, default=ROOT / "data/samples/scenarios.jsonl")
    parser.add_argument("--out", type=Path, default=ROOT / "audio/samples")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/samples/generated-manifest.jsonl")
    parser.add_argument("--ids", help="Comma-separated story IDs")
    parser.add_argument("--batch", help="Only one batch label, e.g. b001")
    parser.add_argument("--limit", type=int, help="Only first N selected ready scenarios")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--include-drafts", action="store_true", help="Allow status other than ready; mostly for local testing")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--prompt-influence", type=float, default=0.35)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    rows = select_rows(read_jsonl(args.scenarios), parse_ids(args.ids), args.batch, args.include_drafts, args.limit)
    print(f"selected {len(rows)} scenario(s)")
    if args.dry_run:
        for row in rows:
            payload = api_payload(row, args.prompt_influence)
            print(f"{row['story_id']}.mp3 — {row.get('title')} — {row.get('sample_scenario')}")
            print(f"  {payload['text']}")
        return

    api_key = os.environ.get("ELEVENLABS")
    if not api_key:
        raise SystemExit("Missing ELEVENLABS env var / GitHub secret")
    endpoint = os.environ.get("ELEVENLABS_SOUNDGEN_ENDPOINT") or DEFAULT_ENDPOINT
    args.out.mkdir(parents=True, exist_ok=True)

    generated = skipped = failed = 0
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
                generated += 1
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
                print(f"WARN {sid}: attempt {attempt + 1}/{args.retries + 1}: {last_error}", file=sys.stderr)
                if attempt < args.retries:
                    time.sleep(min(30, 2 * (attempt + 1)))
        if last_error:
            append_manifest(args.manifest, row, out_file, "failed", last_error)
            failed += 1
        time.sleep(args.sleep)
    print(f"done: generated={generated}, skipped={skipped}, failed={failed}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
