# Clockwork industrial progression (TFG Modern)

## Gameplay contract

Ship **physics-body assembly starts in Steam Age**; electrical technology improves bearings, controls and propulsion rather than unlocking ship construction itself.

### First Wanderlite in an existing world

- Prospect deep graphite veins (roughly Y -64 to -16) and magnetite veins; mine their raw ores.
- Obtain 4 amethyst shards. With a **Steam Age Greate Mixer**, combine **16 raw graphite, 8 raw magnetite, and 4 amethyst shards** to recover **1 Wanderlite Crystal**.
- This intentionally consumes naturally mined ore and requires no Wanderlite seed. It can be costly, but it avoids dependence on new chunks or meteor spawns.
- For new chunks, rare **Deep Wanderlite** veins generate in six TFC rock types, roughly Y -60 to -24; crush the native Clockwork ore as usual. They are rare (vein rarity 420) and no richer than the base Clockwork crushing yields.
- Existing Clockwork Charged Nyx crushing (50% crystal byproduct) remains another potential source wherever Charged Nyx can actually be obtained.

### Steam Age (first ship)

1. Make one Wanderlite Crystal using mineral recovery, natural deep Wanderlite ore, or other existing Clockwork loot.
2. Polish the crystal to a Cube and mechanically press to a Matrix (Clockwork Create recipes remain intact).
3. Craft a Wanderwand using its existing Brass -> Create sequenced assembly -> Matrix path. Steam Age quests already include Deployers and Mechanical Crafters.
4. Craft the Physics Infuser from 4 Brass Plates, 2 Wrought-Iron Double Plates, 2 Brass Casings, and 1 Wanderlite Matrix (the MV casing override is explicitly removed).
5. Build a **disconnected** hull, select two opposing corners with the Wanderwand, insert the wand in the Infuser, and empty-hand right click to assemble.
6. For primitive propulsion use the native Juryrigged Propeller Bearing, sails or other Steam-era mechanisms. An assembled body alone does **not** provide lift or power.

### Electrical progression

| Stage | Unlocked/industrialized technology |
|---|---|
| LV | Faster precision crystal shaping (Lathe); electric Air Compressor |
| MV | Physics Bearing, Gimbal Bearing, Gyroscope and Wanderglass via electric machinery |
| HV | Industrial Gas Thruster; **separate PR #95** adds renewable seeded Wanderlite ore synthesis |
| EV | Gravitron via high-tier sensor, motor and titanium frame |

The fundamental Physics Infuser and Wanderwand **must never** be LV/MV/HV gated. Do not remove their Steam Age path when refining other Clockwork recipes.

## Deployment and verification

- Keep new worldgen limited to newly generated chunks. Do not regenerate or mutate existing player chunks.
- Worldgen registration: `kubejs/data/tfg/worldgen/configured_feature/earth/vein/deep_wanderlite.json`, paired placed feature and TFC's `tfc:in_biome/veins` tag.
- KubeJS entrypoint: `registerTFGClockworkProgressionRecipes` from TFG's standard recipe registration.
- Clockwork mod guard: recipes and vein-tag registration only run when `vs_clockwork` is loaded.
- A modded integration test must validate item IDs, both native/TFG recipe overrides, machine tier requirements, and survival acquisition before merge.
- Existing PR #95 remains independent. When merged, preserve the seed-gated HV recipe, the nonconsumed crystal and Vitrified Pearls, and the Steam Age access route.
