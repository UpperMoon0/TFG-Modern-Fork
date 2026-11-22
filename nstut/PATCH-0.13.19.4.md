# TFG 0.13.19-nstut.4 — Distant Horizons SecureJar correction

- Replace Distant Horizons Forge 3.3.3-nstut.1 with 3.3.3-nstut.2 for client and server.
- SHA-256: a7555a83a0edd250af7ff6b592bff0987e5201c4a1204f7e813565f4c804121f
- Correct final Multi-Release manifest that caused Forge 47.4.13 SecureJar NoSuchFileException during .19.3 promotion.
- Native on-prem-1 build and Forge 47.4.13 + Chunky 1.3.146 isolated server reached Done, saved and shut down cleanly.
- Preserve world, TrueUUID, whitelist, ops, timestamps and rollback backups; no intended world data changes.

Publish only after exact-SHA Jenkins promotion gates and immutable asset readback; deploy using approved Manager CLI with offline snapshot and proof.
