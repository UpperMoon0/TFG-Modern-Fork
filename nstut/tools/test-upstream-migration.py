import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('migration', Path(__file__).with_name('validate-upstream-migration.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MigrationRegressionTests(unittest.TestCase):
    def setUp(self):
        self.args = [m.load('pakku-lock.json'), m.load('nstut/managed-mods.json'), m.load('kubejs/assets/tfg/lang/en_us.json'),
                     m.historical(m.BASE, 'pakku-lock.json'), m.historical(m.PREVIOUS, 'nstut/managed-mods.json'),
                     m.historical(m.PREVIOUS, 'kubejs/assets/tfg/lang/en_us.json'), m.historical('0.13.10', 'kubejs/assets/tfg/lang/en_us.json')]

    def rejected(self):
        with self.assertRaises(AssertionError):
            m.validate(*self.args)

    def test_reviewed_migration(self):
        m.validate(*self.args)

    def test_upstream_hash_drift(self):
        self.args[0]['projects'][0]['files'][0]['hashes']['sha1'] = '0' * 40
        self.rejected()

    def test_upstream_mod_removed(self):
        del self.args[0]['projects'][0]
        self.rejected()

    def test_duplicate_mod(self):
        self.args[0]['projects'].append(copy.deepcopy(self.args[0]['projects'][0]))
        self.rejected()

    def test_missing_packetweave(self):
        self.args[0]['projects'] = [p for p in self.args[0]['projects'] if p['slug'].get('github') != 'UpperMoon0/PacketWeave']
        self.rejected()

    def test_custom_pin_changed(self):
        self.args[1]['mods'][0]['version'] = '0.0.1'
        self.rejected()

    def test_trueuuid_fork_pin_changed(self):
        mod = next(m for m in self.args[1]['mods'] if m['id'] == 'trueuuid')
        mod['repository'] = 'YuWan-030/TrueUUID'
        self.rejected()

    def test_base_downloads_exclude_managed_mods(self):
        m.validate_base_downloads(m.load('nstut/base-migration.json'), m.load('nstut/managed-mods.json'))

    def test_base_cannot_reinstall_old_packetweave(self):
        migration = m.load('nstut/base-migration.json')
        migration['targets']['server']['downloads'].append({'path': 'mods/packetweave-forge-1.20.1-0.1.2.jar'})
        with self.assertRaises(AssertionError):
            m.validate_base_downloads(migration, m.load('nstut/managed-mods.json'))

    def test_old_upstream_translations_restored(self):
        self.args[2].update(self.args[6])
        self.rejected()

    def test_custom_translation_removed(self):
        del self.args[2][next(iter(self.args[2]))]
        self.rejected()

    def base_args(self):
        return [m.load('nstut/base-installation.json'), m.load('nstut/release.json'), m.load('nstut/modpack-manager.patch.json'),
                [m.load(f'.pakku/{side}-overrides/.nstut-tfg-base-{m.BASE}') for side in ('client', 'server')]]

    def test_base_marker_contract(self):
        m.validate_base_installation(*self.base_args())

    def test_overlay_missing_base_guard(self):
        args = self.base_args()
        args[2]['requiredPaths'].remove(args[0]['requiredMarker'])
        with self.assertRaises(AssertionError):
            m.validate_base_installation(*args)

    def test_pack_marker_wrong_base(self):
        args = self.base_args()
        args[3][0]['baseRef'] = '0.13.10'
        with self.assertRaises(AssertionError):
            m.validate_base_installation(*args)

    def test_missing_client_marker(self):
        args = self.base_args()
        args[3].pop(0)
        with self.assertRaises(AssertionError):
            m.validate_base_installation(*args)


if __name__ == '__main__':
    unittest.main()
