# Capsule TODO: Book Enhancement

This file tracks **capsule-local** work only. It is maintained by capsule agents.

## How to Use
- Add tasks you discover while implementing.
- Keep scope limited to this capsule.
- Mark items done with `[x]` and keep ordering stable.
- If you identify cross-module work (API/SPI/assemblies), log it in `docs/agent-logs/` and stop.

## Tasks
- [x] Define book identity schema (book_id, edition, bookmark).
- [x] Draft packaged library layout (manifest + text locations).
- [x] Implement pagination cache utilities (pure logic).
- [x] Add BookEnhancementFeature entrypoint stub.
- [x] Log capability sweep for required core contracts and assembly hooks.
- [x] Stage 2: Add BookBookmark record for bookId + page tracking.
- [x] Stage 2: Add BookChapter record with title and startPage.
- [x] Stage 2: Add BookTableOfContents validation and page lookup.
- [x] Stage 1: Coordinate Bible text asset in the bible capsule resources.
- [x] Move pagination + bookmark helper logic into this capsule.
