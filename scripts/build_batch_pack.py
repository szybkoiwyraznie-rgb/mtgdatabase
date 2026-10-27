#!/usr/bin/env python3
"""ZIP jednej paczki (batch) do dostawy właścicielowi.

Buduje płaski ZIP z ``audio/samples/<id>.mp3`` dla wybranej paczki
(``--batch b080``) albo listy ID (``--ids 426,427,...``) i dokłada do niego
``README.txt`` z mapowaniem ID → karta → archetyp → scenariusz → długość.

Różnica względem ``build_pack.py``: tamten pakuje **cały** korpus do
``samples-latest.zip``, ten pakuje **jedną dostawę**, żeby dało się ją wysłać
(np. na Google Drive) bez 600+ plików w archiwum.

Przykłady::

    python scripts/build_batch_pack.py --batch b080
    python scripts/build_batch_pack.py --ids 426,427,429 --output build/test.zip
"""
from __future__ import annotations

import argparse
import json
import zipfile
from datetime import date
from pathlib import Path

DEFAULT_SCENARIOS = Path("data/samples/scenarios.jsonl")
DEFAULT_CATALOG = Path("data/catalog.json")
DEFAULT_SRC = Path("audio/samples")


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"brak pliku scenariuszy: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_titles(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    stories = data["stories"] if isinstance(data, dict) else data
    return {str(s["id"]): s.get("title", "") for s in stories}


def select_ids(*, batch: str | None, ids: str | None, scenarios: list[dict]) -> list[str]:
    by_id = {str(r["story_id"]): r for r in scenarios}
    if ids:
        chosen = [part.strip() for part in ids.split(",") if part.strip()]
        missing = [i for i in chosen if i not in by_id]
        if missing:
            raise SystemExit(f"ID bez scenariusza: {', '.join(missing)}")
    elif batch:
        chosen = [str(r["story_id"]) for r in scenarios if r.get("batch") == batch]
        if not chosen:
            raise SystemExit(f"brak scenariuszy z batch={batch!r}")
    else:
        raise SystemExit("podaj --batch albo --ids")
    return sorted(set(chosen), key=int)


def readme_text(ids: list[str], *, batch: str | None, rows: dict[str, dict], titles: dict[str, str]) -> str:
    label = batch or "wybór ręczny"
    lines = [
        f"Paczka {label} — {len(ids)} sampli (dostawa {date.today().isoformat()})",
        "=" * 72,
        "",
        "Płaski ZIP: każdy plik to <id_fabuly>.mp3, LUFS -20, limiter -1 dBTP.",
        "ID = numeryczna część kolumny 'Ilustracja' w fabuły270926.csv.",
        "",
        f"{'ID':>4}  {'Karta':<26} {'Archetyp':<18} {'Dług.':>6}  Scenariusz",
        "-" * 110,
    ]
    for i in ids:
        r = rows.get(i, {})
        dur = r.get("duration_seconds")
        dur_s = f"{dur:g} s" if isinstance(dur, (int, float)) else "?"
        lines.append(
            f"{i:>4}  {titles.get(i, '?'):<26} {str(r.get('archetype') or ''):<18} {dur_s:>6}  "
            f"{r.get('sample_scenario', '')}"
        )
    lines.append("")
    return "\n".join(lines)


def build_pack(
    *,
    ids: list[str],
    output: Path,
    scenarios: list[dict],
    titles: dict[str, str],
    src: Path = DEFAULT_SRC,
    allow_missing: bool = False,
) -> list[str]:
    rows = {str(r["story_id"]): r for r in scenarios}
    available = []
    missing = []
    for i in ids:
        if (src / f"{i}.mp3").exists():
            available.append(i)
        else:
            missing.append(i)
    if missing and not allow_missing:
        raise SystemExit(f"brak MP3 dla: {', '.join(missing)} (użyj --allow-missing, żeby pominąć)")
    if not available:
        raise SystemExit("brak plików do spakowania")

    output.parent.mkdir(parents=True, exist_ok=True)
    batch = next((rows[i].get("batch") for i in available if rows.get(i, {}).get("batch")), None)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as pack:
        for i in available:
            pack.write(src / f"{i}.mp3", arcname=f"{i}.mp3")
        pack.writestr("README.txt", readme_text(available, batch=batch, rows=rows, titles=titles))
    return available


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch", help="np. b080 — bierze wszystkie scenariusze z tym batch")
    parser.add_argument("--ids", help="lista ID po przecinku, np. 426,427,429")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC)
    parser.add_argument("--output", type=Path, help="domyślnie build/samples-<batch|ids>-<data>.zip")
    parser.add_argument("--allow-missing", action="store_true", help="pomiń ID bez MP3 zamiast kończyć błędem")
    args = parser.parse_args()

    scenarios = load_rows(args.scenarios)
    ids = select_ids(batch=args.batch, ids=args.ids, scenarios=scenarios)
    output = args.output or Path(f"build/samples-{args.batch or 'wybor'}-{date.today().isoformat()}.zip")
    packed = build_pack(
        ids=ids,
        output=output,
        scenarios=scenarios,
        titles=load_titles(args.catalog),
        src=args.src,
        allow_missing=args.allow_missing,
    )
    print(f"{output}: {len(packed)} sample(s) ({packed[0]}…{packed[-1]})")


if __name__ == "__main__":
    main()
