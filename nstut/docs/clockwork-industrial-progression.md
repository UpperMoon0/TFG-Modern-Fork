# Clockwork industrial progression (TFG Modern)

## Gameplay contract

Ship **physics-body assembly starts in Steam Age**; electrical technology improves bearings, controls and propulsion rather than unlocking ship construction itself.

### First Wanderlite in an existing world

- Prospect deep graphite veins (roughly Y -64 to -16) and magnetite veins; mine their raw ores.
- Obtain 4 amethyst gems (Forge gem tag, including compatible shards). With a **Steam Age Greate Mixer**, combine **64 raw graphite, 64 raw magnetite, and 16 amethyst gems** to recover **1 Wanderlite Crystal**.
- This intentionally consumes naturally mined ore and requires no Wanderlite seed. It can be costly, but it avoids dependence on new chunks or meteor spawns.
- For new chunks, rare **Deep Wanderlite** veins generate in all 20 TFC stone types, roughly Y -60 to -24; crush the native Clockwork ore as usual. They are rare (vein rarity 420) and no richer than the base Clockwork crushing yields.
- Existing Clockwork Charged Nyx crushing (50% crystal byproduct) remains another potential source wherever Charged Nyx can actually be obtained.

### Steam versus HV Wanderlite: balance invariant

| Route | Consumed input per batch | Output | Requirements |
|---|---|---|---|
| Steam bootstrap | **64 raw graphite ores + 64 raw magnetite ores + 16 amethyst gems** | **1 crystal** | One Greate Steam-tier Mixer, **no electricity** and **no prior Wanderlite** |
| HV renewable (PR #95) | **16 renewable felsic dust + 8 renewable metamorphic dust + 4 amethyst shards + 8 redstone + 8 buckets distilled water + 1 bucket oxygen** | **1 Wanderlite ore (~1.75 crystals after Create crushing)** | Three HV machines; 1.44 M EU; 2 reusable Vitrified Pearls and 1 reusable Wanderlite seed |

The Steam fallback spends **128 finite natural ore items** for a single
crystal, whereas HV uses **24 renewable rock dusts** per roughly 1.75 crystals.
The HV route needs greater capital, power and process complexity but has a
much lower recurring resource cost and can scale without fresh graphite or
magnetite deposits. It is therefore a better bulk route without making the
first ship depend on electricity. These inputs are not chemically equivalent:
do not present this as a precise single-price efficiency ratio.

The new Matrix assembly also uses two Steam Age Create loops instead of the
native instant pressing. Once LV is reached, electric shaping reduces the
manual processing and brass/bronze consumption.

### Steam Age (first ship)

1. Make one Wanderlite Crystal using mineral recovery, natural deep Wanderlite ore, or other existing Clockwork loot.
2. Use a mechanical saw to cut a Rough Wanderlite Cube; sandpaper-polish it to a Cube. Then run two Create sequenced-assembly loops (Brass Plate + Small Bronze Gear + Press) to form a Matrix. From LV onward, Lathe and Forming Press recipes shortcut those Steam operations.
3. Craft a Wanderwand using its existing Brass -> Create sequenced assembly -> Matrix path. Steam Age quests already include Deployers and Mechanical Crafters.
4. Craft the Physics Infuser from 4 Brass Plates, 2 Wrought-Iron Double Plates, 2 Brass Casings, and 1 Wanderlite Matrix (the MV casing override is explicitly removed).
5. Build a **disconnected** hull, select two opposing corners with the Wanderwand, insert the wand in the Infuser, and empty-hand right click to assemble.
6. For primitive propulsion use the native Juryrigged Propeller Bearing, sails or other Steam-era mechanisms. An assembled body alone does **not** provide lift or power.

### Electrical progression

| Stage | Unlocked/industrialized technology |
|---|---|
| LV | Electric Cube Lathe and Matrix Forming Press; Air Compressor and Pump Duct |
| MV | Physics Bearing, Gimbal Bearing, Gyroscope, Physical Piston/Gantry, Wanderglass, Gas Nozzle and Gas Crafter via electric machinery |
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

## Lean headless worldgen acceptance (no client, spectator, or Chunky)

Keep the routine PR gate deliberately small: **one Forge startup at a fixed seed**, let
the dedicated server's **ordinary spawn-chunk initialization** perform natural
terrain generation, then inspect the saved blocks. Minecraft 1.20.1 initializes
spawn chunks without a player, so a separate pregenerator is not normally needed.

### Test coverage

1. **Static invariant (always run)**: run
   `python3 nstut/tools/validate-clockwork-progression.py .` to ensure production
   rarity is **420**, the intended rocks and heights remain unchanged, and the
   TFC vein tag/placed/configured feature are defined.
2. **Prepare the smoke overlay** (the script refuses to write outside a *new*
   directory under `/tmp`, and refuses to mutate existing files):

   ```bash
   python3 nstut/tools/stage-clockwork-worldgen-smoke.py \
     --repo-root . --output-dir /tmp/tfg-clockwork-smoke-overlay
   ```

   The script validates the candidate's production rarity, copies **only**
   `kubejs/data/tfg/worldgen/configured_feature/earth/vein/deep_wanderlite.json`,
   changes **rarity 420 → 1** in that temporary copy, preserves all six original
   host-rock replacements and Y constraints, and writes an audit manifest.
3. **Real natural generation in one disposable Forge world**: construct a fresh
   candidate server pack in a separate temporary directory, apply that single
   staged overlay **before the server starts**, select a fixed seed, and start
   Forge normally. Verify Clockwork is loaded and worldgen registry/tag accepts
   the configured + placed feature. Allow the initial spawn chunks to finish
   generating; execute `save-all flush`, then `stop` using the **isolated**
   console. No external Chunky mod, RCON to production, players, `/place
   feature`, or manual exploration are needed.
4. **Read-only world evidence** (after shutdown):

   ```bash
   python3 nstut/tools/scan-clockwork-worldgen.py \
     /tmp/tfg-worldgen-ci/world/region \
     --min-chunks 64 --min-blocks 1 \
     --report /tmp/tfg-clockwork-wanderlite.json
   ```

   The scanner requires **64 fully generated chunks** and at least **one
   actually placed Wanderlite block**, and reports X/Y/Z, chunk status and ore
   count. Partially generated chunks or unused block palette entries never
   count as successes. The scan runs offline.
5. **Optional retry only on zero evidence**: one second fixed seed in a new
   disposable world helps distinguish unsupported spawn geology from a broken
   vein. A zero in both seeds is a **diagnostic failure/inconclusive generation
   check**; inspect host-rock strata, loaded worldgen registry and logs before
   changing production rarity. Do not silently turn a zero into a pass.

### Verification guarantees and limitations

- This is a **real-worldgen integration test**, not a direct `/place feature`
  shortcut. It proves that the fully loaded pack can naturally spawn the exact
  ore block via registered TFC worldgen in at least one generated chunk.
- It does **not** estimate natural ore frequency with rarity 420. That is a
  separate, explicitly requested balancing benchmark—not a required PR gate.
- The runtime must additionally verify item/recipe registry and Steam Age
  craftability; worldgen alone does not prove the full progression chain.
- Store the fixed seed, server/KubeJS/mod jar hashes, overlay manifest, server
  logs and scanner JSON as CI artifacts. Only the **production feature JSON**
  is packaged and released, never the temporary rarity-1 override.
- For environments where startup does not generate 64 full chunks, report
  insufficient coverage and explicitly request a small bounded extra chunk
  generation run. Do not default to generating thousands.
- Synthetic scanner and override-protection fixtures can run without Forge:

  ```bash
  python3 nstut/tools/test_scan_clockwork_worldgen.py -v
  python3 nstut/tools/test_stage_clockwork_worldgen_smoke.py -v
  ```

Never inspect, pre-generate, or mutate production Minecraft regions for
this test. The disposable Forge instance must use its own separate world.
