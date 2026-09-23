#!/usr/bin/env python3
"""Serwer podglądu biblioteki z wyłączonym cache.

`python -m http.server` odpowiada nagłówkiem Last-Modified bez Cache-Control,
więc przeglądarka trzymała stare mp3 pod tą samą nazwą (właściciel słyszał
starą wersję fabuły 5). Ten serwer zawsze wysyła no-store; dodatkowo
build_site.py dokleja ?v=<odcisk> do adresów audio.

Usage:
  python scripts/serve_site.py [--port 3000] [--dir site/generated]
"""
from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=3000)
    ap.add_argument("--dir", type=Path, default=REPO / "site" / "generated")
    args = ap.parse_args()
    root = args.dir.resolve()

    class Handler(SimpleHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(root), **kw)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            super().end_headers()

        def log_message(self, fmt, *a):
            pass

    print(f"biblioteka na porcie {args.port} (no-store) — {root}")
    ThreadingHTTPServer(("0.0.0.0", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
