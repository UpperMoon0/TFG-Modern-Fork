# Clockwork industrial progression (TFG Modern)

## Gameplay contract

Ship **physics-body assembly starts in Steam Age**; electrical technology improves bearings, controls and propulsion rather than unlocking ship construction itself.

### First Wanderlite in an existing world

- Prospect deep graphite veins (roughly Y -64 to -16) and magnetite veins; mine their raw ores.
- Obtain 4 amethyst gems (Forge gem tag, including compatible shards). With a **Steam Age Greate Mixer**, combine **16 raw graphite, 8 raw magnetite, and 4 amethyst shards** to recover **1 Wanderlite Crystal**.
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

## Headless worldgen acceptance (no client or spectator)

The existing static assertions in `nstut/tools/validate-clockwork-progression.py` prove only recipe/worldgen *definitions*. They do not prove a TFC feature was registered and ran in a real seed. The following is the acceptance procedure to automate in an isolated Jenkins job:

1. Take the **actual candidate server pack** plus PR KubeJS/data files and construct a throwaway dedicated Forge 1.20.1 instance. No production world, credentials, network ports, or Minecraft-MCP connections. Record exact mod jar hashes, PR commit and world seed.
2. Install a version-compatible **Forge Chunky pregenerator in the CI instance only** (not in the distributed modpack). Start the server and run the following through the *isolated server console/RCON*, with no player connected:

   ```text
   chunky world minecraft:overworld
   chunky shape square
   chunky center 0 0
   chunky radius 640
   chunky start
   ```

   Chunky radius uses **blocks**, not chunks. Radius 640 and square shape should generate about 6,400 chunks. Wait for Chunky to finish and verify the count rather than assuming it completed. Flush saves and shut down Forge before scanning.
3. Scan the saved region files from that temporary world:

   ```bash
   python3 nstut/tools/scan-clockwork-worldgen.py \
     /tmp/tfg-worldgen-ci/world/region \
     --min-chunks 4096 --min-blocks 1 \
     --report /tmp/tfg-clockwork-wanderlite.json
   ```

   Exit code **0** means both sample-size and actual block-count thresholds passed; **2** means insufficient chunks or no Wanderlite; **3** means corrupt/invalid region files or unavailable world input. The JSON includes real block coordinates, counts and Y histogram. `blocks_found` counts decoded packed block indices; palette-name presence alone does not count.
4. Repeat across at least **three fixed, unrelated seeds**, each in a freshly initialized world. Fail if all samples are empty, or if the blocks are outside the intended deep underground distribution. For rare ores, expand sample size before treating an individual zero as proof of failure.
5. Preserve seed, scanner JSON, console log, modpack/PR hashes and generation settings as CI artifacts. Compare sample distributions against a fixed baseline when tuning balance. Confirm `tfc:in_biome/veins` includes `tfg:earth/vein/deep_wanderlite` in the *loaded* runtime worldgen registry.

This is the critical **in-game generation acceptance**, not a static JSON check. Run the scanner's synthetic Anvil fixtures independently:

```bash
python3 nstut/tools/test_scan_clockwork_worldgen.py -v
```

Never use `/place feature` as the sole evidence of natural generation: direct placement can bypass normal biome selection or rarity. Never add Chunky to the production server for this test. Clean up temporary worlds only after archiving evidence; keep production regions untouched.
