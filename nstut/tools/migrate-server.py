#!/usr/bin/env python3
"""Upgrade the currently installed TFG server, including its base and world.

Example: python3 migrate-server.py /path/to/server --service tfg-manager.service
The service option uses the sibling tfg-manager.py for graceful stop, wake and
authenticated readiness. Without it, the caller must stop/start the server.
"""
import argparse
import base64
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tarfile
import time
import urllib.request

HERE = Path(__file__).resolve().parent
VERSION = '1.0.7'
EXCLUDED = ('.modpack-manager', 'backups', 'logs', 'crash-reports')


def protected_inventory(root):
    """Hash instance-owned data outside the public pack's writable roots."""
    pack_roots = {'mods', 'config', 'defaultconfigs', 'kubejs', 'resourcepacks', 'shaderpacks', 'tacz'}
    result = {}
    paths = [p for p in root.iterdir() if p.name not in pack_roots | set(EXCLUDED)]
    identity = root / 'config/trueuuid-registry.json'
    if identity.exists():
        paths.append(identity)
    for entry in paths:
        for path in entry.rglob('*') if entry.is_dir() else [entry]:
            if path.is_file() and not path.is_symlink():
                with path.open('rb') as stream:
                    result[path.relative_to(root).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return result


def snapshot(root, backup):
    def ignore(path, names):
        return [name for name in names if name in EXCLUDED] if Path(path).resolve() == root else []
    shutil.copytree(root, backup, symlinks=True, ignore=ignore)


def restore_snapshot(root, backup):
    for child in root.iterdir():
        if child.name in EXCLUDED:
            continue
        if child.is_symlink() or child.is_file():
            child.unlink()
        else:
            assert child.resolve().is_relative_to(root)
            shutil.rmtree(child)
    for child in backup.iterdir():
        destination = root / child.name
        if child.is_symlink():
            destination.symlink_to(os.readlink(child), target_is_directory=child.is_dir())
        elif child.is_dir():
            shutil.copytree(child, destination, symlinks=True)
        else:
            shutil.copy2(child, destination)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def server_pids(root):
    result = []
    for process in Path('/proc').iterdir():
        if process.name.isdigit():
            try:
                if b'java' in (process / 'cmdline').read_bytes() and (process / 'cwd').resolve() == root:
                    result.append(int(process.name))
            except (FileNotFoundError, PermissionError):
                pass
    return result


def ensure_cli(root):
    directory = root / '.modpack-manager/tools' / VERSION
    cli = directory / 'modpackctl'
    if cli.exists():
        return cli
    directory.mkdir(parents=True, exist_ok=True)
    base = f'https://github.com/UpperMoon0/Modpack-Manager/releases/download/v{VERSION}/'
    name = 'modpackctl-linux-x86_64.tar.gz'
    expected = urllib.request.urlopen(base + name + '.sha256', timeout=60).read().decode().split()[0]
    data = urllib.request.urlopen(base + name, timeout=300).read()
    assert hashlib.sha256(data).hexdigest() == expected, 'CLI release checksum mismatch'
    archive = directory / name
    archive.write_bytes(data)
    with tarfile.open(archive) as tar:
        members = [m for m in tar.getmembers() if m.isfile() and Path(m.name).name == 'modpackctl']
        assert len(members) == 1
        cli.write_bytes(tar.extractfile(members[0]).read())
    cli.chmod(0o700)
    return cli


def wake(control):
    # Wake through the real manager, rather than creating a second JVM.
    host = b'localhost'
    p = control.varint(0) + control.varint(control.PROTOCOL) + control.varint(len(host)) + host + control.PUBLIC_PORT.to_bytes(2, 'big') + control.varint(2)
    for _ in range(20):
        try:
            with socket.create_connection(('127.0.0.1', control.PUBLIC_PORT), timeout=3) as s:
                s.sendall(control.varint(len(p)) + p)
                s.recv(1024)
            return
        except ConnectionRefusedError:
            time.sleep(.25)
    raise RuntimeError('server wake service did not start')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--modpackctl', type=Path)
    parser.add_argument('--manifest', help='Local test manifest; normal use follows the published TFG profile')
    parser.add_argument('--service', help='systemd wake manager service')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--timeout', type=int, default=900)
    args = parser.parse_args()
    assert sys.platform.startswith('linux'), 'Use Modpack Manager 1.0.7 for desktop/client updates'
    os.umask(0o077)
    root = args.root.resolve()
    assert root.is_dir() and root != Path('/'), 'invalid server root'
    for directory in ('mods', 'config', 'kubejs', 'defaultconfigs'):
        assert (root / directory).is_dir(), 'incomplete TFG installation'
    cli = args.modpackctl.resolve() if args.modpackctl else ensure_cli(root)
    source = ['--manifest', args.manifest] if args.manifest else ['--tfg']
    command = [str(cli), 'plan', '--root', str(root), '--target', 'server', *source, '--json']
    plan = json.loads(subprocess.check_output(command, text=True))
    print('Migration plan', plan['manifestVersion'], len(plan['items']), 'changes', flush=True)
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    control = None
    was_active = False
    if args.service:
        sys.path.insert(0, str(root.parent))
        control = load_module('tfg_migration_control', root.parent / 'tfg-manager.py')
        assert Path(control.SERVER_DIR).resolve() == root, 'wake manager targets a different installation'
        was_active = subprocess.run(['systemctl', 'is-active', '--quiet', args.service]).returncode == 0
        if server_pids(root):
            subprocess.run(['screen', '-S', control.SCREEN_NAME, '-p', '0', '-X', 'stuff', 'stop\n'], check=True)
            deadline = time.monotonic() + 180
            while server_pids(root) and time.monotonic() < deadline:
                time.sleep(1)
            assert not server_pids(root), 'server did not save/stop; migration aborted'
        subprocess.run(['systemctl', 'stop', args.service], check=True)
    assert not server_pids(root), 'stop the server before migration'
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    metadata = root / '.modpack-manager'
    backup = metadata / 'migration-backups' / stamp
    backup.parent.mkdir(parents=True, exist_ok=True)
    old_state = metadata / 'state-server.json'
    state_bytes = old_state.read_bytes() if old_state.exists() else None
    no_sleep = Path(control.NOSLEEP_FILE) if control else None
    no_sleep_existed = no_sleep.exists() if no_sleep else False
    backup_complete = False
    checkpoint = metadata / 'active-upstream-migration.json'
    try:
        if checkpoint.exists():
            previous = json.loads(checkpoint.read_text())
            assert previous['version'] == plan['manifestVersion'] and previous['root'] == str(root), 'another migration is unfinished'
            backup = Path(previous['backup']).resolve()
            backup.relative_to((metadata / 'migration-backups').resolve())
            assert backup.is_dir(), 'original migration backup missing'
            state_bytes = base64.b64decode(previous['state']) if previous['state'] is not None else None
            no_sleep_existed = previous['noSleepExisted']
        else:
            snapshot(root, backup)
            checkpoint.write_text(json.dumps({'root': str(root), 'version': plan['manifestVersion'], 'backup': str(backup), 'state': base64.b64encode(state_bytes).decode() if state_bytes is not None else None, 'noSleepExisted': no_sleep_existed}) + '\n')
        backup_complete = True
        print('Stopped installation backup complete', str(backup), flush=True)
        properties = load_module('tfg_properties', HERE / 'prepare-premium-identities.py').properties
        world_name = properties((root / 'server.properties').read_bytes().decode('latin-1')).get('level-name', 'world')
        world = (root / world_name).resolve()
        world.relative_to(root)
        subprocess.run([sys.executable, str(HERE / 'migrate-world-0.13.12.py'), str(world), '--apply', '--report', str(backup.parent / (stamp + '-world.json'))], check=True)
        protected = protected_inventory(root)
        command[1] = 'apply'
        result = json.loads(subprocess.check_output(command, text=True))
        assert protected_inventory(root) == protected, 'pack migration changed protected instance data'
        command[1] = 'plan'
        post = json.loads(subprocess.check_output(command, text=True))
        assert not post['items'], 'migration did not converge to an empty plan'
        report = {'version': post['manifestVersion'], 'backup': str(backup), 'changedPaths': result['changedPaths'], 'postPlanItems': 0, 'protectedFilesVerified': len(protected)}
        if control and was_active:
            java17 = Path('/usr/lib/jvm/java-17-openjdk-amd64/bin/java')
            assert java17.is_file(), 'Java 17 is required for the migrated server'
            start = root / 'start_server.sh'
            content = start.read_text()
            if 'exec java ' in content:
                content = content.replace('exec java ', 'exec ' + str(java17) + ' ', 1)
            forge_args = 'libraries/net/minecraftforge/forge/1.20.1-47.4.13/unix_args.txt'
            assert (root / forge_args).is_file(), 'installed Forge launch arguments are missing'
            # The generic starter checks the Internet even with installed libraries.
            # Launch the installed, unchanged Forge directly, retaining heap flags.
            content = content.replace('-jar minecraft_server.jar', '@' + forge_args, 1)
            start.write_text(content)
            no_sleep.touch()
            subprocess.run(['systemctl', 'start', args.service], check=True)
            wake(control)
            deadline = time.monotonic() + args.timeout
            while time.monotonic() < deadline and not control.server_ready():
                time.sleep(5)
            assert control.server_ready(), 'migrated server failed authenticated readiness'
            report.update(ready=True, players=control.players_online(), TPS=control.rcon_command('forge tps', timeout=30))
            print(control.rcon_command('save-all flush', timeout=90), flush=True)
        (backup.parent / (stamp + '-result.json')).write_text(json.dumps(report, indent=2) + '\n')
        checkpoint.unlink()
        print(json.dumps(report), flush=True)
    except BaseException:
        if control:
            if server_pids(root):
                subprocess.run(['screen', '-S', control.SCREEN_NAME, '-p', '0', '-X', 'stuff', 'stop\n'], check=False)
                deadline = time.monotonic() + 180
                while server_pids(root) and time.monotonic() < deadline:
                    time.sleep(1)
            if server_pids(root):
                raise RuntimeError('server still saving; backup retained, no automatic file rollback attempted')
            subprocess.run(['systemctl', 'stop', args.service], check=True)
        if backup_complete:
            restore_snapshot(root, backup)
            if state_bytes is None:
                old_state.unlink(missing_ok=True)
            else:
                old_state.write_bytes(state_bytes)
            checkpoint.unlink(missing_ok=True)
            print('Restored the original installation and world', flush=True)
        if control and was_active:
            subprocess.run(['systemctl', 'start', args.service], check=True)
        raise
    finally:
        if no_sleep and not no_sleep_existed:
            no_sleep.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
