#!/usr/bin/env python3
"""Generate the Modpack Manager manifest from the NsTut TFG fork source of truth."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
NSTUT = ROOT / "nstut"
GENERATED = NSTUT / "modpack-manager.patch.json"

SEMANTIC_PATHS = {
    "config/economy-storage.properties",
    ".pakku/server-overrides/config/trueuuid-common.toml",
    ".pakku/server-overrides/server.properties",
    "config/simplyspeakers-common.toml",
    ".pakku/server-overrides/config/simplyspeakers-common.toml",
    "config/gtceu.yaml",
    "defaultconfigs/createhorsepower-server.toml",
    ".pakku/server-overrides/defaultconfigs/ftbchunks-world.snbt",
    ".pakku/server-overrides/defaultconfigs/ftbranks/ranks.snbt",
}
IGNORED_PREFIXES = ("nstut/", "scripts/nstut/", ".github/")
IGNORED_EXACT = {"pakku.json", "pakku-lock.json"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def fork_changes(base_ref: str) -> list[tuple[str, str]]:
    out = git("diff", "--no-renames", "--name-status", base_ref, "--")
    result = []
    for line in out.splitlines():
        if not line:
            continue
        parts = line.split("\t")
        result.append((parts[0], parts[-1].replace("\\", "/")))
    return result


def ignored(path: str) -> bool:
    return path in IGNORED_EXACT or any(path.startswith(prefix) for prefix in IGNORED_PREFIXES)


def raw_url(source_ref: str, path: str) -> str:
    encoded_path = "/".join(quote(part, safe="") for part in path.split("/"))
    return (
        "https://raw.githubusercontent.com/UpperMoon0/TFG-Modern-Fork/"
        f"refs/tags/{quote(source_ref, safe='')}/{encoded_path}"
    )


def git_normalized_file_bytes(path: str) -> bytes:
    """Return the bytes Git will store/serve for path, after clean filters/EOL normalization."""
    raw = (ROOT / path).read_bytes()
    object_id = subprocess.check_output(
        ["git", "-C", str(ROOT), "hash-object", "-w", "--path", path, "--stdin"],
        input=raw,
    ).decode().strip()
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "cat-file", "blob", object_id]
    )


def deployment_path(path: str) -> tuple[str, list[str]]:
    server_prefix = ".pakku/server-overrides/"
    client_prefix = ".pakku/client-overrides/"
    if path.startswith(server_prefix):
        return path[len(server_prefix):], ["server"]
    if path.startswith(client_prefix):
        return path[len(client_prefix):], ["client"]
    if (ROOT / server_prefix / path).is_file():
        # Pakku replaces this root file with its dedicated server override.
        return path, ["client"]
    return path, ["client", "server"]


def validate_install_destinations(manifest):
    artifacts = {artifact['id']: artifact['sha256'] for artifact in manifest['artifacts']}
    destinations = {}
    for operation in manifest['operations']:
        if operation['type'] != 'installFile':
            continue
        checksum = artifacts[operation['artifact']]
        for side in operation['targets']:
            key = (side, operation['destination'])
            if key in destinations and destinations[key] != checksum:
                raise ValueError(f'conflicting managed artifacts target {side}: {key[1]}')
            destinations[key] = checksum


def build_manifest() -> dict:
    release = load(NSTUT / "release.json")
    managed = load(NSTUT / "managed-mods.json")
    runtime = load(NSTUT / "runtime-overlays.json")

    artifacts = []
    operations = []

    migration_path = NSTUT / "base-migration.json"
    if migration_path.exists():
        migration = load(migration_path)
        if migration['baseRef'] != release['baseRef']:
            raise ValueError('migration payload base does not match release')
        for side, target in migration['targets'].items():
            artifact_id = f"base-{side}-{release['baseRef']}"
            artifacts.append({'id': artifact_id, **target['archive']})
            fields = {key: target[key] for key in ('sourceFile', 'sourceSha256', 'targetFile', 'targetSha256', 'marker', 'markerContent')}
            operations.append({'type': 'migratePack', 'artifact': artifact_id, **fields, 'targets': [side]})
            for download in target['downloads']:
                artifact_id = 'upstream-' + side + '-' + hashlib.sha256(download['path'].encode()).hexdigest()[:16]
                artifacts.append({'id': artifact_id, **{key: download[key] for key in ('url', 'sha256', 'fileName')}})
                operations.append({'type': 'installFile', 'artifact': artifact_id, 'destination': download['path'], 'targets': [side]})

    for mod in managed["mods"]:
        artifacts.append(
            {
                "id": mod["id"],
                "url": mod["url"],
                "sha256": mod["sha256"],
                "fileName": mod["fileName"],
            }
        )
        for pattern in mod["cleanupPatterns"]:
            operations.append(
                {
                    "type": "removeMatching",
                    "pattern": pattern,
                    "targets": mod["cleanupTargets"],
                }
            )
        operations.append(
            {
                "type": "installFile",
                "artifact": mod["id"],
                "destination": f"mods/{mod['fileName']}",
                "targets": mod["installTargets"],
            }
        )

    for overlay in runtime["overlays"]:
        if overlay["format"] == "yaml":
            operations.append(
                {
                    "type": "patchYaml",
                    "destination": overlay["path"],
                    "values": overlay["values"],
                    "skipIfMissing": False,
                    "targets": overlay["targets"],
                }
            )
        elif overlay["format"] == "properties":
            operations.append({
                "type": "patchProperties", "destination": overlay["path"],
                "values": overlay["values"], "skipIfMissing": False,
                "targets": overlay["targets"],
            })
        elif overlay["format"] == "toml":
            operations.append(
                {
                    "type": "patchToml",
                    "destination": overlay["path"],
                    "values": overlay["values"],
                    "skipIfMissing": False,
                    "targets": overlay["targets"],
                }
            )
        elif overlay["format"] in {"snbt", "snbtAll"}:
            operations.append(
                {
                    "type": "patchSnbt",
                    "destination": overlay["path"],
                    "values": overlay["values"],
                    "replaceAll": overlay["format"] == "snbtAll",
                    "skipIfMissing": True,
                    "targets": overlay["targets"],
                }
            )

    for status, path in fork_changes(release["baseRef"]):
        if ignored(path) or path in SEMANTIC_PATHS:
            continue
        destination, targets = deployment_path(path)
        if migration_path.exists() and destination.startswith('.nstut-tfg-base-'):
            # Manager commits the marker only after the entire base and overlay.
            continue
        if status.startswith("D"):
            operations.append(
                {
                    "type": "removeMatching",
                    "pattern": destination,
                    "targets": targets,
                }
            )
            continue
        file_path = ROOT / path
        if not file_path.is_file():
            continue
        artifact_id = "fork-" + hashlib.sha256(path.encode()).hexdigest()[:16]
        artifacts.append(
            {
                "id": artifact_id,
                "url": raw_url(release["sourceRef"], path),
                "sha256": hashlib.sha256(git_normalized_file_bytes(path)).hexdigest(),
                "fileName": file_path.name,
            }
        )
        operations.append(
            {
                "type": "installFile",
                "artifact": artifact_id,
                "destination": destination,
                "targets": targets,
            }
        )

    manifest = {
        "schemaVersion": 1,
        "id": "tfg-nstut-managed",
        "name": "TFG NsTut Fork Overlay",
        "version": release["overlayVersion"],
        "description": (
            f"Generated from UpperMoon0/TFG-Modern-Fork {release['sourceRef']} "
            f"on upstream {release['baseRef']}."
        ),
        "requiredPaths": ["mods", "config", "kubejs", "defaultconfigs"] + required_base_markers(release),
        "artifacts": artifacts,
        "operations": operations,
    }
    validate_install_destinations(manifest)
    return manifest


def required_base_markers(release: dict) -> list[str]:
    path = NSTUT / "base-installation.json"
    if not path.exists():
        return []
    installation = load(path)
    if installation["baseRef"] != release["baseRef"]:
        raise ValueError("base installation marker does not match release base")
    return [installation["requiredMarker"]]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = json.dumps(build_manifest(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        existing = GENERATED.read_text(encoding="utf-8-sig") if GENERATED.exists() else ""
        if existing != rendered:
            print(f"{GENERATED.relative_to(ROOT)} is stale; regenerate it")
            return 1
        print("generated Modpack Manager manifest is current")
        return 0

    GENERATED.write_text(rendered, encoding="utf-8")
    print(f"wrote {GENERATED.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
