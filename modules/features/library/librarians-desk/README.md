# Librarian's Desk Capsule

## Purpose
Provide a Vocations-aligned utility block that salvages books into paper through a narrow, explicit interaction rule set. The capsule only registers data and pure interaction logic and does not introduce writing, editing, or authoring systems.

## Scope
- Block registration via `FeatureEntrypoint` and `BlockDef`
- Capsule-local `BlockInteractionHandler` for salvage-only behavior
- Block/item/lang/model/blockstate assets
- Pure logic/data only (no Fabric/Minecraft classes)

## Dependencies
- `modules/core/api`
- `modules/core/spi`

## Key Files
- `module.json`
- `src/main/java/.../LibrariansDeskFeature.java`
- `src/main/java/.../LibrariansDeskInteractionHandler.java`
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`
- `docs/PRD.md`, `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/`
