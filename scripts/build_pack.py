#!/usr/bin/env python3
"""Flat ZIP of v2 generated samples: only <id>.mp3 from audio/samples.

Old v1 signatures are archived under archive/v1-curated-sound-design and are
never included by default.
"""
from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

NAME_RULE = re.compile(r"^\d+\.mp3$")


def zip_pack(src: Path, out: Path) -> list[str]:
    src.mkdir(parents=True, exist_ok=True)
    bad = [p.name for p in src.iterdir() if p.is_file() and not p.name.startswith(".") and not NAME_RULE.match(p.name)]
    if bad:
        raise SystemExit(f"niedozwolone nazwy w {src} (reguła <id>.mp3): {bad}")
    files = sorted((p for p in src.glob("*.mp3")), key=lambda p: int(p.stem))
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as pack:
        for path in files:
            pack.write(path, arcname=path.name)
    return [p.name for p in files]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, default=Path("audio/samples"))
    parser.add_argument("--output", type=Path, default=Path("build/samples-latest.zip"))
    args = parser.parse_args()
    names = zip_pack(args.src, args.output)
    print(f"{args.output}: {len(names)} sample(s)" + (f" ({names[0]}…{names[-1]})" if names else ""))


if __name__ == "__main__":
    main()
