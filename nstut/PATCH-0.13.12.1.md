# 0.13.12-nstut.1 migration candidate

Status: preparation and validation only. Production remains 0.13.10-nstut.33.
The future `nstut-0.13.12.1` deployment tag is reserved, not published.

## Base and preserved customizations

The candidate merges upstream tag 0.13.12
(`4b4732760b2885db45832a07f2925ba10f4c5930`) into the existing stable
history. This is an upstream prerelease, including the 0.13.11 gameplay
changes and 0.13.12 dedicated-server/Linux recipe fixes.

All 15 managed mod artifacts are retained from .33, including Simply Screens
0.8.11, Simply Speakers 0.9.1 and PacketWeave 0.1.2. The CE Horse Power
replacement, renewable ore routes, recipe fixes, 512-bucket Economy storage,
TrueUUID policy and semantic server overlays remain present. Upstream mod
artifacts retain their exact 0.13.12 pins. The removed upstream TFG language
file is replaced with only our 73 custom material names, avoiding restoration
of obsolete upstream translations. See CORE-AUDIT-0.13.12.md for the Core pin audit.

## Upgrade installation boundary

The Manager manifest remains an overlay on a matching upstream 0.13.12 base.
Applying it directly over a 0.13.10 installation does not upgrade upstream
mods, remove obsolete upstream scripts, or replace upstream configuration.
Do not promote the candidate as an in-place .10 upgrade without a complete
base-upgrade mechanism.

The candidate's complete client/server exports include `.nstut-tfg-base-0.13.12`.
The overlay requires this marker, so existing Modpack Manager versions reject
unmigrated .10 installations before any patch operation. Do not manually add
the marker to an old installation to bypass this check.

The migration path for this candidate is a fresh complete 0.13.12 pack with
the custom managed overlay applied, followed by copying preserved world,
identity and server-owned data while stopped. Do not copy the old mods or
entire old kubejs/config directories over the new installation. Review and
carry over individual runtime settings, serverconfig values, identity registry,
player data, media storage, permissions, JVM settings and service bindings.
Server-private identity files must never enter public exports.

Raw exports preserve the existing redistributable=false policy and can omit
custom JARs. Apply the managed overlay before calling an installation complete.
The generator's future tag URLs must be replaced with local artifact paths in
disposable staging only; never retag or publish an unreviewed candidate to run tests.

## Required release gates

Completed preparation evidence is recorded in [validation-0.13.12.1.json](validation-0.13.12.1.json).
All 291 downloaded projects match provider artifact hashes. Full policy checks,
89 renewable recipes, upstream pin checks and 12 regression cases pass.
CurseForge, Modrinth and server archives pass CRC checks; all 12,371 client
asset files are preserved after simplifying the recursive export selector.
Packaged base markers are present on both sides. Manager 1.0.6 rejects an old-base
fixture, applies the complete server overlay and produces an empty subsequent plan.

A disposable copy of the stopped .33 world reached authenticated readiness under
Java 17 in a private network with a 4-GiB heap, 6-GiB memory cap and one CPU of
quota. All 130 startup and 346 server scripts loaded with zero script errors or
warnings. Game ticks advanced, the idle server reported 20 TPS, and it saved all
dimensions and exited cleanly. This is a startup smoke check, not a loaded-world
performance benchmark or comprehensive gameplay test.

### Upstream-removed registry entries

The copied world's registry table contains seven entries removed by the new AE2
and Fluid Logistics versions (five item IDs and two block IDs). A read-only scan
of 572,460 serialized region/entity/POI chunks and 327 standalone data files
found only one reference: a Create factory-panel filter using
`fluidlogistics:waterproof_cardboard_block`. Parsing that chunk's block palettes
found zero placed blocks of that removed type. No matching AE2 references were
found within this scan's scope. This does not cover nested custom compressed
storage payloads or changes made after the snapshot.

Review or clear/remap that legacy filter in the migration copy before production
rollout. Preserve the untouched original world and make a fresh live backup.
The startup check must not be interpreted as proof that every removed registry
entry can be discarded without affecting player content.

- Full NsTut policy, upstream artifact preservation and renewable recipe checks.
- Complete client/server exports and archive/artifact checks.
- Normal dedicated-server startup on a disposable copy of the existing world,
  with isolated ports and services and bounded resources.
- Packaged client join, Screens/Speakers transfer and playback, and Spice of Life
  integration behavior with the newly embedded TFC implementation.
- Review oxygen distributors/heat/gravity equipment, gas burners, AE2 recipe and
  machine changes, Fluid Logistics gauge conversion and changed recipe circuits.
- Back up the live instance and coordinate the complete base upgrade on server
  and clients before reconnecting.

After review, merge into nstut/0.13.12, create the exact-head immutable tag,
pass the promotion gate, and promote through nstut/stable. Keep the current
stable pointer until the base-installation migration and runtime gates are ready.
