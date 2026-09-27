#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the v2 sample library HTML.

The page lists story IDs, hand-written sample scenarios, generated MP3 players,
and the original story text for context. It copies audio/samples/*.mp3 into the
site output, so it works both in sandbox preview and GitHub Pages.
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSS = """
:root { color-scheme: dark; }
body { margin:0 auto; max-width:1100px; padding:24px 16px 96px; background:#101216; color:#e9edf2; font-family:ui-sans-serif,system-ui,sans-serif; line-height:1.45; }
a { color:#8cc7ff; }
h1 { font-size:1.6rem; margin:.2rem 0; }
.sub { color:#aab4c0; margin-top:.2rem; }
.tools { display:flex; gap:12px; flex-wrap:wrap; margin:18px 0; }
input { flex:1; min-width:260px; background:#171b22; color:#e9edf2; border:1px solid #303846; border-radius:8px; padding:10px 12px; }
.card { border:1px solid #2b323d; background:#171b22; border-radius:12px; padding:14px 16px; margin:12px 0; }
.card.ready { border-color:#345a3d; }
.card.missing { opacity:.72; }
.top { display:flex; gap:12px; align-items:baseline; flex-wrap:wrap; }
.id { color:#f5c86a; font-weight:800; }
.title { font-weight:700; font-size:1.05rem; }
.status { color:#9fb0c5; font-size:.84rem; }
.scenario { color:#cfe7cf; margin:.65rem 0 .25rem; }
.prompt { color:#aeb9c4; font-size:.86rem; margin:.25rem 0; }
.story { color:#9da8b5; font-size:.84rem; margin-top:.55rem; }
audio { width:min(100%, 460px); height:36px; margin-top:8px; }
.badge { font-size:.75rem; padding:2px 7px; border-radius:999px; background:#263143; color:#c7d3e1; }
"""

JS = """
const q = document.querySelector('#q');
q?.addEventListener('input', () => {
  const needle = q.value.toLowerCase();
  document.querySelectorAll('.card').forEach(card => {
    card.style.display = card.textContent.toLowerCase().includes(needle) ? '' : 'none';
  });
});
"""


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def copy_samples(src: Path, out: Path) -> set[str]:
    dst = out / "samples"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    have: set[str] = set()
    if src.exists():
        for mp3 in sorted(src.glob("*.mp3"), key=lambda p: int(p.stem) if p.stem.isdigit() else 10**9):
            shutil.copy2(mp3, dst / mp3.name)
            have.add(mp3.stem)
    return have


def page(catalog: dict, scenarios: dict[str, dict], generated: dict[str, dict], have_audio: set[str]) -> str:
    stories = sorted(catalog.get("stories", []), key=lambda s: int(s["id"]))
    ready = sum(1 for sid in scenarios if sid in have_audio)
    planned = len(scenarios)
    cards: list[str] = []
    for story in stories:
        sid = str(story["id"])
        sc = scenarios.get(sid)
        has = sid in have_audio
        if not sc and not has:
            continue
        cls = "ready" if has else "missing"
        audio = f'<audio controls preload="none" src="samples/{sid}.mp3"></audio>' if has else '<div class="status">brak wygenerowanego MP3</div>'
        scenario = html.escape(sc.get("sample_scenario", "—") if sc else "—")
        prompt = html.escape(sc.get("prompt", "") if sc else "")
        batch = html.escape(str(sc.get("batch", "") if sc else ""))
        gen = generated.get(sid, {})
        status = "wygenerowany" if has else html.escape(str(sc.get("status", "missing") if sc else "missing"))
        if gen.get("generated_at_unix"):
            status += f" · unix {gen['generated_at_unix']}"
        cards.append(f"""
<section class="card {cls}">
  <div class="top"><span class="id">#{sid}</span><span class="title">{html.escape(story['title'])}</span><span class="badge">{status}</span>{f'<span class="badge">{batch}</span>' if batch else ''}</div>
  <div class="scenario">{scenario}</div>
  {audio}
  {f'<div class="prompt">Prompt: {prompt}</div>' if prompt else ''}
  <details><summary>narracja</summary><div class="story">{html.escape(story.get('story',''))}</div></details>
</section>
""")
    return f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Biblioteka sampli — MTG Database</title><style>{CSS}</style></head>
<body>
<h1>Biblioteka sampli v2</h1>
<p class="sub">Jedna fabuła → jeden krótki jednorodny sample. Wygenerowane: <b>{ready}</b>; scenariusze: <b>{planned}</b>; katalog: <b>{len(stories)}</b>.</p>
<div class="tools"><input id="q" placeholder="Szukaj po ID, tytule, scenariuszu…"></div>
{''.join(cards) if cards else '<p class="sub">Brak scenariuszy lub wygenerowanych sampli. Dodaj wpisy do data/samples/scenarios.jsonl i uruchom scouta.</p>'}
<script>{JS}</script>
</body></html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "site/generated")
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/catalog.json")
    parser.add_argument("--scenarios", type=Path, default=ROOT / "data/samples/scenarios.jsonl")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/samples/generated-manifest.jsonl")
    parser.add_argument("--samples", type=Path, default=ROOT / "audio/samples")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    have_audio = copy_samples(args.samples, args.out)
    scenarios = {str(r["story_id"]): r for r in read_jsonl(args.scenarios)}
    generated = {str(r["story_id"]): r for r in read_jsonl(args.manifest)}
    html_text = page(read_json(args.catalog), scenarios, generated, have_audio)
    (args.out / "index.html").write_text(html_text, encoding="utf-8")
    print(f"{args.out}: {len(have_audio)} sample(s), {len(scenarios)} scenario(s)")


if __name__ == "__main__":
    main()
