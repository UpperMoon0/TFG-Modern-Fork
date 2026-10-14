import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

spec = importlib.util.spec_from_file_location('world_migration', Path(__file__).with_name('migrate-world-0.13.12.py'))
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def string(value):
    data = value.encode()
    return struct.pack('>H', len(data)) + data


def tag(name, value):
    return b'\x08' + string(name) + string(value)


def compound(name, body):
    return b'\x0a' + string(name) + body + b'\x00'


def factory_filter():
    entity = tag('id', 'create:factory_panel') + compound('top_right', compound('Filter', tag('id', m.OLD))) + b'\x00'
    return b'\x0a\x00\x00' + b'\x09' + string('block_entities') + b'\x0a' + struct.pack('>i', 1) + entity + b'\x00'


def region_record(data):
    compressed = zlib.compress(data)
    record = struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed
    return record + b'\x00' * (4096 - len(record))


class WorldMigrationTests(unittest.TestCase):
    def test_only_factory_filter_is_remapped(self):
        source = factory_filter()
        updated, count, unknown = m.remap(source)
        self.assertEqual((count, unknown), (1, {}))
        self.assertNotIn(m.NEEDLES[m.OLD], updated)
        self.assertIn(string(m.NEW), updated)
        self.assertEqual(m.remap(updated)[1:], (0, {}))

    def test_removed_block_or_inventory_reference_is_not_replaced(self):
        source = b'\x0a\x00\x00' + tag('Name', m.OLD) + b'\x00'
        updated, count, unknown = m.remap(source)
        self.assertEqual(updated, source)
        self.assertEqual(count, 0)
        self.assertEqual(unknown, {m.OLD: 1})

    def test_region_rewrite_preserves_other_chunks_and_backups(self):
        with tempfile.TemporaryDirectory() as directory:
            world = Path(directory)
            (world / 'level.dat').write_bytes(b'global registry snapshot')
            region = world / 'r.0.0.mca'
            header = bytearray(8192)
            header[:4] = struct.pack('>I', (2 << 8) | 1)
            header[4:8] = struct.pack('>I', (3 << 8) | 1)
            other = region_record(b'\x0a\x00\x00' + tag('Name', 'minecraft:stone') + b'\x00')
            original = bytes(header) + region_record(factory_filter()) + other
            region.write_bytes(original)
            report = world / 'report.json'
            command = [sys.executable, str(Path(m.__file__)), str(world), '--apply', '--report', str(report)]
            subprocess.run(command, check=True, capture_output=True)
            result = region.read_bytes()
            self.assertEqual(result[:8192], original[:8192])
            self.assertEqual(result[12288:], other)
            self.assertEqual(region.with_name(region.name + '.pre-0.13.12').read_bytes(), original)
            self.assertEqual(json.loads(report.read_text())['unmappedReferences'], [])
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(region.read_bytes(), result)


if __name__ == '__main__':
    unittest.main()
