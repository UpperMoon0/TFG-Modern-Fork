#!/usr/bin/env python3
"""Audit removed IDs; remap only legacy Create waterproof-cardboard filters.

Never remap placed blocks or inventories into unrelated content. Unknown removed
ID references abort before writing. Run only against a stopped world or snapshot.
"""
import argparse
from dataclasses import dataclass
import gzip
import hashlib
import json
from pathlib import Path
import struct
import zlib

REMOVED = ('ae2:auto_complete_card', 'ae2:colorizer', 'ae2:pattern_box',
           'ae2:singularity_crafting_storage', 'fluidlogistics:waterproof_cardboard_block')
OLD = REMOVED[-1]
NEW = 'tfc:empty_jar'
NEEDLES = {name: struct.pack('>H', len(name)) + name.encode() for name in REMOVED}


@dataclass
class String:
    value: str
    start: int
    end: int


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, size):
        assert 0 <= size <= len(self.data) - self.pos, 'truncated NBT'
        result = self.data[self.pos:self.pos + size]
        self.pos += size
        return result

    def number(self, fmt):
        return struct.unpack(fmt, self.take(struct.calcsize(fmt)))[0]

    def string(self):
        start = self.pos
        size = self.number('>H')
        return String(self.take(size).decode('utf-8', errors='replace'), start, self.pos)

    def value(self, kind):
        if kind in (1, 2, 3, 4, 5, 6):
            return self.number({1: '>b', 2: '>h', 3: '>i', 4: '>q', 5: '>f', 6: '>d'}[kind])
        if kind in (7, 11, 12):
            size = self.number('>i')
            assert size >= 0
            self.take(size * {7: 1, 11: 4, 12: 8}[kind])
            return None
        if kind == 8:
            return self.string()
        if kind == 9:
            child, count = self.number('>B'), self.number('>i')
            assert count >= 0
            return [self.value(child) for _ in range(count)]
        if kind == 10:
            result = {}
            while True:
                child = self.number('>B')
                if child == 0:
                    return result
                name = self.string().value
                result[name] = self.value(child)
        raise ValueError('unsupported NBT tag ' + str(kind))


def remap(data):
    present = {name: data.count(needle) for name, needle in NEEDLES.items() if needle in data}
    if not present:
        return data, 0, {}
    reader = Reader(data)
    assert reader.number('>B') == 10
    reader.string()
    root = reader.value(10)
    replacements = []
    for entity in root.get('block_entities', []):
        entity_id = entity.get('id')
        if not isinstance(entity_id, String) or entity_id.value != 'create:factory_panel':
            continue
        for side in ('top_left', 'top_right', 'bottom_left', 'bottom_right'):
            value = entity.get(side, {}).get('Filter', {}).get('id')
            if isinstance(value, String) and value.value == OLD:
                replacements.append(value)
    unknown = dict(present)
    unknown[OLD] = unknown.get(OLD, 0) - len(replacements)
    unknown = {key: value for key, value in unknown.items() if value}
    if unknown:
        return data, 0, unknown
    for value in sorted(replacements, key=lambda v: v.start, reverse=True):
        data = data[:value.start] + struct.pack('>H', len(NEW)) + NEW.encode() + data[value.end:]
    return data, len(replacements), {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('world', type=Path)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    world = args.world.resolve()
    assert world.is_dir() and (world / 'level.dat').is_file(), 'invalid world root'
    changes, unknown = [], []
    chunks = 0
    for path in sorted(world.rglob('*.mca')):
        assert path.resolve().is_relative_to(world), 'world symlink escapes root'
        raw = path.read_bytes()
        if not raw:
            continue
        assert len(raw) >= 8192, path
        modified = bytearray(raw)
        file_changed = False
        for index in range(1024):
            entry = int.from_bytes(raw[index * 4:index * 4 + 4], 'big')
            offset, sectors = entry >> 8, entry & 255
            if not offset:
                continue
            assert offset >= 2 and sectors
            begin = offset * 4096
            length = struct.unpack('>I', raw[begin:begin + 4])[0]
            kind = raw[begin + 4]
            external = None
            if kind & 128:
                rx, rz = map(int, path.stem.split('.')[1:])
                external = path.parent / f'c.{rx * 32 + index % 32}.{rz * 32 + index // 32}.mcc'
                payload = external.read_bytes()
                kind &= 127
            else:
                assert 1 < length <= sectors * 4096 - 4
                payload = raw[begin + 5:begin + 4 + length]
            data = gzip.decompress(payload) if kind == 1 else zlib.decompress(payload) if kind == 2 else payload if kind == 3 else None
            assert data is not None, 'unsupported region compression'
            updated, count, unmatched = remap(data)
            chunks += 1
            if unmatched:
                unknown.append({'file': str(path.relative_to(world)), 'chunkIndex': index, 'ids': unmatched})
            if not count:
                continue
            compressed = gzip.compress(updated, mtime=0) if kind == 1 else zlib.compress(updated) if kind == 2 else updated
            if external:
                changes.append((external, external.read_bytes(), compressed, count))
            else:
                record = struct.pack('>I', len(compressed) + 1) + bytes([kind]) + compressed
                assert len(record) <= sectors * 4096, 'remapped chunk no longer fits its allocated sectors'
                modified[begin:begin + sectors * 4096] = record + b'\0' * (sectors * 4096 - len(record))
                file_changed = True
        if file_changed:
            changes.append((path, raw, bytes(modified), 1))
    for path in sorted(world.rglob('*.dat')):
        if path.name in ('level.dat', 'level.dat_old'):
            continue  # Forge's global registry snapshot does not prove live usage.
        assert path.resolve().is_relative_to(world)
        raw = path.read_bytes()
        data = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
        hits = {name: data.count(needle) for name, needle in NEEDLES.items() if needle in data}
        if hits:
            unknown.append({'file': str(path.relative_to(world)), 'ids': hits})
    report = {'chunksScanned': chunks, 'changedFiles': [str(p.relative_to(world)) for p, _, _, _ in changes], 'unmappedReferences': unknown,
              'scope': 'Serialized region/entity/POI chunks and standalone data; nested custom compressed storage is not decoded.'}
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    if unknown:
        raise SystemExit('Unmapped removed-ID references found; world was not changed. See ' + str(args.report))
    if args.apply:
        for path, before, after, _ in changes:
            assert path.read_bytes() == before, 'world changed during audit'
        for path, before, after, _ in changes:
            backup = path.with_name(path.name + '.pre-0.13.12')
            if not backup.exists():
                backup.write_bytes(before)
            elif hashlib.sha256(backup.read_bytes()).digest() != hashlib.sha256(before).digest():
                raise RuntimeError('Conflicting existing world-remap backup')
            path.write_bytes(after)
    print(json.dumps(report))


if __name__ == '__main__':
    main()
