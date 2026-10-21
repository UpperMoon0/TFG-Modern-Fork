#!/usr/bin/env python3
"""Check the separate client and dedicated-server TFC collapse defaults."""
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PATHS = (
    'defaultconfigs/tfc-server.toml',
    '.pakku/server-overrides/defaultconfigs/tfc-server.toml',
)


def validate(root=ROOT):
    for relative in PATHS:
        with (root / relative).open('rb') as stream:
            collapse = tomllib.load(stream)['mechanics']['collapses']
        for key in ('enableBlockCollapsing', 'enableExplosionCollapsing',
                    'enableBlockLandslides', 'enableChiselsStartCollapses'):
            if collapse[key] is not True:
                raise AssertionError(f'{relative}: {key} must be enabled')
        for key, value in {'collapseTriggerChance': 0.1, 'collapseFakeTriggerChance': 0.35,
                           'collapsePropagateChance': 0.55, 'collapseExplosionPropagateChance': 0.3}.items():
            if collapse[key] != value:
                raise AssertionError(f'{relative}: {key} must retain the upstream default {value}')
    print('TFC collapses and landslides enabled with upstream probabilities in both packaged defaults.')


if __name__ == '__main__':
    validate()
