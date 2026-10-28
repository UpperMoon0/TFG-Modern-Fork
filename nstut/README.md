# NsTut TFG fork

This branch is the source of truth for NsTut changes layered on top of the released TerraFirmaGreg Modern pack.

## Branch model

The fork uses three deliberately different branch roles:

- `dev` is the integration/development branch. Upstream TFG development and NsTut feature work land here first. It is never a deployment pointer.
- `nstut/<base>` is a release-construction branch, for example `nstut/0.13.10`. It starts from the currently promoted release history, receives only the reviewed pack changes intended for that release, regenerates deployment metadata, and is fully validated before promotion.
- `nstut/stable` is a production promotion pointer. Modpack Manager follows only this branch. Do not develop on it and do not merge `dev` into it directly.

`nstut/release.json` records the upstream base, release-construction branch, overlay version, and immutable deployment tag.

### Promotion procedure

1. Integrate and test changes on `dev`.
2. Bring the reviewed release content into the matching `nstut/<base>` construction branch.
3. Bump `overlayVersion` and `sourceRef` in `nstut/release.json`.
4. Regenerate `nstut/modpack-manager.patch.json` and run the NsTut validators.
5. Commit the complete release state.
6. Create the immutable `sourceRef` tag on that exact release commit and push it.
7. Open a PR from the declared `nstut/<base>` branch to `nstut/stable`.
8. Merge only after both `validate` and `promotion-gate` pass.

The promotion gate rejects a PR into `nstut/stable` when its source is not the declared release-construction branch, when the immutable tag is missing, when the tag does not point to the exact PR head, or when the release branch does not descend from the current stable release.

On `nstut/stable`, validation additionally requires the complete repository tree to match the immutable deployment tag. This catches accidental direct `dev -> stable` merges even if `release.json` itself was not modified.

## What lives natively in the fork

Pack-owned changes are ordinary tracked files and Pakku metadata. This currently includes the CE Horse Power dependency/config, custom managed mods, the GTCEu weather/terrain explosion setting, and server-export FTB chunk limits.

GitHub projects with multiple loader assets are pinned to the reviewed Forge 1.20.1 asset and use update_strategy NONE; version changes are explicit fork commits rather than implicit Pakku updates.

## Deployment metadata

nstut/managed-mods.json contains exact downloadable artifacts and cleanup rules.

nstut/runtime-overlays.json describes semantic overlays for mutable config/runtime files. YAML, TOML, and SNBT entries are emitted into nstut/modpack-manager.patch.json. Existing-world FTB SNBT is patched semantically through patchSnbt; nstut/tools/patch-existing-server.py remains a standalone fallback that updates the same managed keys.

nstut/tools/generate-modpack-manager-manifest.py also inspects the fork diff against baseRef. Any future ordinary changed file not classified as mutable or metadata is emitted as an exact file replacement, sourced from the immutable sourceRef tag.

## Validation

Run these commands from the repository root:

    python nstut/tools/generate-modpack-manager-manifest.py
    python nstut/tools/validate.py

The validator checks the upstream ancestry, Forge/Minecraft target, exact managed JAR filenames/hashes, client-only boundaries, native config policy, server FTB defaults, and generated manifest freshness.

`nstut/stable` is therefore intentionally boring: it exists to identify the latest approved immutable release, not to accumulate development commits. Pakku server-overrides and client-overrides are generated to their real installation path and target, never copied under `.pakku`.

## Candidate: upstream 0.13.17

`0.13.17-nstut.1` integrates upstream 0.13.17 and updates Economy, OpenUI,
Simply Screens, Simply Speakers and PacketWeave. All sixteen managed artifacts
are hash/CRC verified; recipes, building protections and runtime policies are
preserved. See [release notes and promotion prerequisites](PATCH-0.13.17.1.md).
The 0.13.15 to 0.13.17 migration includes complete client/server base payloads.
Publish compatible Modpack Manager support before promoting this candidate.

## Previous overlay 0.13.15-nstut.8

TrueUUID 1.3.1 is pinned from the reviewed owner fork on both clients and server.
The Forge-only public release is hash-verified. Relative to stable .6 this also
includes the previously approved server-only VanishGuard addition; every other
mod pin and authentication setting is unchanged. See
[validation evidence](TRUEUUID-1.3.1-REVIEW.md) and [release notes](PATCH-0.13.15.8.md).

## Previous release: upstream 0.13.15

`0.13.15-nstut.6` updates Create Horse Power CE to 1.2.8 on clients and
servers for horse ownership and kinetic network recovery after loading.
All other pins and runtime settings are unchanged. See [release notes](PATCH-0.13.15.6.md).

### Previous overlay 0.13.15-nstut.5

`0.13.15-nstut.5` upgrades Economy, OpenUI, Screens, Speakers, Building Gadgets
Extra and PacketWeave to their latest compatible releases; the other nine
custom pins are current. Update clients and server together. See
[the custom-mod audit and release notes](PATCH-0.13.15.5.md).

The 0.13.15 release line upgrades the complete 0.13.12 base through Modpack Manager
1.0.7 or newer, preserving all 15 custom mods, expanded renewable recipes,
runtime overlays and building-safe collapse rules. Close Minecraft before
updating. Installations still on 0.13.10 must first apply the prior 0.13.12
migration. See [release and migration notes](PATCH-0.13.15.4.md).

## Previous upstream 0.13.12 automatic migration

The 0.13.12 construction branch preserves the .34 MV slurry recipe and all
15 managed mod artifacts. Modpack Manager 1.0.7 upgrades the installed base and
applies the overlay automatically; update the Manager first and close Minecraft.
The server script snapshots, upgrades and checks the current server and world,
with automatic rollback on failure. See
[the migration notes](PATCH-0.13.12.1.md).

## Overlay 0.13.10-nstut.34 (previous release)

PR #32 adds an optional MV Chemical Reactor recipe: 1,728 mB molten igneous
mafic plus 8,000 mB water produces 8,000 mB mafic mineral slurry at 120 EU/t
for 160 ticks. The LV Mixer route and downstream iron requirements are retained.
The generated Manager manifest includes the updated recipe file and its exact hash.
Fork-policy checks run for PRs targeting `main` as well as `nstut/**`.

This release preserves all `.33` managed mod pins, including Simply Screens
0.8.11, Simply Speakers 0.9.1 and PacketWeave 0.1.2. Server patching and Manager
publication are authorized. Packaged-client recipe visibility and interactive
machine operation remain unverified. See [release notes](PATCH-0.13.10.34.md).

## Overlay 0.13.10-nstut.33 (previous release)

All ten installed custom mods were checked against official stable releases on 2026-10-13. Simply Screens is updated to 0.8.11, Simply Speakers to 0.9.1, and standalone PacketWeave 0.1.2 is added to both clients and servers. The other eight installed custom mods and all third-party pins are unchanged. See [the complete audit](custom-mod-audit-0.13.10.33.json) and [compatibility and validation notes](PATCH-0.13.10.33.md).

Speakers changes its transfer protocol: update clients and server together before reconnecting.

## Overlay 0.13.10-nstut.32 (authorized rollout)

Server patching and stable updater publication are authorized. The user explicitly deferred packaged-client and interactive checks until after updating; those checks have not passed. See [the preparation and migration checklist](PATCH-0.13.10.32.md) and [the complete custom-mod audit](custom-mod-audit-0.13.10.32.json).

Economy is updated to 0.0.18, Simply Speakers to 0.9.0 and Celestial Nail to 0.1.6. The other six previously installed custom mods already match their latest published releases. Third-party pins and runtime configuration remain unchanged.

SpiceOfLife-Integrations 0.1.0 is now pinned from its published GitHub release on both clients and servers. The release uses the exact reviewed addon tree and CI artifact hash. [pending-integrations.json](pending-integrations.json) records the remaining server startup gate and explicitly deferred user-owned client checks. Never combine the standalone addon with the emergency binary-patched Classic jar.

## Previous overlay 0.13.10-nstut.31

All 13 managed mods were reviewed for Forge 1.20.1 compatibility on 2026-10-10. Economy is updated to 0.0.17 and Simply Speakers to 0.8.4, using exact GitHub release asset SHA-256 digests; the other previously managed versions remain pinned. Celestial Nail 0.1.5 requires Perfomant Boom 1.1.3 or newer within 1.x, satisfied by the current pin.

LittleTiles 1.6.0-pre161 (upstream beta, latest compatible Forge 1.20.1) and Spice of Life: Classic Edition 2.13 are added to both client and server patches with SHA-256-pinned Modrinth artifacts and removal of older JARs. Their downloaded JARs were verified against publisher SHA-512 hashes. LittleTiles requires CreativeCore >=2.12.30 (pack locks 2.12.39), while Spice of Life Classic requires Architectury >=9.2.14 (pack locks 9.2.14). No additional dependency JAR is needed. Spice of Life Classic penalizes repeatedly eating the same food by reducing recovered hunger; existing TFC nutrition mechanics are not replaced. Existing worlds must be backed up and client/server restarted after installing the two new mods. Because LittleTiles 1.20.1 is beta, test tile creation, saving, and network interaction in a staging world before broad rollout.

Economy Tank capacity is 512 buckets (`tankCapacity=512000`, in mB) in `config/economy-storage.properties`. Fresh client/server exports include this config. Modpack Manager and the existing-server fallback patch only this key, preserving other storage settings such as `allowExternalAutomation`. Economy 0.0.16 and newer upgrade already-placed tanks when they load on the server; stored fluid and larger saved capacities are preserved. Restart the game or server after applying the update. Modpack Manager 1.0.6 already supports the generated property patch; no app rebuild is required.

Server exports and existing-server overlays set `online-mode=false`. Only that property is managed; existing world names, ports, MOTDs, and other properties remain intact. Simply Speakers uploads are limited to 100 MiB (`maxUploadSize=104857600`) on clients, singleplayer, and servers. The server keeps its existing 512-block speaker range.

TrueUUID 1.3.0 for Forge 1.20.1 is required on both clients and servers. Premium players must join with their Microsoft/Mojang session so TrueUUID verifies their account and retains their original UUID. Existing inventories, advancements, statistics, mod capabilities, teams, quests, claims, balances, and entity ownership continue to refer to that identity; do not rename premium saves to offline UUIDs. Players without TrueUUID are refused before entering the world.

The server policy permits explicit offline sessions only for names that are not already bound to a verified account. Failed premium checks and timeouts must not downgrade to an offline profile. When converting an existing server, stop joins, back up identity data, and seed `config/trueuuid-registry.json` from confirmed premium identities before reopening joins. This registry belongs to the individual server and must never be shipped as a pack override. Keep `knownPremiumDenyOffline` and `allowOfflineForUnknownOnly` enabled. Account renames keep the verified UUID; newly changed names should also be bound in the server registry before admitting offline sessions with those names.

Upstream installation and authentication details: https://github.com/YuWan-030/TrueUUID/tree/v1.3.0.

With the server and wake service stopped, preview `python3 nstut/tools/prepare-premium-identities.py <server-root>`, then repeat with `--apply` to reserve cached premium names that have existing v4 UUID saves. The tool reads Java world-name syntax, preserves existing bindings, refuses conflicting UUIDs or malformed registries, ignores offline IDs and cache entries without saves, and changes only the server-private TrueUUID registry. It refuses to proceed if any saved premium UUID has no reserved name; restore its username cache or confirm and bind that identity first. Back up the world and identity files before changing login policy. A real premium-client join is still required to verify the complete login and gameplay path.

Merge the pack changes through the release-construction branch, tag its final reviewed commit as `nstut-0.13.10.31`, and promote it through the existing stable gate.


## Manager fresh-install release check

The `manager-fresh-install` policy job downloads the latest published Manager CLI,
checks its archive checksum, and runs `install --manifest ... --dry-run` against
this candidate's generated manifest. It requires the exact overlay version and
Minecraft/Forge versions in `pakku-lock.json`. Unsupported bases, missing complete
client payloads, or stale launcher metadata fail the check before promotion.
Publish a compatible Manager before promoting a pack that needs new installer
support. The existing `promotion-gate` explicitly requires this job to succeed, including
when this job fails or is cancelled. A dry run checks planning, not a full game launch.
