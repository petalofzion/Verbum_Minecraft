# PRD: Librarian's Desk

## Purpose
Add a placeable Librarian's Desk block for Vocations that performs strict salvage-only interactions for books.

## Non-Goals
- Any writing or editing UI.
- Any authored text workflow or persistence system.
- Cross-module wiring or contract changes.

## User Stories
- As a player, I can place and use a Librarian's Desk.
- As a player, holding `minecraft:book` lets me salvage it into paper.
- As a player, holding `minecraft:written_book` only salvages while sneaking.
- As a player, holding Verbum library/manual books only salvages while sneaking.

## Data Model
- Block id: `verbum:librarians_desk`
- Interaction handler: `com.verbum_minecraft.features.library.librariansdesk.LibrariansDeskInteractionHandler`
- Salvage output: `minecraft:paper`

## Performance Notes
- Hot path: no.
- Interaction is constant-time checks against small immutable sets.

## Build / Profile Target
- Vocations edition tier, inherited upward by Visions and Vorago.

## API / SPI Needs
- Uses `FeatureEntrypoint`, `BlockDef`, `BlockInteractionHandler`, `BlockInteractionContext`, `BlockInteractionResult`, and `ItemGrant`.

## Test Plan
- Capsule-local verification only for this task.
