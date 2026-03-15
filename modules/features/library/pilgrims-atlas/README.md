# Pilgrim's Atlas Capsule

This capsule provides a Visions profile manual as a library-backed book item.
It gives players a concise field-guide orientation to the flagship line: broad, luminous, and feature-rich.

## Scope
- Library-backed profile manual registration via `FeatureEntrypoint`.
- Packaged manual text for offline reading.
- Pure data and logic; no direct Minecraft/Fabric dependencies.

## Capsule Docs
- `docs/PRD.md`
- `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/` (issues/questions/decisions)

## Key Files
- `module.json`: module metadata and dependency declarations.
- `src/main/java/.../PilgrimsAtlasFeature.java`: feature entrypoint.
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`: SPI registration.

## Asset Checklist (Item)
- `src/main/resources/assets/verbum/items/pilgrims_atlas.json`
- `src/main/resources/assets/verbum/models/item/pilgrims_atlas.json`
- `src/main/resources/assets/verbum/textures/item/pilgrims_atlas.png`
- `src/main/resources/assets/verbum/lang/en_us.json`

## Asset Checklist (Library Book)
- `src/main/resources/assets/verbum/books/pilgrims_atlas@visions.txt`
