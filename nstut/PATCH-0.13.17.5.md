# TFG 0.13.17-nstut.5 — LDLib fork, Horse Power 1.2.11, and Builder's Multitool

Minecraft 1.20.1 / Forge 47.4.13 / upstream TFG 0.13.17.

This release contains exactly the managed mod and gameplay changes of the previously tagged 0.13.17-nstut.4 integration candidate. The new version and immutable tag exist because the original .4 source did not descend from the current `nstut/stable` release commit, and the promotion gate correctly rejects such lineage. The .4 source tag has **not** been moved or overwritten.

## New content
- Replace upstream LDLib 1.0.52.a with the SHA-256 pinned owner fork `1.0.52.a-nstut.2` on both client and server, removing older `ldlib-*.jar` artifacts first.
- Upgrade Create Horse Power CE 1.2.10 to the published Forge 1.20.1 artifact 1.2.11 on both sides.
- Add a tech-progression-safe IV assembler recipe for Building Gadgets Extra's Builder's Multitool, using all five EV gadgets, two titanium double plates, an IV field generator and an IV circuit (circuit 4, 600 ticks, IV EU/t).
- Retain TrueUUID 1.3.1, since 1.3.2 has no published authorized release artifact. Other custom mod pins are unchanged.

## Compatibility and verification
- LDLib's Forge channel changed to 0.0.2. **Clients and server must upgrade together.** Old clients will not be protocol-compatible.
- Pack validator, base migration, Manager fresh-install policy, manifest hash, and promotion gate must pass before publication.
- **Known verification gap:** client/connected-dedicated-server interactive LDLib RPC targeting and dynamic slot re-use acceptance, JEI/machine crafting for the multitool, and horse cogwheel behavior are not fully verified. Do not mistake passing CI for these tests.
- Rollout requires safe world and identity snapshot, stopping new joins, server shutdown and mod replacement via the official Manager, startup verification, and immediate rollback on errors. Preserve the world, player identity, server configuration, and backups.
- Stable GitHub release publication and live server patching are distinct steps; the manifest is immutable and checksum-pinned.
