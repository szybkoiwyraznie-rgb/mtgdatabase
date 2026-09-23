#!/usr/bin/env python3
"""Gablotka gotowych sygnatur (GitHub Pages).

Statyczna strona z katalogu fabuł: pełna lista, przy fabułach z sygnaturą
odtwarzacz audio/signatures/<id>.mp3 i podpis złożenia (klocki a·b·c·d).
Nie jest bramką ocen — bramki odbywają się na podglądzie sandboxa
(docs/gate-protocol.md).

Usage: python scripts/build_site.py --out site/generated
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

PAGE = """<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gablotka sygnatur — fabularne okna dźwiękowe</title>
<style>
  :root { color-scheme: dark; }
  body { font-family: ui-sans-serif, system-ui, sans-serif; background:#111418; color:#e6e9ee; max-width:860px; margin:0 auto; padding:24px 16px 80px; line-height:1.5; }
  h1 { font-size:1.4rem; }
  .sub { color:#9fb3c8; font-size:.9rem; margin-bottom:2em; }
  .card { background:#181c22; border:1px solid #262c36; border-radius:12px; padding:14px 18px; margin:.8em 0; }
  .card h2 { font-size:1.02rem; margin:0 0 .3em; }
  .sid { color:#f2c66d; font-weight:700; margin-right:.5em; }
  .story { font-size:.86rem; color:#aeb9c4; margin:.5em 0; }
  .blocks { font-size:.78rem; color:#8bd3a8; }
  audio { width:100%; height:36px; margin-top:.6em; }
  .empty { color:#6c7a89; font-size:.85rem; }
</style></head><body>
<h1>Gablotka sygnatur</h1>
<p class="sub">Gotowe okna dźwiękowe: tło + hero + koda muzyczna. __DONE__ / __TOTAL__ fabuł. Bramki odsłuchowe klocków odbywają się poza tą stroną.</p>
__BODY__
</body></html>
"""


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=REPO / "site" / "generated")
    args = parser.parse_args()
    catalog = load(REPO / "data" / "catalog.json")["stories"]
    recipes = {p.stem: load(p) for p in (REPO / "data" / "recipes").glob("*.json")}
    sig_dir = REPO / "audio" / "signatures"
    have_sig = {p.stem: p for p in sig_dir.glob("*.mp3")} if sig_dir.is_dir() else {}

    out = args.out
    if out.exists():
        shutil.rmtree(out)
    (out / "audio").mkdir(parents=True)

    parts: list[str] = []
    done = 0
    for story in sorted(catalog, key=lambda s: int(s["id"])):
        sid = story["id"]
        if sid in have_sig and sid in recipes:
            done += 1
            shutil.copy2(have_sig[sid], out / "audio" / f"{sid}.mp3")
            r = recipes[sid]
            coda = r.get("coda") or {}
            blocks = (f"tło: {r['background']['id']} · hero: {r['hero']['id']}"
                      + (f" · koda: {coda.get('gesture')} na {coda.get('instrument')}" if coda else ""))
            parts.append(
                f'<div class="card"><h2><span class="sid">{sid}</span>{html.escape(story["title"])}</h2>'
                f'<p class="story">{html.escape(story["story"])}</p>'
                f'<p class="blocks">{html.escape(blocks)}</p>'
                f'<audio controls preload="none" src="audio/{sid}.mp3"></audio></div>'
            )
        else:
            parts.append(
                f'<div class="card"><h2><span class="sid">{sid}</span>{html.escape(story["title"])}</h2>'
                f'<p class="empty">sygnatura w kolejce</p></div>'
            )
    page = (PAGE.replace("__DONE__", str(done)).replace("__TOTAL__", str(len(catalog)))
                .replace("__BODY__", "\n".join(parts)))
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"{out}: {done}/{len(catalog)} fabuł z sygnaturą")


if __name__ == "__main__":
    main()
