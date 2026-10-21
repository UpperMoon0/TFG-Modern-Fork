"use strict";
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../..');
const context = vm.createContext({global: {}, console});
for (const file of ['kubejs/startup_scripts/createdeco/constants.js',
    'kubejs/startup_scripts/tfg/stone_types/constants.rocks.js',
    'kubejs/server_scripts/tfg/natural_blocks/tags.building_safety.js']) {
    vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, {filename: file});
}
const registry = new Set();
function collect(value) {
    if (typeof value === 'string' && /^[a-z0-9_]+:[a-z0-9_/]+$/.test(value)) registry.add(value);
    else if (value && typeof value === 'object') Object.values(value).forEach(collect);
}
collect(context.global.BIG_ROCK_TABLE);
const natural = ['tfc:rock/raw/marble', 'tfc:rock/raw/gabbro', 'tfc:rock/hardened/marble',
    'tfc:rock/gravel/gabbro', 'tfc:sand/white', 'tfc:dirt/loam', 'gtceu:marble_hematite_ore',
    'tfc:rock/cobble/gabbro', 'tfc:rock/mossy_cobble/marble', 'tfc:rock/cobble/gabbro_stairs'];
const buildings = ['tfc:rock/smooth/marble', 'tfc:rock/smooth/gabbro', 'tfc:rock/smooth/marble_slab',
    'tfc:rock/raw/gabbro_stairs',
    'tfc:rock/bricks/gabbro', 'tfc:rock/cracked_bricks/marble_wall', 'tfc:rock/chiseled/marble',
    'create:cut_diorite', 'create:andesite_pillar', 'gtceu:light_concrete', 'gtceu:dark_concrete',
    'minecraft:white_concrete', 'minecraft:oak_planks', 'minecraft:glass', 'minecraft:terracotta'];
[...natural, ...buildings].forEach(id => registry.add(id));
const affected = ['tfc:can_collapse', 'tfc:can_start_collapse', 'tfc:can_trigger_collapse',
    'tfc:can_landslide', 'tfc:breaks_when_isolated'];
const tags = new Map([
    ['test:inherited', new Set(registry)],
    ['minecraft:planks', new Set(['minecraft:oak_planks'])],
    ['forge:glass', new Set(['minecraft:glass'])],
    ['minecraft:terracotta', new Set(['minecraft:terracotta'])],
]);
affected.forEach(tag => tags.set(tag, new Set(['#test:inherited'])));
function entries(tag) {
    if (!tags.has(tag)) tags.set(tag, new Set());
    return tags.get(tag);
}
function resolve(tag, seen = new Set()) {
    assert(!seen.has(tag), 'tag cycle');
    const next = new Set([...seen, tag]);
    return new Set([...entries(tag)].flatMap(id => id.startsWith('#') ? [...resolve(id.slice(1), next)] : [id]));
}
const event = {
    get: tag => ({getObjectIds: () => ({toArray: () => [...resolve(tag)]})}),
    getElementIds: () => ({toArray: () => [...registry]}),
    removeAll: tag => entries(tag).clear(),
    add(tag, id) {
        if (id.startsWith('/')) {
            const regex = new RegExp(id.slice(1, -1));
            registry.forEach(value => { if (regex.test(value)) entries(tag).add(value); });
        } else {
            assert(registry.has(id), 'invalid registry ID ' + id);
            entries(tag).add(id);
        }
    },
};
context.registerTFGBuildingSafetyTags(event);
for (const tag of affected) {
    const result = resolve(tag);
    buildings.forEach(id => assert(!result.has(id), tag + ' still contains building ' + id));
    natural.forEach(id => assert(result.has(id), tag + ' lost natural terrain ' + id));
}
const before = affected.map(tag => [...resolve(tag)].sort().join('\n'));
context.registerTFGBuildingSafetyTags(event);
assert.deepEqual(affected.map(tag => [...resolve(tag)].sort().join('\n')), before, 'reload changed membership');
const main = fs.readFileSync(path.join(root, 'kubejs/server_scripts/main_server_script.js'), 'utf8');
assert(main.indexOf('registerTFGBuildingSafetyTags(event)') > main.indexOf('registerWABBlockTags(event)'), 'safety must run last');
console.log('Building safety passed: real rock table, nested tags, five collapse/slide/isolation tags, natural terrain and reload stability');
