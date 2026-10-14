# Renewable-resource source audit for upstream 0.13.12

The pack keeps GTCEu 7.5.3 and moves TFG Core from 0.9.23 to 0.9.25.
Source tags inspected: `TerraFirmaGreg-Team/Core-Modern` 0.9.23
(`4264687194c395b243614c9c898d12de6840773e`) and 0.9.25
(`f4929e738e83dbc8d46680276faa67520dffa172`).

- `TFGModifyMaterials`, `TagPrefixItemMixin`, and `TFGMaterialInfoModification`
  are unchanged between these tags.
- `TFGMaterialHandler` changes only anvil substitutions for VanadiumSteel,
  StainlessSteel and Tungsten, plus the Steel drill-head substitution. It does
  not change the renewable chains' ore or dust substitutions.
- `TFGKubeJSPlugin` adds the gas-burner fuel schema; its existing recipe-map
  registration is retained.
- Core now embeds TFC, still with mod ID `tfc`. Its `TFCItems.GRADED_ORES`
  registers `ore/<grade>_<ore>` and `Ore` retains POOR/NORMAL/RICH plus all seven
  ores used by the custom renewable routes.
- The pack's 89 renewable recipes and 73 custom material declarations retain
  their source checks. Updating the Core pin does not disable recipe bounds,
  collision checks, material checks, or translation checks.

This source audit supports updating the validation pin to 0.9.25. It does not
establish migrated-world gameplay, client rendering or recipe execution; those
are separate runtime gates.
