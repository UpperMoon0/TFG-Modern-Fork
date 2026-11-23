#!/usr/bin/env python3
"""Tests for the disposable, non-production Clockwork worldgen override."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("stage-clockwork-worldgen-smoke.py")
spec = importlib.util.spec_from_file_location("clockwork_stage", MODULE)
stage_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage_module)


class SmokeStageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="clockwork-stage-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        feature = self.repo / stage_module.FEATURE
        feature.parent.mkdir(parents=True)
        self.example = {
            "type": "tfc:disc_vein",
            "config": {
                "rarity": 420, "min_y": -60, "max_y": -24,
                "blocks": [{"replace": [f"tfc:rock/raw/{r}"],
                            "with": [{"block": "vs_clockwork:wanderlite_deepslate_ore", "weight": 1}]}
                           for r in ("gabbro", "gneiss", "schist", "slate", "granite")]
            }
        }
        feature.write_text(json.dumps(self.example), encoding="utf-8")

    def test_one_overlay_without_mutating_production(self):
        result = stage_module.stage(self.repo, self.base / "isolated-overlay")
        target = Path(result["override_feature"])
        overridden = json.loads(target.read_text())
        original = json.loads((self.repo / stage_module.FEATURE).read_text())
        self.assertEqual(overridden["config"]["rarity"], 1)
        self.assertEqual(original["config"]["rarity"], 420)
        self.assertEqual(overridden["config"]["blocks"], original["config"]["blocks"])
        self.assertTrue(result["source_unchanged"])

    def test_refuse_existing_directory(self):
        output = self.base / "existing"
        output.mkdir()
        with self.assertRaises(FileExistsError):
            stage_module.stage(self.repo, output)

    def test_refuse_rarity_drift(self):
        feature = self.repo / stage_module.FEATURE
        cfg = json.loads(feature.read_text())
        cfg["config"]["rarity"] = 1
        feature.write_text(json.dumps(cfg))
        with self.assertRaises(AssertionError):
            stage_module.stage(self.repo, self.base / "overlay")

    def test_refuse_non_temp_output(self):
        with self.assertRaises(ValueError):
            stage_module.stage(self.repo, Path("/var/lib/minecraft/worldgen-overlay"))


if __name__ == "__main__":
    unittest.main()
