#!/usr/bin/env python3
"""Protect the upstream upgrade and the previously released custom overlay."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = 'nstut-0.13.10.33'
BASE = '0.13.12'


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
    assert managed['mods'] == previous_managed['mods'], 'custom managed artifacts changed during base migration'
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


def main():
    validate(load('pakku-lock.json'), load('nstut/managed-mods.json'), load('kubejs/assets/tfg/lang/en_us.json'),
             historical(BASE, 'pakku-lock.json'), historical(PREVIOUS, 'nstut/managed-mods.json'),
             historical(PREVIOUS, 'kubejs/assets/tfg/lang/en_us.json'), historical('0.13.10', 'kubejs/assets/tfg/lang/en_us.json'))
    print('Upstream migration passed: upstream artifact pins and all 15 custom mods preserved; 73 custom translations retained')


if __name__ == '__main__':
    main()
