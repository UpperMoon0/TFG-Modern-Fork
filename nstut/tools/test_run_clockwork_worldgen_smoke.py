#!/usr/bin/env python3
"""Side-effect safety and predictable parsing tests for isolated Forge smoke."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

runner_path = Path(__file__).with_name("run-clockwork-worldgen-smoke.py")
spec = importlib.util.spec_from_file_location("clockwork_ci_smoke", runner_path)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class SmokeRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="clockwork-ci-test-")
        self.addCleanup(self.temp.cleanup)
        self.server = Path(self.temp.name) / "server"
        self.server.mkdir()
        (self.server / "mods").mkdir()
        (self.server / "kubejs").mkdir()
        (self.server / "eula.txt").write_text("eula=true\n")
        (self.server / runner.DISPOSABLE_MARKER).touch()

    def test_only_disposable_packs(self):
        self.assertEqual(runner.safely_disposable(self.server), self.server)
        (self.server / runner.DISPOSABLE_MARKER).unlink()
        with self.assertRaises(ValueError):
            runner.safely_disposable(self.server)

    def test_must_not_overwrite_a_world(self):
        (self.server / runner.WORLD).mkdir()
        with self.assertRaises(ValueError):
            runner.safely_disposable(self.server)

    def test_missing_eula_is_rejected(self):
        (self.server / "eula.txt").write_text("eula=false\n")
        with self.assertRaises(ValueError):
            runner.safely_disposable(self.server)

    def test_properties_no_production_port_or_rcon(self):
        runner.set_properties(self.server, 1234)
        value = (self.server / "server.properties").read_text()
        self.assertIn("level-seed=1234", value)
        self.assertIn("server-ip=127.0.0.1", value)
        self.assertIn("server-port=0", value)
        self.assertIn("enable-rcon=false", value)
        self.assertIn("online-mode=false", value)
        self.assertNotIn("server-port=25565", value)

    def test_done_marker_not_false_positive(self):
        self.assertTrue(runner.DONE.search("[INFO]: Done (28.4s)! For help, type 'help'"))
        self.assertFalse(runner.DONE.search("World generation started"))

    def test_non_recursive_world_reuse_prevention(self):
        # A marker on a parent does not authorize use of an unmarked child.
        other = self.server / "other"
        other.mkdir()
        with self.assertRaises(ValueError):
            runner.safely_disposable(other)


if __name__ == "__main__":
    unittest.main()
