# PRD: Pilgrim's Atlas

## Purpose
Provide a concise Visions profile manual that orients players to the flagship experience: expansive systems, luminous atmosphere, and broad discovery loops.

## Non-Goals
- Deep lore anthology or long narrative arcs.
- Custom book UI behavior.
- Cross-module profile routing logic.

## User Stories
- As a player, I can find Pilgrim's Atlas in creative inventory.
- As a player, I can open it and quickly understand how to approach Visions content.

## Data Model
- Registers one `LibraryBookDef` item with stable id `verbum:pilgrims_atlas`.
- Uses book handle `verbum:pilgrims_atlas@visions`.
- Loads text from `assets/verbum/books/pilgrims_atlas@visions.txt`.

## Performance Notes
- Hot path: no.
- Content is static and loaded through existing library book wiring.

## Build / Profile Target
- Visions profile content.

## API / SPI Needs
- Uses `FeatureEntrypoint`, `ItemDef`, and `LibraryBookDef` from core contracts.

## Test Plan
- Capsule-local checks were requested with no required commands.
- Manual runtime verification can be done later in client.
