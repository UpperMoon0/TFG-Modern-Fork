# TFG 0.13.19-nstut.3 ? Distant Horizons Forge compatibility hotfix

- Replace official Distant Horizons 3.3.3 for Minecraft 1.20.1 with the verified UpperMoon0/DistantHorizons Forge fork v3.3.3-nstut.1 (SHA-256 f6d8339b55537baff3a2e45b89b8280373f85ab51821faba35095a8ccaa7c169).
- Fix early Chunky API provider registration (UpperMoon0/DistantHorizons PR #1), which crashed the protected 0.13.19-nstut.2 live rollout during chunk promotion.
- Pin the fork's immutable asset in Pakku and the Modpack Manager managed overlay; remove older DistantHorizons JAR names before installing the fork on client and server.
- Disable Distant Horizons automatic upstream updates.
- No intentional world-generation or save-format changes. Preserve all player data and rollback material.

Production requires signed exact-SHA Jenkins checks, immutable release, verified Manager patch, offline world backup, and live readback. The nstut-0.13.19.2 release remains unchanged.
