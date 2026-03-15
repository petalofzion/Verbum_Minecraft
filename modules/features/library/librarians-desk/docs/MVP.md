# MVP: Librarian's Desk

## Must-Have
- Register `verbum:librarians_desk` via `BlockDef` in capsule `FeatureEntrypoint`.
- Provide a capsule-local `BlockInteractionHandler` class.
- Support salvage-only interactions:
  - `minecraft:book` salvages into paper.
  - `minecraft:written_book` salvages into paper only while sneaking.
  - Verbum library/manual books salvage into paper only while sneaking.
- Never perform writing/editing/authoring behavior.
- Include block/item/lang/model/blockstate assets.

## Out of Scope (for MVP)
- New core contracts.
- Assembly wiring edits.
- Custom writing screens or persistent authoring systems.

## Acceptance Criteria
- Handler returns `BlockInteractionResult` with `ItemGrant("minecraft:paper", 3)` on allowed salvage.
- Non-eligible interactions return pass-through or a non-consuming handled response.
- Capsule stays pure (no Minecraft/Fabric imports).
