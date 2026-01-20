# MVP: Book Core (Stage 1)

## Must-Have
- Book library resolver for packaged resources (offline-only).
- Bible item uses a book handle (`book_id`) instead of embedding full text in NBT.
- Full Bible is readable in-game via pagination cache.
- Hard limits enforced for safety (raw bytes, pages, page length).

## Out of Scope (for MVP)
- Multiplayer sync or streaming.
- World-save overrides or player-written mega-books.
- Custom rendering beyond a functional reader.

## Acceptance Criteria
- Bible item reads the complete text offline without exceeding vanilla book NBT limits.
- No Fabric/Minecraft classes used inside the capsule.
- Build and check pass.

## Risks / Open Questions
- Translation selected (Douay-Rheims via Project Gutenberg) with attribution and license recorded.
