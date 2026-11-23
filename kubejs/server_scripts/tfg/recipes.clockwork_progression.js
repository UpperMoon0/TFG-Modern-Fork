// priority: 0
"use strict";

/**
 * Clockwork progression for TFG Modern:
 * Steam = expensive bootstrap + mechanical ship fabrication;
 * LV/MV = industrial precision and control;
 * HV/EV = high-energy propulsion and physics.
 *
 * No rare material bootstrap must require a Wanderlite seed or electricity.
 * PR #95 provides efficient, renewable, seeded HV synthesis after discovery.
 */
function registerTFGClockworkProgressionRecipes(event) {
    if (!Platform.isLoaded('vs_clockwork')) return;

    const LV = GTValues.VA[GTValues.LV];
    const MV = GTValues.VA[GTValues.MV];
    const HV = GTValues.VA[GTValues.HV];
    const EV = GTValues.VA[GTValues.EV];

    // Steam Age: straightforward THREE-ingredient one-machine recovery, but
    // consumes 128 nonrenewable RAW ORES and 16 amethyst gems per crystal.
    // It is an expensive first-seed/emergency route, not a cheap HV substitute.
    // By comparison, PR #95 consumes 16 felsic + 8 metamorphic renewable
    // rock dusts, 4 amethysts, 8 redstone, 8 B distilled water, 1 B oxygen,
    // and 1.44 M EU to make 1 ore (~1.75 crystals) using reusable catalysts.
    event.recipes.greate.mixing('vs_clockwork:wanderlite_crystal', [
        '64x gtceu:raw_graphite',
        '64x gtceu:raw_magnetite',
        '16x #forge:gems/amethyst'
    ])
        .recipeTier(1)
        .id('tfg:clockwork/steam/wanderlite_trace_recovery');

    // Steam-era precision cutting and polishing, instead of a single instant
    // sandpaper transformation. LV Lathe provides a faster direct alternative.
    event.remove({ output: 'vs_clockwork:wanderlite_cube' });
    event.custom({
        type: 'create:cutting',
        ingredients: [{ item: 'vs_clockwork:wanderlite_crystal' }],
        results: [{ item: 'tfg:rough_wanderlite_cube' }],
        processingTime: 150
    }).id('tfg:clockwork/steam/cut_rough_wanderlite_cube');

    event.recipes.create.sandpaper_polishing(
        'vs_clockwork:wanderlite_cube', 'tfg:rough_wanderlite_cube'
    ).id('tfg:clockwork/steam/polish_wanderlite_cube');

    // Precision Matrix: each of two Create assembly loops deploys brass
    // plates and a small bronze gear before pressing. This retains a real,
    // pre-electric route with meaningful machinery/material cost.
    event.remove({ output: 'vs_clockwork:wanderlite_matrix' });
    event.recipes.createSequencedAssembly(
        ['vs_clockwork:wanderlite_matrix'],
        'vs_clockwork:wanderlite_cube', [
            event.recipes.createDeploying('tfg:unfinished_wanderlite_matrix',
                ['tfg:unfinished_wanderlite_matrix', '#forge:plates/brass']),
            event.recipes.createDeploying('tfg:unfinished_wanderlite_matrix',
                ['tfg:unfinished_wanderlite_matrix', '#forge:small_gears/brass']),
            event.recipes.createPressing('tfg:unfinished_wanderlite_matrix',
                'tfg:unfinished_wanderlite_matrix')
        ]
    ).transitionalItem('tfg:unfinished_wanderlite_matrix').loops(2)
     .id('tfg:clockwork/steam/precision_wanderlite_matrix');

    // Electric routes save Create assembly operations and brass. They are
    // convenience upgrades, NOT prerequisites for constructing the first ship.
    event.recipes.gtceu.lathe('tfg:clockwork/lv/precision_wanderlite_cube')
        .itemInputs('vs_clockwork:wanderlite_crystal')
        .itemOutputs('vs_clockwork:wanderlite_cube')
        .duration(100).EUt(LV);

    event.recipes.gtceu.forming_press('tfg:clockwork/lv/form_wanderlite_matrix')
        .itemInputs('vs_clockwork:wanderlite_cube', '2x #forge:plates/brass')
        .itemOutputs('vs_clockwork:wanderlite_matrix')
        .duration(160).EUt(LV);

    // TFG Skies' optional infuser has an MV casing. This replacement makes
    // assembly accessible without any electric machine.
    event.remove({ output: 'vs_clockwork:physics_infuser' });
    event.shaped('vs_clockwork:physics_infuser', [
        'BPB', 'CMC', 'BPB'
    ], {
        B: '#forge:plates/brass',
        P: '#forge:double_plates/wrought_iron',
        C: 'create:brass_casing',
        M: 'vs_clockwork:wanderlite_matrix'
    }).id('tfg:clockwork/steam/physics_infuser');

    // Steam pneumatics should use existing infrastructure rather than a
    // near-free 3-copper-sheet recipe. Still fully non-electric.
    event.remove({ output: 'vs_clockwork:steam_generator' });
    event.shaped('vs_clockwork:steam_generator', [
        'PDP', 'EHE', 'PCP'
    ], {
        P: '#forge:plates/copper',
        D: 'vs_clockwork:duct',
        E: '#forge:plates/wrought_iron',
        H: 'vs_clockwork:heat_exchanger',
        C: 'vs_clockwork:coal_burner'
    }).id('tfg:clockwork/steam/steam_generator');

    // LV compressed-air system: an electric pump and motor, rather than
    // iron bars and dried kelp. Ducts remain manually craftable.
    event.remove({ output: 'vs_clockwork:air_compressor' });
    event.recipes.gtceu.assembler('tfg:clockwork/lv/air_compressor')
        .itemInputs(
            'gtceu:lv_electric_motor', 'gtceu:lv_electric_pump',
            '2x #forge:plates/steel', 'vs_clockwork:duct'
        )
        .itemOutputs('vs_clockwork:air_compressor')
        .duration(200).EUt(LV);

    event.remove({ output: 'vs_clockwork:pump_duct' });
    event.recipes.gtceu.assembler('tfg:clockwork/lv/pump_duct')
        .itemInputs('vs_clockwork:duct', 'gtceu:lv_electric_pump',
            '#forge:plates/steel')
        .itemOutputs('vs_clockwork:pump_duct')
        .duration(120).EUt(LV);

    // MV - motorized moving structures, stabilized bearings, sensing
    // and industrial gas handling. Early free hull assembly remains.
    event.remove({ output: 'vs_clockwork:phys_bearing' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/physics_bearing')
        .itemInputs('vs_clockwork:wanderlite_matrix',
            'gtceu:mv_electric_motor', 'gtceu:steel_rotor',
            'create:brass_casing')
        .itemOutputs('vs_clockwork:phys_bearing')
        .duration(300).EUt(MV);

    event.remove({ output: 'vs_clockwork:gimbal_bearing' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/gimbal_bearing')
        .itemInputs('vs_clockwork:wanderlite_matrix',
            '2x gtceu:mv_electric_motor', '2x gtceu:steel_rotor',
            'create:brass_casing')
        .itemOutputs('vs_clockwork:gimbal_bearing')
        .duration(400).EUt(MV);

    event.remove({ output: 'vs_clockwork:gyro' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/gyro')
        .itemInputs('vs_clockwork:wanderlite_matrix', 'gtceu:mv_sensor',
            'gtceu:steel_rotor', 'create:flywheel')
        .itemOutputs('vs_clockwork:gyro')
        .duration(300).EUt(MV);

    // Clockwork 0.5.7.1 does not register "phys_piston" or "phys_gantry".
    // Industrialize the real moving-control bearings instead; Create pistons
    // and gantries remain available through their own progression.
    event.remove({ output: 'vs_clockwork:smart_flap_bearing' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/smart_flap_bearing')
        .itemInputs('vs_clockwork:wanderlite_matrix',
            'gtceu:mv_electric_piston', 'create:brass_casing',
            'create:mechanical_piston')
        .itemOutputs('vs_clockwork:smart_flap_bearing')
        .duration(300).EUt(MV);

    event.remove({ output: 'vs_clockwork:copter_bearing' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/copter_bearing')
        .itemInputs('vs_clockwork:wanderlite_matrix',
            'gtceu:mv_electric_motor', 'gtceu:steel_rotor',
            'vs_clockwork:brass_propeller_bearing')
        .itemOutputs('vs_clockwork:copter_bearing')
        .duration(300).EUt(MV);

    // Native crafting turned one crystal + eight glass into finished
    // Wanderglass. Industrializing it costs water, power and a crystal.
    // Assembler accepts both item inputs (unlike single-input Autoclave).
    event.remove({ output: 'vs_clockwork:wanderglass' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/wanderglass')
        .itemInputs('8x minecraft:glass', 'vs_clockwork:wanderlite_crystal')
        .inputFluids(Fluid.of('gtceu:distilled_water', 1000))
        .itemOutputs('8x vs_clockwork:wanderglass')
        .duration(300).EUt(MV);

    event.remove({ output: 'vs_clockwork:gas_nozzle' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/pressure_gas_nozzle')
        .itemInputs('vs_clockwork:duct',
            '#forge:plates/steel', '#forge:rods/steel',
            'gtceu:steel_rotor')
        .itemOutputs('vs_clockwork:gas_nozzle')
        .duration(260).EUt(MV);

    event.remove({ output: 'vs_clockwork:gas_crafter' });
    event.recipes.gtceu.assembler('tfg:clockwork/mv/gas_crafter')
        .itemInputs('vs_clockwork:duct', 'gtceu:mv_electric_pump',
            'gtceu:aluminium_rotor', 'create:electron_tube')
        .itemOutputs('vs_clockwork:gas_crafter')
        .duration(260).EUt(MV);

    // HV: industrial thrust requires a pressure nozzle, heat exchanger,
    // corrosion-resistant rotor and lubricant. Native Clockwork gas
    // chemistry (phlogiston etc.) is deliberately left intact.
    event.remove({ output: 'vs_clockwork:gas_thruster' });
    event.recipes.gtceu.assembler('tfg:clockwork/hv/gas_thruster')
        .itemInputs('gtceu:hv_electric_motor',
            'gtceu:stainless_steel_rotor',
            'vs_clockwork:gas_nozzle',
            'vs_clockwork:heat_exchanger')
        .inputFluids(Fluid.of('gtceu:lubricant', 250))
        .itemOutputs('vs_clockwork:gas_thruster')
        .duration(600).EUt(HV);

    // EV physics manipulation uses EV electrical control components.
    event.remove({ output: 'vs_clockwork:gravitron' });
    event.recipes.gtceu.assembler('tfg:clockwork/ev/gravitron')
        .itemInputs('vs_clockwork:wanderlite_matrix',
            'gtceu:ev_sensor', 'gtceu:ev_electric_motor',
            'gtceu:titanium_frame')
        .itemOutputs('vs_clockwork:gravitron')
        .duration(800).EUt(EV);
}
