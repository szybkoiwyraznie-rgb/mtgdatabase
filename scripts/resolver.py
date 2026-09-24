#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etap 4 (ADR 0006 + aneks „Jeden typ = jeden klocek"): resolver obsady.

Model 1:1 — typ taksonomii ma najwyżej jeden klocek w bazie. Obsada fabuły
to deterministyczne złożenie: typy z profilu → ich jedyne klocki.

Twarde filtry:
  1. typ bez klocka                → BRAK (bramka audio na jedyny klocek typu),
  2. weto bad_for na cesze wymaganej → BRAK (typ nie obsługuje profilu:
     inny istniejący typ albo propozycja nowego — bramka tekstowa),
  3. cecha wymagana bez pokrycia w traits/opisie klocka → BRAK (jak wyżej),
  4. kombinacja czterech klocków identyczna z istniejącą recepturą
     → KOLIZJA (propozycja doprecyzowania taksonomii — bramka tekstowa).

Ranking kandydatów istnieje tylko przy bramce (wybór jedynego klocka
nowego typu); resolver per fabuła niczego nie rankuje.

Użycie:
  scripts/resolver.py STORY_ID [--json]
  scripts/resolver.py --survey
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LAYERS = ("background", "hero", "mood", "instrumentation")
LAYER_KIND = {
    "background": "backgrounds",
    "hero": "heroes",
    "mood": "gestures",
    "instrumentation": "instruments",
}
# kolejność jak w combo_key() library_tool (background, hero, gesture, instrument)
COMBO_ORDER = ("background", "hero", "mood", "instrumentation")


def load_data() -> dict:
    def rd(p):
        return json.loads((REPO / p).read_text(encoding="utf-8"))

    data = {
        "taxonomy": rd("data/semantics/taxonomy.json"),
        "profiles": rd("data/semantics/story-profiles.json")["profiles"],
        "classes": rd("data/semantics/story-classes.json")["classes"],
        "library": {kind: rd(f"data/library/{kind}.json")["entries"]
                    for kind in LAYER_KIND.values()},
        "recipes": [json.loads(p.read_text(encoding="utf-8"))
                    for p in sorted((REPO / "data/recipes").glob("*.json"))],
    }
    # indeks typ -> klocek per warstwa (niezmiennik 1:1 pilnuje library_tool)
    data["by_type"] = {}
    for layer, kind in LAYER_KIND.items():
        idx = {}
        for e in data["library"][kind]:
            sem = e.get("semantics") or {}
            if "type" in sem:
                idx[sem["type"]] = e
        data["by_type"][layer] = idx
    return data


def tokens(text: str) -> set[str]:
    # min. 3 znaki: polskie rdzenie dźwięków bywają krótkie (pęd, ryk, syk, huk)
    return {w[:6] for w in re.findall(r"[a-ząćęłńóśźż]+", text.lower()) if len(w) >= 3}


def overlap(a: str, b: str) -> bool:
    return bool(tokens(a) & tokens(b))


def block_evidence(entry: dict) -> str:
    sem = entry.get("semantics", {})
    parts = [" ".join(sem.get("traits", [])), sem.get("type", "")]
    for key in ("desc", "role", "setting", "semantic", "character", "good_for"):
        val = entry.get(key, "")
        parts.append(" ".join(val) if isinstance(val, list) else str(val))
    return " ".join(parts)


def check_required(profile_layer: dict, entry: dict) -> list[dict]:
    """Twarde filtry 2 i 3 dla jednej warstwy. Zwraca listę problemów."""
    problems = []
    bad = " | ".join(entry.get("semantics", {}).get("bad_for", []))
    evidence = block_evidence(entry)
    for req in profile_layer.get("wymagane", []):
        if overlap(req, bad):
            problems.append({"filtr": "weto bad_for", "cecha": req,
                             "bad_for": entry["semantics"]["bad_for"]})
        elif not overlap(req, evidence):
            problems.append({"filtr": "cecha wymagana bez pokrycia",
                             "cecha": req})
    return problems


def recipe_combo(recipe: dict) -> tuple:
    coda = recipe.get("coda") or {}
    return (recipe["background"]["id"], recipe["hero"]["id"],
            coda.get("gesture"), coda.get("instrument"))


def resolve_story(sid: str, data: dict) -> dict:
    types = data["classes"][sid]
    profile = data["profiles"][sid]
    result = {"story_id": sid, "title": profile.get("title"),
              "types": types, "blocks": {}, "braki": [], "status": None}
    for layer in LAYERS:
        t = types[layer]
        entry = data["by_type"][layer].get(t)
        if entry is None:
            result["braki"].append({
                "layer": layer, "typ": t, "filtr": "typ bez klocka",
                "akcja": "bramka audio: kandydaci na jedyny klocek typu"})
            continue
        problems = check_required(profile[layer], entry)
        if problems:
            for pr in problems:
                pr.update({"layer": layer, "typ": t, "klocek": entry["id"],
                           "akcja": "typ nie obsługuje profilu: inny istniejący "
                                    "typ albo propozycja nowego (bramka tekstowa)"})
            result["braki"].extend(problems)
        else:
            result["blocks"][layer] = entry["id"]
    if not result["braki"]:
        combo = tuple(result["blocks"][l] for l in COMBO_ORDER)
        for r in data["recipes"]:
            if recipe_combo(r) == combo and str(r.get("story_id")) != sid:
                result["braki"].append({
                    "filtr": "kolizja kombinacji",
                    "z_recepturą": str(r.get("story_id")), "combo": combo,
                    "akcja": "propozycja doprecyzowania taksonomii "
                             "(bramka tekstowa)"})
    result["status"] = "OBSADZONA" if not result["braki"] else "BRAK"
    if result["status"] == "OBSADZONA":
        result["resolution"] = {
            "types": types,
            "blocks": result["blocks"],
            "reason": "model 1:1 — typy profilu wskazały jedyne klocki; "
                      "filtry twarde czyste; kombinacja unikalna",
        }
    return result


def survey(data: dict) -> None:
    full, partial = [], []
    brak_typow: dict[str, int] = {}
    for sid in sorted(data["classes"], key=int):
        res = resolve_story(sid, data)
        got = len(res["blocks"])
        if res["status"] == "OBSADZONA":
            full.append(sid)
        elif got:
            partial.append((sid, got))
        for b in res["braki"]:
            if b["filtr"] == "typ bez klocka":
                brak_typow[f"{b['layer']}:{b['typ']}"] = \
                    brak_typow.get(f"{b['layer']}:{b['typ']}", 0) + 1
    print(f"fabuł w pełni obsadzalnych dziś: {len(full)} {full}")
    print(f"fabuł z częściową obsadą (≥1 klocek): {len(partial)}")
    top = sorted(brak_typow.items(), key=lambda kv: -kv[1])[:15]
    print("najczęściej wołane typy bez klocka (top 15):")
    for k, n in top:
        print(f"  {n:4d}  {k}")


def main(argv: list[str]) -> int:
    data = load_data()
    if "--survey" in argv:
        survey(data)
        return 0
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    sid = args[0]
    if sid not in data["classes"]:
        print(f"nieznana fabuła: {sid}")
        return 2
    res = resolve_story(sid, data)
    if "--json" in argv:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"fabuła {sid} ({res['title']}): {res['status']}")
        for layer in LAYERS:
            t = res["types"][layer]
            b = res["blocks"].get(layer, "—")
            print(f"  {layer:16s} {t:28s} -> {b}")
        for brak in res["braki"]:
            print(f"  BRAK: {json.dumps(brak, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
