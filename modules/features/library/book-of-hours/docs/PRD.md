# PRD: Book of Hours Feature

## Purpose
Provide a Book of Hours item that registers a Vocations profile manual as a library-backed book so players can read calm, practical orientation content offline.

## Non-Goals
- Custom reader UI beyond the existing library-backed view.
- Cross-module progression systems.
- Server-side profile syncing.

## User Stories
- As a player, I can find Book of Hours in creative inventory.
- As a player, I can open Book of Hours and read a short Vocations profile manual.

## Data Model
- Item id: `verbum:book_of_hours`
- Library book id: `verbum:book_of_hours@vocations`
- Content resource: `assets/verbum/books/book_of_hours@vocations.txt`

## Performance Notes
- Hot path: no.
- Book content is static packaged text loaded through library book wiring.

## Build / Profile Target
- Vocations edition tier (player-facing Vocations line), inherited upward into Visions and Vorago.

## API / SPI Needs
- Uses `LibraryBookDef` for a library-backed profile manual.

## Test Plan
- Capsule-local verification only for this task.
