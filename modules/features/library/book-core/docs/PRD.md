# PRD: Book Core (Library-Backed Books)

## Purpose
Provide a library-backed book system so the vanilla written book can reference large, offline content (e.g., the full Bible) without storing megabytes in item NBT.

## Non-Goals
- No Minecraft/Fabric classes in this capsule.
- No networking or multiplayer sync in stages 1-3.
- No world-save mutations or player-written mega-books (stages 1-3).
- No kernel hot-path logic.

## User Stories
- As a player, I can open the Bible item and read the full text offline.
- As a player, the Bible item remains lightweight and safe in inventories.
- As a content author, I can ship large books as packaged resources.

## Data Model
- Book identity stored as a compact handle (Stage 1 uses the item definition; later stages can add `book_id`/bookmark components).
- Book content stored as packaged resources (Stage 1-3).
- Pagination cache keyed by `(book_id, locale, font, gui_scale, wrap_width)`.
- No world-save data in Stage 1 (offline-only).

## Performance Notes
- Hot path: no.
- Avoid repeated pagination; cache page breaks on first open.
- Hard caps for safety (see Staging Plan).

## Edition Target
- Vanilla+ baseline (included in Visions assembly).

## Staging Plan (Offline First)
### Stage 1: Library Pointer + Full Bible (Offline)
- Vanilla written book becomes a handle keyed by the item definition.
- Packaged book library resolver (no network).
- Pagination + caching so the full Bible is readable.
- Hard limits: max raw text bytes (128 MB), max pages (100000), max page chars (16384).

### Stage 2: Offline UX Enhancements
- Table of contents / chapter index mapping.
- Bookmarks and last-read position.
- Improved pagination stability across client settings.
- Page formatting heuristics (wrap width, paragraph handling).

### Stage 3: Offline “Nice-to-Have” Features
- Crosslinks and footnotes (data-driven).
- Spine/cover variants driven by metadata.
- Search within book (cached index).

### Stage 4: Multiplayer / Server Features
- Server-authoritative library with chunked streaming.
- Rate limits and max-bytes-per-request guards.
- Optional world-local override packs and sync rules.

## API / SPI Needs
- Expected: new core contracts for book identity, library lookup, and pagination hooks.
- If missing, log a capability sweep under `docs/agent-logs/`.

## Attribution / Licensing
- Use a Creative Commons translation (e.g., Douay-Rheims) or another permissive source.
- Add an entry to `SOURCE_ATTRIBUTION.md` and copy the license into `LICENSES/` once final text is chosen.

## Test Plan
- `./gradlew build`
- `./gradlew check`
- Manual: run client, open Bible item, verify full text loads offline.
- Stage 4: add network tests once multiplayer is implemented.
