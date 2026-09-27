#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate one ElevenLabs sound-effect prompt per story.

This is the simplified v2 pipeline requested after g035:

    catalog/profile -> one semantic SFX scenario -> one generated <id>.mp3

The script does NOT call any external API. It writes a stable JSONL prompt
manifest that can be reviewed, versioned, and fed into scripts/elevenlabs_soundgen.py.

Usage:
  python scripts/generate_ai_sound_prompts.py \
    --catalog data/catalog.json \
    --profiles data/semantics/story-profiles.json \
    --out data/ai-sfx/prompts.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NEGATIVE = (
    "No music, no melody, no song, no spoken words, no narration, no UI beeps, "
    "no modern studio whoosh unless the scene is explicitly magical or technical. "
    "Nonverbal creature or human vocalizations are allowed only when explicitly described."
)


POLISH_HINTS = {
    # Keep this intentionally small and conservative: it nudges the English
    # wrapper while preserving the unique Polish semantic profile verbatim.
    "kruk": "raven call",
    "wrona": "crow call",
    "ogień": "fire",
    "płomień": "flame",
    "wod": "water splash",
    "plusk": "splash",
    "morze": "sea",
    "las": "forest",
    "noc": "night",
    "burza": "storm",
    "wiatr": "wind",
    "jaskinia": "cave",
    "podziem": "underground",
    "kuźnia": "forge",
    "młot": "hammer",
    "metal": "metal",
    "laboratorium": "laboratory",
    "maszyna": "machine",
    "mechan": "mechanism",
    "świątynia": "temple",
    "sanktuarium": "sanctuary",
    "dzwon": "bell",
    "smok": "dragon",
    "bestia": "beast",
    "chochlik": "imp giggle",
    "chichot": "malicious giggle",
    "krzyk": "scream or call",
    "wilkołak": "werewolf",
    "zombie": "zombie",
    "szkielet": "skeleton",
    "portal": "portal",
    "zaklęcie": "spell",
    "magia": "magic",
    "krew": "blood",
    "kości": "bones",
}


SAFE_WS = re.compile(r"\s+")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compact(text: str, limit: int) -> str:
    text = SAFE_WS.sub(" ", (text or "").strip())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:.-")
    return cut + "…"


def keyword_hints(*texts: str) -> list[str]:
    hay = " ".join(texts).lower()
    out: list[str] = []
    for needle, hint in POLISH_HINTS.items():
        if needle in hay and hint not in out:
            out.append(hint)
    return out[:8]


def load_profiles(path: Path | None) -> dict[str, dict]:
    if not path or not path.exists():
        return {}
    data = read_json(path)
    return data.get("profiles", {})


def make_prompt(story: dict, profile: dict | None, duration: float) -> tuple[str, dict]:
    title = story["title"]
    narrative = story.get("story", "")
    sid = str(story["id"])

    if profile:
        bg = profile.get("background", {})
        hero = profile.get("hero", {})
        mood = profile.get("mood", {})
        instr = profile.get("instrumentation", {})
        bg_text = bg.get("opis", "")
        hero_text = hero.get("opis", "")
        mood_text = mood.get("opis", "")
        instr_text = instr.get("opis", "")
        hints = keyword_hints(bg_text, hero_text, mood_text, instr_text, narrative)
        prompt = (
            f"Create a unique {duration:.1f}-second non-musical fantasy game sound effect for story #{sid}, '{title}'. "
            f"Audible place: {compact(bg_text, 180)}. "
            f"Main event: {compact(hero_text, 220)}. "
            f"Emotional color: {compact(mood_text, 120)}. "
            f"Texture: {compact(instr_text, 120)}. "
            f"Make it one coherent short audio scene with a clear beginning, one signature event, and a natural tail. "
            f"Useful sound anchors: {', '.join(hints) if hints else 'scene-specific ambience and one clear physical or magical event'}. "
            f"{DEFAULT_NEGATIVE}"
        )
        analysis = {
            "background": bg_text,
            "hero": hero_text,
            "mood": mood_text,
            "instrumentation": instr_text,
            "hints": hints,
            "source": "story-profiles",
        }
    else:
        hints = keyword_hints(narrative)
        prompt = (
            f"Create a unique {duration:.1f}-second non-musical fantasy game sound effect for story #{sid}, '{title}'. "
            f"Base it on this scene: {compact(narrative, 700)}. "
            f"Make it one coherent short audio scene with a clear place, one signature event, and a natural tail. "
            f"Useful sound anchors: {', '.join(hints) if hints else 'scene-specific ambience and one clear physical or magical event'}. "
            f"{DEFAULT_NEGATIVE}"
        )
        analysis = {"hints": hints, "source": "catalog-story"}

    return compact(prompt, 1250), analysis


def iter_selected(stories: list[dict], ids: set[str] | None, limit: int | None) -> list[dict]:
    selected = [s for s in stories if ids is None or str(s["id"]) in ids]
    selected.sort(key=lambda s: int(s["id"]))
    if limit is not None:
        selected = selected[:limit]
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/catalog.json")
    parser.add_argument("--profiles", type=Path, default=ROOT / "data/semantics/story-profiles.json")
    parser.add_argument("--out", type=Path, default=ROOT / "data/ai-sfx/prompts.jsonl")
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--ids", help="Comma-separated story IDs to include")
    parser.add_argument("--limit", type=int, help="Only first N selected stories")
    args = parser.parse_args()

    catalog = read_json(args.catalog)
    profiles = load_profiles(args.profiles)
    ids = {x.strip() for x in args.ids.split(",") if x.strip()} if args.ids else None
    stories = iter_selected(catalog.get("stories", []), ids, args.limit)
    if ids:
        found = {str(s["id"]) for s in stories}
        missing = sorted(ids - found, key=lambda x: int(x) if x.isdigit() else x)
        if missing:
            raise SystemExit(f"Unknown story IDs in --ids: {missing}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for story in stories:
            sid = str(story["id"])
            prompt, analysis = make_prompt(story, profiles.get(sid), args.duration)
            row = {
                "story_id": sid,
                "art_id": story.get("art_id"),
                "title": story.get("title"),
                "duration_seconds": args.duration,
                "prompt": prompt,
                "negative_prompt": DEFAULT_NEGATIVE,
                "semantic_analysis": analysis,
            }
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"{args.out}: {len(stories)} prompts")


if __name__ == "__main__":
    main()
