# Overlay 0.13.10-nstut.32: repository preparation

Status: **REVIEWED RELEASE; SERVER ROLLOUT AUTHORIZED, CLIENT CHECK DEFERRED TO USER.** On 2026-10-11 the user authorized server patching and stable updater publication, explicitly choosing to test the updated client afterward rather than load on-prem-1. Packaged-client join and interactive food-route checks remain unperformed; they are not release-pass claims. Normal packaged full-TFG server startup, verified backup and rollback, and original Classic replacement remain server rollout gates.

## Custom-mod audit

On 2026-10-11, all nine UpperMoon0-owned projects in the Pakku lock and managed manifest were checked against their published, non-prerelease GitHub assets. The complete before/after inventory, immutable-version URLs, SHA-256 hashes and client/server targets are in [custom-mod-audit-0.13.10.32.json](custom-mod-audit-0.13.10.32.json).

| Custom mod | Previous | Prepared |
| --- | --- | --- |
| Economy | 0.0.17 | 0.0.18 |
| OpenUI MC | 0.0.12 | unchanged, client only |
| Create: Precise Controls | 0.1.1 | unchanged, client only |
| Simply Screens | 0.8.9 | unchanged |
| Simply Speakers | 0.8.4 | 0.9.0 |
| Create Horse Power CE | 1.2.7 | unchanged |
| Building Gadgets Extra | 0.0.4 | unchanged |
| Perfomant Boom | 1.1.3 | unchanged |
| Celestial Nail | 0.1.5 | 0.1.6 |
| Spice of Life Integrations | absent | 0.1.0 |

The new Speakers and Nail Forge 1.20.1 jars were downloaded and independently hashed; both match their GitHub release digests. Their packaged `META-INF/mods.toml` declarations were inspected. Speakers requires Architectury >=9.2.14, OpenUI >=0.0.12 on the client, and Patchouli; the pack already has Architectury 9.2.14, OpenUI 0.0.12 and Patchouli 1.20.1-85-FORGE. Nail requires Architectury >=9.2.14 and Boom >=1.1.3,<2.0.0; both are satisfied. Forge 47.4.13 and Minecraft 1.20.1 remain unchanged. Neither update adds a new dependency or changes installation sides.

Economy 0.0.18 was published after the approved PR #37 merge at `f0cb1a5589b8ef9fdf099cb266e986e39a0b448e`. The exact Forge asset is pinned with SHA-256 `0c3f7a183b22ab4cf644482bbf5bb7e6ac7421a9bb91312ab4102d4c4c6aacff`. Downloaded Economy bytes match that digest and size 727633. Packaged metadata requires Forge [47,48), Minecraft [1.20.1,1.21) and client OpenUI >=0.0.12, satisfied by the pack. It includes the reopened-market crash fix; repository preparation leaves existing storage and UI settings unchanged.

Extra Gauges, TrueUUID, LittleTiles and original Spice of Life Classic remain pinned exactly as before. No unrelated third-party update was requested or performed. The audit does not imply newer unpublished custom-mod source has been released.

## Spice of Life integration release and staging

The approved addon PR was merged at `a5ff8595eedc69dac065a280f71af47146a6e92d`, preserving the exact reviewed tree from `38df6144d34b8ad81db26f928513f6c3bf43ab5a`. [Release v0.1.0](https://github.com/UpperMoon0/SpiceOfLife-Integrations/releases/tag/v0.1.0) was published on 2026-10-11 after [all release CI gates passed](https://github.com/UpperMoon0/SpiceOfLife-Integrations/actions/runs/38118693429). GitHub asset 630015843 is `solintegrations-0.1.0.jar`, 674610 bytes, SHA-256 `ee4180ec10d5c242941f605268d1e649f364dfe750741e6423407ee86282c92d`, matching the earlier tested CI artifact.

The published JAR was independently downloaded and hashed: exact SHA-256 and size match the GitHub digest, release provenance/checksum receipts and previously tested CI artifact. Packaged metadata requires original Classic [2.13], Forge [47.4.13,48) and Minecraft [1.20.1], all satisfied. Jar-in-Jar metadata is present and no GameTest fixtures or TFC/Sophisticated implementation classes are bundled.

The addon is now an active, version-pinned entry in Pakku and the managed client/server manifest. Old `solintegrations-*.jar` copies are cleaned on both sides. No expiring Actions URL or guessed release URL is used. `pending-integrations.json` retains release provenance and the remaining staging blocker; artifact availability is no longer a blocker.

The exact addon tree has passing 46 JUnit tests, 81 Python checks and five development GameTest profiles. The combined development profile uses a documented test-only bootstrap. These checks do **not** establish normal packaged dedicated-server/client startup, full TFG Core 0.9.23 behavior or production readiness.

For the remaining user-owned compatibility checks, use the addon's [packaged and full-pack validation matrix](https://github.com/UpperMoon0/SpiceOfLife-Integrations/blob/a5ff8595eedc69dac065a280f71af47146a6e92d/docs/VALIDATION.md) in isolated instances. The user has explicitly deferred the client and interactive checks until after receiving the update. Current pack versions match the reviewed targets: Classic 2.13, TFC 3.2.25, Sophisticated Core 1.3.84.2308 and Backpacks 3.24.67.2109. No new integration configuration is imposed; packaged metadata and source inspection are separate from gameplay validation.

## Future migration warning

The live server may contain the emergency binary-patched Classic 2.13. **Do not install the standalone addon alongside that modified jar.** Before any separately authorized deployment, stop joins and services, verify a restorable backup of the world, player/food history, configs and exact current mod binaries, and record their hashes.

The new integration must be paired with the **original unmodified Classic 2.13** already pinned by this repository: SHA-256 `c7f1fe7f1d183ca69d69ae1e37284632ef997dff18bfbfce27de343f83dcc336`. Replace the emergency jar rather than retaining another copy under a different filename. Ensure exactly one Classic and one approved addon are present on each required side. Existing cleanup globs cover only their documented names; inventory all actual filenames before migration.

Preserve existing depletion settings, food-history/world data and user configuration. This preparation changes no runtime overlay or config, does not reset food history and does not enable a new minimum-hunger/floor option. Exercise hand, basket and backpack feeding; positive/fractional/zero depletion; native hydration/nutrients; repeated-food cycling; inventory costs; reconnect and restart in copied staging worlds when performing the deferred client verification.

Rollback requires restoring the matching previous mod/config set and the verified pre-migration world/player backup as one coherent state. Remove the standalone addon before restoring an emergency-patched Classic jar. Do not blindly downgrade jars over a world that has already been saved by the new stack.

## Validation and promotion boundary

Run `python nstut/tools/generate-modpack-manager-manifest.py`, then `python nstut/tools/validate.py` and `git diff --check`. The existing validator includes client/server boundary and generated-manifest checks plus isolated temporary-directory dry-run, semantic-config preservation and idempotence fixtures. It does not test Minecraft gameplay.

The preparation branch is based on current stable `2a257a58e0e9ef38d8cac5103be2f4178efeed65`; the current `nstut/0.13.10` construction head has the identical tree. Submit a draft PR into the construction branch, not the production pointer. The authorized immutable release tag is `nstut-0.13.10.32`; tag the final reviewed construction head and retain the existing stable promotion checks. The server candidate uses the same artifact hashes and operations with immutable commit URLs until that tag is published. Client validation is explicitly deferred, not reported as passing.

## Server preflight receipt

Read-only server preflight passed on 2026-10-11. Live and isolated plans agree on exactly eight mod-file operations; all 28 artifacts match pinned hashes. Configuration/authentication changes are no-ops, and `server.properties` identity/content remained unchanged. The stale 0.13.9 label is the actual MOTD text, to be corrected separately during the approved maintenance. This receipt does not establish installation or runtime success.
