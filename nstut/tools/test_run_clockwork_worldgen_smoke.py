#!/usr/bin/env python3
"""Side-effect safety and predictable parsing tests for isolated Forge smoke."""
import importlib.util
import json
import subprocess
import sys
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

    def test_kubejs_success_summary_is_not_a_registry_error(self):
        # The real Forge startup prints "0 errors", which used to trip
        # a broad /KubeJS.+ERROR/i match and abort successful launches.
        successful = (
            "[18:36:09] [modloading-worker-0/INFO] [KubeJS Startup/]: "
            "Loaded 131/131 KubeJS startup scripts in 4.053 s with "
            "0 errors and 0 warnings"
        )
        self.assertIsNone(runner.ERRORS.search(successful))
        self.assertIsNotNone(runner.ERRORS.search(
            "[18:37:02] [Server thread/ERROR] [KubeJS Server/]: "
            "Failed to register Wanderlite recipe"
        ))
        self.assertIsNotNone(runner.ERRORS.search(
            "[18:37:02] [KubeJS Server/ERROR]: Invalid recipe"
        ))

    def test_real_recipe_failures_are_fatal_but_baseline_noise_is_not(self):
        failures = [
            "[18:45:43] [KubeJS Server/WARN]: Error parsing recipe "
            "tfg:clockwork/steam/wanderlite_trace_recovery[greate:mixing]",
            "[18:45:48] [GregTechCEu/WARN]: failed to add recipe from "
            "staging into lookup DB: tfg:assembler/clockwork/mv/physics_bearing",
            "[18:45:55] [KubeJS Server/INFO]: Added 35000 recipes, "
            "removed 14000 recipes, modified 1000 recipes, with 1 failed recipes",
        ]
        for line in failures:
            with self.subTest(line=line):
                self.assertIsNotNone(runner.ERRORS.search(line))
        self.assertIsNone(runner.ERRORS.search(
            "[18:45:16] [KubeJS Server/WARN]: Failed to parse recipe "
            "'vs_clockwork:extruder/wanderlite_matrix'! Falling back to vanilla"
        ))

    def test_real_ore_in_one_full_chunk_is_sufficient_positive_proof(self):
        result = runner.assess_worldgen({
            "fully_generated_chunks": 1,
            "ore_bearing_chunks": 1,
            "blocks_found": 67,
            "ore_y_histogram": {"-50": 2, "-47": 65},
        }, 64)
        self.assertTrue(result["passed"])
        self.assertEqual(result["positive_min_fully_generated_chunks"], 1)
        self.assertEqual(result["negative_min_fully_generated_chunks"], 64)

    def test_missing_ore_cannot_be_claimed_from_one_chunk(self):
        result = runner.assess_worldgen({
            "fully_generated_chunks": 1,
            "ore_bearing_chunks": 0,
            "blocks_found": 0,
            "ore_y_histogram": {},
        }, 64)
        self.assertFalse(result["passed"])
        invalid_depth = runner.assess_worldgen({
            "fully_generated_chunks": 1,
            "ore_bearing_chunks": 1,
            "blocks_found": 1,
            "ore_y_histogram": {"70": 1},
        }, 64)
        self.assertFalse(invalid_depth["passed"])
        self.assertFalse(invalid_depth["depth_ok"])

    def test_done_marker_not_false_positive(self):
        self.assertTrue(runner.DONE.search("[INFO]: Done (28.4s)! For help, type 'help'"))
        self.assertFalse(runner.DONE.search("World generation started"))

    def test_non_recursive_world_reuse_prevention(self):
        # A marker on a parent does not authorize use of an unmarked child.
        other = self.server / "other"
        other.mkdir()
        with self.assertRaises(ValueError):
            runner.safely_disposable(other)


    def test_full_mock_smoke_path_uses_one_spawn_world_and_writes_evidence(self):
        """Exercise the runner end-to-end with synthetic Anvil chunks, NOT Forge."""
        spec = importlib.util.spec_from_file_location(
            "clockwork_anvil_fixture", runner_path.with_name("test_scan_clockwork_worldgen.py")
        )
        fixtures = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixtures)

        candidate = Path(self.temp.name) / "candidate"
        source = candidate / runner.FEATURE
        source.parent.mkdir(parents=True)
        source.write_text(json.dumps({
            "type": "tfc:disc_vein",
            "config": {
                "rarity": 420, "min_y": -60, "max_y": -24,
                "blocks": [
                    {"replace": [f"tfc:rock/raw/{rock}"],
                     "with": [{"block": "vs_clockwork:wanderlite_deepslate_ore", "weight": 1}]}
                    for rock in ("gabbro", "granite", "gneiss", "slate", "marble")
                ],
            },
        }))
        installed = self.server / runner.FEATURE
        installed.parent.mkdir(parents=True)
        installed.write_bytes(source.read_bytes())
        # 64 chunks, one actual ore. These are synthetic test fixtures only.
        fixtures.region_file(self.server / "fixture.mca", {
            slot: fixtures.make_chunk(slot % 32, slot // 32, {0: 1} if slot == 0 else {})
            for slot in range(64)
        })
        fake = self.server / "fake_forge.py"
        fake.write_text(
            "import shutil, sys\n"
            "from pathlib import Path\n"
            "home = Path.cwd()\n"
            "region = home / 'clockwork-smoke' / 'region'\n"
            "region.mkdir(parents=True)\n"
            "shutil.copyfile(home / 'fixture.mca', region / 'r.0.0.mca')\n"
            "print('Done (0.1s)!', flush=True)\n"
            "for command in sys.stdin:\n"
            "    if command.strip() == 'stop': break\n"
        )
        evidence = Path(self.temp.name) / "evidence"
        proc = subprocess.run(
            [
                sys.executable, str(runner_path),
                "--repo-root", str(candidate),
                "--server-dir", str(self.server),
                "--launch", f"{sys.executable} fake_forge.py",
                "--evidence-dir", str(evidence),
                "--timeout", "15",
                "--min-chunks", "64",
            ], text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        summary = json.loads((evidence / "summary.json").read_text())
        self.assertTrue(summary["passed"])
        self.assertEqual(summary["attempts"], 1)
        self.assertEqual(summary["results"][0]["fully_generated_chunks"], 64)
        self.assertEqual(summary["results"][0]["blocks_found"], 1)
        self.assertTrue(summary["results"][0]["depth_ok"])
        self.assertIn("Done (0.1s)!", (evidence / f"forge-seed-{runner.SEEDS[0]}.log").read_text())
        # Original candidate is untouched, while only the isolated server is
        # allowed to contain the test-only rarity override.
        self.assertEqual(json.loads(source.read_text())["config"]["rarity"], 420)
        self.assertEqual(json.loads(installed.read_text())["config"]["rarity"], 1)


if __name__ == "__main__":
    unittest.main()
