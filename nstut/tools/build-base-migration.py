#!/usr/bin/env python3
"""Build public, owned-file migration payloads from verified Pakku exports.

Mod JARs remain downloads from their original providers; private instance data
never enters these archives. Run with a pristine previous upstream checkout.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOTS = ('mods/', 'config/', 'defaultconfigs/', 'kubejs/', 'resourcepacks/', 'shaderpacks/', 'tacz/')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def owned(path):
    return path.startswith(ROOTS) and not path.startswith('kubejs/export/') and path != 'config/trueuuid-registry.json'


def previous_files(source, side):
    result = {}
    for directory in ('config', 'defaultconfigs', 'kubejs', 'tacz', 'resourcepacks', 'shaderpacks'):
        if side == 'server' and directory in ('resourcepacks', 'shaderpacks'):
            continue
        for p in (source / directory).rglob('*'):
            if not p.is_file():
                continue
            name = p.relative_to(source).as_posix()
            if owned(name) and not (side == 'server' and name.startswith('kubejs/assets/')):
                result[name] = p.read_bytes()
    overrides = source / '.pakku' / (side + '-overrides')
    for p in overrides.rglob('*'):
        if p.is_file() and owned(p.relative_to(overrides).as_posix()):
            result[p.relative_to(overrides).as_posix()] = p.read_bytes()
    return result


def provider_file(lock, filename, data):
    choices = [f for p in lock['projects'] for f in p['files'] if f['file_name'] == filename]
    assert choices, 'No pinned provider artifact for ' + filename
    matching = [f for f in choices if all(hashlib.new(a, data).hexdigest() == h for a, h in f['hashes'].items())]
    assert matching, 'No matching provider hash for ' + filename
    return next((f for f in matching if f['type'] == 'modrinth'), matching[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--previous', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source, previous, out = args.source, args.previous, args.output
    assert not (previous / 'world').exists(), 'previous must be a pristine source checkout'
    assert json.loads((previous / 'pakku-lock.json').read_text())['mc_versions'] == ['1.20.1']
    out.mkdir(parents=True, exist_ok=True)
    lock = json.loads((source / 'pakku-lock.json').read_text())
    old_lock = json.loads((previous / 'pakku-lock.json').read_text())
    old_core = next(f for p in old_lock['projects'] for f in p['files'] if f['file_name'] == 'TerraFirmaGreg-Core-Modern-0.9.23.jar')
    cached_old = out / old_core['file_name']
    if not cached_old.exists():
        cached_old.write_bytes(urllib.request.urlopen(old_core['url'], timeout=90).read())
    assert hashlib.sha1(cached_old.read_bytes()).hexdigest() == old_core['hashes']['sha1']
    new_core = source / 'mods/TerraFirmaGreg-Core-Modern-0.9.25.jar'
    assert new_core.is_file()
    marker = '.nstut-tfg-base-0.13.12'
    marker_content = (source / '.pakku/client-overrides' / marker).read_text()
    metadata = {'schemaVersion': 1, 'baseRef': '0.13.12', 'sourceBaseRef': '0.13.10', 'minimumManagerVersion': '1.0.7', 'targets': {}}
    for side in ('server', 'client'):
        data = {}
        if side == 'server':
            pack = next((source / 'build/serverpack').glob('*.zip'))
            with zipfile.ZipFile(pack) as archive:
                assert archive.testzip() is None
                for info in archive.infolist():
                    name = info.filename.removeprefix('./')
                    if not info.is_dir() and owned(name):
                        data[name] = archive.read(info)
        else:
            # Use the canonical CurseForge export for matching server/client
            # mod versions; Modrinth provider versions can legitimately differ.
            pack = next((source / 'build/curseforge').glob('*.zip'))
            with zipfile.ZipFile(pack) as archive:
                assert archive.testzip() is None
                manifest = json.loads(archive.read('manifest.json'))
                for ref in manifest['files']:
                    choices = [(p, f) for p in lock['projects'] for f in p['files']
                               if f['type'] == 'curseforge' and str(f['parent_id']) == str(ref['projectID']) and str(f['id']) == str(ref['fileID'])]
                    assert len(choices) == 1, ref
                    project, f = choices[0]
                    folder = {'MOD': 'mods', 'RESOURCE_PACK': 'resourcepacks', 'SHADER': 'shaderpacks'}[project['type']]
                    path = folder + '/' + f['file_name']
                    local = source / path
                    if not local.exists():
                        local = source / 'mods' / f['file_name']
                    b = local.read_bytes() if local.is_file() else b''
                    if not all(hashlib.new(a, b).hexdigest() == h for a, h in f['hashes'].items()):
                        b = urllib.request.urlopen(f['url'], timeout=90).read()
                    assert all(hashlib.new(a, b).hexdigest() == h for a, h in f['hashes'].items()), path
                    data[path] = b
                for info in archive.infolist():
                    name = info.filename.removeprefix('overrides/')
                    if info.filename.startswith('overrides/') and not info.is_dir() and owned(name):
                        data[name] = archive.read(info)
        # All provider assets are installed through pinned manifest artifacts,
        # preserving the pack's upstream redistribution boundary.
        downloads = []
        for name in sorted(list(data)):
            if any(f['file_name'] == Path(name).name for p in lock['projects'] for f in p['files']):
                b = data.pop(name)
                f = provider_file(lock, Path(name).name, b)
                for algorithm, expected in f['hashes'].items():
                    assert hashlib.new(algorithm, b).hexdigest() == expected, name
                downloads.append({'path': name, 'fileName': Path(name).name, 'url': f['url'], 'sha256': sha(b)})
        assert any(f['path'] == 'mods/' + new_core.name for f in downloads)
        old = previous_files(previous, side)
        inventory = {name: sha(b) for name, b in old.items()}
        for project in old_lock['projects']:
            if side == 'server' and project.get('side') == 'CLIENT':
                continue
            folder = {'MOD': 'mods', 'RESOURCE_PACK': 'resourcepacks', 'SHADER': 'shaderpacks'}[project['type']]
            if side == 'server' and folder != 'mods':
                continue
            for f in project['files']:
                inventory.setdefault(folder + '/' + f['file_name'], '0' * 64)
        path = out / ('tfg-base-0.13.12-' + side + '.zip')
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
            archive.writestr('migration-index.json', json.dumps({'schemaVersion': 1, 'files': {name: sha(b) for name, b in data.items()}, 'previousFiles': inventory}))
            for name, b in sorted(data.items()):
                assert owned(name) and '..' not in Path(name).parts
                archive.writestr('files/' + name, b)
            for name, b in sorted(old.items()):
                if name.startswith('config/'):
                    archive.writestr('previous/' + name, b)
        metadata['targets'][side] = {
            'archive': {'fileName': path.name, 'url': 'https://github.com/UpperMoon0/TFG-Modern-Fork/releases/download/nstut-base-0.13.12/' + path.name, 'sha256': sha(path.read_bytes())},
            'sourceFile': 'mods/' + old_core['file_name'], 'sourceSha256': sha(cached_old.read_bytes()),
            'targetFile': 'mods/' + new_core.name, 'targetSha256': sha(new_core.read_bytes()),
            'marker': marker, 'markerContent': marker_content,
            'downloads': downloads,
        }
        print(side, 'owned payload files', len(data), 'provider mod downloads', len(downloads), 'archive bytes', path.stat().st_size, flush=True)
    (out / 'base-migration.json').write_text(json.dumps(metadata, indent=2) + '\n')


if __name__ == '__main__':
    main()
