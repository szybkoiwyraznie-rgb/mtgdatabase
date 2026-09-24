#!/usr/bin/env python3
"""Narzędzie czterech baz klocków (docs/signature-system.md).

Podkomendy:
  check                walidacja rejestrów + unikalność kombinacji receptur
  accept --gate gNNN   przeniesienie zaakceptowanych kandydatów z bramki do baz
  report               statystyka użycia klocków w recepturach
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIB = REPO / "data" / "library"
RECIPES = REPO / "data" / "recipes"
# data/usage-policy.json (schema 2, ADR 0006): jedyna twarda reguła to
# unikalna kombinacja a·b·c·d — egzekwowana bezpośrednio w check().
KIND_DIR = {"heroes": "heroes", "backgrounds": "backgrounds", "instruments": "instruments"}
SLOT_NAMES = ("background", "hero", "gesture", "instrument")

REQUIRED = {
    "heroes": ["id", "role", "desc", "file", "duration_sec", "character", "distance", "energy", "source", "approved"],
    "backgrounds": ["id", "setting", "desc", "file", "duration_sec", "level_ref_db", "source", "approved"],
    "gestures": ["id", "semantic", "desc", "notes", "instrument_tags", "approved"],
    "instruments": ["id", "semantic", "family", "samples", "source", "approved"],
}
SOURCE_KEYS = ["title", "author", "license", "url", "channel"]


def load(kind: str) -> dict:
    return json.loads((LIB / f"{kind}.json").read_text(encoding="utf-8"))


def save(kind: str, data: dict) -> None:
    (LIB / f"{kind}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def combo_key(recipe: dict) -> tuple:
    coda = recipe.get("coda") or {}
    return (recipe["background"]["id"], recipe["hero"]["id"], coda.get("gesture"), coda.get("instrument"))


def usage_counts(recipes: list[dict]) -> dict[str, Counter]:
    """Policz użycia klocków per slot — wyłącznie informacyjnie (ADR 0006).

    Klocki są reużywalne bez limitów; jedyna twarda reguła to unikalna
    kombinacja a·b·c·d (sprawdzana w check()). Statystyki służą miękkiemu
    rankingowi resolvera i audytowi ostrzeżeń, nie zakazom.
    """
    counts = {slot: Counter() for slot in SLOT_NAMES}
    for recipe in recipes:
        for slot, value in zip(SLOT_NAMES, combo_key(recipe)):
            if value:
                counts[slot][value] += 1
    return counts


def check() -> int:
    errors: list[str] = []
    for kind, required in REQUIRED.items():
        data = load(kind)
        ids: set[str] = set()
        for entry in data["entries"]:
            missing = [k for k in required if k not in entry]
            if missing:
                errors.append(f"{kind}/{entry.get('id', '?')}: brak pól {missing}")
                continue
            if entry["id"] in ids:
                errors.append(f"{kind}: zduplikowane id {entry['id']}")
            ids.add(entry["id"])
            source = entry.get("source", {})
            missing_src = [k for k in SOURCE_KEYS if k not in source]
            if missing_src and kind != "gestures":
                errors.append(f"{kind}/{entry['id']}: source bez pól {missing_src}")
            if kind in KIND_DIR and entry.get("file") and not (REPO / entry["file"]).exists():
                errors.append(f"{kind}/{entry['id']}: brak pliku {entry['file']}")
            if kind == "instruments":
                samples = entry["samples"]
                files = samples.values() if "articulations" not in samples else [f for fs in samples["articulations"].values() for f in fs]
                for f in files:
                    paths = f if isinstance(f, list) else [f]
                    for p in paths:
                        if not (REPO / p).exists():
                            errors.append(f"instruments/{entry['id']}: brak pliku próbki {p}")
            if kind == "gestures" and not entry["notes"]:
                errors.append(f"gestures/{entry['id']}: pusty gest")
    combos: dict[tuple, str] = {}
    recipes: list[dict] = []
    for recipe_path in sorted(RECIPES.glob("*.json")):
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
        recipes.append(recipe)
        key = combo_key(recipe)
        if key in combos:
            errors.append(f"zduplikowana kombinacja a·b·c·d: {combos[key]} i {recipe_path.name}")
        else:
            combos[key] = recipe_path.name
    for error in errors:
        print(f"BŁĄD: {error}")
    print(f"OK: {sum(len(load(k)['entries']) for k in REQUIRED)} wpisów, {len(combos)} receptur" if not errors else f"{len(errors)} problemów")
    return 1 if errors else 0


def report() -> None:
    recipes = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(RECIPES.glob("*.json"))]
    counts = usage_counts(recipes)
    total = len(recipes)
    usage = Counter(value for slot in counts.values() for value, n in slot.items() for _ in range(n))
    print("polityka (ADR 0006): reuse bez limitów; twarda tylko unikalność kombinacji a·b·c·d; "
          "statystyki poniżej są informacyjne (miękki ranking resolvera)")
    for kind in REQUIRED:
        entries = load(kind)["entries"]
        unused = [e["id"] for e in entries if e["id"] not in usage]
        print(f"{kind}: {len(entries)} wpisów, {len(unused)} nieużytych{': ' + ', '.join(unused) if unused else ''}")
    print("użycie w recepturach:")
    for slot in SLOT_NAMES:
        values = ", ".join(f"{item}={n} ({n/max(total, 1):.1%})" for item, n in counts[slot].most_common())
        print(f"  {slot}: {values or 'brak'}")


def _ingest_candidate(gate_dir: Path, kind: str, cand: dict, stamp: dict) -> str:
    """Wprowadź kandydata z bramki do właściwej bazy (pieczątka + pliki)."""
    reg = load(kind)
    entry = dict(cand["entry"])
    entry["approved"] = stamp
    if any(e["id"] == entry["id"] for e in reg["entries"]):
        reg["entries"] = [entry if e["id"] == entry["id"] else e for e in reg["entries"]]
        print(f"  {entry['id']}: już w bazie — aktualizuję approved")
    else:
        reg["entries"].append(entry)
    if kind in KIND_DIR and entry.get("file"):
        dst = REPO / entry["file"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(gate_dir / cand["file"], dst)
    if kind == "instruments":
        for midi, src_rel in entry.pop("gate_sources", {}).items():
            dst = REPO / entry["samples"][midi]
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                shutil.copy2(gate_dir / src_rel, dst)
    save(kind, reg)
    return f"{kind}/{entry['id']}"


def accept(gate_id: str, rest: bool = False) -> int:
    gate_dir = REPO / "data" / "gates" / gate_id
    manifest = json.loads((gate_dir / "manifest.json").read_text(encoding="utf-8"))
    verdicts = json.loads((gate_dir / "verdicts.json").read_text(encoding="utf-8"))
    today = date.today().isoformat()
    slot_kind = {"c": "heroes", "d": "backgrounds", "a": "gestures", "b": "instruments"}
    added: list[str] = []
    stamped: set[str] = set()  # id wpisów przyjętych z werdyktów fabuł
    for story in manifest.get("stories", []):
        sid = str(story["story_id"])
        if sid not in verdicts:
            print(f"! fabuła {sid}: brak werdyktu — pomijam")
            continue
        for slot, label in verdicts[sid].items():
            if label in ("żaden", "żadna", "none", None):
                print(f"  fabuła {sid} [{slot}]: odrzucone — kandydaci zostają w archiwum bramki")
                continue
            cands = {c["label"]: c for c in story["slots"][slot]["candidates"]}
            if label not in cands:
                print(f"BŁĄD fabuła {sid} [{slot}]: nieznana etykieta {label!r}")
                return 1
            cand = cands[label]
            kind = slot_kind[slot]
            stamp = {"gate": gate_id, "choice": f"{slot}.{label.split('.')[-1]}", "date": today}
            added.append(_ingest_candidate(gate_dir, kind, cand, stamp))
            stamped.add(cand["entry"]["id"])
    if rest:
        # wycofane (2026-09-23, ADR 0004 w wersji uzupełnionej): nie wielo-
        # wariantowo — do bazy trafia dokładnie JEDEN kandydat na wpis.
        print("BŁĄD: --rest wycofany (złamany model; właściciel wybiera jednego kandydata na wpis)")
        return 1
    # tryb wpisowy (bramki od g002): dla każdego wpisu bazy 3 kandydaci,
    # właściciel wybiera dokładnie jednego albo „żaden".
    for entry_spec in manifest.get("entries", []):
        slug = entry_spec["slug"]
        label = verdicts.get(slug)
        if label is None:
            print(f"! wpis {slug!r}: brak werdyktu — pomijam")
            continue
        if label in ("żaden", "żadna", "none"):
            print(f"  wpis {slug!r}: odrzucony — kandydaci w archiwum bramki")
            continue
        cands = {c["label"]: c for c in entry_spec["candidates"]}
        if label not in cands:
            print(f"BŁĄD wpis {slug!r}: nieznana etykieta {label!r}")
            return 1
        stamp = {"gate": gate_id, "choice": f"{slug}.{label.split('.')[-1]}", "date": today}
        added.append(_ingest_candidate(gate_dir, entry_spec["kind"], cands[label], stamp))
    manifest["verdicts"] = verdicts
    (gate_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"przyjęto: {', '.join(added) if added else 'nic'}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("report")
    p_accept = sub.add_parser("accept")
    p_accept.add_argument("--gate", required=True)
    p_accept.add_argument("--rest", action="store_true",
                          help="WYCOFANY: złamany model (doktryna-jakości cofnięta 2026-09-23)")
    args = parser.parse_args()
    sys.exit({"check": check, "report": report, "accept": lambda: accept(args.gate, rest=args.rest)}[args.cmd]())


if __name__ == "__main__":
    main()
