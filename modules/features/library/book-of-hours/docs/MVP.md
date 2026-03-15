# MVP: Book of Hours Feature

## Must-Have
- Book of Hours item registered via `FeatureEntrypoint` using `LibraryBookDef`.
- Book id uses `@votum` edition suffix.
- Player-facing manual text explains Vocations in a warm domestic tone.
- Item assets and lang entry included.

## Out of Scope (for MVP)
- New contracts or assembly wiring changes.
- Advanced UI behavior.
- Additional profile books.

## Acceptance Criteria
- Registration defines `verbum:book_of_hours` item id.
- Library book id is `verbum:book_of_hours@votum`.
- Content uses Vocations as the player-facing profile name.
- Capsule stays pure (no Minecraft/Fabric classes).
