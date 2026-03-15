# Book of Hours Capsule

## Purpose
Provide a cozy Vocations profile manual as a library-backed book item. The capsule introduces practical, player-facing orientation text for calm pastoral play without adding platform logic.

## Scope
- Library-backed Book of Hours registration via `FeatureEntrypoint`
- Packaged profile manual text resource
- Pure logic/data only (no Fabric/Minecraft classes)

## Dependencies
- `modules/core/api`
- `modules/core/spi`

## Key Files
- `module.json`
- `src/main/java/.../BookOfHoursFeature.java`
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`
- `docs/PRD.md`, `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/`

## Asset Checklist (Item)
- `src/main/resources/assets/verbum/items/book_of_hours.json`
- `src/main/resources/assets/verbum/models/item/book_of_hours.json`
- `src/main/resources/assets/verbum/textures/item/book_of_hours.png`
- `src/main/resources/assets/verbum/lang/en_us.json`

## Asset Checklist (Library Book)
- `src/main/resources/assets/verbum/books/book_of_hours@vocations.txt`
