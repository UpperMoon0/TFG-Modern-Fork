#!/usr/bin/env python3
"""Require the pinned fork JAR to be publicly downloadable before integration."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

root = Path(__file__).resolve().parents[2]
managed = json.loads((root / "nstut/managed-mods.json").read_text(encoding="utf-8-sig"))
mod = next(m for m in managed["mods"] if m["id"] == "trueuuid")
assert mod["repository"] == "UpperMoon0/TrueUUID", "TrueUUID must use the reviewed owner fork"
expected = f"https://github.com/UpperMoon0/TrueUUID/releases/download/v{mod['version']}/{mod['fileName']}"
assert mod["url"] == expected, "TrueUUID URL must use its exact versioned release"
with urlopen(mod["url"], timeout=30) as response:
    data = response.read(2 * 1024 * 1024 + 1)
assert len(data) <= 2 * 1024 * 1024, "unexpected TrueUUID artifact size"
assert hashlib.sha256(data).hexdigest() == mod["sha256"], "published TrueUUID hash mismatch"
lock = json.loads((root / "pakku-lock.json").read_text(encoding="utf-8-sig"))
project = next(p for p in lock["projects"] if p.get("slug", {}).get("github") == mod["repository"])
assert project["files"][0]["size"] == len(data), "published TrueUUID size mismatch"
print(f"Verified public {mod['fileName']}: {len(data)} bytes, {mod['sha256']}")
