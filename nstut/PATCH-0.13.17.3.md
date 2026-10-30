# TFG 0.13.17-nstut.3 — custom-mod compatibility refresh

Upstream base: **TerraFirmaGreg Modern 0.13.17** (Minecraft 1.20.1 / Forge 47.4.13).
This pack release refreshes four of the sixteen managed custom mods. It does
**not** patch, restart, or migrate the live TFG server.

## Updated custom mods

| Mod | Previous | New | Reason |
| --- | --- | --- | --- |
| Building Gadgets Extra | 0.0.7 | 0.0.8 | Fix production CopyGUI Mixin crash and preserve typed coordinate edits |
| Create Horse Power CE | 1.2.8 | 1.2.10 | Crank/worker recovery and optional Create: Bionics integration |
| Simply Screens | 0.10.1 | 0.10.2 | Bounded image transfer, receipt-driven scheduling and stale-cache cancellation |
| PacketWeave | 0.1.4 | 0.1.5 | Shared authenticated, bounded send/receipt scheduler required by Screens 0.10.2 |

The remaining **12 managed pins stay unchanged** after the Forge 1.20.1
release audit. In particular, OpenUI MC 0.0.15, Simply Speakers 0.10.2,
Economy 0.0.21, TrueUUID 1.3.1, Spice of Life Integrations 0.1.1, and server-only
VanishGuard 0.1.0 are retained. LittleTiles, Extra Gauges and Spice of Life:
Classic remain at their verified Minecraft 1.20.1-compatible provider artifacts.

## Installation and compatibility

- **Update both client and server together** when server deployment is separately authorized. Screens 0.10.2 requires PacketWeave 0.1.5 or newer; a mixed media-transfer stack is unsupported.
- Use the stable Modpack Manager channel after this candidate passes immutable-tag, policy, migration and fresh-install validation. Close Minecraft before applying an update.
- This release changes only managed pins/Pakku metadata, audit/release documentation and the immutable Manager manifest; it retains upstream base payloads, normal configs, protected world/identity state and gameplay recipe policy.
- No live TFG service, player data, authentication configuration or installed server JARs are changed by publication.

## Verification limits

Official published Forge 1.20.1 release-asset SHA-256 digests were used for
all four changes; the audit records exact asset IDs, sizes and hashes. Pack
policy/Manager compatibility and combined runtime tests must pass as part of
promotion; **a successful GitHub release alone is not proof of live server
compatibility**. Building Gadgets Extra's full coordinate-edit interaction test
and Horse Power's optional Bionics two-client acceptance remain known separate
runtime-verification limits.
