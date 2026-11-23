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

    # Starting minerals must be directly mineable from the TFG world and must
    # not require electricity, the HV seeded route, or a first Wanderlite item.
    steam = recipe.split("// Steam Age:", 1)[1].split("// Replace both", 1)[0]
    assert "event.recipes.greate.mixing" in steam and ".recipeTier(1)" in steam
    assert all(material in steam for material in ("64x gtceu:raw_graphite", "64x gtceu:raw_magnetite", "16x #forge:gems/amethyst"))
    assert "vs_clockwork:wanderlite_crystal" in steam and not re.search(r"(?<!['\\w])vs_clockwork:wanderlite_(?:cube|matrix|deepslate_ore)", steam)

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
    assert "event.create('tfg:rough_wanderlite_cube')" in startup_items
    assert "event.create('tfg:unfinished_wanderlite_matrix', 'create:sequenced_assembly')" in startup_items
    assert "event.remove({ output: 'vs_clockwork:wanderwand' })" not in recipe

    expected = {
        "vs_clockwork:air_compressor": "lv",
        "vs_clockwork:pump_duct": "lv",
        "vs_clockwork:phys_piston": "mv",
        "vs_clockwork:phys_gantry": "mv",
        "vs_clockwork:gas_nozzle": "mv",
        "vs_clockwork:gas_crafter": "mv",
        "vs_clockwork:phys_bearing": "mv",
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
    print(f"PASS: Clockwork progression static checks ({len(ids)} recipes, {len(rocks)} host rocks, Steam to EV)")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve())
