# 0.13.12-nstut.1 automatic migration

This release upgrades an installed upstream 0.13.10 pack to 0.13.12, then applies the managed fork overlay. It includes upstream 0.13.11 gameplay changes and 0.13.12 server fixes, preserving all 15 managed mod pins from .34 and the LV/MV renewable slurry routes. The upstream source is `4b4732760b2885db45832a07f2925ba10f4c5930`.

## Client update

Update Modpack Manager to **1.0.7** first, close Minecraft, select the existing TFG installation and apply its update. The Manager verifies the installed Core and every downloaded file, upgrades pack-owned files, removes obsolete upstream files, merges changed TOML/JSON settings against old defaults, and applies the fork overlay. Saves, options, identity data and unknown user files are preserved. Edited obsolete configs and unsupported modified config formats are retained. The base marker is committed only after the complete update succeeds. Interrupted updates can resume, and failed transactions roll back their files.

Older Managers reject installations lacking the 0.13.12 base marker; manually creating that marker does not upgrade the base. The new Manager also verifies the target Core hash when accepting a completed migration.

## Server update

Run the scripts from this release's `nstut/tools` directory:

    python3 migrate-server.py /path/to/current/server --service tfg-manager.service

For an installation without the wake manager, omit `--service` and stop the server first. The script obtains the checksum-verified Manager 1.0.7 CLI, follows the published TFG profile, snapshots the stopped installation, audits and migrates the existing world, applies the complete base and overlay, and checks that the subsequent plan is empty. With the wake service it also uses Java 17 and the installed Forge launch arguments, restarts through that service, waits for authenticated readiness and saves the world. Original heap flags, environment setup, ports and service bindings remain in place.

Backups and reports are saved under `.modpack-manager/migration-backups`. Existing root backup/log directories are preserved during rollback; nested world data is included in the snapshot. Interrupted migration retains its original backup through the checkpoint. Failed boot restores that installation only after the JVM has stopped saving. Check available disk space for a full snapshot.

The world migration maps removed Fluid Logistics cardboard references only in Create factory-panel filter slots to `tfc:empty_jar`. Unsupported removed block or inventory references abort before world writes. The scan covers serialized region/entity/POI chunks and standalone NBT files, excluding the global registry table and nested custom compressed storage payloads.

## Validation and limits

Full policy checks, upstream pins, 90 renewable recipes, 12 upstream regression cases, world migration tests, snapshot/rollback tests and Manager migration regressions pass. Immutable client/server payloads and provider downloads are pinned by SHA-256 in `base-migration.json`.

A fresh stopped .34 server copy upgraded in place, remapped one legacy filter across 572,460 chunks, and produced an empty plan. Original private identity registry and server properties were preserved. A client fixture also converged to an empty plan and retained options and a private-save sentinel.

The migrated world booted under Java 17 in an isolated network with a 4-GiB heap, 6-GiB cap and one CPU. All 130 startup and 346 release server scripts loaded without errors or warnings. Authenticated readiness, advancing game ticks, 20 idle TPS, native LV/MV slurry recipes and the automatic large-reactor copy, save-all and graceful shutdown passed. See [validation evidence](validation-0.13.12.1.json).

A packaged client join, interactive media/food behavior and comprehensive oxygen, gas-burner, AE2 and machine gameplay remain unverified. The startup check is not a loaded-world performance benchmark.
