#!/usr/bin/env python3
"""Validate the immutable 0.13.19 upstream migration and NsTut overlay pins.

The 0.13.19 update must retain every official project unchanged, all existing
managed mods, and only the reviewed extra projects from the staging candidate.
"""
import fnmatch
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = '0.13.19'
PREVIOUS_BASE = '0.13.18'
PREVIOUS = 'nstut-0.13.18.2'
PUBLISHED_19_SOURCE = '0b1a607e6f0252d8ace7da90fdf18594103b9069'
CHUNKY_KEY = (('curseforge', 'chunky-pregenerator-forge'), ('modrinth', 'chunky'))
UPSTREAM_COMMIT = '065edebfa6196056767c3484648286964b949536'
REVIEWED_CANDIDATE = '8aa1e56cb321be92af0f58348116ba828fe5b5e7'
FORK_ADDITIONS = {
    (('curseforge', 'kelvin-vs'),),
    (('modrinth', 'create-clockwork'),),
    (('modrinth', 'distanthorizons'),),
    (('modrinth', 'extra-gauges'),),
    (('modrinth', 'foodvariations'),),
    (('modrinth', 'littletiles'),),
    (('modrinth', 'minecraft-comes-alive-reborn'),),
    (('modrinth', 'valkyrien-skies'),),
}
REMOVED_UPSTREAM = {
    (('curseforge', 'additional-placements'), ('modrinth', 'additional-placements')),
    (('curseforge', 'create-horse-power'), ('modrinth', 'create-horse-power')),
    (('curseforge', 'ldlib'), ('modrinth', 'ldlib')),
    CHUNKY_KEY, # DH 3.3.3 calls ChunkyProvider before initialization and crashes world boot
}

def historical(ref, path):
    return json.loads(subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{ref}:{path}']))

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))

def project_key(project):
    return tuple(sorted(project['slug'].items()))

def validate(lock, managed, translations, upstream, previous_managed, previous_lang, old_lang):
    assert managed['base']['ref'] == BASE, 'wrong managed-mod base'
    release = load('nstut/release.json')
    assert release['baseRef'] == BASE and release['branch'] == 'nstut/'+BASE
    assert release['overlayVersion'] == BASE+'-nstut.3' and release['sourceRef'] == 'nstut-0.13.19.3'
    audit = load('nstut/custom-mod-audit-0.13.19.3.json')
    pin_keys = ('id','repository','version','fileName','url','sha256','installTargets')
    pins = [{k:m[k] for k in pin_keys if k in m} for m in managed['mods']]
    assert pins == audit['pins'] and audit['sourceRef'] == release['sourceRef'] and audit['baseRef'] == BASE
    assert managed['mods'] == previous_managed['mods'], 'existing immutable NsTut custom mods drifted'
    assert translations == previous_lang, 'fork translations changed from promoted 0.13.18'
    assert lock['mc_versions'] == upstream['mc_versions'] == ['1.20.1']
    assert lock['loaders'] == upstream['loaders']
    actual = {project_key(p): p for p in lock['projects']}
    expected = {project_key(p): p for p in upstream['projects']}
    assert len(actual) == len(lock['projects']) == 298, 'duplicate or missing locked projects'
    assert len(expected) == len(upstream['projects']), 'duplicate official project'
    custom = set()
    for m in managed['mods']:
        repo = m['repository']
        custom.add((('modrinth', repo.split(':',1)[1]),) if repo.startswith('modrinth:') else (('github',repo),))
    assert actual.keys() - expected.keys() == custom | FORK_ADDITIONS, 'unexpected fork project additions or removals'
    assert expected.keys() - actual.keys() == REMOVED_UPSTREAM, 'missing unexpected official projects'
    for key in actual.keys() & expected.keys():
        assert actual[key] == expected[key], f'official 0.13.19 project pin drift: {key}'
    reviewed = historical(REVIEWED_CANDIDATE, 'pakku-lock.json')
    retained_reviewed = [p for p in reviewed['projects'] if project_key(p) != CHUNKY_KEY]
    assert lock['projects'] == retained_reviewed, 'candidate pin drift other than reviewed Chunky exclusion'
    assert all(project_key(p) != CHUNKY_KEY for p in lock['projects']), 'DH-incompatible Chunky must not ship'
    for slug in ('create-clockwork','distanthorizons','minecraft-comes-alive-reborn','valkyrien-skies'):
        matches = [p for p in lock['projects'] if p['slug'].get('modrinth')==slug]
        assert len(matches) == 1 and matches[0]['side'] == 'BOTH', f'{slug} must be both-side'
    kelvin = [p for p in lock['projects'] if p['slug'].get('curseforge')=='kelvin-vs']
    assert len(kelvin)==1 and kelvin[0]['side']=='BOTH'

def validate_base_installation(installation, release, manifest, markers):
    marker = f'.nstut-tfg-base-{BASE}'
    assert installation == {'schemaVersion':1,'baseRef':BASE,'requiredMarker':marker}
    assert release['baseRef'] == BASE and marker in manifest['requiredPaths']
    assert len(markers)==2 and all(m=={'baseRef':BASE,'upstreamCommit':UPSTREAM_COMMIT} for m in markers)

def validate_base_downloads(migration, managed):
    assert migration['baseRef']==BASE and migration['sourceBaseRef']==PREVIOUS_BASE
    assert set(migration['targets'])=={'server','client'}
    published = historical(PUBLISHED_19_SOURCE, 'nstut/base-migration.json')
    for side,target in migration['targets'].items():
        old_target = published['targets'][side]
        assert target['archive'] == old_target['archive'], 'immutable .19 base archive changed'
        assert target['downloads'] == [d for d in old_target['downloads'] if d['path'] != 'mods/Chunky-1.3.146.jar'], 'only Chunky download may be excluded'
        assert not any('chunky' in d['path'].lower() for d in target['downloads']), 'DH-incompatible Chunky provider still present'
        a=target['archive']
        assert a['fileName']==f'tfg-base-{BASE}-{side}.zip'
        assert a['url'].startswith(f'https://github.com/UpperMoon0/TFG-Modern-Fork/releases/download/nstut-base-{BASE}/')
        assert len(a['sha256'])==64
        assert target['marker']==f'.nstut-tfg-base-{BASE}'
        assert json.loads(target['markerContent'])=={'baseRef':BASE,'upstreamCommit':UPSTREAM_COMMIT}
        for download in target['downloads']:
            assert len(download.get('sha256',''))==64 and download.get('url','').startswith('https://')
            assert not any(fnmatch.fnmatchcase(download['path'],p)
                           for mod in managed['mods'] for p in mod['cleanupPatterns']), 'base migration would reinstall custom mod: '+download['path']

def main():
    validate(load('pakku-lock.json'),load('nstut/managed-mods.json'),load('kubejs/assets/tfg/lang/en_us.json'),
             historical(BASE,'pakku-lock.json'),historical(PREVIOUS,'nstut/managed-mods.json'),
             historical(PREVIOUS,'kubejs/assets/tfg/lang/en_us.json'),historical('0.13.10','kubejs/assets/tfg/lang/en_us.json'))
    validate_base_installation(load('nstut/base-installation.json'),load('nstut/release.json'),load('nstut/modpack-manager.patch.json'),
                               [load(f'.pakku/{side}-overrides/.nstut-tfg-base-{BASE}') for side in ('client','server')])
    validate_base_downloads(load('nstut/base-migration.json'),load('nstut/managed-mods.json'))
    manifest = load('nstut/modpack-manager.patch.json')
    assert manifest['version'] == BASE+'-nstut.3'
    assert not any('chunky' in x.get('fileName','').lower() for x in manifest['artifacts']), 'Chunky reinstall artifact remains'
    assert not any(x.get('type')=='installFile' and 'chunky' in x.get('destination','').lower() for x in manifest['operations']), 'Chunky reinstall operation remains'
    cleanup = [x for x in manifest['operations'] if x.get('type')=='removeMatching' and x.get('pattern')=='mods/Chunky-*.jar']
    assert cleanup == [{'type':'removeMatching','pattern':'mods/Chunky-*.jar','targets':['client','server']}], 'required prior-0.13.19 cleanup not pinned'
    assert all(any(x.get('type')=='installFile' and 'DistantHorizons-' in x.get('destination','') and side in x.get('targets',[]) for x in manifest['operations']) for side in ('client','server')), 'DH must remain on both sides'
    print('Upstream 0.13.19: all retained official pins, minus one DH-incompatible Chunky; immutable mods, expanded both-side pins and base archive/rollback contracts verified')

if __name__=='__main__': main()
