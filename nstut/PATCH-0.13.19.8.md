# TFG 0.13.19-nstut.8 — Distant Horizons full-data response lifecycle

- Forge 1.20.1 client and server both install Distant Horizons `3.3.3-nstut.8` from https://github.com/UpperMoon0/DistantHorizons/releases/tag/v3.3.3-nstut.8.
- JAR: `DistantHorizons-forge-3.3.3-nstut.8-1.20.1.jar` (asset 782510257, size 23,023,566 bytes, SHA-256 `bd03e4cc7691017c755c9884081f3be8cada4ac0edc5600e172d973ab56c109d`).
- Exact source: DH `cab384f5fbbf15d7c2098cebbf040410c3d62c68`, core `54091a15d03178152b5982ec726435dc700c5144`.
- Retains the previously proven TFC 3×3 biome-neighbor and 8-chunk structure-reference corrections. Fixes an early client-level packet race and protects split full-data buffers against cache expiry while requests wait in compression queues; decoded Netty buffers are released.
- Removes DH duplicate jars on both sides and installs immutable checksum-pinned jar and config. Existing player, world, TrueUUID, whitelist and unrelated mod data are not intentionally changed.
- Release hold: require error-free same-version client/server LOD handshake, storage, visible rendering and reconnect, full native Jenkins checks, safe player-offline maintenance and validated rollback prior to production cutover.
