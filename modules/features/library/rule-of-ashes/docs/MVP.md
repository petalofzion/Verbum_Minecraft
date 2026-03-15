# MVP: Rule of Ashes

## Must-Have
- `Rule of Ashes` item registered via `LibraryBookDef`.
- Stable item ID `verbum:rule_of_ashes`.
- Vorago edition book ID `verbum:rule_of_ashes@vorago`.
- Concise player-facing manual text in severe, useful Vorago tone.
- Complete capsule scaffold and item assets.

## Out of Scope (for MVP)
- Any mechanical survival systems.
- Any cross-module contract or assembly changes.
- Expanded lorebook collection.

## Acceptance Criteria
- Capsule structure and docs exist and are coherent.
- `module.json` declares `edition: vorago`.
- SPI registration points to the capsule entrypoint class.
- Item assets, lang entry, model mapping, and book text are present.
