# TFG 0.13.19-nstut.7 — DH client packet startup race fix

- Both client and server pin Distant Horizons Forge 1.20.1 `3.3.3-nstut.7` from https://github.com/UpperMoon0/DistantHorizons/releases/tag/v3.3.3-nstut.7.
- Immutable JAR: `DistantHorizons-forge-3.3.3-nstut.7-1.20.1.jar`, asset `782356935`, 23,022,882 bytes, SHA-256 `bd504cd412293bfc46a91fcf8c646da49d369ff8ab678afe44d1e6b216a350a4`.
- DH source `b27b1ac6760019091002ca3abec8c9e34007d7ee`, core fix `30a139d0cb641f6b61efa9ec38c6ebe702867caf`.
- Addresses the real Forge client↔server test defect where four full-data LOD packets raced the `DhClientLevel.clientside` constructor and raised `NullPointerException` before initialization.
- Preserves the previously verified TFC temporary ProtoChunk biome-neighbor repair and structure-reference safety. Prior .6 full 234-mod TFC worldgen reached 32/32 radius with 397 persisted LODs and no biome generation errors.
- Both-side DH cleanup removes older JAR names before installing the checksum-pinned binary and config. Does not intentionally change worlds, players, TrueUUID, or unrelated mods.
- **Release gate:** require clean .7 client/server transfer, reconnect and rendering evidence, passing native exact-head Jenkins checks, full offline rollback and players-offline deployment before promotion.
