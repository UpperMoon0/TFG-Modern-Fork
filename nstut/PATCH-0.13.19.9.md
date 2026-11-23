# TFG 0.13.19-nstut.9 — DH v5 config drift follow-up

Tracks [TFG #93](https://github.com/UpperMoon0/TFG-Modern-Fork/issues/93) and [DH #6](https://github.com/UpperMoon0/DistantHorizons/issues/6).

- Preserve immutable .8 release tag, DH binary and production rollback.
- Pin **DH Forge 1.20.1 3.3.3-nstut.9** on both client/server: https://github.com/UpperMoon0/DistantHorizons/releases/tag/v3.3.3-nstut.9, asset ID `783916779`, 23,081,143 bytes, SHA-256 `dd42f36b06af4c8c554deec6aba591705154080530c938c072703cf7d41825cd`. This source is the exact-tree-reviewed merge of DH PR #7; the known TFC background noise generation future is classified INFO once, while unknown generators retain WARN and every future still joins before the next stage.

- The DH core v5 loader **deletes** older v4 configuration; it does not migrate its values. The .8 full-file install made Modpack Manager repeatedly report drift.
- Supply a v5-native template derived from the live v5 file; remove host-specific `server.serverId`, disable client automatic and silent updates, preserve a two-thread budget and generation limits, enable adaptive transfer as in pinned v4, and retain the .8-tested `FEATURES` + `SURFACE_THEN_CHUNKS` modes.
- Use a single idempotent semantic `patchToml` operation on both client/server, not a full-file `installFile`. Unmanaged GUI settings, comments and generated server identity remain untouched.
- Deliberately retain .8 runtime `FEATURES`: v4 `INTERNAL_SERVER` was reset on first boot, but restoring it without testing may write vanilla chunks and increase server tick load. Evaluate separately in an isolated TFC workload.
- Require native validator, Jenkins exact-SHA tests, client/server generation + LOD transfer, boot/reboot twice with zero Manager changes/warnings, rollback before immutable tagging/promotion or any production restart.
