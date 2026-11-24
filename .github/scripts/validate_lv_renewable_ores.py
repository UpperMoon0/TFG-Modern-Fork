#!/usr/bin/env python3
"""Fail-closed LV regression alongside full multi-tier renewable ore validation.

0.13.18 has 49 audited LV recipes within a 93-recipe multi-tier system.
The old pre-MV/HV 33-recipe validator must not reject intentionally added
Tin/Lead/Redstone paths or silently ignore their downstream waste recovery.
"""
from __future__ import annotations
from pathlib import Path
import re
import runpy

full = runpy.run_path(str(Path(__file__).with_name('validate_renewable_ores.py')))
blocks = full['blocks']
lv = [(machine, ident, body) for machine, ident, body in blocks
      if ident.startswith('tfg:lv_')]
if len(blocks) != 93 or len(lv) != 49:
    raise SystemExit('LV renewable validation failed: full/LV audited recipe count drift')

ids = {ident for _, ident, _ in lv}
if len(ids) != 49:
    raise SystemExit('LV renewable validation failed: duplicated LV recipe IDs')

# The six tier-one mineralization lines must end in Poor Ore, and no output
# may be generated without a mined any-grade mineral discovery seed.
tfc_finals = ('hematite', 'malachite', 'sphalerite', 'cassiterite')
gt_finals = ('redstone', 'galena')
for mineral in (*tfc_finals, *gt_finals):
    ident = f'tfg:lv_renewable_poor_{mineral}'
    found = [(machine, body) for machine, name, body in lv if name == ident]
    if len(found) != 1 or found[0][0] != 'autoclave':
        raise SystemExit(f'LV renewable validation failed: {mineral} mineralizer drift')
    body = found[0][1]
    seed = f".notConsumable('#tfg:renewable_{mineral}_seed')"
    if seed not in body or sum(seed in candidate for _, _, candidate in blocks) != 1:
        raise SystemExit(f'LV renewable validation failed: {mineral} geological seed drift')
    if mineral in tfc_finals and f".itemOutputs('tfc:ore/poor_{mineral}')" not in body:
        raise SystemExit(f'LV renewable validation failed: {mineral} TFC Poor Ore drift')
    if mineral in gt_finals and 'TFGTagPrefix.poorRawOre' not in body:
        raise SystemExit(f'LV renewable validation failed: {mineral} GT Poor Ore drift')

# Do not turn geological poor ore production into direct metal dust minting.
for machine, ident, body in lv:
    for output in re.findall(r'\.itemOutputs\(\s*[\'\"]([^\'\"]+)[\'\"]', body):
        if re.match(r'(?:\d+x\s+)?gtceu:(?:iron|copper|zinc|tin|lead|redstone|galena)_(?:dust|ingot)$', output):
            raise SystemExit(f'LV renewable validation failed: direct metal output in {ident}')

print('LV renewable validation passed: all 93 recipes audited, 49 LV recipes, six geological seed-gated mineralizers')
