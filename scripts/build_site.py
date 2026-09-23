#!/usr/bin/env python3
"""Build the static Pages preview from a catalog JSON."""
from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

CRITERIA = [
    ("feeling", "Feeling ogólny"),
    ("story_fit", "Zgodność z fabułą"),
    ("sample_quality", "Jakość sampli"),
]


def escape(value: object) -> str:
    """Escape every catalog value interpolated into generated HTML."""
    return html.escape(str(value), quote=True)


def project_description_html(version: dict) -> str:
    design = version.get("project_description", {})
    if not design:
        return '<p class="missing-design">Brak opisu projektowego.</p>'
    qa = design.get("qa", {})
    qa_score = qa.get("score")
    qa_details = "<br>".join(escape(item) for item in qa.get("details", []))
    qa_badge = (f'<span class="qa-score-wrap"><span class="qa-score">QA Score: {escape(qa_score)}/100</span>'
                f'<span class="qa-tooltip">{qa_details}</span></span>'
                if qa_score is not None else '')
    return (
        '<div class="design"><div class="design-heading"><strong>Opis projektowy</strong>'
        f'{qa_badge}</div>'
        f'<p class="design-summary">{escape(design.get("description", design.get("summary", "")))}</p>'
        '</div>'
    )


def version_number(version: dict) -> int:
    try:
        return int(str(version.get("label", "v0")).lstrip("v"))
    except ValueError:
        return 0


def rating_summary_html(version: dict) -> str:
    """Rated versions display their score, breakdown and the owner's comment."""
    score = version.get("score")
    scores = version.get("scores") or {}
    breakdown = "".join(
        f'<li>{title}: {escape(scores.get(name)) if scores.get(name) is not None else "–"}/5</li>'
        for name, title in CRITERIA
    )
    rated_at = version.get("rated_at")
    when = f' · oceniono {escape(str(rated_at).split("T")[0])}' if rated_at else ""
    # Owner request (2026-09-23): show the text comments, not only numbers.
    # Newest report first — it carries the current rating.
    reports = [r for r in version.get("reports", []) if str(r.get("comment", "")).strip()]
    reports.sort(key=lambda r: str(r.get("created_at", "")), reverse=True)
    comments_html = ""
    if reports:
        items = []
        for report in reports:
            date = escape(str(report.get("created_at", "")).split("T")[0])
            issue = str(report.get("issue_url", ""))
            link = (f' <a class="rated-comment-link" href="{escape(issue)}" '
                    'target="_blank" rel="noopener">issue</a>') if issue else ""
            items.append(
                '<blockquote class="rated-comment">'
                f'<span class="rated-comment-meta">Komentarz właściciela · {date}{link}</span>'
                f'{escape(str(report.get("comment", "")).strip())}</blockquote>'
            )
        comments_html = '<div class="rated-comments">' + "".join(items) + "</div>"
    return (
        f'<div class="rated"><p class="rated-total">Ocena tej wersji: {escape(score)}/15{when}</p>'
        f'<ul class="rated-breakdown">{breakdown}</ul>'
        f'{comments_html}'
        '<p class="rated-note">Ta wersja ma już ocenę — formularz oceny pokazuje się wyłącznie przy wersjach bez oceny.</p></div>'
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
        if private_file.exists():
            private_file.unlink()
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
                # Per-version audio: `5_v2.mp3` serves v2, v1 keeps `5.mp3`.
                source = args.audio_root / f"{story['id']}_{version.get('label')}.mp3"
                if not source.is_file():
                    source = args.audio_root / f"{story['id']}.mp3"
                if source.is_file():
                    shutil.copy2(source, audio_out / source.name)
                    version["audio"] = f"audio/{source.name}"

    (args.output / "data/catalog.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    template = Path("site/story-template.html").read_text(encoding="utf-8")
    for story in data.get("stories", []):
        all_versions = story.get("versions", [])
        # Owner's display order (2026-09-23): versions awaiting a rating come
        # first (newest on top), then rated versions from the highest score
        # down; a tie keeps the newer version higher.
        rated_versions = [v for v in all_versions if isinstance(v.get("score"), (int, float))]
        unrated_versions = [v for v in all_versions if not isinstance(v.get("score"), (int, float))]
        rated_versions.sort(key=lambda v: (float(v["score"]), version_number(v)), reverse=True)
        versions = sorted(unrated_versions, key=version_number, reverse=True) + rated_versions
        best_score = max((float(v["score"]) for v in rated_versions), default=None)
        cards = []
        for version in versions:
            audio = escape(str(version.get("audio", "")).replace("audio/", "../../audio/", 1))
            score = version.get("score")
            has_score = isinstance(score, (int, float))
            label = f"{escape(score)}/15" if has_score else "oczekuje na ocenę"
            version_label = escape(version.get("label", ""))
            # Owner request (2026-09-23): colour frames — amber for versions
            # awaiting a rating, green for the best-rated version, none for
            # the rest.
            card_class = "version"
            if not has_score:
                card_class += " unrated"
            elif best_score is not None and float(score) >= best_score:
                card_class += " best"
            if has_score:
                form = rating_summary_html(version)
            else:
                fields = []
                for name, title in CRITERIA:
                    options = "".join(f'<label class="rating-option"><input type="radio" name="{name}" value="{value}" required>{value}</label>' for value in range(1, 6))
                    fields.append(f'<fieldset><legend>{title}</legend><div class="rating-options">{options}</div></fieldset>')
                form = (f'<form class="feedback" data-story="{escape(story["id"])}" '
                        f'data-version="{version_label}">' + "".join(fields) +
                        '<textarea name="comment" maxlength="2000" placeholder="Komentarz (opcjonalnie)"></textarea>'
                        '<button>Prześlij ocenę tej wersji</button><output></output></form>')
            cards.append(
                f'<section class="{card_class}"><div class="version-head"><strong>{version_label}</strong><small>{label}</small></div>'
                f'<div class="player"><audio controls preload="metadata"><source src="{audio}" type="audio/mpeg">'
                f'Twoja przeglądarka nie obsługuje audio.</audio></div>{project_description_html(version)}{form}</section>'
            )
        latest = escape(versions[-1].get("label", "v1")) if versions else "v1"
        page = (template.replace("__ID__", escape(story["id"]))
                .replace("__TITLE__", escape(story["title"]))
                .replace("__STORY__", escape(story["story"]))
                .replace("__VERSIONS__", "".join(cards))
                .replace("__LATEST__", latest))
        destination = args.output / "stories" / str(story["id"]) / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
