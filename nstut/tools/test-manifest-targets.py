import importlib.util
import json
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('manifest', Path(__file__).with_name('generate-modpack-manager-manifest.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ManifestTargets(unittest.TestCase):
    def test_server_override_excludes_root_file_from_server(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            override = root / '.pakku/server-overrides/defaultconfigs/tfc-server.toml'
            override.parent.mkdir(parents=True)
            override.write_text('server defaults')
            with patch.object(m, 'ROOT', root):
                self.assertEqual(m.deployment_path('defaultconfigs/tfc-server.toml'),
                                 ('defaultconfigs/tfc-server.toml', ['client']))
                self.assertEqual(m.deployment_path('.pakku/server-overrides/defaultconfigs/tfc-server.toml'),
                                 ('defaultconfigs/tfc-server.toml', ['server']))

    def test_conflicting_destination_rejected_but_separate_targets_allowed(self):
        manifest = {'artifacts': [{'id': 'a', 'sha256': 'a' * 64}, {'id': 'b', 'sha256': 'b' * 64}],
                    'operations': [{'type': 'installFile', 'artifact': 'a', 'destination': 'config/example.toml', 'targets': ['server']},
                                   {'type': 'installFile', 'artifact': 'b', 'destination': 'config/example.toml', 'targets': ['server']}]}
        with self.assertRaises(ValueError):
            m.validate_install_destinations(manifest)
        manifest['operations'][1]['targets'] = ['client']
        m.validate_install_destinations(manifest)


class VanishGuardTargets(unittest.TestCase):
    def test_vanishguard_only_installs_and_cleans_server(self):
        manifest = m.build_manifest()
        operations = [op for op in manifest['operations']
                      if op.get('artifact') == 'vanishguard' or 'vanishguard' in op.get('pattern', '')]
        self.assertEqual(len(operations), 2)
        self.assertTrue(all(op['targets'] == ['server'] for op in operations))
        self.assertEqual({op['type'] for op in operations}, {'installFile', 'removeMatching'})

    def test_private_config_has_no_pack_operation(self):
        manifest = m.build_manifest()
        self.assertFalse(any('vanishguard.json' in json.dumps(op) for op in manifest['operations']))
        self.assertFalse(any('vanishguard.json' in json.dumps(a) for a in manifest['artifacts']))

    def test_only_trueuuid_pin_changes_from_reviewed_construction(self):
        previous = json.loads(subprocess.check_output([
            'git', '-C', str(m.ROOT), 'show',
            'cb658e7b9871274242327a723d3ff5a2f3add913:nstut/modpack-manager.patch.json']))
        candidate = m.build_manifest()
        expected_ops = json.loads(json.dumps(previous['operations']))
        for op in expected_ops:
            if op.get('artifact') == 'trueuuid':
                self.assertEqual(op['destination'], 'mods/trueuuid-1.3.0-forge-1.20.1.jar')
                self.assertEqual(op['targets'], ['client', 'server'])
                op['destination'] = 'mods/trueuuid-1.3.1-forge-1.20.1.jar'
        # Includes every auth/config operation and every other mod on both sides.
        self.assertEqual(candidate['operations'], expected_ops)
        old = {a['id']: a for a in previous['artifacts']}
        new = {a['id']: a for a in candidate['artifacts']}
        self.assertEqual(set(old), set(new))
        for artifact, expected in old.items():
            if artifact == 'trueuuid':
                self.assertEqual(new[artifact], {
                    'id': 'trueuuid',
                    'fileName': 'trueuuid-1.3.1-forge-1.20.1.jar',
                    'url': 'https://github.com/UpperMoon0/TrueUUID/releases/download/v1.3.1/trueuuid-1.3.1-forge-1.20.1.jar',
                    'sha256': '1d40b23c9a87c4c374bc66d092ed781fd5a303638a83ac3aced6677690b3181f',
                })
                continue
            expected = dict(expected)
            expected['url'] = expected['url'].replace('/nstut-0.13.15.7/', '/nstut-0.13.15.8/')
            self.assertEqual(new[artifact], expected)


if __name__ == '__main__':
    unittest.main()
