# PRD: Bible Feature

## Purpose
Provide a dedicated Bible item in Verbum that is discoverable in-game and serves as the foundation for future scripture reading systems.

## Non-Goals
- Custom UI or text rendering beyond vanilla item behavior (for now).
- Custom simulation logic or ticking systems.
- Cross-feature dependencies.

## User Stories
- As a player, I can find a Bible item in creative inventory.
- As a player, the Bible item has a distinct name and icon (even if placeholder).

## Data Model
- No new saved data in MVP.
- No migrations required.

## Performance Notes
- Hot path: no.
- The capsule only registers data definitions.

## Edition Target
- Vanilla+ and Visions.

## API / SPI Needs
- None for MVP.

## Test Plan
- `./gradlew build`
- `./gradlew check`
- Manual: `./gradlew runClient`, confirm the Bible item is present in creative inventory.
