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
UPSTREAM_COMMIT = '065edebfa6196056767c3484648286964b949536'
REVIEWED_CANDIDATE = '8aa1e56cb321be92af0f58348116ba828fe5b5e7'
FORK_ADDITIONS = {
    (('curseforge', 'kelvin-vs'),),
    (('modrinth', 'create-clockwork'),),
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
    # Release construction can advance immutable overlay revisions without
    # rewriting upstream 0.13.19 acceptance invariants for each new tag.
    version_prefix = BASE + '-nstut.'
    assert release['overlayVersion'].startswith(version_prefix), 'unexpected overlay version family'
    suffix = release['overlayVersion'][len(version_prefix):]
    assert suffix.isdecimal() and int(suffix) >= 8, 'overlay revision predates reviewed DH baseline'
    assert release['sourceRef'] == 'nstut-' + BASE + '.' + suffix, 'source ref must match immutable overlay'
    assert load('pakku.json')['version'] == release['overlayVersion'], 'Pakku pack version differs from immutable release'
    audit = load('nstut/custom-mod-audit-' + BASE + '.' + suffix + '.json')
    pin_keys = ('id','repository','version','fileName','url','sha256','installTargets')
    pins = [{k:m[k] for k in pin_keys if k in m} for m in managed['mods']]
    assert pins == audit['pins'] and audit['sourceRef'] == release['sourceRef'] and audit['baseRef'] == BASE
    clockwork = int(suffix) >= 13
    prior_count = len(previous_managed['mods'])
    assert managed['mods'][:prior_count] == previous_managed['mods'], 'existing immutable NsTut custom mods drifted'
    extras = managed['mods'][prior_count:]
    assert [m['id'] for m in extras] == ['distant-horizons'] + (['clockwork-compat'] if clockwork else []), 'unexpected managed additions'
    dh_pin = extras[0]
    if clockwork:
        compat = extras[1]
        assert compat['repository'] == 'UpperMoon0/Clockwork-Compat'
        assert compat['version'] == '0.1.0' and compat['fileName'] == 'clockwork-compat-forge-1.20.1-0.1.0.jar'
        assert compat['sha256'] == 'e844e219b5d5492e9779d1ff02f369c0db39945927bf43f104908f89aa63dbfe'
        assert compat['url'] == 'https://github.com/UpperMoon0/Clockwork-Compat/releases/download/v0.1.0/' + compat['fileName']
        assert compat['installTargets'] == compat['cleanupTargets'] == ['client', 'server']
        assert compat['cleanupPatterns'] == ['mods/clockwork-compat-*.jar']
    # Preserve every migrated translation; permit only reviewed additive overlay keys.
    expected_lang = dict(previous_lang)
    if int(suffix) >= 12:
        additions = {
            'material.tfg.wanderlite_silicate_slurry': 'Wanderlite Silicate Slurry',
            'material.tfg.charged_wanderlite_precursor': 'Charged Wanderlite Precursor',
        }
        assert not additions.keys() & expected_lang.keys(), 'reviewed additions overwrite prior translations'
        expected_lang.update(additions)
    assert translations == expected_lang, 'unreviewed fork translation drift'
    assert lock['mc_versions'] == upstream['mc_versions'] == ['1.20.1']
    assert lock['loaders'] == upstream['loaders']
    actual = {project_key(p): p for p in lock['projects']}
    expected = {project_key(p): p for p in upstream['projects']}
    assert len(actual) == len(lock['projects']) == 299 + int(clockwork), 'duplicate or missing locked projects'
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
    # All reviewed projects are immutable except the one explicit DH provider
    # transition from Modrinth to our published, checksum-verified Forge binary.
    def without_dh(projects):
        return [p for p in projects if p['slug'].get('modrinth') != 'distanthorizons'
                and p['slug'].get('github') not in ('UpperMoon0/DistantHorizons', 'UpperMoon0/Clockwork-Compat')]
    assert without_dh(lock['projects']) == without_dh(reviewed['projects']), 'unrelated Pakku project pin drift since review'
    dh_projects = [p for p in lock['projects'] if p['slug'].get('github') == 'UpperMoon0/DistantHorizons']
    assert len(dh_projects) == 1 and dh_projects[0]['side'] == 'BOTH', 'exactly one both-side DH fork required'
    dh_file = dh_projects[0]['files']
    assert len(dh_file) == 1 and dh_file[0]['file_name'] == dh_pin['fileName'], 'DH fork artifact differs from managed pin'
    assert dh_file[0]['hashes']['sha256'] == dh_pin['sha256'], 'DH lockfile checksum differs from published managed mod'
    assert dh_file[0]['url'] == dh_pin['url'], 'DH lockfile URL differs from published managed mod'
    if clockwork:
        p = actual[(('github', 'UpperMoon0/Clockwork-Compat'),)]
        assert p['side'] == 'BOTH' and len(p['files']) == 1
        f = p['files'][0]
        assert f['file_name'] == compat['fileName'] and f['hashes']['sha256'] == compat['sha256'] and f['url'] == compat['url']
        assert f['id'] == '787007271' and f['parent_id'] == '1470021241' and f['size'] == 8866
    for slug in ('create-clockwork','minecraft-comes-alive-reborn','valkyrien-skies'):
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
    for side,target in migration['targets'].items():
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
    print('Upstream 0.13.19: all 279 official projects, 18 preserved managed mods, verified DH fork and version-gated Clockwork Compat, reviewed extra projects and rollback contracts verified')

if __name__=='__main__': main()
