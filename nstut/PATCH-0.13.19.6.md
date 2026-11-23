# TFG 0.13.19-nstut.6 — DH/TFC feature-generation candidate

- Pin **Distant Horizons Forge 1.20.1 `3.3.3-nstut.6`** on both client and server. This supersedes the broken `.3` staged candidate; production remains on `.2`.
- Prerelease: https://github.com/UpperMoon0/DistantHorizons/releases/tag/v3.3.3-nstut.6
- GitHub asset ID: `782130788`; filename: `DistantHorizons-forge-3.3.3-nstut.6-1.20.1.jar`; size: `23022905` bytes.
- SHA-256: `fbefec799ede70ddebb1b16aa66760a23892469a65a833066a43c623ae88ec1e`.
- Root cause: DH's TFC-specific extra biome ring was incorrectly processed during structure references; its temporary adjacent ProtoChunks also exposed Minecraft's default `minecraft:plains` (numeric biome ID `211`) to TFC feature decoration. The fix keeps structure searches inside allocated bounds and repairs only actual default biome values in temporary TFC ProtoChunk neighbors; persisted LevelChunks are untouched.
- Verification: DH geometry/source regression **PASS**; Python syntax **PASS**; Forge 1.20.1 `:forge:build` **PASS**; SecureJar check **PASS**. Isolated 234-mod TFC server reached `Done` and completed `dh pregen start minecraft:overworld 0 0 32` (32/32, approximately 20 cps), with SQLite `FullData` **5 → 397** and `quick_check = ok`; zero `Biome: 211`, feature-generation or structure-reference exceptions.
- **Release hold:** end-to-end real client/server LOD synchronization, native Jenkins exact-head acceptance, signed Manager manifest and checksum readback, complete offline backup and rollback have not been accepted. Do not merge/promote or restart production until those gates pass.
- No intentional world, player, TrueUUID, whitelist, ops or unrelated mod changes.
