# TFG 0.13.19-nstut.1 — upstream 0.13.19 and reviewed fork additions

Base: TerraFirmaGreg Modern 0.13.19 / Minecraft 1.20.1 / Forge 47.4.13.

- Integrates complete upstream 0.13.19 source (`065edebfa6196056767c3484648286964b949536`) as a real merge descendant of production `nstut/stable`.
- Preserves all 16 immutable NsTut custom-mod artifacts and server-private world/player/identity data.
- Adds Clockwork 0.5.7.1, Valkyrien Skies 2.4.11, Kelvin Lib 0.5.2, MCA Reborn 7.6.26+1.20.1 and Distant Horizons 3.3.3 to both client and server.
- Retains hot spring healing (`hotWaterHealAmount = 0.08`) on Hard, with a source regression check; server runtime behavior must also be checked.
- Caps Distant Horizons generation thread count from 8 to 2 for safe operation on the 4-vCPU production host. Monitor LOD cache growth and bandwidth.
- Retains retired GitHub Actions routes and the protected Jenkins-only release gates.

## Migration and deployment

The 0.13.18 → 0.13.19 migration has independent client and server archives under `nstut-base-0.13.19` and hash-checked per-file downloads. Clients and the dedicated server must update together. Do not copy a live world or private TrueUUID registry into a pack distribution. Preserve a full pre-deployment world/config snapshot and rollback capability. Do not release before the isolated Forge smoke, migration archive, source policy, and promotion gates pass.

## Known dedicated-server shutdown behavior

An isolated full Forge 47.4.13 instance started and saved successfully, but Distant Horizons 3.3.3 left non-daemon chunk-update and full-data worker threads alive after `/stop`. This is reproducible on a fresh test world (independent of the live world). The production TFG wake manager already bounds graceful shutdown to 180 seconds, then terminates a stalled JVM; verify completed world saves before relying on this fallback. Treat it as a known upstream DH 3.3.3 defect, not a clean shutdown. Do not delete rollback snapshots until a live restart and save/reconnect check passes.
