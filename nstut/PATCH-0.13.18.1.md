# TFG 0.13.18-nstut.1 — upstream sync, latest custom mods, Additional Placements fork

Base: TerraFirmaGreg Modern 0.13.18 / Minecraft 1.20.1 / Forge 47.4.13.

## Changes
- Merge the full official upstream 0.13.18 source and retain NsTut's previously promoted fixes and recipes.
- OpenUI-MC: 0.0.15 -> 0.0.16 (client only).
- Create: Precise Controls: 0.1.1 -> 0.2.0 (client only).
- Building Gadgets Extra: 0.0.8 -> 0.0.9.
- Celestial Nail: 0.1.6 -> 0.2.0.
- Replace the original Additional Placements 3.0.1 with NsTut's Forge 1.20.1 fork 3.0.1.2 (BOTH sides). Clean both original and older fork JARs.
- All other NsTut custom pins retain their latest published, compatible Forge 1.20.1 artifacts. Do not use unpublished Horse Power 1.2.12 PR snapshots.
- Every managed artifact uses an exact immutable release URL and SHA-256, with matching Pakku and Manager pins.

## Promotion and compatibility gates
- The original Additional Placements fork passed an isolated real Forge GameTest 1/1, but an installed FowlPlay pigeon-pathing regression and full TFG server + client acceptance are still required.
- Generate and publish verified 0.13.18 base-migration payloads (client and server) before stable promotion.
- Preserve TrueUUID player mappings, private configs, saved worlds, and the server identity registry. Never copy private world files into public base archives.
- Run pack validators, migration tests, actual exports and server startup before deploying; leave this PR unmerged pending acceptance.
