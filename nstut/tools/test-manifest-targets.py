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
            'nstut-0.13.17.5:nstut/modpack-manager.patch.json']))
        candidate = m.build_manifest()
        # A new base and new mod binaries must retain authentication, capacity,
        # upload, collapse and other semantic policies on their original sides.
        semantic = lambda manifest: [op for op in manifest['operations']
                                     if op['type'].startswith('patch')]
        # A DH v5 semantic policy is deliberately new in this release. Preserve
        # every pre-existing managed setting and allow exactly that one addition.
        prior_patches = semantic(previous)
        current_patches = semantic(candidate)
        dh_patches = [op for op in current_patches
                      if op.get('destination') == 'config/DistantHorizons.toml']
        self.assertEqual(len(dh_patches), 1)
        self.assertEqual(dh_patches[0]['type'], 'patchToml')
        self.assertEqual(dh_patches[0]['targets'], ['client', 'server'])
        self.assertEqual(dh_patches[0]['values']['_version'], 5)
        self.assertEqual(
            [op for op in current_patches if op.get('destination') != 'config/DistantHorizons.toml'],
            prior_patches,
        )
        managed = json.loads((m.ROOT / 'nstut/managed-mods.json').read_text(encoding='utf-8'))
        ids = {mod['id'] for mod in managed['mods']}
        installs = lambda manifest: {op['artifact']: op['targets']
                                     for op in manifest['operations']
                                     if op['type'] == 'installFile' and op['artifact'] in ids}
        previous_installs = installs(previous)
        candidate_installs = installs(candidate)
        # Existing mod-side policy stays immutable. Additional Placements
        # and the DH Chunky compatibility fork replace upstream binaries
        # on both client and server; only DH's new v5 policy is added.
        self.assertEqual(
            {mod_id: candidate_installs[mod_id] for mod_id in previous_installs},
            previous_installs,
        )
        self.assertEqual(set(candidate_installs) - set(previous_installs),
                         {"additional-placements", "distant-horizons"})
        self.assertEqual(candidate_installs["additional-placements"], ["client", "server"])
        self.assertEqual(candidate_installs["distant-horizons"], ["client", "server"])

    def test_distant_horizons_replaces_upstream_client_and_server_jar(self):
        manifest = m.build_manifest()
        artifacts = [a for a in manifest['artifacts'] if a['id'] == 'distant-horizons']
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(
            artifacts[0]['sha256'],
            'dd42f36b06af4c8c554deec6aba591705154080530c938c072703cf7d41825cd')
        self.assertTrue(artifacts[0]['url'].startswith(
            'https://github.com/UpperMoon0/DistantHorizons/releases/download/v3.3.3-nstut.9/'))
        operations = [op for op in manifest['operations']
                      if op.get('artifact') == 'distant-horizons'
                      or op.get('pattern') in ('mods/DistantHorizons-*.jar',
                                              'mods/distanthorizons-*.jar')]
        self.assertEqual(len(operations), 3)
        self.assertEqual(
            {op['pattern'] for op in operations if op['type'] == 'removeMatching'},
            {'mods/DistantHorizons-*.jar', 'mods/distanthorizons-*.jar'})
        self.assertTrue(all(op['targets'] == ['client', 'server'] for op in operations))
        install = [op for op in operations if op['type'] == 'installFile']
        self.assertEqual(len(install), 1)
        self.assertEqual(install[0]['destination'],
                         'mods/DistantHorizons-forge-3.3.3-nstut.9-1.20.1.jar')


if __name__ == '__main__':
    unittest.main()
