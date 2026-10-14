#!/usr/bin/env node
"use strict";

/**
 * Execute the two mafic-slurry recipe declarations with a minimal KubeJS-style
 * builder. This catches recipe-DSL argument/registration regressions without
 * launching Forge; the Python renewable validator separately checks economics,
 * recipe-map I/O ceilings and the liquefaction source.
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..", "..");
const recipes = fs.readFileSync(
    path.join(root, "kubejs/server_scripts/tfg/ores_and_materials/recipes.renewable_ores.js"),
    "utf8",
);

function captureRecipe(type, id, tier, nominalEUt) {
    const declaration = "event.recipes.gtceu." + type + "('" + id + "')";
    const terminator = ".EUt(" + tier + ");";
    assert.equal(recipes.split(declaration).length, 2, id + ": must be declared once");

    const start = recipes.indexOf(declaration);
    const ending = recipes.indexOf(terminator, start);
    assert(ending > start, id + ": missing " + terminator);
    const code = recipes.slice(start, ending + terminator.length);

    const calls = [];
    const builder = {};
    for (const method of ["itemInputs", "inputFluids", "outputFluids", "duration", "EUt"]) {
        builder[method] = (...args) => {
            calls.push({ method, args });
            return builder;
        };
    }

    const event = {
        recipes: {
            gtceu: {
                [type]: recipeId => {
                    calls.push({ method: type, args: [recipeId] });
                    return builder;
                },
            },
        },
    };
    const Fluid = {
        of: (fluidId, amount) => ({ id: fluidId, amount }),
    };
    vm.runInNewContext(code, { event, Fluid, LV: 30, MV: 120 }, { timeout: 1000 });

    // Cross-VM objects have different prototypes; compare plain JSON values.
    const actual = JSON.parse(JSON.stringify(calls));
    assert.deepEqual(actual.at(-1), { method: "EUt", args: [nominalEUt] });
    return actual;
}

assert.deepEqual(
    captureRecipe("mixer", "tfg:lv_renewable_iron_mafic_slurry", "LV", 30),
    [
        { method: "mixer", args: ["tfg:lv_renewable_iron_mafic_slurry"] },
        { method: "itemInputs", args: ["16x tfg:igneous_mafic_dust"] },
        { method: "inputFluids", args: [{ id: "minecraft:water", amount: 8000 }] },
        { method: "outputFluids", args: [{ id: "tfg:mafic_mineral_slurry", amount: 8000 }] },
        { method: "duration", args: [300] },
        { method: "EUt", args: [30] },
    ],
);

assert.deepEqual(
    captureRecipe("chemical_reactor", "tfg:mv_pressurized_mafic_mineral_slurry", "MV", 120),
    [
        { method: "chemical_reactor", args: ["tfg:mv_pressurized_mafic_mineral_slurry"] },
        {
            method: "inputFluids",
            args: [
                { id: "tfg:igneous_mafic", amount: 1728 },
                { id: "minecraft:water", amount: 8000 },
            ],
        },
        { method: "outputFluids", args: [{ id: "tfg:mafic_mineral_slurry", amount: 8000 }] },
        { method: "duration", args: [160] },
        { method: "EUt", args: [120] },
    ],
);

assert.equal(3 * (16 * 144), 4 * 1728, "tower output must exactly feed MV batches");
console.log("Mafic slurry LV/MV recipe-builder validation passed");
