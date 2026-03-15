# Bible Feature Capsule

This capsule provides the Bible item definition and related feature wiring for Verbum.

## Scope
- Library-backed Bible item definition registered via `FeatureEntrypoint`.
- Packaged Bible text resource for offline reading.
- Pure data and logic; no direct Minecraft/Fabric dependencies.

## Capsule Docs
- `docs/PRD.md`
- `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/` (issues/questions/decisions)

## Key Files
- `module.json`: module metadata and dependency declarations.
- `src/main/java/.../BibleFeature.java`: feature entrypoint.
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`: SPI registration.

## Asset Checklist (Item)
- `src/main/resources/assets/verbum/items/bible.json`
- `src/main/resources/assets/verbum/models/item/bible.json`
- `src/main/resources/assets/verbum/textures/item/bible.png`
- `src/main/resources/assets/verbum/lang/en_us.json`

## Asset Checklist (Library Book)
- `src/main/resources/assets/verbum/books/bible.txt`
