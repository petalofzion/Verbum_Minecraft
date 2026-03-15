# Dusty Devotional Capsule

This capsule provides a Veritas profile manual as a library-backed book item.
It offers a short orientation to how baseline Verbum should feel: clear, durable, and grounded.

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
- `src/main/java/.../DustyDevotionalFeature.java`: feature entrypoint.
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`: SPI registration.

## Asset Checklist (Item)
- `src/main/resources/assets/verbum/items/dusty_devotional.json`
- `src/main/resources/assets/verbum/models/item/dusty_devotional.json`
- `src/main/resources/assets/verbum/textures/item/dusty_devotional.png`
- `src/main/resources/assets/verbum/lang/en_us.json`

## Asset Checklist (Library Book)
- `src/main/resources/assets/verbum/books/dusty_devotional@veritas.txt`
