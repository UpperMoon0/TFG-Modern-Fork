import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('server_migration', Path(__file__).with_name('migrate-server.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SnapshotTests(unittest.TestCase):
    def test_protected_inventory_includes_world_identity_and_media(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = ['world/region/r.0.0.mca', 'config/trueuuid-registry.json', 'media/upload.bin',
                     'server.properties', 'mods/example.jar', '.modpack-manager/state-server.json']
            for name in paths:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'original')
            original = m.protected_inventory(root)
            self.assertEqual(set(original), set(paths[:4]))
            (root / paths[0]).write_bytes(b'changed')
            self.assertNotEqual(m.protected_inventory(root), original)

    def test_rollback_preserves_backup_folders_and_nested_world_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'server'
            root.mkdir()
            for p, data in [('world/backups/private.dat', b'nested world data'), ('config/private.json', b'original config'), ('backups/old.zip', b'existing backup')]:
                f = root / p
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes(data)
            backup = root / '.modpack-manager/migration-backups/test'
            backup.parent.mkdir(parents=True)
            m.snapshot(root.resolve(), backup)
            self.assertEqual((backup / 'world/backups/private.dat').read_bytes(), b'nested world data')
            (root / 'config/private.json').write_bytes(b'changed config')
            (root / 'new-file').write_bytes(b'new migration file')
            m.restore_snapshot(root.resolve(), backup)
            self.assertEqual((root / 'config/private.json').read_bytes(), b'original config')
            self.assertEqual((root / 'backups/old.zip').read_bytes(), b'existing backup')
            self.assertEqual((root / 'world/backups/private.dat').read_bytes(), b'nested world data')
            self.assertFalse((root / 'new-file').exists())


if __name__ == '__main__':
    unittest.main()
