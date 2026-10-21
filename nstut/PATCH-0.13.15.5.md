# TFG 0.13.15-nstut.5

Refresh all custom-mod pins against their published Forge 1.20.1 releases,
checked on 2026-10-21. Six upgrades are available:

| Mod | Previous | Updated |
| --- | --- | --- |
| Economy | 0.0.18 | 0.0.20 |
| OpenUI MC | 0.0.12 | 0.0.14 |
| Simply Screens | 0.8.11 | 0.9.1 |
| Simply Speakers | 0.9.1 | 0.10.1 |
| Building Gadgets Extra | 0.0.4 | 0.0.7 |
| PacketWeave | 0.1.2 | 0.1.3 |

Create Precise Controls 0.1.1, Create Horse Power CE 1.2.7, Extra Gauges 2.0.7,
Perfomant Boom 1.1.3, Celestial Nail 0.1.6, TrueUUID 1.3.0, LittleTiles
1.6.0-pre161, Spice of Life Classic 2.13 and Spice of Life Integrations 0.1.0
already match their latest compatible published versions. LittleTiles remains
on its existing beta; no newer compatible beta was available.

Downloaded upgrade JARs match GitHub's published SHA-256 digests. Their Forge
metadata confirms Minecraft 1.20.1 support. Screens and Speakers require OpenUI
0.0.14 on clients; Building Gadgets Extra requires PacketWeave 0.1.3 on both
sides. Existing Building Gadgets 1.0.8 and Architectury 9.2.14 satisfy the
remaining dependencies. OpenUI remains client-only.

Update clients and server together before reconnecting: the media/gadget
protocols changed. Close Minecraft before updating through Modpack Manager.
The upstream base remains 0.13.15; existing 0.13.15 installations receive only
the overlay changes. The previous full-base migration remains available for
0.13.12 installations.

All custom JARs are now owned exclusively by the overlay rather than also
appearing in base-migration downloads. This prevents a later update or repair
from reinstalling an older custom JAR alongside the reviewed version. A
regression test rejects this duplication.

The enabled TFC collapse settings, finished-building exclusions, unstable
cobblestone, 73 material names and 90 renewable recipes are preserved. The audit
records every reviewed pin and the upgraded JAR dependency declarations in
`custom-mod-audit-0.13.15.5.json`. Packaged-client gameplay remains unverified.
