#!/usr/bin/env python3
"""Independent synthetic Anvil fixtures for the Clockwork worldgen scanner."""
import importlib.util
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

SCANNER = Path(__file__).with_name("scan-clockwork-worldgen.py")
spec = importlib.util.spec_from_file_location("clockwork_worldgen_scan", SCANNER)
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


def tag(kind, name, payload):
    name = name.encode("utf-8")
    return bytes([kind]) + struct.pack(">H", len(name)) + name + payload


def string(value):
    b = value.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def compound(*fields):
    return b"".join(fields) + b"\0"


def make_chunk(cx, cz, indices, palette=None, status="minecraft:full"):
    palette = palette or ["minecraft:stone", scan.TARGET]
    arr = [0] * 256  # 4-bit index; 16 positions per long
    for slot, palette_index in indices.items():
        arr[slot // 16] |= palette_index << (slot % 16) * 4
    items = [tag(8, "Name", string(name)) for name in palette]
    pal = tag(9, "palette", bytes([10]) + struct.pack(">i", len(items)) +
              b"".join(compound(item) for item in items))
    data = tag(12, "data", struct.pack(">i", len(arr)) +
               b"".join(struct.pack(">Q", word) for word in arr))
    states = tag(10, "block_states", compound(pal, data))
    section = compound(tag(1, "Y", struct.pack(">b", -3)), states)
    sections = tag(9, "sections", bytes([10]) + struct.pack(">i", 1) + section)
    root = compound(tag(3, "xPos", struct.pack(">i", cx)),
                    tag(3, "zPos", struct.pack(">i", cz)),
                    tag(8, "Status", string(status)),
                    sections)
    return bytes([10]) + string("") + root


def region_file(path, chunks):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = bytearray(8192)
    sectors = []
    next_sector = 2
    for slot, raw in chunks.items():
        compressed = zlib.compress(raw)
        data = struct.pack(">IB", len(compressed) + 1, 2) + compressed
        blocks = (len(data) + 4095) // 4096
        header[slot * 4:slot * 4 + 3] = next_sector.to_bytes(3, "big")
        header[slot * 4 + 3] = blocks
        sectors.extend([data.ljust(blocks * 4096, b"\0")])
        next_sector += blocks
    path.write_bytes(header + b"".join(sectors))


class WorldgenScanTests(unittest.TestCase):
    def test_real_ore_blocks_and_unused_palette_entry(self):
        # Chunk 0: exactly three actual ore blocks, at Y -48.
        # Chunk 1: target is in palette, but no blocks use that palette index.
        one = make_chunk(0, 0, {0: 1, 1: 1, 255: 1})
        two = make_chunk(1, 0, {})
        with tempfile.TemporaryDirectory() as base:
            directory = Path(base)
            region_file(directory / "r.0.0.mca", {0: one, 1: two})
            result = scan.scan(directory, scan.TARGET)
        self.assertEqual(result["chunks_scanned"], 2)
        self.assertEqual(result["blocks_found"], 3)
        self.assertEqual(result["ore_bearing_chunks"], 1)
        self.assertEqual(result["ore_y_histogram"], {-48: 3})
        self.assertEqual(
            [(x["x"], x["y"], x["z"]) for x in result["sample_positions"]],
            [(0, -48, 0), (1, -48, 0), (15, -48, 15)]
        )

    def test_unfinished_chunks_cannot_claim_success(self):
        finished = make_chunk(0, 0, {0: 1})
        unfinished = make_chunk(1, 0, {0: 1, 1: 1},
                                status="minecraft:features")
        with tempfile.TemporaryDirectory() as base:
            directory = Path(base)
            region_file(directory / "r.0.0.mca", {0: finished, 1: unfinished})
            result = scan.scan(directory, scan.TARGET)
        self.assertEqual(result["chunks_scanned"], 2)
        self.assertEqual(result["fully_generated_chunks"], 1)
        self.assertEqual(result["blocks_found"], 1)

    def test_negative_chunk_coordinates(self):
        one = make_chunk(-32, -32, {0: 1})
        with tempfile.TemporaryDirectory() as base:
            directory = Path(base)
            region_file(directory / "r.-1.-1.mca", {0: one})
            result = scan.scan(directory, scan.TARGET)
        self.assertEqual(result["sample_positions"], [{"x": -512, "y": -48, "z": -512}])

    def test_only_singles_are_counted_when_no_palette_data(self):
        chunk = {"xPos": 2, "zPos": 3, "sections": [
            {"Y": -2, "block_states": {"palette": [{"Name": scan.TARGET}]}}
        ]}
        self.assertEqual(len(list(scan.chunk_positions(chunk))), 4096)

    def test_invalid_chunk_location_fails(self):
        with tempfile.TemporaryDirectory() as base:
            directory = Path(base)
            region_file(directory / "r.0.0.mca", {0: make_chunk(9, 0, {0: 1})})
            with self.assertRaises(scan.CorruptWorld):
                scan.scan(directory, scan.TARGET)


if __name__ == "__main__":
    unittest.main()
