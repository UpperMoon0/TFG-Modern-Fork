#!/usr/bin/env python3
"""Protect the upstream upgrade and the previously released custom overlay."""
import json
import fnmatch
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = 'nstut-0.13.15.8'
BASE = '0.13.17'


def historical(ref, path):
    return json.loads(subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{ref}:{path}']))


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))


def project_key(project):
    return tuple(sorted(project['slug'].items()))


def artifact_signature(project):
    # Display-name encoding and generated Pakku IDs do not identify an artifact.
    return {key: project.get(key) for key in ('type', 'side', 'slug', 'id', 'files')}


def validate(lock, managed, translations, upstream, previous_managed, previous_lang, old_lang):
    assert managed['base']['ref'] == BASE, 'wrong declared managed-mod base'
    audit_version = load('nstut/release.json')['sourceRef'].removeprefix('nstut-')
    approved = load(f'nstut/custom-mod-audit-{audit_version}.json')['approvedMods']
    assert managed['mods'] == approved, 'custom managed artifacts differ from the reviewed release audit'
    assert {m['id'] for m in approved} == {m['id'] for m in previous_managed['mods']}, 'custom managed mod set changed'
    upgraded = {'economy', 'openui', 'simply-screens', 'simply-speakers', 'packetweave', 'spice-of-life-integrations'}
    unchanged = lambda mods: [m for m in mods if m['id'] not in upgraded]
    assert unchanged(approved) == unchanged(previous_managed['mods']), 'unreviewed existing managed pin changed'
    trueuuid = next(m for m in approved if m['id'] == 'trueuuid')
    assert trueuuid['repository'] == 'UpperMoon0/TrueUUID' and trueuuid['version'] == '1.3.1', 'wrong TrueUUID fork/version'
    assert trueuuid['installTargets'] == ['client', 'server'], 'TrueUUID must remain installed on both sides'
    assert lock['mc_versions'] == upstream['mc_versions'] and lock['loaders'] == upstream['loaders'], 'Minecraft/loader drift'
    actual = {project_key(p): p for p in lock['projects']}
    expected = {project_key(p): p for p in upstream['projects']}
    assert len(actual) == len(lock['projects']), 'duplicate provider project'
    custom_keys = set()
    for mod in managed['mods']:
        repository = mod['repository']
        custom_keys.add((('modrinth', repository.split(':', 1)[1]),) if repository.startswith('modrinth:') else (('github', repository),))
    removed = {(('curseforge', 'create-horse-power'), ('modrinth', 'create-horse-power'))}
    assert actual.keys() - expected.keys() == custom_keys, 'unexpected added projects or missing custom mods'
    assert expected.keys() - actual.keys() == removed, 'unexpected upstream project removal'
    for key in actual.keys() & expected.keys():
        assert artifact_signature(actual[key]) == artifact_signature(expected[key]), f'upstream artifact drift: {key}'
    custom_lang = {key: value for key, value in previous_lang.items() if old_lang.get(key) != value}
    assert len(custom_lang) == 73 and translations == custom_lang, 'custom material names lost or obsolete upstream translations restored'


def validate_base_installation(installation, release, manifest, markers):
    expected = f'.nstut-tfg-base-{BASE}'
    assert installation == {'schemaVersion': 1, 'baseRef': BASE, 'requiredMarker': expected}, 'invalid base-installation contract'
    assert release['baseRef'] == BASE, 'release base mismatch'
    assert expected in manifest['requiredPaths'], 'overlay can be applied to an old base'
    for marker in markers:
        assert marker == {'baseRef': BASE, 'upstreamCommit': '32ba9f19d60bfc5b4148888fc84e50316b2b0fed'}, 'missing or wrong packaged base marker'
    assert len(markers) == 2, 'client and server markers required'


def validate_base_downloads(migration, managed):
    assert migration['baseRef'] == BASE and migration['sourceBaseRef'] == '0.13.15', 'wrong migration source/target base'
    for target in migration['targets'].values():
        for download in target['downloads']:
            assert not any(fnmatch.fnmatchcase(download['path'], pattern)
                           for mod in managed['mods'] for pattern in mod['cleanupPatterns']), \
                'base migration must not reinstall an overlay-owned mod: ' + download['path']


def main():
    validate(load('pakku-lock.json'), load('nstut/managed-mods.json'), load('kubejs/assets/tfg/lang/en_us.json'),
             historical(BASE, 'pakku-lock.json'), historical(PREVIOUS, 'nstut/managed-mods.json'),
             historical(PREVIOUS, 'kubejs/assets/tfg/lang/en_us.json'), historical('0.13.10', 'kubejs/assets/tfg/lang/en_us.json'))
    validate_base_installation(load('nstut/base-installation.json'), load('nstut/release.json'), load('nstut/modpack-manager.patch.json'),
                              [load(f'.pakku/{side}-overrides/.nstut-tfg-base-{BASE}') for side in ('client', 'server')])
    validate_base_downloads(load('nstut/base-migration.json'), load('nstut/managed-mods.json'))
    print('Upstream 0.13.17 migration passed: exact upstream pins, 16 custom mods, reviewed custom upgrades and 73 custom translations retained')


if __name__ == '__main__':
    main()
