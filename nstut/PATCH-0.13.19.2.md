# TFG 0.13.19-nstut.2 — audited renewable-ore compatibility

Supersedes the unpromoted 0.13.19-nstut.1 candidate without modifying any distributed mod, world contents, recipe definitions, or 0.13.19 base download artifacts. The earlier immutable `nstut-0.13.19.1` tag remains unchanged.

- Re-audits TerraFirmaGreg Core Modern 0.9.34 → 0.9.36. The original KubeJS renewable ore recipes and tags have identical blob hashes; GTCEu remains 7.5.3. TFG's `TFGTagPrefix`, `TagPrefixItemMixin`, `GTMaterialBlocksMixin`, `TFGMaterialHandler`, and `TFGRecipeSchema` binary class payloads are unchanged in the two provider JARs.
- Pins the fail-closed renewable recipe validator to Core Modern 0.9.36 only after the binary comparison. All 90 multi-tier recipes, 49 LV recipes and the mafic slurry builder validator pass in the 0.13.19 test checkout.
- Preserves the migration, Clockwork/MCA/Distant Horizons additions and runtime warnings in [PATCH-0.13.19.1.md](PATCH-0.13.19.1.md); changes to TFC geological world generation and EMI ore display are **not** taken as evidence of successful in-game runtime behavior.

No production deployment is authorized until immutable-source Jenkins policy, promotion and release acceptance pass and a fresh world backup is verified.
