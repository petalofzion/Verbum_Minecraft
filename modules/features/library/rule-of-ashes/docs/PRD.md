# PRD: Rule of Ashes

## Purpose
Provide a concise Vorago profile manual as a library-backed book. The text should teach the player that Vorago is Visions under harsher constraints, not a second full content jump.

## Non-Goals
- New gameplay systems, modifiers, or mechanics.
- Cross-module wiring changes.
- Custom UI behavior beyond existing library-book wiring.

## User Stories
- As a player, I can acquire `Rule of Ashes` as an item.
- As a player, I can open it and quickly understand Vorago's intended play posture.

## Data Model
- Register one `LibraryBookDef` item with ID `verbum:rule_of_ashes`.
- Use book ID `verbum:rule_of_ashes@vorago`.
- Package edition-specific text in a capsule resource.

## Performance Notes
- Hot path: no.
- Book content is classpath-loaded and cached by library wiring.

## Build / Profile Target
- Vorago-only content (`edition: vorago`).

## API / SPI Needs
- `FeatureEntrypoint`
- `LibraryBookDef`
- `ItemDef`

## Test Plan
- Capsule-local verification only for this task.
- No required checks were requested.
