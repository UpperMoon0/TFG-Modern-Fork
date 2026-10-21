# TFG 0.13.15-nstut.4

Upgrades the upstream base from 0.13.12 to 0.13.15. Update with Modpack Manager
1.0.7 or newer and close Minecraft before applying the update. Older 0.13.10
installations must first apply the published 0.13.12 migration.

All 15 custom mod artifacts retain their previously published pins. The release
preserves all 73 custom material translations, 90 renewable recipes including
the MV molten-mafic slurry route, and the existing runtime overlays. Both
packaged TFC defaults enable collapses and landslides with upstream probabilities.

Smooth/polished stone (including marble and gabbro), bricks and their mossy or
cracked forms, chiseled stone, cut-stone decorations, pillars, aqueducts,
supports, raw-stone slabs/stairs/walls, concrete, timber, glass, terracotta and
wool are excluded from collapse initiation, triggering, propagation, landslides
and isolated-block breaking. Cobblestone and mossy cobblestone retain their
upstream instability, as do natural raw stone, hardened stone, ores, gravel,
sand and dirt. A falling block can still collide with a structure; this policy
controls which building blocks can themselves collapse.

Core 0.9.29's `ServerLifecycleHooksMixin` loads server settings from
`defaultconfigs`, including for existing worlds. The Manager patch changes only
the eight collapse settings there, preserving unrelated configuration.

The KubeJS 2001.6.5 tag implementation only removes direct ID entries. The safety
pass runs last, resolves inherited tag membership and rebuilds the five affected
tags without protected construction blocks. Regression tests use the real rock
table, nested tags and terrain/cobblestone controls, and check reload stability.

The integration PR had one language-file conflict. Constructing the release
also reconciled the release branch's expanded materials, recipes, tags,
registrations and custom dependency entries against the integration branch.
The result uses upstream 0.13.15 provider artifacts except for the intentional
Create Horse Power replacement and the 15 custom managed additions.

The complete-base client and server migration payloads use original-provider
downloads with exact hashes. Previous defaults come from canonical upstream
0.13.12 source files so Manager can preserve user configuration changes.
World, player, identity and media data are excluded from public payloads.

Validation includes fork policy, generated manifest freshness, migration
regressions, renewable-chain and MV recipe registration checks, enabled
collapse defaults and building protections, archive CRCs and provider hashes. Server deployment uses a
stopped-instance snapshot, an empty post-apply Manager plan and authenticated
readiness/TPS checks. Packaged-client join and interactive gameplay remain
unverified.
