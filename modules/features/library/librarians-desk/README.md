# Librarian's Desk Capsule

## Purpose
Provide a Vocations-aligned utility block that exposes a workstation flow for book handling. The capsule registers pure workstation rules for salvage, copying, and editing-prep behavior without importing Minecraft/Fabric classes.

## Scope
- Block registration via `FeatureEntrypoint` and `BlockDef`
- Capsule-local `BlockWorkstationHandler` for workstation action rules
- Capsule-local `BlockWorkstationBehaviorProvider` for SPI behavior resolution
- Block/item/lang/model/blockstate assets
- Pure logic/data only (no Fabric/Minecraft classes)

## Current Action Semantics
- `salvage_all`: consumes input books and grants material outputs.
- `copy_books`: keeps source manuals/books immutable, consumes plain `minecraft:book` copy targets, and grants player-owned written copies.
- `edit_player_book`: converts player-written books into editable draft materials (`minecraft:writable_book`) by consuming the written source.
- `write_draft`: consumes one plain/writable source book and emits a player-owned written result from workstation draft payload.

If an action is selected without valid inputs, the handler returns a clear status message instead of silent pass-through.

## Dependencies
- `modules/core/api`
- `modules/core/spi`

## Key Files
- `module.json`
- `src/main/java/.../LibrariansDeskFeature.java`
- `src/main/java/.../LibrariansDeskWorkstationHandler.java`
- `src/main/java/.../LibrariansDeskWorkstationBehaviorProvider.java`
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.BlockWorkstationBehaviorProvider`
- `docs/PRD.md`, `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/`
