from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_batch_pack as pack  # noqa: E402

ROWS = [
    {"story_id": "5", "title": "Five", "sample_scenario": "pięć dzwonów", "duration_seconds": 4.0, "batch": "b900", "archetype": "temple_bell"},
    {"story_id": "2", "title": "Two", "sample_scenario": "dwa trzaski", "duration_seconds": 2.0, "batch": "b900", "archetype": "fire_crackle"},
    {"story_id": "9", "title": "Nine", "sample_scenario": "dziewięć kroków", "duration_seconds": 3.0, "batch": "b901", "archetype": "heavy_footsteps"},
]


class BuildBatchPackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.tmp = Path(self.td.name)
        self.src = self.tmp / "samples"
        self.src.mkdir()
        for i in ("2", "5", "9"):
            (self.src / f"{i}.mp3").write_bytes(b"ID3fake" + i.encode())

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_batch_selection_is_numeric_and_batch_scoped(self) -> None:
        ids = pack.select_ids(batch="b900", ids=None, scenarios=ROWS)
        self.assertEqual(ids, ["2", "5"])

    def test_unknown_batch_exits(self) -> None:
        with self.assertRaises(SystemExit):
            pack.select_ids(batch="b999", ids=None, scenarios=ROWS)

    def test_ids_without_scenario_exit(self) -> None:
        with self.assertRaises(SystemExit):
            pack.select_ids(batch=None, ids="2,77", scenarios=ROWS)

    def test_pack_contains_flat_mp3_and_readme(self) -> None:
        out = self.tmp / "pack.zip"
        packed = pack.build_pack(
            ids=["2", "5"],
            output=out,
            scenarios=ROWS,
            titles={"2": "Two", "5": "Five"},
            src=self.src,
        )
        self.assertEqual(packed, ["2", "5"])
        with zipfile.ZipFile(out) as z:
            self.assertEqual(sorted(z.namelist()), ["2.mp3", "5.mp3", "README.txt"])
            readme = z.read("README.txt").decode("utf-8")
        self.assertIn("b900", readme)
        self.assertIn("temple_bell", readme)
        self.assertIn("pięć dzwonów", readme)
        self.assertEqual(zipfile.ZipFile(out).read("2.mp3"), b"ID3fake2")

    def test_missing_mp3_fails_unless_allowed(self) -> None:
        (self.src / "5.mp3").unlink()
        with self.assertRaises(SystemExit):
            pack.build_pack(ids=["2", "5"], output=self.tmp / "a.zip", scenarios=ROWS, titles={}, src=self.src)
        packed = pack.build_pack(
            ids=["2", "5"], output=self.tmp / "b.zip", scenarios=ROWS, titles={}, src=self.src, allow_missing=True
        )
        self.assertEqual(packed, ["2"])

    def test_readme_handles_missing_duration(self) -> None:
        text = pack.readme_text(["2"], batch="b900", rows={"2": {"sample_scenario": "x"}}, titles={"2": "Two"})
        self.assertIn("Two", text)
        self.assertIn("x", text)


if __name__ == "__main__":
    unittest.main()
