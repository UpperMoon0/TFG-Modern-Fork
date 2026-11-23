# Clockwork industrial progression (TFG Modern)

## Gameplay contract

Ship **physics-body assembly starts in Steam Age**; electrical technology improves bearings, controls and propulsion rather than unlocking ship construction itself.

### First Wanderlite in an existing world

- Prospect deep graphite veins (roughly Y -64 to -16) and magnetite veins; mine their raw ores.
- Obtain 16 amethyst gems (Forge gem tag, including compatible shards). Run **16 Steam Age Greate Mixer batches**; each takes **4 raw graphite, 4 normal TFC magnetite and 1 amethyst** to yield one Wanderlite Trace. Arrange **16 traces in a 4×4 Create Mechanical Crafter** for **1 Wanderlite Crystal** (total: **64 graphite + 64 magnetite + 16 amethyst**).
- This intentionally consumes naturally mined ore and requires no Wanderlite seed. It can be costly, but it avoids dependence on new chunks or meteor spawns.
- For new chunks, rare **Deep Wanderlite** veins generate in all 20 TFC stone types, roughly Y -60 to -24; crush the native Clockwork ore as usual. They are rare (vein rarity 420) and no richer than the base Clockwork crushing yields.
- Existing Clockwork Charged Nyx crushing (50% crystal byproduct) remains another potential source wherever Charged Nyx can actually be obtained.

### Steam versus HV Wanderlite: balance invariant

| Route | Consumed input per batch | Output | Requirements |
|---|---|---|---|
| Steam bootstrap | **64 raw graphite ores + 64 raw magnetite ores + 16 amethyst gems** | **1 crystal** | Greate Steam-tier Mixer + 4×4 Create Mechanical Crafter; **no electricity** and **no prior Wanderlite** |
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
manual processing and brass consumption.

### Steam Age (first ship)

1. Make one Wanderlite Crystal using mineral recovery, natural deep Wanderlite ore, or other existing Clockwork loot.
2. Use a mechanical saw to cut a Rough Wanderlite Cube; sandpaper-polish it to a Cube. Then run two Create sequenced-assembly loops (Brass Plate + Small Brass Gear + Press) to form a Matrix. From LV onward, Lathe and Forming Press recipes shortcut those Steam operations.
3. Craft a Wanderwand using its existing Brass -> Create sequenced assembly -> Matrix path. Steam Age quests already include Deployers and Mechanical Crafters.
4. Craft the Physics Infuser from 4 Brass Plates, 2 Wrought-Iron Double Plates, 2 Brass Casings, and 1 Wanderlite Matrix (the MV casing override is explicitly removed).
5. Build a **disconnected** hull, select two opposing corners with the Wanderwand, insert the wand in the Infuser, and empty-hand right click to assemble.
6. For primitive propulsion use the native Juryrigged Propeller Bearing, sails or other Steam-era mechanisms. An assembled body alone does **not** provide lift or power.

### Electrical progression

| Stage | Unlocked/industrialized technology |
|---|---|
| LV | Electric Cube Lathe and Matrix Forming Press; Air Compressor and Pump Duct |
| MV | Physics Bearing, Gimbal Bearing, Gyroscope, Smart Flap Bearing and Copter Bearing, Wanderglass, Gas Nozzle and Gas Crafter via electric machinery |
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

**Ordinary PR checks:** The static validator enforces the exact production rarity
of 420, all twenty TFC stone hosts, matching configured/placed feature IDs,
seed-free 64+64+16 Steam synthesis, matrix assembly, and all machine tiers.
Run this whenever the corresponding recipe or worldgen source changes:

```bash
python3 nstut/tools/validate-clockwork-progression.py .
python3 nstut/tools/test_scan_clockwork_worldgen.py -v
python3 nstut/tools/test_stage_clockwork_worldgen_smoke.py -v
python3 nstut/tools/test_run_clockwork_worldgen_smoke.py -v
```

**One real Forge integration test**, needed before the feature merges:

1. A trusted CI job provisions a **fresh dedicated candidate TFG Forge 1.20.1
   server pack** (correct mod versions, KubeJS, configs and startup scripts)
   in its own directory below /tmp. It must contain an empty world, `mods/`,
   `kubejs/`, an already accepted `eula.txt`, and the marker
   `.tfg-clockwork-disposable`. No server/world path may point into production.
   Use the immutable PR commit and store its pack hashes.
2. Run the included bounded runner, using the **actual candidate server**
   launch script. It validates the production feature JSON, applies a **rarity 1
   test-only overlay** to the disposable server, sets localhost/ephemeral
   server binding and a fixed seed, and performs one normal spawn generation
   (no Chunky, pregen plugin, player or spectator):

   ```bash
   python3 nstut/tools/run-clockwork-worldgen-smoke.py \
     --repo-root . \
     --server-dir /tmp/tfg-clockwork-ci-server \
     --launch "./run.sh nogui" \
     --evidence-dir /tmp/tfg-clockwork-ci-evidence
   ```

**Combined native gameplay gate (release acceptance):** Add `--native-assembly`
to the same command. The runner then stages the **test-only** fixture from
`nstut/tools/fixtures/clockwork-native-assembly-smoke.js` into the explicitly
marked disposable pack and waits for both Forge's `Done` marker and the native
`[CLOCKWORK_GAMEPLAY_PASS]` marker **in the same single server startup**.
The fixture builds a disconnected 3×3 wooden hull, rejects an Infuser with
no wand, creates a valid Wanderwand selection, force-ticks the fixture chunks
(playerless servers otherwise need not tick them), calls Clockwork's real
`PhysicsInfuserBlockEntity.startAssembly`, and requires Valkyrien Skies to
move the nine blocks into a ship with a valid ID. The fixture is never part
of release KubeJS scripts and is not installed on production.

The standalone native integration was verified on disposable Java 17 /
Forge 1.20.1 / Clockwork 0.5.7.1: ship ID **15**, nine source blocks moved,
**82 server ticks**, 35,212 registered recipes and zero failed recipes.
For reproducibility, the original success log, four failed fixture attempts,
raw Anvil region files and SHA256 are archived under
`/var/lib/nstut-acceptance/tfg-clockwork-gameplay-20261124/` on cloud-1.
This proves native assembly functionality, not every client interaction or
physics edge case.

3. The runner detects the Forge `Done` startup marker, issues `save-all flush`
   and `stop`, then decodes the fully saved Overworld region. **Positive pass:
   at least one actually FULL, ore-bearing chunk with a Wanderlite block at
   the correct deep Y-coordinate.** Requiring 64 full chunks in addition to
   direct positive evidence needlessly slows CI. The scanner counts actual
   packed block indices, never unused palette entries or unfinished chunks.
   Only when the first seed gives zero ore does the runner retry another seed.
   **Negative evidence requires 64 full chunks** to avoid treating partial
   spawn generation as evidence that the ore never spawns; without adequate
   fully generated chunks, the negative result remains inconclusive.
4. Archive the summary JSON, individual coordinate reports, overlay manifest,
   server logs, world seed, candidate commit and modpack hashes. Do not
   archive the test-only rarity override as a release artifact. Destroy the
   disposable server directory only after evidence is retained.

The separate stage utility is available for inspection:

```bash
python3 nstut/tools/stage-clockwork-worldgen-smoke.py \
  --repo-root . --output-dir /tmp/clockwork-manual-overlay
```

It **refuses to modify source** or overwrite an existing output directory.
The automated runner calls this utility itself. It does not need Chunky or
other pre-generation mods.

This smoke test proves that natural worldgen is correctly registered and can
place Wanderlite in real terrain. It is **not** a statistical rarity benchmark:
the real rarity 420 is validated statically, and proving its long-run natural
frequency would require substantially more chunks. That costly balance check
is optional and is deliberately excluded from normal PR CI.

A real modded recipe-registry check is also required before shipping to verify
GTCEu item IDs, KubeJS Create sequenced assembly, native recipe override
removal and Steam Age playability; passing the ore smoke alone does not prove
those recipes load.

Never inspect, regenerate, or mutate production regions to test this feature.
