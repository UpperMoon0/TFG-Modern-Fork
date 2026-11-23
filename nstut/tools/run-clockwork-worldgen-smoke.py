#!/usr/bin/env python3
"""Run one bounded, headless Clockwork worldgen check in a disposable Forge pack.

NOT a server installer. CI provisions a complete, isolated candidate Forge pack
under /tmp and creates the marker .tfg-clockwork-disposable; this tool then
generates ordinary spawn chunks with a temporary rarity-1 feature, stops the
server, and inspects saved Anvil blocks. No players, Chunky or spectator mode.

Example:
  python3 nstut/tools/run-clockwork-worldgen-smoke.py \
    --repo-root . --server-dir /tmp/clockwork-ci-server \
    --launch "./run.sh nogui" --evidence-dir /tmp/clockwork-ci-evidence

Only the ordinary test seed is run; a second seed is used if the first failed
to place any ore despite generating enough full chunks.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FEATURE = Path("kubejs/data/tfg/worldgen/configured_feature/earth/vein/deep_wanderlite.json")
DISPOSABLE_MARKER = ".tfg-clockwork-disposable"
WORLD = "clockwork-smoke"
SEEDS = (2026112401, 2026112402)
DONE = re.compile(r"\bDone \([0-9,.]+s?\)", re.IGNORECASE)
ERRORS = re.compile(
    r"Failed to load datapacks|Failed to load.*recipes|No such item|"
    r"Errors in registry|Failed to load.*tag|"
    r"\[[^\r\n\[\]]+/ERROR\][ \t]*\[KubeJS[^\r\n\[\]]*\]|"
    r"\[KubeJS[^\r\n\[\]]*/ERROR\]|"
    r"Error parsing recipe tfg:clockwork/|"
    r"failed to add recipe from staging into lookup DB: tfg:assembler/clockwork/|"
    r"with [1-9][0-9]* failed recipes\\b|"
    r"Caused by: .*Invalid.*Recipe",
    re.IGNORECASE,
)


def module(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def safely_disposable(path: Path) -> Path:
    path = path.resolve()
    tmp = Path(tempfile.gettempdir()).resolve()
    if path == tmp or not path.is_relative_to(tmp):
        raise ValueError(f"CI server MUST live below {tmp}: {path}")
    if not path.is_dir() or not (path / DISPOSABLE_MARKER).is_file():
        raise ValueError(f"Missing disposable marker in isolated CI server: {path}")
    if not (path / "mods").is_dir() or not (path / "kubejs").is_dir():
        raise ValueError("Expected pre-provisioned isolated Forge mods + kubejs")
    if not (path / "eula.txt").is_file() or "eula=true" not in (
        path / "eula.txt"
    ).read_text(encoding="utf-8"):
        raise ValueError("Isolated test server must already accept the EULA")
    if (path / WORLD).exists():
        raise ValueError("Refusing an already-generated world; smoke needs fresh chunks")
    return path


def set_properties(server: Path, seed: int) -> None:
    target = server / "server.properties"
    settings = {}
    if target.exists():
        for line in target.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, val = line.split("=", 1)
                settings[key.strip()] = val.strip()
    settings.update({
        "level-name": WORLD,
        "level-seed": str(seed),
        "server-ip": "127.0.0.1",
        "server-port": "0",  # OS-assigned ephemeral port, never production 25565
        "enable-rcon": "false",
        "enable-query": "false",
        "online-mode": "false",
        "white-list": "true",
        "max-players": "1",
        "view-distance": "2",
        "simulation-distance": "2",
        "enable-status": "false",
        "motd": "Clockwork isolated worldgen smoke",
    })
    target.write_text(
        "".join(f"{k}={v}\n" for k, v in sorted(settings.items())),
        encoding="utf-8",
    )


def stage_feature(repo: Path, server: Path, evidence: Path) -> dict:
    stagedir = server / FEATURE
    if stagedir.is_symlink() or any(
        parent.is_symlink() for parent in stagedir.parents
        if parent == server or server in parent.parents
    ):
        raise ValueError("Refusing to write through symlink in isolated KubeJS path")
    production = (repo / FEATURE).read_bytes()
    if stagedir.exists() and stagedir.read_bytes() != production:
        raise ValueError("CI candidate worldgen differs from the branch's production feature")
    smoke = module("stage-clockwork-worldgen-smoke.py", "clockwork_stage")
    # Stage in a separately named fresh temp directory under the same /tmp.
    overlay = server.parent / (server.name + "-clockwork-overlay")
    result = smoke.stage(repo, overlay)
    stagedir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(overlay / FEATURE, stagedir)
    cfg = json.loads(stagedir.read_text(encoding="utf-8"))
    if cfg["config"]["rarity"] != 1:
        raise AssertionError("Rarity override not installed on test server")
    evidence.mkdir(parents=True, exist_ok=False)
    (evidence / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def run_server(server: Path, command: str, log: Path, timeout: int) -> None:
    argv = shlex.split(command)
    if not argv or any("\0" in arg for arg in argv):
        raise ValueError("Empty or invalid launch command")
    begin = time.monotonic()
    with log.open("w", encoding="utf-8") as output:
        proc = subprocess.Popen(
            argv, cwd=server, stdin=subprocess.PIPE,
            stdout=output, stderr=subprocess.STDOUT, text=True,
            start_new_session=True,
        )
        try:
            ready = False
            last = 0
            with log.open("r", encoding="utf-8", errors="replace") as reader:
                while time.monotonic() - begin < timeout:
                    reader.seek(last)
                    text = reader.read()
                    last = reader.tell()
                    if ERRORS.search(text):
                        raise RuntimeError("Forge/KubeJS registry or recipe load error")
                    if DONE.search(text):
                        ready = True
                        break
                    if proc.poll() is not None:
                        raise RuntimeError(f"Forge exited before ready: {proc.returncode}")
                    time.sleep(0.5)
            if not ready:
                raise TimeoutError("Spawn generation did not finish before timeout")
            proc.stdin.write("save-all flush\n")
            proc.stdin.flush()
            time.sleep(2)
            proc.stdin.write("stop\n")
            proc.stdin.flush()
            proc.wait(timeout=120)
            if proc.returncode != 0:
                raise RuntimeError(f"Forge exited unsuccessfully ({proc.returncode})")
            if ERRORS.search(log.read_text(encoding="utf-8", errors="replace")):
                raise RuntimeError("Forge/KubeJS error found in the final server log")
        finally:
            if proc.poll() is None:
                # Kill only this disposable server process group.
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait(timeout=15)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--server-dir", type=Path, required=True)
    parser.add_argument("--launch", required=True, help="Trusted argv string, e.g. ./run.sh nogui")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--min-chunks", type=int, default=64)
    args = parser.parse_args()
    server = safely_disposable(args.server_dir)
    repo = args.repo_root.resolve(strict=True)
    evidence = args.evidence_dir.resolve()
    if evidence.exists():
        raise FileExistsError("Refusing to overwrite prior evidence directory")
    tmp = Path(tempfile.gettempdir()).resolve()
    if not evidence.is_relative_to(tmp) or evidence == tmp:
        raise ValueError("Evidence must be under /tmp")
    if evidence == server or evidence.is_relative_to(server):
        raise ValueError("Evidence must not be inside the disposable server")
    staged = stage_feature(repo, server, evidence)
    scan = module("scan-clockwork-worldgen.py", "clockwork_scan")
    all_results = []
    try:
        for index, seed in enumerate(SEEDS, 1):
            if (server / WORLD).exists():
                # First attempt was verified and logged before removing its
                # disposable world for a retry. Never remove any other path.
                if index == 1:
                    raise ValueError("Unexpected existing smoke world")
                shutil.rmtree(server / WORLD)
            set_properties(server, seed)
            log = evidence / f"forge-seed-{seed}.log"
            run_server(server, args.launch, log, args.timeout)
            result = scan.scan(server / WORLD / "region", scan.TARGET)
            coords = result["sample_positions"]
            # TFC disc veins have height 4, so allow small vertical displacement.
            depth_ok = all(-64 <= loc["y"] <= -20 for loc in coords)
            result.update({
                "seed": seed,
                "feature_config_sha256": hashlib.sha256(
                    (server / FEATURE).read_bytes()
                ).hexdigest(),
                "min_fully_generated_chunks": args.min_chunks,
                "depth_ok": depth_ok,
            })
            result["passed"] = (
                result["fully_generated_chunks"] >= args.min_chunks
                and result["blocks_found"] > 0 and depth_ok
            )
            (evidence / f"result-seed-{seed}.json").write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            all_results.append(result)
            print(json.dumps(result, indent=2), flush=True)
            if result["passed"]:
                return 0
            if result["fully_generated_chunks"] < args.min_chunks:
                raise RuntimeError("Too few full spawn chunks; cannot interpret zero ore")
        return 2
    finally:
        (evidence / "summary.json").write_text(
            json.dumps({"attempts": len(all_results),
                        "passed": any(r["passed"] for r in all_results),
                        "results": all_results, "overlay": staged},
                       indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, TimeoutError, AssertionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(3)
