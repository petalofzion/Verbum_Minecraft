# Book Core Capsule

## Purpose
Provide a library-backed book system that allows very large books (e.g., the full Bible) to be read from a vanilla written book without storing megabytes in item NBT.

## Scope
- Feature registrations via `FeatureEntrypoint`
- Pure logic/data only (no Fabric/Minecraft classes)
- Offline-first book content store, pagination rules, and cache metadata

## Dependencies
- `modules/core/api`
- `modules/core/spi`

## Key Files
- `module.json`
- `src/main/java/.../BookCoreFeature.java`
- `src/main/resources/META-INF/services/com.verbum_minecraft.spi.FeatureEntrypoint`
- `docs/PRD.md`, `docs/MVP.md`
- `docs/TODO.md`
- `docs/agent-logs/`

## Content Assets (Stage 1)
- `src/main/resources/assets/verbum/books/` (packaged book text, UTF-8)
