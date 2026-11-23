#!/usr/bin/env python3
"""Inspect actual generated Minecraft 1.20.1 Anvil chunks for Clockwork Wanderlite.

Offline and read-only; use on the *stopped* disposable Forge server world only.
This proves that the world contains blocks, not merely that a feature/tag exists.

Example:
  python3 nstut/tools/scan-clockwork-worldgen.py \
    /tmp/tfg-worldgen-ci/world/region \
    --min-chunks 64 --min-blocks 1 --report /tmp/wanderlite-evidence.json

The region path must belong to a newly generated Overworld for the tested seed.
Supports modern sections.block_states.palette/data and signed packed longs.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path
from typing import Any

TARGET = "vs_clockwork:wanderlite_deepslate_ore"
S64 = (1 << 64) - 1
REGION_NAME = re.compile(r"^r\.(-?\d+)\.(-?\d+)\.mca$")


class CorruptWorld(ValueError):
    """A chunk is corrupted or uses an unsupported format."""


class NBT:
    def __init__(self, data: bytes):
        self.buf = memoryview(data)
        self.at = 0

    def take(self, size: int) -> memoryview:
        if size < 0 or size > len(self.buf) - self.at:
            raise CorruptWorld("truncated or invalid NBT length")
        out = self.buf[self.at:self.at + size]
        self.at += size
        return out

    def number(self, fmt: str) -> int | float:
        return struct.unpack(fmt, self.take(struct.calcsize(fmt)))[0]

    def string(self) -> str:
        length = self.number(">H")
        return bytes(self.take(length)).decode("utf-8")

    def payload(self, kind: int) -> Any:
        if kind == 1:
            return self.number(">b")
        if kind == 2:
            return self.number(">h")
        if kind == 3:
            return self.number(">i")
        if kind == 4:
            return self.number(">q")
        if kind == 5:
            return self.number(">f")
        if kind == 6:
            return self.number(">d")
        if kind == 7:
            size = self.number(">i")
            self.take(size)
            return None
        if kind == 8:
            return self.string()
        if kind == 9:
            sub_kind = self.number(">B")
            count = self.number(">i")
            if not 0 <= count <= 1000000:
                raise CorruptWorld("invalid NBT list size")
            return [self.payload(sub_kind) for _ in range(count)]
        if kind == 10:
            obj = {}
            while True:
                sub_kind = self.number(">B")
                if sub_kind == 0:
                    break
                name = self.string()
                obj[name] = self.payload(sub_kind)
            return obj
        if kind == 11:
            length = self.number(">i")
            self.take(length * 4)
            return None
        if kind == 12:
            length = self.number(">i")
            if not 0 <= length <= 1000000:
                raise CorruptWorld("invalid NBT long array size")
            # Build only packed bitplanes. Other arrays (heightmaps) are small.
            return list(struct.unpack(f">{length}Q", self.take(length * 8)))
        raise CorruptWorld(f"unsupported NBT tag kind: {kind}")

    def root(self) -> dict:
        if self.number(">B") != 10:
            raise CorruptWorld("root NBT is not a compound")
        self.string()  # root name, usually ""
        root = self.payload(10)
        if not isinstance(root, dict):
            raise CorruptWorld("invalid root compound")
        return root


def chunk_positions(chunk: dict, target: str = TARGET):
    """Yield actual block positions of target. A palette hit alone is NOT enough."""
    body = chunk.get("Level", chunk)
    if not isinstance(body, dict):
        raise CorruptWorld("invalid chunk body")
    cx, cz = body.get("xPos"), body.get("zPos")
    if not isinstance(cx, int) or not isinstance(cz, int):
        raise CorruptWorld("chunk missing xPos/zPos")
    for section in body.get("sections", body.get("Sections", [])):
        if not isinstance(section, dict):
            continue
        y = section.get("Y")
        if not isinstance(y, int):
            continue
        states = section.get("block_states", {})
        if not states and "Palette" in section:  # older Anvil format
            states = {"palette": section["Palette"], "data": section.get("BlockStates")}
        if not isinstance(states, dict):
            continue
        palette = states.get("palette", [])
        if not isinstance(palette, list) or not palette:
            continue
        hits = {idx for idx, entry in enumerate(palette)
                if isinstance(entry, dict) and entry.get("Name") == target}
        if not hits:
            continue
        data = states.get("data")
        if data is None:
            if len(palette) != 1:
                raise CorruptWorld("multi-state palette missing packed data")
            if 0 not in hits:
                continue
            ids = (0 for _ in range(4096))
        else:
            if not isinstance(data, list):
                raise CorruptWorld("invalid packed block state array")
            bits = max(4, (len(palette) - 1).bit_length())
            per_long = 64 // bits
            needed = (4096 + per_long - 1) // per_long
            if len(data) < needed:
                raise CorruptWorld("packed block states shorter than required")
            mask = (1 << bits) - 1
            ids = ((data[i // per_long] >> ((i % per_long) * bits)) & mask
                   for i in range(4096))
        for i, idx in enumerate(ids):
            if idx in hits:
                x = (cx << 4) + (i & 15)
                z = (cz << 4) + ((i >> 4) & 15)
                yy = (y << 4) + (i >> 8)
                yield (x, yy, z)


def read_region(region: Path):
    name = REGION_NAME.match(region.name)
    if not name:
        raise CorruptWorld(f"invalid region name: {region.name}")
    rx, rz = map(int, name.groups())
    with region.open("rb") as handle:
        header = handle.read(8192)
        if len(header) < 8192:
            raise CorruptWorld(f"truncated region header: {region}")
        for slot in range(1024):
            n = struct.unpack(">I", b"\0" + header[slot * 4:slot * 4 + 3])[0]
            sectors = header[slot * 4 + 3]
            if n == 0:
                continue
            if sectors == 0:
                raise CorruptWorld(f"{region}:{slot} has zero sector count")
            handle.seek(n * 4096)
            block = handle.read(5)
            if len(block) < 5:
                raise CorruptWorld(f"{region}:{slot} truncated compressed chunk")
            length, compression = struct.unpack(">IB", block)
            if length < 1 or length > sectors * 4096 - 4:
                raise CorruptWorld(f"{region}:{slot} invalid chunk length")
            compressed = handle.read(length - 1)
            if len(compressed) != length - 1:
                raise CorruptWorld(f"{region}:{slot} truncated chunk payload")
            if compression == 1:
                raw = gzip.decompress(compressed)
            elif compression == 2:
                raw = zlib.decompress(compressed)
            elif compression == 3:
                raw = compressed
            else:
                raise CorruptWorld(f"{region}:{slot} unsupported compression {compression}")
            chunk = NBT(raw).root()
            body = chunk.get("Level", chunk)
            expected = (rx * 32 + slot % 32, rz * 32 + slot // 32)
            actual = (body.get("xPos"), body.get("zPos"))
            if actual != expected:
                raise CorruptWorld(f"{region}:{slot} expected chunk {expected}, got {actual}")
            yield chunk


def scan(regions: Path, target: str, sample_limit: int = 40) -> dict:
    if not regions.is_dir():
        raise ValueError(f"region directory missing: {regions}")
    files = sorted(p for p in regions.iterdir() if REGION_NAME.match(p.name))
    if not files:
        raise ValueError(f"no Anvil region files in {regions}")
    chunks = 0
    ores = 0
    chunks_with_ore = set()
    per_y = Counter()
    examples = []
    status_counts = Counter()
    fully_generated_chunks = 0
    for filename in files:
        for chunk in read_region(filename):
            chunks += 1
            body = chunk.get("Level", chunk)
            status = str(body.get("Status", "<missing>"))
            status_counts[status] += 1
            if status.split(":")[-1] != "full":
                continue  # Unfinished chunks are not evidence of successful worldgen.
            fully_generated_chunks += 1
            for x, y, z in chunk_positions(chunk, target):
                ores += 1
                chunks_with_ore.add((x >> 4, z >> 4))
                per_y[y] += 1
                if len(examples) < sample_limit:
                    examples.append({"x": x, "y": y, "z": z})
    return {
        "target": target,
        "source_directory": str(regions.resolve()),
        "region_files": len(files),
        "chunks_scanned": chunks,
        "fully_generated_chunks": fully_generated_chunks,
        "blocks_found": ores,
        "ore_bearing_chunks": len(chunks_with_ore),
        "blocks_per_1000_chunks": round(1000.0 * ores / chunks, 3) if chunks else 0,
        "ore_y_histogram": dict(sorted(per_y.items())),
        "chunk_statuses": dict(status_counts),
        "sample_positions": examples,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("region_dir", type=Path, help="Fresh isolated world/region directory")
    parser.add_argument("--target", default=TARGET)
    parser.add_argument("--min-chunks", type=int, default=64)
    parser.add_argument("--min-blocks", type=int, default=1)
    parser.add_argument("--sample-limit", type=int, default=40)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = scan(args.region_dir, args.target, args.sample_limit)
    result["passed"] = result["fully_generated_chunks"] >= args.min_chunks and result["blocks_found"] >= args.min_blocks
    result["thresholds"] = {"min_chunks": args.min_chunks, "min_blocks": args.min_blocks}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, struct.error, EOFError, zlib.error) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(3)
