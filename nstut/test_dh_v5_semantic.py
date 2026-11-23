#!/usr/bin/env python3
"""Guard the DH v5 semantic policy against repeated Modpack Manager drift.

This is a contract/model test, not a substitute for a real Manager apply + Forge
boot + two subsequent manager plans on an isolated server.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "DistantHorizons.toml"
MANIFEST = ROOT / "nstut" / "modpack-manager.patch.json"
OVERLAYS = ROOT / "nstut" / "runtime-overlays.json"


def apply_semantic_values(doc: dict, values: dict) -> int:
    """Model patchToml's dotted-key writes; count changed semantic values."""
    changed = 0
    for path, desired in values.items():
        keys = path.split(".")
        node = doc
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        if node.get(keys[-1]) != desired or type(node.get(keys[-1])) is not type(desired):
            node[keys[-1]] = desired
            changed += 1
    return changed


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    overlays = json.loads(OVERLAYS.read_text(encoding="utf-8"))
    template = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    operations = [o for o in manifest["operations"] if o.get("destination") == "config/DistantHorizons.toml"]
    policies = [o for o in overlays["overlays"] if o["path"] == "config/DistantHorizons.toml"]
    assert len(operations) == len(policies) == 1
    op, policy = operations[0], policies[0]
    assert op["type"] == "patchToml" and op["targets"] == ["client", "server"]
    assert op["values"] == policy["values"] and op["skipIfMissing"] is False
    assert template["_version"] == 5
    assert "serverId" not in template["server"]
    assert not any(
        o.get("destination") == "config/DistantHorizons.toml" and o["type"] == "installFile"
        for o in manifest["operations"]
    )

    # Runtime-only settings must survive; repeated plan should find no policy drift.
    runtime = deepcopy(template)
    runtime["server"]["serverId"] = 123456789
    runtime["server"]["privateRuntimeExtension"] = "preserve"
    runtime["client"]["advanced"]["autoUpdater"]["enableAutoUpdater"] = True
    runtime["server"]["enableAdaptiveTransferSpeed"] = False
    runtime["common"]["multiThreading"]["numberOfThreads"] = 4
    first = apply_semantic_values(runtime, op["values"])
    assert first == 3, first
    assert apply_semantic_values(runtime, op["values"]) == 0
    assert runtime["server"]["serverId"] == 123456789
    assert runtime["server"]["privateRuntimeExtension"] == "preserve"
    assert runtime["common"]["worldGenerator"]["chunkGeneratorMode"] == "FEATURES"
    assert runtime["client"]["advanced"]["autoUpdater"]["enableAutoUpdater"] is False
    assert runtime["server"]["enableAdaptiveTransferSpeed"] is True

    # The policy must be complete enough for a fresh v5 install as well.
    fresh = {}
    assert apply_semantic_values(fresh, op["values"]) == len(op["values"])
    assert apply_semantic_values(fresh, op["values"]) == 0
    assert fresh["_version"] == 5
    print("PASS: DH v5 semantic policy idempotence, runtime identity preservation, new installs")


if __name__ == "__main__":
    main()
