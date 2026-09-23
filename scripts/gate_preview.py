#!/usr/bin/env python3
"""Strona bramki odsłuchowej z manifestu kandydatów (work/gates/<id>/).

Generuje statyczny index.html (grupowanie: fabuła → slot → kandydaci) i
serwuje katalog na 0.0.0.0. Odpowiedź wpisujemy w czacie, np.:
  fabuła 1: a.1 b.2 c.2 d.żaden-za-cichy

Usage:
  python scripts/gate_preview.py work/gates/g001 [--port 8080] [--build-only]
"""
from __future__ import annotations

import argparse
import html
import json
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

SLOT_TITLE = {
    "d": "tło — przestrzeń miejsca",
    "c": "hero — jedno główne zdarzenie",
    "a": "koda — muzyczna odpowiedź (render neutralny: fortepian)",
    "b": "instrument — brzmienie kody (fraza demonstracyjna)",
}
SLOT_ORDER = ["d", "c", "a", "b"]

PAGE = """<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bramka __GID__ — system sygnatur</title>
<style>
  :root { color-scheme: dark; }
  body { font-family: ui-sans-serif, system-ui, sans-serif; background:#111418; color:#e6e9ee; margin:0 auto; max-width:880px; padding:24px 16px 120px; line-height:1.5; }
  h1 { font-size:1.35rem; } h2 { font-size:1.15rem; margin-top:2.2em; border-top:1px solid #2a2f38; padding-top:1.2em;}
  h3 { font-size:0.95rem; text-transform:uppercase; letter-spacing:.08em; color:#9fb3c8; margin:1.6em 0 .4em; }
  .story { font-size:.9rem; color:#b8c2cc; }
  .role { font-size:.9rem; color:#8bd3a8; margin:0 0 .6em; }
  .cand { display:flex; align-items:center; gap:12px; background:#181c22; border:1px solid #262c36; border-radius:10px; padding:10px 14px; margin:.5em 0; }
  .cand .lab { font-weight:700; font-size:1.05rem; min-width:2.6em; color:#f2c66d; }
  .cand .meta { flex:1; min-width:0; }
  .cand .name { font-weight:600; font-size:.95rem; }
  .cand .desc { font-size:.82rem; color:#aeb9c4; }
  .cand .src { font-size:.72rem; color:#6c7a89; margin-top:2px; }
  audio { width:230px; height:36px; }
  .howto { background:#1a2230; border:1px solid #2c3a4f; border-radius:10px; padding:12px 16px; font-size:.9rem; }
  code { background:#0d1014; padding:1px 6px; border-radius:6px; color:#f2c66d; }
</style></head><body>
<h1>Bramka odsłuchowa <b>__GID__</b></h1>
<div class="howto">__HOWTO__</div>
__BODY__
</body></html>
"""


def render_candidate(cand: dict, gate_dir_uri: str) -> str:
    label = html.escape(cand["label"])
    name = html.escape(cand.get("title", cand["label"]))
    desc = html.escape(cand.get("desc", ""))
    src = html.escape(cand.get("source", ""))
    file_uri = f"{gate_dir_uri}/{cand['file']}" if gate_dir_uri else html.escape(cand["file"])
    return (
        f'<div class="cand"><div class="lab">{label}</div>'
        f'<div class="meta"><div class="name">{name}</div>'
        f'<div class="desc">{desc}</div><div class="src">{src}</div></div>'
        f'<audio controls preload="none" src="{file_uri}"></audio></div>'
    )


def build_page(gate_dir: Path) -> None:
    manifest = json.loads((gate_dir / "manifest.json").read_text(encoding="utf-8"))
    parts: list[str] = []
    entries_mode = bool(manifest.get("entries"))
    for entry_spec in manifest.get("entries", []):
        # tryb wpisowy (ADR 0004): dla KAŻDEGO wpisu bazy 3 kandydaci,
        # właściciel wybiera dokładnie jednego (albo „żaden").
        parts.append(f"<h2>Wpis do bazy: <code>{html.escape(entry_spec['slug'])}</code> "
                     f"· baza {html.escape(entry_spec['kind'])}</h2>")
        parts.append(f'<p class="role">rola: {html.escape(entry_spec.get("role", ""))}</p>')
        for cand in entry_spec["candidates"]:
            parts.append(render_candidate(cand, ""))
    for story in manifest.get("stories", []):
        parts.append(f"<h2>Fabuła {story['story_id']} — {html.escape(story['title'])}</h2>")
        parts.append(f'<p class="story">{html.escape(story["story"])}</p>')
        for slot in SLOT_ORDER:
            if slot not in story["slots"]:
                continue
            block = story["slots"][slot]
            parts.append(f"<h3>{slot} · {SLOT_TITLE.get(slot, slot)}</h3>")
            parts.append(f'<p class="role">rola: {html.escape(block.get("role", ""))}</p>')
            for cand in block["candidates"]:
                parts.append(render_candidate(cand, ""))
    if entries_mode:
        howto = ("Dla każdego wpisu wybierz <b>dokładnie jednego</b> kandydata albo wszystkich odrzuć.\n"
                 "Tylko wybrany trafia do bazy; pozostali zostają w archiwum bramki.\n"
                 "Odpowiedź napisz w czacie agenta, np.:<br><br>\n"
                 "<code>jezioro: j.2 · krzyki-nurka: n.żaden-za-ostry · grandpiano: p.1</code><br><br>\n"
                 "Po „żaden\" dopisz jedno słowo dlaczego (<code>za cichy</code>, <code>zły klimat</code>) — "
                 "poprawi drugą rundę kandydatów.")
    else:
        howto = ("Wybierz dla każdego slotu <b>jednego</b> kandydata albo wszystkich odrzuć.\n"
                 "Odpowiedź napisz w czacie agenta, np. dla dwóch fabuł:<br><br>\n"
                 "<code>fabuła 1: d.1 c.2 a.1 b.2 &nbsp;·&nbsp; fabuła 4: d.1 c.1 a.2 b.3 d.żaden</code><br><br>\n"
                 "Po „żaden\" dopisz jedno słowo dlaczego (<code>za cichy</code>, <code>zły klimat</code>) — poprawi drugą rundę kandydatów.")
    page = (PAGE.replace("__GID__", html.escape(manifest["id"]))
                .replace("__BODY__", "\n".join(parts))
                .replace("__HOWTO__", howto))
    (gate_dir / "index.html").write_text(page, encoding="utf-8")
    print(f"zbudowano {gate_dir / 'index.html'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gate_dir", type=Path)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()
    gate_dir = args.gate_dir.resolve()
    build_page(gate_dir)
    if args.build_only:
        return

    class Handler(SimpleHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(gate_dir), **kw)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            super().end_headers()

        def log_message(self, fmt, *a):
            pass

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print(f"bramka na porcie {args.port} — Ctrl+C kończy")
    server.serve_forever()


if __name__ == "__main__":
    main()
