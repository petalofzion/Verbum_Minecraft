# PRD: Librarian's Desk

## Purpose
Add a placeable Librarian's Desk block for Vocations that uses the workstation seam for multi-slot book processing.

## Non-Goals
- New persistence layers or save-schema changes.
- Direct Minecraft/Fabric imports in the capsule.
- Cross-module wiring edits from this capsule task.

## User Stories
- As a player, I can place and use a Librarian's Desk.
- As a player, the desk can process multiple book inputs through workstation actions.
- As a player, ordinary books can be salvaged in batches into paper and leather.
- As a player, shipped Verbum library/manual books can be copied into player-owned written books without mutating the source books.
- As a player, my written books can be converted into editable drafts.
- As a player, desk writing can consume a source input and produce a player-owned written result when draft content is provided by workstation wiring.

## Data Model
- Block id: `verbum:librarians_desk`
- Workstation behavior id: `verbum:librarians_desk`
- Default workstation slot count: `9`
- Default open action behavior:
  - batch salvage plain books
  - copy shipped manuals to player-owned written copies
  - convert player-written books to editable drafts

## Performance Notes
- Hot path: no.
- Workstation processing is linear to workstation slots and uses small immutable lookups.

## Build / Profile Target
- Vocations edition tier, inherited upward by Visions and Vorago.

## API / SPI Needs
- Uses `FeatureEntrypoint`, `BlockDef`, `BlockWorkstationHandler`, `BlockWorkstationBehaviorProvider`, `WorkstationUiSpec`, `WorkstationActionRequest`, `WorkstationActionResult`, `WorkstationSlotDelta`, `WorkstationPlayerBookGrant`, and `ItemGrant`.

## Current Seam Constraints
- This capsule provides pure action logic only; assembly wiring owns the concrete UI/screen/menu implementation.
- Draft writing and detailed copy fidelity depend on the workstation request payload supplied by assembly wiring.
- The capsule never mutates shipped resource books; it emits player-owned outputs.
- Copy mode uses plain `minecraft:book` items as copy targets to avoid free duplication while preserving source books.

## Test Plan
- Capsule-local verification only for this task.
