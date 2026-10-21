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
            if collapse[key] is not False:
                raise AssertionError(f'{relative}: {key} must be disabled')
        for key in ('collapseTriggerChance', 'collapseFakeTriggerChance',
                    'collapsePropagateChance', 'collapseExplosionPropagateChance'):
            if collapse[key] != 0.0:
                raise AssertionError(f'{relative}: {key} must be zero')
    print('TFC collapses and landslides disabled in both packaged defaults.')


if __name__ == '__main__':
    validate()
