# Overlay 0.13.10-nstut.32: repository preparation

Status: **BLOCKED DRAFT. Do not tag, promote or deploy.** This preparation changes repository files only; it does not install mods, restart a server, or mutate a game world.

## Custom-mod audit

On 2026-10-11, all nine UpperMoon0-owned projects in the Pakku lock and managed manifest were checked against their published, non-prerelease GitHub assets. The complete before/after inventory, immutable-version URLs, SHA-256 hashes and client/server targets are in [custom-mod-audit-0.13.10.32.json](custom-mod-audit-0.13.10.32.json).

| Custom mod | Previous | Prepared |
| --- | --- | --- |
| Economy | 0.0.17 | unchanged |
| OpenUI MC | 0.0.12 | unchanged, client only |
| Create: Precise Controls | 0.1.1 | unchanged, client only |
| Simply Screens | 0.8.9 | unchanged |
| Simply Speakers | 0.8.4 | 0.9.0 |
| Create Horse Power CE | 1.2.7 | unchanged |
| Building Gadgets Extra | 0.0.4 | unchanged |
| Perfomant Boom | 1.1.3 | unchanged |
| Celestial Nail | 0.1.5 | 0.1.6 |

The two new Forge 1.20.1 jars were downloaded and independently hashed; both match their GitHub release digests. Their packaged `META-INF/mods.toml` declarations were inspected. Speakers requires Architectury >=9.2.14, OpenUI >=0.0.12 on the client, and Patchouli; the pack already has Architectury 9.2.14, OpenUI 0.0.12 and Patchouli 1.20.1-85-FORGE. Nail requires Architectury >=9.2.14 and Boom >=1.1.3,<2.0.0; both are satisfied. Forge 47.4.13 and Minecraft 1.20.1 remain unchanged. Neither update adds a new dependency or changes installation sides.

Extra Gauges, TrueUUID, LittleTiles and original Spice of Life Classic remain pinned exactly as before. No unrelated third-party update was requested or performed. The audit does not imply newer unpublished custom-mod source has been released.

## Spice of Life integration prerequisite

The requested standalone addon is staged as a **pending integration**, not a fake downloadable artifact. As checked on 2026-10-11, [addon PR #1](https://github.com/UpperMoon0/SpiceOfLife-Integrations/pull/1) remains draft at `38df6144d34b8ad81db26f928513f6c3bf43ab5a`, and the repository has no published GitHub release. `pending-integrations.json` records its intended identity, both-side installation and cleanup rules, reviewed source and CI artifact hash. It is deliberately outside the active Pakku and deployment manifests.

The addon PR records passing 46 JUnit tests, 81 Python checks and five development GameTest profiles on that exact head. The combined development profile uses a documented test-only bootstrap. These checks do **not** establish normal packaged dedicated-server/client startup, full TFG Core 0.9.23 behavior or production readiness.

Before completing this patch:

1. Obtain explicit approval for any addon merge/release, complete its review and publish the approved immutable release. This pack-preparation request does not authorize that separate publication.
2. Download the release's reobfuscated `solintegrations` jar; verify exact bytes, release asset ID, provenance, SHA-256, Minecraft/Forge and dependency metadata. Do not substitute an expiring Actions URL, unreviewed source build or guessed release URL.
3. Add synchronized entries to `pakku.json`, `pakku-lock.json` and `nstut/managed-mods.json`, pin `update_strategy: NONE`, install on client and server and clean old addon versions on both sides. Regenerate the deployment manifest. Remove the pending blocker only when these steps and staging are evidenced.
4. Run the addon's [packaged and full-pack validation matrix](https://github.com/UpperMoon0/SpiceOfLife-Integrations/blob/38df6144d34b8ad81db26f928513f6c3bf43ab5a/docs/VALIDATION.md) in isolated instances. Current pack versions match the reviewed targets: Classic 2.13, TFC 3.2.25, Sophisticated Core 1.3.84.2308 and Backpacks 3.24.67.2109.

## Future migration warning

The live server may contain the emergency binary-patched Classic 2.13. **Do not install the standalone addon alongside that modified jar.** Before any separately authorized deployment, stop joins and services, verify a restorable backup of the world, player/food history, configs and exact current mod binaries, and record their hashes.

The new integration must be paired with the **original unmodified Classic 2.13** already pinned by this repository: SHA-256 `c7f1fe7f1d183ca69d69ae1e37284632ef997dff18bfbfce27de343f83dcc336`. Replace the emergency jar rather than retaining another copy under a different filename. Ensure exactly one Classic and one approved addon are present on each required side. Existing cleanup globs cover only their documented names; inventory all actual filenames before migration.

Preserve existing depletion settings, food-history/world data and user configuration. This preparation changes no runtime overlay or config, does not reset food history and does not enable a new minimum-hunger/floor option. Exercise hand, basket and backpack feeding; positive/fractional/zero depletion; native hydration/nutrients; repeated-food cycling; inventory costs; reconnect and restart in copied staging worlds before promotion.

Rollback requires restoring the matching previous mod/config set and the verified pre-migration world/player backup as one coherent state. Remove the standalone addon before restoring an emergency-patched Classic jar. Do not blindly downgrade jars over a world that has already been saved by the new stack.

## Validation and promotion boundary

Run `python nstut/tools/generate-modpack-manager-manifest.py`, then `python nstut/tools/validate.py` and `git diff --check`. The existing validator includes client/server boundary and generated-manifest checks plus isolated temporary-directory dry-run, semantic-config preservation and idempotence fixtures. It does not test Minecraft gameplay.

The preparation branch is based on current stable `2a257a58e0e9ef38d8cac5103be2f4178efeed65`; the current `nstut/0.13.10` construction head has the identical tree. Submit a draft PR into the construction branch, not the production pointer. `nstut-0.13.10.32` is only a reserved future source reference and is deliberately not created here. Raw file URLs referencing it cannot be downloaded until an authorized final tag is published. Keep existing promotion checks intact; resolve the pending addon and staging blockers before requesting promotion.
