#!/usr/bin/env python3
"""Require the published Manager to plan this candidate pack's fresh install."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def check(manager: str, root: Path) -> None:
    release = json.loads((root / "nstut/release.json").read_text(encoding="utf-8-sig"))
    lock = json.loads((root / "pakku-lock.json").read_text(encoding="utf-8-sig"))
    with tempfile.TemporaryDirectory(prefix="tfg-install-check-") as temporary:
        destination = Path(temporary) / "new-instance"
        result = subprocess.run(
            [manager, "install", "--manifest", str(root / "nstut/modpack-manager.patch.json"),
             "--root", str(destination), "--dry-run", "--json"],
            text=True, capture_output=True, check=False,
        )
        if result.returncode:
            raise SystemExit("fresh-install compatibility failed: published Manager rejected "
                             + release["overlayVersion"] + "\n" + result.stderr)
        plan = json.loads(result.stdout)
        if plan["version"] != release["overlayVersion"]:
            raise SystemExit("fresh-install compatibility failed: wrong pack version")
        if lock["mc_versions"] != [plan["minecraftVersion"]]:
            raise SystemExit("fresh-install compatibility failed: Minecraft version differs from pack")
        if lock["loaders"] != {"forge": plan["forgeVersion"]}:
            raise SystemExit("fresh-install compatibility failed: Forge version differs from pack")
        if destination.exists():
            raise SystemExit("fresh-install compatibility failed: dry run modified destination")
    print("fresh-install compatibility passed for " + release["overlayVersion"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manager", required=True, help="Path to the released modpackctl executable")
    args = parser.parse_args()
    check(str(Path(args.manager).resolve()), Path(__file__).resolve().parents[2])


if __name__ == "__main__":
    main()
