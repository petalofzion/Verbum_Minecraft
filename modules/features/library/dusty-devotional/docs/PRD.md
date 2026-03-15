# PRD: Dusty Devotional

## Purpose
Provide a concise Veritas profile manual that clearly explains:
- what Veritas is for,
- how Veritas should feel in play,
- what practical play posture Veritas invites.

## Non-Goals
- Deep lore anthology or long narrative arcs.
- Custom book UI behavior.
- Cross-module profile routing logic.

## User Stories
- As a player, I can find Dusty Devotional in creative inventory.
- As a player, I can open it and quickly understand why Veritas exists as a profile.
- As a player, I can read a short, practical description of the kind of play Veritas favors.

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
- Manual runtime verification can be done later in client (open book and confirm pages read as a practical Veritas manual).
