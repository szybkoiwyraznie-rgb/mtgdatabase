#!/usr/bin/env python3
"""Build the static Pages preview from a catalog JSON."""
from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path


def project_description_html(version: dict) -> str:
    design = version.get("project_description", {})
    if not design:
        return '<p class="missing-design">Brak opisu projektowego.</p>'
    events = "".join(
        f'<li><strong>{html.escape(str(event.get("time_sec", "?")))} s</strong> — '
        f'{html.escape(str(event.get("sample", "")))}'
        f' <span>{html.escape(str(event.get("role", "")))}</span></li>'
        for event in design.get("events", [])
    )
    qa = design.get("qa", {})
    qa_score = qa.get("score")
    qa_details = "&#10;".join(html.escape(str(item)) for item in qa.get("details", []))
    qa_badge = (f'<span class="qa-score" title="{qa_details}">QA Score: {qa_score}/100</span>'
                if qa_score is not None else '')
    return (
        '<div class="design"><div class="design-heading"><strong>Opis projektowy</strong>'
        f'{qa_badge}</div>'
        f'<p class="design-summary">{html.escape(str(design.get("description", design.get("summary", ""))) )}</p>'
        '<details open><summary>Szczegóły techniczne</summary>'
        '<dl>'
        f'<dt>Ambience</dt><dd>{html.escape(str(design.get("ambience", "—")))}</dd>'
        f'<dt>Drone</dt><dd>{html.escape(str(design.get("drone", "—")))}</dd>'
        '</dl>'
        f'<h4>Sample i timestampy</h4><ul>{events}</ul>'
        f'<p><strong>Uwagi miksu:</strong> {html.escape(str(design.get("mix_notes", "—")))}</p>'
        '</details></div>'
    )


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
    # Pages is a showcase of finished work, not a list of empty production slots.
    data["stories"] = [story for story in data.get("stories", []) if story.get("versions")]
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
            criteria = [("feeling", "Feeling ogólny"), ("story_fit", "Zgodność z fabułą"), ("sample_quality", "Jakość sampli")]
            fields = []
            for name, title in criteria:
                options = "".join(f'<label class="rating-option"><input type="radio" name="{name}" value="{value}" required>{value}</label>' for value in range(1, 6))
                fields.append(f'<fieldset><legend>{title}</legend><div class="rating-options">{options}</div></fieldset>')
            form = f'<form class="feedback" data-story="{story["id"]}" data-version="{version["label"]}">' + "".join(fields) + '<textarea name="comment" maxlength="2000" placeholder="Komentarz (opcjonalnie)"></textarea><button>Prześlij ocenę tej wersji</button><output></output></form>'
            cards.append(
                f'<section class="version"><div class="version-head"><strong>{version["label"]}</strong><small>{label}</small></div><div class="player"><audio controls preload="metadata"><source src="{audio}" type="audio/mpeg">Twoja przeglądarka nie obsługuje audio.</audio><a href="{audio}">Otwórz plik MP3</a></div>{project_description_html(version)}{form}</section>'
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
