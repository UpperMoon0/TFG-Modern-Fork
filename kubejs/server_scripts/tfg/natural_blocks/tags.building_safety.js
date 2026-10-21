// priority: 0
"use strict";

// Run after all upstream block-tag registrations. TFC uses separate tags for
// triggering, starting and propagating collapses, plus landslides/isolation.
function registerTFGBuildingSafetyTags(event) {
	const safe = new Set();
	function addForms(forms) {
		if (forms == null) return;
		['block', 'stair', 'slab', 'wall'].forEach(shape => {
			if (forms[shape] != null) safe.add(String(forms[shape]));
		});
		addForms(forms.mossy);
		addForms(forms.cracked);
	}
	Object.values(global.BIG_ROCK_TABLE).forEach(rock => {
		['polished', 'bricks', 'chiseled'].forEach(form => addForms(rock[form]));
		(rock.stonecutting || []).forEach(addForms);
		['pillar', 'pillar2', 'aqueduct', 'support'].forEach(form => {
			if (rock[form] != null) safe.add(String(rock[form]));
		});
		// Slabs, stairs and walls are manufactured; natural raw full blocks stay unstable.
		if (rock.raw != null) ['stair', 'slab', 'wall'].forEach(shape => {
			if (rock.raw[shape] != null) safe.add(String(rock.raw[shape]));
		});
		if (rock.collapsible === false && rock.raw != null) safe.add(String(rock.raw.block));
	});
	['minecraft:planks', 'minecraft:logs', 'minecraft:wooden_slabs', 'minecraft:wooden_stairs',
		'minecraft:stone_bricks', 'forge:stone_bricks', 'forge:glass', 'forge:glass_panes',
		'minecraft:terracotta', 'minecraft:wool', 'tfg:brick_index', 'tfg:brick_slabs',
		'tfg:brick_stairs', 'tfg:brick_walls'].forEach(tag => {
		event.get(tag).getObjectIds().toArray().forEach(id => safe.add(String(id)));
	});
	// Concrete and manufactured timber/glass/metal construction parts are already
	// stable upstream. Include registered variants to protect future tag changes.
	event.add('tfg:collapse_safe_building_blocks', '/.*(?:_concrete|_concrete_slab|_concrete_stairs|_concrete_wall)$/');
	event.get('tfg:collapse_safe_building_blocks').getObjectIds().toArray().forEach(id => safe.add(String(id)));
	const registeredSafe = event.getElementIds().toArray().map(id => String(id)).filter(id => safe.has(id));
	registeredSafe.forEach(id => event.add('tfg:collapse_safe_building_blocks', id));

	// KubeJS 2001.6.5 removes IDs only from direct tag entries. Resolve nested
	// membership first, then rebuild these tags so inherited entries are excluded too.
	const tags = ['tfc:can_collapse', 'tfc:can_start_collapse', 'tfc:can_trigger_collapse',
		'tfc:can_landslide', 'tfc:breaks_when_isolated'];
	const resolved = {};
	tags.forEach(tag => {
		resolved[tag] = event.get(tag).getObjectIds().toArray().map(id => String(id)).filter(id => !safe.has(id));
	});
	tags.forEach(tag => {
		event.removeAll(tag);
		resolved[tag].forEach(id => event.add(tag, id));
	});
	console.info('[TFG building safety] protected ' + registeredSafe.length + ' registered building variants; raw stone and ores retain collapse rules');
	console.info('[TFG building safety audit] ' + JSON.stringify({
		smoothMarbleProtected: registeredSafe.indexOf('tfc:rock/smooth/marble') !== -1,
		smoothGabbroProtected: registeredSafe.indexOf('tfc:rock/smooth/gabbro') !== -1,
		rawMarbleCollapses: resolved['tfc:can_collapse'].indexOf('tfc:rock/raw/marble') !== -1,
		rawGabbroCollapses: resolved['tfc:can_collapse'].indexOf('tfc:rock/raw/gabbro') !== -1,
		cobblestoneSlides: resolved['tfc:can_landslide'].indexOf('tfc:rock/cobble/gabbro') !== -1,
		mossyCobblestoneSlides: resolved['tfc:can_landslide'].indexOf('tfc:rock/mossy_cobble/marble') !== -1
	}));
}
