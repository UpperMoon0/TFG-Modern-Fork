# TrueUUID fork integration evidence

Fix PR1 and the explicit Forge-only publication path PR2 are merged in
UpperMoon0/TrueUUID. Release v1.3.1 is public and its anonymous download matches
the canonical CI JAR. Complete provenance, asset ID, hash, size, tested commit
and release commit are in trueuuid-fork-candidate.json.

Pakku and Manager pin the exact Forge 1.20.1 JAR for clients and servers with
update_strategy NONE and stale-TrueUUID cleanup. Every other operation and mod
pin is preserved relative to construction cb658e7b. Authentication configuration,
vanilla UUID policy and account files are unchanged. Private VanishGuard data
is never included.

The trueuuid-release-asset CI check verifies public HTTPS availability, exact
SHA-256 and size. Upstream all-loader release_ready stays false; the owner-fork
publisher approves only this Forge 1.20.1 artifact and retains LGPL provenance.

The owner authorized merge, publication, pack promotion and empty-server rollout.
Deployment must use the final immutable pack tag, preserve rollback and existing
account data, and verify startup and installed hash. Genuine live-player login
acceptance remains distinct from build tests or server readiness. No account
migration or policy change is authorized by the dependency update.
