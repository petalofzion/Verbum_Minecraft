# MVP: Librarian's Desk

## Must-Have
- Register `verbum:librarians_desk` via `BlockDef` in capsule `FeatureEntrypoint`.
- Provide a capsule-local `BlockWorkstationHandler` class.
- Provide a capsule-local `BlockWorkstationBehaviorProvider` service binding.
- Use workstation seam actions with multi-slot input handling.
- Support default open-action behavior:
  - plain books salvage in batches to paper and leather
  - shipped Verbum manuals copy to player-owned written outputs
  - player written books convert to editable drafts
- Support explicit action handling for:
  - `salvage_all`
  - `copy_books`
  - `edit_player_book`
  - `write_draft` (when draft payload is provided)
- Explicit action feedback when selected inputs are invalid.
- `copy_books` preserves source books and consumes plain book copy targets.
- Include block/item/lang/model/blockstate assets.

## Out of Scope (for MVP)
- New core contracts.
- Assembly wiring edits.
- New persistence stores or save-schema migration work.

## Acceptance Criteria
- Handler returns `WorkstationActionResult` with coherent `slotDeltas`, `itemGrants`, and/or `playerBookGrants`.
- Invalid explicit actions return actionable status messages.
- Open/no-action path does not silently mutate slot content.
- Capsule stays pure (no Minecraft/Fabric imports).
