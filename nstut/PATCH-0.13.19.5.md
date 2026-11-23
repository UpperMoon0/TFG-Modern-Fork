# TFG 0.13.19-nstut.5 — server-side Distant Horizons TFC biome fix

- Upgrade Distant Horizons Forge to `3.3.3-nstut.3` on **client and server**, GitHub asset ID `781488186`.
- Release: https://github.com/UpperMoon0/DistantHorizons/releases/tag/v3.3.3-nstut.3
- SHA-256: `ea01b3da475bcbe41d3e679c804655b846ba8fd677471f0f404c068b00f8ed70` (23,078,424 bytes).
- TFC's feature decorator scans a 3×3 neighborhood of biomes; DH's previous zero-border feature generation supplied uninitialized neighbor chunks and caused 37 `NullPointerException: Biome: 211` failures on the live previous-version world.
- DH now builds a one-chunk biome margin for TFC and KubeJS-TFC generators, decorating only the complete interior. Non-TFC generation behavior remains unchanged.
- Native on-prem-1 Forge 1.20.1 `:forge:assemble`, SecureJar verification and geometry regression passed.
- **Acceptance still required:** isolated TFG/TFC generation and real client/server LOD transfer, exact SHA Jenkins policy/promotion and GitHub App checks. Do not treat this as a production-tested fix.
- No intentional changes to world, player, TrueUUID, whitelist, ops, or other mods. Preserve rollback releases and take a complete offline world snapshot before deployment.
