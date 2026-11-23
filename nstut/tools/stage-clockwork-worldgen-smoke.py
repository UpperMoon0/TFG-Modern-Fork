#!/usr/bin/env python3
"""Stage a *temporary* high-frequency Clockwork vein override for a disposable server.

Does not modify the repository, a running server, or any existing directory.
The isolated server must be assembled separately using the generated KubeJS
overlay. Intended for one fresh Forge 1.20.1 world at a fixed smoke-test seed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

FEATURE = Path("kubejs/data/tfg/worldgen/configured_feature/earth/vein/deep_wanderlite.json")
PRODUCTION_RARITY = 420
SMOKE_RARITY = 1


def stage(repo: Path, output: Path) -> dict:
    src = (repo / FEATURE).resolve(strict=True)
    data = src.read_bytes()
    cfg = json.loads(data)
    vein = cfg["config"]
    assert cfg["type"] == "tfc:disc_vein", "unexpected vein type"
    assert vein["rarity"] == PRODUCTION_RARITY, "production rarity drifted"
    assert vein["min_y"] == -60 and vein["max_y"] == -24, "production depth drifted"
    assert len(vein["blocks"]) >= 5
    assert all(
        entry["with"] == [{"block": "vs_clockwork:wanderlite_deepslate_ore", "weight": 1}]
        for entry in vein["blocks"]
    ), "target/host rock entries drifted"

    output = output.resolve()
    tmp = Path(tempfile.gettempdir()).resolve()
    if output == tmp or not output.is_relative_to(tmp):
        raise ValueError(f"smoke overlay must be a new directory under {tmp}")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing directory: {output}")

    cfg["config"]["rarity"] = SMOKE_RARITY
    target = output / FEATURE
    target.parent.mkdir(parents=True, exist_ok=False)
    target.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    assert src.read_bytes() == data, "production source was modified"
    result = {
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "production_rarity": PRODUCTION_RARITY,
        "smoke_rarity": SMOKE_RARITY,
        "test_overlay": str(output),
        "override_feature": str(target),
        "source_unchanged": True,
        "note": "Apply overlay ONLY to an isolated disposable server before world creation.",
    }
    (output / "smoke-manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(stage(args.repo_root, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyError, ValueError, AssertionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
