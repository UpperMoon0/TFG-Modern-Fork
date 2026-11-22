# 0.13.19-nstut.3 — production boot compatibility hotfix

**Root cause:** The initial production 0.13.19-nstut.2 boot on 2026-11-22 reached Forge `Done`, then crashed while promoting a world chunk to FULL status. Distant Horizons 3.3.3 invoked `ChunkyAccessor.bindOnGenerationProgressEvent` and `ChunkyProvider.get` threw `IllegalStateException: Chunky is not loaded` with optional Chunky 1.3.146.

**Remediation:** Remove *only* Chunky from both server and client pinned Pakku projects and both provider download lists in the 0.13.18 → 0.13.19 migration contract. No mod requires Chunky; Distant Horizons 3.3.3 remains both-side and provides LOD generation. Existing checksum-pinned 0.13.19 base migration archives remain immutable: their `migration-index.json` inventories old Chunky as a removable mod, while all target provider operations come from the new .3 manifest. Modpack Manager removes old Chunky during base migration rather than reinstalling it.

**Safety:** Supersedes .2 without modifying any immutable tag/release or enabling GitHub Actions. The failed .2 live migration automatically rolled back to 0.13.18-nstut.2, and protected world/player data and snapshots remain retained. Before production retry, require native exact-source Jenkins policy/promotion checks, an isolated copy of the real world to boot and save successfully, and adequate disk headroom for the full snapshot and rollback.


**Already updated instances:** An explicit, narrowly pinned cross-side `removeMatching` operation for `mods/Chunky-*.jar` ensures an existing 0.13.19-nstut.1/.2 installation removes Chunky even though its base migration marker already exists. No other mod paths are targeted.
