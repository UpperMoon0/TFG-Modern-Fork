#!/usr/bin/env python3
"""Static acceptance checks for TFG's Clockwork progression.

Usage: python3 nstut/tools/validate-clockwork-progression.py [repo-root]
This deliberately does not claim modded recipe registration or worldgen success;
those require an isolated Forge + KubeJS integration test.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main(root: Path) -> None:
    recipe = (root / "kubejs/server_scripts/tfg/recipes.clockwork_progression.js").read_text(encoding="utf-8")
    entry = (root / "kubejs/server_scripts/tfg/recipes.js").read_text(encoding="utf-8")
    tags = (root / "kubejs/server_scripts/tfg/tags.js").read_text(encoding="utf-8")
    cfg = json.loads((root / "kubejs/data/tfg/worldgen/configured_feature/earth/vein/deep_wanderlite.json").read_text(encoding="utf-8"))
    placed = json.loads((root / "kubejs/data/tfg/worldgen/placed_feature/earth/vein/deep_wanderlite.json").read_text(encoding="utf-8"))

    assert "registerTFGClockworkProgressionRecipes(event)" in entry, "KubeJS recipes function is not called"
    assert "if (!Platform.isLoaded('vs_clockwork')) return;" in recipe, "Optional-mod guard missing"
    assert "event.add('tfc:in_biome/veins', 'tfg:earth/vein/deep_wanderlite')" in tags, "TFC worldgen vein tag missing"
    assert "if (Platform.isLoaded('vs_clockwork'))" in tags, "Worldgen optional-mod guard missing"

    assert cfg["type"] == "tfc:disc_vein", "Should use TFG's established TFC vein feature"
    c = cfg["config"]
    assert c["min_y"] == -60 and c["max_y"] == -24 and c["rarity"] == 420, "Depth or rarity drifted"
    rocks = {next(iter(b["replace"])) for b in c["blocks"]}
    expected_rocks = {
        "gabbro", "granite", "diorite", "rhyolite", "basalt", "andesite", "dacite",
        "shale", "claystone", "limestone", "conglomerate", "dolomite", "chert",
        "chalk", "quartzite", "slate", "phyllite", "schist", "gneiss", "marble",
    }
    assert rocks == {f"tfc:rock/raw/{rock}" for rock in expected_rocks}
    assert all(b["with"] == [{"block": "vs_clockwork:wanderlite_deepslate_ore", "weight": 1}] for b in c["blocks"])
    assert placed["feature"] == "tfg:earth/vein/deep_wanderlite"

    # The Steam Greate mixer accepts nine individually consumed items per
    # operation, not quantity-prefixed stacks. Sixteen batches and a 4x4
    # mechanical craft consume 64 graphite, 64 magnetite, 16 amethyst.
    # No HV materials, prior Wanderlite seed or electricity may enter.
    steam = recipe.split("// Steam recovery stays", 1)[1].split("// Steam-era precision", 1)[0]
    assert "event.recipes.greate.mixing('tfg:wanderlite_trace'" in steam
    assert ".recipeTier(1)" in steam
    assert steam.count("'gtceu:raw_graphite'") == 4
    assert steam.count("'tfc:ore/normal_magnetite'") == 4
    assert steam.count("'#forge:gems/amethyst'") == 1
    assert "'64x " not in steam and "'16x " not in steam
    assert "event.recipes.createMechanicalCrafting('vs_clockwork:wanderlite_crystal'" in steam
    assert "'TTTT', 'TTTT', 'TTTT', 'TTTT'" in steam
    assert "T: 'tfg:wanderlite_trace'" in steam
    assert not re.search(r"(?<!['\\w])vs_clockwork:wanderlite_(?:cube|matrix|deepslate_ore)", steam)

    # Neither the base recipe nor its MV-casing TFG Skies override should
    # survive the recipe removal. Steam assembly still needs a real seed.
    assert "event.remove({ output: 'vs_clockwork:physics_infuser' })" in recipe
    infuser = recipe.split("event.shaped('vs_clockwork:physics_infuser'", 1)[1].split("}).id(", 1)[0]
    assert "vs_clockwork:wanderlite_matrix" in infuser
    assert "gtceu:mv_machine_casing" not in infuser
    assert "#forge:double_plates/wrought_iron" in infuser
    assert "create:brass_casing" in infuser
    assert "event.remove({ output: 'vs_clockwork:wanderlite_cube' })" in recipe
    assert "tfg:rough_wanderlite_cube" in recipe
    assert "tfg:clockwork/steam/polish_wanderlite_cube" in recipe
    assert "event.remove({ output: 'vs_clockwork:wanderlite_matrix' })" in recipe
    assert "tfg:unfinished_wanderlite_matrix" in recipe
    assert "tfg:clockwork/steam/precision_wanderlite_matrix" in recipe
    assert "tfg:clockwork/lv/form_wanderlite_matrix" in recipe
    startup_items = (root / "kubejs/startup_scripts/tfg/items.js").read_text(encoding="utf-8")
    assert "event.create('tfg:wanderlite_trace')" in startup_items
    assert "event.create('tfg:rough_wanderlite_cube')" in startup_items
    assert "event.create('tfg:unfinished_wanderlite_matrix', 'create:sequenced_assembly')" in startup_items
    assert "event.remove({ output: 'vs_clockwork:wanderwand' })" not in recipe

    expected = {
        "vs_clockwork:air_compressor": "steam",
        "vs_clockwork:pump_duct": "steam",
        "vs_clockwork:smart_flap_bearing": "lv",
        "vs_clockwork:copter_bearing": "mv",
        "vs_clockwork:gas_nozzle": "steam",
        "vs_clockwork:gas_crafter": "lv",
        "vs_clockwork:phys_bearing": "lv",
        "vs_clockwork:gimbal_bearing": "mv",
        "vs_clockwork:gyro": "mv",
        "vs_clockwork:wanderglass": "mv",
        "vs_clockwork:gas_thruster": "hv",
        "vs_clockwork:gravitron": "ev",
    }
    for item, tier in expected.items():
        assert f"event.remove({{ output: '{item}' }})" in recipe, f"ungated native recipe: {item}"
        assert re.search(rf"tfg:clockwork/{tier}/[a-z_]+", recipe), f"missing {tier} recipes"
    assert "gtceu:lv_electric_motor" in recipe
    # GTCEu's lookup trie distinguishes ingredient identities, not only
    # stack quantities. Both MV bearings must not share the same item-key set.
    phys = recipe.split("assembler('tfg:clockwork/lv/physics_bearing')", 1)[1].split(".itemOutputs(", 1)[0]
    gimbal = recipe.split("assembler('tfg:clockwork/mv/gimbal_bearing')", 1)[1].split(".itemOutputs(", 1)[0]
    assert "'create:turntable'" in phys and "'create:brass_casing'" not in phys
    assert "'create:brass_casing'" in gimbal and "'create:turntable'" not in gimbal
    assert "gtceu:mv_electric_motor" in recipe
    assert "gtceu:hv_electric_motor" in recipe
    assert "gtceu:ev_electric_motor" in recipe

    ids = re.findall(r"tfg:clockwork/((?:steam|lv|mv|hv|ev)/[a-z_]+)", recipe)
    assert len(ids) >= 18 and len(ids) == len(set(ids)), "duplicate/insufficient recipe IDs"
    assert "2x #forge:plates/brass" in recipe
    assert "#forge:small_gears/brass" in recipe
    assert "loops(2)" in recipe
    # Steam spends 128 finite mined ore items for one crystal. HV uses 24
    # renewable rock dusts for one ore (about 1.75 crystals); its energy
    # investment is justified by much lower recurring material consumption.
    assert 64 + 64 >= 8 * 24 / 1.75
    assert "event.remove({ output: 'vs_clockwork:juryrigged_propeller_bearing' })" not in recipe
    assert "event.remove({ output: 'vs_clockwork:wanderwand' })" not in recipe
    validate_native_compatibility(root, recipe)
    print(f"PASS: Clockwork progression static checks ({len(ids)} recipes, {len(rocks)} host rocks, Steam to EV)")


def validate_native_compatibility(root: Path, recipe: str) -> None:
    native = (root / "kubejs/server_scripts/tfg/recipes.clockwork_native_compatibility.js").read_text()
    audit = json.loads((root / "nstut/tools/fixtures/clockwork-native-recipe-audit.json").read_text())
    rows = {}
    for line in native.splitlines():
        if line.strip().startswith('["'):
            key, data = json.loads(line.strip().rstrip(","))
            assert key not in rows, f"duplicate override: {key}"
            rows[key] = data
    assert audit["version"] == "0.5.7.1" and audit["originalRecipeCount"] == 95
    assert set(rows) == set(audit["compatReplacements"])
    assert "registerTFGClockworkNativeCompatibility(event)" in recipe
    removed = set()
    removed_patterns = []
    for path in (root / "config/reliable_remover").glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        for rule in data if isinstance(data, list) else [data]:
            if isinstance(rule, dict) and rule.get("action") == "remove":
                removed.update(rule.get("items", []))
                if "pattern" in rule:
                    pattern = rule["pattern"]
                    assert pattern.startswith("/") and pattern.endswith("/"), pattern
                    removed_patterns.append(re.compile(pattern[1:-1]))
    # TFG also removes recipes for hidden but registered vanilla items.
    constants = (root / "kubejs/startup_scripts/minecraft/constants.js").read_text()
    hidden = constants.split("global.MINECRAFT_HIDED_ITEMS = [", 1)[1].split("];", 1)[0]
    removed.update(re.findall(r"""['"](minecraft:[^'"]+)['"]""", hidden))

    def unavailable(items):
        return {item for item in items if item in removed or
                any(pattern.fullmatch(item) for pattern in removed_patterns)}

    def refs(value):
        if isinstance(value, dict):
            if isinstance(value.get("item"), str):
                yield value["item"]
            for v in value.values():
                yield from refs(v)
        elif isinstance(value, list):
            for v in value:
                yield from refs(v)

    for key, original in audit["originalItemReferences"].items():
        if key in audit["replacedByProgression"]:
            continue
        actual = set(refs(rows[key])) if key in rows else set(original)
        assert not unavailable(actual), f"{key} uses removed items: {unavailable(actual)}"
    assert "create:steam_engine" not in removed
    assert "create:shaft" in removed, "Do not restore untiered shafts"
    assert "greate:steel_shaft" in recipe
    assert "tfg:clockwork/steam/gas_engine_piston" in recipe
    assert "Platform.isLoaded('clockworkcompat')" in recipe
    for name in ("air_compressor", "pump_duct", "gas_nozzle"):
        block = recipe.split(f"event.shaped('vs_clockwork:{name}'", 1)[1].split("}).id(", 1)[0]
        assert "gtceu:lv_" not in block and "gtceu:mv_" not in block, name
        assert "vs_clockwork:duct" in block
    for name in ("physics_bearing", "smart_flap_bearing", "gas_crafter"):
        block = recipe.split(f"assembler('tfg:clockwork/lv/{name}')", 1)[1].split(".EUt(", 1)
        assert "gtceu:mv_" not in block[0] and block[1].startswith("LV)")
    assert rows["crafting/pneumatics/gas_heater"]["key"]["B"]["item"] == "create:blaze_burner"
    assert rows["gas_crafting/phlogiston"]["requirements"]["kelvin:min_temperature"] <= 800
    assert rows["gas_crafting/methane_reforming"]["requirements"]["kelvin:min_temperature"] <= 800
    assert rows["gas_crafting/vitriol_awkward"]["ingredients"][0]["fluid"] == "gtceu:sulfuric_acid"
    assert rows["gas_crafting/vitriol_thick"] is None
    assert rows["sequenced_assembly/universal_shaft_item"]["ingredient"]["item"] == "greate:steel_shaft"
    print(f"PASS: {len(audit['originalItemReferences'])} native Clockwork recipe references audited, {len(rows)} compatibility overrides")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve())
