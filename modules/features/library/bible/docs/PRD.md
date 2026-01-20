# PRD: Bible Feature

## Purpose
Provide a Bible item that registers a library-backed book entry so players can read the full Bible offline without storing megabytes in item data.

## Non-Goals
- Custom reader UI beyond the library-backed book view.
- Multiplayer sync or server-streaming behavior.
- World-save mutations or player-written mega-books.

## User Stories
- As a player, I can find a Bible item in creative inventory.
- As a player, I can open the Bible item and read the full text offline.

## Data Model
- Bible item registers a `book_id` handle via core contracts.
- Book content is packaged as a resource in this capsule.

## Performance Notes
- Hot path: no.
- Content is loaded once and cached by the book-enhancement library.

## Edition Target
- Both editions (vanilla-plus and visions).

## API / SPI Needs
- Uses `LibraryBookDef` to register the library-backed Bible.

## Test Plan
- `./gradlew build`
- `./gradlew check`
- Manual: `./gradlew runClient`, open the Bible item and verify full text loads.
