# Overlay 0.13.10-nstut.33: custom-mod refresh

Status: **REPOSITORY PREPARATION ONLY; NOT PROMOTED OR DEPLOYED.**

This update audits all ten UpperMoon0-owned mods already installed in the stable `.32` pack and adds the explicitly requested PacketWeave dependency. Exact release URLs, downloaded SHA-256 digests, sizes, installation sides and packaged dependency declarations are recorded in [custom-mod-audit-0.13.10.33.json](custom-mod-audit-0.13.10.33.json).

## Version changes

| Mod | Previous | Prepared | Installation |
| --- | --- | --- | --- |
| Simply Screens | 0.8.9 | 0.8.11 | Client and server |
| Simply Speakers | 0.9.0 | 0.9.1 | Client and server |
| PacketWeave | absent | 0.1.2 | Client and server |

The other eight installed custom mods already match their latest published stable compatible releases: Economy 0.0.18, OpenUI MC 0.0.12, Create Precise Controls 0.1.1, Create Horse Power CE 1.2.7, Building Gadgets Extra 0.0.4, Perfomant Boom 1.1.3, Celestial Nail 0.1.6 and Spice of Life Integrations 0.1.0. OpenUI and Precise Controls remain client-only. All eleven selected custom JARs were independently downloaded and matched to their official GitHub release SHA-256 and size.

No installed custom mod has only a prerelease upgrade. Biotech, NsTut-Lib, Endless and Firstworks are not installed in this fork and are not added. Extra Gauges is a third-party project. Its pin and the other third-party pins remain unchanged. Forge 47.4.13 and Minecraft 1.20.1 remain unchanged.

## Compatibility and migration

- Use the standalone `packetweave-forge-1.20.1-0.1.2.jar`, not the core-only, Fabric or NeoForge asset. It embeds its own transfer core; no separate core JAR is needed.
- Screens requires PacketWeave >=0.1.1; Speakers requires >=0.1.2. The selected 0.1.2 satisfies both. The required Architectury, client OpenUI and Speakers Patchouli dependencies are already present in the pack.
- **Update clients and server together before reconnecting.** Speakers 0.9.1 changes its transfer protocol; mixed old/new Speakers installations are unsupported. PacketWeave must be present on both sides.
- Existing Screens/Speakers media, world data and runtime configuration are retained. No migration script is run by this repository update. PacketWeave cleanup removes stale standalone/core/other-loader copies before installing the one pinned Forge JAR.
- The prior [Spice of Life integration migration warning and pending runtime checks](PATCH-0.13.10.32.md) still apply. `pending-integrations.json` retains that `.32` evidence; this refresh does not claim those checks passed. Never combine the standalone integration with the emergency binary-patched Classic JAR.

## Validation and promotion boundary

Run the manifest generator and policy validator from the repository root:

    python nstut/tools/generate-modpack-manager-manifest.py
    python nstut/tools/validate.py

Validation performed on 2026-10-13:

- Manifest generation, complete NsTut policy validator and `git diff --check`: passed.
- Independent review: all eleven custom JARs and their dependencies checked; ten negative mutation tests rejected broken transfer-stack pins.
- Pakku fetch: exit 0. All 290 locked projects have downloaded bytes matching at least one pinned provider artifact (projects can have different CurseForge/Modrinth alternatives).
- Pakku export: exit 0; CurseForge, Modrinth and server archives generated and passed ZIP CRC validation.
- PacketWeave's exact SHA-256 verified inside CurseForge/client and server archives. Server archive excludes client-only OpenUI/Precise Controls. Modrinth index references the exact Screens 0.8.11, Speakers 0.9.1 and PacketWeave 0.1.2 downloads as required on both sides.
- Managed-overlay simulation for client and server: exact new JAR bytes verified, old Screens/Speakers and stale PacketWeave core/other-loader names removed, exactly one current transfer-stack JAR remains per mod. Client installs 15 managed mods; server installs 13.

**Existing export limitation:** the unchanged `redistributable: false` entries mean raw CurseForge/client and server archives omit Economy, Building Gadgets Extra, Screens and Speakers. These archives alone are not a complete runnable custom pack; use the managed overlay to obtain the exact official artifacts. The Modrinth index uses download references. Distribution policy was not changed as part of this refresh. Runtime startup, join and media playback remain untested.

Policy checks now reject missing/old PacketWeave, wrong-loader transfer-stack pins, mismatched hashes/URLs and client-only installation of any transfer-stack component.

The candidate starts from the current stable tree and is proposed into the `nstut/0.13.10` release-construction branch, following the recent `.32` preparation workflow. The older `dev` branch does not contain the current stable managed-mod infrastructure; merging it into stable would discard unrelated approved changes.

`nstut-0.13.10.33` is a reserved future source reference, not a published tag. Do not use this draft manifest for deployment before completing the documented immutable-tag and stable-promotion procedure. No stable pointer, immutable deployment tag, release publication, server, updater or live configuration is changed by preparation. Packaged exports and metadata checks do not establish interactive client join, media upload/playback or dedicated-server runtime compatibility.
