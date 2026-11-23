# TFG 0.13.19-nstut.10 — accepted DH v5 native regression tests

Supersedes the **unpromoted**, immutable `nstut-0.13.19.9` tag. That tag is deliberately **not moved**. No world, player, TrueUUID, gameplay, mod binary, or safety-policy changes beyond the reviewed 0.13.19-nstut.9 candidate.

## Fix

Jenkins policy build #89 and native release #27 correctly failed two stale assertions in `nstut/tools/test-manifest-targets.py`: the test pinned Distant Horizons `3.3.3-nstut.8` despite the reviewed `.9` artifact, and expected semantic overlays to equal the 0.13.17.5 baseline even though the new DH v5 policy is intentional. Update both assertions without weakening any existing policy: all old overlays must remain byte-for-byte equivalent, with **exactly one** DH v5 semantic TOML patch added for both client/server. Continue checking a known DH .9 SHA256, the exact filename, and both-side cleanup/install. Native validator and Manager idempotence coverage remain required.

## Immutable artifacts

- Distant Horizons Forge 1.20.1 `3.3.3-nstut.9`, asset ID `783916779`, SHA-256 `dd42f36b06af4c8c554deec6aba591705154080530c938c072703cf7d41825cd`, from https://github.com/UpperMoon0/DistantHorizons/releases/tag/v3.3.3-nstut.9.
- Modpack Manager manifest uses `0.13.19-nstut.10`, with 22 pinned `nstut-0.13.19.10` fork-source URLs; DH TOML remains a semantic `patchToml` operation, never a full-file `installFile`.
- Source tree requires fresh full native validation and **new signed Jenkins acceptance** on the exact new immutable tag. Do not reuse failed build #89/#27 or the old .9 tag receipt.

Production requires a new consistent offline backup, qualified player-free maintenance window, rollback, full client/server DH test and two reboots with zero subsequent Modpack Manager changes/warnings. Do not reapply old v4 TOML to the running server.
