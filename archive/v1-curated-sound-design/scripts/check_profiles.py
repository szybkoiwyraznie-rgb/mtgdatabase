#!/usr/bin/env python3
"""Walidator profili semantycznych (Etap 1 roadmapy, ADR 0006).

Sprawdza data/semantics/story-profiles.json przeciwko data/catalog.json:
- każdy profil odpowiada istniejącej fabule (żadnych sierot),
- profil ma komplet czterech warstw (background, hero, mood, instrumentation),
- każda warstwa ma niepusty `opis` i niepuste `cechy`,
- `wymagane` (jeśli są) to podzbiór `cechy`.

Kompletność katalogu (510/510) jest raportowana; twardym błędem staje się
dopiero z flagą --require-complete (DoD Etapu 1).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "data" / "catalog.json"
PROFILES = REPO / "data" / "semantics" / "story-profiles.json"
LAYERS = ("background", "hero", "mood", "instrumentation")


def main() -> int:
    require_complete = "--require-complete" in sys.argv[1:]
    catalog_ids = {s["id"] for s in json.loads(CATALOG.read_text(encoding="utf-8"))["stories"]}
    if not PROFILES.exists():
        print(f"BŁĄD: brak {PROFILES.relative_to(REPO)}")
        return 1
    data = json.loads(PROFILES.read_text(encoding="utf-8"))
    profiles: dict[str, dict] = data["profiles"]
    errors: list[str] = []
    for sid, prof in profiles.items():
        if sid not in catalog_ids:
            errors.append(f"profil {sid}: nie ma takiej fabuły w katalogu")
            continue
        for layer in LAYERS:
            block = prof.get(layer)
            if not isinstance(block, dict):
                errors.append(f"profil {sid}: brak warstwy {layer}")
                continue
            if not str(block.get("opis", "")).strip():
                errors.append(f"profil {sid}/{layer}: pusty opis")
            cechy = block.get("cechy")
            if not isinstance(cechy, list) or not cechy:
                errors.append(f"profil {sid}/{layer}: puste cechy")
                continue
            wymagane = block.get("wymagane", [])
            extra = [w for w in wymagane if w not in cechy]
            if extra:
                errors.append(f"profil {sid}/{layer}: wymagane spoza cech: {extra}")
    missing = sorted(catalog_ids - set(profiles), key=int)
    for error in errors:
        print(f"BŁĄD: {error}")
    print(f"profile: {len(profiles)}/{len(catalog_ids)} fabuł"
          + (f"; brakuje m.in.: {', '.join(missing[:10])}…" if missing else " — komplet"))
    if require_complete and missing:
        print("BŁĄD: --require-complete, a katalog nie jest pokryty")
        return 1
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
