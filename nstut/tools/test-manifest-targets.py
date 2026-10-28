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

    def test_runtime_policies_preserved_from_previous_release(self):
        previous = json.loads(subprocess.check_output([
            'git', '-C', str(m.ROOT), 'show',
            'nstut-0.13.15.8:nstut/modpack-manager.patch.json']))
        candidate = m.build_manifest()
        # A new base and new mod binaries must retain authentication, capacity,
        # upload, collapse and other semantic policies on their original sides.
        semantic = lambda manifest: [op for op in manifest['operations']
                                     if op['type'].startswith('patch')]
        self.assertEqual(semantic(candidate), semantic(previous))
        managed = json.loads((m.ROOT / 'nstut/managed-mods.json').read_text(encoding='utf-8'))
        ids = {mod['id'] for mod in managed['mods']}
        installs = lambda manifest: {op['artifact']: op['targets']
                                     for op in manifest['operations']
                                     if op['type'] == 'installFile' and op['artifact'] in ids}
        self.assertEqual(installs(candidate), installs(previous))


if __name__ == '__main__':
    unittest.main()
