# TFG 0.13.15-nstut.7 candidate: VanishGuard

Draft source integration only. This change does not promote the stable feed,
install anything on the live server, configure a real player, or restart it.

Adds public VanishGuard 0.1.0 for Forge 1.20.1 on servers only, using the official
29,683-byte `vanishguard-1.20.1-0.1.0.jar`, SHA-256
`d9e73e37e6ca9794f2e8458e6330fcc77569bf78a1a41ea2571dad0f205dfb9d`.
Source release: https://github.com/UpperMoon0/VanishGuard/releases/tag/v0.1.0.
The source commit is `b9db4596798b23bac7610cac0858672fdf706f63`.

No client mod is required or installed. Client operations and all 15 existing
managed-mod pins remain unchanged. Cleanup of old VanishGuard JARs is also
server-only. No Modpack Manager application update is needed.

The mod creates `config/vanishguard.json` only when absent, with an empty UUID
list and observer mode enabled. Configure real player UUIDs privately on the
server. This public fork intentionally contains neither that config file nor a
Manager operation replacing it, so subsequent pack updates preserve it.
Configuration is startup-only; activation requires a separately authorized
server restart. Hidden observers are placed in spectator mode.

The source release passed 94 tests and isolated vanilla-protocol integration
covering player-list/entity visibility, delayed skin-refresh packets, login,
status/query, dimension changes and respawn. This draft's pack checks cover
server-only targeting, unchanged client operations, exact artifact pins and
private-config preservation. No live activation or live gameplay is claimed.
