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

    def test_old_upstream_translations_restored(self):
        self.args[2].update(self.args[6])
        self.rejected()

    def test_custom_translation_removed(self):
        del self.args[2][next(iter(self.args[2]))]
        self.rejected()


if __name__ == '__main__':
    unittest.main()
