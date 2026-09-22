#!/usr/bin/env python3
"""Tests for the live-samples rule (AGENTS.md #14).

Covers both enforcement points:
- scripts/render_jingle.py::validate_live_samples (recipe gate; needs numpy,
  skipped with a clear message when the authoring venv is absent),
- scripts/validate_versions.py genre checks (stdlib only, always runs).

Run: python scripts/test_rules.py   (exit 0 = all tests pass)
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

PASS, FAIL = "OK", "BŁĄD"
results: list[tuple[str, str, str]] = []


def record(name: str, ok: bool, note: str = "") -> None:
    results.append((name, PASS if ok else FAIL, note))


# ---------------------------------------------------------------- render gate
def test_render_gate() -> None:
    try:
        from render_jingle import validate_live_samples
    except ImportError as error:  # numpy missing -> authoring venv not active
        results.append(("render: bramka żywych sampli", "SKIP", f"brak zależności autorskich: {error}"))
        return

    stem = {"type": "stem", "file": "whoosh_flap.mp3", "time_sec": 2.0}
    stem_late = {"type": "stem", "file": "raven_call.mp3", "time_sec": 5.0}
    synth = {"type": "synth", "kind": "chime", "time_sec": 1.0, "length_sec": 0.5, "params": {}}

    def recipe(genre: str, events: list) -> dict:
        return {"genre": genre, "climax_window": [1.5, 3.8], "events": events}

    def rejects(r: dict) -> bool:
        try:
            validate_live_samples(r)
            return False
        except ValueError:
            return True

    record("render: brak genre -> odrzucenie", rejects({"climax_window": [1.5, 3.8], "events": [stem]}))
    record("render: sci-fi z 1 stemem -> akcept", not rejects(recipe("sci-fi", [synth, stem])))
    record("render: sci-fi bez stemów -> odrzucenie", rejects(recipe("sci-fi", [synth])))
    record("render: fantasy z 1 stemem -> odrzucenie", rejects(recipe("fantasy", [synth, stem])))
    record("render: fantasy 2 stemy, kulminacja żywa -> akcept", not rejects(recipe("fantasy", [synth, stem, stem_late])))
    record("render: fantasy 2 stemy poza oknem kulminacji -> odrzucenie",
           rejects(recipe("fantasy", [synth, stem_late, dict(stem_late, file="bear_growl.mp3")])))


# ------------------------------------------------------------ metadata checks
def run_validator(payload: dict) -> int:
    import validate_versions

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(payload, tmp, ensure_ascii=True)
        path = tmp.name
    old_argv = sys.argv
    try:
        sys.argv = ["validate_versions.py", path]
        return validate_versions.main()
    except SystemExit as error:  # defensive: main() may evolve to sys.exit
        return int(error.code or 0)
    finally:
        sys.argv = old_argv
        Path(path).unlink(missing_ok=True)


def version(genre: str | None, live: int, synth: int = 1) -> dict:
    events = [{"time_sec": 1.0 + i, "sample": f"live_{i}.mp3", "role": "foley"} for i in range(live)]
    events += [{"time_sec": 4.0, "sample": "synth:chime", "role": "detal"} for _ in range(synth)]
    design = {
        "description": "opis", "ambience": "wind", "drone": "brak", "events": events,
        "mix_notes": "notatki",
        "qa": {"score": 87.0, "base": 70.0, "dramaturgy": 17.0, "status": "pass", "details": []},
    }
    if genre:
        design["genre"] = genre
    return {"label": "v1", "project_description": design}


def test_validator() -> None:
    base = {"stories": [{"id": "1", "versions": []}]}

    base["stories"][0]["versions"] = [version("sci-fi", live=1)]
    record("validator: sci-fi z 1 żywym eventem -> akcept", run_validator(json.loads(json.dumps(base))) == 0)

    base["stories"][0]["versions"] = [version("sci-fi", live=0, synth=2)]
    record("validator: sci-fi bez żywych eventów -> odrzucenie", run_validator(json.loads(json.dumps(base))) == 1)

    base["stories"][0]["versions"] = [version("fantasy", live=1)]
    record("validator: fantasy z 1 żywym eventem -> odrzucenie", run_validator(json.loads(json.dumps(base))) == 1)

    base["stories"][0]["versions"] = [version("fantasy", live=2)]
    record("validator: fantasy z 2 żywymi eventami -> akcept", run_validator(json.loads(json.dumps(base))) == 0)

    base["stories"][0]["versions"] = [version(None, live=0)]
    record("validator: wersja historyczna bez genre -> akcept", run_validator(json.loads(json.dumps(base))) == 0)


def test_sync_state_refresh() -> None:
    import sync_ratings

    data = {"stories": [{"id": "1", "versions": [{"label": "v1", "reports": [], "score": None, "scores": None}]}]}
    issue = {
        "html_url": "https://example.invalid/issues/1",
        "created_at": "2026-01-01T00:00:00Z",
        "state": "open",
        "body": "<!-- jingle-feedback: 1:v1 -->\n**Feeling:** 3/5\n**Story fit:** 3/5\n**Sample quality:** 3/5\n**Comment:** x",
    }
    rating = sync_ratings.parse_issue(issue)
    sync_ratings.apply_ratings(data, [rating])
    # Same issue comes back on the next sync with an updated state.
    sync_ratings.apply_ratings(data, [dict(rating, state="closed")])
    version = data["stories"][0]["versions"][0]
    reports = version["reports"]
    record("sync: ponowny sync odświeża stan raportu bez duplikatu",
           len(reports) == 1 and reports[0]["state"] == "closed" and version["score"] == 9)


def test_sync_report_refresh() -> None:
    import sync_ratings

    data = {"stories": [{"id": "1", "versions": [{"label": "v1", "reports": [], "score": None, "scores": None}]}]}
    original = {
        "html_url": "https://example.invalid/issues/1",
        "created_at": "2026-01-01T00:00:00Z",
        "state": "open",
        "body": "<!-- jingle-feedback: 1:v1 -->\n**Feeling:** 2/5\n**Story fit:** 2/5\n**Sample quality:** 2/5\n**Comment:** original",
    }
    edited = {
        **original,
        "state": "closed",
        "body": "<!-- jingle-feedback: 1:v1 -->\n**Feeling:** 5/5\n**Story fit:** 4/5\n**Sample quality:** 3/5\n**Comment:** poprawiony komentarz",
    }
    sync_ratings.apply_ratings(data, [sync_ratings.parse_issue(original)])
    sync_ratings.apply_ratings(data, [sync_ratings.parse_issue(edited)])
    version = data["stories"][0]["versions"][0]
    report = version["reports"][0]
    record("sync: edytowany raport odświeża wynik i komentarz w historii",
           version["score"] == 12 and report["scores"] == {"feeling": 5, "story_fit": 4, "sample_quality": 3}
           and report["comment"] == "poprawiony komentarz" and report["state"] == "closed")


def main() -> int:
    test_render_gate()
    test_validator()
    test_sync_state_refresh()
    test_sync_report_refresh()
    failures = 0
    for name, status, note in results:
        suffix = f" ({note})" if note else ""
        print(f"{status:5} {name}{suffix}")
        if status == FAIL:
            failures += 1
    print(f"\n{len(results)} testów, {failures} błędów" + ("" if "SKIP" not in {r[1] for r in results} else " (część SKIP)"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
