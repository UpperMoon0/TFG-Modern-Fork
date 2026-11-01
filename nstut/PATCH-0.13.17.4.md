# TFG 0.13.17-nstut.4 — LDLib fork and Builder's Multitool (integration candidate)

Base: TerraFirmaGreg Modern 0.13.17, Minecraft 1.20.1 / Forge 47.4.13.

This candidate **does not patch the live server or authorize a stable promotion**.

## Managed mod changes

| Mod | Old | Candidate | Artifact status |
| --- | --- | --- | --- |
| LDLib | Upstream `1.0.52.a` | NsTut `1.0.52.a-nstut.2` | GitHub **prerelease**, Forge 1.20.1 JAR, SHA-256 pinned |
| Create Horse Power CE | `1.2.10` | `1.2.11` | Published GitHub release, Forge 1.20.1 JAR, SHA-256 pinned |

Pakku no longer resolves upstream `ldlib`; it locks `UpperMoon0/LDLib-MultiLoader` instead. The managed installation removes any prior `ldlib-*.jar` on **both clients and servers**, then installs exactly one checked fork JAR. The base-migration download lists now omit the upstream LDLib JAR entirely on both sides. Managed cleanup also removes pre-existing LDLib JARs before installing the fork.

The fork fixes RPC target indexing and stale/reused modular-UI slots. The Forge networking channel is now `0.0.2`; **do not mix old/new clients and servers**. Passing JUnit and an isolated Forge/GTCEu server smoke test is not the same as a connected client/server acceptance run.

Create Horse Power CE `1.2.11` uses the reviewed published Forge 1.20.1 artifact. No other custom-mod **published** Forge 1.20.1 release is newer than the existing pack pin as of 2026-11-01. In particular, TrueUUID `1.3.2` is only a merged, unapproved release candidate; the public verified `1.3.1` JAR stays installed. Simply Speakers remains at its latest published `0.10.2` until `0.10.3` ships.

## Building Gadgets Extra: Builder's Multitool

The addon already registers `buildinggadgetsextra:builders_multitool`, but its stock crafting recipe consumes vanilla Nether resources and bypasses TFG's five EV-gadget progression. The KubeJS pack now **removes that stock recipe** and adds a **GTCEu IV assembler** recipe using:

- All five Building Gadgets 2 tools: Building, Exchanging, Copy/Paste, Cut/Paste, Destruction
- Two titanium double plates, one IV field generator, and one IV circuit
- Integrated circuit setting 4, 600 ticks, IV voltage

The exact item ID and the five input tools were checked against the addon's own Forge 1.20.1 recipe and the pack's existing EV gadget recipes. The new recipe is statically validated. Confirm JEI/EMI visibility and a successful machine craft in an isolated TFG instance before promotion.

## Verification and release gates

- `nstut/tools/validate.py` must pass (managed pins, single-LDLib replacement, recipe policy).
- The generated Modpack Manager manifest must be current and all URLs/hashes immutable.
- Client + server must start with no duplicate LDLib; test GTCEu machine GUI, RPC targeting, removal/reuse of UI slots, and reconnect.
- Confirm Horse Power CE `1.2.11` worker/cogwheel behavior and the IV multitool recipe in a non-production world.
- Only then create/tag the final `nstut-0.13.17.4` release-construction commit and promote into `nstut/stable` through the normal gate.
- No live server restart, release deployment, or player/world data modification is part of this candidate.
