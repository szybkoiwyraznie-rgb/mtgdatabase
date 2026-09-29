#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate v2 sample scenarios.

A scenario is not a layered design. It is a short, homogeneous sample idea for
one story, for example: "krakanie wron", "pojedyncze uderzenie dzwonu",
"szczęk bitwy", "upadek zbroi na kamień".

Schema: one JSON object per line in data/samples/scenarios.jsonl.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = {"story_id", "title", "sample_scenario", "prompt", "duration_seconds", "status", "batch"}
STATUSES = {"draft", "ready", "generated", "rejected"}
BANNED_LAYER_WORDS = re.compile(r"\b(hero|coda|koda|background|tło|warstwa|layers?|mix)\b", re.I)
# Źródła muzyczne dopuszczalne przy music_allowed — instrument musi być
# nazwany, bo wyjątek dotyczy grania w kadrze, nie podkładu muzycznego.
MUSICAL_SOURCE = re.compile(
    r"fujark|piszczał|flet|fife|skrzypc|fiddle|lutni|lute|harf|harp|"
    r"bęb[ne]|drum|tambouryn|tambourine|cymbał|dulcimer|lir[aey]|lyre|"
    r"róg\b|rogu\b|horn|trąb|trumpet|dzwon|bell|gong|organ|kobz|bagpipe|"
    r"grzechotk|rattle|klekotk|struny|strings|instrument|melodi|melody|"
    r"przyśpiew|nuc|hum\b|śpiew|chant|sing", re.I)


def read_catalog(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(s["id"]): s for s in data.get("stories", [])}


def read_jsonl(path: Path) -> list[tuple[int, dict]]:
    rows: list[tuple[int, dict]] = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            raw = line.strip()
            if not raw:
                continue
            try:
                rows.append((line_no, json.loads(raw)))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def validate_row(row: dict, line_no: int, catalog: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED - set(row)
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
        return errors
    sid = str(row["story_id"])
    if not sid.isdigit():
        errors.append("story_id must be numeric string/int")
    elif catalog and sid not in catalog:
        errors.append(f"story_id {sid} not found in catalog")
    status = str(row["status"])
    if status not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}, got {status!r}")
    try:
        duration = float(row["duration_seconds"])
    except Exception:
        errors.append("duration_seconds must be numeric")
        duration = 0.0
    if not (0.8 <= duration <= 5.0):
        errors.append("duration_seconds must be 0.8..5.0 for short samples")
    scenario = str(row["sample_scenario"]).strip()
    prompt = str(row["prompt"]).strip()
    if len(scenario) < 12:
        errors.append("sample_scenario too short")
    if len(scenario) > 220:
        errors.append("sample_scenario too long; keep one focused sound")
    if len(prompt) < 30:
        errors.append("prompt too short")
    if len(prompt) > 650:
        errors.append("prompt too long; keep it focused on one sample")
    if BANNED_LAYER_WORDS.search(scenario) or BANNED_LAYER_WORDS.search(prompt):
        errors.append("scenario/prompt mentions layered v1 concepts; v2 must be one homogeneous sample")
    # Muzyka jest domyślnie zakazana, ale NIE jest zakazana bezwzględnie.
    # Jeśli fabuła stawia instrument w centrum zdarzenia (bard z lutnią,
    # myszy grające w marszu, róg bojowy), to sample MA być muzyczny —
    # jako źródło dźwięku w kadrze, nie jako podkład pod scenę.
    # Wyjątek trzeba zadeklarować wprost polem music_allowed.
    if row.get("music_allowed"):
        if not MUSICAL_SOURCE.search(scenario) and not MUSICAL_SOURCE.search(prompt):
            errors.append("music_allowed set but no instrument/musical source named; "
                          "name the instrument that is played in frame")
        if "no speech" not in prompt.lower() and "no narration" not in prompt.lower():
            errors.append("music_allowed still requires forbidding speech in prompt")
    elif "music" not in prompt.lower() and "muzyk" not in prompt.lower():
        errors.append("prompt should explicitly forbid music")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenarios", type=Path, nargs="?", default=ROOT / "data/samples/scenarios.jsonl")
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/catalog.json")
    args = parser.parse_args()
    catalog = read_catalog(args.catalog)
    rows = read_jsonl(args.scenarios)
    seen: dict[str, int] = {}
    ok = True
    ready = 0
    for line_no, row in rows:
        sid = str(row.get("story_id", ""))
        if sid in seen:
            print(f"{args.scenarios}:{line_no}: duplicate story_id {sid} (first at line {seen[sid]})", file=sys.stderr)
            ok = False
        else:
            seen[sid] = line_no
        errors = validate_row(row, line_no, catalog)
        if str(row.get("status")) == "ready":
            ready += 1
        for err in errors:
            print(f"{args.scenarios}:{line_no}: {err}", file=sys.stderr)
            ok = False
    print(f"Sample scenarios: {len(rows)} total, {ready} ready")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
