import importlib.util
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


if __name__ == '__main__':
    unittest.main()
