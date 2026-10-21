# TFG 0.13.15-nstut.3

Upgrades the upstream base from 0.13.12 to 0.13.15. Update with Modpack Manager
1.0.7 or newer and close Minecraft before applying the update. Older 0.13.10
installations must first apply the published 0.13.12 migration.

All 15 custom mod artifacts retain their previously published pins. The release
preserves all 73 custom material translations, 90 renewable recipes including
the MV molten-mafic slurry route, and the existing runtime overlays. Both
packaged TFC defaults disable collapses and landslides.

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
regressions, renewable-chain and MV recipe registration checks, disabled
collapse defaults, archive CRCs and provider hashes. Server deployment uses a
stopped-instance snapshot, an empty post-apply Manager plan and authenticated
readiness/TPS checks. Packaged-client join and interactive gameplay remain
unverified.
