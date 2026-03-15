# Version Gotchas (1.21.11)

This file is the shared, version-specific pitfalls list for both capsule and
repo agents. Update it whenever versions change or new issues are discovered.
Include a source link for each entry.

## Current Targets
- Minecraft: 1.21.11
- Fabric API: 0.140.2+1.21.11

## Gotchas
- Item model definitions live in `assets/<namespace>/items/<id>.json`, and the
  `minecraft:item_model` item component points to the resource location for the
  items model. Missing `items/<id>.json` breaks item rendering even if the model
  and texture exist.
  Source: https://minecraft.wiki/w/Items_model_definition
- Data components are now the canonical item data mechanism and partially
  replace NBT for items and block entities. This affects how item data is stored
  and surfaced.
  Source: https://minecraft.wiki/w/Data_component_format
- 1.21.11 Mojang mappings: `BookViewScreen.BookAccess` is a record that takes a
  `List<Component>` and `BookViewScreen` constructors are public but no longer
  accept the `(BookAccess, boolean)` signature. Item `use` returns
  `InteractionResult` and `Level.isClientSide()` is a method, not a field.
  Source: local 1.21.11 mapped jar inspection (Loom cache).
- Resource pack format is now 75.0 for 1.21.11.
  Source: https://minecraft.wiki/w/Java_Edition_1.21.11
- Data pack format is now 94.1 for 1.21.11.
  Source: https://minecraft.wiki/w/Java_Edition_1.21.11
- Block model and block state formats were expanded to allow more rotations.
  Source: https://minecraft.wiki/w/Java_Edition_1.21.11
- New GPU sprite animation shaders and uniform changes were introduced. This
  only matters if custom shaders are shipped or relied upon.
  Source: https://minecraft.wiki/w/Java_Edition_1.21.11
- 1.21.11 has an unobfuscated build (`1.21.11_unobfuscated`) in preparation for
  removing obfuscation from Java Edition. This may affect tooling workflows.
  Source: https://minecraft.wiki/w/Java_Edition_1.21.11
- Fabric API 0.140.2+1.21.11: language provider subclasses can change output
  paths (datagen), and there are small helper API additions and fixes.
  Source: https://github.com/FabricMC/fabric-api/releases/tag/0.140.2%2B1.21.11
