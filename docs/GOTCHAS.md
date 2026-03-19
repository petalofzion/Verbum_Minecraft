# Version Gotchas (26.1-pre-3)

This file is the shared, version-specific pitfalls list for both capsule and
repo agents. Update it whenever versions change or new issues are discovered.
Include a source link for each entry.

## Current Targets
- Minecraft: 26.1-pre-3
- Fabric API: 0.143.14+26.1
- Java: 25
- Loom: 1.15.5

## Gotchas
- 26.1 snapshots use the unobfuscated game jars. Build script migration is required:
  use the modern Loom plugin id, remove the old `mappings` dependency line, and
  replace old `modImplementation` usage with normal dependency configurations
  where required by the 26.1 snapshot tooling.
  Source: [Fabric porting guide](https://docs.fabricmc.net/develop/porting/next)
- The Minecraft dependency coordinate and Fabric Loader's runtime version string
  are not identical for this snapshot line. Verbum uses `26.1-pre-3` in Gradle
  coordinates, but `fabric.mod.json` must target the loader-visible form
  `26.1-pre.3` for dependency resolution to pass.
  Source: local `:assemblies:veritas:runClient` smoke on 2026-03-19.
- Java 25 is required for this baseline, including Gradle toolchain resolution
  and IDE support.
  Source: [Fabric porting guide](https://docs.fabricmc.net/develop/porting/next)
- Custom GUI screens are on the new extractor-based rendering pipeline. Old
  `GuiGraphics`-based overrides no longer compile; custom screens must use
  `GuiGraphicsExtractor` and extractor methods such as `extractBackground`,
  `extractLabels`, and `extractRenderState`.
  Source: local Verbum migration compile against 26.1-pre-3 on 2026-03-19.
- Custom container screens now need the image dimensions passed through the
  `AbstractContainerScreen` constructor instead of assigning `imageWidth` and
  `imageHeight` afterward.
  Source: local Verbum migration compile against 26.1-pre-3 on 2026-03-19.
- Some Fabric helper packages moved:
  - creative tab events are under `net.fabricmc.fabric.api.creativetab.v1`
  - key mapping helpers are under `net.fabricmc.fabric.api.client.keymapping.v1`
  Source: local 26.1 dependency inspection and compile migration on 2026-03-19.
- Player-facing feedback methods changed in the runtime path used by Verbum:
  `Player.sendSystemMessage(...)` is available where old `displayClientMessage`
  calls no longer compile.
  Source: local Verbum migration compile against 26.1-pre-3 on 2026-03-19.
- `EditBox` input filtering changed. Verbum’s numeric page-jump fields now need
  responder-based sanitization instead of the removed `setFilter(...)` hook.
  Source: local Verbum migration compile against 26.1-pre-3 on 2026-03-19.
- Item model definitions still depend on `assets/<namespace>/items/<id>.json`
  and the `minecraft:item_model` item component. Keep verifying this path during
  the 26.1 migration because item rendering will fail even when models/textures
  exist if the item definition file is missing.
  Source: https://minecraft.wiki/w/Items_model_definition
- Data components remain the canonical item data mechanism; continue treating
  them as the main item/block-entity data surface instead of legacy NBT-first
  assumptions.
  Source: https://minecraft.wiki/w/Data_component_format
