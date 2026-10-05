#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Triage katalogu: przypisanie archetypu każdej fabule (0 kredytów).

Audyt rozpoznawalności (`audit_archetype_match.py`) działa tylko dla kart, które
mają zadeklarowane pole `archetype`. Ręcznie da się to zrobić dla kilkunastu
kart; katalog ma 553. Ten skrypt robi przypisanie regułami, **czytając prompt,
nie tytuł** — prompt opisuje dźwięk, który zamówiliśmy, więc jest znacznie
pewniejszym źródłem niż nazwa karty (zgadywanie z tytułu było jednym ze źródeł
pierwotnego problemu).

Zasady:
- reguła łapie **zdarzenie**, nie materiał: `stone`/`rock`/`metal` są w połowie
  promptów jako tworzywo, więc `stone_slide` wymaga skały *w ruchu*
  (grind/slide/tumble/roll/cascade), a nie słowa „stone”,
- reguły są uporządkowane od najbardziej swoistych; wygrywa pierwsze trafienie,
- fabuła, której żadna reguła nie łapie, dostaje `null` i trafia na listę
  `unassigned` — skrypt **nie zgaduje**. To celowe: lepiej 40 kart do ręcznego
  obejrzenia niż 40 fałszywych archetypów w audycie.

Użycie:
    python scripts/assign_archetypes.py --dry-run          # tylko raport
    python scripts/assign_archetypes.py --apply            # zapis do scenarios.jsonl
    python scripts/assign_archetypes.py --apply --overwrite
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from audit_archetype_match import CONTRACTS  # noqa: E402

# Doklejki scouta i formułki realizacyjne — nie niosą treści dźwiękowej.
BOILERPLATE = [
    re.compile(r"\bno (music|speech|narration|voice|dialogue|ambience bed|"
               r"multi-layer cinematic scene|reverberation)[.,]?\s*", re.I),
    re.compile(r"\b(clean|close|dry|isolated|detailed|studio) recording\b[^.]*\.?", re.I),
    re.compile(r"\b(at|moderate|low) (level|volume)\b[^.]*\.?", re.I),
]


def clean_text(row: dict) -> str:
    text = f"{row.get('prompt', '')} {row.get('sample_scenario', '')}"
    for rx in BOILERPLATE:
        text = rx.sub(" ", text)
    return re.sub(r"\s+", " ", text).lower()


def both(a: str, b: str, span: int = 70) -> str:
    """Dwa motywy w tej samej klauzuli, w dowolnej kolejności."""
    return rf"(?:{a})\w*[^.]{{0,{span}}}(?:{b})|(?:{b})\w*[^.]{{0,{span}}}(?:{a})"


# Kolejność = priorytet. Im wyżej, tym bardziej swoista reguła.
RULES: list[tuple[str, str, str]] = [
    ("arcane_choir", r"choir|choral|chant|wordless (mystical )?voices|voices in unison|chór|śpiew",
     "chór / zaśpiew"),
    ("folk_music", r"lute|fiddle|tambourine|flute melody|folk (music|dance|tune)|wiejsk\w+ (muzyk|taniec)|lutni|bęben\w* i",
     "muzyka ludowa"),
    ("horn_call", r"war horn|hunting horn|trumpet|bugle|brazen horn|róg bojow|trąbk",
     "róg / sygnał dęty"),
    ("temple_bell", r"\bbell\b|gong|chime|tolling|dzwon",
     "dzwon"),
    ("anvil_strike", r"anvil|smith|forge hammer|kowadł|kuźn",
     "kowadło"),
    ("sword_clash", r"sword|blade|sabre|claymore|rapier|steel (clash|on steel|meeting)|miecz|ostrz|głowni|szabl",
     "stal"),
    ("arrow_flight", r"arrow|bowstring|crossbow bolt|quarrel whistl|strzał[ay]|bełt",
     "strzała"),
    ("whip_crack", r"\bwhip\b|lash crack|bicz",
     "bicz"),
    ("thunder_clap", r"thunder|lightning|grzmot|piorun",
     "grzmot"),
    ("volcanic_eruption", r"volcan|lava|magma|eruption|wulkan|law[ay]|magm",
     "wulkan"),
    ("earth_rumble", r"earth elemental|ground (shak|split|heav)|avalanche|landslide|rockslide|"
                     r"osuwisk|trzęsieni|ziemi[aa] (pęk|drż| dudn)",
     "trzęsienie / żywiołak ziemi"),
    ("stone_slide", both(r"stone|rock|boulder|rubble|gravel|scree",
                         r"grind|slid|tumbl|roll|crumbl|cascad|scrap|shift|split|crack|fall"),
     "skały w ruchu"),
    ("glass_shatter", both(r"glass|crystal|bottle|vial|szkł|kryształ|fiolk",
                           r"shatter|break|breaks|splinter|smash|crack|tłucz|pęk|rozbic|krusz"),
     "tłuczenie szkła / kryształu"),
    ("plate_clank", r"armou?r|plate[s]? (clank|clack|shift|scrap|snap)|chainmail|kolczug|zbroj|pancerz|"
                    r"płyt\w* (stal|pancerz|zbroj)|blach",
     "pancerz / płyty"),
    ("electric_zap", r"\bzaps?\b|static (spark|crackl|snap)|sparks? (snap|strike|crackl|jump)|"
                     r"arc of (electric|energy)|electric (snap|crackl|discharge)|wyładowani|przeskok iskry",
     "wyładowanie / iskra"),
    ("steam_hiss", both(r"hiss|syczen|syk", r"steam|vapo[u]?r|gas|gaz|par[ay]|jet|vent|wyziew"),
     "syk pary / gazu (syk musi być parą/gazem, nie przypadkowym słowem)"),
    ("chain_rattle", r"chain|rattles? (of|as) (plates|mail)|chainmail|kolczug|łańcuch|zbrojn\w+ płyt",
     "łańcuch / kolczuga"),
    ("heavy_footsteps", r"footstep|heavy (boot|step|tread)|hoof|gallop|stomp|krok[iy]|kopyt|tupot|galop",
     "kroki / kopyta"),
    ("wing_flutter", r"\bwings?\b (beat|flap|flutter|burst)|flutter(ing)? (of )?wings|wingbeats|"
                     r"skrzydł|trzepot|łopot",
     "skrzydła"),
    ("fire_crackle", r"fire crackl|crackling (fire|flame|ember)|flames? (roar|crackl)|embers? crackl|"
                     r"trzask\w* (ogni|żar)|ogni\w+ trzask|płomień|żar",
     "ogień / żar"),
    ("water_splash", r"splash|plunge into water|impact into (water|pool)|plusk|chlup|wpad\w+ (do )?wod",
     "plusk"),
    ("liquid_pour", r"pour(ing)? (liquid|water|potion)|liquid (pour|glug)|bubbling (potion|vial|flask)|"
                    r"lanie|przelew|bulgot|fiolk|mikstur",
     "ciecz / mikstura"),
    ("door_creak", r"creak|creaking|hinge|skrzyp|zawias",
     "skrzypienie"),
    ("bone_snap", r"bone[s]? (snap|crack|break)|snap of bone|breaking bone|kość|kości (pęk|trzask|łama)",
     "kości"),
    ("insect_swarm", r"insect|swarm|buzzing (of|wing)|beetle|owad|rój|bzyk",
     "rój"),
    ("mechanism_click", r"clockwork|ticking|gear[s]? (click|tick|turn)|lock (click|turn)|latch|mechanizm|"
                        r"zegarow|zapadk|zamek (klik|obr)",
     "mechanizm"),
    ("magic_shimmer", r"magic|arcane|shimmer|sparkle|enchant|glow|humm?ing (energy|crystal)|"
                      r"magicz|czar|zaklę|aur[ay]|migot",
     "magia"),
    ("wind_gust", r"\bwind\b|gust|howling air|wiatr|podmuch|wicher",
     "wiatr"),
    ("creature_roar", r"\broar|bellow|growl|snarl|ryk|warcz|porykiw",
     "ryk / warczenie"),
    ("creature_cackle", r"cackle|cackling|chitter|skitter(ing)? laugh|chichot|pokrzykiw",
     "chichot"),
    ("beast_screech", r"screech|shriek of a (beast|creature)|wrzask|pisk",
     "wrzask bestii"),
    ("undead_groan", r"\bmoan|groan|undead|zombie|jęk|pomruk",
     "jęk"),
    ("psychic_shriek", r"psychic|mind (stab|blast|shriek)|psionic|psychiczn|umysł",
     "uderzenie psychiczne"),
    ("forest_birdsong", r"bird|crow|raven|owl|birdsong|ptak|kruk|sowa|ćwierk",
     "ptaki"),
    ("robot_servo", r"servo|robot|automaton|construct|hydraulic|serwo|robot|automat",
     "serwo / mechanizm robota"),
    ("war_machine", r"war machine|gunship|engine (roar|spool)|reactor|dredge|machina wojenn|silnik|reaktor",
     "machina wojenna"),
    ("heavy_impact", r"\bimpact\b|heavy (blow|slam|hit)|slam|uderzeni|cios|trzask drzwi",
     "ciężkie uderzenie"),
]
COMPILED = [(a, re.compile(rx, re.I), note) for a, rx, note in RULES]


def assign(text: str) -> tuple[str | None, str | None]:
    for archetype, rx, note in COMPILED:
        if rx.search(text):
            return archetype, note
    return None, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", type=Path, default=ROOT / "data/samples/scenarios.jsonl")
    ap.add_argument("--apply", action="store_true", help="zapisz archetype do scenarios.jsonl")
    ap.add_argument("--overwrite", action="store_true", help="nadpisz archetypy ustawione ręcznie")
    ap.add_argument("--json", type=Path, dest="json_out",
                    default=ROOT / "data/samples/archetype-assignment-latest.json")
    ap.add_argument("--markdown", type=Path)
    ap.add_argument("--top-unassigned", type=int, default=30)
    args = ap.parse_args()

    rows = [json.loads(l) for l in args.scenarios.read_text(encoding="utf-8").splitlines() if l.strip()]
    known = set(CONTRACTS)
    missing = {a for a, _, _ in RULES} - known
    if missing:
        raise SystemExit(f"reguły wskazują archetypy bez kontraktu: {sorted(missing)}")

    out, by_arch, unassigned = [], collections.Counter(), []
    for row in rows:
        sid = str(row["story_id"])
        text = clean_text(row)
        archetype, note = assign(text)
        manual = row.get("archetype")
        if manual and not args.overwrite:
            archetype, note = manual, "ręczna deklaracja"
        out.append({"id": sid, "title": row.get("title"), "archetype": archetype,
                    "rule": note, "prompt": row.get("prompt", "")[:160]})
        if archetype:
            by_arch[archetype] += 1
        else:
            unassigned.append((sid, row.get("title"), row.get("prompt", "")[:150]))

    covered = len(out) - len(unassigned)
    print(f"fabuł: {len(out)} · z archetypem: {covered} ({covered / len(out):.0%}) · "
          f"bez przypisania: {len(unassigned)}")
    print(f"archetypów użytych: {len(by_arch)} z {len(known)} zdefiniowanych")
    for a, c in by_arch.most_common():
        print(f"  {c:>4}  {a}")

    payload = {"total": len(out), "covered": covered, "unassigned": len(unassigned),
               "by_archetype": dict(by_arch.most_common()), "assignments": out,
               "unassigned_rows": [{"id": i, "title": t, "prompt": p} for i, t, p in unassigned]}
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"raport: {args.json_out}")

    if args.markdown:
        lines = ["# Przypisanie archetypów — triage katalogu",
                 "",
                 f"Fabuł: **{len(out)}** · z archetypem: **{covered}** ({covered / len(out):.0%}) · "
                 f"bez przypisania: **{len(unassigned)}**",
                 "",
                 "Przypisanie regułami z promptu (nie z tytułu). Fabuły bez trafienia zostają bez",
                 "archetypu — skrypt nie zgaduje.",
                 "",
                 "| Archetyp | Kart |", "|---|---:|"]
        lines += [f"| {a} | {c} |" for a, c in by_arch.most_common()]
        lines += ["", f"## Bez przypisania ({len(unassigned)})", ""]
        lines += [f"- `{i}` {t} — {p}" for i, t, p in unassigned[:args.top_unassigned]]
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"markdown: {args.markdown}")

    if args.apply:
        changed = 0
        for row, rec in zip(rows, out):
            if rec["archetype"] and (args.overwrite or not row.get("archetype")):
                if row.get("archetype") != rec["archetype"]:
                    row["archetype"] = rec["archetype"]
                    changed += 1
        args.scenarios.write_text(
            "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
            encoding="utf-8")
        print(f"zapisano {changed} nowych archetypów do {args.scenarios}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
