# Upstream 0.13.15 sync

Prepared on 2026-10-21 for the fork's `dev` integration branch.

- Fork base: `2be24d9d75a46186cc7ee7c3f5fe3c01e7c25d2d`.
- Upstream tag: `0.13.15`, commit `21a4caf531e6abb8b992cc83c5a94df7a39fc83a`.
- The upstream Pakku lock is retained exactly, including Minecraft 1.20.1,
  Forge 47.4.13, GTCEu 7.5.3 and TFG Core 0.9.29.

## Conflict resolution

The merge into `dev` had one modify/delete conflict:
`kubejs/assets/tfg/lang/en_us.json`. Upstream removed this pack language file;
the fork had added renewable-material translations. Retain the 25 fork-added
translations only, identified against the common ancestor
`328f2ef0d4337cb8439331f93a302930825b09ba`. Keeping the old complete language
file would restore obsolete upstream overrides. The renewable validator now
requires a nonempty translation for every custom intermediate.

The renewable scripts, registration calls and tags merge with upstream. Both
packaged TFC configurations retain the disabled collapse and landslide settings
from PR #40 while receiving upstream's composter duration change.

## Dependency source review

Compared Core tags `0.9.23` (`4264687194c395b243614c9c898d12de6840773e`)
and `0.9.29` (`1fb4e23e868b1bb28f0a234aaa2c3af0efead60a`) in
<https://github.com/TerraFirmaGreg-Team/Core-Modern> before advancing the
renewable validator's Core pin:

- `GTRecipeTypesMixin.java`: unchanged, including machine recipe input/output
  limits used by the custom chains.
- `TagPrefixItemMixin.java` and the `gtceu/materials` mixins: unchanged,
  including `OrePropertyMixin` byproduct handling.
- `TFGTagPrefix.java`: only a scythe-head generation condition was added;
  poor/rich raw-ore prefixes are unchanged.
- GTCEu remains pinned to 7.5.3. This is a scoped source review, not a claim
  that every upstream gameplay change has been tested.

## Validation and release scope

Run the renewable-chain and TFC-collapse validators and syntax-check changed
KubeJS scripts. Verify that `pakku-lock.json` exactly matches tag `0.13.15`,
that every fork-added translation survives, and that no conflict markers remain.

This PR integrates upstream into `dev`. The separately maintained release
construction branches, 15 managed release-overlay mods, Manager stable pointer,
immutable release tags and live server are not updated by this PR. Bringing
0.13.15 to Manager requires a separate release-construction and migration step.
Packaged client/server startup and gameplay compatibility remain unverified.
