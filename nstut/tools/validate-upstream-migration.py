#!/usr/bin/env python3
"""Validate full TFG 0.13.18 upstream ancestry, immutable custom pins and migration."""
import json
import fnmatch
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = 'nstut-0.13.17.5'
BASE = '0.13.18'
PREVIOUS_BASE = '0.13.17'
UPSTREAM_COMMIT = 'a51824514af63ada07fcfd162ef85b3b9840c103'


def historical(ref, path):
    return json.loads(subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{ref}:{path}']))


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))


def project_key(project):
    return tuple(sorted(project['slug'].items()))


def artifact_signature(project):
    return {key: project.get(key) for key in ('type', 'side', 'slug', 'id', 'files')}


def validate(lock, managed, translations, upstream, previous_managed, previous_lang, old_lang):
    assert managed['base']['ref'] == BASE, 'wrong declared managed-mod base'
    audit_version = load('nstut/release.json')['sourceRef'].removeprefix('nstut-')
    audit = load(f'nstut/custom-mod-audit-{audit_version}.json')
    pin_keys = ('id', 'repository', 'version', 'fileName', 'url', 'sha256', 'installTargets')
    actual_pins = [{k: mod[k] for k in pin_keys if k in mod} for mod in managed['mods']]
    assert actual_pins == audit['pins'], 'custom managed artifacts differ from reviewed release audit'
    prior = {m['id']: m for m in previous_managed['mods']}
    current = {m['id']: m for m in managed['mods']}
    assert set(current) - set(prior) == {'additional-placements'}, 'unexpected new managed mods'
    assert set(prior) <= set(current), 'previously managed mod was removed'
    changed = {'openui', 'create-precise-controls', 'building-gadgets-extra', 'celestial-nail'}
    assert {mid for mid in prior if current[mid] != prior[mid]} == changed, 'unreviewed change to existing mod pins'
    assert all(current[mid]['repository']==prior[mid]['repository'] for mid in changed), 'modified managed repository identity'
    trueuuid = current['trueuuid']
    assert trueuuid['repository'] == 'UpperMoon0/TrueUUID' and trueuuid['version'] == '1.3.1', 'wrong TrueUUID pin'
    assert trueuuid['installTargets'] == ['client', 'server'], 'TrueUUID must remain both-side'
    assert lock['mc_versions'] == upstream['mc_versions'] and lock['loaders'] == upstream['loaders'], 'Minecraft/loader drift'

    actual = {project_key(p): p for p in lock['projects']}
    expected = {project_key(p): p for p in upstream['projects']}
    assert len(actual) == len(lock['projects']), 'duplicate provider project'
    custom_keys = set()
    for mod in managed['mods']:
        repo = mod['repository']
        custom_keys.add((('modrinth', repo.split(':', 1)[1]),) if repo.startswith('modrinth:') else (('github', repo),))
    removed = {
        (('curseforge', 'create-horse-power'), ('modrinth', 'create-horse-power')),
        (('curseforge', 'ldlib'), ('modrinth', 'ldlib')),
        (('curseforge', 'additional-placements'), ('modrinth', 'additional-placements')),
    }
    assert actual.keys() - expected.keys() == custom_keys, 'unexpected added projects or custom project missing'
    assert expected.keys() - actual.keys() == removed, 'unexpected upstream project replacement/removal'
    for key in actual.keys() & expected.keys():
        assert artifact_signature(actual[key]) == artifact_signature(expected[key]), f'upstream artifact drift: {key}'
    custom_lang = {key: value for key, value in previous_lang.items() if old_lang.get(key) != value}
    assert len(custom_lang) == 73 and translations == custom_lang, 'custom material translations lost or unexpected upstream translations restored'


def validate_base_installation(installation, release, manifest, markers):
    expected = f'.nstut-tfg-base-{BASE}'
    assert installation == {'schemaVersion': 1, 'baseRef': BASE, 'requiredMarker': expected}, 'invalid base-installation contract'
    assert release['baseRef'] == BASE, 'release base mismatch'
    assert expected in manifest['requiredPaths'], 'overlay can be applied to an old base'
    for marker in markers:
        assert marker == {'baseRef': BASE, 'upstreamCommit': UPSTREAM_COMMIT}, 'missing or wrong packaged base marker'
    assert len(markers) == 2, 'client and server markers required'


def validate_base_downloads(migration, managed):
    assert migration['baseRef'] == BASE and migration['sourceBaseRef'] == PREVIOUS_BASE, 'wrong migration source/target base'
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
    print(f"Upstream {BASE} migration passed: exact upstream pins, {len(load('nstut/managed-mods.json')['mods'])} managed mods, reviewed upgrades and 73 custom translations retained")


if __name__ == '__main__':
    main()
