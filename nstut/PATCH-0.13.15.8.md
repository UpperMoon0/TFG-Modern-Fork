# TFG 0.13.15-nstut.8 — TrueUUID rejected-login fix

Updates TrueUUID from upstream 1.3.0 to the owner fork's published Forge 1.20.1
build 1.3.1 on clients and servers. Rejected/disconnected sessions stay terminal;
cleanup and delayed callbacks cannot reopen vanilla login acceptance. Existing
premium and policy-approved offline authentication keep their protocol and policy.

Relative to stable .6, this release also includes the previously reviewed
VanishGuard 0.1.0 server-only addition from PR47. Clients do not install
VanishGuard. All other mod pins are unchanged. Private UUID configuration is
server-local and is not shipped in this pack.

No authentication configuration or account migration is part of this update.
The source fix passes 17 controller regressions (14 fail upstream), all 132
Forge/shared Linux tests and its full verification matrix. The JAR is
reproducible and its public download is hash-verified. These tests do not claim
that a particular player's prompt is resolved or substitute for genuine live
player-login acceptance.

Update through Modpack Manager with Minecraft closed. Server rollout requires
an empty-player maintenance window and preserves world/account data and rollback.
