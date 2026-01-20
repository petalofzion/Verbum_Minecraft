# MVP: Bible Feature

## Must-Have
- Bible item registered via `FeatureEntrypoint` using `LibraryBookDef`.
- Full Bible text packaged as `assets/verbum/books/bible.txt`.
- Custom Bible icon/model asset.

## Out of Scope (for MVP)
- Multiplayer sync or server-authoritative streaming.
- Lectern-specific integration beyond default item behavior.
- Custom reader UI beyond the library-backed book view.

## Acceptance Criteria
- Bible item exists in-game (creative inventory).
- Opening the Bible reads the full text offline.
- No Minecraft/Fabric classes used in the capsule.
- Build and check pass.

## Risks / Open Questions
- Resource loading across modules vs. assemblies (verify in-game).
