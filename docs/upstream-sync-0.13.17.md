# Upstream 0.13.17 integration audit

Upstream pack tag: `32ba9f19d60bfc5b4148888fc84e50316b2b0fed`.
GTCEu remains 7.5.3. TFG Core changes from 0.9.29
(`1fb4e23e868b1bb28f0a234aaa2c3af0efead60a`) to 0.9.31
(`6eb1127365289086b45814f1799c3e6c57fd1367`).

The complete Core source comparison preserves `TFGModifyMaterials`,
`TagPrefixItemMixin`, `TFGMaterialInfoModification`, `TFGMaterialHandler`,
`TFCItems` and `Ore`. The renewable chains' material substitutions, dust/ore
prefix behavior and graded ore IDs therefore retain their audited contracts.
`TFGKubeJSPlugin` only adds the `TFGRockGetters` binding; existing recipe
schemas and bindings remain present. `CollapseRecipe.tryTriggerCollapse` adds
an early return when block collapsing is disabled. Our enabled collapse
configuration and finished-building tag protections remain applicable.

Source comparison:
https://github.com/TerraFirmaGreg-Team/Core-Modern/compare/0.9.29...0.9.31

Validation still requires the exact Core and GTCEu artifacts, recipe IO and
bounds, material declarations, translations, and natural-terrain/building
collapse behavior. These source checks do not establish live world startup,
client rendering or interactive recipe execution.
