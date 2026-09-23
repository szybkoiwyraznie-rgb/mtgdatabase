#!/usr/bin/env python3
"""Download a small, community-ranked, CC0 sample shortlist on a GitHub runner.

The Arena sandbox cannot reach Freesound or Internet Archive directly. This
script is deliberately run by `.github/workflows/sample-scout.yml`, where the
GitHub Actions runner has normal network access. It downloads *candidates*,
not production stems: an agent still verifies the source and, only after owner
approval at a listening gate, registers the chosen sound in data/library/*.json.

Freesound candidates are ordered by community rating, rating count and
downloads. Internet Archive does not expose an equivalent rating, so its CC0
candidates are ordered by downloads. Downloads are capped, checked for MP3
headers and recorded with SHA-256 in a manifest.

Usage:
  FREESOUND_TOKEN=... python scripts/sample_scout.py \
      --source freesound --query "wolf howl" --count 5 --out legacy/source/sample_scout
  python scripts/sample_scout.py \
      --source archive.org --query "steam vent" --count 3 --out legacy/source/sample_scout
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "mtgdatabase-sample-scout/1.1 (private non-commercial project)"}
SOURCES = ("freesound", "archive.org")
SORTS = ("rating_desc", "downloads_desc", "score")
MAX_CANDIDATES = 5
MAX_QUERY_LENGTH = 120
MAX_SAMPLE_BYTES = 12_000_000
MIN_SAMPLE_BYTES = 2_000
CC0_URL_MARKER = "creativecommons.org/publicdomain/zero"


def http_get(url: str, token: str | None = None, timeout: int = 30) -> bytes:
    headers = dict(UA)
    if token:
        headers["Authorization"] = f"Token {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as response:
        return response.read(MAX_SAMPLE_BYTES + 1)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "query"


def is_cc0(license_field: object) -> bool:
    """Recognise the actual CC0 labels/URLs returned by the two source APIs."""
    if not license_field:
        return False
    value = str(license_field).lower()
    return "creative commons 0" in value or "cc0" in value or CC0_URL_MARKER in value


def is_mp3(blob: bytes) -> bool:
    """Reject HTML/API error documents accidentally saved as an .mp3 file."""
    return blob.startswith(b"ID3") or (len(blob) >= 2 and blob[0] == 0xFF and (blob[1] & 0xE0) == 0xE0)


def validate_args(query: str, count: int) -> None:
    if not query.strip() or len(query.strip()) > MAX_QUERY_LENGTH:
        raise ValueError(f"query musi mieć od 1 do {MAX_QUERY_LENGTH} znaków")
    if not 1 <= count <= MAX_CANDIDATES:
        raise ValueError(f"count musi być w zakresie 1–{MAX_CANDIDATES}")


# --------------------------------------------------------------------------
# Connector: Freesound (community metrics: rating, number of ratings, downloads)
# --------------------------------------------------------------------------
def fetch_freesound(query: str, count: int, sort: str, token: str) -> list[dict]:
    params = urllib.parse.urlencode({
        "query": query,
        "filter": 'license:"Creative Commons 0"',
        # Fetch more than we publish: malformed/incompletely licensed entries
        # are filtered locally before the quality ranking.
        "sort": sort,
        "page_size": min(100, count * 10),
        "fields": "id,name,username,license,duration,avg_rating,num_ratings,downloads,comments,previews,download,url,bitrate,samplerate,channels",
    })
    payload = json.loads(http_get(f"https://freesound.org/apiv2/search/text/?{params}", token))
    candidates: list[dict] = []
    for item in payload.get("results", []):
        preview = (item.get("previews") or {}).get("preview-hq-mp3")
        download = item.get("download") or preview
        if not download or not is_cc0(item.get("license")):
            continue
        candidates.append({
            "source": "freesound",
            "source_id": str(item["id"]),
            "download_url": download,
            "retrieval": "original" if item.get("download") else "preview-hq-mp3",
            "name": item.get("name", str(item["id"])),
            "author": item.get("username") or "unknown",
            "license": str(item["license"]),
            "source_url": item.get("url") or f"https://freesound.org/s/{item['id']}/",
            "duration_sec": item.get("duration"),
            "avg_rating": item.get("avg_rating"),
            "num_ratings": item.get("num_ratings"),
            "downloads": item.get("downloads"),
            "comments": item.get("comments"),
            "bitrate": item.get("bitrate"),
            "samplerate": item.get("samplerate"),
            "channels": item.get("channels"),
        })
    candidates.sort(
        key=lambda item: (
            float(item.get("avg_rating") or 0),
            int(item.get("num_ratings") or 0),
            int(item.get("downloads") or 0),
        ),
        reverse=True,
    )
    return candidates[:count]


# --------------------------------------------------------------------------
# Connector: Internet Archive (community metric: downloads)
# --------------------------------------------------------------------------
def fetch_archiveorg(query: str, count: int) -> list[dict]:
    params = urllib.parse.urlencode({
        "q": f"({query}) AND mediatype:(audio)",
        "fl[]": ["identifier", "title", "creator", "downloads", "licenseurl"],
        "rows": count * 8,
        "sort[]": "downloads desc",
        "output": "json",
    }, doseq=True)
    payload = json.loads(http_get(f"https://archive.org/advancedsearch.php?{params}"))
    candidates: list[dict] = []
    for doc in (payload.get("response") or {}).get("docs", []):
        if not is_cc0(doc.get("licenseurl")) or len(candidates) >= count:
            continue
        identifier = str(doc.get("identifier", ""))
        if not identifier:
            continue
        try:
            metadata = json.loads(http_get(f"https://archive.org/metadata/{identifier}"))
        except Exception as error:
            print(f"skip {identifier}: metadata ({error})", file=sys.stderr)
            continue
        metadata_license = (metadata.get("metadata") or {}).get("licenseurl", doc.get("licenseurl"))
        if not is_cc0(metadata_license):
            print(f"skip {identifier}: metadata nie potwierdza CC0", file=sys.stderr)
            continue
        files = [
            item for item in metadata.get("files", [])
            if "mp3" in str(item.get("format", "")).lower() and str(item.get("name", "")).lower().endswith(".mp3")
        ]
        files.sort(key=lambda item: float(item.get("size", MAX_SAMPLE_BYTES + 1) or MAX_SAMPLE_BYTES + 1))
        picked = next(
            (item for item in files if MIN_SAMPLE_BYTES <= float(item.get("size") or 0) <= MAX_SAMPLE_BYTES),
            None,
        )
        if not picked:
            continue
        filename = str(picked["name"])
        candidates.append({
            "source": "archive.org",
            "source_id": identifier,
            "download_url": f"https://archive.org/download/{identifier}/{urllib.parse.quote(filename, safe='/')}",
            "name": f"{doc.get('title', identifier)} — {Path(filename).name}",
            "author": doc.get("creator") or "unknown",
            "license": str(doc["licenseurl"]),
            "source_url": f"https://archive.org/details/{identifier}",
            "duration_sec": None,
            "avg_rating": None,
            "num_ratings": None,
            "downloads": doc.get("downloads"),
            "archive_file": filename,
            "note": "Internet Archive nie publikuje porównywalnej oceny gwiazdkowej; ranking wg liczby pobrań.",
        })
    candidates.sort(key=lambda item: int(item.get("downloads") or 0), reverse=True)
    return candidates[:count]


def save_candidates(candidates: list[dict], out_dir: Path, token: str | None = None) -> list[dict]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[dict] = []
    for position, candidate in enumerate(candidates, 1):
        source_id = slugify(str(candidate["source_id"]))
        filename = f"{position:02d}-{source_id}-{slugify(candidate['name'])}.mp3"
        target = out_dir / filename
        try:
            blob = http_get(candidate["download_url"], token=token)
            if not MIN_SAMPLE_BYTES <= len(blob) <= MAX_SAMPLE_BYTES:
                raise ValueError(f"nieprawidłowy rozmiar ({len(blob)} B)")
            if not is_mp3(blob):
                raise ValueError("odpowiedź nie ma nagłówka MP3")
            target.write_bytes(blob)
        except Exception as error:
            print(f"skip {filename}: {error}", file=sys.stderr)
            continue
        record = dict(candidate)
        record.pop("download_url", None)
        record.update({
            "file": str(target),
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
            "candidate_rank": position,
        })
        saved.append(record)
        if record.get("avg_rating") is not None:
            metric = f"ocena {record['avg_rating']} ({record.get('num_ratings') or 0} ocen)"
        else:
            metric = f"{record.get('downloads') or 0} pobrań"
        print(f"pobrano {filename} — {metric}")
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", choices=SOURCES, default="freesound")
    parser.add_argument("--query", required=True, help='np. "wolf howl" / "steam vent"')
    parser.add_argument("--count", type=int, default=5, help=f"1–{MAX_CANDIDATES} kandydatów")
    parser.add_argument("--sort", choices=SORTS, default="rating_desc", help="sortowanie Freesound")
    parser.add_argument("--out", type=Path, default=Path("legacy/source/sample_scout"))
    args = parser.parse_args()
    try:
        validate_args(args.query, args.count)
    except ValueError as error:
        parser.error(str(error))

    if args.source == "freesound":
        token = os.environ.get("FREESOUND_TOKEN", "").strip()
        if not token:
            print("Brak FREESOUND_TOKEN. Dodaj sekret Actions z kluczem API Freesound; "
                  "alternatywnie wybierz source=archive.org.", file=sys.stderr)
            return 2
        candidates = fetch_freesound(args.query, args.count, args.sort, token)
    else:
        token = None
        candidates = fetch_archiveorg(args.query, args.count)
    if not candidates:
        print(f"{args.source}: brak kandydatów CC0 dla {args.query!r}.", file=sys.stderr)
        return 1

    destination = args.out / f"{args.source}_{slugify(args.query)}"
    saved = save_candidates(candidates, destination, token=token)
    if not saved:
        print("Nie udało się pobrać żadnego poprawnego MP3.", file=sys.stderr)
        return 1
    manifest_path = destination / "manifest.json"
    manifest_path.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nManifest: {manifest_path} ({len(saved)} kandydatów).")
    print("Kandydat nie jest jeszcze samplem produkcyjnym: agent weryfikuje go, wystawia w "
          "bramce odsłuchowej i dopiero po akceptacji właściciela wpisuje do data/library/*.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
