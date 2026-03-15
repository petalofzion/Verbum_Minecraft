# PRD: Dusty Devotional

## Purpose
Provide a concise Veritas profile manual that orients players to the refined baseline tone: plain, stable, and trustworthy.

## Non-Goals
- Deep lore anthology or long narrative arcs.
- Custom book UI behavior.
- Cross-module profile routing logic.

## User Stories
- As a player, I can find Dusty Devotional in creative inventory.
- As a player, I can open it and quickly understand what Veritas is trying to be.

## Data Model
- Registers one `LibraryBookDef` item with stable id `verbum:dusty_devotional`.
- Uses book handle `verbum:dusty_devotional@veritas`.
- Loads text from `assets/verbum/books/dusty_devotional@veritas.txt`.

## Performance Notes
- Hot path: no.
- Content is static and loaded through existing library book wiring.

## Build / Profile Target
- Veritas baseline content.

## API / SPI Needs
- Uses `FeatureEntrypoint`, `ItemDef`, and `LibraryBookDef` from core contracts.

## Test Plan
- Capsule-local checks were requested with no required commands.
- Manual runtime verification can be done later in client.
