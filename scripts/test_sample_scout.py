#!/usr/bin/env python3
"""Offline regression tests for the GitHub Actions Sample Scout connectors."""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "scripts")
import sample_scout as scout


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"OK  {name}")


def test_helpers() -> None:
    check("CC0 label is accepted", scout.is_cc0("Creative Commons 0"))
    check("CC0 URL is accepted", scout.is_cc0("https://creativecommons.org/publicdomain/zero/1.0/"))
    check("CC-BY is rejected", not scout.is_cc0("Creative Commons Attribution 4.0"))
    check("slug is stable", scout.slugify("Wolf Howl #42") == "wolf-howl-42")
    check("ID3 is recognised", scout.is_mp3(b"ID3\x04\x00"))
    check("MPEG frame is recognised", scout.is_mp3(b"\xff\xfb\x90\x00"))
    check("HTML is rejected", not scout.is_mp3(b"<html>error</html>"))
    try:
        scout.validate_args("wolf", scout.MAX_CANDIDATES + 1)
    except ValueError:
        print("OK  candidate count is bounded")
    else:
        raise AssertionError("candidate count is bounded")


def test_freesound_filter_and_ranking() -> None:
    old_get = scout.http_get
    payload = {
        "results": [
            {"id": 1, "name": "low", "username": "a", "license": "Creative Commons 0", "avg_rating": 4.0,
             "num_ratings": 50, "downloads": 100, "previews": {"preview-hq-mp3": "https://cdn/1"}},
            {"id": 2, "name": "high", "username": "b", "license": "Creative Commons 0", "avg_rating": 5.0,
             "num_ratings": 1, "downloads": 2, "download": "https://api/2/download/", "previews": {"preview-hq-mp3": "https://cdn/2"}},
            {"id": 3, "name": "by", "username": "c", "license": "Attribution 4.0", "avg_rating": 5.0,
             "num_ratings": 999, "downloads": 999, "previews": {"preview-hq-mp3": "https://cdn/3"}},
        ]
    }
    scout.http_get = lambda *_args, **_kwargs: json.dumps(payload).encode()
    try:
        results = scout.fetch_freesound("wolf", 5, "rating_desc", "not-a-real-token")
    finally:
        scout.http_get = old_get
    check("Freesound retains only CC0", [item["source_id"] for item in results] == ["2", "1"])
    check("Freesound preserves community metrics", results[0]["num_ratings"] == 1 and results[1]["downloads"] == 100)
    check("Freesound prefers the authenticated original", results[0]["download_url"] == "https://api/2/download/" and results[0]["retrieval"] == "original")


def test_archive_accepts_vbr_mp3() -> None:
    old_get = scout.http_get
    search = {"response": {"docs": [{
        "identifier": "cc0-audio", "title": "CC0 audio", "creator": "maker", "downloads": 42,
        "licenseurl": "https://creativecommons.org/publicdomain/zero/1.0/",
    }]}}
    metadata = {"files": [
        {"name": "notes.txt", "format": "Text", "size": "200"},
        {"name": "clip.mp3", "format": "VBR MP3", "size": "64000"},
    ]}
    calls = iter([json.dumps(search).encode(), json.dumps(metadata).encode()])
    scout.http_get = lambda *_args, **_kwargs: next(calls)
    try:
        results = scout.fetch_archiveorg("steam", 1)
    finally:
        scout.http_get = old_get
    check("Archive accepts VBR MP3 metadata", len(results) == 1 and results[0]["archive_file"] == "clip.mp3")
    check("Archive candidate has original details URL", results[0]["source_url"].endswith("cc0-audio"))


def main() -> int:
    test_helpers()
    test_freesound_filter_and_ranking()
    test_archive_accepts_vbr_mp3()
    print("Sample Scout tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def test_archiveorg_finds_cc0_behind_popular_non_cc0_rows(monkeypatch):
    """Regresja 2026-09-23: puste wyniki dla 'creek stream flowing water'.

    Stara wersja pobierała najpopularniejsze audio i dopiero lokalnie
    filtrowała CC0 — popularne pozycje Archive praktycznie nigdy nie są CC0,
    więc lista wychodziła pusta. Filtr licencyjny musi być w zapytaniu.
    """
    seen_queries = []

    def fake_get(url, token=None, timeout=30):
        if "advancedsearch" in url:
            seen_queries.append(url)
            return json.dumps({"response": {"docs": [{
                "identifier": "creek01", "title": "Mountain Creek",
                "creator": "fieldrec", "downloads": 900,
                "licenseurl": "http://creativecommons.org/publicdomain/zero/1.0/",
            }]}}).encode()
        if "metadata" in url:
            return json.dumps({
                "metadata": {"licenseurl": "http://creativecommons.org/publicdomain/zero/1.0/"},
                "files": [{"name": "creek.mp3", "format": "VBR MP3", "size": "48000000"}],
            }).encode()
        return b"\xff\xfb" + b"\x00" * 5000

    monkeypatch.setattr(scout, "http_get", fake_get)
    found = scout.fetch_archiveorg("creek stream flowing water", 3)

    assert found, "kandydat CC0 musi zostać znaleziony"
    assert "publicdomain" in seen_queries[0], "filtr licencyjny należy do zapytania"
    # długie nagranie terenowe nie może być odrzucone przez limit rozmiaru
    assert found[0]["truncated"] is True
    assert found[0]["archive_file"] == "creek.mp3"


def test_licence_status_classifies_free_unknown_and_restricted():
    """Polityka właściciela: prywatny użytek dopuszcza nieznaną licencję.

    Wolne (CC0/PD Mark) ma pierwszeństwo w rankingu, brak informacji jest
    dopuszczony i oznaczony, a jawne zastrzeżenia komercyjne wyróżnione,
    żeby nie trafiły do publicznej gablotki.
    """
    assert scout.licence_status("https://creativecommons.org/publicdomain/zero/1.0/") == "free"
    assert scout.licence_status("http://creativecommons.org/publicdomain/mark/1.0/") == "free"
    assert scout.licence_status("") == "unknown"
    assert scout.licence_status(None) == "unknown"
    assert scout.licence_status("Copyright status unknown. This work may be protected "
                                "by the U.S. Copyright Law.") == "restricted"
    assert scout.licence_status("http://creativecommons.org/licenses/by-nc/4.0/") == "restricted"


def test_licence_prose_with_public_domain_words_is_rejected():
    """Regresja 2026-09-23: nota „Copyright status unknown” przeszła jako wolna.

    Archiwa opisują status prozą, w której zwrot „public domain” pojawia się
    w zdaniu o tym, czego NIE wolno. Wolny materiał rozpoznajemy po URL-u
    licencji, a frazy ostrzegawcze odrzucamy twardo.
    """
    unknown = ("Copyright status unknown. This work may be protected by the U.S. "
               "Copyright Law (Title 17, U.S.C.). Works not in the public domain "
               "cannot be commercially exploited without permission.")
    assert scout.is_cc0(unknown) is False
    assert scout.is_cc0("https://creativecommons.org/publicdomain/zero/1.0/") is True
    assert scout.is_cc0("http://creativecommons.org/publicdomain/mark/1.0/") is True
    assert scout.is_cc0("Creative Commons 0") is True
    assert scout.is_cc0("http://creativecommons.org/licenses/by-nc/4.0/") is False
