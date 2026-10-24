# TFG 0.13.15-nstut.6

Updates Create Horse Power CE from 1.2.7 to the official 1.2.8 Forge 1.20.1
release on both clients and servers. This fixes horse ownership restoration and
Create kinetic-network recovery when crank chunks reload or the server restarts.
All other 14 managed-mod pins, upstream 0.13.15 files, recipes, runtime settings,
and migration payloads remain unchanged.

The official asset is `createhorsepower-ce-1.20.1-1.2.8.jar` (469,478 bytes),
SHA-256 `ff51780958fb24e038f3f7db7b1ae75cc0479b66c48e35974aac63d586151d33`.
It was published from CreateHorsePower-CE merge commit
`ebedf15def38e977ed4d8e4cbf29347e93213481` after PR #29. Downloaded bytes match
the GitHub release digest. Forge metadata requires Minecraft 1.20.1, Forge 47+
and Create 6.0.8 through below 6.1.0; the pack pins Forge 47.4.13 and Create 6.0.8.

Both crank-first and non-source-chunk-first isolated process-restart tests passed
with four horses and 29 kinetic nodes. The official artifact's runtime classes
and resources match the tested candidate; only its manifest build timestamp
differs. This does not claim an interactive client test or full live-layout
restart proof.

Close Minecraft and update clients through Modpack Manager. Its existing stable
TFG feed resolves this immutable overlay; no Manager application version bump is
needed. The published Manager v1.0.13 CLI is used for release compatibility and
rollout checks. Existing server worlds and player data are preserved. The
previous immutable overlay `nstut-0.13.15.5` remains available for rollback.
