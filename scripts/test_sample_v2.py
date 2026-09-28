from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=cwd, text=True, capture_output=True, check=True)


class SampleV2Tests(unittest.TestCase):
    def test_validate_sample_scenarios_accepts_short_homogeneous_sample(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            catalog = tmp / "catalog.json"
            catalog.write_text(json.dumps({"stories": [{"id": "1", "title": "Bell", "story": "A bell rings."}]}), encoding="utf-8")
            scenarios = tmp / "scenarios.jsonl"
            scenarios.write_text(json.dumps({
                "story_id": "1",
                "title": "Bell",
                "sample_scenario": "pojedyncze uderzenie starego dzwonu",
                "prompt": "A single old bronze bell strike, short decay, no music, no speech.",
                "duration_seconds": 2.0,
                "status": "ready",
                "batch": "b001",
            }, ensure_ascii=False) + "\n", encoding="utf-8")
            cp = run("scripts/validate_sample_scenarios.py", str(scenarios), "--catalog", str(catalog))
            self.assertIn("1 total", cp.stdout)

    def test_elevenlabs_sample_scout_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            scenarios = tmp / "scenarios.jsonl"
            scenarios.write_text(json.dumps({
                "story_id": "2",
                "title": "Crow",
                "sample_scenario": "krótkie krakanie wrony",
                "prompt": "A short crow caw, close and dry, no music, no speech.",
                "duration_seconds": 1.5,
                "status": "ready",
                "batch": "b001",
            }, ensure_ascii=False) + "\n", encoding="utf-8")
            cp = run("scripts/elevenlabs_sample_scout.py", "--scenarios", str(scenarios), "--dry-run")
            self.assertIn("2.mp3", cp.stdout)
            self.assertIn("no music", cp.stdout.lower())

    def test_elevenlabs_sample_scout_posts_to_mock_api_and_writes_mp3(self) -> None:
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                self.server.seen_body = body  # type: ignore[attr-defined]
                data = b"ID3" + (b"x" * 2048)
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, fmt, *args):
                pass

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            scenarios = tmp / "scenarios.jsonl"
            scenarios.write_text(json.dumps({
                "story_id": "3",
                "title": "Fall",
                "sample_scenario": "krótki łoskot upadku zbroi na kamień",
                "prompt": "A short armor crash falling on stone, dry impact, no music, no speech.",
                "duration_seconds": 2.0,
                "status": "ready",
                "batch": "b001",
            }, ensure_ascii=False) + "\n", encoding="utf-8")
            server = HTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                env = {**os.environ, "ELEVENLABS": "dummy", "ELEVENLABS_SOUNDGEN_ENDPOINT": f"http://127.0.0.1:{server.server_port}/sound"}
                out = tmp / "out"
                manifest = tmp / "manifest.jsonl"
                cp = subprocess.run([
                    sys.executable, "scripts/elevenlabs_sample_scout.py",
                    "--scenarios", str(scenarios), "--out", str(out), "--manifest", str(manifest), "--limit", "1",
                ], cwd=ROOT, text=True, capture_output=True, check=True, env=env)
                self.assertIn("OK 3", cp.stdout)
                self.assertTrue((out / "3.mp3").exists())
                self.assertIn("armor crash", server.seen_body.decode("utf-8"))  # type: ignore[attr-defined]
                self.assertIn("generated", manifest.read_text(encoding="utf-8"))
            finally:
                server.shutdown()
                thread.join(timeout=2)
                server.server_close()

    def test_build_pack_uses_audio_samples(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            src = tmp / "samples"
            src.mkdir()
            (src / "10.mp3").write_bytes(b"fake mp3 bytes")
            out = tmp / "pack.zip"
            cp = run("scripts/build_pack.py", "--src", str(src), "--output", str(out))
            self.assertTrue(out.exists())
            self.assertIn("1 sample", cp.stdout)

    def test_build_site_lists_scenarios_and_samples(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            catalog = tmp / "catalog.json"
            catalog.write_text(json.dumps({"stories": [{"id": "1", "title": "Bell", "story": "A bell rings."}]}), encoding="utf-8")
            scenarios = tmp / "scenarios.jsonl"
            scenarios.write_text(json.dumps({
                "story_id": "1",
                "title": "Bell",
                "sample_scenario": "pojedyncze uderzenie starego dzwonu",
                "prompt": "A single old bronze bell strike, no music, no speech.",
                "duration_seconds": 2.0,
                "status": "ready",
                "batch": "b001",
            }, ensure_ascii=False) + "\n", encoding="utf-8")
            samples = tmp / "audio"
            samples.mkdir()
            (samples / "1.mp3").write_bytes(b"fake mp3 bytes")
            out = tmp / "site"
            run("scripts/build_site.py", "--catalog", str(catalog), "--scenarios", str(scenarios),
                "--samples", str(samples), "--out", str(out), "--audit", str(tmp / "no-audit.json"))
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("Biblioteka sampli v2", html)
            self.assertIn("pojedyncze uderzenie", html)
            self.assertTrue((out / "samples" / "1.mp3").exists())
            self.assertNotIn('class="chips"', html)

    def test_build_site_renders_audit_flags_and_filters(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            catalog = tmp / "catalog.json"
            catalog.write_text(json.dumps({"stories": [
                {"id": "1", "title": "Bell", "story": "A bell rings."},
                {"id": "2", "title": "Crow", "story": "A crow caws."},
            ]}), encoding="utf-8")
            scenarios = tmp / "scenarios.jsonl"
            scenarios.write_text("\n".join(json.dumps({
                "story_id": sid,
                "title": title,
                "sample_scenario": scenario,
                "prompt": "A short sound, no music, no speech.",
                "duration_seconds": 2.0,
                "status": "ready",
                "batch": "b001",
            }, ensure_ascii=False) for sid, title, scenario in [
                ("1", "Bell", "pojedyncze uderzenie starego dzwonu"),
                ("2", "Crow", "krótkie krakanie wrony"),
            ]) + "\n", encoding="utf-8")
            samples = tmp / "audio"
            samples.mkdir()
            (samples / "1.mp3").write_bytes(b"fake mp3 bytes")
            (samples / "2.mp3").write_bytes(b"fake mp3 bytes")
            audit = tmp / "audit.json"
            audit.write_text(json.dumps({
                "files": [
                    {"id": "1", "flags": ["too_quiet", "sub_dominant"], "lufs": -40.0,
                     "peak_db": -12.0, "true_peak_dbtp": -11.5, "content_s": 1.2},
                    {"id": "2", "flags": [], "lufs": -16.0, "peak_db": -0.5,
                     "true_peak_dbtp": 0.2, "content_s": 2.0},
                ],
                "similar_pairs": [{"a": "1", "b": "2", "cosine": 0.99}],
            }), encoding="utf-8")
            out = tmp / "site"
            cp = run("scripts/build_site.py", "--catalog", str(catalog), "--scenarios", str(scenarios),
                     "--samples", str(samples), "--out", str(out), "--audit", str(audit))
            self.assertIn("audyt: 2", cp.stdout)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn('data-flags="too_quiet sub_dominant twin"', html)
            self.assertIn("-40.0 LUFS", html)
            self.assertIn('data-flag="too_quiet"', html)  # filtr w pasku chipów
            self.assertIn("bliźniak", html)


if __name__ == "__main__":
    unittest.main()
