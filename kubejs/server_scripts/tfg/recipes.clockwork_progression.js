// priority: 0
"use strict";

/**
 * Clockwork's ship-assembly capability begins in Steam Age. More capable
 * mechanisms follow TFG's electrical progression; renewable Wanderlite
 * remains the independent HV chain in PR #95.
 *
 * Keep the first-crystal route independent of existing Wanderlite: already
 * explored worlds cannot receive new underground ore veins retroactively.
 */
function registerTFGClockworkProgressionRecipes(event) {
    if (!Platform.isLoaded('vs_clockwork')) return;

    const LV = GTValues.VA[GTValues.LV];
    const MV = GTValues.VA[GTValues.MV];
    const HV = GTValues.VA[GTValues.HV];
    const EV = GTValues.VA[GTValues.EV];

    // Steam Age: trace-bearing graphite/magnetite must be mined, not synthesized.
    // The deliberately expensive first-crystal fallback also serves old chunks.
    // The deep Wanderlite veins are the preferred exploration path in new chunks.
    event.recipes.greate.mixing('vs_clockwork:wanderlite_crystal', [
        '16x gtceu:raw_graphite',
        '8x gtceu:raw_magnetite',
        '4x minecraft:amethyst_shard'
    ])
        .recipeTier(1)
        .id('tfg:clockwork/steam/wanderlite_trace_recovery');

    // Replace both the base recipe and Clockwork's optional TFG Skies override,
    // which requires an MV casing and prevents the first Steam Age ship.
    // The Create machinery needed for a Wanderwand already appears in Steam quests.
    event.remove({ output: 'vs_clockwork:physics_infuser' });
    event.shaped('vs_clockwork:physics_infuser', [
        'BPB',
        'CMC',
        'BPB'
    ], {
        B: '#forge:plates/brass',
        P: '#forge:double_plates/wrought_iron',
        C: 'create:brass_casing',
        M: 'vs_clockwork:wanderlite_matrix'
    }).id('tfg:clockwork/steam/physics_infuser');

    // Steam-era Create polishing/pressing and Wanderwand assembly deliberately
    // remain available. Electric industry provides a faster automated route.
    event.recipes.gtceu.lathe('tfg:clockwork/lv/precision_wanderlite_cube')
        .itemInputs('vs_clockwork:wanderlite_crystal')
        .itemOutputs('vs_clockwork:wanderlite_cube')
        .duration(100)
        .EUt(LV);

    // These machines are useful but not necessary for a physics body.
    event.remove({ output: 'vs_clockwork:air_compressor' });
    event.recipes.gtceu.assembler('tfg:clockwork/lv/air_compressor')
        .itemInputs(
            'gtceu:lv_electric_motor',
            'gtceu:lv_electric_pump',
            '2x #forge:plates/steel',
            'vs_clockwork:duct'
        )
        .itemOutputs('vs_clockwork:air_compressor')
        .duration(200)
        .EUt(LV);

    // MV: properly stabilized, motorized bearings and inertial control.
    // A primitive hull can still be assembled without any of these.
    event.remove({ output: 'vs_clockwork:phys_bearing' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/physics_bearing')
        .itemInputs(
            'vs_clockwork:wanderlite_matrix',
            'gtceu:mv_electric_motor',
            'gtceu:steel_rotor',
            'create:brass_casing'
        )
        .itemOutputs('vs_clockwork:phys_bearing')
        .duration(300)
        .EUt(MV);

    event.remove({ output: 'vs_clockwork:gimbal_bearing' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/gimbal_bearing')
        .itemInputs(
            'vs_clockwork:wanderlite_matrix',
            '2x gtceu:mv_electric_motor',
            '2x gtceu:steel_rotor',
            'create:brass_casing'
        )
        .itemOutputs('vs_clockwork:gimbal_bearing')
        .duration(400)
        .EUt(MV);

    event.remove({ output: 'vs_clockwork:gyro' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/gyro')
        .itemInputs(
            'vs_clockwork:wanderlite_matrix',
            'gtceu:mv_sensor',
            'gtceu:steel_rotor',
            'create:flywheel'
        )
        .itemOutputs('vs_clockwork:gyro')
        .duration(300)
        .EUt(MV);

    // MV: advanced optics from a refined Wanderlite Crystal, not 8 plain
    // glass blocks instantly converted on a crafting table.
    event.remove({ output: 'vs_clockwork:wanderglass' });
    event.recipes.gtceu.autoclave('tfg:clockwork/mv/wanderglass')
        .itemInputs('8x minecraft:glass', 'vs_clockwork:wanderlite_crystal')
        .inputFluids(Fluid.of('gtceu:distilled_water', 1000))
        .itemOutputs('8x vs_clockwork:wanderglass')
        .duration(300)
        .EUt(MV);

    // HV: genuinely industrial propulsion; low-tech sail/propeller hardware
    // is still available for Steam Age ships.
    event.remove({ output: 'vs_clockwork:gas_thruster' });
    event.recipes.gtceu.assembler('tfg:clockwork/hv/gas_thruster')
        .itemInputs(
            'gtceu:hv_electric_motor',
            'gtceu:stainless_steel_rotor',
            'vs_clockwork:gas_nozzle',
            'vs_clockwork:heat_exchanger'
        )
        .inputFluids(Fluid.of('gtceu:lubricant', 250))
        .itemOutputs('vs_clockwork:gas_thruster')
        .duration(600)
        .EUt(HV);

    // EV: advanced manipulation of other physics bodies.
    event.remove({ output: 'vs_clockwork:gravitron' });
    event.recipes.gtceu.assembler('tfg:clockwork/ev/gravitron')
        .itemInputs(
            'vs_clockwork:wanderlite_matrix',
            'gtceu:ev_sensor',
            'gtceu:ev_electric_motor',
            'gtceu:titanium_frame'
        )
        .itemOutputs('vs_clockwork:gravitron')
        .duration(800)
        .EUt(EV);
}
