# TFG 0.13.17-nstut.1

This candidate upgrades the complete upstream base from 0.13.15 to the exact
0.13.17 tag `32ba9f19d60bfc5b4148888fc84e50316b2b0fed`, preserving the fork's
renewable resources, MV mafic slurry recipe, finished-building protections,
512-bucket Economy tanks, authentication policy and server-only VanishGuard.

All 16 managed artifacts were checked on 2026-10-28. Published Forge 1.20.1
builds were downloaded and checked against publisher hashes and ZIP CRCs.

| Mod | Previous | Candidate |
| --- | --- | --- |
| Economy | 0.0.20 | 0.0.21 |
| OpenUI MC | 0.0.14 | 0.0.15 |
| Simply Screens | 0.9.1 | 0.10.1 |
| Simply Speakers | 0.10.1 | 0.10.2 |
| PacketWeave | 0.1.3 | 0.1.4 |

The other eleven managed pins already match their latest compatible releases.
LittleTiles remains the upstream Forge 1.20.1 beta; original Classic 2.13 is
retained with the standalone Spice of Life integration. OpenUI and Precise
Controls remain client-only; VanishGuard remains server-only.

Minecraft remains 1.20.1 and Forge remains 47.4.13. TFG Core moves from 0.9.29
to 0.9.31; see [the source audit](../docs/upstream-sync-0.13.17.md). Native JAR
dependency declarations are recorded in [the complete custom-mod audit](custom-mod-audit-0.13.17.1.json).

The complete client/server migration payloads use the pristine 0.13.15 upstream
inventory and the official 0.13.17 CurseForge/server exports. Provider artifacts
retain their pinned hashes. Overlay-owned mods are excluded from the base
payload/downloads so obsolete variants cannot be reinstalled. Existing worlds,
identity registries and private media are outside the payload ownership roots.

Release gates: publish a Manager version supporting the reviewed 0.13.17 base
before stable promotion, publish the prepared base assets, and tag the exact
release head. Published Manager 1.0.13 rejects fresh installations of this base.
This preparation does not establish migrated-world startup, interactive client
gameplay or a production deployment. Update clients and server together.
