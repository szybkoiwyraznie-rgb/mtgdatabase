#!/usr/bin/env python3
"""Narzędzie czterech baz klocków (docs/signature-system.md).

Podkomendy:
  check                walidacja rejestrów + unikalność kombinacji receptur
  accept --gate gNNN   przeniesienie zaakceptowanych kandydatów z bramki do baz
  report               statystyka użycia klocków w recepturach
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIB = REPO / "data" / "library"
RECIPES = REPO / "data" / "recipes"
KIND_DIR = {"heroes": "heroes", "backgrounds": "backgrounds", "instruments": "instruments"}

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
            if kind in KIND_DIR and not (REPO / entry["file"]).exists():
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
    for recipe_path in sorted(RECIPES.glob("*.json")):
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
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
    usage: dict[str, int] = {}
    for recipe_path in sorted(RECIPES.glob("*.json")):
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
        for item in combo_key(recipe):
            if item:
                usage[item] = usage.get(item, 0) + 1
    for kind in REQUIRED:
        entries = load(kind)["entries"]
        unused = [e["id"] for e in entries if e["id"] not in usage]
        print(f"{kind}: {len(entries)} wpisów, {len(unused)} nieużytych{': ' + ', '.join(unused) if unused else ''}")


def accept(gate_id: str) -> int:
    gate_dir = REPO / "work" / "gates" / gate_id
    manifest = json.loads((gate_dir / "manifest.json").read_text(encoding="utf-8"))
    verdicts = json.loads((gate_dir / "verdicts.json").read_text(encoding="utf-8"))
    today = date.today().isoformat()
    slot_kind = {"c": "heroes", "d": "backgrounds", "a": "gestures", "b": "instruments"}
    added: list[str] = []
    for story in manifest["stories"]:
        sid = str(story["story_id"])
        if sid not in verdicts:
            print(f"! fabuła {sid}: brak werdyktu — pomijam")
            continue
        for slot, label in verdicts[sid].items():
            if label in ("żaden", "żadna", "none", None):
                print(f"  fabuła {sid} [{slot}]: odrzucone — poza bazą")
                continue
            cands = {c["label"]: c for c in story["slots"][slot]["candidates"]}
            if label not in cands:
                print(f"BŁĄD fabuła {sid} [{slot}]: nieznana etykieta {label!r}")
                return 1
            cand = cands[label]
            kind = slot_kind[slot]
            reg = load(kind)
            entry = dict(cand["entry"])
            entry.setdefault("approved", {})
            entry["approved"] = {"gate": gate_id, "choice": f"{slot}.{label.split('.')[-1]}", "date": today}
            if any(e["id"] == entry["id"] for e in reg["entries"]):
                print(f"  {entry['id']}: już w bazie — aktualizuję approved")
                reg["entries"] = [entry if e["id"] == entry["id"] else e for e in reg["entries"]]
            else:
                reg["entries"].append(entry)
            if kind in KIND_DIR:
                dst = REPO / entry["file"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists():
                    shutil.copy2(gate_dir / cand["file"], dst)
            save(kind, reg)
            added.append(f"{kind}/{entry['id']}")
    manifest["verdicts"] = verdicts
    (gate_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gates_log = REPO / "data" / "gates"
    gates_log.mkdir(parents=True, exist_ok=True)
    shutil.copy2(gate_dir / "manifest.json", gates_log / f"{gate_id}.json")
    print(f"przyjęto: {', '.join(added) if added else 'nic'}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("report")
    p_accept = sub.add_parser("accept")
    p_accept.add_argument("--gate", required=True)
    args = parser.parse_args()
    sys.exit({"check": check, "report": report, "accept": lambda: accept(args.gate)}[args.cmd]())


if __name__ == "__main__":
    main()
