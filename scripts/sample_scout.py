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
        return response.read(MAX_SAMPLE_BYTES)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "query"


# Wolne: CC0 i Public Domain Mark. „Public domain” w prozie bywa notą
# archiwum o NIEZNANYM statusie, więc sam ten zwrot nie wystarcza.
PD_URL_MARKERS = (CC0_URL_MARKER, "creativecommons.org/publicdomain/mark")
LICENCE_RED_FLAGS = (
    "copyright status unknown", "may be protected", "all rights reserved",
    "permission of the copyright", "rights reserved", "noncommercial", "non-commercial",
    "nc/", "by-nc", "educational use", "fair use",
)


def licence_status(license_field: object) -> str:
    """Zwraca 'free' | 'unknown' | 'restricted'.

    Polityka właściciela (2026-09-23): projekt jest prywatny i niekomercyjny,
    pliki lądują na dysku lokalnym, więc brak podanej licencji NIE dyskwalifikuje
    kandydata — zapisujemy status i lecimy dalej. Materiał jawnie wolny ma
    pierwszeństwo w rankingu; jawne zastrzeżenia komercyjne oznaczamy, żeby
    nie trafiły przypadkiem do publicznej gablotki Pages.
    """
    value = str(license_field or "").lower()
    if not value.strip():
        return "unknown"
    if any(marker in value for marker in PD_URL_MARKERS):
        return "free"
    if len(value) <= 80 and ("creative commons 0" in value or "cc0" in value):
        return "free"
    if any(flag in value for flag in LICENCE_RED_FLAGS):
        return "restricted"
    return "unknown"


def is_cc0(license_field: object) -> bool:
    """Czy pole licencji oznacza materiał wolny (CC0 / Public Domain Mark).

    Regresja 2026-09-23: przebieg Scouta przyniósł nagranie z notą
    „Copyright status unknown… may be protected by the U.S. Copyright Law”,
    bo tekst zawierał zwrot „public domain” w zdaniu o tym, czego NIE wolno.
    Dlatego: najpierw twarde odrzucenie po frazach ostrzegawczych, dopiero
    potem rozpoznanie po URL-u licencji (a nie po dowolnej prozie).
    """
    if not license_field:
        return False
    value = str(license_field).lower()
    if any(flag in value for flag in LICENCE_RED_FLAGS):
        return False
    if any(marker in value for marker in PD_URL_MARKERS):
        return True
    # Krótka etykieta API (Freesound) — proza archiwum tu nie przejdzie.
    return len(value) <= 80 and ("creative commons 0" in value or "cc0" in value)


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
def fetch_archiveorg(query: str, count: int, allow_unknown: bool = True) -> list[dict]:
    """Search Internet Archive for CC0 audio.

    Two lessons are baked in (2026-09-23, empty result for a stream query):

    * the CC0 filter belongs in the Lucene query, not in a local pass over
      the most-downloaded rows — popular Archive audio is almost never CC0,
      so filtering afterwards returned nothing for perfectly common sounds;
    * field recordings are long. Accept large files and cut a window later
      instead of demanding a whole file under the download cap.
    """
    licence_clause = (
        'licenseurl:("*publicdomain/zero*" OR "*creativecommons.org/licenses/publicdomain*")'
    )
    queries = [
        f"({query}) AND mediatype:(audio) AND {licence_clause}",
        # Fallback: Archive also flags public-domain items without a CC0 URL.
        f"({query}) AND mediatype:(audio) AND (rights:(public domain) OR licenseurl:(*publicdomain*))",
    ]
    if allow_unknown:
        # Prywatny, niekomercyjny użytek: materiał bez podanej licencji też jest
        # dopuszczony (decyzja właściciela), ale dopiero po wyczerpaniu wolnego.
        queries.append(f"({query}) AND mediatype:(audio)")
    seen: set[str] = set()
    candidates: list[dict] = []
    for lucene in queries:
        if len(candidates) >= count:
            break
        params = urllib.parse.urlencode({
            "q": lucene,
            "fl[]": ["identifier", "title", "creator", "downloads", "licenseurl"],
            "rows": max(count * 8, 40),
            "sort[]": "downloads desc",
            "output": "json",
        }, doseq=True)
        try:
            payload = json.loads(http_get(f"https://archive.org/advancedsearch.php?{params}"))
        except Exception as error:
            print(f"archive.org: zapytanie nie powiodło się ({error})", file=sys.stderr)
            continue
        docs = (payload.get("response") or {}).get("docs", [])
        print(f"archive.org: {len(docs)} pozycji dla filtra licencyjnego", file=sys.stderr)
        for doc in docs:
            if len(candidates) >= count:
                break
            identifier = str(doc.get("identifier", ""))
            if not identifier or identifier in seen:
                continue
            seen.add(identifier)
            try:
                metadata = json.loads(http_get(f"https://archive.org/metadata/{identifier}"))
            except Exception as error:
                print(f"skip {identifier}: metadata ({error})", file=sys.stderr)
                continue
            meta = metadata.get("metadata") or {}
            licence = meta.get("licenseurl") or doc.get("licenseurl") or meta.get("rights") or ""
            status = licence_status(licence)
            if status == "restricted" and not allow_unknown:
                print(f"skip {identifier}: licencja zastrzeżona "
                      f"({str(licence)[:70]!r})", file=sys.stderr)
                continue
            files = [
                item for item in metadata.get("files", [])
                if "mp3" in str(item.get("format", "")).lower()
                and str(item.get("name", "")).lower().endswith(".mp3")
                and float(item.get("size") or 0) >= MIN_SAMPLE_BYTES
            ]
            if not files:
                continue
            # Prefer a file we can fetch whole; otherwise take the smallest and
            # download a capped prefix (enough to cut an 8 s window from).
            files.sort(key=lambda item: float(item.get("size") or 0))
            picked = next(
                (item for item in files if float(item.get("size") or 0) <= MAX_SAMPLE_BYTES),
                files[0],
            )
            filename = str(picked["name"])
            size = int(float(picked.get("size") or 0))
            candidates.append({
                "source": "archive.org",
                "source_id": identifier,
                "download_url": f"https://archive.org/download/{identifier}/{urllib.parse.quote(filename, safe='/')}",
                "name": f"{doc.get('title', identifier)} — {Path(filename).name}",
                "author": doc.get("creator") or meta.get("creator") or "unknown",
                "license": str(licence) or "brak informacji",
                "license_status": status,
                "source_url": f"https://archive.org/details/{identifier}",
                "duration_sec": None,
                "avg_rating": None,
                "num_ratings": None,
                "downloads": doc.get("downloads"),
                "archive_file": filename,
                "archive_file_bytes": size,
                "truncated": size > MAX_SAMPLE_BYTES,
                "note": ("Internet Archive nie publikuje oceny gwiazdkowej; ranking wg pobrań."
                         + (" Pobrano początek pliku (nagranie dłuższe niż limit)."
                            if size > MAX_SAMPLE_BYTES else "")),
            })
    candidates.sort(key=lambda item: (item.get("license_status") == "free",
                                      int(item.get("downloads") or 0)), reverse=True)
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
            if len(blob) > MAX_SAMPLE_BYTES:
                # Field recordings bywają wielominutowe; bierzemy początek pliku,
                # z którego i tak wycinamy okno kilku sekund.
                blob = blob[:MAX_SAMPLE_BYTES]
            if len(blob) < MIN_SAMPLE_BYTES:
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
    parser.add_argument("--free-only", action="store_true",
                        help="tylko materiał jawnie wolny (CC0/PD Mark); domyślnie "
                             "dopuszczamy też nieznaną licencję — użytek prywatny")
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
        candidates = fetch_archiveorg(args.query, args.count,
                                      allow_unknown=not args.free_only)
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
