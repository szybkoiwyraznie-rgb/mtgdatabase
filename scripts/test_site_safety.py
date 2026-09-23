#!/usr/bin/env python3
"""Regression checks for safe interpolation of catalog data into Pages HTML."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MALICIOUS = '<script>alert("catalog-xss")</script>'


def main() -> int:
    catalog = {
        "stories": [{
            "id": "999",
            "title": MALICIOUS,
            "story": MALICIOUS,
            "versions": [{
                "label": "v1",
                "audio": "audio/999.mp3",
                "score": 12,
                "scores": {"feeling": MALICIOUS, "story_fit": MALICIOUS, "sample_quality": MALICIOUS},
                "reports": [{
                    "issue_url": MALICIOUS,
                    "created_at": "2026-09-23T00:00:00Z",
                    "state": "closed",
                    "scores": {"feeling": 4, "story_fit": 4, "sample_quality": 4},
                    "total": 12,
                    "comment": MALICIOUS,
                }],
                "project_description": {
                    "description": MALICIOUS,
                    "qa": {"score": MALICIOUS, "details": [MALICIOUS]},
                },
            }],
        }],
    }
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        catalog_path = temp_path / "catalog.json"
        output = temp_path / "site"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        subprocess.run(
            [sys.executable, "scripts/build_site.py", "--catalog", str(catalog_path), "--output", str(output)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        page = (output / "stories" / "999" / "index.html").read_text(encoding="utf-8")

    escaped = "&lt;script&gt;alert(&quot;catalog-xss&quot;)&lt;/script&gt;"
    assert MALICIOUS not in page, "niebezpieczne dane katalogu trafiły do HTML bez escapingu"
    assert escaped in page, "dane katalogu nie zostały poprawnie escaped"
    assert 'class="rated-comment"' in page, "komentarz właściciela nie jest renderowany na karcie ocenionej wersji"

    app = (ROOT / "site/assets/app.js").read_text(encoding="utf-8")
    assert "const storyTitle = escapeHtml(story.title);" in app, "homepage nie escape'uje tytułu z katalogu"
    assert " ${story.title}</a>" not in app, "homepage interpoluje surowy tytuł do innerHTML"
    print("OK  HTML z katalogu jest escapowany w stronie szczegółów i na liście")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
